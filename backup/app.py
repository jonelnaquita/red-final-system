from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from MySQLdb import OperationalError

from datetime import datetime, timedelta
from apiip import apiip
import pytz
import MySQLdb.cursors
import json
import re
import bcrypt
import requests
import pdfkit

from views import views
from utils import utils
from fetchGraphData import fetchData
from generateReport import report

import xml.etree.ElementTree as ET
import emoji

import os
import pinecone
import openai
import tiktoken
from dotenv import load_dotenv
from langchain.document_loaders import DirectoryLoader
from langchain.chains.question_answering import load_qa_chain
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI

from langchain.chains import LLMChain, ConversationChain
from langchain.chains.conversation.memory import (ConversationBufferMemory, 
                                                  ConversationSummaryMemory, 
                                                  ConversationBufferWindowMemory,
                                                  ConversationKGMemory)
from langchain.callbacks import get_openai_callback
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.prompts import PromptTemplate
from bs4 import BeautifulSoup

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import MongoClient

from flask_mail import Mail, Message
import secrets

app = Flask(__name__,
            template_folder="templates",
            static_folder="static",
            static_url_path="/static")

app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = "localhost"
app.config['MYSQL_USER'] = "root"
app.config['MYSQL_PASSWORD'] = ""
app.config['MYSQL_DB'] = "redcms"
app.config['MYSQL_AUTOCOMMIT'] = True

app.config['SECRET_KEY'] = 'ahsuahedwgdjsdhsbds283'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'responseandengagedirectly@gmail.com'
app.config['MAIL_PASSWORD'] = 'ylmi ymrv acrr tksv'

mail = Mail(app)

mysql = MySQL(app)

#Register Views
app.register_blueprint(views)
app.register_blueprint(utils)
app.register_blueprint(fetchData)
app.register_blueprint(report)


load_dotenv()
# Load environment variables
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
INDEX_NAME = os.getenv('INDEX_NAME')
EMBEDDING_MODEL ="text-embedding-ada-002"

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
# Initialize the OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# MongoDB connection
uri = "mongodb+srv://jonelnaquita:Admin12345@redcms.x009aew.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(uri)
db = client['redcms']

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404page.html'), 404

@app.route('/')
def home():
    # Your IPinfo API key
    ipinfo_client = apiip('889f150d-cf76-4567-96bf-ee7309aa5864')
    info = ipinfo_client.get_location()
    
    print(info)

    # Extract location data
    visitor_ip = info.get('ip')
    city = info.get('city')
    region = info.get('regionName')
    country = info.get('countryName')
    ph_time = pytz.timezone('Asia/Manila')
    timestamp = datetime.now(ph_time)

    # Save location data to MySQL database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO tblvisitors (ip_address, city, region, country, date) VALUES (%s, %s, %s, %s, %s)",
                   (visitor_ip, city, region, country, timestamp))
    mysql.connection.commit()
    cursor.close()
    
    #Save to MongoDB
    collection = db["visitors"]
    visitor_data = {
        "visitorIP": visitor_ip,
        "city": city,
        "region": region,
        "country": country,  # replace with the actual response time
        "timestamp": timestamp
    }

    # Insert the conversation data into the collection
    result = collection.insert_one(visitor_data)
    
    return render_template('index.html')

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("UTF-8"), hashed_password)

def hash_password(password):
    salt = bcrypt.gensalt(13)
    hashed_password = bcrypt.hashpw(password.encode("UTF-8"), salt)
    return hashed_password

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if the user is already logged in
    if 'login' in session and session['login']:
        return redirect(url_for('dashboard'))

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
            return render_template('login.html', message=message) 
        message = 'Email address is not registered!'    
        return render_template('login.html', message=message)          
    return render_template('login.html', message=message)


#Forgot Password Function

@app.route("/send-email", methods=["GET"])
def send_email():
    email = request.args.get("email")

    # Check if the email is registered in your database
    if is_email_registered(email):
        # Generate a random code
        reset_code = secrets.token_hex(16)  # You can adjust the length as needed
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('UPDATE tbluser SET code = %s WHERE email = %s', (reset_code, email))
        mysql.connection.commit()

        msg_title = "Reset Password"
        sender = "noreply@app.com"
        msg = Message(msg_title, sender=sender, recipients=[email])

        # Include the reset code in the email body
        msg_body = f"To reset your password, click the reset button."
        msg.body = ""

        # Pass data including the reset code to the email template
        data = {
            'app_name': "RESPONSE AND ENGAGE DIRECTLY",
            'title': msg_title,
            'body': msg_body,
            'reset_code': reset_code,
        }

        msg.html = render_template("email.html", data=data)

        # Send the email
        mail.send(msg)

        # Return a success message
        return jsonify({"status": "success", "message": "Email sent successfully! Please check your email"})
    else:
        # Return an error message
        return jsonify({"status": "error", "message": "Email not registered."})

def is_email_registered(email):
    # Connect to your MySQL database and check if the email exists
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM tbluser WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()

    return user is not None

        
