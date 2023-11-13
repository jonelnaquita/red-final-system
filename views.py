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
    
@views.route('/conversation-length')
def conversationLength():
    if 'login' not in session or not session['login']:
        # If 'login' session variable is not set or is False, redirect to login page
        return redirect(url_for('login'))
    
    # Fetch sessions with their most recent messages from the database
    cursor = mysql.cursor(MySQLdb.cursors.DictCursor)
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
    
    return render_template('conversationlength.html', sessions=sessions)
