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
from utils import mysql

report = Blueprint("report",
                __name__,
                template_folder="templates",
                static_folder="static",
                static_url_path="/static"
                )

#User Engagement PDF

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

    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)

    # Query data for the specified date range
    cursor.execute(
        "SELECT DATE(timestamp) AS date, COUNT(DISTINCT sessionID) AS sessions "
        "FROM tblconversations "
        "WHERE DATE(timestamp) BETWEEN %s AND %s "
        "GROUP BY date",
        (date_from, date_to),
    )
    data = cursor.fetchall()

    # Create a dictionary to store the counts for each date
    date_counts = {date.strftime('%Y-%m-%d'): 0 for date in all_dates}

    # Update the dictionary with counts from the MySQL query
    for record in data:
        date_str = record["date"].strftime('%Y-%m-%d')
        date_counts[date_str] = record["sessions"]

    date_labels=list(date_counts.keys())
    session_data=list(date_counts.values())
    
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
    # Get date range from request parameters
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")

    # Parse date strings to datetime objects
    date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
    date_to = datetime.strptime(date_to_str, '%Y-%m-%d')

    # Generate a list of all dates within the range
    all_dates = [date_from + timedelta(days=x) for x in range((date_to - date_from).days + 1)]

    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)

    # Query data for the specified date range
    cursor.execute(
        "SELECT DATE(timestamp) AS date, COUNT(DISTINCT sessionID) AS sessions "
        "FROM tblconversations "
        "WHERE DATE(timestamp) BETWEEN %s AND %s "
        "GROUP BY date",
        (date_from, date_to),
    )
    data = cursor.fetchall()

    # Create a dictionary to store the counts for each date
    date_counts = {date.strftime('%Y-%m-%d'): 0 for date in all_dates}

    # Update the dictionary with counts from the MySQL query
    for record in data:
        date_str = record["date"].strftime('%Y-%m-%d')
        date_counts[date_str] = record["sessions"]

    # Prepare CSV data
    csv_data = []
    for index, (date, sessions) in enumerate(date_counts.items(), start=1):
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

    cursor.close()

    # Use send_file directly
    return send_file(
        BytesIO(response.data),
        as_attachment=True,
        download_name=csv_filename,
        mimetype='text/csv',
    )