@app.route('/change-user-password', methods=['GET', 'POST'])
def change_user_password():
    if request.method == "POST":
        data = request.json
        reset_code = data.get("code")
        new_password = data.get("new_password")

        # Check if the reset code is valid
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM tbluser WHERE code = %s', (reset_code,))
        user = cursor.fetchone()
        cursor.close()

        if user:
            # Hash the new password
            password_hashed = hash_password(new_password)

            # Update the user's password in the database
            cursor = mysql.connection.cursor()
            cursor.execute('UPDATE tbluser SET password = %s, code = NULL WHERE code = %s', (password_hashed, reset_code))
            mysql.connection.commit()
            cursor.close()

            return jsonify({"status": "success", "message": "Password reset successfully"})
        else:
            return jsonify({"status": "error", "message": "Invalid reset code"})
    else:
        # Handle other HTTP methods if needed
        return render_template('utils/changepassword.html')


@app.route('/dashboard')
def dashboard():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
    try:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT COUNT(DISTINCT sessionID) AS session_count, COUNT(incomingMessage) AS inMessages, ROUND(AVG(responseTime), 2) AS avg_response_time FROM tblconversations")
        data = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(botMessage) AS botMessages FROM tblconversations WHERE botMessage != ''")
        data2 = cursor.fetchone()
        
        #################################################################################################
        # Get the current data
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                
        #################################################################################################
        
        session_count = data['session_count']
        inMessage_count = data['inMessages']
        avg_response_time = data['avg_response_time']
        botMessage_count = data2['botMessages']
            
        ############################### GET VISITOR DATA ################################################
        
        cursor.execute("SELECT COUNT(ip_address) AS visitor_number FROM tblvisitors")
        visitors = cursor.fetchone()
        visitor_count = visitors['visitor_number']
        
        # Fetch the visitor count for the day and month
        current_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(ip_address) AS visitor_number FROM tblvisitors WHERE date = %s", (current_date,))
        today_visitors = cursor.fetchone()

        cursor.execute("SELECT COUNT(ip_address) AS visitor_number FROM tblvisitors WHERE MONTH(date) = MONTH(CURDATE())")
        monthly_visitors = cursor.fetchone()
        
        today_visitors = today_visitors['visitor_number']
        monthly_visitors = monthly_visitors['visitor_number']
        
        
        cursor.close()
        
        return render_template(
            'dashboard.html',
            session_count = session_count,
            inMessage_count = inMessage_count,
            botMessage_count = botMessage_count,
            avg_response_time = avg_response_time,
            visitor_count = visitor_count,
            today_visitors = today_visitors,
            monthly_visitors = monthly_visitors,
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

@app.route('/fallbacks')
def fallbacks():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    return render_template('fallbacks.html')


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
        
        ph_time = pytz.timezone('Asia/Manila')
        dateAdded = datetime.now(ph_time)

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
            cursor.execute("INSERT INTO tbldata (vectorID, dataSource, dataText, characters, status, dateAdded) VALUES (%s, %s, %s, %s, %s, %s)",(vectorID, dataSource, text, characters, status, dateAdded))
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
        office = request.form['selectOffice']

        answer = removeStyles(answer)

        # Concatenate the question and answer to create faq_text
        faqQuestion = "Question"
        faqAnswer = "Answer"
        faq_text = f"{faqQuestion}: {question} {faqAnswer}: {answer}"
        
        characters = len(faq_text)

        # Update the question and answer in MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("UPDATE tbldata SET dataFAQQuestion = %s, dataFAQAnswer = %s, office = %s, characters = %s WHERE id = %s", (question, answer, office, characters, faq_id))
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
        dataText = ""
        question = request.form['questions']
        answer = request.form['answers']
        dataSource = "FAQ"
        office = request.form['selectOffice']
        ph_time = pytz.timezone('Asia/Manila')
        dateAdded = datetime.now(ph_time)

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
            cursor.execute("INSERT INTO tbldata (vectorID, dataSource, dataText, dataFAQQuestion, dataFAQAnswer, characters, status, office, dateAdded) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", (vectorID, dataSource, dataText, question, removeStyles(answer), characters, status, office, dateAdded))
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
      
index = pinecone.Index(INDEX_NAME)

def find_match(input):
    embed_query = openai.Embedding.create(
        input=input,
        engine=EMBEDDING_MODEL
    )
    input_em = embed_query['data'][0]['embedding']
    result = index.query(input_em, top_k=3, includeMetadata=True)
    return result['matches'][0]['metadata']['text']+"\n"+result['matches'][1]['metadata']['text']+"\n"+result['matches'][2]['metadata']['text']


llm = ChatOpenAI(model_name="gpt-3.5-turbo", 
openai_api_key=OPENAI_API_KEY)

def query_refiner(conversation):

    response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=f"Provide the second question you see on the context provided. Don't rephrase anything! Keep it one question only. \n\nContext: \n{conversation}\n\n\nRefined Query:",
    temperature=0,
    max_tokens=30,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response['choices'][0]['text']


# Use the unique user identifier in conversations
user_conversation_memories = {}
print(user_conversation_memories)

# Function to set up the conversation with the user identifier
def setup_conversation(session_id):
    # Check if there's already a memory instance for this user
    if session_id not in user_conversation_memories:
        # If not, create a new instance of ConversationBufferWindowMemory for this user
        user_conversation_memories[session_id] = ConversationBufferWindowMemory(k=3, return_messages=True)
    
    # Retrieve the user's conversation memory
    conversation_memory = user_conversation_memories[session_id]
    

@app.route('/dialogflow', methods=['POST'])
def dialogflow_webhook():
    try:
        data = request.get_json()
        session_info = data['sessionInfo']['session']
        sessionID = session_info.split('/')[-1]

        # Parse the XML file
        tree = ET.parse('xml/instructions.xml')
        root = tree.getroot()
        items_text = [element.text for element in root.findall('.//item')]
        instructions = '\n'.join(items_text)
        
        setup_conversation(sessionID)
        conversation_memory = user_conversation_memories[sessionID]
        
        system_msg_template = SystemMessagePromptTemplate.from_template(template=f"""{instructions}'""")
        human_msg_template = HumanMessagePromptTemplate.from_template(template="{input}")
        prompt_template = ChatPromptTemplate.from_messages([system_msg_template, MessagesPlaceholder(variable_name="history"), human_msg_template])
        conversation = ConversationChain(memory=conversation_memory, prompt=prompt_template, llm=llm, verbose=True)

        # Record the start time before processing the request
        start_time = datetime.now()

        query = str(data['text'])
        postPrompt = str(query + " Don’t give me information not in your context.")
        print(postPrompt)
        userQuery = emoji.demojize(query)
        context = find_match(query)
        response = conversation.predict(input=f"\nContext: \n{context}\n\nQuery: \n{postPrompt}")
        botMessage = emoji.demojize(response)

        refined_query = query_refiner(context)

        ph_time = pytz.timezone('Asia/Manila')
        timestamp = datetime.now(ph_time)
        response_time = (timestamp - timestamp).total_seconds()

        # Record the end time after processing the request
        end_time = datetime.now()
        # Calculate response time in seconds
        response_time = (end_time - start_time).total_seconds()

        # Create a cursor and execute the SQL query 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO tblconversations (sessionID, incomingMessage, botMessage, responseTime, timestamp) VALUES (%s, %s, %s, %s, %s)",
                       (sessionID, userQuery, botMessage, response_time, timestamp))
        mysql.connection.commit()
        cursor.close()
        
        #Save to MongoDB
        collection = db["conversations"]
        conversation_data = {
            "sessionID": sessionID,
            "userQuery": userQuery,
            "botMessage": botMessage,
            "response_time": response_time,  # replace with the actual response time
            "timestamp": timestamp
        }

        # Insert the conversation data into the collection
        result = collection.insert_one(conversation_data)

        response_json = jsonify(
            {
                "fulfillmentResponse": {
                    "messages": [
                        {
                            "text": {
                                "text": [response]
                            }
                        },
                        {
                            "payload": {
                                "richContent": [
                                    [
                                        {
                                            "options": [
                                                {
                                                    "text": [refined_query]
                                                },
                                            ],
                                            "type": "chips"
                                        }
                                    ]
                                ],
                            },
                            "payload": {
                                "botcopy": [
                                    {
                                        "suggestions": [
                                            {
                                                "title": refined_query,
                                                "action": {
                                                    "message": {
                                                        "command": refined_query,
                                                        "type": "training"
                                                    }
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        }
                    ]
                }
            }
        )

        return response_json

    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)
        error_response = jsonify(
            {
                'fulfillment_response': {
                    'messages': [
                        {
                            'text': {
                                'text': "Sorry for the inconvenience. There's a problem with the server. Please try again later!"
                            }
                        }
                    ]
                }
            }
        )
        return error_response
    
@app.route('/dialogflow-ratings', methods=['POST'])
def dialogflow_ratings():
    data = request.get_json()
    print(json.dumps(data))
    
    session_info = data['sessionInfo']['session']  # Access the sessionInfo field
    sessionID = session_info.split('/')[-1]
    feedback = data['sessionInfo']['parameters']['feedback']
    
    ratingSatisfied = data['sessionInfo']['parameters']['rating']['satisfied']
    
    if ratingSatisfied:
        rating = "Satisfied"
    else:
        rating = "Unsatisfied"
    
    ph_time = pytz.timezone('Asia/Manila')
    timestamp = datetime.now(ph_time)
    
    # Create a cursor and execute the SQL query
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("INSERT INTO tblratings (sessionID, rating, feedback, timestamp) VALUES (%s, %s, %s, %s)",
                       (sessionID, rating, feedback, timestamp))
        mysql.connection.commit()
        
        #Save to MongoDB
        collection = db["ratings"]
        ratings_data = {
            "sessionID": sessionID,
            "rating": rating,
            "feedback": feedback,
            "timestamp": timestamp
        }

        # Insert the conversation data into the collection
        result = collection.insert_one(ratings_data)
    except Exception as e:
        # Handle any database-related errors here
        print("Database error:", str(e))
    finally:
        cursor.close()

    # Return a response to the client
    return jsonify({"message": "Rating data successfully recorded."})
    

        
if __name__ == "__main__":
    app.run(debug=True)
