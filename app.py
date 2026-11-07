
import os
import time
from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

# MySQL Configuration
# DB_HOST = "localhost"
# DB_USER = "root"
# DB_PASSWORD = "password"
# DB_NAME = "company_db1"
# DB_PORT = 3306

# MySQL Configuration
MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')
MYSQL_DB = os.getenv('MYSQL_DB', 'company_db')


def get_db_connection():
    """Connects to the database, retrying if it's not ready yet."""

    for attempt in range(5):
        try:
            return pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                database=MYSQL_DB,
                port=3306,
                cursorclass=pymysql.cursors.DictCursor
            )

        except pymysql.MySQLError as e:
            print(f"Database connection attempt {attempt + 1} failed: {e}")
            time.sleep(2)

    raise Exception("Could not connect to the MySQL database.")



# Automatically create database and table
def initialize_database():
    connection = None
    for attempt in range(10):
        try:
            connection = pymysql.connect(
                host=MYSQL_HOST,
                user=MYSQL_USER,
                password=MYSQL_PASSWORD,
                port=3306,
            )
            break
        except pymysql.MySQLError as e:
            print(f"Init connection attempt {attempt + 1} failed: {e}")
            time.sleep(3)
    else:
        raise Exception("Could not connect to MySQL for initialization.")

    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{MYSQL_DB}`")
            cursor.execute(f"USE `{MYSQL_DB}`")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    role VARCHAR(100) NOT NULL,
                    email VARCHAR(100) NOT NULL
                )
            """)
        connection.commit()
        print(f"Database '{MYSQL_DB}' and employees table are ready!")
    finally:
        connection.close()


@app.route('/')
def index():

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM employees")
            employees = cursor.fetchall()

    finally:
        connection.close()

    return render_template('index.html', employees=employees)


@app.route('/add', methods=['POST'])
def add_employee():

    name = request.form['name']
    role = request.form['role']
    email = request.form['email']

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO employees (name, role, email) VALUES (%s, %s, %s)"
            cursor.execute(sql, (name, role, email))

        connection.commit()

    finally:
        connection.close()

    return redirect(url_for('index'))


@app.route('/delete/<int:emp_id>')
def delete_employee(emp_id):

    connection = get_db_connection()

    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM employees WHERE id = %s", (emp_id,))

        connection.commit()

    finally:
        connection.close()

    return redirect(url_for('index'))


if __name__ == '__main__':

    # Create database and table before starting Flask
    initialize_database()

    # Start Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
