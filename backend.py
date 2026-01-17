# backend.py - Groceria Flask Backend
# Author - Vedanth Yellai

from flask import Flask, render_template, request, jsonify # used for the API
import sqlite3 # Used for the database

app = Flask(__name__) # in simple wording, this sets up a means for a connection between the front and back


# Creates the database table if it doesn't exist yet
def init_db():
    conn = sqlite3.connect('grocery.db') # sets up a conenction to the database and creates the database if not made yet
    cursor = conn.cursor()
    
    cursor.execute(' CREATE TABLE IF NOT EXISTS grocery_history (item TEXT,list_number INTEGER) ')
    
    conn.commit()
    conn.close()


# Calculates what the next list number should be
def get_next_list_number():
    conn = sqlite3.connect('grocery.db') 
    cursor = conn.cursor()
    
    cursor.execute('SELECT MAX(list_number) FROM grocery_history') # gets the max value from the list_number column
    result = cursor.fetchone()[0]
    
    conn.close()
    
    if result:
        return result + 1
    else:
        return 1


# Switches to the home page
@app.route('/')
def home():
    return render_template('Home.html')


# Switches to the edit page
@app.route('/edit')
def edit():
    return render_template('Edit.html')

#Switches to the view lists page
@app.route('/view-lists')
def view_list():
    return render_template('ViewLists.html')

# Saves the current lis tin the database right before resetting
@app.route('/api/save-list', methods=['POST'])
def save_list():
    try:
        data = request.json # saves all the items int he form of an array in a dictionary variable
        items = data.get('items', []) # accesses the value of the items key in the data dictionary
        
        # sends a message to the front end so that it knows that there is nothing there
        if not items:
            return jsonify({
                "status": "error",
                "message": "No items to save"
            })
        
        list_number = get_next_list_number() # used when saving the current list on the edit page
        
        conn = sqlite3.connect('grocery.db')
        cursor = conn.cursor()
        
        for item in items:
            cursor.execute('INSERT INTO grocery_history (item, list_number) VALUES (?, ?)', (item, list_number))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "list_number": list_number
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }) # this is if there is an overall error with the buttons functions


# Retrieves every single list that has been saved in the database
@app.route('/api/get-history', methods=['GET'])
def get_history():
    try:
        conn = sqlite3.connect('grocery.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT item, list_number FROM grocery_history ORDER BY list_number ASC')
        rows = cursor.fetchall()
        
        conn.close()
        
        history = {}
        
        for item, list_num in rows:
            if item not in history:
                history[item] = []
            history[item].append(list_num)
        
        # sends a message to the front end to say that it worked and also sends the history dictionary for display
        return jsonify({
            "status": "success",
            "history": history
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# Deletes the entire history from the view lists
@app.route('/api/clear-history', methods=['POST'])
def clear_history():
    try:
        conn = sqlite3.connect('grocery.db')
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM grocery_history')
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "message": "All history cleared"
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        })


# Runs when the file is executed directly
if __name__ == '__main__':
    init_db() 
    
    print("Starting Groceria server...")
    
    app.run(host="0.0.0.0", debug=False, port=5001) # allows the app to run on any machine