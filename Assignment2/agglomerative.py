from sequence import AminoAcid
from preprocess import *
from collections import OrderedDict
import math


class Cluster:
    cluster_count = 0
    similarity = None
    instances = list()
    linkage_matrix = list()

    def __init__(self, members):
        self.cluster_id = Cluster.cluster_count
        Cluster.cluster_count += 1
        Cluster.instances.append(self)
        self.num_total_members = sum([m.num_total_members if isinstance(m, Cluster) else 1 for m in members])
        self.members = members

    def distance(self, c, similarity, index_dict, metric="MIN"):
        if metric == "MIN":
            res = math.inf
            fn = min
        elif metric == "MAX":
            res = -math.inf
            fn = max
        elif metric == "AVG":
            res = 0
            fn = sum

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
                res = fn([res, d])
            if metric == "AVG":
                return res/(len(multiple.members)+1)
            return res

        for member1 in self.members:
            for member2 in c.members:
                d = member1.distance(member2, similarity, index_dict, metric)
                res = fn([res, d])
        if metric == "AVG":
            return res/(len(self.members)*len(c.members))
        return res

    def __str__(self):
        res = "-----\nCluster ID: "+ str(self.cluster_id) + '\n'
        for m in self.members:
            res += str(m) + '\n'
        return res+'-----\n'

    def get_set(self):
        if len(self.members) == 1:
            return {self.members[0].sequence}
        return set([m.get_set() for m in self.numbers])


def merge_clusters(similarity, index_dict, dist_metric="MIN"):
    min_distance = math.inf
    mini, minj = 0, 1
    l = len(Cluster.similarity)
    for i in range(l):
        for j in range(i+1, l):
            if Cluster.similarity[i][j] < min_distance:
                min_distance = Cluster.similarity[i][j]
                mini = i
                minj = j
    c1 = Cluster.instances[mini]
    c2 = Cluster.instances[minj]
    new_cluster = Cluster([c1, c2])

    Cluster.linkage_matrix.append([c1.cluster_id, c2.cluster_id, min_distance, new_cluster.num_total_members])

    Cluster.instances[mini] = Cluster.instances[-1]  # Replace at index i with the new cluster instances
    del Cluster.instances[minj]  # Delete instance at index j
    del Cluster.instances[len(Cluster.instances)-1]  # Delete new instance at last index (since i was replaced with the new instance)

    # Delete cluster j
    Cluster.similarity = np.delete(Cluster.similarity, (minj), axis=0)
    Cluster.similarity = np.delete(Cluster.similarity, (minj), axis=1)

    # Update similarity for cluster i
    new_row = [new_cluster.distance(c, similarity, index_dict, dist_metric) if not c==new_cluster else 0 for c in Cluster.instances]
    Cluster.similarity[mini, :] = new_row
    Cluster.similarity[:, mini] = new_row

    return Cluster.instances

def draw_dendrogram(dist_metric, fname, reverse_index_dict):
    from scipy.cluster import hierarchy
    import matplotlib.pyplot as plt

    print("Generating and saving dendrogram")
    plt.figure(figsize=(40, 25))
    labels = list(zip(*sorted(reverse_index_dict.items(), key=lambda x: x[0])))[1]
    dendro = hierarchy.dendrogram(Cluster.linkage_matrix, labels=labels)
    # plt.show()
    plt.savefig("Results/agg_{}_{}.svg".format(fname.split('.')[0], dist_metric), dpi=400)



def main():
    distance_metric = sys.argv[1] if len(sys.argv) > 1 else "MIN"
    fname = sys.argv[2] if len(sys.argv) > 2 else "AminoAcidSequences.fa"

    amino_acids = read_data(fname)
    similarity = get_similarity_matrix(fname, amino_acids, match=0, mismatch=1, indel=2)
    Cluster.similarity = similarity

    index_dict = {a.name: i for i, a in enumerate(amino_acids)}
    reverse_index_dict = {i: a.name for i, a in enumerate(amino_acids)}

    _ = [Cluster([a]) for a in amino_acids]
    print("Merging {} initial clusters".format(len(amino_acids)))
    pbar = tqdm(total=len(amino_acids)-1)
    while len(Cluster.instances) > 1:
        merge_clusters(similarity, index_dict, dist_metric=distance_metric)
        pbar.update(1)
    print("Clustering complete")
    # clusters = Cluster.instances[0].get_set()
    # print(clusters)

    draw_dendrogram(distance_metric, fname, reverse_index_dict)



if __name__ == '__main__':
    main()
