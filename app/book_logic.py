# Functions for Add/search books

# Connect to DB

from app.db_connect import create_connection
from app.query_loader import load_queries
from decimal import Decimal

# Load all SQL queries once
queries = load_queries("db/queries.sql")


def add_book_and_credit_customer(book_name, author_name, book_condition, average_ratings,
                                 isbn, isbn_13, language, num_pages,
                                 purchase_price, resale_price,
                                 customer_id):
    """
    Adds a new book (with purchase + resale price) and updates the customer's credit_total.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error  # Pass detailed DB error to GUI

    cursor = None

    try:
        cursor = conn.cursor()

        # 1. Insert the new book
        sql_insert_book = queries.get("add_book_and_credit_customer")
        if not sql_insert_book:
            return False, "Query 'add_book_and_credit_customer' not found."

        cursor.execute(sql_insert_book, (
            book_name, author_name, book_condition, average_ratings,
            isbn, isbn_13, language, num_pages,
            purchase_price, resale_price
        ))
        conn.commit()

        # Get the new Book ID
        book_id = cursor.lastrowid

        # 2. Fetch customer's current credit
        sql_fetch_credit = queries.get("fetch_credit_by_customer_id")
        if not sql_fetch_credit:
            return False, "Query 'fetch_credit_by_customer_id' not found."

        cursor.execute(sql_fetch_credit, (customer_id,))
        result = cursor.fetchone()
        if not result:
            return False, f"Customer ID {customer_id} not found."

        (current_credit,) = result

        # 3. Update customer's credit_total
        new_credit_total = current_credit + Decimal(str(purchase_price))

        sql_update_credit = queries.get("update_customer_credit_total")
        if not sql_update_credit:
            return False, "Query 'update_customer_credit_total' not found."

        cursor.execute(sql_update_credit, (new_credit_total, customer_id))
        conn.commit()

        # Return results to GUI
        return True, {
            "book_id": book_id,
            "book_price": resale_price,
            "credit_total": new_credit_total
        }

    except Exception as e:
        return False, str(e)

    finally:
        if cursor:
            cursor.close()
        conn.close()


def search_book_by_isbn(isbn):
    """
    Searches for a book by ISBN or ISBN-13.
    Returns book details if found, otherwise a message that it's unavailable.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error  # DB connection error

    cursor = None

    try:
        cursor = conn.cursor()

        # Get the SQL query
        sql_search_book_by_isbn = queries.get("search_book_by_isbn")
        if not sql_search_book_by_isbn:
            return False, "Query 'search_book_by_isbn' not found."

        # Execute the query (pass ISBN twice to match either isbn and isbn_13)
        cursor.execute(sql_search_book_by_isbn, (isbn, isbn))
        results = cursor.fetchall()

        # Return not found message with ISBN # entered.
        if not results:
            return False, f"No book found with ISBN: {isbn}"

        # Unpack result
        book_name, author_name, resale_price, book_status = results[0]
        availability = "Available" if book_status.lower() == "available" else "Sold"

        # Return book info to GUI
        return True, {
            "book_name": book_name,
            "author_name": author_name,
            "resale_price": resale_price,
            "availability": availability
        }

    except Exception as e:
        return False, str(e)

    finally:
        if cursor:
            cursor.close()
        conn.close()


def validate_book_by_id(book_id):
    """
    Validate a book by its ID.
    Returns (True, dict) with book details if available, or (False, message).
    """
    conn, error = create_connection()
    if conn is None:
        return False, error

    try:
        cursor = conn.cursor()
        sql = "SELECT book_id, book_Name, resale_price, book_status FROM Book WHERE book_id = %s;"
        cursor.execute(sql, (book_id,))
        result = cursor.fetchone()

        if not result:
            return False, f"No book found with ID: {book_id}"

        book_id, book_name, resale_price, book_status = result
        if book_status.lower() != "available":
            return False, f"Book '{book_name}' is already sold."

        return True, {
            "book_id": book_id,
            "book_name": book_name,
            "resale_price": resale_price
        }
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()
