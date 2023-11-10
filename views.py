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
