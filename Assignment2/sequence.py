class AminoAcid:
    def __init__(self, name="UNK", sequence=""):
        self.name = name
        self.sequence = sequence
    def __str__(self):
        return self.sequence
