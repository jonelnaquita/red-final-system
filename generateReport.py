from flask import Flask, Blueprint, render_template, request, make_response, Response, redirect, url_for, session, flash, jsonify, send_file
import uuid
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import pytz
import MySQLdb.cursors
import json
import re
import bcrypt
import requests
import os
import pdfkit
import csv
from io import BytesIO, StringIO
from utils import db
import nltk
from nltk.tokenize import word_tokenize

report = Blueprint("report",
                __name__,
                template_folder="templates",
                static_folder="static",
                static_url_path="/static"
                )

#User Engagement PDF
conversations_collection = db["conversations"]
ratings_collection = db['ratings']
platforms_collection = db['platforms']

@report.route('/generate-engagement-line-report')
def generateEngagementLineReport():
    # Get date range from request parameters
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")

    # Parse date strings to datetime objects
    date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
    date_to = datetime.strptime(date_to_str, '%Y-%m-%d')
    
    # Generate a list of all dates within the range
    all_dates = [date_from + timedelta(days=x) for x in range((date_to - date_from).days + 1)]

    # Query data for the specified date range
    pipeline = [
        {"$match": {"timestamp": {"$gte": date_from, "$lte": date_to}}},
        {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}, "sessions": {"$addToSet": "$sessionID"}}},
        {"$project": {"_id": 0, "date": "$_id", "sessions": {"$size": "$sessions"}}}
    ]

    data = list(conversations_collection.aggregate(pipeline))

    # Create a dictionary to store the counts for each date
    date_counts = {record["date"]: record["sessions"] for record in data}

    # Ensure all dates within the range are present in the dictionary
    all_date_strs = [date.strftime('%Y-%m-%d') for date in all_dates]

    # Create a list of tuples (date, sessions) and sort it
    sorted_date_counts = sorted(
        [(date_str, date_counts.get(date_str, 0)) for date_str in all_date_strs],
        key=lambda x: x[0]
    )

    date_labels, session_data = zip(*sorted_date_counts)

    # Zipping data for the template
    zipped_data = zip(date_labels, session_data)

    # Render the HTML template with the data
    rendered_template = render_template(
        'report/pdfEngagementLineReport.html',
        date_from=date_from_str,
        date_to=date_to_str,
        zipped_data=zipped_data  # Pass the zipped data to the template
    )

    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

    date_today = datetime.now().strftime('%Y-%m-%d')

    # Configure PDF options
    pdf_options = {
        'page-size': 'Letter',
        'orientation': 'Portrait',
        'encoding': "UTF-8",
    }

    # Generate PDF from HTML template
    pdf = pdfkit.from_string(rendered_template, False, options=pdf_options, configuration=config)

    # Create response with PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    filename = f"User_Engagement_Data_{date_today}.pdf"
    response.headers['Content-Disposition'] = f'inline; filename={filename}'

    return response

#User Engagement CSV

@report.route("/generate-user-engagement-data-csv")
def generate_csv():
    try:
        # Get date range from request parameters
        date_from_str = request.args.get("date_from")
        date_to_str = request.args.get("date_to")

        # Parse date strings to datetime objects
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d')

        # Query data for the specified date range
        pipeline = [
            {"$match": {"timestamp": {"$gte": date_from, "$lte": date_to}}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}}, "sessions": {"$addToSet": "$sessionID"}}},
            {"$project": {"_id": 0, "date": "$_id", "sessions": {"$size": "$sessions"}}}
        ]

        data = list(conversations_collection.aggregate(pipeline))

        # Create a dictionary to store the counts for each date
        date_counts = {record["date"]: record["sessions"] for record in data}

        # Generate a list of all dates within the range
        all_dates = [date_from + timedelta(days=x) for x in range((date_to - date_from).days + 1)]

        # Ensure all dates within the range are present in the dictionary
        all_date_strs = [date.strftime('%Y-%m-%d') for date in all_dates]
        for date_str in all_date_strs:
            date_counts.setdefault(date_str, 0)

        # Prepare CSV data
        csv_data = []
        for index, (date, sessions) in enumerate(sorted(date_counts.items()), start=1):
            csv_data.append([index, date, sessions])

        # Format filename with today's date
        today_date_str = datetime.now().strftime('%Y-%m-%d')
        csv_filename = f"User Engagement Report - {today_date_str}.csv"

        # Create CSV file
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerow(["No.", "Date", "Sessions"])
        csv_writer.writerows(csv_data)

        # Serve the file as a response
        response = make_response(csv_buffer.getvalue().encode('utf-8'))
        response.headers["Content-Disposition"] = f"attachment; filename={csv_filename}"
        response.headers["Content-type"] = "text/csv"

        # Use send_file directly
        return send_file(
            BytesIO(response.data),
            as_attachment=True,
            download_name=csv_filename,
            mimetype='text/csv',
        )
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})


    
#Generate PDF for Satisfaction Data    

