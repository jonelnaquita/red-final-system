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
from utils import db

from bson.son import SON

fetchData = Blueprint("fetchData",
                __name__,
                template_folder="templates",
                static_folder="static",
                static_url_path="/static"
                )

################### HORIZONTAL DASHBOARD #####################

#SessionID Increase/Decrease
@fetchData.route("/fetch-session-change", methods=["GET"])
def fetch_session_change():
    try:
        # Calculate date ranges for this week and last week
        today = datetime.today()
        
        this_week_start = today - timedelta(days=(today.weekday() + 1) % 7)
        this_week_end = this_week_start + timedelta(days=6)

        # Calculate the start and end dates for the previous week
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = last_week_start + timedelta(days=6)

        # Query unique sessions for last week and this week based on sessionID
        last_week_sessions = len(set(db["conversations"].distinct("sessionID", {
            "timestamp": {"$gte": last_week_start, "$lte": last_week_end}
        })))

        this_week_sessions = len(set(db["conversations"].distinct("sessionID", {
            "timestamp": {"$gte": this_week_start, "$lte": this_week_end}
        })))

        # Calculate the percentage change
        percentage_change = ((this_week_sessions - last_week_sessions) / last_week_sessions) * 100 if last_week_sessions != 0 else 100

        # Count the number of added sessions from last week
        added_sessions = this_week_sessions - last_week_sessions

        # Prepare the response
        response = {
            'percentage_change': round(percentage_change, 1),  # Round to one decimal place
            'added_sessions_last_week': added_sessions
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})


#Visitor Increase/Decrease
@fetchData.route("/fetch-visitor-change", methods=["GET"])
def fetch_visitor_change():
    try:
        # Calculate date ranges for this week and last week
        today = datetime.today()
        this_week_start = today - timedelta(days=(today.weekday() + 1) % 7)
        this_week_end = this_week_start + timedelta(days=6)

        # Calculate the start and end dates for the previous week
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = last_week_start + timedelta(days=6)

        # Query unique visitors for last week and this week based on IP address
        last_week_visitors = len(set(db["visitors"].distinct("visitorIP", {
            "timestamp": {"$gte": last_week_start, "$lte": last_week_end}
        })))

        this_week_visitors = len(set(db["visitors"].distinct("visitorIP", {
            "timestamp": {"$gte": this_week_start, "$lte": this_week_end}
        })))

        # Calculate the percentage change
        percentage_change = ((this_week_visitors - last_week_visitors) / last_week_visitors) * 100

        # Count the number of added visitors from last week
        added_visitors = this_week_visitors - last_week_visitors

        # Prepare the response
        response = {
            'percentage_change': round(percentage_change, 1),  # Round to one decimal place
            'added_visitors': added_visitors
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})


@fetchData.route("/fetch-inmessages-change", methods=["GET"])
def fetch_inmessages_change():
    try:
        # Calculate date ranges for this week and last week
        today = datetime.today()
        this_week_start = today - timedelta(days=(today.weekday() + 1) % 7)
        this_week_end = this_week_start + timedelta(days=6)

        # Calculate the start and end dates for the previous week
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = last_week_start + timedelta(days=6)

        # Query to count the number of incoming messages for last week and this week
        last_week_inmessages = db["conversations"].count_documents({
            "timestamp": {"$gte": last_week_start, "$lte": last_week_end}
        })

        this_week_inmessages = db["conversations"].count_documents({
            "timestamp": {"$gte": this_week_start, "$lte": this_week_end}
        })

        # Calculate the percentage change
        percentage_change = ((this_week_inmessages - last_week_inmessages) / last_week_inmessages) * 100 if last_week_inmessages != 0 else 100

        # Count the number of added incoming messages from last week
        added_inmessages = this_week_inmessages - last_week_inmessages

        # Prepare the response
        response = {
            'percentage_change': round(percentage_change, 1),  # Round to one decimal place
            'added_inmessages': added_inmessages
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})


