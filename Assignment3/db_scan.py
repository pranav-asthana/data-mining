from preprocess import *
import matplotlib.pyplot as plt

data_dir = "data/"
fname = 'german.data-numeric'
eps = 10
min_points = 80

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
        if not set(neighbours[i]).intersection(set(core)) == set():
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
        if point == center: continue

        d = distance_matrix[points.index(center)][i]
        if d < eps:
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
            TP += 1
        else:
            FP += 1
    for p in noise:
        if p.label == 2:
            TN += 1
        else:
            FN += 1

    print("\n\t     CONFUSION MATRIX")
    print("\t\t| Actual Class\t| Total")
    print("                | GOOD\tFRAUD")
    print("Predicted Class +---------------+---------------")
    print("GOOD\t\t| "+str(TP)+"\t"+str(FP)+"\t| "+str(TP+FP))
    print("FRAUD\t\t| "+str(FN)+"\t"+str(TN)+"\t| "+str(FN+TN))
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

    # points = []
    # for center in tqdm(transactions):
    #     points.append(len(get_neighbours(transactions, center, eps)))
    # print(np.mean(points))
    #
    # distances = []
    # for p in tqdm(transactions):
    #     for p2 in transactions:
    #         distances.append(np.linalg.norm(p.attr-p2.attr))
    # print(np.mean(distances))

    core, border, noise = label_points(transactions, distance_matrix)
    print(len(core))
    print(len(border))
    print(len(noise))
    evaluate(core, border, noise)


if __name__ == '__main__':
    main()
