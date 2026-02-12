# gui/views.py
# This file contains the different "pages" or "views" for your application.

import tkinter as tk
from tkinter import messagebox, ttk

# Try to import your backend logic functions, but make them optional for testing
try:
    from app.book_logic import search_book_by_isbn, add_book_and_credit_customer
    from app.customer_logic import add_new_customer, lookup_customer_credit_by_email, mark_customer_as_inactive
    from app.employee_logic import add_new_employee, mark_employee_as_terminated
    from app.order_logic import (
        fetch_customer_by_id,
        lookup_customer_credit_by_id,
        search_book_by_isbn_for_order,
        validate_book_by_id,
        complete_order
    )


    BACKEND_AVAILABLE = True
except ImportError:
    BACKEND_AVAILABLE = False


# A helper function for consistent styling of pages
def create_page_title(parent, text):
    """Creates a styled title label for a page."""
    return tk.Label(parent, text=text, font=("Arial", 20, "bold"), bg="#ecf0f1", fg="#2c3e50")


# --- Book-Related Views ---

class BookSearchView(tk.Frame):
    """A view for searching books by their ISBN."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#ecf0f1")

        # --- Widgets ---
        create_page_title(self, "Search Book by ISBN").pack(pady=20, padx=20)

        input_frame = tk.Frame(self, bg="#ecf0f1")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="ISBN:", font=("Arial", 12), bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=5)
        self.isbn_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.isbn_entry.grid(row=0, column=1, padx=5, pady=5)

        search_button = tk.Button(input_frame, text="Search", command=self.perform_search, font=("Arial", 12),
                                  bg="#3498db", fg="white", relief="flat", highlightthickness=0)
        search_button.grid(row=0, column=2, padx=10)

        results_frame = tk.Frame(self, bg="white", relief="sunken", borderwidth=1)
        results_frame.pack(pady=20, padx=20, fill="x")

        tk.Label(results_frame, text="Search Results", font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        self.result_text = tk.Label(results_frame, text="Enter an ISBN and click Search.", font=("Arial", 12),
                                    bg="white", justify="left", wraplength=400)
        self.result_text.pack(pady=10, padx=10)

    def perform_search(self):
        """Handles the button click to search for a book by calling the backend."""
        isbn = self.isbn_entry.get().strip()
        if not isbn:
            messagebox.showwarning("Input Error", "Please enter an ISBN.")
            return

        if not BACKEND_AVAILABLE:
            self.result_text.config(text="Backend not available - this is a test", fg="orange")
            return

        success, result = search_book_by_isbn(isbn)

        if success:
            # Format the successful result for display
            book_info = (
                f"Book Name: {result['book_name']}\n\n"
                f"Author: {result['author_name']}\n\n"
                f"Price: ${result['resale_price']:.2f}\n\n"
                f"Availability: {result['availability']}"
            )
            self.result_text.config(text=book_info, fg="black")
        else:
            # Display the error message from the backend (e.g., "No book found...")
            self.result_text.config(text=result, fg="red")


class BuyBookView(tk.Frame):
    """A view for buying a used book and crediting a customer."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#ecf0f1")

        # --- Page Title ---
        create_page_title(self, "Buy Used Book from Customer").pack(pady=(20, 10), padx=20)

        # --- Create main container frame ---
        main_container = tk.Frame(self, bg="#ecf0f1")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Scrollable Area for the form ---
        canvas = tk.Canvas(main_container, bg="#ecf0f1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ecf0f1")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Form Fields ---
        self.entries = {}
        fields = {
            "book_name": ("Book Name:", False),
            "author_name": ("Author Name:", False),
            "book_condition": ("Condition:", False),
            "average_ratings": ("Avg. Rating (0-5):", True),
            "isbn": ("ISBN:", False),
            "isbn_13": ("ISBN-13:", False),
            "language": ("Language:", False),
            "num_pages": ("Number of Pages:", True),
            "purchase_price": ("Purchase Price ($):", True),
            "resale_price": ("Resale Price ($):", True),
            "customer_id": ("Customer ID:", True)
        }

        # Create form fields using grid within the scrollable frame
        for i, (name, (text, is_numeric)) in enumerate(fields.items()):
            tk.Label(scrollable_frame, text=text, font=("Arial", 12), bg="#ecf0f1").grid(
                row=i, column=0, padx=10, pady=8, sticky="w"
            )
            entry = tk.Entry(scrollable_frame, font=("Arial", 12), width=40)
            entry.grid(row=i, column=1, padx=10, pady=8, sticky="ew")
            self.entries[name] = entry

        # Configure the scrollable frame to expand the entry column
        scrollable_frame.grid_columnconfigure(1, weight=1)

        # --- Submit Button (outside the scrollable area) ---
        button_frame = tk.Frame(self, bg="#ecf0f1")
        button_frame.pack(pady=20)

        submit_button = tk.Button(button_frame, text="Submit Purchase", command=self.perform_purchase,
                                  font=("Arial", 14, "bold"), bg="#27ae60", fg="white", relief="flat",
                                  highlightthickness=0, padx=20, pady=8)
        submit_button.pack()

        # Bind mousewheel to canvas for scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

    def perform_purchase(self):
        """Gathers data, validates it, and calls the backend function."""
        if not BACKEND_AVAILABLE:
            messagebox.showinfo("Test Mode", "Backend not available - this is a test of the form")
            return

        data = {}
        for name, entry in self.entries.items():
            value = entry.get().strip()
            if not value:
                messagebox.showwarning("Input Error", f"Field '{name.replace('_', ' ').title()}' cannot be empty.")
                return

            is_numeric = name in ["average_ratings", "num_pages", "purchase_price", "resale_price", "customer_id"]
            if is_numeric:
                try:
                    if '.' in value:
                        data[name] = float(value)
                    else:
                        data[name] = int(value)
                except ValueError:
                    messagebox.showwarning("Input Error",
                                           f"Field '{name.replace('_', ' ').title()}' must be a valid number.")
                    return
            else:
                data[name] = value

        success, result = add_book_and_credit_customer(
            book_name=data["book_name"], author_name=data["author_name"],
            book_condition=data["book_condition"], average_ratings=data["average_ratings"],
            isbn=data["isbn"], isbn_13=data["isbn_13"],
            language=data["language"], num_pages=data["num_pages"],
            purchase_price=data["purchase_price"], resale_price=data["resale_price"],
            customer_id=data["customer_id"]
        )

        if success:
            messagebox.showinfo("Success",
                                f"Book purchased and customer credited!\nNew Book ID: {result['book_id']}\nCustomer's New Credit Total: ${result['credit_total']:.2f}")
            for entry in self.entries.values():
                entry.delete(0, tk.END)
        else:
            messagebox.showerror("Database Error", f"Could not complete purchase.\nError: {result}")


