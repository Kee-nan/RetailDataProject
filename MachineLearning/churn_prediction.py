#!/usr/bin/env python
# coding: utf-8

import pyodbc
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

def main():
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

    # Establish connection
    conn = pyodbc.connect(conn_str)

    # Load data
    households_df = pd.read_sql("SELECT * FROM HOUSEHOLDS", conn)
    transactions_df = pd.read_sql("SELECT TOP 20000 * FROM TRANSACTIONS", conn)

    
    conn.close()

    transactions_df.columns = transactions_df.columns.str.strip().str.upper()
    households_df.columns = households_df.columns.str.strip().str.upper()

    # Convert date column
    transactions_df['PURCHASE'] = pd.to_datetime(transactions_df['PURCHASE'])

    households_df['LOYALTY_FLAG'] = households_df['L'].map({'Y': 1, 'N': 0}).fillna(0).astype(int)

    # Aggregate per household
    agg_df = transactions_df.groupby('HSHD_NUM').agg(
        total_spend=('SPEND', 'sum'),
        total_visits=('PURCHASE', 'count'),
        last_purchase=('PURCHASE', 'max')
    ).reset_index()

    # Calculate time since last purchase
    latest_date = transactions_df['PURCHASE'].max()
    agg_df['days_since_last_purchase'] = (latest_date - agg_df['last_purchase']).dt.days
    agg_df.drop(columns='last_purchase', inplace=True)

    # Merge with households (if you want loyalty flag or other demographics)
    if 'LOYALTY_FLAG' in households_df.columns:
        households_df['LOYALTY_FLAG'] = households_df['LOYALTY_FLAG'].astype(int)  # Optional binary encoding
        agg_df = agg_df.merge(households_df[['HSHD_NUM', 'LOYALTY_FLAG']], on='HSHD_NUM', how='left')

    agg_df['churned'] = (agg_df['days_since_last_purchase'] > 90).astype(int)

    features = ['total_spend', 'total_visits', 'days_since_last_purchase']
    if 'LOYALTY_FLAG' in agg_df.columns:
        features.append('LOYALTY_FLAG')

    X = agg_df[features]
    y = agg_df['churned']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    agg_df['churn_prob'] = model.predict_proba(X)[:, 1]  # Probability of class 1 (churn)
    agg_df['churn_risk'] = (agg_df['churn_prob'] >= 0.5).astype(int)  # Optional thresholding

    # Show top 10 highest risk customers (by probability)
    at_risk = agg_df.sort_values(by='churn_prob', ascending=False)
    at_risk[['HSHD_NUM', 'total_spend', 'days_since_last_purchase', 'churn_prob']]

    at_risk.to_csv("MachineLearning/at_risk_customers.csv", index=False)
    
if __name__ == "__main__":
    main()
