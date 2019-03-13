from sequence import AminoAcid
from preprocess import *
from collections import OrderedDict
import math
import copy

class Cluster:
    cluster_count = 0
    instances = list()
    linkage_matrix = list()
    dendrogram_index_map = dict()
    hierarchy = dict()

    def __init__(self, members=[]):
        self.id = Cluster.cluster_count
        Cluster.cluster_count += 1
        Cluster.instances.append(self)
        self.members = members

    def diameter(self, similarity, index_dict):
        dia = -1
        for p1 in self.members:
            for p2 in self.members:
                dia = max(similarity[index_dict[p1.name]][index_dict[p2.name]], dia)
        return dia

    def get_total_members(self):
        return sum([m.get_total_members() if isinstance(m, Cluster) else 1 for m in self.members])

    def add_point(self, p):
        self.members.append(p)

    def delete_point(self, p):
        self.members.remove(p)

    def __str__(self):
        res = "Cluster ID: " + str(self.id) + "\n" + ",".join([m.name for m in self.members])
        return res


    def get_set(self):
        if len(self.members) == 1:
            return {self.members[0].sequence}
        return set([m.get_set() for m in self.numbers])

def splinter(similarity, index_dict):
    cluster_diameters = {c:c.diameter(similarity, index_dict) for c in Cluster.instances}
    max_diameter_cluster = max(cluster_diameters.items(), key=lambda x: x[1])
    if max_diameter_cluster[1] == 0:
        return None, None
    splitting_cluster = max_diameter_cluster[0]
    sse = lambda point: sum(list(map(lambda x: x**1, similarity[index_dict[point.name], :])))
    splinter_point = max([(point, sse(point)) for point in splitting_cluster.members], key = lambda x: x[1])[0]
    # print({c.id:v for c, v in cluster_diameters.items()})
    return splitting_cluster, splinter_point

def split_clusters(similarity, index_dict, amino_acids):
    '''
    1. Find cluster with max diameter
    2. Find splinter element: Element farthest away from max diameter cluster
    3. Reassign points between the cluster being divided and the new splinter cluster
    4. Repeat 1,2,3 until all clusters have a single element
    '''
    original_cluster, splinter_point = splinter(similarity, index_dict)
    if not original_cluster:
        return
    # print("ORIGINAL")
    # print(original_cluster)
    # print("Diameter:", original_cluster.diameter(similarity, index_dict))
    new_cluster = Cluster([])
    num_total_members = original_cluster.get_total_members()

    Cluster.dendrogram_index_map[original_cluster.id] = 2*similarity.shape[0]-len(Cluster.instances)

    # print([m.sequence for m in original_cluster.members])
    # print(splinter_point)
    # print()
    cluster_dists = {}
    for pt in original_cluster.members:
        cluster_dists[pt] = 0
        for p2 in original_cluster.members:
            cluster_dists[pt] += similarity[index_dict[pt.name]][index_dict[p2.name]]
        cluster_dists[pt] /= len(original_cluster.members)
    splinter_dist = {pt: similarity[index_dict[pt.name]][index_dict[splinter_point.name]] for pt in original_cluster.members}
    diff = {pt: cluster_dists[pt]-splinter_dist[pt] for pt in original_cluster.members}

    # print({str(p):v for p, v in cluster_dists.items()})
    # print({str(p):v for p, v in splinter_dist.items()})
    # print({str(p):v for p, v in diff.items()})

    for pt in diff:
        if diff[pt] > 0:
            original_cluster.delete_point(pt)
            new_cluster.add_point(pt)

    new_cluster2 = Cluster(original_cluster.members)
    original_cluster.members = []
    for i in range(len(Cluster.instances)):
        if len(Cluster.instances[i].members)==0:
            del Cluster.instances[i]
            break
    # print("NEW CLUSTERS")
    # print(new_cluster)
    # print("Diameter:", new_cluster.diameter(similarity, index_dict))
    # print(new_cluster2)
    # print("Diameter:", new_cluster2.diameter(similarity, index_dict))


    dist = 0
    count = 0
    for p1 in new_cluster.members:
        for p2 in new_cluster2.members:
            count += 1
            dist += similarity[index_dict[p1.name]][index_dict[p2.name]]
    dist /= count
    if len(new_cluster.members) == 1:
        Cluster.dendrogram_index_map[new_cluster.id] = amino_acids.index(new_cluster.members[0])
    if len(new_cluster2.members) == 1:
        Cluster.dendrogram_index_map[new_cluster2.id] = amino_acids.index(new_cluster2.members[0])

    Cluster.linkage_matrix.insert(0, [new_cluster2.id, new_cluster.id, dist, num_total_members])
    Cluster.hierarchy[len(Cluster.instances)] = copy.deepcopy(Cluster.instances)

def draw_dendrogram(fname, reverse_index_dict):
    from scipy.cluster import hierarchy
    import matplotlib.pyplot as plt

    for i in range(len(Cluster.linkage_matrix)):
        temp1 = Cluster.dendrogram_index_map[Cluster.linkage_matrix[i][0]]
        temp2 = Cluster.dendrogram_index_map[Cluster.linkage_matrix[i][1]]
        Cluster.linkage_matrix[i][0] = max(temp1, temp2)
        Cluster.linkage_matrix[i][1] = min(temp1, temp2)

    print("Generating and saving dendrogram")
    for i in range(len(Cluster.linkage_matrix)):
        Cluster.linkage_matrix[i][0] = Cluster.linkage_matrix[i][0]
    plt.figure(figsize=(40, 25))
    plt.rcParams.update({'font.size': 26})
    plt.title("Divisive clustering: " + fname)
    plt.xlabel("Amino acid sequences")
    plt.ylabel("Distance")
    labels = list(zip(*sorted(reverse_index_dict.items(), key=lambda x: x[0])))[1]
    dendro = hierarchy.dendrogram(Cluster.linkage_matrix, labels=labels)
    # plt.show()
    plt.savefig("Results/div_{}.svg".format(fname.split('.')[0]), dpi=400)


def main():
    fname = sys.argv[1] if len(sys.argv) > 1 else "AminoAcidSequences.fa"

    amino_acids = read_data(fname)
    similarity = get_similarity_matrix(fname, amino_acids, match=0, mismatch=1, indel=2)
    index_dict = {a.name: i for i, a in enumerate(amino_acids)}
    reverse_index_dict = {i: a.name for i, a in enumerate(amino_acids)}

    initial_cluster = Cluster([a for a in amino_acids])
    Cluster.hierarchy[1] = copy.deepcopy(Cluster.instances)
    print("Split initial cluster into {} clusters".format(len(amino_acids)))
    pbar = tqdm(total=len(amino_acids)-1)
    iter_num = 0
    while iter_num < len(amino_acids):
        iter_num += 1
        split_clusters(similarity, index_dict, amino_acids)
        pbar.update(1)
    print("Clustering complete")
    # for item in Cluster.hierarchy.items():
    #     print("Iter: ", item[0])
    #     for c in item[1]:
    #         print(c)
    #     print('-------')

    draw_dendrogram(fname, reverse_index_dict)


if __name__ == '__main__':
    main()
