from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import pytz
import MySQLdb.cursors
import json
import re
import bcrypt

import os
import pinecone
import openai
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    ChatPromptTemplate,
    MessagesPlaceholder
)
from langchain import PromptTemplate

from bs4 import BeautifulSoup

app = Flask(__name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/static")

app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'mysql-152093-0.cloudclusters.net'
app.config['MYSQL_PORT'] = 19876
app.config['MYSQL_USER'] = 'admin'
app.config['MYSQL_PASSWORD'] = 'redchatbot'   
app.config['MYSQL_DB'] = 'redcms'

mysql = MySQL(app)

load_dotenv()
# Load environment variables
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
INDEX_NAME = "red-chatbot-final"
EMBEDDING_MODEL ="text-embedding-ada-002"

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)

# Initialize the OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404page.html'), 404


@app.route('/')
def home():
    return render_template('index.html')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("UTF-8"), hashed_password)

def hash_password(password):
    salt = bcrypt.gensalt(13)
    hashed_password = bcrypt.hashpw(password.encode("UTF-8"), salt)
    return hashed_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM tbluser WHERE email = %s', (email,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            hashed_password = user['password']
            if check_password(password, hashed_password.encode("UTF-8")):
                session['login'] = True
                session['admin'] = user['id']
                session['email'] = user['email']
                
                return redirect(url_for('dashboard'))
            message = 'Wrong password!'    
            return render_template('login.html', message = message) 
        message = 'Email address is not registered!'    
        return render_template('login.html', message = message)          
    return render_template('login.html', message=message)


@app.route('/dashboard')
def dashboard():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(DISTINCT sessionID) AS session_count, COUNT(incomingMessage) AS inMessages FROM tblconversations")
        data = cursor.fetchone()
        
        cursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor2.execute("SELECT COUNT(botMessage) AS botMessages FROM tblconversations WHERE botMessage != ''")
        data2 = cursor2.fetchone()
        
        # Get the current date
        today = datetime.now()
        
        # Calculate the start and end dates for the current week (Sunday to Saturday)
        days_until_sunday = (today.weekday() - 6) % 7
        start_of_week = today - timedelta(days=days_until_sunday)
        end_of_week = start_of_week + timedelta(days=6)
        
        # Calculate the start and end dates for the previous week
        start_of_last_week = start_of_week - timedelta(days=7)
        end_of_last_week = end_of_week - timedelta(days=7)
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Query data for the current week
        query_current_week = (
            "SELECT DAYNAME(timestamp) AS day, COUNT(DISTINCT sessionID) AS session_count "
            "FROM tblconversations "
            "WHERE DATE(timestamp) BETWEEN %s AND %s "
            "GROUP BY day"
        )
        cursor.execute(query_current_week, (start_of_week, end_of_week))
        current_week_data = cursor.fetchall()
        
        # Query data for the previous week
        query_last_week = (
            "SELECT DAYNAME(timestamp) AS day, COUNT(DISTINCT sessionID) AS session_count "
            "FROM tblconversations "
            "WHERE DATE(timestamp) BETWEEN %s AND %s "
            "GROUP BY day"
        )
        cursor.execute(query_last_week, (start_of_last_week, end_of_last_week))
        last_week_data = cursor.fetchall()

        # Prepare data for JavaScript (current and last week's session data)
        days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        current_week_session_data = [0, 0, 0, 0, 0, 0, 0]  # Initialize data for each day of the current week
        last_week_session_data = [0, 0, 0, 0, 0, 0, 0]  # Initialize data for each day of the previous week
        
        for row in current_week_data:
            day_name = row['day'].upper()
            if day_name in days:
                day_index = days.index(day_name)
                current_week_session_data[day_index] = row['session_count']
        
        for row in last_week_data:
            day_name = row['day'].upper()
            if day_name in days:
                day_index = days.index(day_name)
                last_week_session_data[day_index] = row['session_count']
        
        session_count = data['session_count']
        inMessage_count = data['inMessages']
        botMessage_count = data2['botMessages']
        
        # Query data for the current week
        query = (
            "SELECT DATE(timestamp) AS day, COUNT(DISTINCT sessionID) AS session_count "
            "FROM tblconversations "
            "WHERE DATE(timestamp) BETWEEN %s AND %s "
            "GROUP BY day"
        )
        cursor.execute(query, (start_of_week, end_of_week))
        current_week_data = cursor.fetchall()
        # Calculate the total sessions for the current week
        total_sessions = sum(row['session_count'] for row in current_week_data)
        
        # Query data for total sessions per month
        query = (
            "SELECT "
            "MONTH(timestamp) AS month, "
            "COUNT(DISTINCT sessionID) AS session_count "
            "FROM tblconversations "
            "GROUP BY month"
        )
        cursor.execute(query)
        monthly_session_data = cursor.fetchall()

        # Prepare data for JavaScript
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        session_month = [0] * 12  # Initialize data for each month

        for row in monthly_session_data:
            month_index = row['month'] - 1  # MySQL months are 1-based
            session_month[month_index] = row['session_count']
        
        cursor.close()
        
        return render_template(
            'dashboard.html',
            session_count = session_count,
            inMessage_count = inMessage_count,
            botMessage_count = botMessage_count,
            current_week_session_data = current_week_session_data,
            last_week_session_data = last_week_session_data,
            total_sessions=total_sessions,
            session_month=session_month
        )
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route('/manage')
def managedatasource():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
    # Fetch data from the MySQL database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM tbldata WHERE dataSource = 'Text'")
    dataText = cursor.fetchall()
    cursor.close()
    
    cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor1.execute("SELECT * FROM tbldata WHERE dataSource = 'FAQ'")
    dataFAQ = cursor1.fetchall()
    cursor1.close()
    
    # Fetch data from the MySQL database for total sources, processed, and error
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT COUNT(*) AS total_sources FROM tbldata")
    total_sources = cursor.fetchone()['total_sources']

    cursor.execute("SELECT COUNT(*) AS processed FROM tbldocuments WHERE status = 'Processed'")
    processed = cursor.fetchone()['processed']

    cursor.execute("SELECT COUNT(*) AS error FROM tbldocuments WHERE status = 'Error'")
    error = cursor.fetchone()['error']
    
    cursor.close()
    
    return render_template('datasource.html', data = dataText, dataFAQ = dataFAQ, total_sources=total_sources, processed=processed, error=error)

