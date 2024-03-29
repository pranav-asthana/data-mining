from tqdm import tqdm
from pprint import pprint
import sys

# data = list(filter( lambda x: not x == '', open('test_dataset.csv', 'r').read().split('\n')))
# minsup = 2
data = list(filter(lambda x: not x == '', open('groceries.csv', 'r').
                   read().split('\n')))
minsup = 100
minconf = 50


def support_count(itemset):
    sc = 0
    for line in data:
        if itemset.intersection(set(line.split(','))) == itemset:
            sc += 1
    return sc


def generate_itemsets(Lj, k):
    # Merge Lj with itself to generate candidates of length k
    Ck = {}
    for is1 in Lj:
        for is2 in Lj:
            if is1 == is2:
                continue
            u = is1.union(is2)
            if len(u) == k:
                Ck[u] = 0

    # Prune/remove candidates that do not meet the minimum support requirement
    for t in tqdm(data):
        t = set(t.split(','))
        for c in Ck.keys():
            if t.intersection(c) == c:  # if c in t
                Ck[c] += 1
    Lk = [(c[0], c[1]) for c in tqdm(Ck.items()) if c[1] >= minsup]
    return frozenset(Lk)


def find_confidence(rule, freq_items_sup):
    confidence = freq_items_sup[rule[0].union(rule[1])]/freq_items_sup[rule[0]]
    confidence *= 100
    return confidence


def generate_rules(itemset, freq_items_sup, final_rules, X):
    LPrev = []  # Stores the list of rules of the prev level in lattice

    # To generate rules in the first level
    for i in itemset:
        t = frozenset([i])
        u = (itemset.difference(t), t)
        if find_confidence(u, freq_items_sup) >= minconf:
            X[u] = find_confidence(u, freq_items_sup)
            LPrev.append(u)
    final_rules.extend(LPrev)

    Li = []
    # To make sure no repeated elements
    LPrev = list(set(LPrev))
    while 1:
        # print('-')
        if len(LPrev) <= 1:
            return X
        for i in LPrev:
            for j in LPrev:
                if i == j:
                    continue
                # Combine the two rules
                rhs = i[1].union(j[1])
                lhs = i[0].union(j[0])
                lhs = lhs.difference(rhs)
                if len(lhs) == 0:
                    return X
                s = (lhs, rhs)
                fc = find_confidence(s, freq_items_sup)
                if fc >= minconf:
                    X[s] = fc
                    Li.append(s)
        # To make sure no repeated elements
        Li = list(set(Li))
        LPrev = Li
        final_rules.extend(LPrev)


def assn_rule_gen(X, L, freq_items_sup, final_rules):
    # Helper function to call generate_rules
    for i in range(0, len(L)):
        for c in L[i]:
            freq_items_sup[c[0]] = c[1]

    for i in tqdm(range(1, len(L))):
        for c in L[i]:
            X.update(generate_rules(c[0], freq_items_sup, final_rules, X))

    return X


