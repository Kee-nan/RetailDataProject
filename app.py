#Imports and tools
from flask import Flask, render_template, request, redirect, url_for, flash
import pyodbc
import pandas as pd
from MachineLearning import churn_prediction, basket_analysis

# Only run this once when app starts
churn_prediction.main()
basket_analysis.main()

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

# Function to connect to database
def get_db_connection():
    return pyodbc.connect(conn_str)

#Route for login and account creation page
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
                return redirect(url_for('explore'))
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

#Route /
@app.route('/explore', methods=['GET', 'POST'])
def explore():
    # Capture filters from POST or fallback to GET (for page navigation)
    if request.method == 'POST':
        hshd_num_filter = request.form.get('hshd_num')
        group_by = request.form.get('group_by')
        page = 1  # Reset to first page after new filter
    else:
        hshd_num_filter = request.args.get('hshd_num')
        group_by = request.args.get('group_by')
        page = request.args.get('page', 1, type=int)

    per_page = 1000
    offset = (page - 1) * per_page

    conn = get_db_connection()

    # Base SQL structure
    base_query = """
    SELECT
        t.HSHD_NUM,
        t.BASKET_NUM,
        t.PURCHASE,
        t.PRODUCT_NUM,
        t.SPEND,
        t.UNITS,
        t.STORE_R,
        t.WEEK_NUM,
        t.YEAR,
        h.L,
        h.AGE_RANGE,
        h.MARITAL,
        h.INCOME_RANGE,
        h.HOMEOWNER,
        h.HSHD_COMPOSITION,
        h.HH_SIZE,
        h.CHILDREN,
        p.DEPARTMENT,
        p.COMMODITY,
        p.BRAND_TY,
        p.NATURAL_ORGANIC_FLAG
    FROM Transactions t
    JOIN Households h ON t.HSHD_NUM = h.HSHD_NUM
    JOIN Products p ON t.PRODUCT_NUM = p.PRODUCT_NUM
    {where_clause}
    {order_clause}
    OFFSET {offset} ROWS FETCH NEXT {fetch_count} ROWS ONLY
    """

    # Filtering & ordering
    where_clause = ""
    order_clause = "ORDER BY t.HSHD_NUM"
    params = []

    if hshd_num_filter and hshd_num_filter.strip().isdigit():
        where_clause = "WHERE h.HSHD_NUM = ?"
        params.append(int(hshd_num_filter.strip()))
    else:
        hshd_num_filter = None  # fallback to None if not valid


    valid_group_bys = {
        "HSHD_NUM": "t.HSHD_NUM",
        "BASKET_NUM": "t.BASKET_NUM",
        "PURCHASE": "t.PURCHASE",
        "PRODUCT_NUM": "t.PRODUCT_NUM",
        "DEPARTMENT": "p.DEPARTMENT",
        "COMMODITY": "p.COMMODITY"
    }

    if group_by in valid_group_bys:
        order_clause = f"ORDER BY {valid_group_bys[group_by]}"

    final_query = base_query.format(
        where_clause=where_clause,
        order_clause=order_clause,
        offset=offset,
        fetch_count=per_page
    )

    df = pd.read_sql(final_query, conn, params=params)
    conn.close()

    records = df.to_dict(orient='records')

    # Count total records for pagination
    conn = get_db_connection()
    count_query = f"""
    SELECT COUNT(*) 
    FROM Transactions t 
    JOIN Households h ON t.HSHD_NUM = h.HSHD_NUM 
    JOIN Products p ON t.PRODUCT_NUM = p.PRODUCT_NUM 
    {where_clause}
    """
    total_records = pd.read_sql(count_query, conn, params=params).iloc[0, 0]
    conn.close()

    total_pages = (total_records // per_page) + (1 if total_records % per_page > 0 else 0)

    return render_template(
        'Explore.html',
        records=records,
        hshd_num_filter=hshd_num_filter,
        group_by=group_by,
        page=page,
        total_pages=total_pages
    )

#New routes here
@app.route("/ml-dashboard")
def ml_dashboard():
    # Load full churn data
    churn_df_full = pd.read_csv("MachineLearning/at_risk_customers.csv")

    # Filter high-risk for the table
    churn_df_table = churn_df_full[churn_df_full["churn_prob"] > 0.75]

    # Convert to dicts
    churn_data = churn_df_table.to_dict(orient='records')
    churn_chart_data = churn_df_full.to_dict(orient='records')
	
    # Load data
    df = pd.read_csv("MachineLearning/commodity_correlations.csv")

    # Add sorted pair column
    df['pair'] = df.apply(
        lambda row: tuple(sorted([row['Target_Commodity'], row['Predictor']])),
        axis=1
    )

    # For each unique pair, keep row with max absolute coefficient
    df['abs_coef'] = df['Coefficient'].abs()
    dedup_df = df.loc[df.groupby('pair')['abs_coef'].idxmax()].drop(columns=['pair', 'abs_coef'])

    # Sort again
    dedup_df = dedup_df.sort_values(by='Coefficient', ascending=False)

    # Convert to dict
    basket_data = dedup_df.to_dict(orient='records')

    return render_template("ML-dashboard.html",
                       churn_data=churn_data,
                       churn_chart_data=churn_chart_data,
                       basket_data=basket_data)

#Must be at the bottom
if __name__ == '__main__':
    app.run(debug=True)
