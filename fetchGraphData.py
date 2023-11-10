from flask import Flask, Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import uuid
from xml.etree.ElementTree import Element, ElementTree
from flask_mysqldb import MySQL
from datetime import datetime, timedelta
import pytz
import MySQLdb.cursors
import json
import re
import bcrypt
import requests
import os
from utils import mysql

fetchData = Blueprint("fetchData",
                __name__,
                template_folder="templates",
                static_folder="static",
                static_url_path="/static"
                )

#################### DASHBOARD DATA ##########################

@fetchData.route('/performance-linechart-data', methods=['GET'])
def get_performance_linechart_data():
    try:
        # Get the current date
        ph_time = pytz.timezone('Asia/Manila')
        today = datetime.now(ph_time)
        
        # Calculate the start and end dates for the current week (Monday to Sunday)
        start_of_week = today - timedelta(days=(today.weekday() + 0) % 7)
        end_of_week = start_of_week + timedelta(days=6)

        # Calculate the start and end dates for the previous week
        start_of_last_week = start_of_week - timedelta(days=7)
        end_of_last_week = start_of_last_week + timedelta(days=6)
        
        cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
        
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
        days = ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"]
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

        data = {
            'days': days,
            'current_week_session_data': current_week_session_data,
            'last_week_session_data': last_week_session_data
        }
        # Return the data as JSON
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
    
@fetchData.route('/performance-barchart-data', methods=['GET'])
def get_performanceBarChartData():
    try:
        # Connect to the MySQL database
        cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
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

        # Close the cursor and the database connection
        cursor.close()

        # Return the data as JSON
        data = {"months": months, "session_counts": session_month}
        
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
    
    
@fetchData.route('/session-summary-data', methods=['GET'])
def get_session_summary_data():
    try:

        ph_time = pytz.timezone('Asia/Manila')
        today = datetime.now(ph_time)

        # Calculate the start and end dates for the current week (Monday to Sunday)
        start_of_week = today - timedelta(days=(today.weekday() + 0) % 7)
        end_of_week = start_of_week + timedelta(days=6)

        cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
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
        
        data = {
            'current_week_data': current_week_data,
            'total_sessions': total_sessions
        }

        # Return the data as JSON
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
    
    
@fetchData.route('/ratings-data', methods=['GET'])
def get_ratings_data():
    try:
        cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
        # Query to count the number of satisfied and unsatisfied ratings
        cursor.execute("SELECT *, rating, COUNT(DISTINCT sessionID) as rating_number FROM tblratings GROUP BY rating")
        result = cursor.fetchall()

        data = {}
        for row in result:
            rating = row['rating']
            count = row['rating_number']
            data[rating.lower()] = count
        cursor.close()
    
        # Return the data as JSON
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
    
######################### END OF DASHBOARD DATA #########################    

######################### USER ENGAGEMENT ###############################

@fetchData.route('/user-engagement-data', methods=['GET'])
def user_engagement_data():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, return an empty response
        return jsonify(error="Not logged in")

    end_date = datetime.now()
    start_date = end_date - timedelta(days=6)

    date_counts = {}

    current_date = start_date
    while current_date <= end_date:
        date_counts[current_date.strftime('%Y-%m-%d')] = 0
        current_date += timedelta(days=1)

    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT DATE(timestamp) AS date, COUNT(DISTINCT sessionID) AS sessions FROM tblconversations WHERE DATE(timestamp) BETWEEN %s AND %s GROUP BY date", (start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')))
    data = cursor.fetchall()
    cursor.close()

    for record in data:
        date_str = record["date"].strftime('%Y-%m-%d')
        date_counts[date_str] = record["sessions"]

    return jsonify({"date_labels": list(date_counts.keys()), "session_data": list(date_counts.values())})

@fetchData.route("/fetch-user-engagement", methods=["GET"])
def fetch_user_engagement():
    # Generate the date range dynamically
    today = datetime.now().date()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1) - timedelta(days=1))

    date_range = [first_day_of_month.strftime('%Y-%m-%d'), last_day_of_month.strftime('%Y-%m-%d')]

    # Check if the current date is within the date range
    if today < first_day_of_month or today > last_day_of_month:
        return jsonify(error="Data is not available for the current month")

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
    
    response = {'labels': date_labels, 'data': session_data}

    return jsonify(response)

@fetchData.route("/filter-user-engagement-data", methods=["GET"])
def filter_engagement_data():
    date_from_str = request.args.get("date_from")
    date_to_str = request.args.get("date_to")

    # Parse date strings to datetime objects
    date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
    date_to = datetime.strptime(date_to_str, '%Y-%m-%d')

    # Generate a list of all dates within the range
    all_dates = [date_from + timedelta(days=x) for x in range((date_to - date_from).days)]

    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT DATE(timestamp) AS date, COUNT(DISTINCT sessionID) AS sessions FROM tblconversations WHERE DATE(timestamp) BETWEEN %s AND %s GROUP BY date",
        (date_from, date_to),
    )
    data = cursor.fetchall()
    cursor.close()

    # Create a dictionary to store the counts for each date
    date_counts = {date.strftime('%Y-%m-%d'): 0 for date in all_dates}

    # Update the dictionary with counts from the MySQL query
    for record in data:
        date_str = record["date"].strftime('%Y-%m-%d')
        date_counts[date_str] = record["sessions"]
        
    response = {"date_labels": list(date_counts.keys()), "session_data": list(date_counts.values())}

    return jsonify(response)

######################### END OF USER ENGAGEMENT ###############################

######################### FETCH USER SATISFACTION ##############################
@fetchData.route("/fetch-ratings", methods=["GET"])
def fetch_ratings():
    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)

    # Query to count the number of satisfied and unsatisfied ratings
    cursor.execute("SELECT rating, COUNT(DISTINCT sessionID) as rating_number FROM tblratings GROUP BY rating")
    results = cursor.fetchall()
    cursor.close()

    total_ratings = sum(result["rating_number"] for result in results)
    satisfied_number = next((result["rating_number"] for result in results if result["rating"] == "Satisfied"), 0)
    unsatisfied_number = next((result["rating_number"] for result in results if result["rating"] == "Unsatisfied"), 0)

    satisfied_percentage = (satisfied_number / total_ratings) * 100 if total_ratings != 0 else 0
    unsatisfied_percentage = (unsatisfied_number / total_ratings) * 100 if total_ratings != 0 else 0
    
    data = {
        "total_ratings": total_ratings,
        "satisfied_number": satisfied_number,
        "unsatisfied_number": unsatisfied_number,
        "satisfied_percentage": satisfied_percentage,
        "unsatisfied_percentage": unsatisfied_percentage
    }
    return jsonify(data)