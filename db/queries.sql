-- Query file
-- Insert rows into table 'Customer'
-- Author: Gonçalo Nascimento
INSERT INTO Customer (customer_id, first_name, last_name, email)
VALUES (102, 'Jane', 'James', 'janej@gmail.com'),
    (129, 'James', 'Bond', 'bondjames@gmail.com'),
    (132, 'John', 'Doe', 'Jdon@gmail.com');

-- Insert rows into table 'Employee'
-- Author: Gonçalo Nascimento
INSERT INTO Employee (employee_id, first_name, last_name, phone_number, access_level)
VALUES (1212, 'Rodrigo', 'Alvarez', '7798121234', '2'),
    (1211, 'Maria', 'Smith', '7705389756', '3');

-- Update employee access level for Rodrigo
-- Author: Gonçalo Nascimento
UPDATE Employee
SET access_level = '3'
WHERE employee_id = 1212;

-- name: add_new_employee
INSERT INTO Employee (first_name, last_name, phone_number, access_level, employee_status)
VALUES (%s, %s, %s, %s, %s);

-- name: add_new_customer
INSERT INTO Customer (first_name, last_name, email)
VALUES (%s, %s, %s);

-- name: check_customer_email
SELECT 1 FROM Customer WHERE email = %s;


-- name: add_book_and_credit_customer
INSERT INTO Book (book_Name, author_Name, book_Condition, average_Ratings,
                  isbn, isbn_13, `language`, num_pages,
                  purchase_price, resale_price)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- name: fetch_credit_by_customer_id
SELECT credit_total FROM Customer WHERE customer_id = %s;

-- name: update_customer_credit_total
UPDATE Customer SET credit_total = %s WHERE customer_id = %s;


-- name: lookup_customer_credit_by_email
SELECT credit_total FROM Customer WHERE email = %s;

-- name: search_book_by_isbn
SELECT book_Name, author_Name, resale_price, book_status
FROM Book
WHERE isbn = %s OR isbn_13 = %s;

-- name: mark_employee_as_terminated
UPDATE Employee SET employee_status = 'terminated' WHERE employee_id = %s;

-- name: mark_customer_as_inactive
UPDATE Customer SET customer_status = 'inactive' WHERE customer_id = %s;



-- Order Logic Code
-- name: fetch_customer_by_id
SELECT customer_id, first_name, last_name, credit_total
FROM Customer
WHERE customer_id = %s AND customer_status = 'active';

-- name: search_book_by_isbn_for_order
SELECT book_id, book_Name, author_Name, resale_price, book_status
FROM Book
WHERE isbn = %s OR isbn_13 = %s;

-- name: validate_book_by_id
SELECT book_id, book_Name, resale_price, book_status
FROM Book
WHERE book_id = %s;

-- name: insert_order
INSERT INTO `Order` (customer_id, employee_id, order_date, total_amount, store_credit_used, final_amount_paid)
VALUES (%s, %s, NOW(), %s, %s, %s);

-- name: insert_order_detail
INSERT INTO Order_Detail (order_id, book_id, final_price)
VALUES (%s, %s, %s);

-- name: mark_book_as_sold
UPDATE Book SET book_status = 'sold' WHERE book_id = %s;

-- name: update_customer_credit_after_order
UPDATE Customer SET credit_total = %s WHERE customer_id = %s;
