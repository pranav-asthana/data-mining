import numpy as np

class Transaction:
    def __init__(self, transaction_id, attributes, label):
        self.id = transaction_id
        self.attributes = np.array(attributes)
        self.label = label

    def __str__(self):
        return "ID:{}\nAttributes({}):{}\nLabel:{}\n".format(self.id, len(self.attributes), self.attributes, self.label)
