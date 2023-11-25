def find_match(input):
    embed_query = openai.Embedding.create(
        input=input,
        engine=EMBEDDING_MODEL
    )
    input_em = embed_query['data'][0]['embedding']
    result = index.query(input_em, top_k=3, includeMetadata=True)
    return result['matches'][0]['metadata']['text']+"\n"+result['matches'][1]['metadata']['text']+"\n"+result['matches'][2]['metadata']['text']

conversation_memory = ConversationBufferWindowMemory(k=3, return_messages=True)

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
        response = conversation.predict(input=f"\n\nContext:\n {context} \n\nQuery:\n{postPrompt}\n")
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