# --- Customer-Related Views ---

class CustomerManagementView(tk.Frame):
    """A combined view for adding and deactivating customers."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#ecf0f1")

        create_page_title(self, "Customer Management").pack(pady=20, padx=20, anchor="w")

        # --- Add Customer Section ---
        add_frame = tk.LabelFrame(self, text="Add New Customer", font=("Arial", 12, "bold"), bg="#ecf0f1", padx=15,
                                  pady=15)
        add_frame.pack(pady=10, padx=20, fill="x")

        tk.Label(add_frame, text="First Name:", font=("Arial", 12), bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=8,
                                                                                       sticky="w")
        self.first_name_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=8)

        tk.Label(add_frame, text="Last Name:", font=("Arial", 12), bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=8,
                                                                                      sticky="w")
        self.last_name_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=8)

        tk.Label(add_frame, text="Email:", font=("Arial", 12), bg="#ecf0f1").grid(row=2, column=0, padx=5, pady=8,
                                                                                  sticky="w")
        self.email_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.email_entry.grid(row=2, column=1, padx=5, pady=8)

        add_button = tk.Button(add_frame, text="Add Customer", command=self.perform_add_customer,
                               font=("Arial", 12, "bold"),
                               bg="#2ecc71", fg="white", relief="flat", padx=10, pady=5, highlightthickness=0)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        # --- Deactivate Customer Section ---
        deactivate_frame = tk.LabelFrame(self, text="Mark Customer as Inactive", font=("Arial", 12, "bold"),
                                         bg="#ecf0f1", padx=15, pady=15)
        deactivate_frame.pack(pady=20, padx=20, fill="x")

        tk.Label(deactivate_frame, text="Customer ID:", font=("Arial", 12), bg="#ecf0f1").grid(row=0, column=0, padx=5,
                                                                                               pady=8, sticky="w")
        self.deactivate_id_entry = tk.Entry(deactivate_frame, font=("Arial", 12), width=30)
        self.deactivate_id_entry.grid(row=0, column=1, padx=5, pady=8)

        deactivate_button = tk.Button(deactivate_frame, text="Mark as Inactive",
                                      command=self.perform_deactivate_customer, font=("Arial", 12, "bold"),
                                      bg="#e74c3c", fg="white", relief="flat", padx=10, pady=5, highlightthickness=0)
        deactivate_button.grid(row=1, column=0, columnspan=2, pady=10)

    def perform_add_customer(self):
        """Handles the button click to add a new customer."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        email = self.email_entry.get().strip()

        if not all([first_name, last_name, email]):
            messagebox.showwarning("Input Error", "All fields are required.")
            return

        if not BACKEND_AVAILABLE:
            messagebox.showinfo("Test Mode", f"Backend not available - would add: {first_name} {last_name} ({email})")
            return

        success, result = add_new_customer(first_name, last_name, email)

        if success:
            messagebox.showinfo("Success", f"Customer added successfully with ID: {result}")
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.email_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"Could not add customer: {result}")

    def perform_deactivate_customer(self):
        """Handles the button click to mark a customer as inactive."""
        customer_id = self.deactivate_id_entry.get().strip()
        if not customer_id:
            messagebox.showwarning("Input Error", "Customer ID is required.")
            return

        if not messagebox.askyesno("Confirm Deactivation",
                                   f"Are you sure you want to mark customer with ID: {customer_id} as inactive?"):
            return

        if not BACKEND_AVAILABLE:
            messagebox.showinfo("Test Mode", "Backend not available.")
            return

        success, result = mark_customer_as_inactive(customer_id)

        if success:
            messagebox.showinfo("Success", result)  # Backend returns a success message
            self.deactivate_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"Could not deactivate customer: {result}")