@report.route("/generate-engagement-data-report")
def generateUserEngagementReport():
    # Get the current date range for the current month
    current_month = datetime.now().strftime('%B %Y')
     
    today = datetime.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1) - timedelta(days=1))

    date_from_str = first_day_of_month.strftime('%Y-%m-%d')
    date_to_str = last_day_of_month.strftime('%Y-%m-%d')

    # Generate a list of all dates within the range
    all_dates = [first_day_of_month + timedelta(days=x) for x in range((last_day_of_month - first_day_of_month).days + 1)]

    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)

    # Query data for the specified date range
    cursor.execute(
        "SELECT DATE(timestamp) AS date, COUNT(DISTINCT sessionID) AS sessions "
        "FROM tblconversations "
        "WHERE DATE(timestamp) BETWEEN %s AND %s "
        "GROUP BY date",
        (first_day_of_month, last_day_of_month),
    )
    data = cursor.fetchall()

    # Create a dictionary to store the counts for each date
    date_counts = {date.strftime('%Y-%m-%d'): 0 for date in all_dates}

    # Update the dictionary with counts from the MySQL query
    for record in data:
        date_str = record["date"].strftime('%Y-%m-%d')
        date_counts[date_str] = record["sessions"]

    date_labels = list(date_counts.keys())
    session_data = list(date_counts.values())

    # Calculate total engagement for the current month
    total_engagement = sum(session_data)

    # Zipping data for the template
    zipped_data = zip(date_labels, session_data)

    # Render the HTML template with the data
    rendered_template = render_template(
        'report/pdfEngagementDataReport.html',
        date_from=date_from_str,
        date_to=date_to_str,
        current_month=current_month,  # Pass the current month to the template
        zipped_data=zipped_data,  # Pass the zipped data to the template
        total_engagement=total_engagement  # Pass the total engagement to the template
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

    cursor.close()

    # Create response with PDF
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'inline; filename=report.pdf'

    return response

#Generate CSV
@report.route("/generate-engagement-month-csv")
def generateEngagementMonthCSV():
    # Generate the date range dynamically
    today = datetime.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1) - timedelta(days=1))

    # Generate a list of all dates within the range
    all_dates = [first_day_of_month + timedelta(days=x) for x in range((last_day_of_month - first_day_of_month).days + 1)]
    date_labels = []
    session_data = []

    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)

    for date in all_dates:
        date_str = date.strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(DISTINCT sessionID) AS sessions FROM tblconversations WHERE DATE(timestamp) = %s", (date_str,))
        data = cursor.fetchone()

        date_labels.append(date_str)
        session_data.append(data["sessions"] if data else 0)

    cursor.close()

    # Prepare CSV data
    csv_data = []
    for index, (date, sessions) in enumerate(zip(date_labels, session_data), start=1):
        csv_data.append([index, date, sessions])

    # Format filename with today's date
    today_date_str = datetime.now().strftime('%Y-%m-%d')
    csv_filename = f"User_Engagement_Report_{today_date_str}.csv"

    # Create CSV file
    csv_buffer = StringIO()
    csv_writer = csv.writer(csv_buffer)
    csv_writer.writerow(["No.", "Date", "Number of Users"])
    csv_writer.writerows(csv_data)

    # Serve the file as a response
    response = make_response(csv_buffer.getvalue().encode('utf-8'))
    response.headers["Content-Disposition"] = f"attachment; filename={csv_filename}"
    response.headers["Content-type"] = "text/csv"

    return send_file(BytesIO(response.data),
                     as_attachment=True,
                     download_name=csv_filename,
                     mimetype='text/csv')
    
#Generate PDF for Satisfaction Data    

@report.route("/generate-satisfaction-data-report", methods=["GET"])
def generate_satisfaction_data_report():
    date_from = request.args.get("dateFrom")
    date_to = request.args.get("dateTo")

    if date_from is None or date_to is None:
        # Handle the case where date_from or date_to is not provided
        return jsonify({"error": "Invalid date range"})

    # Convert date strings to datetime objects
    date_from = datetime.strptime(date_from, "%Y-%m-%d")
    date_to = datetime.strptime(date_to, "%Y-%m-%d")

    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)

    # Query to fetch sessionID, rating, and feedback for the specified date range
    cursor.execute(
        "SELECT DISTINCT sessionID, rating, feedback "
        "FROM tblratings "
        "WHERE timestamp BETWEEN %s AND %s",
        (date_from, date_to),
    )
    data = cursor.fetchall()
    cursor.close()

    # Render PDF template with the data
    rendered_template = render_template(
        'report/pdfSatisfactionReport.html',
        date_from=date_from.strftime('%Y-%m-%d'),
        date_to=date_to.strftime('%Y-%m-%d'),
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
    # Get date range from request parameters
    date_from_str = request.args.get("dateFrom")
    date_to_str = request.args.get("dateTo")

    if date_from_str is None or date_to_str is None:
        # Handle the case where date_from or date_to is not provided
        return jsonify({"error": "Invalid date range"})

    # Convert date strings to datetime objects
    date_from = datetime.strptime(date_from_str, "%Y-%m-%d")
    date_to = datetime.strptime(date_to_str, "%Y-%m-%d")

    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)

    # Query to fetch sessionID, rating, and feedback for the specified date range
    cursor.execute(
        "SELECT DISTINCT sessionID, rating, feedback, timestamp "
        "FROM tblratings "
        "WHERE timestamp BETWEEN %s AND %s",
        (date_from, date_to),
    )
    data = cursor.fetchall()
    cursor.close()

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

