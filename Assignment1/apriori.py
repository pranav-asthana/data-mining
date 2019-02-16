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

def generate_itemsets(Lj, k):
    Ck = {}
    for is1 in Lj:
        for is2 in Lj:
            if is1 == is2:
                continue
            u = is1.union(is2)
            if len(u) == k:
                Ck[u] = 0

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
    maximal = []
    closed = []
    for i in range(2, len(C1)+1):
        Li = generate_itemsets(list(zip(*Lprev))[0], i)
        l = len(Li)
        total += l
        print("Number of length {} itemsets = {}".format(i, l))

        ## If an item belongs in Lprev but uska superset not in Li, then item in Lprev is maximal
        for item1 in Lprev:
            belongs = False
            eq_count = False
            for item2 in Li:
                ii = item1[0].intersection(item2[0])
                if ii == item1[0]:
                    belongs = True
                if ii == item1[0] and item2[1]==item1[1]:
                    eq_count = True
            if not belongs:
                maximal.append(item1)
            if not eq_count:
                closed.append(item1)
        ## If an item has sc1 in Li and subset has same sc1 in Lprev

        if l == 0:
            break
        f.write("Length "+ str(i) +": " + str(l) + '\n')
        _ = [f.write(",".join(c[0])+" ({})\n".format(c[1])) for c in Li]
        # f.write(str(Li))
        f.write('\n')
        Lprev = Li
    f.write("Maximal frequent itemsets: " + str(len(maximal)) + '\n')
    _ = [f.write(",".join(m[0])+" ({})\n".format(m[1])) for m in maximal]
    f.write("\n")
    f.write("Closed frequent itemsets: " + str(len(closed)) + '\n')
    _ = [f.write(",".join(c[0])+" ({})\n".format(c[1])) for c in closed]
    f.write("\n")
    print("Total number of frequent itemsets =", total)
    print("Number of maximal frequent itemsets =", len(maximal))
    print("Number of closed frequent itemsets =", len(closed))


if __name__ == '__main__':
    main()
