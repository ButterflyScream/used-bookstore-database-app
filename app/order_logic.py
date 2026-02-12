# Functions for creating and processing orders

# Connect to DB
# Connect to DB
from app.db_connect import create_connection
from app.query_loader import load_queries


queries = load_queries("db/queries.sql")


def lookup_customer_credit_by_id(customer_id):
    """
    Fetch a customer's credit balance by their ID.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error

    cursor = None
    try:
        cursor = conn.cursor()
        sql = queries.get("fetch_credit_by_customer_id")
        cursor.execute(sql, (customer_id,))
        result = cursor.fetchone()
        if not result:
            return False, f"No customer found with ID: {customer_id}"
        (credit_total,) = result
        return True, credit_total
    except Exception as e:
        return False, str(e)
    finally:
        cursor.close()
        conn.close()


def search_book_by_isbn_for_order(isbn):
    """
    Searches for a book (for order processing) and includes book_id.
    Returns (True, dict) if found or (False, error message) if not.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error

    cursor = None
    try:
        cursor = conn.cursor()

        # Fetch the query
        sql = queries.get("search_book_by_isbn_for_order")
        if not sql:
            return False, "Query 'search_book_by_isbn_for_order' not found."

        # Execute search
        cursor.execute(sql, (isbn, isbn))
        results = cursor.fetchall()

        if not results:
            return False, f"No book found with ISBN: {isbn}"

        # Use the first result
        book_id, book_name, author_name, resale_price, book_status = results[0]

        # Check availability
        if book_status.lower() != "available":
            return False, f"Book '{book_name}' is not available."

        # Return book info
        return True, {
            "book_id": book_id,
            "book_name": book_name,
            "author_name": author_name,
            "resale_price": float(resale_price),
            "availability": "Available"
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

    cursor = None
    try:
        cursor = conn.cursor()

        # Fetch the SQL query
        sql_validate_book_by_id = queries.get("validate_book_by_id")
        if not sql_validate_book_by_id:
            return False, "Query 'validate_book_by_id' not found."

        # Execute query
        cursor.execute(sql_validate_book_by_id, (book_id,))
        result = cursor.fetchone()

        # No book found
        if not result:
            return False, f"No book found with ID: {book_id}"

        book_id, book_name, resale_price, book_status = result

        # Book is already sold
        if book_status.lower() != "available":
            return False, f"Book '{book_name}' is already sold."

        # Book is valid and available
        return True, {
            "book_id": book_id,
            "book_name": book_name,
            "resale_price": float(resale_price)
        }

    except Exception as e:
        return False, str(e)

    finally:
        if cursor:
            cursor.close()
        conn.close()


def fetch_customer_by_id(customer_id):
    """
    Fetch customer info and credit by ID.
    Returns (True, dict) if found or (False, error message) if not.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error

    cursor = None
    try:
        cursor = conn.cursor()
        sql = queries.get("fetch_customer_by_id")
        if not sql:
            return False, "Query 'fetch_customer_by_id' not found."

        cursor.execute(sql, (customer_id,))
        result = cursor.fetchone()
        if not result:
            return False, f"No active customer found with ID: {customer_id}"

        cust_id, first_name, last_name, credit_total = result
        return True, {
            "customer_id": cust_id,
            "name": f"{first_name} {last_name}",
            "credit_total": float(credit_total)
        }

    except Exception as e:
        return False, str(e)
    finally:
        if cursor:
            cursor.close()
        conn.close()


def complete_order(customer_id, employee_id, order_items, credit_used, current_credit):
    """
    Completes an order: inserts into Order and Order_Detail,
    deducts credit if used, and marks inventory books sold.
    """
    conn, error = create_connection()
    if conn is None:
        return False, error

    cursor = None
    try:
        cursor = conn.cursor()

        # Calculate totals
        total_amount = sum(float(item["price"]) for item in order_items)
        final_amount_paid = max(0, total_amount - float(credit_used))

        # Insert into Order
        sql_order = queries.get("insert_order")
        cursor.execute(sql_order, (customer_id, employee_id, total_amount, credit_used, final_amount_paid))
        order_id = cursor.lastrowid

        # Insert Order Details
        sql_detail = queries.get("insert_order_detail")
        sql_mark_sold = queries.get("mark_book_as_sold")
        for item in order_items:
            cursor.execute(sql_detail, (order_id, item["book_id"], item["price"]))

            # Mark inventory books as sold (skip manual items with None or 0 ID)
            if item["book_id"] and isinstance(item["book_id"], int):
                cursor.execute(sql_mark_sold, (item["book_id"],))

        # Deduct credit if used
        if credit_used > 0:
            new_credit = max(0, float(current_credit) - float(credit_used))
            sql_update_credit = queries.get("update_customer_credit_after_order")
            cursor.execute(sql_update_credit, (new_credit, customer_id))

        conn.commit()
        return True, {"order_id": order_id}

    except Exception as e:
        conn.rollback()
        return False, str(e)
    finally:
        if cursor:
            cursor.close()
        conn.close()
