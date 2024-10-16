import csv

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
                if cat in self.items.keys():
                    self.items[cat].append(item)
                else:
                    self.items[cat] = [item]
        
                