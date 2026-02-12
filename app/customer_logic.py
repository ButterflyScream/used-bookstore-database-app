# Functions for adding or looking up customers

# Connect to DB
from app.db_connect import create_connection
from app.query_loader import load_queries

queries = load_queries("db/queries.sql")

# Add a new customer account


def add_new_customer(first_name, last_name, email):
    """
    Add a new customer, first check email is not taken.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error  # Pass detailed DB error to GUI

    cursor = None

    try:
        cursor = conn.cursor()

        # Convert email to lowercase before checking for duplicate and inserting
        email = email.lower()

        # Check for duplicate email first
        sql_check_customer_email = queries.get("check_customer_email")
        if not sql_check_customer_email:
            return False, "Query 'check_customer_email' not found."
        cursor.execute(sql_check_customer_email, (email,))
        if cursor.fetchone():
            return False, "Email already in use."

        sql_add_new_customer = queries.get("add_new_customer")
        if not sql_add_new_customer:
            return False, "Query 'add_new_customer' not found."

        cursor.execute(sql_add_new_customer, (first_name, last_name, email))
        conn.commit()

        customer_id = cursor.lastrowid

        # Return new customer_id to GUI
        return True, customer_id

    except Exception as e:
        return False, str(e)

    finally:
        if cursor:
            cursor.close()
        conn.close()


# Mark customer as inactive (delete customer)


def mark_customer_as_inactive(customer_id):
    """
    Mark customer as 'inactive' by entering customer_id.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error

    cursor = None
    try:
        cursor = conn.cursor()
        sql_mark_customer_as_inactive = queries.get("mark_customer_as_inactive")
        if not sql_mark_customer_as_inactive:
            return False, "Query 'mark_customer_as_inactive' not found."

        cursor.execute(sql_mark_customer_as_inactive, (customer_id,))
        conn.commit()

        # Confirm update happened
        if cursor.rowcount == 0:
            return False, f"No customer found with ID: {customer_id}"

        return True, "Customer marked as inactive."

    except Exception as e:
        return False, str(e)
    finally:
        if cursor:
            cursor.close()
        conn.close()



def lookup_customer_credit_by_email(email):
    """
    Looks up a customer's credit balance by email address.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error  # Pass detailed DB error to GUI

    cursor = None

    try:
        cursor = conn.cursor()

        email = email.lower()   # Change to lowercase, as all email's inserting as lower.

        # Get SQL query
        sql_lookup_customer_credit_by_email = queries.get("lookup_customer_credit_by_email")
        if not sql_lookup_customer_credit_by_email:
            return False, "Query 'lookup_customer_credit_by_email' not found."

        # Execute query with email
        cursor.execute(sql_lookup_customer_credit_by_email, (email,))
        result = cursor.fetchone()

        if not result:
            return False, f"No customer found with email: {email}"

        # Take the credit_total value from SQL
        (credit_total,) = result

        # Return success and credit amount
        return True, credit_total

    except Exception as e:
        return False, str(e)

    finally:
        if cursor:
            cursor.close()
        conn.close()