class CreditLookUpView(tk.Frame):
    """A view for looking up a customer's credit by their email."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#ecf0f1")

        create_page_title(self, "Look Up Customer Credit").pack(pady=20, padx=20)

        # --- Input Frame ---
        input_frame = tk.Frame(self, bg="#ecf0f1")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="Customer Email:", font=("Arial", 12), bg="#ecf0f1").grid(row=0, column=0, padx=5,
                                                                                             pady=5)
        self.email_entry = tk.Entry(input_frame, font=("Arial", 12), width=30)
        self.email_entry.grid(row=0, column=1, padx=5, pady=5)

        lookup_button = tk.Button(input_frame, text="Look Up", command=self.perform_lookup, font=("Arial", 12),
                                  bg="#3498db", fg="white", relief="flat", highlightthickness=0)
        lookup_button.grid(row=0, column=2, padx=10)

        # --- Results Frame ---
        results_frame = tk.Frame(self, bg="white", relief="sunken", borderwidth=1, width=400, height=100)
        results_frame.pack(pady=20, padx=20)
        results_frame.pack_propagate(False)  # Prevent frame from shrinking to fit label

        self.result_text = tk.Label(results_frame, text="Enter a customer email and click Look Up.",
                                    font=("Arial", 14), bg="white", justify="center")
        self.result_text.pack(expand=True)

    def perform_lookup(self):
        """Handles the button click to look up customer credit."""
        email = self.email_entry.get().strip()
        if not email:
            messagebox.showwarning("Input Error", "Please enter a customer email.")
            return

        if not BACKEND_AVAILABLE:
            self.result_text.config(text="Backend not available.", fg="orange")
            return

        success, result = lookup_customer_credit_by_email(email)

        if success:
            # On success, result is the credit amount
            self.result_text.config(text=f"Credit Balance: ${result:.2f}", fg="green", font=("Arial", 16, "bold"))
        else:
            # On failure, result is an error message string
            self.result_text.config(text=result, fg="red", font=("Arial", 12))


# --- Employee-Related Views ---

class EmployeeManagementView(tk.Frame):
    """A combined view for adding and terminating employees."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#ecf0f1")

        create_page_title(self, "Employee Management").pack(pady=20, padx=20, anchor="w")

        # --- Add Employee Section ---
        add_frame = tk.LabelFrame(self, text="Add New Employee", font=("Arial", 12, "bold"), bg="#ecf0f1", padx=15,
                                  pady=15)
        add_frame.pack(pady=10, padx=20, fill="x")

        # Form Fields
        tk.Label(add_frame, text="First Name:", font=("Arial", 12), bg="#ecf0f1").grid(row=0, column=0, padx=5, pady=8,
                                                                                       sticky="w")
        self.first_name_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.first_name_entry.grid(row=0, column=1, padx=5, pady=8)

        tk.Label(add_frame, text="Last Name:", font=("Arial", 12), bg="#ecf0f1").grid(row=1, column=0, padx=5, pady=8,
                                                                                      sticky="w")
        self.last_name_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.last_name_entry.grid(row=1, column=1, padx=5, pady=8)

        tk.Label(add_frame, text="Phone Number:", font=("Arial", 12), bg="#ecf0f1").grid(row=2, column=0, padx=5,
                                                                                         pady=8, sticky="w")
        self.phone_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.phone_entry.grid(row=2, column=1, padx=5, pady=8)

        tk.Label(add_frame, text="Access Level:", font=("Arial", 12), bg="#ecf0f1").grid(row=3, column=0, padx=5,
                                                                                         pady=8, sticky="w")
        self.access_level_entry = tk.Entry(add_frame, font=("Arial", 12), width=30)
        self.access_level_entry.grid(row=3, column=1, padx=5, pady=8)

        # Submit Button
        add_button = tk.Button(add_frame, text="Add Employee", command=self.perform_add_employee,
                               font=("Arial", 12, "bold"),
                               bg="#2ecc71", fg="white", relief="flat", padx=10, pady=5, highlightthickness=0)
        add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Terminate Employee Section ---
        terminate_frame = tk.LabelFrame(self, text="Terminate Employee", font=("Arial", 12, "bold"), bg="#ecf0f1",
                                        padx=15, pady=15)
        terminate_frame.pack(pady=20, padx=20, fill="x")

        tk.Label(terminate_frame, text="Employee ID:", font=("Arial", 12), bg="#ecf0f1").grid(row=0, column=0, padx=5,
                                                                                              pady=8, sticky="w")
        self.terminate_id_entry = tk.Entry(terminate_frame, font=("Arial", 12), width=30)
        self.terminate_id_entry.grid(row=0, column=1, padx=5, pady=8)

        terminate_button = tk.Button(terminate_frame, text="Terminate Employee",
                                     command=self.perform_terminate_employee, font=("Arial", 12, "bold"),
                                     bg="#c0392b", fg="white", relief="flat", padx=10, pady=5, highlightthickness=0)
        terminate_button.grid(row=1, column=0, columnspan=2, pady=10)

    def perform_add_employee(self):
        """Handles the button click to add a new employee."""
        first_name = self.first_name_entry.get().strip()
        last_name = self.last_name_entry.get().strip()
        phone_number = self.phone_entry.get().strip()
        access_level = self.access_level_entry.get().strip()

        if not all([first_name, last_name, phone_number, access_level]):
            messagebox.showwarning("Input Error", "All fields for adding an employee are required.")
            return

        if not BACKEND_AVAILABLE:
            messagebox.showinfo("Test Mode", "Backend not available.")
            return

        success, result = add_new_employee(first_name, last_name, phone_number, access_level)

        if success:
            messagebox.showinfo("Success", f"Employee added successfully with ID: {result}")
            self.first_name_entry.delete(0, tk.END)
            self.last_name_entry.delete(0, tk.END)
            self.phone_entry.delete(0, tk.END)
            self.access_level_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"Could not add employee: {result}")

    def perform_terminate_employee(self):
        """Handles the button click to terminate an employee."""
        employee_id = self.terminate_id_entry.get().strip()
        if not employee_id:
            messagebox.showwarning("Input Error", "Employee ID is required.")
            return

        # Confirmation dialog to prevent accidental termination
        if not messagebox.askyesno("Confirm Termination",
                                   f"Are you sure you want to terminate employee with ID: {employee_id}?"):
            return

        if not BACKEND_AVAILABLE:
            messagebox.showinfo("Test Mode", "Backend not available.")
            return

        success, result = mark_employee_as_terminated(employee_id)

        if success:
            messagebox.showinfo("Success", result)  # Backend returns a success message
            self.terminate_id_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", f"Could not terminate employee: {result}")


