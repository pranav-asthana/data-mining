from tqdm import tqdm
from pprint import pprint
import sys

# data = list(filter( lambda x: not x == '', open('test_dataset.csv', 'r').read().split('\n')))
# minsup = 2
data = list(filter(lambda x: not x == '', open('groceries.csv', 'r').read().split('\n')))
minsup = 100
minconf = 50

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
    Lk = [(c[0],c[1]) for c in tqdm(Ck.items()) if c[1]>=minsup]
    return frozenset(Lk)

def find_confidence(rule, freq_items_sup):

    confidence = freq_items_sup[rule[0].union(rule[1])]/freq_items_sup[rule[0]]
    confidence *= 100
    return confidence

def generate_rules(itemset, freq_items_sup, final_rules, X):
    LPrev = []
    # X = {}  #dictionary that stores rule(tuple) with it's confidence
    for i in itemset:
        t = frozenset([i])
        u = (itemset.difference(t) ,t)
        if find_confidence(u,freq_items_sup) >= minconf:
            X[u] = find_confidence(u,freq_items_sup)
            LPrev.append(u)

    final_rules.extend(LPrev)

    Li = []
    #to make sure no repeated elements
    LPrev = list(set(LPrev))

    while 1:
        if len(LPrev) <= 1:
            return X
        for i in LPrev:
            for j in LPrev:
                if i == j:
                    continue
                #combine the two rules
                rhs = i[1].union(j[1])
                lhs = i[0].union(j[0])
                lhs = lhs.difference(rhs)

                if len(lhs) == 0:
                    return X

                s = (lhs, rhs)
                fc = find_confidence(s, freq_items_sup)
                if  fc >= minconf:
                    X[s] = fc
                    Li.append(s)

        #to make sure no repeated elements
        Li = list(set(Li))
        LPrev = Li
        final_rules.extend(LPrev)

def assn_rule_gen(X, L, freq_items_sup, final_rules):

    for i in range(0, len(L)):
        for c in L[i]:
            freq_items_sup[c[0]] = c[1]

    for i in range(1, len(L)):
        for c in L[i]:
            X.update(generate_rules(c[0], freq_items_sup, final_rules, X))

    return X

def main():
    global minsup
    global minconf
    if len(sys.argv) > 2:
        minsup = int(sys.argv[1])
        minconf = int(sys.argv[2])

    elif len(sys.argv) > 1:
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

    maximal = []
    closed = []
    L = [frozenset(L1)]

    for i in range(2, len(C1)+1):
        Li = generate_itemsets(list(zip(*L[-1]))[0], i)
        l = len(Li)
        total += l
        print("Number of length {} itemsets = {}".format(i, l))

        ## If an item belongs in Lprev but uska superset not in Li, then item in Lprev is maximal
        for item1 in L[-1]:
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

        L.append(Li)

    f.write("Maximal frequent itemsets: " + str(len(maximal)) + '\n')
    _ = [f.write(",".join(m[0])+" ({})\n".format(m[1])) for m in maximal]
    f.write("\n")
    f.write("Closed frequent itemsets: " + str(len(closed)) + '\n')
    _ = [f.write(",".join(c[0])+" ({})\n".format(c[1])) for c in closed]
    f.write("\n")
    print("Number of maximal frequent itemsets =", len(maximal))
    print("Number of closed frequent itemsets =", len(closed))
    print("Total number of frequent itemsets = ", total)

    X = {}
    final_rules = []
    freq_items_sup = {}
    X = assn_rule_gen(X, L, freq_items_sup, final_rules)

    f = open("output/Assn_Rules_sup:{},conf:{}".format(minsup, minconf), 'w')
    for elem in final_rules:
        f.write("{} ({}) --> {} ({}) - conf({:.2f})\n".format(set(elem[0]), freq_items_sup[elem[0]], set(elem[1]), freq_items_sup[elem[1]], X[elem]))

    f.close()

    print("Total number of association rules = {}".format(len(final_rules)))

if __name__ == '__main__':
    main()