@fetchData.route("/fetch-botresponse-change", methods=["GET"])
def fetch_botresponse_change():
    try:
        # Calculate date ranges for this week and last week
        today = datetime.today()
        this_week_start = today - timedelta(days=(today.weekday() + 1) % 7)
        this_week_end = this_week_start + timedelta(days=6)

        # Calculate the start and end dates for the previous week
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = last_week_start + timedelta(days=6)

        # Query to count the number of bot responses for last week and this week
        last_week_botresponses = db["conversations"].count_documents({
            "timestamp": {"$gte": last_week_start, "$lte": last_week_end},
            "botMessage": {"$exists": True}
        })

        this_week_botresponses = db["conversations"].count_documents({
            "timestamp": {"$gte": this_week_start, "$lte": this_week_end},
            "botMessage": {"$exists": True}
        })

        # Calculate the percentage change
        percentage_change = ((this_week_botresponses - last_week_botresponses) / last_week_botresponses) * 100 if last_week_botresponses != 0 else 100

        # Count the number of added bot responses from last week
        added_botresponse = this_week_botresponses - last_week_botresponses

        # Prepare the response
        response = {
            'percentage_change': round(percentage_change, 1),  # Round to one decimal place
            'added_botresponse': added_botresponse
        }

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})


@fetchData.route("/fetch-averageresponse-change", methods=["GET"])
def fetch_averageresponse_change():
    try:
        # Calculate date ranges for this week and last week
        today = datetime.today()
        this_week_start = today - timedelta(days=(today.weekday() + 1) % 7)
        this_week_end = this_week_start + timedelta(days=6)

        # Calculate the start and end dates for the previous week
        last_week_start = this_week_start - timedelta(days=7)
        last_week_end = last_week_start + timedelta(days=6)

        # Query to calculate average response time for last week
        last_week_aggregate = db["conversations"].aggregate([
            {"$match": {"timestamp": {"$gte": last_week_start, "$lte": last_week_end}}},
            {"$group": {"_id": None, "average_response": {"$avg": "$response_time"}}}
        ])

        # Query to calculate average response time for this week
        this_week_aggregate = db["conversations"].aggregate([
            {"$match": {"timestamp": {"$gte": this_week_start, "$lte": this_week_end}}},
            {"$group": {"_id": None, "average_response": {"$avg": "$response_time"}}}
        ])

        # Extract average response time from aggregation result
        last_week_averageresponse = next(last_week_aggregate, {}).get("average_response", 0)
        this_week_averageresponse = next(this_week_aggregate, {}).get("average_response", 0)

        # Calculate the percentage change
        if last_week_averageresponse == 0:
            percentage_change = float('inf')  # Positive infinity for no average response last week
        else:
            percentage_change = ((this_week_averageresponse - last_week_averageresponse) / last_week_averageresponse) * 100

        added_response = round(this_week_averageresponse - last_week_averageresponse, 2)

        response = {'percentage_change': round(percentage_change, 1),
                    'added_response': added_response}

        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)})


#################### DASHBOARD DATA ##########################
conversations_collection = db["conversations"]
visitors_collection = db["visitors"]