@report.route("/generate-satisfaction-data-report", methods=["GET"])
def generate_satisfaction_data_report():
    date_from_str = request.args.get("dateFrom")
    date_to_str = request.args.get("dateTo")

    if date_from_str is None or date_to_str is None:
        # Handle the case where date_from or date_to is not provided
        return jsonify({"error": "Invalid date range"})

    # Convert date strings to datetime objects
    date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
    date_to = datetime.strptime(date_to_str, "%Y-%m-%d")

    # Query to fetch sessionID, rating, and feedback for the specified date range
    data = list(ratings_collection.find(
        {"timestamp": {"$gte": date_from, "$lte": date_to}},
        {"sessionID": 1, "rating": 1, "feedback": 1, "_id": 0}
    ))

    # Render PDF template with the data
    rendered_template = render_template(
        'report/pdfSatisfactionReport.html',
        date_from=date_from_str,
        date_to=date_to_str,
        satisfaction_data=data
    )

    config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')

    # Configure PDF options
    pdf_options = {
        'page-size': 'Letter',
        'orientation': 'Portrait',
        'encoding': "UTF-8",
    }

    # Generate PDF from HTML template
    pdf = pdfkit.from_string(rendered_template, False, options=pdf_options, configuration=config)

    # Create response with PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=satisfaction_report.pdf'

    return response

#Generate CSV

@report.route("/generate-ratings-csv", methods=["GET"])
def generate_ratings_csv():
    date_from_str = request.args.get("dateFrom")
    date_to_str = request.args.get("dateTo")

    if date_from_str is None or date_to_str is None:
        # Handle the case where date_from or date_to is not provided
        return jsonify({"error": "Invalid date range"})

    # Convert date strings to datetime objects
    date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
    date_to = datetime.strptime(date_to_str, "%Y-%m-%d")

    # Query to fetch sessionID, rating, feedback, and timestamp for the specified date range
    data = list(ratings_collection.find(
        {"timestamp": {"$gte": date_from, "$lte": date_to}},
        {"sessionID": 1, "rating": 1, "feedback": 1, "timestamp": 1, "_id": 0}
    ))

    # Prepare CSV data
    csv_data = [['No.', 'SessionID', 'Ratings', 'Feedback', 'Date']]

    for index, entry in enumerate(data, start=1):
        session_id = entry.get('sessionID', '')
        rating = entry.get('rating', '')
        feedback = entry.get('feedback', '')
        date = entry.get('timestamp', '').strftime('%Y-%m-%d') if entry.get('timestamp') else ''

        csv_data.append([index, session_id, rating, feedback, date])

    # Format filename with today's date
    today_date_str = datetime.now().strftime('%Y-%m-%d')
    csv_filename = f"Ratings Report - {today_date_str}.csv"

    # Create CSV file
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerows(csv_data)

    # Serve the file as a response
    response = make_response(csv_buffer.getvalue().encode('utf-8'))
    response.headers["Content-Disposition"] = f"attachment; filename={csv_filename}"
    response.headers["Content-type"] = "text/csv"

    return response


