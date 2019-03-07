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

    def find_medioid(self, similarity):
        # set medioid to first member by default
        medioid = self.members[0]
        l = len(self.members)
        min_sse = math.inf
        # change medioid to point with lowest total squ distance from hte rest of the points
        for i in range(l):
            sse = 0
            for j in range(l):
                sse += similarity[i][j] ** 2
            if sse < min_sse:
                sse = min_sse
                medioid = self.members[i]
        return medioid

def get_clusters(list_medioid, points, similarity, index_dict):
    # initialize empty clusters
    clusters = [Cluster() for m in list_medioid]


    # Add the medioids to each cluster
    for i in range(len(list_medioid)):
        clusters[i].members =[]
        clusters[i].members.append(list_medioid[i])
        
    # For each point, find the medioid it is closest to and add to that cluster
    for x in range(len(points)):
        min_dist = math.inf
        index_closest = -1
        for i in range(len(list_medioid)):
            if similarity[x][index_dict[list_medioid[i].name]] < min_dist: 
                min_dist = similarity[x][index_dict[list_medioid[i].name]]
                index_closest = i
        
        clusters[index_closest].add_point(points[x])        

    # To avoid repetions in the list
    for c in clusters:
        c.members = list(set(c.members))

    return clusters

def main():
    num_cluster = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    fname = sys.argv[2] if len(sys.argv) > 2 else "AminoAcidSequences.fa"

    amino_acids = read_data(fname)
    similarity = get_similarity_matrix(fname, amino_acids, match=0, mismatch=1, indel=2)

    # print(similarity)
    # dictionary mapping name to index in amino_acid list
    index_dict = {a.name: i for i, a in enumerate(amino_acids)}


    #select num_cluster random points from list of amino_acids
    list_medioid_index = random.sample(range(len(amino_acids)), num_cluster)
    
    list_medioid = []   # list of amino_acid objects
    for x in range(len(list_medioid_index)):
        list_medioid.append(amino_acids[list_medioid_index[x]])

    iter_num = 0
    # Stop after 100 iters or when prev medioids are same as newly calculated medioids
    while 1:
        iter_num += 1
        new_list_medioid = []
        # get lcusters based on medioid list
        clusters = get_clusters(list_medioid, amino_acids, similarity, index_dict)

        # find medioid for each cluster
        for i in range(len(clusters)):
            new_list_medioid.append(clusters[i].find_medioid(similarity))

        # if medioids don't change stop process
        if set(new_list_medioid) == set(list_medioid) or iter_num == 100:
            print("Reached end in {} iterations".format(iter_num))
            print("Final clusters")
            for i in range(len(list_medioid)):
                print("{} : {}".format(i , list(map(lambda x: x.sequence, clusters[i].members))))

            return clusters

        # else update medioid list 
        else:
            list_medioid = new_list_medioid

if __name__ == '__main__':
    main()
