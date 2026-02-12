# Logic for functions involving employees

from app.db_connect import create_connection
from app.query_loader import load_queries

queries = load_queries("db/queries.sql")  # path from root


# Add an employee


def add_new_employee(first_name, last_name, phone_number, access_level):

    conn, error = create_connection()
    if conn is None:
        return False, error  # Pass detailed DB error to GUI

    cursor = None

    try:
        cursor = conn.cursor()

        # Get the SQL query
        sql_add_new_employee = queries.get("add_new_employee")
        if not sql_add_new_employee:
            return False, "Query 'add_new_employee' not found."

        # Execute query with input data
        cursor.execute(sql_add_new_employee, (first_name, last_name, phone_number, access_level, 'active'))
        conn.commit()

        # Get the new employee ID
        employee_id = cursor.lastrowid
        return True, employee_id

    except Exception as e:
        return False, str(e)  # Pass the error message to the GUI

    finally:
        if cursor:
            cursor.close()
        conn.close()


# Terminate an employee


def mark_employee_as_terminated(employee_id):
    conn, error = create_connection()
    if conn is None:
        return False, error

    cursor = None

    try:
        cursor = conn.cursor()
        sql_mark_employee_as_terminated = queries.get("mark_employee_as_terminated")
        if not sql_mark_employee_as_terminated:
            return False, "Query 'mark_employee_as_terminated' not found."

        cursor.execute(sql_mark_employee_as_terminated, (employee_id,))
        conn.commit()
        return True, "Employee marked as terminated."

    except Exception as e:
        return False, str(e)

    finally:
        if cursor:
            cursor.close()
        conn.close()
