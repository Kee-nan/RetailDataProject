This final group project is designed to apply cloud computing, data engineering, and data science skills using Azure Cloud Technologies and Tools. Students will analyze real-world retail data to derive insights on customer engagement and spending behaviors, delivering scalable, impactful solutions through Azure services. With the rapid growth in data across industries—especially in healthcare, finance, and retail—data analytics has become critical for advancements like drug discovery, investment analysis, and demand forecasting.

With the rising demand for cloud and data professionals, this project provides students with hands-on experience in building end-to-end solutions on Azure Cloud. The project focuses on data ingestion, transformation, analysis, and machine learning to generate actionable insights from retail data. Using Azure's suite of data and machine learning services, students will analyze customer engagement and spending behaviors, creating an interactive web application to visualize key findings.

In this final project, students will work with anonymized retail data from 84.51°/Kroger in Azure Cloud. The main objective is to develop solutions that enhance the retail experience by simplifying life for shoppers. Creativity and empathy for the customer experience are encouraged, with a focus on the principle: "Make the Customer's Life Easier."  

🔧 How to Use
Clone the repository and install dependencies:

pip install -r requirements.txt
Start the Flask App:
>> python app.py

Navigate to: http://localhost:5000

Use the login or create account form to get started.

After logging in, explore the dataset using the dashboard page.

---

Login and Account Creation Page
Users can log in or create a new account directly from the landing page.

Account creation requires:

Username
Password
Email address

Users are stored in a table called accounts
Once stored they can sign in using 

Username
Password

Flashing messages exist for errors or confirmations (e.g., incorrect login, user already exists, etc.).

---

📊 Explore Dashboard (Keenan)
After logging in, users are redirected to the Explore page where they can interact with real-time retail data.

How It Works:
An SQL query joins the Transactions, Households, and Products tables on:

HSHD_NUM for households
PRODUCT_NUM for product details

The joined data includes all demographic info, purchase details, and product attributes.

Explore Page Functionality:
HSHD Number Filter: Enter a specific household number to filter the records.

Dropdown filter allows results to be grouped by:

Household Number
Basket Number
Purchase Date
Product Number
Department
Commodity

Paginated Results: Displays 1,000 results per page so as to not slow or freeze the query.
Parameters should carry over upon page switches
Use "Previous" and "Next" buttons to navigate through pages.

Example Columns Shown:
HSHD_NUM, BASKET_NUM, PRODUCT_NUM, SPEND, UNITS, STORE_R, YEAR, DEPARTMENT, NATURAL_ORGANIC_FLAG, etc.

Data is stored in SQL Azure database and can be updated live via an Azure datapipeline by adding new
CSV data to block storage it automatically updates the database.

---
📊 Trend Analysis 


---
📊 Machine Learning Analysis 