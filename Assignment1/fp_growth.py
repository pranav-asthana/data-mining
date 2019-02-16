import pandas as pd
import sys

df = pd.read_csv('groceries.csv', sep='delimiter', header=None)
df.columns = ['items']
dataSet = list(df['items'].apply(lambda x: x.split(',')))

class TreeNode:
    def __init__(self,value,count,parent):
        self.value = value
        self.count = count
        self.parent = parent
        self.nodelink = None
        self.children = {}


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

def main():
    minsup = 100
    minconf = 50
    if len(sys.argv) > 2:
        minsup = int(sys.argv[1])
        minconf = int(sys.argv[2])

    elif len(sys.argv) > 1:
        minsup = int(sys.argv[1])

    data = init_data(dataSet)
    header = create_tree(data, minsup)
    frequent_items = {}
    minetree(header, set([]), frequent_items, minsup)
    #confidence_data = get_confidence(support_data, .6)
    print(len(frequent_items.items()))
    f = open('output_fp/Freq_Items_sup:{}'.format(minsup), 'w')
    _ = [f.write(",".join(c[0]) + " ({})\n".format(c[1])) for c in frequent_items.items()]
    f.close()
    #print(confidence_data)

    # l_keys = [list(item) for item in list(frequent_items.keys())]
    # l_supports = list(frequent_items.values())
    #
    # #I should really learn how to write to a txt file :( I got very irritated trying to figure it out
    # l1_k = []
    # l1_s = []
    # l2_k = []
    # l2_s = []
    # l3_k = []
    # l3_s = []
    # for i in range (0,len(l_keys)):
    #     lenght = len(l_keys[i])
    #     if(lenght==1):
    #         l1_k.append(l_keys[i])
    #         l1_s.append(l_supports[i])
    #     elif(lenght==2):
    #         l2_k.append(l_keys[i])
    #         l2_s.append(l_supports[i])
    #     elif(lenght==3):
    #         l3_k.append(l_keys[i])
    #         l3_s.append(l_supports[i])
    #
    #
    # final_k = l1_k + l2_k + l3_k
    # final_s = l1_s + l2_s + l3_s
    #
    #
    # df_new = pd.DataFrame()
    # df_new['itemsets'] = final_k
    # df_new['supports'] = final_s
    # df_new.to_csv('output_fp/sup_100.txt', header=None, index=None, sep=' ', mode='a')

if __name__ == '__main__':
    main()