#Delete Text Data
@app.route('/delete_selected', methods=['POST'])
def delete_selected_rows():
    try:
        selected_ids = request.form.getlist('selected_ids[]')  # Get the selected row IDs
        selected_ids = [int(id) for id in selected_ids]  # Convert IDs to integers

        if len(selected_ids) == 0:
            return jsonify({'success': False, 'message': 'No rows selected for deletion'})

        # Establish a database connection (you may need to adapt this to your code)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Step 1: Fetch Vector IDs associated with selected IDs
        select_vector_ids_query = "SELECT vectorID FROM tbldata WHERE id IN (%s)"
        placeholders = ', '.join(['%s'] * len(selected_ids))
        select_vector_ids_query = select_vector_ids_query % placeholders
        cursor.execute(select_vector_ids_query, tuple(selected_ids))
        vector_ids = [row['vectorID'] for row in cursor.fetchall()]
        
        # Delete the rows from MySQL
        delete_query = "DELETE FROM tbldata WHERE id IN (%s)"
        delete_query = delete_query % placeholders
        cursor.execute(delete_query, tuple(selected_ids))
        mysql.connection.commit()
        cursor.close()
        
        # Step 2: Use Pinecone to delete the vectors
        index = pinecone.Index(INDEX_NAME)
        index.delete(ids=vector_ids)  # Delete vectors using Vector IDs
        
        return jsonify({'success': True, 'message': 'Selected rows deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/add-data-source')
def adddatasource():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    return render_template('adddatasource.html')


@app.route('/conversations')
def conversation():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))

    # Fetch sessions with their most recent messages from the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
       SELECT c1.sessionID, c1.timestamp, c1.incomingMessage, c1.botMessage
        FROM tblconversations c1
        JOIN (
            SELECT sessionID, MAX(timestamp) AS max_timestamp
            FROM tblconversations
            GROUP BY sessionID
        ) c2
        ON c1.sessionID = c2.sessionID AND c1.timestamp = c2.max_timestamp
        ORDER BY c1.timestamp DESC;
    """)
    sessions = cursor.fetchall()
    cursor.close()

    return render_template('conversations.html', sessions=sessions)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'login' not in session or not session['login']:
        return redirect(url_for('login'))
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_email = request.form['new_email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT email, password FROM tbluser WHERE id = %s', (session['admin'],))
        user = cursor.fetchone()
        if user:
            if new_email == user['email']:
                flash('This email is already in use. Please choose a different email address.', 'danger')
            else:
                hashed_password = user['password'].encode("utf-8")
                if bcrypt.checkpw(current_password.encode("utf-8"), hashed_password):
                    cursor.execute('UPDATE tbluser SET email = %s WHERE id = %s', (new_email, session['admin']))
                    mysql.connection.commit()
                    cursor.close()
                    flash('Email address updated successfully!', 'success')
                    return redirect(url_for('settings'))
                else:
                    flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('User not found.', 'danger')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT email FROM tbluser WHERE id = %s', (session['admin'],))
    user = cursor.fetchone()
    current_email = user['email'] if user else ''
    cursor.close()
    return render_template('settings.html', current_email=current_email)

#CHANGE PASSWORD
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Validate the form data (e.g., password complexity)

        # Check if the new password matches the current password in the database
        with mysql.connection.cursor(MySQLdb.cursors.DictCursor) as cursor:
            cursor.execute('SELECT password FROM tbluser WHERE id = %s', (session.get('admin', 0),))
            result = cursor.fetchone()
            if result is None:
                flash('User not found.', 'danger')
            elif not bcrypt.checkpw(current_password.encode("utf-8"), result['password'].encode("utf-8")):
                flash('Incorrect current password.', 'danger')
            elif new_password != confirm_password:
                flash('New password and confirm password do not match.', 'danger')
            else:
                try:
                    # Update the user's password in the database
                    password_hashed = hash_password(new_password)
                    cursor.execute('UPDATE tbluser SET password = %s WHERE id = %s', (password_hashed, session.get('admin', 0)))
                    mysql.connection.commit()

                    flash('Password updated successfully!', 'success')
                    return redirect(url_for('settings'))
                except Exception as e:
                    # Handle database or other errors
                    flash('An error occurred. Please try again later.', 'danger')

    return render_template('settings.html')

#LOGOUT
@app.route('/logout')
def logout():
    session.pop('login', None)
    session.pop('admin', None)
    return redirect(url_for('login'))

#LIST CONVERSATION
@app.route('/conversations/<session_id>')
def get_conversation(session_id):
    # Fetch the conversation for the given session ID from the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT timestamp, incomingMessage, botMessage
        FROM tblconversations
        WHERE sessionID = %s
        ORDER BY timestamp ASC
    """, (session_id,))
    conversation = cursor.fetchall()
    cursor.close()
    return jsonify(conversation)