# Add this to your views.py file

class OrderProcessingView(tk.Frame):
    """A view for creating and processing customer orders."""

    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.configure(bg="#ecf0f1")

        # Initialize order data
        self.order_items = []  # List of dictionaries: [{'book_id': X, 'title': Y, 'price': Z}, ...]
        self.customer_credit = 0.0
        self.selected_customer_id = None

        # --- Page Title ---
        create_page_title(self, "Process Customer Order").pack(pady=(20, 10), padx=20)

        # --- Main Container with Scrollbar ---
        main_container = tk.Frame(self, bg="#ecf0f1")
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = tk.Canvas(main_container, bg="#ecf0f1", highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg="#ecf0f1")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- Customer Selection Section ---
        customer_frame = tk.LabelFrame(scrollable_frame, text="Customer Information",
                                       font=("Arial", 12, "bold"), bg="#ecf0f1", padx=15, pady=15)
        customer_frame.pack(fill="x", pady=(0, 20))

        # Customer ID input
        tk.Label(customer_frame, text="Customer ID:", font=("Arial", 12), bg="#ecf0f1").grid(
            row=0, column=0, padx=5, pady=8, sticky="w")
        self.customer_id_entry = tk.Entry(customer_frame, font=("Arial", 12), width=15)
        self.customer_id_entry.grid(row=0, column=1, padx=5, pady=8)

        load_customer_btn = tk.Button(customer_frame, text="Load Customer",
                                      command=self.load_customer_info,
                                      font=("Arial", 10), bg="#3498db", fg="white",
                                      relief="flat", highlightthickness=0)
        load_customer_btn.grid(row=0, column=2, padx=10, pady=8)

        # Customer info display
        self.customer_info_label = tk.Label(customer_frame, text="No customer loaded",
                                            font=("Arial", 11), bg="#ecf0f1", fg="#7f8c8d")
        self.customer_info_label.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="w")

        # --- Add Books Section ---
        books_frame = tk.LabelFrame(scrollable_frame, text="Add Books to Order",
                                    font=("Arial", 12, "bold"), bg="#ecf0f1", padx=15, pady=15)
        books_frame.pack(fill="x", pady=(0, 20))

        # Book search by ISBN
        tk.Label(books_frame, text="Book ISBN:", font=("Arial", 12), bg="#ecf0f1").grid(
            row=0, column=0, padx=5, pady=8, sticky="w")
        self.book_isbn_entry = tk.Entry(books_frame, font=("Arial", 12), width=20)
        self.book_isbn_entry.grid(row=0, column=1, padx=5, pady=8)

        search_book_btn = tk.Button(books_frame, text="Search Book",
                                    command=self.search_and_add_book,
                                    font=("Arial", 10), bg="#27ae60", fg="white",
                                    relief="flat", highlightthickness=0)
        search_book_btn.grid(row=0, column=2, padx=10, pady=8)

        # Or manual book entry
        tk.Label(books_frame, text="Or manually add:", font=("Arial", 11, "italic"),
                 bg="#ecf0f1", fg="#7f8c8d").grid(row=1, column=0, columnspan=3, pady=(15, 5))

        tk.Label(books_frame, text="Book ID:", font=("Arial", 12), bg="#ecf0f1").grid(
            row=2, column=0, padx=5, pady=5, sticky="w")
        self.manual_book_id_entry = tk.Entry(books_frame, font=("Arial", 12), width=10)
        self.manual_book_id_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        tk.Label(books_frame, text="Book Title:", font=("Arial", 12), bg="#ecf0f1").grid(
            row=3, column=0, padx=5, pady=5, sticky="w")
        self.manual_book_title_entry = tk.Entry(books_frame, font=("Arial", 12), width=30)
        self.manual_book_title_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(books_frame, text="Price:", font=("Arial", 12), bg="#ecf0f1").grid(
            row=4, column=0, padx=5, pady=5, sticky="w")
        self.manual_book_price_entry = tk.Entry(books_frame, font=("Arial", 12), width=10)
        self.manual_book_price_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        add_manual_btn = tk.Button(books_frame, text="Add Book Manually",
                                   command=self.add_book_manually,
                                   font=("Arial", 10), bg="#f39c12", fg="white",
                                   relief="flat", highlightthickness=0)
        add_manual_btn.grid(row=5, column=0, columnspan=2, pady=10, sticky="w")

        # --- Order Items Display ---
        items_frame = tk.LabelFrame(scrollable_frame, text="Order Items",
                                    font=("Arial", 12, "bold"), bg="#ecf0f1", padx=15, pady=15)
        items_frame.pack(fill="x", pady=(0, 20))

        # Treeview for order items
        self.items_tree = ttk.Treeview(items_frame, columns=("book_id", "title", "price"),
                                       show="headings", height=6)
        self.items_tree.heading("book_id", text="Book ID")
        self.items_tree.heading("title", text="Book Title")
        self.items_tree.heading("price", text="Price")

        self.items_tree.column("book_id", width=80, anchor="center")
        self.items_tree.column("title", width=300, anchor="w")
        self.items_tree.column("price", width=100, anchor="e")

        self.items_tree.pack(fill="x", pady=(0, 10))

        # Remove item button
        remove_item_btn = tk.Button(items_frame, text="Remove Selected Item",
                                    command=self.remove_selected_item,
                                    font=("Arial", 10), bg="#e74c3c", fg="white",
                                    relief="flat", highlightthickness=0)
        remove_item_btn.pack(pady=5)

        # --- Order Summary Section ---
        summary_frame = tk.LabelFrame(scrollable_frame, text="Order Summary",
                                      font=("Arial", 12, "bold"), bg="#ecf0f1", padx=15, pady=15)
        summary_frame.pack(fill="x", pady=(0, 20))

        # Employee ID
        tk.Label(summary_frame, text="Employee ID:", font=("Arial", 12), bg="#ecf0f1").grid(
            row=0, column=0, padx=5, pady=8, sticky="w")
        self.employee_id_entry = tk.Entry(summary_frame, font=("Arial", 12), width=15)
        self.employee_id_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        # Order totals
        self.subtotal_label = tk.Label(summary_frame, text="Subtotal: $0.00",
                                       font=("Arial", 12, "bold"), bg="#ecf0f1")
        self.subtotal_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Store credit usage
        tk.Label(summary_frame, text="Use Store Credit:", font=("Arial", 12), bg="#ecf0f1").grid(
            row=2, column=0, padx=5, pady=8, sticky="w")
        self.credit_used_entry = tk.Entry(summary_frame, font=("Arial", 12), width=15)
        self.credit_used_entry.grid(row=2, column=1, padx=5, pady=8, sticky="w")
        self.credit_used_entry.bind("<KeyRelease>", self.update_final_total)

        self.available_credit_label = tk.Label(summary_frame, text="Available: $0.00",
                                               font=("Arial", 10), bg="#ecf0f1", fg="#7f8c8d")
        self.available_credit_label.grid(row=2, column=2, padx=10, pady=8, sticky="w")

        # Final total
        self.final_total_label = tk.Label(summary_frame, text="Final Amount: $0.00",
                                          font=("Arial", 14, "bold"), bg="#ecf0f1", fg="#27ae60")
        self.final_total_label.grid(row=3, column=0, columnspan=3, padx=5, pady=10, sticky="w")

        # --- Action Buttons ---
        button_frame = tk.Frame(scrollable_frame, bg="#ecf0f1")
        button_frame.pack(pady=20)

        preview_btn = tk.Button(button_frame, text="Preview Order",
                                command=self.preview_order,
                                font=("Arial", 12, "bold"), bg="#9b59b6", fg="white",
                                relief="flat", highlightthickness=0, padx=20, pady=8)
        preview_btn.pack(side="left", padx=10)

        complete_btn = tk.Button(button_frame, text="Complete Order",
                                 command=self.complete_order,
                                 font=("Arial", 12, "bold"), bg="#27ae60", fg="white",
                                 relief="flat", highlightthickness=0, padx=20, pady=8)
        complete_btn.pack(side="left", padx=10)

        clear_btn = tk.Button(button_frame, text="Clear Order",
                              command=self.clear_order,
                              font=("Arial", 12), bg="#95a5a6", fg="white",
                              relief="flat", highlightthickness=0, padx=20, pady=8)
        clear_btn.pack(side="left", padx=10)

        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind("<MouseWheel>", _on_mousewheel)

    def load_customer_info(self):
        """Load customer information and credit balance."""
        customer_id = self.customer_id_entry.get().strip()
        if not customer_id:
            messagebox.showwarning("Input Error", "Please enter a customer ID.")
            return
        """ #DELETE?
        if not BACKEND_AVAILABLE:
            # Mock data for testing
            self.selected_customer_id = customer_id
            self.customer_credit = 45.50
            self.customer_info_label.config(
                text=f"Customer ID: {customer_id} | Available Credit: ${self.customer_credit:.2f}",
                fg="#27ae60")
            self.available_credit_label.config(text=f"Available: ${self.customer_credit:.2f}")
            return
        """
        success, result = fetch_customer_by_id(customer_id)
        if success:
            self.selected_customer_id = result["customer_id"]
            self.customer_credit = result["credit_total"]

            self.customer_info_label.config(
                text=f"{result['name']} | Available Credit: ${self.customer_credit:.2f}",
                fg="#27ae60"
            )
            self.available_credit_label.config(
                text=f"Available: ${self.customer_credit:.2f}"
            )
        else:
            messagebox.showerror("Error", result)

    def search_and_add_book(self):
        """Search for a book by ISBN and add it to the order."""
        isbn = self.book_isbn_entry.get().strip()
        if not isbn:
            messagebox.showwarning("Input Error", "Please enter an ISBN.")
            return
        """#Delete
        if not BACKEND_AVAILABLE:
            # Mock book data
            mock_book = {
                'book_id': len(self.order_items) + 100,
                'title': f"Sample Book (ISBN: {isbn})",
                'price': 15.99
            }
            self.order_items.append(mock_book)
            self.update_order_display()
            self.book_isbn_entry.delete(0, tk.END)
            return

        # Here you would call search_book_by_isbn(isbn) and add to order
        messagebox.showinfo("Test Mode", "Backend not available - adding mock book")
        """
        success, result = search_book_by_isbn_for_order(isbn)
        if success:
            # Add book to order_items
            book = {
                "book_id": result["book_id"],
                "title": result["book_name"],
                "price": result["resale_price"]
            }
            self.order_items.append(book)
            self.update_order_display()
            self.book_isbn_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", result)

    def add_book_manually(self):
        """Add a book manually to the order."""
        book_id = self.manual_book_id_entry.get().strip()
        title = self.manual_book_title_entry.get().strip()
        price = self.manual_book_price_entry.get().strip()

        # Require Book ID always (for inventory integrity)
        if not book_id:
            messagebox.showwarning("Input Error", "Book ID is required.")
            return

        try:
            book_id_int = int(book_id)
        except ValueError:
            messagebox.showwarning("Input Error", "Book ID must be a number.")
            return

        # Validate the book in DB
        success, result = validate_book_by_id(book_id_int)
        if success:
            # Auto-fill title and price from DB for inventory items
            title = result["book_name"]
            price_float = result["resale_price"]
        else:
            # If the book isn't in inventory, require manual title/price
            if not title or not price:
                messagebox.showwarning("Input Error", "Title and Price are required for non-inventory items.")
                return
            try:
                price_float = float(price)
            except ValueError:
                messagebox.showwarning("Input Error", "Price must be a valid number.")
                return

        """ # Delete-need to make sure we check for book_id in Book table and use that info first.
        if not all([book_id, title, price]):
            messagebox.showwarning("Input Error", "All fields are required for manual entry.")
            return

        try:
            price_float = float(price)
            book_id_int = int(book_id)
        except ValueError:
            messagebox.showwarning("Input Error", "Book ID must be a number and price must be a valid amount.")
            return
        """
        # Check if book already in order
        if any(item['book_id'] == book_id_int for item in self.order_items):
            messagebox.showwarning("Duplicate Item", "This book is already in the order.")
            return

        book_item = {
            'book_id': book_id_int,
            'title': title,
            'price': price_float
        }

        self.order_items.append(book_item)
        self.update_order_display()

        # Clear manual entry fields
        self.manual_book_id_entry.delete(0, tk.END)
        self.manual_book_title_entry.delete(0, tk.END)
        self.manual_book_price_entry.delete(0, tk.END)

    def remove_selected_item(self):
        """Remove the selected item from the order."""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return

        item = self.items_tree.item(selection[0])
        book_id = int(item['values'][0])

        # Remove from order_items list
        self.order_items = [item for item in self.order_items if item['book_id'] != book_id]
        self.update_order_display()

    def update_order_display(self):
        """Update the order items display and totals."""
        # Clear treeview
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)

        # Add items to treeview
        subtotal = 0.0
        for item in self.order_items:
            self.items_tree.insert("", "end", values=(
                item['book_id'],
                item['title'],
                f"${item['price']:.2f}"
            ))
            subtotal += item['price']

        # Update subtotal
        self.subtotal_label.config(text=f"Subtotal: ${subtotal:.2f}")
        self.update_final_total()

    def update_final_total(self, event=None):
        """Update the final total based on store credit used."""
        subtotal = sum(item['price'] for item in self.order_items)

        credit_used = 0.0
        credit_text = self.credit_used_entry.get().strip()
        if credit_text:
            try:
                credit_used = float(credit_text)
                if credit_used > self.customer_credit:
                    credit_used = self.customer_credit
                    self.credit_used_entry.delete(0, tk.END)
                    self.credit_used_entry.insert(0, f"{credit_used:.2f}")
            except ValueError:
                pass

        final_amount = max(0, subtotal - credit_used)
        self.final_total_label.config(text=f"Final Amount: ${final_amount:.2f}")

    def preview_order(self):
        """Show a preview of the order before completion."""
        if not self.order_items:
            messagebox.showwarning("Empty Order", "Please add items to the order first.")
            return

        if not self.selected_customer_id:
            messagebox.showwarning("Missing Customer", "Please load a customer first.")
            return

        subtotal = sum(item['price'] for item in self.order_items)
        credit_used = float(self.credit_used_entry.get() or "0")
        final_amount = max(0, subtotal - credit_used)

        preview_text = f"""Order Preview:

Customer ID: {self.selected_customer_id}
Employee ID: {self.employee_id_entry.get() or 'Not specified'}

Items ({len(self.order_items)}):
"""
        for item in self.order_items:
            preview_text += f"  - {item['title']} (ID: {item['book_id']}) - ${item['price']:.2f}\n"

        preview_text += f"""
Subtotal: ${subtotal:.2f}
Store Credit Used: ${credit_used:.2f}
Final Amount: ${final_amount:.2f}"""

        messagebox.showinfo("Order Preview", preview_text)

    def complete_order(self):
        """Complete the order and process payment."""
        if not self.order_items:
            messagebox.showwarning("Empty Order", "Please add items to the order first.")
            return

        if not self.selected_customer_id:
            messagebox.showwarning("Missing Customer", "Please load a customer first.")
            return

        employee_id = self.employee_id_entry.get().strip()
        if not employee_id:
            messagebox.showwarning("Missing Employee", "Please enter an employee ID.")
            return

        if not messagebox.askyesno("Confirm Order", "Are you sure you want to complete this order?"):
            return

        credit_used = float(self.credit_used_entry.get() or "0")

        success, result = complete_order(
            self.selected_customer_id,
            employee_id,
            self.order_items,
            credit_used,
            self.customer_credit  # Pass current credit for proper deduction
        )

        if success:
            messagebox.showinfo("Success", f"Order #{result['order_id']} completed successfully!")
            self.clear_order()
        else:
            messagebox.showerror("Error", result)

        """ #  Delete
        if not BACKEND_AVAILABLE:
            messagebox.showinfo("Test Mode", "Order would be completed in real system!")
            self.clear_order()
            return

        # Here you would call your backend function to complete the order
        # success, result = complete_order(customer_id, employee_id, order_items, credit_used)
        messagebox.showinfo("Success", "Order completed successfully!")
        """


    def clear_order(self):
        """Clear all order data and reset the form."""
        if self.order_items and not messagebox.askyesno("Clear Order", "Are you sure you want to clear this order?"):
            return

        # Clear all fields
        self.order_items = []
        self.customer_credit = 0.0
        self.selected_customer_id = None

        self.customer_id_entry.delete(0, tk.END)
        self.book_isbn_entry.delete(0, tk.END)
        self.manual_book_id_entry.delete(0, tk.END)
        self.manual_book_title_entry.delete(0, tk.END)
        self.manual_book_price_entry.delete(0, tk.END)
        self.employee_id_entry.delete(0, tk.END)
        self.credit_used_entry.delete(0, tk.END)

        self.customer_info_label.config(text="No customer loaded", fg="#7f8c8d")
        self.available_credit_label.config(text="Available: $0.00")

        self.update_order_display()