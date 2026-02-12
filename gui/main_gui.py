# gui/main_gui.py
import tkinter as tk
from tkinter import Frame, Button, Label
import sys
import os

# --- Setup Project Path ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(project_root)
sys.path.append(project_root)
# --- End of Setup ---

# Now that the working directory and path are correct, these imports will work.
# Import the new CustomerManagementView and OrderProcessingView
from gui.views import BookSearchView, CustomerManagementView, BuyBookView, CreditLookUpView, EmployeeManagementView, \
    OrderProcessingView


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Used Bookstore Management System")
        self.geometry("1000x700")
        self.minsize(800, 600)

        # --- Basic Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = Frame(self, bg="#2c3e50", width=200)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_propagate(False)

        Label(self.sidebar_frame, text="Bookstore DB", bg="#2c3e50", fg="white", font=("Arial", 18, "bold")).pack(
            pady=20, padx=10)

        # --- Main Content Frame ---
        self.content_frame = Frame(self, bg="#ecf0f1")
        self.content_frame.grid(row=0, column=1, sticky="nsew")

        # --- Page Container ---
        container = Frame(self.content_frame, bg="#ecf0f1")
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # --- Dictionary of Pages/Views ---
        # Replace "Add Customer" with "Manage Customers"
        self.pages = {
            "Process Order": OrderProcessingView,
            "Buy Book": BuyBookView,
            "Search Book": BookSearchView,
            "Manage Customers": CustomerManagementView,
            "Look Up Credit": CreditLookUpView,
            "Manage Employees": EmployeeManagementView,
        }

        self.frames = {}
        for page_name, F in self.pages.items():
            frame = F(container)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # --- Create Sidebar Buttons ---
        for page_name in self.pages.keys():
            btn = Button(self.sidebar_frame, text=page_name, bg="#34495e", fg="white", font=("Arial", 12),
                         relief="flat", cursor="hand2", anchor="w", padx=10, highlightthickness=0,
                         command=lambda p=page_name: self.navigate_to(p))
            btn.pack(fill="x", pady=2)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#4a6278"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#34495e"))

        # --- Initial Page ---
        self.show_welcome_message()

    def navigate_to(self, page_name):
        """Raises the selected page frame to the top."""
        # Remove welcome message if it exists
        if hasattr(self, 'welcome_label'):
            self.welcome_label.destroy()
            delattr(self, 'welcome_label')

        view_class = self.pages[page_name]

        if view_class.__name__ in self.frames:
            frame = self.frames[view_class.__name__]
            # Make sure the frame is properly gridded and raised
            frame.grid(row=0, column=0, sticky="nsew")
            frame.tkraise()

    def show_welcome_message(self):
        """Displays the initial welcome message in the content area."""
        # Hide all page frames by removing them from grid
        for frame in self.frames.values():
            frame.grid_forget()

        # Create welcome message frame
        welcome_frame = Frame(self.content_frame, bg="#ecf0f1")
        welcome_frame.pack(fill="both", expand=True)

        # Create a more attractive welcome screen
        welcome_container = Frame(welcome_frame, bg="#ecf0f1")
        welcome_container.place(relx=0.5, rely=0.5, anchor="center")

        # Main welcome title
        welcome_title = Label(welcome_container,
                              text="Welcome to the Used Bookstore Database",
                              bg="#ecf0f1", fg="#2c3e50",
                              font=("Arial", 24, "bold"))
        welcome_title.pack(pady=(0, 20))

        # Subtitle
        welcome_subtitle = Label(welcome_container,
                                 text="Select an option from the sidebar to get started",
                                 bg="#ecf0f1", fg="#7f8c8d",
                                 font=("Arial", 14))
        welcome_subtitle.pack(pady=(0, 30))

        # Feature list
        features_frame = Frame(welcome_container, bg="#ecf0f1")
        features_frame.pack()

        features = [
            "🛒 Process customer orders",
            "📖 Buy books from customers",
            "🔍 Search books by ISBN",
            "👥 Manage customer accounts",
            "💰 Look up customer credits",
            "👨‍💼 Manage employee records"
        ]

        for feature in features:
            feature_label = Label(features_frame, text=feature,
                                  bg="#ecf0f1", fg="#34495e",
                                  font=("Arial", 12), anchor="w")
            feature_label.pack(pady=5, anchor="w")

        # Store reference to welcome frame so we can destroy it later
        self.welcome_label = welcome_frame


if __name__ == "__main__":
    app = Dashboard()
    app.mainloop()