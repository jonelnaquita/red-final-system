@app.route('/register')

def register():
    email = "20-67814@g.batstate-u.edu.ph"
    password = "admin123"
    hashed_password = hash_password(password)  # Hash the password
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO tbluser (email, password) VALUES (%s, %s)", (email, hashed_password))
    mysql.connection.commit()
    cursor.close()
    
    flash('You have successfully registered!', 'success')
    return redirect(url_for('login'))  # Redirect to the login page after registration

    return render_template('login.html')

@app.route('/createAccount')
def createAccount():
    email = "jonel.naquita@gmail.com"
    password = "admin"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # Insert the user's email and hashed password into the database
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO tbluser (email, password) VALUES (%s, %s)", (email, hashed_password))
    mysql.connection.commit()
    cursor.close()

    # Optionally, you can set a session variable or display a message
    session['registered'] = True

    return redirect(url_for('login'))  # Redirect to the login page after successful registration


@app.route('/save-faq', methods=['POST'])
def save_faq():
    if request.method == 'POST':
        questions = request.form.getlist('questions[]')
        answers = request.form.getlist('answers[]')
        dataSource = "FAQ"
        status = "Processed"

        # Check if the number of questions and answers match
        if len(questions) != len(answers):
            return jsonify({"error": "Number of questions and answers do not match"})

        # Save each FAQ as a separate vector in Pinecone
        for i in range(len(questions)):
            question = questions[i]
            answer = answers[i]
            
            # Create a unique identifier for each FAQ (e.g., using a prefix)
            faq_id = f"faq_{i}"
            
            # Append the FAQ to the text_data list
            appendAnswer = text_data.append(f"{faq_id}: {question}\n{faq_id}: {answer}")
            text_store = Pinecone.from_texts([f"{faq_id}: {question}\n{faq_id}: {answer}"], embeddings, index_name=INDEX_NAME)
            
            characters = len(answers)
            
            # Create a query to save in MySQL
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute("INSERT INTO tbldata (dataSource, dataFAQQuestion, dataFAQAnswer, characters, status) VALUES (%s, %s, %s, %s, %s)", (dataSource, questions, answers, characters, status))
            mysql.connection.commit()
            cursor.close()
            

        return jsonify({"message": "FAQs saved successfully"})