@fetchData.route('/dashboard')
def dashboard():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))

    try:
        # Get conversation data
        sessionIDCount = conversations_collection.aggregate([
            {"$group": {"_id": "$sessionID"}}
        ])
        
        conversation_data = conversations_collection.aggregate([
            {"$group": {"_id": None, 
                        "inMessages_count": {"$sum": {"$cond": {"if": {"$ne": ["$userQuery", ""]}, "then": 1, "else": 0}}},
                        "avg_response_time": {"$avg": "$response_time"},
                        "botMessages_count": {"$sum": {"$cond": {"if": {"$ne": ["$botMessage", ""]}, "then": 1, "else": 0}}}
                        }
            }
        ])
        
        session_count = len(list(sessionIDCount))
        data = next(conversation_data, {})
        inMessage_count = data.get('inMessages_count', 0)
        avg_response_time = round(data.get('avg_response_time', 0), 2)
        botMessage_count = data.get('botMessages_count', 0)

        # Get visitor data
        visitor_count = visitors_collection.count_documents({})

        # Fetch the visitor count for the day and month

        current_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        today_visitors = visitors_collection.count_documents({"timestamp": {"$gte": current_date}})
        print(today_visitors)

        monthly_visitors = visitors_collection.count_documents({"timestamp": {"$gte": current_date.replace(day=1), "$lt": current_date + timedelta(days=1)}})
        print(monthly_visitors)


        return render_template(
            'dashboard.html',
            session_count=session_count,
            inMessage_count=inMessage_count,
            botMessage_count=botMessage_count,
            avg_response_time=avg_response_time,
            visitor_count=visitor_count,
            today_visitors=today_visitors,
            monthly_visitors=monthly_visitors,
        )

    except Exception as e:
        return jsonify({"error": str(e)})


@fetchData.route('/performance-linechart-data', methods=['GET'])
def get_performance_linechart_data():
    try:
        today = datetime.today()

        # Calculate the start and end dates for the current week (Monday to Sunday)
        start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
        end_of_week = start_of_week + timedelta(days=6)

        # Calculate the start and end dates for the previous week
        start_of_last_week = start_of_week - timedelta(days=7)
        end_of_last_week = start_of_last_week + timedelta(days=6)

        # MongoDB aggregation pipeline for the current week
        current_week_pipeline = [
            {"$match": {"timestamp": {"$gte": start_of_week, "$lte": end_of_week}}},
            {"$group": {"_id": {"$dayOfWeek": "$timestamp"}, "session_count": {"$addToSet": "$sessionID"}}},
            {"$project": {"day": "$_id", "session_count": {"$size": "$session_count"}}},
            {"$sort": {"day": 1}}
        ]

        # MongoDB aggregation pipeline for the previous week
        last_week_pipeline = [
            {"$match": {"timestamp": {"$gte": start_of_last_week, "$lte": end_of_last_week}}},
            {"$group": {"_id": {"$dayOfWeek": "$timestamp"}, "session_count": {"$addToSet": "$sessionID"}}},
            {"$project": {"day": "$_id", "session_count": {"$size": "$session_count"}}},
            {"$sort": {"day": 1}}
        ]

        # Execute the MongoDB aggregations
        current_week_data = list(conversations_collection.aggregate(current_week_pipeline))
        last_week_data = list(conversations_collection.aggregate(last_week_pipeline))

        # Prepare data for JavaScript (current and last week's session data)
        days = ["SUNDAY", "MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY"]
        current_week_session_data = [0, 0, 0, 0, 0, 0, 0]  # Initialize data for each day of the current week
        last_week_session_data = [0, 0, 0, 0, 0, 0, 0]  # Initialize data for each day of the previous week

        for row in current_week_data:
            day_index = row.get('day', 0) - 1  # Adjust day index to match the "days" list
            current_week_session_data[day_index] = row.get('session_count', 0)

        for row in last_week_data:
            day_index = row.get('day', 0) - 1  # Adjust day index to match the "days" list
            last_week_session_data[day_index] = row.get('session_count', 0)

        data = {
            'days': days,
            'current_week_session_data': current_week_session_data,
            'last_week_session_data': last_week_session_data
        }

        # Return the data as JSON
        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})

#BarChart MongoDB

