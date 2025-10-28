# config.py
import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="CAJ25@as",
            database="multas_app",
            charset="utf8mb4"
        )
        return conn
    except Error as e:
        print("Error al conectar con la BD:", e)
        raise