#Remove Style from a textarea
def removeStyles(html):
    soup = BeautifulSoup(html, 'html.parser')
    # Remove all HTML tags
    text = soup.get_text(separator=' ')
    return text

#Initialize the text data list
text_data = []

#Insert data from text
@app.route('/save-text-vector', methods=['POST'])
def save_text():
    if request.method == 'POST':
        dataSource = "Text"
        text = request.form['textarea']

        text = removeStyles(text)
        text_data.append(text)

        try:
            # Index text data in Pinecone
            text_store = Pinecone.from_texts(text_data, embeddings, index_name=INDEX_NAME)

            # Create an OpenAI embedding
            test_bed = openai.Embedding.create(
                input=[
                    text  # Use the text variable here
                ],
                engine=EMBEDDING_MODEL
            )

            test_vector = test_bed['data'][0]['embedding']

            # Query Pinecone for similar vectors
            index = pinecone.Index(INDEX_NAME)
            data_from_pc = index.query(vector=test_vector, top_k=3, include_values=True)
            vectorID = data_from_pc['matches'][0]['id']

            characters = len(text)
            status = "Processed"

            # Create a query to save in MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO tbldata (vectorID, dataSource, dataText, characters, status) VALUES (%s, %s, %s, %s, %s)",(vectorID, dataSource, text, characters, status))
            mysql.connection.commit()

            # Insert "Processed" status into tbldocuments
            cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor1.execute("INSERT INTO tbldocuments (status) VALUES (%s)", (status,))
            mysql.connection.commit()
            cursor1.close()

            return jsonify({"message": "Data source added successfully"})

        except Exception as e:
            # Handle exceptions and insert "Error" status into tbldocuments
            status = "Error"
            cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor1.execute("INSERT INTO tbldocuments (status) VALUES (%s)", (status,))
            mysql.connection.commit()
            cursor1.close()
            return jsonify({"message": f"An error occurred: {str(e)}"})

    return "Invalid request"


