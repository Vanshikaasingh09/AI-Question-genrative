

import psycopg2

def get_db_connection():
    conn = psycopg2.connect(
        dbname="quiz_app_db",
        user="postgres",
        password="12345678",
        host="localhost",
        port="5432"
    )
    return conn

def get_db_cursor():
    conn = get_db_connection()
    return conn.cursor(), conn



