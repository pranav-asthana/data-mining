from transaction import Transaction
import os
import sys
from tqdm import tqdm
import pickle as pkl
import subprocess


def read_data(data_dir, fname):
    if fname+'.pkl' in os.listdir(data_dir):
        f = open(os.path.join(data_dir, fname+'.pkl'), 'rb')
        transactions = pkl.load(f)
        f.close()
        return transactions

    fpath = os.path.join(os.path.abspath(sys.path[0]), data_dir, fname)
    f = open(fpath, 'r')

    transactions = []
    num_lines = int(subprocess.check_output(['wc', fpath]).split()[0])
    pbar = tqdm(total=num_lines)
    for line in f:
        line = line.split()
        transactions.append(Transaction(len(transactions)+1, line[:-1], line[-1]))
        pbar.update(1)

    f = open(os.path.join(data_dir, fname+'.pkl'), 'wb')
    pkl.dump(transactions, f)
    f.close()
    return transactions


def main():
    data_dir = "data/"
    t = read_data(data_dir, 'german.data-numeric')
    for i in range(5):
        print(t[i])

if __name__ == '__main__':
    main()
