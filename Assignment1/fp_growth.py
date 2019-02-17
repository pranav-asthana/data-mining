import pandas as pd
import sys
from pprint import pprint
from tqdm import tqdm

class TreeNode:
    def __init__(self,value,count,parent):
        self.value = value
        self.count = count
        self.parent = parent
        self.nodelink = None
        self.children = {}
    def __str__(self):
        res = self.__repr__() + "\n"
        res += "value: " + str(self.value) + "\n"
        res += "count: " + str(self.count) + "\n"
        res += "parent: {" + str(self.parent) + "}\n"
        res += "nodelink: {" + str(self.nodelink) + "}\n"
        res += "children: " + str(self.children) + "\n"
        res += "\n"
        return res


#make a dictionary of the transactions in the datast and increment if duplicate
def init_data(data):
    data_dict = {}
    for transaction in data:
        temp = frozenset(transaction)
        data_dict[temp] = data_dict.get(temp,0)+1
    return data_dict


#build tree
def create_tree(data,support):
    #first pass throrugh the dataset where ht is a dictionary containing all the items and their counts/support
    ht = {}
    for transaction in data:
        for item in transaction:
            ht[item] = ht.get(item,0)+data[transaction]

    #header will contain only those items that meet the support criteria
    headertable = {}
    for item in ht:
        if ht[item] >= support:
            headertable[item] = [ht[item],None]

    #return None if no item meets minimum support
    if len(headertable) == 0:
        return None

    #create an empty node
    node = TreeNode(None,None,None)

    #second pass through dataset to put the items in order
    for transaction in data:
        temp = {}

        #selecting the items of each transaction that are present in the headertable
        for item in transaction:
            if item in headertable: temp[item] = headertable[item][0]

        #if more than 1 item are present then sort them in descending order of support
        if len(temp) > 0:
            temp = [r[0] for r in sorted(temp.items(), key=lambda r:r[1], reverse=True)]

            #populate tree with ordered frequent item set
            update_tree(temp,headertable,node,data[transaction])

    return headertable


#inserting a path into the tree
def update_tree(items,headertable,node,count):

    #if tree has a child such that child name is equal to item(s) name then just increment the count of children
    if items[0] in node.children:
        node.children[items[0]].count += count

    #otherwise create a new node
    else:
        node.children[items[0]] = TreeNode(items[0],count,node)

        #this if-else is for linking the node link to the most recent occurence of the item
        if headertable[items[0]][1] is None:
            headertable[items[0]][1] = node.children[items[0]]
        else:
            _node = headertable[items[0]][1]
            while _node.nodelink is not None:
                _node = _node.nodelink
            _node.nodelink = node.children[items[0]]

    #call update_tree with the remaining ordered items
    if len(items) > 1:
        update_tree(items[1:],headertable,node.children[items[0]],count)


#this function keeps moving up the tree collecting the names of the nodes it encounters along the way
def ascend_path(node):
    path = []
    while node.parent.value is not None:
        path.append(node.parent.value)
        node = node.parent
    return path


#this keeps calling ascend_tree for all the nodes of the same item by traversing the linked list until it hits the end
def find_prefix_path(node):
    data = {}
    while node is not None:
        path = ascend_path(node)
        if len(path) > 0: data[frozenset(path)] = node.count
        node = node.nodelink
    return data


def minetree(headertable,s,f,support):
    x = [r[0] for r in sorted(headertable.items(),key=lambda r:r[1][0])]
    for i in x:
        ss = s.copy()
        ss.add(i)
        f[tuple(ss)] = headertable[i][0]
        data = find_prefix_path(headertable[i][1])
        if len(data) > 0:
            new_header = create_tree(data,support)
            if new_header is not None:
                minetree(new_header,ss,f,support)

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
    global minsup, minconf
    minconf = 50
    minsup = 100
    df = pd.read_csv('groceries.csv', sep='delimiter', header=None)

    # minsup = 2
    # df = pd.read_csv('test_dataset.csv', sep='delimiter', header=None)

    df.columns = ['items']
    dataSet = list(df['items'].apply(lambda x: x.split(',')))

    if len(sys.argv) > 2:
        minsup = int(sys.argv[1])
        minconf = int(sys.argv[2])

    elif len(sys.argv) > 1:
        minsup = int(sys.argv[1])

    data = init_data(dataSet)
    header = create_tree(data, minsup)
    frequent_items = {}
    minetree(header, set([]), frequent_items, minsup)

    print("Number of frequent itemsets generated:", len(frequent_items.items()))
    # print(frequent_items)

    f = open('output_fp/Freq_Items_sup:{}'.format(minsup), 'w')
    _ = [f.write(",".join(c[0]) + " ({})\n".format(c[1])) for c in frequent_items.items()]
    f.close()

    L = {}
    for itemset in frequent_items.items():
        fs = frozenset(itemset[0])
        sc = itemset[1]
        L[len(fs)] = L.get(len(fs), []) + [(fs, sc)]
    res = []
    for k in sorted(L.keys()):
        res.append(L[k])

    X = {}
    final_rules = []
    freq_items_sup = {}
    X = assn_rule_gen(X, res, freq_items_sup, final_rules)

    f = open("output_fp/Assn_Rules_sup:{},conf:{}".format(minsup, minconf), 'w')
    for elem in final_rules:
        f.write("{} ({}) --> {} ({}) - conf({:.2f})\n".format(set(elem[0]), freq_items_sup[elem[0]], set(elem[1]), freq_items_sup[elem[1]], X[elem]))
    f.close()

    print("Total number of association rules = {}".format(len(final_rules)))

if __name__ == '__main__':
    main()
    # for i in range(100):
    #     main()
