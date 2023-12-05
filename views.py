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

views = Blueprint("views",
                __name__,
                template_folder="templates",
                static_folder="static",
                static_url_path="/static"
                )

@views.route('/instructions')
def instructions():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
    try:
        # Read and parse the XML file
        tree = ElementTree(file='xml/instructions.xml')
        root = tree.getroot()

        # Extract data from the XML, including item text and ID
        items = [{'id': element.get('id'), 'text': element.text} for element in root.findall('.//item')]
    except Exception as e:
        items = []

    return render_template('instructions.html', items=items)

@views.route('/user-engagement')
def userEngagement():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
    return render_template('userengagement.html')

@views.route('/user-satisfaction')
def userSatisfaction():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
    return render_template('usersatisfaction.html')
    
    
conversations_collection = db['conversations']

@views.route('/conversation-length')
def conversation_length():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))

    # MongoDB Aggregation Pipeline
    pipeline = [
        {
            '$sort': {'timestamp': -1}  # Sort in descending order based on timestamp
        },
        {
            '$group': {
                '_id': '$sessionID',
                'max_timestamp': {'$first': '$timestamp'},
                'session_data': {'$first': '$$ROOT'}  # Preserve the entire document for the latest timestamp
            }
        },
        {
            '$project': {
                '_id': 0,
                'sessionID': '$_id',
                'timestamp': '$max_timestamp',
                'incomingMessage': '$session_data.userQuery',
                'botMessage': '$session_data.botMessage'
            }
        }
    ]

    # Execute the aggregation pipeline
    sessions = list(conversations_collection.aggregate(pipeline))

    return render_template('conversationlength.html', sessions=sessions)

@views.route('/privacy-policy')
def privacyPolicy():

    return render_template('privacypolicy.html')

@views.route('/forgot-password')
def forgotPassword():

    return render_template('utils/forgotpassword.html')

@views.route('/user-guidelines')
def userGuidelines():
    
    return render_template('userguidelines.html')
