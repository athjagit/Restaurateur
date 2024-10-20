import tkinter as tk
from tkinter import ttk, Menu,messagebox
from datetime import datetime
from PIL import Image, ImageTk
from DataLoaders import CustomerSide, CustomerCheckout
import math

class RestaurantApp:
    def __init__(self, root: tk.Tk, username):
        self.root = root
        self.root.title("Restaurant Management System")
        self.root.bind('<Button-1>', self.clear_focus)
        self.user = username
        # Set a larger window size and minimum size
        self.root.state('zoomed')
        self.root.resizable(False, False)
        self.root.columnconfigure(0, weight=1)

        # Data
        self.DL = CustomerSide('menu_items.csv')
        self.menu_items = self.DL.items
        self.menu_items_linear = self.DL.items_linear
        self.qtyvars = [{'Name':a['Name'], "QtyVar": tk.IntVar(root, 0),'Price':0, 'Qty': 0} for a in self.menu_items_linear]
        self.order = []
        # Create the header bar
        self.create_header()

        # Category selection combobox
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.root, textvariable=self.category_var, state='readonly')
        self.category_combobox['values'] = list(self.menu_items.keys())
        self.category_combobox.bind("<<ComboboxSelected>>", self.load_category)
        self.category_combobox.grid(row=1, column=0, padx=10, pady=10)

        # Notebook (Tabs) for displaying items in the selected category
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')

        # Make the notebook expand with window resizing
        self.root.grid_rowconfigure(2, weight=1)

        # Load the 'Appetizers' category by default
        self.category_combobox.set("Appetizers")
        self.load_category(None)

        # Create the static "Checkout" button
        buttonframe = tk.Frame(root)
        buttonframe.grid(row = 3, sticky='e')
        self.create_checkout_button()

    def create_header(self):
        # Header frame
        header_frame = ttk.Frame(self.root)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=5)

        # Restaurant name label (left side)
        restaurant_name = ttk.Label(header_frame, text=f'Hi, {self.user}', font=("Arial", 16, "bold"))
        restaurant_name.pack(side="left")

        # Date label (right side)
        current_date = datetime.now().strftime("%A, %d|%m|%y")
        date_label = ttk.Label(header_frame, text=current_date, font=("Arial", 12))
        date_label.pack(side="right")

    def create_menu_bar(self):
        # Create a menu bar
        menubar = Menu(self.root)
        self.root.config(menu=menubar)

        # Create 'Account' menu
        account_menu = Menu(menubar, tearoff=0)
        account_menu.add_command(label="Order History")
        account_menu.add_command(label="Payment Methods")
        account_menu.add_separator()
        account_menu.add_command(label="Sign Out")

        # Add 'Account' to the menu bar
        menubar.add_cascade(label="Account", menu=account_menu)

    def load_category(self, event):
        # Clear the notebook when a new category is selected
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)

        # Get the selected category's items
        selected_category = self.category_var.get()
        self.items = self.menu_items[selected_category]

        # For simplicity, we'll show 4-5 items per tab
        self.populate_tabs(5)

    def populate_tabs(self, items_per_tab):
        # Dynamically create tabs and populate them with item cards
        num_tabs = (len(self.items) + items_per_tab - 1) // items_per_tab
        for i in range(num_tabs):
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=f"Page {i+1}")
            tab_frame.columnconfigure(0, weight=1)

            start = i * items_per_tab
            end = start + items_per_tab
            for j, item in enumerate(self.items[start:end]):
                self.create_item_card(tab_frame, item)
        self.update_order()

    def clear_focus(self, event):
        # Get the widget that was clicked
        widget = event.widget
        # Check if the clicked widget is not a combobox or spinbox
        if not isinstance(widget, (ttk.Combobox, tk.Spinbox)):
            # Clear focus by setting it to the root window
            self.root.focus()

    def create_item_card(self, parent, item):
        name = item["Name"]
        price = item["Price"]
        description = item["Description"]
        item_type = item['Type']
        frame = tk.Frame(parent, bg="white", bd=2, relief=tk.GROOVE)
        frame.pack(fill=tk.X, padx=10, pady=5)

        # Load the appropriate icon based on item type (veg or non-veg)
        if item_type == "Vegetarian":
            veg_icon = Image.open("veg.png")
            veg_icon = veg_icon.resize((20, 20), Image.LANCZOS)
            icon = ImageTk.PhotoImage(veg_icon)
        else:
            non_veg_icon = Image.open("nonveg.png")
            non_veg_icon = non_veg_icon.resize((20, 20), Image.LANCZOS)
            icon = ImageTk.PhotoImage(non_veg_icon)

        # Store the icon reference to prevent garbage collection
        frame.icon_image = icon

        # Configure the grid layout for proper alignment
        frame.grid_columnconfigure(0, weight=0)  # For left-aligned text (name, description)
        frame.grid_columnconfigure(1, weight=1)  # For spinbox group
        frame.grid_columnconfigure(2, weight=0)  # For price label

        # Item Name (aligned to the left) with the icon to its right
        item_name = tk.Label(frame, text=name, font=("Arial", 16, "bold"), bg="white")
        item_name.grid(row=0, column=0, sticky="w", padx=10, pady=(5,0))

        # Icon (placed to the right of the name)
        item_icon = tk.Label(frame, image=icon, bg="white")
        item_icon.grid(row=1, column=1, padx=10, sticky="w")

        # Description (aligned to the left, in light gray)
        item_description = tk.Label(frame, text=description, font=("Arial", 12), bg="white", fg="lightgray", justify='left')
        item_description.grid(row=1, column=0, sticky="w", padx=10, pady=(0,13))

        # Price label (aligned to the far right of the card)
        price_label = tk.Label(frame, text=f"₹{price}", bg="white", font=("Arial", 14), anchor='e')
        price_label.grid(row=0, column=2, rowspan=1, sticky="e", padx=10, pady=10)

        quantity_label = tk.Label(frame, text="Quantity:", bg="white")
        quantity_label.grid(row=1, column=0, columnspan=2, sticky="E", pady=10)

        qty = tk.IntVar(frame, 0)
        for element in self.qtyvars:
            if element['Name']==name:
                if element['Qty'] == 0:
                    element['QtyVar'] = qty
                    element['Price'] = price
                else:
                    qty = tk.IntVar(frame, element['Qty'])
                    element["QtyVar"] = qty
                    element['Price'] = price
        quantity_spinbox = tk.Spinbox(frame, from_=0, to=10, width=5, state='readonly', textvariable=qty)
        quantity_spinbox.grid(row=1, column=2, sticky="e", padx=10, pady=10)


    def create_checkout_button(self):
        # Create a frame for the button at the bottom of the window
        checkout_frame = tk.Frame(self.root, height=50)  # Reduced height
        checkout_frame.grid(row=3, column=0, sticky="ew")

        # Create a canvas with minimal padding
        canvas = tk.Canvas(checkout_frame, highlightthickness=0, width=150, height=50)  # Set canvas to button size
        canvas.pack(side="right", padx=(0, 20), pady=(0, 10))  # Reduced padding

        # Function to create rounded rectangle
        def create_rounded_rectangle(x1, y1, x2, y2, radius=25, **kwargs):
        
            points = [
                x1 + radius, y1,  
                x2 - radius, y1,]
            for i in range(181):
                basex,basey = x2-radius, y1+radius
                points.append(basex+radius*math.sin(math.pi*i/360))
                points.append(basey-radius*math.cos(math.pi*i/360))
            for i in range(181):
                basex,basey = x2-radius, y2-radius
                points.append(basex+radius*math.cos(math.pi*i/360))
                points.append(basey+radius*math.sin(math.pi*i/360))
            for i in range(181):
                basex,basey = x1+radius, y2-radius
                points.append(basex-radius*math.sin(math.pi*i/360))
                points.append(basey+radius*math.cos(math.pi*i/360))
            for i in range(181):
                basex,basey = x1+radius, y1+radius
                points.append(basex-radius*math.cos(math.pi*i/360))
                points.append(basey-radius*math.sin(math.pi*i/360))

            return canvas.create_polygon(points, **kwargs, smooth=True)


        # Define the rounded rectangle for the button background
        button_width = 150
        button_height = 50
        x1, y1, x2, y2 = 0, 0, button_width, button_height  # Start from (0, 0) to match canvas size
        button = create_rounded_rectangle(x1, y1, x2, y2, radius=10, fill="blue")

        # Add text on top of the button
        canvas.create_text((button_width // 2, button_height // 2), text="Checkout", fill="white", font=("Arial", 14, "bold"))

        # Configure the grid row to have minimal space
        self.root.grid_rowconfigure(3, weight=0)

        def checkout_button_click_animation():
            # Change the appearance on press
            def on_press(event):
                canvas.itemconfig(button, fill="darkblue")

            # Revert the button appearance
            def on_release(event):
                self.update_order()
                
                canvas.itemconfig(button, fill="blue")
                if len([a for a in self.qtyvars if a['QtyVar'].get()>0])==0:
                    messagebox.showerror('No Item Sected', 'Please select at least one item to proceed.')
                else:
                    self.on_checkout()

            # Bind the button click event
            canvas.bind("<ButtonPress-1>", on_press)
            canvas.bind("<ButtonRelease-1>", on_release)

        checkout_button_click_animation()



    def update_order(self):
        for a in self.qtyvars:
            a['Qty'] = a["QtyVar"].get()

    def on_checkout(self):
        checkout = CustomerCheckout(self.user)
        contents = [{a['Name']: a['Qty']} for a in self.qtyvars if a['QtyVar'].get() > 0]
        
        total = 0
        for a in self.qtyvars:
            if a['QtyVar'].get() > 0:
                total += float(a['Price']) * a['Qty']
        
        # Append order to CSV
        checkout.append_order_to_csv(contents, status="Pending", total=total)

        # Prepare order details for the popup
        order_details = "\n".join(f"{list(item.keys())[0]}: {list(item.values())[0]}x" for item in contents)
        messagebox.showinfo("Checkout Successful", f"Order Details:\n{order_details}\n\nTotal Price: ₹{total:.2f}")
        for qtyvar in self.qtyvars:
            qtyvar['QtyVar'].set(0)
            qtyvar['Qty'] = 0



if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantApp(root,'a')
    root.mainloop()
