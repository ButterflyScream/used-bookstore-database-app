-- schema.sql
-- Defines all tables for the Used Bookstore database

-- Create the Used Bookstore database.
DROP DATABASE IF EXISTS used_bookstore_db;
CREATE DATABASE IF NOT EXISTS used_bookstore_db;
USE used_bookstore_db;

-- 'Employee' Table creation
-- Author: Gabriel Sosa
CREATE TABLE Employee (
    employee_id SMALLINT UNSIGNED AUTO_INCREMENT,
    first_name VARCHAR(15) NOT NULL,
    last_name VARCHAR(15) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    access_level CHAR(1) NOT NULL,
    employee_status VARCHAR(15) NOT NULL DEFAULT 'active',
    PRIMARY KEY(employee_id)
);

-- 'Customer' Table creation
-- Author: Gonçalo Nascimento
CREATE TABLE Customer(
    customer_id SMALLINT UNSIGNED AUTO_INCREMENT,
    first_name VARCHAR(15) NOT NULL,
    last_name VARCHAR(15) NOT NULL,
    email VARCHAR(50) NOT NULL,
    credit_total DECIMAL(6,2) NOT NULL DEFAULT 0.00 CHECK (credit_total >= 0),
    customer_status VARCHAR(10) NOT NULL DEFAULT 'active',
    PRIMARY KEY(customer_id)
);

-- 'Book' Table creation
-- Auther: Dario Morlote
CREATE TABLE Book (
    book_id SMALLINT UNSIGNED AUTO_INCREMENT,
    book_Name VARCHAR(100) NOT NULL,
    author_Name VARCHAR(20) NOT NULL,
    book_Condition VARCHAR(15),
    average_Ratings DECIMAL(3,2),
    isbn CHAR(10),
    isbn_13 CHAR(13),
    `language` VARCHAR(30),
    num_pages INT,
    resale_price DECIMAL(8,2),
    purchase_price DECIMAL(8,2) NOT NULL,
    book_status VARCHAR(10) NOT NULL DEFAULT 'available',
    PRIMARY KEY (book_id)
);

-- `Order` Table creation
-- Author: Danielle Maki
CREATE TABLE `Order` (
    order_id INT UNSIGNED AUTO_INCREMENT,
    customer_id SMALLINT UNSIGNED,
    employee_id SMALLINT UNSIGNED NOT NULL,
    order_date DATETIME NOT NULL,
    total_amount DECIMAL(6,2) NOT NULL CHECK (total_amount >= 0),
    store_credit_used DECIMAL(6,2) DEFAULT 0.00 CHECK (store_credit_used >= 0),
    final_amount_paid DECIMAL(6,2) NOT NULL CHECK (final_amount_paid >= 0) ,
    PRIMARY KEY (order_id),
    FOREIGN KEY (customer_id) REFERENCES Customer(customer_id)
        ON DELETE SET NULL,
    FOREIGN KEY (employee_id) REFERENCES Employee(employee_id)
        ON DELETE RESTRICT
);

-- Order_Detail table creation
-- Details of each line on an `Order`
-- Author: Danielle Maki
CREATE TABLE Order_Detail (
    order_id INT UNSIGNED,
    book_id SMALLINT UNSIGNED,
    final_price DECIMAL(6,2) NOT NULL CHECK (final_price >= 0),
    PRIMARY KEY (book_id),
    FOREIGN KEY (order_id) REFERENCES `Order`(order_id)
        ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES Book(book_id)
        ON DELETE RESTRICT
);
