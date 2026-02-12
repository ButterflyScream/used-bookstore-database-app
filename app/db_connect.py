# App logic for connecting the database

# Load the Connector/Python library
import mysql.connector
from mysql.connector import Error, errorcode

# Try to load local credentials first (security for users)
try:
    from app.db_config_local import db_settings
# If not found, fall back to template config
except ImportError:
    from app.db_config import db_settings



def create_connection():
    try:
        connection = mysql.connector.connect(**db_settings)
        if connection.is_connected():
            return connection, None  # Return connection and no error
    except Error as e:
        if e.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            return None, "Invalid credentials – check your username or password."
        elif e.errno == errorcode.ER_BAD_DB_ERROR:
            return None, "Database not found – check your database name."
        else:
            return None, f"Error while connecting to MySQL: {e}"
