from sequence import AminoAcid
from preprocess import *
from collections import OrderedDict
import math


class Cluster:
    cluster_count = 0
    similarity = None
    instances = list()

    def __init__(self, members):
        self.cluster_id = Cluster.cluster_count
        Cluster.cluster_count += 1
        Cluster.instances.append(self)
        self.members = members

    def add_member(self, p):  # p can be a single point or a Cluster object
        self.members.append(p)

    def distance(self, c, similarity, index_dict, metric="MIN"):
        if metric == "MIN":
            res = math.inf
            fn = min
        elif metric == "MAX":
            res = -math.inf
            fn = max
        # print("COMPUTING DISTANCE BETWEEN")
        # print(self)
        # print(c)
        # print('-----------------')

        if len(self.members) == 1 and len(c.members) == 1:
            if isinstance(self.members[0], Cluster) or isinstance(c.members[0], Cluster):
                return self.members[0].distance(c.members[0], similarity, index_dict, metric)
            i, j = index_dict[self.members[0].name], index_dict[c.members[0].name]
            return similarity[min(i, j)][max(i, j)]

        elif len(self.members) == 1 or len(c.members) == 1:
            single = self if len(self.members)==1 else c
            multiple = self if len(c.members)==1 else c

            for m in multiple.members:
                if isinstance(single.members[0], Cluster):
                    d = single.members[0].distance(m, similarity, index_dict, metric)
                else:
                    d = single.distance(m, similarity, index_dict, metric)
                res = fn(res, d)
            return res

        for member1 in self.members:
            for member2 in c.members:
                d = member1.distance(member2, similarity, index_dict, metric)
                res = fn(res, d)
        return res

    def __str__(self):
        res = "-----\nCluster ID: "+ str(self.cluster_id) + '\n'
        for m in self.members:
            res += str(m) + '\n'
        return res+'-----\n'


def merge_clusters(clusters, similarity, index_dict, dist_metric="MIN"):
    min_distance = math.inf
    mini, minj = 0, 1
    l = len(Cluster.similarity)
    for i in range(l):
        for j in range(i+1, l):
            if Cluster.similarity[i][j] < min_distance:
                min_distance = Cluster.similarity[i][j]
                mini = i
                minj = j
    c1 = clusters[mini]
    c2 = clusters[minj]
    # print(mini, minj)
    print(min_distance)
    print(c1)
    print(c2)
    new_cluster = Cluster([c1, c2])
    Cluster.instances[mini] = Cluster.instances[-1]
    del Cluster.instances[minj]
    del Cluster.instances[len(Cluster.instances)-1]

    # Delete cluster j
    Cluster.similarity = np.delete(Cluster.similarity, (minj), axis=0)
    Cluster.similarity = np.delete(Cluster.similarity, (minj), axis=1)

    # Update similarity for cluster i
    new_row = [new_cluster.distance(c, similarity, index_dict) for c in Cluster.instances]
    Cluster.similarity[mini, :] = new_row

    return Cluster.instances



def main():
    pass

fname = 'AminoAcidSequences.fa'
fname = 'test.fa'

amino_acids = read_data(fname)
similarity = get_similarity_matrix(fname, amino_acids, match=0, mismatch=1, indel=2)
Cluster.similarity = similarity


name_dict = {a.name: a.sequence for a in amino_acids}
index_dict = {a.name: i for i, a in enumerate(amino_acids)}
reverse_index_dict = {i: a.name for i, a in enumerate(amino_acids)}

clusters = [Cluster([a]) for a in amino_acids]
# while len(clusters) > 1:
print("Number of clusters: ", len(clusters))
print(Cluster.similarity)
print()
while len(Cluster.similarity) > 1:
    clusters = merge_clusters(clusters, similarity, index_dict, dist_metric="MIN")
    print(Cluster.similarity)
    print()




if __name__ == '__main__':
    main()
