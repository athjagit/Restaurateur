import tkinter as tk
from tkinter import ttk, messagebox
import csv

# CSV file paths
MENU_FILE = "menu_items.csv"

class AdminMenuApp(tk.Toplevel):
    def __init__(self, root):
        super().__init__(master=root)
        self.title("Restaurant Menu Editor")
        self.geometry("950x550")
        root.withdraw()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # Configure resizing for all rows/columns
        for i in range(3):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(1, weight=1)


        # Create a Treeview widget to show the menu items, with multiple selection enabled
        self.tree = ttk.Treeview(self, columns=("Category", "Name", "Price", "Description", "Type"), 
                                 show="headings", selectmode='extended')
        self.tree.heading("Category", text="Category")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Price", text="Price")
        self.tree.heading("Description", text="Description")
        self.tree.heading("Type", text="Type")

        # Adjust column width
        self.tree.column("Category", width=120, anchor="center")
        self.tree.column("Name", width=150)
        self.tree.column("Price", width=80, anchor="center")
        self.tree.column("Description", width=150)
        self.tree.column("Type", width=100, anchor="center")

        self.tree.grid(row=1, column=0, columnspan=3, sticky="nsew")

        # Buttons for operations with styling
        self.add_btn = tk.Button(self, text="Add Item", command=self.add_item, padx=10, pady=5, bg="lightblue", font=("Arial", 10, "bold"))
        self.edit_btn = tk.Button(self, text="Edit Item", command=self.edit_item, padx=10, pady=5, bg="lightgreen", font=("Arial", 10, "bold"))
        self.delete_btn = tk.Button(self, text="Delete Item", command=self.delete_item, padx=10, pady=5, bg="salmon", font=("Arial", 10, "bold"))

        self.done_btn = tk.Button(self, text="Done", command=self.on_closing, padx=10, pady=5,bg = '#4CAF50', font=("Arial", 10, "bold"))
        self.done_btn.grid(row = 0, sticky='e', columnspan=3)

        self.add_btn.grid(row=2, column=0, sticky="ew")
        self.edit_btn.grid(row=2, column=1, sticky="ew")
        self.delete_btn.grid(row=2, column=2, sticky="ew")

        # Undo Button
        self.undo_btn = tk.Button(self, text="Undo", command=self.undo, padx=10, pady=5, bg="yellow", font=("Arial", 10, "bold"))
        self.undo_btn.grid(row=3, column=0, columnspan=3, sticky="ew")
        root.bind("<Control-z>", lambda event: self.undo())  # Bind Ctrl+Z for undo

        # Initialize action history for undo feature
        self.action_history = []
        self.update_undo_button()

        # Tag configuration for color coding
        self.tree.tag_configure("veg", background="#98FB98")  # Light green
        self.tree.tag_configure("non_veg", background="#FFB6C1")  # Light red

        # Bind selection change event to disable Edit button for multiple selections
        self.tree.bind("<<TreeviewSelect>>", self.on_selection_change)

        # Load the menu
        self.load_menu()

    def load_menu(self):
        """Load the menu from the CSV file into the Treeview."""
        self.tree.delete(*self.tree.get_children())  # Clear current contents
        self.categories = []
        try:
            with open(MENU_FILE, newline='') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                last_category = None
                last_row = None
                for row in reader:
                    # Skip empty lines
                    if not row or len(row) < 5:
                        continue
                    
                    category, name, price, description, food_type = row
                    if len(category) > 0 and category not in self.categories:
                        self.categories.append(category)
                    # Insert separator if category changes
                    if category != last_category and last_row is not None and last_row[1] != "------":
                        if last_category is not None:  # Insert a separator for the previous category
                            self.tree.insert("", "end", values=("", "------", "", "", ""), tags=("separator",))
                        last_category = category
                                      
                    # Insert the data into Treeview
                    item_id = self.tree.insert("", "end", values=row)

                    # Apply color to "Vegetarian" and "Non-Vegetarian" cells
                    if food_type == "Vegetarian":
                        self.tree.item(item_id, tags=("veg",))
                    elif food_type == "Non-Vegetarian":
                        self.tree.item(item_id, tags=("non_veg",))
                    
                    last_row = row
                    
        except FileNotFoundError:
            if messagebox.askyesno("Error", f"{MENU_FILE} not found!\nMake new menu file?"):
                with open('menu_items.csv', mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Category", "Name", "Price", "Description", "Type"])

    def save_menu(self, rows):
        """Save the current rows back to the CSV file in the correct format."""
        with open(MENU_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Category", "Name", "Price", "Description", "Type"])  # Write the header
            for row in rows:
                if row[1] != "------":  # Write only non-empty rows
                    writer.writerow(row)
        self.load_menu()

    def add_item(self):
        """Open a dialog to add a new menu item."""
        self.edit_dialog()

    def edit_item(self):
        """Edit the selected menu item."""
        selected_item = self.tree.selection()
        if len(selected_item) > 1:
            return  # Prevent editing when multiple items are selected

        if not selected_item:
            messagebox.showwarning("Select item", "Please select an item to edit.")
            return

        # Check if the selected item is a separator
        item_values = self.tree.item(selected_item, 'values')
        if item_values[1] == "------":
            messagebox.showwarning("Edit Item", "Cannot edit a separator.")
            return
        
        self.edit_dialog(item_values, selected_item)

    def delete_item(self):
        """Delete the selected item(s) from the menu."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Select item", "Please select an item to delete.")
            return

        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected item(s)?")
        if confirm:
            # Store deleted items and their indices for undo
            deleted_items = []
            deleted_item_indices = []
            for item in selected_items:
                deleted_item_indices.append(self.tree.index(item))
            for item in selected_items:
                item_values = self.tree.item(item, 'values')
                item_index = self.tree.index(item)
                item_tags = self.tree.item(item, 'tags')
                deleted_items.append({"values": item_values, "index": item_index, "tags": item_tags})
                self.tree.delete(item)
            
            for i in range(len(deleted_item_indices)):
                deleted_items[i]['index'] = deleted_item_indices[i]

            # Update action history for delete
            self.action_history.append({
                "action": "delete",
                "items": deleted_items
            })
            self.save_menu([self.tree.item(item, 'values') for item in self.tree.get_children()])
            self.update_undo_button()

    def undo(self):
        """Undo the last action."""
        if not self.action_history:
            messagebox.showinfo("Undo", "No actions to undo.")
            return

        last_action = self.action_history.pop()
        if last_action["action"] == "add":
            self.tree.delete(self.tree.get_children()[-1 if last_action['index'] == 'end' else last_action['index']])  # Remove last item
        elif last_action["action"] == "edit":
            # Restore previous values for edit
            self.tree.delete(self.tree.get_children()[last_action['index']])
            item_id = self.tree.insert("", last_action['index'], values=last_action["item"])
            self.tree.item(item_id, values=last_action["item"])  # Restore old item values
        elif last_action["action"] == "delete":
            last_action["items"].sort(key=lambda element: element['index'])
            for deleted in last_action["items"]:
                self.tree.insert("", deleted["index"], values=deleted["values"], tags=deleted["tags"])

        self.save_menu([self.tree.item(item, 'values') for item in self.tree.get_children()])
        self.update_undo_button()

    def update_undo_button(self):
        """Enable or disable the undo button based on action history."""
        self.undo_btn.config(state="normal" if len(self.action_history)>0 else "disabled")

    def on_selection_change(self, event):
        """Disable Edit button if multiple items are selected."""
        selected_items = self.tree.selection()
        self.edit_btn.config(state="normal" if len(selected_items) == 1 else "disabled")

    def edit_dialog(self, item_values=None, item_id=None):
        """Open a dialog to edit/add menu items."""
        self.dialog = tk.Toplevel(self)
        self.dialog.title("Edit Item" if item_values else "Add Item")
        self.dialog.geometry("280x270")

        tk.Label(self.dialog, text="Category:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.category_combobox = ttk.Combobox(self.dialog, values=self.categories, state="readonly" if item_values else "normal")
        self.category_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.category_combobox.set(item_values[0] if item_values else "")

        tk.Label(self.dialog, text="Name:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.name_entry = tk.Entry(self.dialog)
        self.name_entry.grid(row=1, column=1, padx=10, pady=10)
        self.name_entry.insert(0, item_values[1] if item_values else "")

        tk.Label(self.dialog, text="Price:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.price_entry = tk.Entry(self.dialog)
        self.price_entry.grid(row=2, column=1, padx=10, pady=10)
        self.price_entry.insert(0, item_values[2] if item_values else "")

        tk.Label(self.dialog, text="Description:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.description_entry = tk.Entry(self.dialog)
        self.description_entry.grid(row=3, column=1, padx=10, pady=10)
        self.description_entry.insert(0, item_values[3] if item_values else "")

        tk.Label(self.dialog, text="Type:").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        self.type_combobox = ttk.Combobox(self.dialog, values=["Vegetarian", "Non-Vegetarian"], state="readonly")
        self.type_combobox.grid(row=4, column=1, padx=10, pady=10)
        self.type_combobox.set(item_values[4] if item_values else "")

        # Add Save button
        self.save_button = tk.Button(self.dialog, text="Save", command=lambda: self.save_item(item_values, item_id), padx=10, pady=5)
        self.save_button.grid(row=5, column=0, columnspan=2, pady=20)

    def save_item(self, item_values, item_id):
        """Save the new or edited menu item."""
        category = self.category_combobox.get()
        name = self.name_entry.get()
        price = self.price_entry.get()
        description = self.description_entry.get()
        food_type = self.type_combobox.get()

        if not category or not name or not price or not description or not food_type:
            messagebox.showwarning("Input Error", "All fields must be filled in.")
            return

        if item_id:  # If editing an existing item
            print('editing')
            index = self.tree.index(item_id)
            self.tree.item(item_id, values=(category, name, price, description, food_type))
            self.action_history.append({
            "action": "edit",
            "item": item_values,
            "index": index
            })
        else:  # Adding new item
            # Get the last item index in the same category
            last_item_index = self.get_last_index(category)
            self.tree.insert("", last_item_index, values=(category, name, price, description, food_type))
            self.action_history.append({
            "action": "add",
            "item": (category, name, price, description, food_type),
            "index": last_item_index
            })
        self.save_menu([self.tree.item(item, 'values') for item in self.tree.get_children()])
        self.dialog.destroy()
        self.update_undo_button()
        messagebox.showinfo("Success", "Item saved successfully.")
        # Close the dialog window
        self.category_combobox.master.destroy()

    def get_last_index(self, cat):
        index = 'end'
        lastcatwassame = False
        items = [self.tree.item(item, 'values') for item in self.tree.get_children()]
        for i in range(len(items)) :
            if lastcatwassame and not items[i][0] == cat:
                return i
            if items[i][0] == cat:
                lastcatwassame = True
        return index

            
    
    def on_closing(self):
        self.destroy()  # Close AdminMenuApp

if __name__ == "__main__":
    root = tk.Tk()
    app = AdminMenuApp(root)
    root.withdraw()
    root.mainloop()