@fetchData.route('/performance-barchart-data', methods=['GET'])
def get_performanceBarChartDataMongoDB():
    try:
        collection = db["conversations"]
        
        # Query data for total sessions per month
        pipeline = [
            {
                "$group": {
                    "_id": {"$month": "$timestamp"},
                    "session_count": {"$addToSet": "$sessionID"}
                }
            },
            {
                "$project": {
                    "month": "$_id",
                    "session_count": {"$size": "$session_count"}
                }
            }
        ]

        monthly_session_data = list(collection.aggregate(pipeline))

        # Prepare data for JavaScript
        months = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]
        session_month = [0] * 12  # Initialize data for each month

        for row in monthly_session_data:
            month_index = row['month'] - 1  # MongoDB months are 1-based
            session_month[month_index] = row['session_count']

        # Return the data as JSON
        data = {"months": months, "session_counts": session_month}

        return jsonify(data)

    except Exception as e:
        return jsonify({"error": str(e)})
    
    
@fetchData.route('/session-summary-data', methods=['GET'])
def get_session_summary_data():
    try:
        # Get the current date
        ph_time = pytz.timezone('Asia/Manila')
        today = datetime.now(ph_time)

        # Calculate the start and end dates for the current week (Monday to Sunday)
        start_of_week = today - timedelta(days=(today.weekday() + 1) % 7)
        end_of_week = start_of_week + timedelta(days=6)

        # MongoDB aggregation pipeline for the current week
        collection = db["conversations"]
        current_week_pipeline = [
            {"$match": {"timestamp": {"$gte": start_of_week, "$lte": end_of_week}}},
            {"$group": {"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                        "session_count": {"$addToSet": "$sessionID"}}},
            {"$project": {"day": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                          "session_count": {"$size": "$session_count"}}}
        ]

        # Execute the MongoDB aggregation
        current_week_data = list(collection.aggregate(current_week_pipeline))

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
    

ratings_collection = db['ratings']  
@fetchData.route('/ratings-data', methods=['GET'])
def get_ratings_data():
    try:
        # Equivalent MongoDB aggregation pipeline
        pipeline = [
            {
                "$group": {
                    "_id": "$rating",
                    "rating_number": {"$addToSet": "$sessionID"},
                    "count": {"$sum": 1}
                }
            }
        ]

        result = list(ratings_collection.aggregate(pipeline))

        data = {}
        for row in result:
            rating = row['_id']
            count = len(row['rating_number'])
            data[rating.lower()] = count

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

    end_date = datetime.today()
    start_date = end_date - timedelta(days=6)

    date_counts = {}

    current_date = start_date
    while current_date <= end_date:
        date_counts[current_date.strftime('%Y-%m-%d')] = 0
        current_date += timedelta(days=1)

    # Equivalent MongoDB aggregation pipeline
    pipeline = [
        {
            "$match": {
                "timestamp": {"$gte": start_date, "$lte": end_date}
            }
        },
        {
            "$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                "sessions": {"$addToSet": "$sessionID"}
            }
        },
        {
            "$project": {
                "_id": 0,
                "date": "$_id",
                "sessions": {"$size": "$sessions"}
            }
        }
    ]

    result = list(conversations_collection.aggregate(pipeline))

    for record in result:
        date_str = record["date"]
        date_counts[date_str] = record["sessions"]

    return jsonify({"date_labels": list(date_counts.keys()), "session_data": list(date_counts.values())})



@fetchData.route("/fetch-user-engagement", methods=["GET"])
def fetch_user_engagement():
    try:
        # Generate the date range dynamically
        today = datetime.today()
        first_day_of_month = today.replace(day=1)
        last_day_of_month = (first_day_of_month.replace(month=first_day_of_month.month % 12 + 1) - timedelta(days=1))

        # Define the date range for MongoDB query
        date_range = {
            '$gte': datetime.combine(first_day_of_month, datetime.min.time()),
            '$lt': datetime.combine(last_day_of_month + timedelta(days=1), datetime.min.time())
        }

        # MongoDB Aggregation Pipeline
        pipeline = [
            {
                '$match': {
                    'timestamp': date_range
                }
            },
            {
                '$group': {
                    '_id': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
                    'sessions': {'$addToSet': '$sessionID'}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'date': '$_id',
                    'sessions': {'$size': '$sessions'}
                }
            },
            {
                '$sort': {'date': 1}
            }
        ]

        # Execute the aggregation pipeline
        result = list(conversations_collection.aggregate(pipeline))

        # Extract dates and sessions from the fetched data
        date_labels = [entry["date"] for entry in result]
        session_data = [entry["sessions"] for entry in result]

        response = {'labels': date_labels, 'data': session_data}

        return jsonify(response)

    except Exception as e:
        # Handle exceptions appropriately (e.g., log the error)
        return jsonify(error=str(e))


@fetchData.route("/filter-user-engagement-data", methods=["GET"])
def filter_engagement_data():
    try:
        date_from_str = request.args.get("date_from")
        date_to_str = request.args.get("date_to")

        # Parse date strings to datetime objects
        date_from = datetime.strptime(date_from_str, '%Y-%m-%d')
        date_to = datetime.strptime(date_to_str, '%Y-%m-%d')

        # Generate a list of all dates within the range
        all_dates = [date_from + timedelta(days=x) for x in range((date_to - date_from).days + 1)]

        # Equivalent MongoDB aggregation pipeline
        pipeline = [
            {
                "$match": {
                    "timestamp": {"$gte": date_from, "$lte": date_to}
                }
            },
            {
                "$group": {
                    "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$timestamp"}},
                    "sessions": {"$addToSet": "$sessionID"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "date": "$_id",
                    "sessions": {"$size": "$sessions"}
                }
            }
        ]

        result = list(conversations_collection.aggregate(pipeline))

        # Create a dictionary to store the counts for each date
        date_counts = {date.strftime('%Y-%m-%d'): 0 for date in all_dates}

        # Update the dictionary with counts from the MongoDB query
        for entry in result:
            date_str = entry["date"]
            date_counts[date_str] = entry["sessions"]

        response = {"date_labels": list(date_counts.keys()), "session_data": list(date_counts.values())}

        return jsonify(response)

    except Exception as e:
        # Handle exceptions appropriately (e.g., log the error)
        return jsonify(error=str(e))

