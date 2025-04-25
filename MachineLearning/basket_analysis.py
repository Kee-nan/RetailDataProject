#!/usr/bin/env python
# coding: utf-8

import pyodbc
import pandas as pd
from sklearn.linear_model import LinearRegression

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

    query = """
    SELECT
        T.Basket_num,
        P.Commodity
    FROM
        TRANSACTIONS T
    JOIN
        PRODUCTS P ON T.Product_num = P.Product_num
    """

    basket_data = pd.read_sql(query, conn)
    conn.close()

    # Convert each basket into a row with 1s where commodities are present
    basket_matrix = (
        basket_data
        .assign(present=1)
        .pivot_table(index='Basket_num', columns='Commodity', values='present', fill_value=0)
    )

    # Try to predict presence of a single target product
    basket_matrix.columns = basket_matrix.columns.str.strip()

    # Sum each column to get purchase counts per commodity
    commodity_counts = basket_matrix.sum().sort_values(ascending=False)

    # Select top 3
    top_commodities = commodity_counts.head(3).index.tolist()

    all_top_associations = {}

    for target_commodity in top_commodities:
        
        X = basket_matrix.drop(columns=target_commodity)
        y = basket_matrix[target_commodity]

        model = LinearRegression()
        model.fit(X, y)

        coefs = pd.Series(model.coef_, index=X.columns).sort_values(ascending=False)
        top_related = coefs.head(10)
        
        all_top_associations[target_commodity] = top_related

    # Combine all into a single DataFrame for export
    export_df = pd.concat(all_top_associations).reset_index()
    export_df.columns = ['Target_Commodity', 'Predictor', 'Coefficient']

    export_df.to_csv("MachineLearning/commodity_correlations.csv", index=False)
    
if __name__ == "__main__":
    main()