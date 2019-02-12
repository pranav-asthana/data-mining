from tqdm import tqdm
from pprint import pprint

# data = list(filter( lambda x: not x == '', open('test_dataset.csv', 'r').read().split('\n')))
data = list(filter( lambda x: not x == '', open('groceries.csv', 'r').read().split('\n')))
minsup = 500

def support_count(itemset):
    sc = 0
    for line in data:
        if itemset.intersection(set(line.split(','))) ==  itemset:
            sc += 1
    return sc

def generate_itemsets(C1, k, Cj=set()):
    if k == 2:
        Cj = C1
    Ck = []
    for itemset in tqdm(Cj):
        for item in C1:
            new_itemset = frozenset(itemset.union(frozenset(item)))
            sc = support_count(new_itemset)
            if sc >= minsup and len(new_itemset)==k:
                Ck.append((new_itemset, sc))
    return frozenset(Ck)

def main():
    L1 = []
    _ = [L1.extend(d.split(',')) for d in data]
    L1 = set([frozenset([c]) for c in L1])

    C1 = []
    for c in tqdm(L1):
        sc = support_count(c)
        if sc >= minsup:
            C1.append((c, sc))
    lC1 = len(C1)
    print("Number of length 1 itemsets = {}".format(lC1))

    total = lC1
    f = open("itemsets", 'w')
    f.write("Length 1: " + str(lC1) + "\n")
    _ = [f.write(",".join(c[0])+" ({})\n".format(c[1])) for c in C1]
    f.write('\n')
    Cprev = C1
    for i in range(2, len(C1)+1):
        Ci = generate_itemsets(list(zip(*C1))[0], i, list(zip(*Cprev))[0])
        l = len(Ci)
        total += l
        print("Number of length {} itemsets = {}".format(i, l))
        if l == 0:
            break
        f.write("Length "+ str(i) +": " + str(l) + '\n')
        _ = [f.write(",".join(c[0])+" ({})\n".format(c[1])) for c in Ci]
        # f.write(str(Ci))
        f.write('\n')
        Cprev = Ci
    print("Total number of itemsets generated: ", total)


if __name__ == '__main__':
    main()
