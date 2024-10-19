import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from Restaurant import AdminMenuApp
from CurrentOrders import OrderManagementApp
from OrderHistory import OrderHistoryApp

class AdminDashboard(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.title("Admin Dashboard")
        self.master.withdraw()
        self.protocol("WM_DELETE_WINDOW", lambda : self.master.destroy())

        # Load and display restaurant photo
        try:
            self.img = Image.open('rest_pic.png')
            self.w,self.h = self.img.size
            self.img = self.img.resize((int(200*self.w/self.h), 200))  # Correctly load saved image
        except FileNotFoundError:
            self.img = Image.new('RGB', (200, 200), color='grey')  # Placeholder if no image found
        self.img_tk = ImageTk.PhotoImage(self.img)

        # Display the photo in a label
        self.photo_label = tk.Label(self, image=self.img_tk, cursor="hand2")
        self.photo_label.pack(pady=10)
        self.photo_label.bind("<Button-1>", self.open_image)  # Click to change image

        # Frame for buttons
        button_frame = tk.Frame(self, pady=10)
        button_frame.pack()

        # Load the PNGs for buttons
        edit_menu_img = Image.open("icon_edit.png").resize((100, 100), Image.LANCZOS)  # Resized smaller
        manage_orders_img = Image.open("icon_orders.png").resize((100, 100), Image.LANCZOS)  # Resized smaller
        billing_history_img = Image.open("icon_hist.png").resize((100, 100), Image.LANCZOS)  # Resized smaller

        self.edit_menu_tk = ImageTk.PhotoImage(edit_menu_img)
        self.manage_orders_tk = ImageTk.PhotoImage(manage_orders_img)
        self.billing_history_tk = ImageTk.PhotoImage(billing_history_img)

        # Create buttons using the provided PNGs as the entire button
        edit_menu_btn = tk.Button(button_frame, image=self.edit_menu_tk, command=self.open_admin_menu_app, bd=0)
        edit_menu_btn.grid(row=0, column=0, padx=10, pady=10)

        manage_orders_btn = tk.Button(button_frame, image=self.manage_orders_tk, command=self.manage_orders, bd=0)
        manage_orders_btn.grid(row=0, column=1, padx=10, pady=10)

        billing_history_btn = tk.Button(button_frame, image=self.billing_history_tk, command=self.billing_history, bd=0)
        billing_history_btn.grid(row=1, column=0, columnspan=2, padx=10, pady=10)  # Span across both columns

        # Fixed window size and non-resizable
        self.geometry("400x500")  # Set fixed geometry
        self.resizable(False, False)  # Non-resizable

    def open_image(self, event=None):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg")])
        if file_path:
            img = Image.open(file_path).resize((int(200*self.w/self.h), 200), Image.LANCZOS)
            img.save('rest_pic.png')  # Save as rest_pic.png
            img_tk = ImageTk.PhotoImage(img)
            self.photo_label.config(image=img_tk)
            self.photo_label.image = img_tk

    def open_admin_menu_app(self):
        # Open AdminMenuApp using the original root passed from login.py
        AdminMenuApp(self.master)
        # self.master.deiconify()
        self.master.withdraw()
          # Pass root to AdminMenuApp
    

    def manage_orders(self):
        OrderManagementApp(self.master)
        # self.master.deiconify()
        self.master.withdraw()

    def billing_history(self):
        OrderHistoryApp(self.master)
        # self.master.deiconify()
        self.master.withdraw()

# Example of running AdminDashboard directly from RestLogin.py (for testing)
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    dashboard = AdminDashboard(root)  # Open AdminDashboard directly for testing
    root.mainloop()