from preprocess import *
import matplotlib.pyplot as plt
import pandas as pd
from pprint import pprint

data_dir = "data/"
fname = 'german.data-numeric'
eps = 10
min_points = 15

def label_points(points, distance_matrix):
    fname = 'dbscan_labelled_{}_{}.pkl'.format(eps, min_points)
    if fname in os.listdir(data_dir):
        f = open(os.path.join(data_dir, fname), 'rb')
        core, border, noise = pkl.load(f)
        f.close()
        return core, border, noise
    core = []
    border = []
    noise = []

    neighbours = [get_neighbours(points, p, eps, distance_matrix) for p in tqdm(points)]

    for i in range(len(points)):
        if len(neighbours[i]) >= min_points:
            core.append(points[i])
    for i in range(len(points)):
        if points[i] in core: continue
        if not set([n.id for n in neighbours[i]]).intersection([c.id for c in set(core)]) == set():
            border.append(points[i])
        else:
            noise.append(points[i])

    f = open(os.path.join(data_dir, fname), 'wb')
    pkl.dump((core, border, noise), f)
    f.close()
    return core, border, noise


def get_neighbours(points, center, eps, distance_matrix):
    neighbours = []
    for i in range(len(points)):
        point = points[i]
        # if point == center: continue  # Decide whether to keep center or not

        d = distance_matrix[points.index(center)][i]
        if d <= eps:  # Points on EPS border also included
            neighbours.append(point)
    return neighbours

def determine_eps(fname, points, distance_matrix, k=4):
    print("Determining eps...")
    overall = []
    for i in trange(len(points)):
        distances = distance_matrix[i,:]
        overall.append(sorted(distances)[k])
    overall = sorted(overall)

    plt.plot(np.arange(0, len(overall)), overall)
    # plt.savefig('Results/DBSCAN/' + fname + '_elbow_'+str(k)+'.png')
    plt.show()
    plt.close()

def evaluate(core, border, noise):
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for p in core+border:
        if p.label == 1:
            TN += 1
        else:
            FN += 1
    for p in noise:
        if p.label == 2:
            TP += 1
        else:
            FP += 1

    print("\n\t     CONFUSION MATRIX")
    print("\t\t| Actual Class\t| Total")
    print("                | OUT\tIN")
    print("Predicted Class +---------------+---------------")
    print("OUT\t\t| "+str(TP)+"\t"+str(FP)+"\t| "+str(TP+FP))
    print("IN\t\t| "+str(FN)+"\t"+str(TN)+"\t| "+str(FN+TN))
    print("----------------+---------------+---------------")
    print("Total\t\t| "+str(TP+FN)+"\t"+str(FP+TN)+"\t| "+str(FN+TN+TP+FP)+"\n")


    precison = TP / (TP + FP)
    print("Precision: {}".format(precison))

    recall = TP / (TP + FN)
    print("Recall: {}".format(recall))

    accuracy = (TP + TN) / (TP + TN + FP + FN)
    print("Accuracy: {}".format(accuracy))


def main():
    global eps, min_points

    eps, min_points = int(sys.argv[1]), int(sys.argv[2])

    transactions = read_data(data_dir, fname)
    distance_matrix = get_distance_matrix(transactions, data_dir)


    # determine_eps(fname, transactions, distance_matrix, 4)

    core, border, noise = label_points(transactions, distance_matrix)
    print(len(core))
    print(len(border))
    print(len(noise))
    # print(len(noise)+len(core)+len(border))
    evaluate(core, border, noise)

    # from sklearn.cluster import DBSCAN
    # outlier_detection = DBSCAN(
    #   eps = eps,
    #   metric="euclidean",
    #   min_samples = min_points,
    #   n_jobs = -1)
    # df = pd.DataFrame([t.attr for t in transactions])
    # clusters = outlier_detection.fit(df).labels_
    # mine = [-1 if t.id in [x.id for x in noise] else 0 for t in transactions]
    # print(clusters)
    # print(set(clusters))
    # print(mine)
    # print(set(mine))
    # for i in range(1000):
    #     if not clusters[i] == mine[i]:
    #         print(transactions[i])
    #         print("My label: " + str(mine[i]))
    #         print("Their label: " + str(clusters[i]))
    # print(sum([clusters[i]==mine[i] for i in range(1000)]))


if __name__ == '__main__':
    main()
