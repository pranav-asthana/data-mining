from sequence import AminoAcid
from preprocess import *
from collections import OrderedDict
import math
import random

class Cluster:
    members = list()

    def __init__(self, members=[]):
        self.members = members

    def add_point(self, p):
        self.members.append(p)

    def find_medioid(self):
        medioid = members[0]
        l = len(members)
        min_sse = math.inf
        for i in range(l):
            sse = 0
            for j in range(l):
                sse += similarity[i][j] ** 2
            if sse < min_sse:
                sse = min_sse
                medioid = members[i]
        return medioid

def get_clusters(list_medioid, points, similarity, index_dict):
    clusters = [Cluster() for i in range(len(list_medioid))]
    # For each point, find the medioid it is closest to

    # Add the medioids to each cluster
    for i in range(len(list_medioid)):
        clusters[i].members.append(list_medioid[i])

    # find distance

    return clusters

def main():
    num_cluster = sys.argv[1] if len(sys.argv) > 1 else 2
    fname = sys.argv[2] if len(sys.argv) > 2 else "AminoAcidSequences.fa"

    amino_acids = read_data(fname)
    similarity = get_similarity_matrix(fname, amino_acids, match=0, mismatch=1, indel=2)

    index_dict = {a.name: i for i, a in enumerate(amino_acids)}

    # initial list of medioids (index)
    #select num_cluster random points from list of amino_acids

    list_medioid_index = random.sample(range(len(amino_acids)), num_cluster)
    print("list_medioid_index")
    print(list_medioid_index)
    list_medioid = []

       for x in range(list_medioid_index):
           list_medioid.append(amino_acids[list_medioid_index[x]])


       get_clusters(list_medioid, amino_acids, similarity, index_dict)

       #form the first num_cluster clusters


if __name__ == '__main__':
    main()
