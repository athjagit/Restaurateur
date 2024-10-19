import csv
from datetime import datetime
import ast  # To safely evaluate string representations of dictionaries



class CustomerSide:
    def __init__(self, path):
        self.path = path
        self.items = {}
        self.items_linear = []
        with open(path, 'r') as file:
            reader = csv.DictReader(file)
            for item in reader:
                self.items_linear.append(item)
                cat = item['Category']
                del item['Category']
                if len(cat)>0:
                    if cat in self.items.keys():
                        self.items[cat].append(item)
                    else:
                        self.items[cat] = [item]

class CustomerCheckout:
    def __init__(self, username):
        self.username = username
        self.today_date = datetime.now().strftime("%d%m%y")
    
    def generate_customer_id(self, order_number):
        """Generates customer ID using ddmmyy{username}{ordernumber}."""
        return f"{self.today_date}{self.username}{order_number}"

    def get_next_order_number(self):
        """Checks {username}_orders.csv for today's orders and returns the next order number."""
        file_name = f"{self.username}_orders.csv"
        order_number = 1
        try:
            with open(file_name, mode='r') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['CustomerID'].startswith(self.today_date):
                        # Extract the order number
                        order_number = int(row['CustomerID'][-1]) + 1
        except FileNotFoundError:
            # If file doesn't exist, this is the first order
            order_number = 1
        return order_number
    
    def append_order_to_csv(self, contents, total, status):
        """Appends the order details to {username}_orders.csv and orders.csv."""
        order_number = self.get_next_order_number()
        customer_id = self.username
        order_id = f"{self.today_date}{self.username}{order_number}"  # Create a unique Order ID, prefixing with "ORD"
        contents_str = str(contents)  # Convert dictionary to string for CSV
        
        # Prepare the order data
        order_data = {
            'OrderID': order_id,
            'CustomerID': customer_id,
            'Contents': contents_str,
            'Total': total,
            'Status': status
        }

        # Append to {username}_orders.csv
        user_file = f"{self.username}_orders.csv"
        with open(user_file, mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=order_data.keys())
            if file.tell() == 0:  # If file is empty, write headers
                writer.writeheader()
            writer.writerow(order_data)

        # Append to orders.csv (global order list)
        with open('orders.csv', mode='a', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=order_data.keys())
            if file.tell() == 0:  # If file is empty, write headers
                writer.writeheader()
            writer.writerow(order_data)
    
def parse_contents(contents_str):
    """Converts the contents string (from CSV) back into a dictionary."""
    try:
        # Safely convert the string back into a dictionary
        contents_dict = eval(contents_str)
        if isinstance(contents_dict, dict):
            return contents_dict
        else:
            raise ValueError("Parsed contents are not a dictionary")
    except (SyntaxError, ValueError) as e:
        print(f"Error parsing contents: {e}")
        return {}

def read_orders_csv():
    """Reads orders from the orders.csv file and returns a list of dictionaries."""
    orders = []
    try:
        with open('orders.csv', mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Convert the Contents string to a dictionary
                row['Contents'] = ast.literal_eval(row['Contents'])
                orders.append(row)
    except Exception as e:
        print(f"Error reading orders.csv: {e}")
    return orders



        
                