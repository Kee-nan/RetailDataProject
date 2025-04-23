from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
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

def query_db(query):
    with pyodbc.connect(conn_str) as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [column[0] for column in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

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

@app.route("/api/spending_over_time")
def spending_over_time():
    query = """
        SELECT YEAR, WEEK_NUM, SUM(SPEND) AS total_spend
        FROM transactions
        GROUP BY YEAR, WEEK_NUM
        ORDER BY YEAR, WEEK_NUM;
    """
    return jsonify(query_db(query))

@app.route("/api/top_departments")
def top_departments():
    query = """
        SELECT p.DEPARTMENT, SUM(t.SPEND) AS total_spend
        FROM transactions t
        JOIN products p ON t.PRODUCT_NUM = p.PRODUCT_NUM
        GROUP BY p.DEPARTMENT
        ORDER BY total_spend DESC
        OFFSET 0 ROWS FETCH NEXT 10 ROWS ONLY;
    """
    return jsonify(query_db(query))

if __name__ == '__main__':
    app.run(debug=True)
