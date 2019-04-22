from preprocess import *
import matplotlib.pyplot as plt

data_dir = "data/"
fname = 'german.data-numeric'
k = 5
distance_matrix = None

k_sets = {}
lrds = {}

def timer(fn):
    def fn_wrapper(*args, **kw):
        import time
        ts = time.time()
        result = fn(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', fn.__name__.upper())
            kw['log_time'][name] = int((te - ts) * 1000)
        else:
            print('%r  %2.2f ms' % (fn.__name__, (te - ts) * 1000))
        return result
    return fn_wrapper

def k_set(p):
    # Return k-set and k_distance
    if k_sets.get(p, False):
        return k_sets[p]
    k_distance = sorted(distance_matrix[:, p])[k]
    Nk = set()
    for p2 in range(N):
        if distance_matrix[p][p2] <= k_distance and not p2 == p:
            Nk.add(p2)
    k_sets[p] = (Nk, k_distance)
    return Nk, k_distance

def RD(a, b):
    return max(k_set(b)[1], distance_matrix[a][b])

# @timer
def LRD(p):
    if lrds.get(p, False):
        return lrds[p]
    Nk, kdist = k_set(p)
    inverse = sum([RD(p, p2) for p2 in Nk])/len(Nk)
    lrds[p] = 1/inverse
    return 1/inverse

def LOF(p):
    Nk, kdist = k_set(p)
    return sum([LRD(p2)/LRD(p) for p2 in Nk])/len(Nk)

def evaluate(pred, labels):
    accuracy = np.mean([pred[i]==labels[i] for i in range(N)])
    print(accuracy)
    TP = 0
    FP = 0
    TN = 0
    FN = 0
    for i in range(N):
        if pred[i] == 1:
            if labels[i] == 1:
                TN += 1
            else:
                FN += 1
        if pred[i] == 2:
            if labels[i] == 2:
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
    global distance_matrix, k, N
    transactions = read_data(data_dir, fname)
    distance_matrix = get_distance_matrix(transactions, data_dir)
    k = 10
    threshold = 1.7

    N = distance_matrix.shape[0]

    lofs = []
    for i in trange(N):
        lofs.append(LOF(i))

    pred = []
    for i in range(N):
        if lofs[i] > threshold:
            pred.append(2)
        else:
            pred.append(1)
    labels = [transactions[i].label for i in range(N)]

    evaluate(pred, labels)
    print(min(lofs), max(lofs))

if __name__ == '__main__':
    main()
