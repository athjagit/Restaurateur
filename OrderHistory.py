import tkinter as tk
from tkinter import ttk
import DataLoaders as DL
from PIL import Image, ImageTk

class OrderHistoryApp(tk.Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.title("Order History")
        self.state('zoomed')
        self.resizable(False, False)
        self.columnconfigure(0, weight=1)
        root.withdraw()

        # Search Bar
        self.search_var = tk.StringVar()
        
        # Search Entry (Increased width)
        self.search_entry = tk.Entry(self, textvariable=self.search_var, width=30)  # Increased width
        self.search_entry.grid(row=0, column=0, padx=(10, 0), sticky='E', pady=10)
        self.search_entry.bind("<KeyRelease>", self.on_search)  # Call the on_search method on key release

        # Clear button (flat style)
        self.clear_button = tk.Button(self, text="X", command=self.clear_search, relief='flat')
        self.clear_button.grid(row=0, column=1, sticky='w', padx=(0, 5), pady=10)

        self.done_btn = tk.Button(self, text="Done", command=self.on_closing, padx=10, pady=5, bg='#4CAF50', font=("Arial", 10, "bold"))
        self.done_btn.grid(row=0, sticky='w', column=2, padx=10, pady=10)

        self.info_image = Image.open("i.png")
        self.info_image = self.info_image.resize((30, 30), Image.LANCZOS)  # Resize if necessary
        self.info_photo = ImageTk.PhotoImage(self.info_image)

        # Notebook for displaying orders
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, padx=10, columnspan=3, pady=10, sticky='nsew')
        self.grid_rowconfigure(1, weight=1)

        # Load orders
        self.orders = []
        self.load_order_history()

    def load_order_history(self):
        """Reads the orders and populates the UI with non-editable order history."""
        self.orders = DL.read_orders_csv()[::-1]  # Read updated orders from file and reverse the order
        self.populate_tabs(6)

    def populate_tabs(self, orders_per_tab):
        """Dynamically creates tabs and populates them with order cards."""
        # Clear all tabs
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
        self.populate_tabs(6)  # Refresh tabs with the filtered results

    def clear_search(self):
        """Clears the search bar and repopulates the tabs with all orders."""
        self.search_var.set("")
        self.populate_tabs(6)

    def create_order_card(self, parent, order):
        """Creates a card for each order displaying its details (non-editable)."""
        order_id = order["OrderID"]
        customer_id = order["CustomerID"]
        contents = order["Contents"]
        status = order["Status"]

        frame = tk.Frame(parent, bg="white", bd=2, relief=tk.GROOVE)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Configure grid layout for alignment
        frame.grid_columnconfigure(0, weight=0)  # Left-aligned text
        frame.grid_columnconfigure(1, weight=1)  # Status label
        frame.grid_columnconfigure(2, weight=0)  # Price label

        # Order ID (aligned to the left)
        order_id_label = tk.Label(frame, text=f"Order ID: {order_id}", font=("Arial", 16, "bold"), bg="white")
        order_id_label.grid(row=0, column=0, sticky="w", padx=10, pady=(7, 0))

        info_button = tk.Button(frame, image=self.info_photo, command=lambda: self.show_order_info(contents, order['Total']), relief='flat', background='white')
        info_button.grid(row=0, column=1, columnspan=2, padx=(3, 10), pady=(5, 0), sticky='w')

        custname_label = tk.Label(frame, text=f"Customer ID: {customer_id}", font=("Arial", 16, "normal"), bg="white")
        custname_label.grid(row=0, column=12, sticky="e", padx=10, pady=(7, 0))

        # Status label (non-editable)
        status_label = tk.Label(frame, text=f"Status: {status}", font=("Arial", 14, "italic"), bg="white")
        status_label.grid(row=1, column=1, sticky="e", padx=10, pady=10)

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
    app = OrderHistoryApp(root)
    root.mainloop()
