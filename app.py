from flask import Flask, request, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For flash messages

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get user input from the form
        host = request.form.get('host')
        port = request.form.get('port')
        username = request.form.get('username')
        password = request.form.get('password')
        database = request.form.get('database')

        try:
            # Attempt to connect to the MySQL database
            connection = mysql.connector.connect(
                host=host,
                port=int(port),
                user=username,
                password=password,
                database=database
            )

            if connection.is_connected():
                connection.close()
                return redirect(url_for('success', db=database, host=host, port=port, username=username, password=password))
        except Error as e:
            flash(f"Connection failed: {str(e)}", 'error')

    return render_template('index.html')

@app.route('/success', methods=['GET', 'POST'])
def success():
    # Retrieve the database connection details from query parameters
    db_name = request.args.get('db', 'No DB Selected')
    host = request.args.get('host')
    port = request.args.get('port')
    username = request.args.get('username')
    password = request.args.get('password')

    results = None
    sql_query = None

    if request.method == 'POST':
        # Get the SQL query from the form
        sql_query = request.form.get('sql_query')

        # Only allow SELECT statements
        if sql_query.strip().lower().startswith('select'):
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
                cursor.execute(sql_query)
                results = cursor.fetchall()
                cursor.close()
                connection.close()
            except Error as e:
                flash(f"Error executing query: {str(e)}", 'error')
        else:
            flash('Only SELECT statements are allowed.', 'warning')

    return render_template('success.html', db_name=db_name, results=results, sql_query=sql_query)

if __name__ == '__main__':
    app.run(debug=True)
