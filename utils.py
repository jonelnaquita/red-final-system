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

utils = Blueprint("utils",
                __name__,
                template_folder="templates",
                static_folder="static",
                static_url_path="/static"
                )

mysql = MySQLdb.connect(
        host="localhost",
        user="root",
        password="",
        db="redcms"
    )


@utils.route('/instructions')
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

@utils.route('/get-instructions', methods=['GET'])
def get_instructions():
    try:
        # Read and parse the XML file
        tree = ElementTree(file='xml/instructions.xml')
        root = tree.getroot()

        # Extract data from the XML, including item text and ID
        items = [{'id': element.get('id'), 'text': element.text} for element in root.findall('.//item')]
    except Exception as e:
        items = []

    return jsonify(items=items)


# Initialize a counter to keep track of the item IDs
item_id_counter = 1

@utils.route('/save-instructions', methods=['POST'])
def save_instructions():
    text = request.form.get('text')

    try:
        # Load the existing XML file
        tree = ElementTree(file='xml/instructions.xml')
        root = tree.getroot()
    except Exception as e:
        # If the file doesn't exist, create a new XML structure
        root = Element("instructions")

    global item_id_counter  # Use the global counter
    item_id = str(item_id_counter)  # Convert the counter to a string for the ID

    # Create a new instruction element with an item ID
    child = Element("item", id=item_id)
    child.text = text
    root.append(child)

    # Increment the counter for the next item
    item_id_counter += 1

    # Create an ElementTree from the root element
    tree = ElementTree(root)

    # Save the updated XML to a file
    tree.write('xml/instructions.xml')

    return jsonify({"message": "Data saved to XML file"})


@utils.route('/delete-instruction/<int:id>', methods=['DELETE'])
def delete_instruction(id):
    try:
        # Load the existing XML file
        tree = ElementTree(file='xml/instructions.xml')
        root = tree.getroot()

        # Find the item to delete based on the ID
        item = root.find('.//item[@id="{}"]'.format(id))

        if item is not None:
            root.remove(item)

            # Create an ElementTree from the root element
            tree = ElementTree(root)

            # Save the updated XML to a file
            tree.write('xml/instructions.xml')

            return jsonify({"success": True, "message": "Item deleted successfully"})
        else:
            return jsonify({"success": False, "message": "Item not found"})
    except Exception as e:
        return jsonify({"success": False, "message": "Error deleting item"})
