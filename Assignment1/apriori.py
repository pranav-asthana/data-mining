from tqdm import tqdm
from pprint import pprint
import sys

# data = list(filter( lambda x: not x == '', open('test_dataset.csv', 'r').read().split('\n')))
# minsup = 2
data = list(filter(lambda x: not x == '', open('groceries.csv', 'r').read().split('\n')))
minsup = 100

def support_count(itemset):
    sc = 0
    for line in data:
        if itemset.intersection(set(line.split(','))) ==  itemset:
            sc += 1
    return sc

def generate_itemsets(L1, k, Lj=set()):
    if k == 2:
        Lj = L1
    Ck = {}
    for itemset in tqdm(Lj):
        for item in L1:
            new_itemset = frozenset(itemset.union(frozenset(item)))
            Ck[new_itemset] = 0

    for t in tqdm(data):
        t = set(t.split(','))
        for c in Ck.keys():
            if t.intersection(c) == c: # if c in t
                Ck[c] += 1
    Lk = [(c[0],c[1]) for c in tqdm(Ck.items()) if c[1]>=minsup and len(c[0])==k]
    return frozenset(Lk)

def main():
    global minsup
    if len(sys.argv) > 1:
        minsup = int(sys.argv[1])

    C1 = []
    _ = [C1.extend(d.split(',')) for d in data]
    C1 = set([frozenset([c]) for c in C1])

    L1 = []
    for c in tqdm(C1):
        sc = support_count(c)
        if sc >= minsup:
            L1.append((c, sc))
    lL1 = len(L1)
    print("Number of length 1 itemsets = {}".format(lL1))

    total = lL1
    f = open("output/Freq_Items_sup:"+str(minsup), 'w')
    f.write("Length 1: " + str(lL1) + "\n")
    _ = [f.write(",".join(c[0])+" ({})\n".format(c[1])) for c in L1]
    f.write('\n')
    Lprev = L1
    for i in range(2, len(C1)+1):
        Li = generate_itemsets(list(zip(*L1))[0], i, list(zip(*Lprev))[0])
        l = len(Li)
        total += l
        print("Number of length {} itemsets = {}".format(i, l))
        if l == 0:
            break
        f.write("Length "+ str(i) +": " + str(l) + '\n')
        _ = [f.write(",".join(c[0])+" ({})\n".format(c[1])) for c in Li]
        # f.write(str(Li))
        f.write('\n')
        Lprev = Li
    print("Total number of frequent itemsets =", total)


if __name__ == '__main__':
    main()