######################### END OF USER ENGAGEMENT ###############################

######################### FETCH USER SATISFACTION ##############################
@fetchData.route("/fetch-ratings", methods=["GET"])
def fetch_ratings():
    try:
        # Get the current month
        current_month = datetime.now().strftime('%Y-%m')

        # Equivalent MongoDB aggregation pipeline
        # MongoDB Aggregation Pipeline
        pipeline = [
            {
                '$match': {
                    'timestamp': {
                        '$gte': datetime.strptime(current_month, '%Y-%m'),
                        '$lt': datetime.strptime(current_month, '%Y-%m') + timedelta(days=31)
                    }
                }
            },
            {
                '$group': {
                    '_id': '$rating',
                    'rating_number': {'$addToSet': '$sessionID'},
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'rating': '$_id',
                    'rating_number': {'$size': '$rating_number'},
                    'count': 1
                }
            }
        ]

        result = list(ratings_collection.aggregate(pipeline))

        total_ratings = sum(entry["rating_number"] for entry in result)
        satisfied_number = next((entry["rating_number"] for entry in result if entry["rating"] == "Satisfied"), 0)
        unsatisfied_number = next((entry["rating_number"] for entry in result if entry["rating"] == "Unsatisfied"), 0)

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

    except Exception as e:
        # Handle exceptions appropriately (e.g., log the error)
        return jsonify(error=str(e))

######################## FETCH USER SATISFACTION CHART DATA #####################

