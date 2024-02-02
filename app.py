from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from bson import ObjectId

from datetime import datetime, timedelta
from apiip import apiip
import pytz
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

app.config['SECRET_KEY'] = 'ahsuahedwgdjsdhsbds283'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'responseandengagedirectly@gmail.com'
app.config['MAIL_PASSWORD'] = 'ylmi ymrv acrr tksv'

mail = Mail(app)

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
MONGODB_URI = os.getenv('MONGODB_URI')

# Initialize Pinecone
pinecone.init(api_key=PINECONE_API_KEY, environment=PINECONE_ENV)
# Initialize the OpenAI Embeddings
embeddings = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)

# MongoDB connection
client = MongoClient(MONGODB_URI)
db = client['redcms']

conversations_collection = db["conversations"]
admin_collection = db["admin"]
data_collection = db['data']
documents_collection = db['documents']
platforms_collection = db["platforms"]


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
    timestamp = datetime.today()
    
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

def check_password_login(password, hashed_password):
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

        user = admin_collection.find_one({"email": email})

        if user:
            hashed_password = user.get('password', '')
            if check_password_login(password, hashed_password):
                session['login'] = True
                session['admin'] = user.get('userID', '')
                session['email'] = user.get('email', '')

                return redirect(url_for('dashboard'))
            message = 'Wrong password!'
        else:
            message = 'Email address is not registered!'

    return render_template('login.html', message=message)
#Forgot Password Function

@app.route('/dashboard')
def dashboard():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
#Forgot Password Function

@app.route("/send-email", methods=["GET"])
def send_email():
    email = request.args.get("email")

    # Check if the email is registered in your MongoDB collection
    if is_email_registered(email):
        # Generate a random code
        reset_code = secrets.token_hex(16)  # You can adjust the length as needed

        # Update the reset code in the MongoDB collection
        admin_collection.update_one({"email": email}, {"$set": {"code": reset_code}})

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
    # Check if the email exists in the MongoDB collection
    return admin_collection.find_one({"email": email}) is not None

    return user is not None

        
@app.route('/change-user-password', methods=['GET', 'POST'])
def change_user_password():
    if request.method == "POST":
        data = request.json
        reset_code = data.get("code")
        new_password = data.get("new_password")

        # Check if the reset code is valid
        user = admin_collection.find_one({"code": reset_code})

        if user:
            # Hash the new password
            password_hashed = hash_password(new_password)

            # Update the user's password and reset the code in the MongoDB collection
            admin_collection.update_one(
                {"code": reset_code},
                {"$set": {"password": password_hashed, "code": ""}}
            )

            return jsonify({"status": "success", "message": "Password reset successfully"})
        else:
            return jsonify({"status": "error", "message": "Invalid reset code"})
    else:
        # Handle other HTTP methods if needed
        return render_template('utils/changepassword.html')

@app.route('/get-platform-cost')
def platform_cost():
    platforms = list(platforms_collection.find({}))
    # Convert ObjectId to string
    for platform in platforms:
        platform['_id'] = str(platform['_id'])
    return jsonify(platforms)

@app.route('/manage')
def manage_datasource():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
    # Fetch data from the MongoDB collections
    data_text = data_collection.find({'dataSource': 'Text'})
    data_FAQ = data_collection.find({'dataSource': 'FAQ'})
    
    # Fetch data from the MongoDB collections for total sources, processed, and error
    total_sources = data_collection.count_documents({})
    processed = documents_collection.count_documents({'status': 'Processed'})
    error = documents_collection.count_documents({'status': 'Error'})
    
    return render_template('datasource.html', data=data_text, dataFAQ=data_FAQ, total_sources=total_sources, processed=processed, error=error)

