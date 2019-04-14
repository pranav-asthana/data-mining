from transaction import Transaction
import os
import sys
from tqdm import tqdm
from tqdm import trange
import pickle as pkl
import numpy as np
import subprocess


def read_data(data_dir, fname):
    if fname+'.pkl' in os.listdir(data_dir):
        f = open(os.path.join(data_dir, fname+'.pkl'), 'rb')
        transactions = pkl.load(f)
        f.close()
        return transactions

    print("Reading data...")
    fpath = os.path.join(os.path.abspath(sys.path[0]), data_dir, fname)
    f = open(fpath, 'r')

    transactions = []
    num_lines = int(subprocess.check_output(['wc', fpath]).split()[0])
    pbar = tqdm(total=num_lines)
    for line in f:
        line = line.split()
        transactions.append(Transaction(len(transactions)+1, [int(attr) for attr in line[:-1]], int(line[-1])))
        pbar.update(1)

    f = open(os.path.join(data_dir, fname+'.pkl'), 'wb')
    pkl.dump(transactions, f)
    f.close()
    return transactions


def distance(a, b):  # Cosine distance
    return np.linalg.norm(a-b)

def get_distance_matrix(transactions, data_dir='data/', fname='distance_matrix.pkl'):
    if fname in os.listdir(data_dir):
        f = open(os.path.join(data_dir, fname), 'rb')
        distance_matrix = pkl.load(f)
        f.close()
        return distance_matrix

    print("Computing distance matrix...")
    l = len(transactions)
    distance_matrix = np.zeros((l, l))

    for i in trange(l):
        for j in range(l):
            d = distance(transactions[i].attr, transactions[j].attr)
            distance_matrix[i][j] = d
            distance_matrix[j][i] = d

    f = open(os.path.join(data_dir, fname), 'wb')
    pkl.dump(distance_matrix, f)
    f.close()
    return distance_matrix

def main():
    data_dir = "data/"
    t = read_data(data_dir, 'german.data-numeric')

    for i in range(5):
        print(t[i])

    dist = get_distance_matrix(t, data_dir, 'creditcard_dist.pkl')
    print(dist.shape)
    # print(dist)

if __name__ == '__main__':
    main()