@fetchData.route("/fetch-ratings-chart", methods=["GET"])
def fetch_ratings_chart():
    # Get date range from request
    date_from = datetime.strptime(request.args.get("dateFrom"), "%Y-%m-%d")
    date_to = datetime.strptime(request.args.get("dateTo"), "%Y-%m-%d")

    # Generate a list of all dates within the range (including the end date)
    all_dates = [date_from + timedelta(days=x) for x in range((date_to - date_from).days + 1)]

    # Initialize dictionaries to store data for each date
    data_by_date = {date.strftime('%Y-%m-%d'): {"Satisfied": 0, "Unsatisfied": 0} for date in all_dates}

    # MongoDB Aggregation Pipeline
    pipeline = [
        {
            '$match': {
                'timestamp': {
                    '$gte': date_from,
                    '$lte': date_to
                }
            }
        },
        {
            '$group': {
                '_id': {
                    'rating_date': {'$dateToString': {'format': '%Y-%m-%d', 'date': '$timestamp'}},
                    'rating': '$rating'
                },
                'rating_number': {'$addToSet': '$sessionID'}
            }
        },
        {
            '$group': {
                '_id': '$_id.rating_date',
                'ratings': {
                    '$push': {
                        'rating': '$_id.rating',
                        'rating_number': {'$size': '$rating_number'}
                    }
                }
            }
        },
        {
            '$project': {
                '_id': 0,
                'rating_date': '$_id',
                'ratings': 1
            }
        },
        {
            '$sort': {'rating_date': 1}
        }
    ]

    results = list(ratings_collection.aggregate(pipeline))

    # Update the dictionaries with the fetched data
    for result in results:
        rating_date = result["rating_date"]
        for rating_data in result["ratings"]:
            rating_type = rating_data["rating"]
            data_by_date[rating_date][rating_type] = rating_data["rating_number"]

    # Convert the data to the required format
    labels = list(data_by_date.keys())
    satisfied_data = [data["Satisfied"] for data in data_by_date.values()]
    unsatisfied_data = [data["Unsatisfied"] for data in data_by_date.values()]

    data = {
        "labels": labels,
        "satisfied_data": satisfied_data,
        "unsatisfied_data": unsatisfied_data
    }

    return jsonify(data)

####################### FETCH CONVERSATION LENGTH ############################

@fetchData.route("/filter-conversation-length", methods=["GET"])
def filter_conversation_length():
    date_from = request.args.get("date_from")
    
    # Convert the date string to a datetime object
    selected_date = datetime.strptime(date_from, "%Y-%m-%d").date()

    # MongoDB Aggregation Pipeline
    pipeline = [
        {
            '$match': {
                'timestamp': {
                    '$gte': datetime.combine(selected_date, datetime.min.time()),
                    '$lt': datetime.combine(selected_date + timedelta(days=1), datetime.min.time())
                }
            }
        },
        {
            '$lookup': {
                'from': 'ratings',
                'localField': 'sessionID',
                'foreignField': 'sessionID',
                'as': 'ratings'
            }
        },
        {
            '$group': {
                '_id': '$sessionID',
                'first_conversation_time': {'$min': '$timestamp'},
                'last_conversation_time': {'$max': '$timestamp'},
                'conversation_length': {'$addToSet': '$timestamp'},
                'rating': {'$max': '$ratings.rating'}
            }
        },
        {
            '$project': {
                '_id': 0,
                'sessionID': '$_id',
                'conversationLength': {
                    '$divide': [
                        {'$subtract': [{'$max': '$conversation_length'}, {'$min': '$conversation_length'}]},
                        60000
                    ]
                },
                'rating': {'$ifNull': ['$rating', None]}
            }
        }
    ]

    result = list(conversations_collection.aggregate(pipeline))

    # Map sessionIDs to user numbers
    user_number_mapping = {session['sessionID']: f"User #{index + 1}" for index, session in enumerate(result)}

    # Modify the response to include user numbers
    sessionID = [user_number_mapping[row["sessionID"]] for row in result]
    conversationLength = [row["conversationLength"] for row in result]
    ratings = [row["rating"] for row in result]

    # Prepare the response
    response = {
        "sessionID": sessionID,
        "conversationLength": conversationLength,
        "ratings": ratings
    }

    return jsonify(response)


#################### FETCH THE MESSAGES ##############################