#Delete Text Data
@app.route('/delete_selected', methods=['POST'])
def delete_selected_rows():
    try:
        selected_ids = request.form.getlist('selected_ids[]')  # Get the selected row IDs
        selected_ids = [ObjectId(id) for id in selected_ids]  # Convert IDs to ObjectId
        
        if len(selected_ids) == 0:
            return jsonify({'success': False, 'message': 'No rows selected for deletion'})
        
        # Step 1: Fetch Vector IDs associated with selected IDs
        cursor = data_collection.find({'_id': {'$in': selected_ids}}, {'vectorID': 1})
        vector_ids = [doc['vectorID'] for doc in cursor]

        # Step 2: Delete the rows from MongoDB
        result = data_collection.delete_many({'_id': {'$in': selected_ids}})
        
        # Step 3: Use Pinecone to delete the vectors
        index = pinecone.Index(INDEX_NAME)
        index.delete(ids=vector_ids)  # Delete vectors using Vector IDs
        
        return jsonify({'success': True, 'message': f'{result.deleted_count} rows deleted successfully'})
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
    pipeline = [
        {
            "$sort": {"timestamp": -1}
        },
        {
            "$group": {
                "_id": "$sessionID",
                "max_timestamp": {"$first": "$timestamp"},
                "incomingMessage": {"$first": "$userQuery"},
                "botMessage": {"$first": "$botMessage"}
            }
        },
        {
            "$sort": {"max_timestamp": -1}
        }
    ]

    sessions = list(conversations_collection.aggregate(pipeline))

    # Format timestamps to strings
    for session_data in sessions:
        session_data["timestamp"] = session_data["max_timestamp"].strftime('%Y-%m-%d %H:%M:%S')

    return render_template('conversations.html', sessions=sessions)


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'login' not in session or not session['login']:
        return redirect(url_for('login'))

    if request.method == 'POST':
        current_password = request.form['current_password']
        new_email = request.form['new_email']

        user = admin_collection.find_one({"userID": session['admin']}, {"email": 1, "password": 1})

        if user:
            if new_email == user['email']:
                flash('This email is already in use. Please choose a different email address.', 'danger')
            else:
                hashed_password = user.get('password', b'')
                if bcrypt.checkpw(current_password.encode("utf-8"), hashed_password):
                    admin_collection.update_one({"userID": session['admin']}, {"$set": {"email": new_email}})
                    flash('Email address updated successfully!', 'success')
                    return redirect(url_for('settings'))
                else:
                    flash('Incorrect password. Please try again.', 'danger')
        else:
            flash('User not found.', 'danger')

    user = admin_collection.find_one({"userID": session['admin']}, {"email": 1})
    current_email = user.get('email', '') if user else ''
    
    return render_template('settings.html', current_email=current_email)

def check_password(password, hashed_password):
    return bcrypt.checkpw(password.encode("UTF-8"), hashed_password)

def generate_password_hash(password):
    salt = bcrypt.gensalt(13)
    hashed_password = bcrypt.hashpw(password.encode("UTF-8"), salt)
    return hashed_password