# Update Data from a Text
@app.route('/edit-text-vector', methods=['POST'])
def editTextData():
    if request.method == 'POST':
        text_id = request.form['textId']  # Get the ID from the form
        text = request.form['updateText']

        text = removeStyles(text)
        text_data.append(text)

        characters = len(text)

        # Create a query to save in MySQL with the ID in the WHERE clause
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE tbldata SET dataText = %s, characters = %s WHERE id = %s", (text, characters, text_id))
        mysql.connection.commit()
        cursor.close()

        # Retrieve the updated data from MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT dataText, vectorID FROM tbldata WHERE id = %s", (text_id,))
        row = cursor.fetchone()  # Fetch one row

        if row:
            updated_text = row['dataText']
            vectorID = row['vectorID']
        else:
            # Handle the case where no row was found for the given id
            updated_text = None
            vectorID = None

        cursor.close()

        if vectorID:
            try:
                # Update the data in the Pinecone vector database
                test_bed = openai.Embedding.create(
                    input=[
                        updated_text
                    ],
                    engine=EMBEDDING_MODEL
                )

                test_vector = test_bed['data'][0]['embedding']

                # Query Pinecone for similar vectors
                index = pinecone.Index(INDEX_NAME)
                index.update(id=vectorID, values=test_vector, set_metadata={'text': updated_text})

                return jsonify({"message": "Data source updated successfully"})
            except Exception as e:
                return jsonify({"message": f"Error updating data in Pinecone: {str(e)}"})
        else:
            return jsonify({"message": "No vectorID found for the given id. Cannot update data in Pinecone."})

    return "Invalid request"


# Update Data from a Text
@app.route('/edit-faq-vector', methods=['POST'])
def editFAQData():
    if request.method == 'POST':
        faq_id = request.form['faqID']
        question = request.form['questions']
        answer = request.form['answers']

        answer = removeStyles(answer)

        # Concatenate the question and answer to create faq_text
        faqQuestion = "Question"
        faqAnswer = "Answer"
        faq_text = f"{faqQuestion}: {question} {faqAnswer}: {answer}"
        
        characters = len(faq_text)

        # Update the question and answer in MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE tbldata SET dataFAQQuestion = %s, dataFAQAnswer = %s, characters = %s WHERE id = %s", (question, answer, characters, faq_id))
        mysql.connection.commit()
        cursor.close()

        # Retrieve the updated data from MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT dataFAQQuestion, dataFAQAnswer, vectorID FROM tbldata WHERE id = %s", (faq_id,))
        row = cursor.fetchone()

        if row:
            updated_question = row['dataFAQQuestion']
            updated_answer = row['dataFAQAnswer']
            vectorID = row['vectorID']
        else:
            updated_question = None
            updated_answer = None
            vectorID = None

        cursor.close()

        if updated_question is not None and updated_answer is not None:
            # Concatenate the updated question and answer to create faq_text
            updated_faq_text = f"{faqQuestion}: {updated_question} {faqAnswer}: {updated_answer}"

            try:
                # Update the data in the Pinecone vector database
                test_bed = openai.Embedding.create(
                    input=[
                        updated_faq_text
                    ],
                    engine=EMBEDDING_MODEL
                )

                test_vector = test_bed['data'][0]['embedding']

                # Query Pinecone for similar vectors
                index = pinecone.Index(INDEX_NAME)
                index.update(id=vectorID, values=test_vector, set_metadata={'text': updated_faq_text})

                return jsonify({"message": "Data source updated successfully"})
            except Exception as e:
                return jsonify({"message": f"Error updating data in Pinecone: {str(e)}"})
        else:
            return jsonify({"message": "No question and answer found for the given id. Cannot update data in Pinecone."})

    return "Invalid request"



