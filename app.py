from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import plotly.express as px
import pandas as pd
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For flash messages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input for MySQL credentials
        host = request.form.get('host')
        port = request.form.get('port')
        username = request.form.get('username')
        password = request.form.get('password')
        database = request.form.get('database')

        try:
            # Try connecting to the MySQL database
            connection = mysql.connector.connect(
                host=host,
                port=int(port),
                user=username,
                password=password,
                database=database
            )
            if connection.is_connected():
                connection.close()
                # Redirect to the execute page on successful connection
                return redirect(url_for(
                    'execute',
                    db=database,
                    host=host,
                    port=port,
                    username=username,
                    password=password
                ))
        except Error as e:
            flash(f"Connection failed: {str(e)}", 'error')

    return render_template('index.html')

@app.route('/execute', methods=['GET', 'POST'])
def execute():
    db_name = request.args.get('db', 'No DB Selected')
    host = request.args.get('host')
    port = request.args.get('port')
    username = request.args.get('username')
    password = request.args.get('password')

    if request.method == 'POST':
        sql_query = request.form.get('sql_query')
        if sql_query.strip().lower().startswith(('select', 'show', 'describe')):
            return redirect(url_for(
                'results',
                db=db_name,
                host=host,
                port=port,
                username=username,
                password=password,
                query=sql_query
            ))
        else:
            flash('Only SELECT/SHOW/DESCRIBE statements are allowed.', 'warning')

    return render_template('execute.html', db_name=db_name)

@app.route('/results')
def results():
    db_name = request.args.get('db')
    host = request.args.get('host')
    port = request.args.get('port')
    username = request.args.get('username')
    password = request.args.get('password')
    query = request.args.get('query')

    results = []
    columns = []
    chart = None

    try:
        # Connect to the database and execute the query
        connection = mysql.connector.connect(
            host=host,
            port=int(port),
            user=username,
            password=password,
            database=db_name
        )
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query)
        results = cursor.fetchall()

        if results:
            # Extract column names and visualize data
            columns = list(results[0].keys())
            df = pd.DataFrame(results)
            chart = px.bar(df, x=columns[0], y=columns[1:], title="Query Results").to_json()
        
        cursor.close()
        connection.close()
    except Error as e:
        flash(f"Error executing query: {str(e)}", 'error')
        return redirect(url_for('execute', db=db_name, host=host, port=port, username=username, password=password))

    return render_template('results.html', db_name=db_name, query=query, results=results, columns=columns, chart=chart)

if __name__ == '__main__':
    app.run(debug=True)