#CHANGE PASSWORD
@app.route('/change-password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        current_password = request.form['current_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Check if the user exists and the current password is correct
        user = admin_collection.find_one({"userID": session.get('admin', 0)})

        if user is None:
            flash('User not found.', 'danger')
        elif not check_password(current_password, user.get('password', '')):
            flash('Incorrect current password.', 'danger')
        elif new_password != confirm_password:
            flash('New password and confirm password do not match.', 'danger')
        else:
            try:
                # Update the user's password in the database
                password_hashed = generate_password_hash(new_password)
                admin_collection.update_one(
                    {"userID": session.get('admin', 0)},
                    {"$set": {"password": password_hashed}}
                )

                flash('Password updated successfully!', 'success')
                return redirect(url_for('settings'))
            except Exception as e:
                # Handle database or other errors
                flash(f'An error occurred: {str(e)}', 'danger')

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
    conversation = list(conversations_collection.find(
        {"sessionID": session_id},
        {"timestamp": 1, "userQuery": 1, "botMessage": 1, "_id": 0}
    ).sort("timestamp", 1))

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

        text_data.append(text)
        
        ph_time = pytz.timezone('Asia/Manila')
        dateAdded = datetime.today()

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

            # Insert data into MongoDB collections
            data_collection.insert_one({
                'vectorID': vectorID,
                'dataSource': dataSource,
                'dataText': text,
                'characters': characters,
                'status': status,
                'dateAdded': dateAdded
            })

            documents_collection.insert_one({'status': status})

            return jsonify({"message": "Data source added successfully"})

        except Exception as e:
            # Handle exceptions and insert "Error" status into tbldocuments
            status = "Error"
            documents_collection.insert_one({'status': status})
            return jsonify({"message": f"An error occurred: {str(e)}"})

    return "Invalid request"


# Update Data from a Text
@app.route('/edit-text-vector', methods=['POST'])
def editTextData():
    if request.method == 'POST':
        text_id = request.form['textId']  # Get the ID from the form
        text = request.form['updateText']
        
        object_id = ObjectId(text_id)

        text = removeStyles(text)
        text_data.append(text)

        characters = len(text)

        data_collection.update_one({'_id': object_id}, {'$set': {'dataText': text, 'characters': characters}})

        # Retrieve the updated data from MongoDB
        updated_data = data_collection.find_one({'_id': object_id}, {'dataText': 1, 'vectorID': 1})

        if updated_data:
            updated_text = updated_data.get('dataText')  # Use get method to safely retrieve values
            vectorID = updated_data.get('vectorID')
            
            print(vectorID)

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
        else:
            return jsonify({"message": "No document found for the given id."})

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

        # Update the question and answer in MongoDB
        data_collection.update_one(
            {'_id': ObjectId(faq_id)},
            {'$set': {
                'dataFAQQuestion': question,
                'dataFAQAnswer': answer,
                'office': office,
                'characters': characters
            }}
        )

        # Retrieve the updated data from MongoDB
        updated_data = data_collection.find_one({'_id': ObjectId(faq_id)}, {'dataFAQQuestion': 1, 'dataFAQAnswer': 1, 'vectorID': 1})

        if updated_data:
            updated_question = updated_data['dataFAQQuestion']
            updated_answer = updated_data['dataFAQAnswer']
            vectorID = updated_data['vectorID']
        else:
            updated_question = None
            updated_answer = None
            vectorID = None

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

                # Query Pinecone for similar vectors (Assuming INDEX_NAME is already defined)
                index = pinecone.Index(INDEX_NAME)
                index.update(id=vectorID, values=test_vector, set_metadata={'text': updated_faq_text})

                return jsonify({"message": "Data source updated successfully"})
            except Exception as e:
                return jsonify({"message": f"Error updating data in Pinecone: {str(e)}"})
        else:
            return jsonify({"message": "No question and answer found for the given id. Cannot update data in Pinecone."})

    return "Invalid request"


# Insert data from a FAQ
@app.route('/save-faq', methods=['POST'])
def save_faq():
    if request.method == 'POST':
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

            # Assuming `embeddings` and `INDEX_NAME` are already defined
            text_store = Pinecone.from_texts([faq_text], embeddings, index_name=INDEX_NAME)

            # Create an OpenAI embedding
            test_bed = openai.Embedding.create(
                input=[faq_text],
                engine=EMBEDDING_MODEL
            )

            test_vector = test_bed['data'][0]['embedding']

            # Query Pinecone for similar vectors (Assuming INDEX_NAME is already defined)
            index = pinecone.Index(INDEX_NAME)
            data_from_pc = index.query(vector=test_vector, top_k=3, include_values=True)
            vectorID = data_from_pc['matches'][0]['id']

            characters = len(faq_text)
            status = "Processed"

            # Insert data into MongoDB
            data_document = {
                "vectorID": vectorID,
                "dataSource": dataSource,
                "dataFAQQuestion": question,
                "dataFAQAnswer": answer,
                "characters": characters,
                "status": status,
                "office": office,
                "dateAdded": dateAdded
            }
            data_collection.insert_one(data_document)

            # Insert "Processed" status into documents_collection
            documents_collection.insert_one({"status": status})

            return jsonify({"message": "FAQ saved successfully"})
        
        except Exception as e:
            # Handle exceptions and insert "Error" status into documents_collection
            status = "Error"
            documents_collection.insert_one({"status": status})
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

def userQuery_refiner(conversation, query):

    response = openai.Completion.create(
    model="gpt-3.5-turbo-instruct",
    prompt=f"Given the following user query and conversation log, formulate a question that would be the most relevant to provide the user with an answer from a knowledge base. If the query is not related, don't rephrase the query.\n\nCONVERSATION LOG: \n{conversation}\n\nQuery: {query}\n\nRefined Query:",
    temperature=0,
    max_tokens=50,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response['choices'][0]['text']

# Use the unique user identifier in conversations
user_conversation_memories = {}

# Function to set up the conversation with the user identifier
def setup_conversation(session_id):
    if session_id not in user_conversation_memories:
        user_conversation_memories[session_id] = ConversationBufferWindowMemory(k=2, return_messages=True)
    
    conversation_memory = user_conversation_memories[session_id]

# Use a dictionary to store limited conversation history for each session
MAX_HISTORY_ENTRIES = 2
conversation_history = {}

def get_conversation_string(session_id):
    if session_id in conversation_history:
        session_history = conversation_history[session_id]
        conversation_string = "\n".join(session_history)
        return conversation_string
    return ""

@app.route('/dialogflow', methods=['POST'])
def dialogflow_webhook():
    try:
        
        if 'responses' not in session:
            session['responses'] = ["hi"]

        if 'requests' not in session:
            session['requests'] = []
            
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
        postPrompt = str(query + " Don’t give me answer NOT AVAILABLE from your context.")

        # Get conversation string before updating
        conversation_string_before = get_conversation_string(sessionID)
        print("Before:", conversation_string_before)
        
        refined_userQuery = userQuery_refiner(conversation_string_before, query)
        print("Refined Query: " + refined_userQuery)
        
        userQuery = emoji.demojize(query)
        context = find_match(refined_userQuery)
        response = conversation.predict(input=f"\nContext: \n{context}\n\nQuery: \n{postPrompt}")
        botMessage = emoji.demojize(response)
        
        #Append Request and Response to Conversation String
        session['requests'].append(query)
        session['responses'].append(response)
        
        # Update conversation history for the current session
        current_history = conversation_history.get(sessionID, [])
        current_history.append(f"Human: {query}")
        current_history.append(f"Bot: {response}")

        # Keep only the first two entries
        conversation_history[sessionID] = current_history[-2:]

        # Get conversation string after updating
        conversation_string_after = get_conversation_string(sessionID)
        print("After:", conversation_string_after)

        refined_query = query_refiner(context)

        ph_time = pytz.timezone('Asia/Manila')
        timestamp = datetime.today()
        response_time = (timestamp - timestamp).total_seconds()

        # Record the end time after processing the request
        end_time = datetime.now()
        # Calculate response time in seconds
        response_time = (end_time - start_time).total_seconds()
        
        #Save to MongoDB
        collection = db["conversations"]
        conversation_data = {
            "sessionID": sessionID,
            "userQuery": query,
            "botMessage": response,
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
    
    timestamp = datetime.today()

    try:
        
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
