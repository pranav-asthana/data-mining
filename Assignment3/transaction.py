import numpy as np

class Transaction:
    def __init__(self, transaction_id, attr, label):
        self.id = transaction_id
        self.attr = np.array(attr)
        self.label = label

    def __str__(self):
        return "ID:{}\nAttributes({}):{}\nLabel:{}\n".format(self.id, len(self.attr), self.attr, self.label)
