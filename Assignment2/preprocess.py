from acid import AminoAcid
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
            amino_acids.append(curr)
            curr = AminoAcid()
            curr.name = line[1:]
            continue
        curr.sequence += line[:-1]
    amino_acids.append(curr)
    amino_acids = amino_acids[1:]
    return amino_acids

def alignment_score(seq1, seq2, match=0, mismatch=-1, indel=-1):
    if seq1 == seq2:
        return len(seq1)*match
    m, n = len(seq1), len(seq2)
    dp = [[0 for i in range(n+1)] for x in range(2)]

    for i in trange(0, m+1):
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

def ldist(seq1, seq2):
    dp = [[0 for i in range(len(seq1)+1)] for x in range(2)]

    # Fill d[][] in bottom up manner
    for i in tqdm(range(len(seq2)+1)):
        for j in range(len(seq1)+1):
            # If first string is empty, only option is to
            # insert all characters of second string
            if i == 0:
                dp[i%2][j] = j    # Min. operations = j

            # If second string is empty, only option is to
            # remove all characters of second string
            elif j == 0:
                dp[i%2][j] = i    # Min. operations = i

            # If last characters are same, ignore last char
            # and recur for remaining string
            elif seq2[i-1] == seq1[j-1]:
                dp[i%2][j] = dp[(i-1)%2][j-1]

            # If last character are different, consider all
            # possibilities and find minimum
            else:
                dp[i%2][j] = 1 + min(dp[i%2][j-1],        # Insert
                                   dp[(i-1)%2][j],        # Remove
                                   dp[(i-1)%2][j-1])    # Replace
    return dp[len(seq2)%2][len(seq1)]


    # print(len(seq1), len(seq2))
    # if len(seq1) == 0: return len(seq2)
    # if len(seq2) == 0: return len(seq1)
    #
    # if seq1[-1] == seq2[-1]:
    #     return dist(seq1[:-1], seq2[:-1])
    # return 1 + min(dist(seq1[:-1], seq2), dist(seq1, seq2[:-1]), dist(seq1[:-1], seq2[:-1]))

def load_similarity_matrix(amino_acids):
    if 'similarity.pkl' in os.listdir('.'):
        f = open('similarity.pkl', 'rb')
        similarity = pkl.load(f)
        f.close()
    else:
        l = len(amino_acids)
        similarity = np.zeros((l, l))
    return similarity

def populate_similarity_matrix(amino_acids, match, mismatch, indel, rerun=False, start1=0, end1=-1, lock=None):
    # try:
    if 1:
        global similarity

        done = 0
        with tqdm(total=sum([len(amino_acids)-i for i in range(end1-start1)])) as pbar:
            for i in range(start1, len(amino_acids) if end1<0 else end1):
                for j in range(i, len(amino_acids)):
                    done += 1
                    pbar.set_description("Processing ({}, {})".format(i, j))
                    if not similarity[i][j] == 0:
                        pbar.update(1)
                        continue
                    score = alignment_score(amino_acids[i].sequence, amino_acids[j].sequence, match=match, mismatch=mismatch, indel=indel)
                    if lock:
                        lock.acquire()
                    similarity[i][j] = score
                    similarity[j][i] = score
                    f = open('similarity.pkl', 'wb')
                    pkl.dump(similarity, f)
                    f.close()
                    if lock:
                        lock.release()
                    pbar.update(1)


        if lock:
            lock.acquire()
        f = open('similarity.pkl', 'wb')
        pkl.dump(similarity, f)
        f.close()
        if lock:
            lock.release()
        return similarity
    # except Exception:
    #     import traceback
    #     print(traceback.format_exc())

def main():
    pass


amino_acids = read_data('AminoAcidSequences.fa')

start = int(sys.argv[1]) if len(sys.argv)>1 else 0
num_threads = int(sys.argv[2]) if len(sys.argv)>2 else 1
items_per_thread = int(sys.argv[3]) if len(sys.argv)>3 else len(amino_acids)//num_threads
# print(len(amino_acids[0].sequence), len(amino_acids[1].sequence))
# print(dist(amino_acids[0].sequence, amino_acids[1].sequence))
# print(alignment_score('CCATTGACAA', 'ACTGGAAT', match=0, mismatch=1, indel=2))

similarity = load_similarity_matrix(amino_acids)

# lock = _thread.allocate_lock()
# threads = []
# for i in range(num_threads):
#     threads.append(_thread.start_new_thread(populate_similarity_matrix, (amino_acids, 0, 1, 2, True, start+i*items_per_thread, start+(i+1)*items_per_thread, lock)))
#
# while 1:
#     pass


if __name__ == '__main__':
    main()
