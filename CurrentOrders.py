import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os  # For file handling
import DataLoaders as DL  # Assuming this is where your CSV reading logic is
from PIL import Image, ImageTk

class OrderManagementApp(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.title("Order Management")
        self.state('zoomed')
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        root.withdraw()

        # Search Bar
        self.search_var = tk.StringVar()
        
        # Search Entry
        self.search_entry = tk.Entry(self, textvariable=self.search_var, width=30)
        self.search_entry.grid(row=0, column=0, padx=(10, 0), sticky='E', pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)

        # Clear button
        self.clear_button = tk.Button(self, text="X", command=self.clear_search, relief='flat')
        self.clear_button.grid(row=0, column=1, sticky='w', padx=(0, 10))

        self.done_btn = tk.Button(self, text="Done", command=self.on_closing, padx=10, pady=5, bg='#4CAF50', font=("Arial", 10, "bold"))
        self.done_btn.grid(row=0, sticky='e', column=2)

        # Notebook for displaying orders
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, padx=10, columnspan=3, pady=10, sticky='nsew')
        self.grid_rowconfigure(1, weight=1)

        self.info_image = Image.open("i.png")
        self.info_image = self.info_image.resize((30, 30), Image.LANCZOS)  # Resize if necessary
        self.info_photo = ImageTk.PhotoImage(self.info_image)

        # Load orders and start periodic refresh
        self.orders = []
        self.refresh_orders()

    def refresh_orders(self):
        """Reads the orders and refreshes the UI every 10 seconds, skipping refresh if a ComboBox is focused."""
        # Check if a ComboBox has focus
        if self.focus_get() and isinstance(self.focus_get(), ttk.Combobox):
            self.after(10000, self.refresh_orders)
            return

        self.orders = [a for a in DL.read_orders_csv() if a['Status'] == 'Pending']
        print(self.orders)

        # Populate the tabs with new data
        self.populate_tabs(6)

        # Schedule the next refresh after 10 seconds
        self.after(10000, self.refresh_orders)

    def populate_tabs(self, orders_per_tab):
        """Dynamically creates tabs and populates them with order cards."""
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        filtered_orders = self.get_filtered_orders()

        num_tabs = (len(filtered_orders) + orders_per_tab - 1) // orders_per_tab
        for i in range(num_tabs):
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=f"Page {i + 1}")
            tab_frame.columnconfigure(0, weight=1)

            start = i * orders_per_tab
            end = start + orders_per_tab
            for order in filtered_orders[start:end]:
                self.create_order_card(tab_frame, order)

    def get_filtered_orders(self):
        """Returns a list of orders filtered by the search term."""
        search_term = self.search_var.get().lower()
        return [
            order for order in self.orders
            if search_term in str(order["OrderID"]).lower() or
            search_term in order["CustomerID"].lower() or
            any(search_term in item.lower() for item in order["Contents"].keys())
        ]

    def on_search(self, event=None):
        """Handles the search input and updates the displayed orders."""
        self.populate_tabs(6)

    def clear_search(self):
        """Clears the search bar and repopulates the tabs with all orders."""
        self.search_var.set("")
        self.populate_tabs(6)

    def create_order_card(self, parent, order):
        """Creates a card for each order displaying its details."""
        order_id = order["OrderID"]
        customer_id = order["CustomerID"]
        contents = order["Contents"]
        status = order["Status"]

        frame = tk.Frame(parent, bg="white", bd=2, relief=tk.GROOVE)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Configure grid layout for alignment
        frame.grid_columnconfigure(0, weight=0)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_columnconfigure(2, weight=0)

        # Order ID (aligned to the left)
        order_id_label = tk.Label(frame, text=f"Order ID: {order_id}", font=("Arial", 16, "bold"), bg="white")
        order_id_label.grid(row=0, column=0, sticky="w", padx=10, pady=(7, 0))

        custname_label = tk.Label(frame, text=f"Customer ID: {customer_id}", font=("Arial", 16, "normal"), bg="white")
        custname_label.grid(row=0, column=2, sticky="e", padx=10, pady=(7, 0))

        # Status label
        status_label = tk.Label(frame, text="Status:", bg="white")
        status_label.grid(row=1, column=1, sticky="e", padx=10, pady=10)

        info_button = tk.Button(frame, image=self.info_photo, command=lambda: self.show_order_info(contents, order['Total']), relief='flat', background='white')
        info_button.grid(row=0, column=1, columnspan=2, padx=(3, 10), pady=(5, 0), sticky='w')


        # Status ComboBox
        status_options = ["Pending", "Preparing", "Delivered"]
        status_var = tk.StringVar(value=status)
        status_combobox = ttk.Combobox(frame, textvariable=status_var, values=status_options, state="readonly")
        status_combobox.grid(row=1, column=2, sticky="e", padx=10, pady=10)

        # Add event handler for status change
        status_combobox.bind("<<ComboboxSelected>>", lambda e, order_id=order_id, customer_id=customer_id: self.on_status_change(order_id, customer_id, status_var.get()))

    def on_status_change(self, order_id, customer_id, new_status):
        """Handles the status change event by updating both orders.csv and {customer_id}_orders.csv."""
        try:
            self.update_order_status_in_csv("orders.csv", order_id, new_status)
            self.update_order_status_in_csv(f"{customer_id}_orders.csv", order_id, new_status)
            messagebox.showinfo("Status Updated", f"Order {order_id} status changed to {new_status}!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update status: {str(e)}")

    def update_order_status_in_csv(self, filename, order_id, new_status):
        """Updates the status of an order in the given CSV file."""
        rows = []
        file_exists = os.path.isfile(filename)

        if not file_exists:
            raise FileNotFoundError(f"{filename} does not exist!")

        # Read CSV and update the status
        with open(filename, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['OrderID'] == order_id:
                    row['Status'] = new_status
                rows.append(row)

        # Write back to the CSV
        with open(filename, mode='w', newline='') as file:
            fieldnames = rows[0].keys()  # Get field names from the first row
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def on_closing(self):
        self.destroy()
    
    def show_order_info(self, items, total_price):
        # Create a new window for displaying the order info
        info_window = tk.Toplevel(self.root)
        info_window.title("Order Details")

        # Create a text area to display the order details
        order_info = tk.Text(info_window, height=10, width=50)
        order_info.pack(padx=10, pady=10)

        # Format the items and total price
        order_info.insert(tk.END, "Items Ordered:\n")
        for a in items:
            order_info.insert(tk.END, f"{list(a.keys())[0]}: {a[list(a.keys())[0]]}x\n")
        order_info.insert(tk.END, f"\nTotal Price: ₹{total_price}")

        # Disable text area for editing
        order_info.config(state="disabled")

if __name__ == "__main__":
    root = tk.Tk()
    app = OrderManagementApp(root)
    root.mainloop()
