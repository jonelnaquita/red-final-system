conversation_memory = ConversationBufferWindowMemory(
    k=3,
    return_messages=True
    )

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

def retrieval_answer(query, doc_db, llm, conversation_memory):
    
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=doc_db.as_retriever(),
    )
    
    result = qa.run(query)
    conversation_memory.save_context({"input": query}, {"output": result})
    
    return result

@app.route('/dialogflow', methods=['POST'])
def dialogflow_webhook():
    llm = ChatOpenAI()
    doc_db = embedding_db()
    
    data = request.get_json()
    print(json.dumps(data))
    
    try:
        # Record the start time before processing the request
        start_time = datetime.now()
        
        session_info = data['sessionInfo']['session']  # Access the sessionInfo field
        sessionID = session_info.split('/')[-1]
        query = data['text']
        response = retrieval_answer(query, doc_db, llm, conversation_memory)
        ph_time = pytz.timezone('Asia/Manila')
        timestamp = datetime.now(ph_time)
        response_time = (timestamp - timestamp).total_seconds()
        
        # Record the end time after processing the request
        end_time = datetime.now()
        # Calculate response time in seconds
        response_time = (end_time - start_time).total_seconds()
        
        if session_info == session_info:
            # Append the response to the conversation memory
            conversation_memory.save_context({"input": query}, {"output": response})
            # You can access and review the conversation history using conversation_memory
            conversation_history = conversation_memory.load_memory_variables({})
            print(conversation_history)
        
        # Check if the MySQL connection is established
        if mysql.connection is None:
            raise Exception("MySQL connection is not established.")
        
        # Create a cursor and execute the SQL query
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("INSERT INTO tblconversations (sessionID, incomingMessage, botMessage, responseTime, timestamp) VALUES (%s, %s, %s, %s, %s)", (sessionID, query, response, response_time, timestamp))
        mysql.connection.commit()
        cursor.close()
    
        response_json = jsonify(
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
        
        return response_json
        
    except Exception as e:
        error_message = f"Error: {str(e)}"
        print(error_message)  # Print the error message to the console
        error_response = jsonify(
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
        return error_response