#Insert data from a FAQ
@app.route('/save-faq', methods=['POST'])
def save_faq():
    if request.method == 'POST':
        question = request.form['questions']
        answer = request.form['answers']
        dataSource = "FAQ"
        office = request.form['selectOffice']  # Get the selected office value

        try:
            # Check if both question and answer are provided
            if not question or not answer:
                return jsonify({"error": "Both question and answer must be provided"})

            # Create a unique identifier for this FAQ (e.g., using a prefix)
            faqQuestion = "Question"
            faqAnswer = "Answer"

            answer = removeStyles(answer)
            # Append the FAQ to the text_data list
            faq_text = f"{faqQuestion}: {question} {faqAnswer}: {answer}"
            text_data.append(faq_text)
            text_store = Pinecone.from_texts([faq_text], embeddings, index_name=INDEX_NAME)
            
            # Create an OpenAI embedding
            test_bed = openai.Embedding.create(
                input=[
                    faq_text
                ],
                engine=EMBEDDING_MODEL
            )

            test_vector = test_bed['data'][0]['embedding']

            # Query Pinecone for similar vectors
            index = pinecone.Index(INDEX_NAME)
            data_from_pc = index.query(vector=test_vector, top_k=3, include_values=True)
            vectorID = data_from_pc['matches'][0]['id']

            characters = len(faq_text)
            status = "Processed"

            # Create a query to save in MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO tbldata (vectorID, dataSource, dataFAQQuestion, dataFAQAnswer, characters, status, office) VALUES (%s, %s, %s, %s, %s, %s, %s)", (vectorID, dataSource, question, removeStyles(answer), characters, status, office))
            mysql.connection.commit()
            cursor.close()
            
            # Insert "Processed" status into tbldocuments
            cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor1.execute("INSERT INTO tbldocuments (status) VALUES (%s)", (status,))
            mysql.connection.commit()
            cursor1.close()

            return jsonify({"message": "FAQ saved successfully"})
        
        except Exception as e:
            # Handle exceptions and insert "Error" status into tbldocuments
            status = "Error"
            cursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor1.execute("INSERT INTO tbldocuments (status) VALUES (%s)", (status,))
            mysql.connection.commit()
            cursor1.close()
            return jsonify({"message": f"An error occurred: {str(e)}"})
        
    return "Invalid request"


#Handle Conversation for Dialogflow
@app.route('/dialogflow-webhook', methods=['POST'])
def handle_dialogflow():
    data = request.get_json()
    
    # Extract relevant data from the Dialogflow webhook response
    responseID = data['responseId']
    query_text = data['queryResult']['queryText']
    fulfillment_text = data['queryResult'].get('fulfillmentText', '')
    action = data['queryResult']['action']
    intent_name = data['queryResult']['intent']['displayName']

    # Create a query to save in MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO tblconversations (sessionID, incomingMessage, botMessage, intentName, action) VALUES (%s, %s, %s, %s, %s)", (responseID, query_text, fulfillment_text, intent_name, action))
    mysql.connection.commit()
    cursor.close()
    
    try:
        action = data['queryResult']['action']
        if action == 'input.unknown':
            
            # Return the response to Dialogflow
            return jsonify({
                'fulfillmentText': 'This response is from webhook'
            })
        else:
            # Handle other actions here if needed
            return jsonify({
                'fulfillmentText': 'Action not recognized.'
            })
    except:
        return jsonify({
            'fulfillmentText': 'Error occurred.'
        })


conversation_history = []

def embedding_db():
    # We use the OpenAI embedding model
    index_name = "red-chatbot-final"
    embeddings = OpenAIEmbeddings()
    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENV
    )

    doc_db = Pinecone.from_existing_index(index_name, embeddings)
    return doc_db

def retrieval_answer(query, doc_db, llm, conversation_history):
    # Append the query to the conversation history
    conversation_history.append({"role": "user", "content": query})

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=doc_db.as_retriever(),
    )
    result = qa.run(query)
    
    # Append the response to the conversation history
    conversation_history.append({"role": "assistant", "content": result})
    return result

@app.route('/dialogflow', methods=['POST'])
def dialogflow_webhook():
    
    llm = ChatOpenAI()
    doc_db = embedding_db()
    
    data = request.get_json()
    print(json.dumps(data))
    
    session_info = data['sessionInfo']['session']  # Access the sessionInfo field
    sessionID = session_info.split('/')[-1]
    query = data['text']
    response = retrieval_answer(query, doc_db, llm, conversation_history)
    ph_time = pytz.timezone('Asia/Manila')
    timestamp = datetime.now(ph_time)
    
   # Check if the MySQL connection is established
    if mysql.connection is None:
        raise Exception("MySQL connection is not established.")
    
    # Create a cursor and execute the SQL query
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO tblconversations (sessionID, incomingMessage, botMessage, timestamp) VALUES (%s, %s, %s, %s)", (sessionID, query, response, timestamp))
    mysql.connection.commit()
    cursor.close()
    
    
    try:
        return jsonify(
            {
                'fulfillment_response': {
                    'messages': [
                        {
                            'text': {
                                'text': [response]
                            }
                        }
                    ]
                }
            }
        )
        
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message to the console
        return jsonify(
            {
                'fulfillment_response': {
                    'messages': [
                        {
                            'text': {
                                'text': [error_message]  # Include the error message in the response
                            }
                        }
                    ]
                }
            }
        )


if __name__ == "__main__":
    llm = ChatOpenAI()
    doc_db = embedding_db()
    app.run()