@fetchData.route('/fetch-user-data/<session_id>')
def fetch_user_data(session_id):
    try:
        # MongoDB Aggregation Pipeline
        pipeline = [
            {
                '$match': {
                    'sessionID': session_id
                }
            },
            {
                '$lookup': {
                    'from': 'ratings',
                    'localField': 'sessionID',
                    'foreignField': 'sessionID',
                    'as': 'ratings'
                }
            },
            {
                '$group': {
                    '_id': '$sessionID',
                    'timestamp': {'$first': '$timestamp'},
                    'user_messages': {'$first': '$userQuery'},
                    'bot_messages': {'$first': '$botMessage'},
                    'conversation_length': {'$addToSet': '$timestamp'},
                    'rating': {'$max': '$ratings.rating'}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'session_id': '$_id',
                    'timestamp': 1,
                    'user_messages': 1,
                    'bot_messages': 1,
                    'conversation_length': {
                        '$divide': [
                            {'$subtract': [{'$max': '$conversation_length'}, {'$min': '$conversation_length'}]},
                            60000
                        ]
                    },
                    'rating': {'$ifNull': ['$rating', 'No Rating']}
                }
            },
            {
                '$sort': {'timestamp': -1}
            }
        ]

        result = list(conversations_collection.aggregate(pipeline))

        if result:
            # Convert ObjectId to str for JSON serialization
            result[0]['session_id'] = str(result[0]['session_id'])
            result[0]['timestamp'] = result[0]['timestamp'].strftime("%d/%m/%Y at %H:%M")

            return jsonify(result[0])
        else:
            return jsonify({"error": "Session not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)})

    

@fetchData.route('/fetch-users-data')
def fetchUsersData():
    try:
        # Get the date from the input field
        date_from = request.args.get("date_from")
        
        # Convert the date string to a datetime object
        selected_date = datetime.strptime(date_from, "%Y-%m-%d").date()

        # MongoDB Aggregation Pipeline
        pipeline = [
            {
                '$match': {
                    'timestamp': {
                        '$gte': datetime.combine(selected_date, datetime.min.time()),
                        '$lt': datetime.combine(selected_date + timedelta(days=1), datetime.min.time())
                    }
                }
            },
            {
                '$lookup': {
                    'from': 'ratings',
                    'localField': 'sessionID',
                    'foreignField': 'sessionID',
                    'as': 'ratings'
                }
            },
            {
                '$group': {
                    '_id': '$sessionID',
                    'conversation_length': {'$addToSet': '$timestamp'},
                    'rating': {'$max': '$ratings.rating'}
                }
            },
            {
                '$project': {
                    '_id': 0,
                    'user_number': {'$add': [{'$indexOfArray': [['$sessionID'], '$_id']}, 1]},
                    'session_id': '$_id',
                    'conversation_length': {
                        '$divide': [
                            {'$round': [
                                {'$divide': [
                                    {'$subtract': [{'$max': '$conversation_length'}, {'$min': '$conversation_length'}]},
                                    60000
                                ]},
                                2  # Specify the number of decimal places
                            ]},
                            1
                        ]
                    },
                    'ratings': {'$ifNull': ['$rating', 'No Rating']}
                }
            },
            {
                '$sort': {'user_number': 1}
            }
        ]

        result = list(conversations_collection.aggregate(pipeline))

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)})
    

@fetchData.route('/fetch-conversation', methods=['GET'])
def get_conversation():
    try:
        session_id = request.args.get('sessionID')

        # MongoDB find query to get the conversation for the given session ID
        conversation = list(conversations_collection.find(
            {'sessionID': session_id},
            {'timestamp': 1, 'userQuery': 1, 'botMessage': 1}
        ).sort('timestamp', 1))

        # Convert ObjectId to string for JSON serialization
        for message in conversation:
            message['_id'] = str(message['_id'])

        return jsonify(conversation)

    except Exception as e:
        return jsonify({"error": str(e)})