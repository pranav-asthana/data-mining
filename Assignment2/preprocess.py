from sequence import AminoAcid
from tqdm import tqdm
from tqdm import trange
from pprint import pprint
import numpy as np
import pickle as pkl
import os
import sys

import time
import _thread

data_dir = 'data'

def read_data(fname):
    f = open(os.path.join(data_dir, fname), 'r')
    amino_acids = []
    curr = AminoAcid()
    for line in f:
        line = line.replace('\n', '')
        if '>' in line:
            curr.sequence = curr.sequence[:-1]
            amino_acids.append(curr)
            curr = AminoAcid()
            curr.name = line[1:]
            continue
        curr.sequence += line
    curr.sequence = curr.sequence[:-1]
    amino_acids.append(curr)
    amino_acids = amino_acids[1:]
    return amino_acids


def alignment_score(seq1, seq2, match=0, mismatch=1, indel=1):
    if seq1 == seq2:
        return len(seq1)*match
    m, n = len(seq1), len(seq2)
    dp = [[0 for i in range(n+1)] for x in range(2)]

    for i in range(0, m+1):
        for j in range(0, n+1):
            if i == 0:
                dp[i][j] = j*indel
                continue
            elif j == 0:
                dp[i%2][j] = i*indel
                continue

            diagonal = dp[(i-1)%2][j-1] + (match if seq1[i-1] == seq2[j-1] else mismatch)
            left = dp[i%2][j-1] + indel
            up = dp[(i-1)%2][j] + indel
            dp[i%2][j] = min(diagonal, left, up)

    return dp[m%2][n]


def get_similarity_matrix(name, amino_acids, match, mismatch, indel):
    l = len(amino_acids)
    file_path = os.path.join(data_dir, name.split('.')[0]+'_similarity_{}_{}_{}.pkl'.format(match, mismatch, indel))
    if os.path.exists(file_path):
        f = open(file_path, 'rb')
        similarity = pkl.load(f)
        f.close()
    else:
        similarity = np.zeros((l, l))

    if not similarity[l-1][l-2] == 0: # Already done
        return similarity

    with tqdm(total=sum([l-i for i in range(l)])) as pbar:
        for i in range(l):
            for j in range(i, l):
                if not similarity[i][j] == 0:
                    pbar.set_description("Checking ({}, {})".format(i, j))
                    pbar.update(1)
                    continue
                pbar.set_description("Processing ({}, {})".format(i, j))
                score = alignment_score(amino_acids[i].sequence, amino_acids[j].sequence, match=match, mismatch=mismatch, indel=indel)
                similarity[i][j] = score
                similarity[j][i] = score

                f = open(file_path, 'wb')
                pkl.dump(similarity, f)
                f.close()
                pbar.update(1)


    f = open(file_path, 'wb')
    pkl.dump(similarity, f)
    f.close()

    return similarity


def main():
    amino_acids = read_data('AminoAcidSequences.fa')

    match = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    mismatch = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    indel = int(sys.argv[3]) if len(sys.argv) > 3 else 2

    similarity = get_similarity_matrix('AminoAcidSequences.fa', amino_acids, match, mismatch, indel)


if __name__ == '__main__':
    main()
