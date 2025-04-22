from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'secret_key_for_demo'  # Not secure, just for flash messages

# Azure SQL connection string
conn_str = (
    'Driver={ODBC Driver 17 for SQL Server};'
    'Server=tcp:cc-project-sql-serrver.database.windows.net,1433;'
    'Database=RetailDataDB;'
    'Uid=sqladmin;'
    'Pwd=Password123;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
    'Connection Timeout=30;'
)

def get_db_connection():
    return pyodbc.connect(conn_str)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        action = request.form['action']

        username = request.form['username']
        password = request.form['password']

        if action == 'Login':
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM accounts WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()
            conn.close()

            if user:
                return redirect(url_for('grid'))
            else:
                flash('Invalid login. Try again.')

        elif action == 'Create Account':
            email = request.form['email']
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO accounts (username, password, email) VALUES (?, ?, ?)", (username, password, email))
            conn.commit()
            conn.close()
            flash('Account created successfully.')

    return render_template('login.html')

@app.route('/grid')
def grid():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
