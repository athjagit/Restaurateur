import tkinter as tk
from tkinter import messagebox
import csv  # For reading user data from CSV
from Customer import RestaurantApp  # Ensure you have this app defined in your developing module


class PlaceholderEntry(tk.Entry):
    def __init__(self, parent, placeholder, color='grey', *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.put_placeholder()

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

    def put_placeholder(self):
        """Insert the placeholder if the entry is empty"""
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        """Remove the placeholder on focus if the entry has the placeholder text"""
        if self.get() == self.placeholder and self['fg'] == self.placeholder_color:
            self.delete(0, 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        """Restore the placeholder if the entry is empty"""
        if not self.get():
            self.put_placeholder()


class LoginWindow:
    def __init__(self, parent):
        self.top = tk.Toplevel(parent)
        self.parent = parent
        self.top.title("Login")
        self.top.geometry("400x400")
        self.top.config(bg="#F5F5F5")

        # Lose focus when clicking anywhere else in the window
        self.top.bind_all("<Button-1>", self.clear_focus, "+")

        # Make sure closing the login window closes the whole application
        self.top.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Welcome message with increased font
        welcome_label = tk.Label(self.top, text="Welcome back, you've been missed!", 
                                 font=("Arial", 14, "bold"), bg="#F5F5F5")  # Increased font
        welcome_label.pack(pady=20)

        # Username and Password fields (no labels, just placeholders)
        self.create_input_fields()

        # Login button
        self.create_login_button()

        # Forgot password option
        forgot_label = tk.Label(self.top, text="Forgot Password?", font=("Arial", 9), 
                                bg="#F5F5F5", fg="blue", cursor="hand2")
        forgot_label.pack(pady=(10, 5))  # Reduced padding between "Forgot Password" and Sign Up
        forgot_label.bind("<Button-1>", self.forgot_password)

        # Sign Up option
        signup_label = tk.Label(self.top, text="Not a member? Register now", font=("Arial", 10),
                                bg="#F5F5F5", fg="blue", cursor="hand2")
        signup_label.pack(side="bottom", pady=(5, 20))  # Reduced padding at the bottom
        signup_label.bind("<Button-1>", self.sign_up)

    def create_input_fields(self):
        # Frame for holding input fields
        input_frame = tk.Frame(self.top, bg="#F5F5F5")
        input_frame.pack(pady=20)

        # Username field with placeholder (no label)
        self.username_entry = PlaceholderEntry(input_frame, " Username", font=("Arial", 12), 
                                               relief="flat", bd=0, highlightthickness=1, highlightcolor="#CCCCCC")
        self.username_entry.grid(row=0, column=1, pady=5, ipady=8, ipadx=15, padx=10)  # Increased padding inside and outside the entry
        self.username_entry.config(highlightbackground="#CCCCCC", highlightcolor="#4CAF50")

        # Password field with placeholder (no label)
        self.password_entry = PlaceholderEntry(input_frame, "  Password", font=("Arial", 12), 
                                               relief="flat", bd=0, highlightthickness=1, highlightcolor="#CCCCCC")
        self.password_entry.grid(row=1, column=1, pady=5, ipady=8, ipadx=15, padx=10)  # Increased padding inside and outside the entry
        self.password_entry.config(highlightbackground="#CCCCCC", highlightcolor="#4CAF50")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()        
        # Check username and hashed password in the CSV file
        try:
            with open('users.csv', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] == username and row['password'] == password:
                        self.app = RestaurantApp(self.parent)
                        self.app.user = username
                        self.top.destroy()
                        messagebox.showinfo("Login Success", f"Welcome {username}!")
                        return
                messagebox.showerror("Login Failed", "Invalid username or password.")
        except FileNotFoundError:
            messagebox.showerror("File Not Found", "The users file was not found.")

    def create_login_button(self):
        # Frame for button
        button_frame = tk.Frame(self.top, bg="#F5F5F5")
        button_frame.pack(pady=20)
        button_frame.columnconfigure(0, weight=1)

        # Modern flat "Sign In" button
        signinlabel = tk.Label(button_frame, text='Sign in as: ' , font=("Arial", 12, "bold"), fg="#4CAF50", bd=0, relief="flat", activebackground="#45A049")
        signinlabel.grid(row=0, column=0, sticky='E')
        

        login_customer = tk.Button(button_frame, text="Customer", font=("Arial", 12, "bold"), 
                                 bg="#4CAF50", fg="white", bd=0, relief="flat", cursor="hand2", padx= 3,
                                 activebackground="#45A049", height=2, command=self.login)
        login_customer.grid(row = 0, column=1, sticky='W', padx= 3)

        login_restaurant = tk.Button(button_frame, text="Restaurant",  font=("Arial", 12, "bold"), 
                                 bg="#4CAF50", fg="white", bd=0, relief="flat", cursor="hand2", padx = 3,
                                 activebackground="#45A049", height=2, command=self.login)
        login_restaurant.grid(row = 0, column=2, sticky='w', padx=3)

    def forgot_password(self, event):
        # Display message for Forgot Password
        messagebox.showinfo("Forgot Password", "Forgot Password functionality will be implemented later.")

    def sign_up(self, event):
        # Display message for Sign-up
        messagebox.showinfo("Sign Up", "Sign-up functionality will be implemented later.")

    def clear_focus(self, event):
        widget = event.widget
        if not isinstance(widget, tk.Entry):
            self.top.focus_set()

    def on_closing(self):
        self.parent.destroy()


# Main Application Code
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window until login is successful
    LoginWindow(root)  # Open the login window
    root.mainloop()