@report.route("/generate-platformcost-csv", methods=["GET"])
def generate_platformcost_csv():
    try:
        # Get the current year
        current_year = datetime.now().year

        # Get the selected year from the request query parameters
        selected_year = request.args.get('year', str(current_year))
        if selected_year == '':
            selected_year = current_year
        selected_year = int(selected_year)  # Convert to integer

        # Define the match condition for the current year
        match_condition = {"$expr": {"$eq": [{"$year": "$timestamp"}, selected_year]}}

        # Define the months in chronological order
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

        # Initialize dictionaries to store data for each month
        total_tokens_per_month_gpt = {month: 0 for month in months}
        total_cost_per_month_gpt = {month: 0 for month in months}
        total_requests_per_month_dialogflow = {month: 0 for month in months}
        total_cost_per_month_dialogflow = {month: 0 for month in months}

        # Retrieve the cost of GPT 3.5 Turbo and Dialogflow CX from the platforms collection
        gpt_cost_document = platforms_collection.find_one({"name": "GPT 3.5 Turbo"})
        gpt_cost = float(gpt_cost_document.get("cost", 0))  # Convert cost to float

        dialogflow_cost_document = platforms_collection.find_one({"name": "Dialogflow CX"})
        dialogflow_cost = float(dialogflow_cost_document.get("cost", 0))  # Convert cost to float

        # Query data based on the match condition
        bot_messages = conversations_collection.find({"$and": [{"botMessage": {"$exists": True}}, match_condition]})

        # Calculate the total tokens used and total cost per month for GPT 3.5 Turbo
        for message in bot_messages:
            month = message["timestamp"].strftime("%b").upper()
            tokens = word_tokenize(message["botMessage"])
            total_tokens_per_month_gpt[month] += len(tokens)
            total_cost_per_month_gpt[month] += (len(tokens) / 1000) * gpt_cost  # Calculate cost for every 1k tokens

        # Retrieve Dialogflow CX requests from the conversations collection
        dialogflow_requests = conversations_collection.find({"$and": [{"botMessage": {"$exists": True}}, match_condition]})

        # Calculate the total requests and total cost per month for Dialogflow CX
        for in_request in dialogflow_requests:
            month = in_request["timestamp"].strftime("%b").upper()
            total_requests_per_month_dialogflow[month] += 1
            total_cost_per_month_dialogflow[month] += dialogflow_cost

        # Prepare CSV data
        csv_data = [['Month', 'Total Tokens Used (GPT)', 'GPT Cost', 'Total Requests (Dialogflow)', 'Dialogflow Cost', 'Total Cost']]
        for month in months:
            total_tokens_used_gpt = total_tokens_per_month_gpt[month]
            total_cost_gpt = round(total_cost_per_month_gpt[month], 2)  # Limit to 2 decimal places
            total_requests_dialogflow = total_requests_per_month_dialogflow[month]
            total_cost_dialogflow = round(total_cost_per_month_dialogflow[month], 2)  # Limit to 2 decimal places
            total_cost = round(total_cost_gpt + total_cost_dialogflow, 2)  # Total cost
            csv_data.append([month, total_tokens_used_gpt, total_cost_gpt, total_requests_dialogflow, total_cost_dialogflow, total_cost])

        today_date_str = datetime.now().strftime('%Y-%m-%d')
        csv_filename = f"Ratings_Report_{today_date_str}.csv"

        # Create CSV file in memory
        csv_buffer = StringIO()
        csv_writer = csv.writer(csv_buffer)
        csv_writer.writerows(csv_data)

        # Serve the file as a response
        response = make_response(csv_buffer.getvalue().encode('utf-8'))
        response.headers["Content-Disposition"] = f"attachment; filename={csv_filename}"
        response.headers["Content-type"] = "text/csv"

        return response

    except Exception as e:
        return jsonify({"error": str(e)})

