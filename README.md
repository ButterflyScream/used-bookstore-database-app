# UsedBookStore
Group 15 COP4710 Final Project

This project is an application designed to manage a used bookstore, 
where customers can trade in books or purchase books.
It includes a:
* MySQL database
* GUI built with Python (Tkinter)
* Supporting application logic :

## Setup Instructions
1. Install Dependencies
Make sure Python 3 and MySQL are installed. Then install the required Python package:
`pip install mysql-connector-python`

1. Create the database:
- Run the `schema.sql` file in MySQL Workbench or command line

2. Configure the database:
- Copy app/db_config.py → app/db_config_local.py and enter your MySQL username/password there.
* Don't upload passwords to public repos! 
* app/db_config_local.py is in the gitignore file, to prevent accidental uploads.

3. Launch the GUI:
- In the terminal, navigate to the root of the project: `cd UsedBookStore`
- Run `python gui/main_gui.py`

## What the App can do:

* Allow employees to add (buy) used books from customers
    -give credit to their account
* Sell the used books to customers 
    -Create an order and order detail
    -Get prices and caluculate totals
    -Mark book as sold
    -Look up customer's credit and update it if used for purchase
* Add and update employees
* Add and update customers
* Look up credit amount by customer's email
* Look up a book by isbn #

It does this through:
* Providing a GUI interface for these functions
* Showing a variety of SQL queries and database design principles

## Database Structure

The project uses a MySQL database with the following main tables:

- `Customer`: Tracks customer info and store credit 
- `Book`: Information about books in inventory
- `Order` and `Order_Detail`: Handles purchases
- `Employee`: For processing transactions.
- 
## File Structure
UsedBookStore/
├── app/
│ ├── book_logic.py
│ ├── customer_logic.py
│ ├── db_config.py
│ ├── db_connect.py
│ ├── employee_logic.py
│ └── order_logic.py
├── db/
│ ├── schema.sql
│ ├── sample_data.sql
│ └── queries.sql
├── gui/
│ └── main_gui.py
├── README.md

## Application Logic

Application logic is written in Python, using:
- `mysql.connector` to connect to the database
- Modular functions for each operation (creating an order, adding a book)

The GUI is built using Python's Tkinter. 


## Team Responsibilities
- Gabe: UI
- Goncalo: Queries
- Danielle: Application logic
- Dario: Documentation

Along with being responsible for their own tables:
- Danielle: Order & Order_Detail
- Goncalo: Customer
- Gabe: Employee
- Dario: Book

Our advanced features include:
- Use of foreign keys and constraints
- A well-designed interface with clear navigation


