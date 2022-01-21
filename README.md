# Backend Challenge

# Problem Statement

1. Fetch data for Petroleum Products from the data.json file using an API call. API endpoint [https://raw.githubusercontent.com/younginnovations/internship-challenges/master/programming/petroleum-report/data.json](https://raw.githubusercontent.com/younginnovations/internship-challenges/master/programming/petroleum-report/data.json)
2. Store the response data into a **sqlite** database.
    - (bonus point) Normalize the data and store into relational structure
    - (bonus point) Fetch the data from the newly stored sqlite database
3. List the total sale of each petroleum.
4. List the top 3 countries that have the highest and lowest total sales till date.
5. List average sale of each petroleum product for 4 years of interval. Note: Do not count zero sale during average calculation

# Solution

## Install Dependencies

- install requests
- install sqlite3

## Run

1. Run python3 report.py