def main():
    global minsup
    global minconf

    # Take minsup and minconf from cmd-line arguments, else default
    if len(sys.argv) > 2:
        minsup = int(sys.argv[1])
        minconf = int(sys.argv[2])

    elif len(sys.argv) > 1:
        minsup = int(sys.argv[1])

    C1 = []  # Candidate set 1
    _ = [C1.extend(d.split(',')) for d in data]
    C1 = set([frozenset([c]) for c in C1])

    L1 = []  # Actual set 1, that have support >= minsup
    for c in tqdm(C1):
        sc = support_count(c)
        if sc >= minsup:
            L1.append((c, sc))
    lL1 = len(L1)
    print("Number of length 1 itemsets = {}".format(lL1))

    total = lL1  # Store total number of itemsets
    f = open("output/Freq_Items_sup:"+str(minsup), 'w')
    f.write("Length 1: " + str(lL1) + "\n")
    _ = [f.write(",".join(c[0])+" ({})\n".format(c[1])) for c in L1]
    f.write('\n')

    maximal = []
    closed = []
    L = [frozenset(L1)]  # Stores all frequent itemsets as a list of sets for different length itemsets

    for i in range(2, len(C1)+1):
        # Use the previous layer (length-1) to generate current layer
        Li = generate_itemsets(list(zip(*L[-1]))[0], i)
        l = len(Li)
        total += l
        print("Number of length {} itemsets = {}".format(i, l))

        # If an item belongs in L[-1] but its superset not in Li, then item in L[-1] is maximal
        # If an item has sc1 in Li and subset has same sc1 in L[-1], then item is L[-1] is closed
        for item1 in L[-1]:
            belongs = False
            eq_count = False
            for item2 in Li:
                ii = item1[0].intersection(item2[0])
                if ii == item1[0]:
                    belongs = True
                if ii == item1[0] and item2[1] == item1[1]:
                    eq_count = True
            if not belongs:
                maximal.append(item1)
            if not eq_count:
                closed.append(item1)

        if l == 0:  # No itemset of length i was found to be frequent
            break

        f.write("Length " + str(i) + ": " + str(l) + '\n')
        _ = [f.write(",".join(c[0]) + " ({})\n".format(c[1])) for c in Li]
        # f.write(str(Li))
        f.write('\n')

        L.append(Li)

    f.write("Maximal frequent itemsets: " + str(len(maximal)) + '\n')
    _ = [f.write(",".join(m[0]) + " ({})\n".format(m[1])) for m in maximal]
    f.write("\n")
    f.write("Closed frequent itemsets: " + str(len(closed)) + '\n')
    _ = [f.write(",".join(c[0]) + " ({})\n".format(c[1])) for c in closed]
    f.write("\n")
    print("Number of maximal frequent itemsets =", len(maximal))
    print("Number of closed frequent itemsets =", len(closed))
    print("Total number of frequent itemsets = ", total)

    # Rule Generation

    X = {}  # dict that stores a tuple of (lhs,rhs) of the rule with it's confidence
    final_rules = []  # list of final rules
    freq_items_sup = {}  # dict that stores itemset with it's sup_count

    X = assn_rule_gen(X, L, freq_items_sup, final_rules)  # Calling helper function

    # print("FINAL RULES")
    # print(final_rules)

    redundant_rules = set()
    # Removing redundant generate_rules
    for i in range(0, len(final_rules)-1):
        for j in range(i+1, len(final_rules)):
            # have equal confidence and support count and lhs and rhs are subset 
            # of another rule's lhs and rhs respectively
            if X[final_rules[i]] == X[final_rules[j]]\
               and freq_items_sup[final_rules[i][0]] == freq_items_sup[final_rules[j][0]]\
               and freq_items_sup[final_rules[i][1]] == freq_items_sup[final_rules[j][1]]:

                if(set(final_rules[j][0]).issubset(set(final_rules[i][0]))\
                   and set(final_rules[j][1]).issubset(set(final_rules[i][1]))):
                    redundant_rules.add(final_rules[j])

                elif (set(final_rules[i][0]).issubset(set(final_rules[j][0]))\
                      and set(final_rules[i][1]).issubset(set(final_rules[j][1]))):
                    redundant_rules.add(final_rules[i])

    final_rules = list(set(final_rules) - redundant_rules)

    #writing results to output file
    f = open("output/Assn_Rules_sup:{},conf:{}".format(minsup, minconf), 'w')
    f.write("Association rules:\n")
    for elem in tqdm(final_rules):
        f.write("{} ({}) --> {} ({}) - conf({:.2f})\n".format(set(elem[0]), freq_items_sup[elem[0]], set(elem[1]), freq_items_sup[elem[1]], X[elem]))
    print("Total number of association rules = {}".format(len(final_rules)))

    if not len(redundant_rules) == 0:
        f.write("\n")
        f.write("Redundant association rules:\n")
        for elem in tqdm(redundant_rules):
            f.write("{} ({}) --> {} ({}) - conf({:.2f})\n".format(set(elem[0]), freq_items_sup[elem[0]], set(elem[1]), freq_items_sup[elem[1]], X[elem]))
        f.close()
        print("Total number of redundant rules = {}".format(len(redundant_rules)))
    else:
        print("Total number of redundant rules = 0")


if __name__ == '__main__':
    main()
