#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
df = pd.read_csv('C:/Users/Sahil/Downloads/nursery.csv')
df.columns = ['parents', 'has_nurs', 'form', 'children', 'housing', 'finance', 'social', 'health', 'target']


# In[2]:


from sklearn.model_selection import train_test_split

train, test = train_test_split(df, test_size=0.2)


# In[3]:


priori = {}
#class_attr = 'target'
class_values = list(set(train['target']))
class_data =  list(train['target'])
for i in class_values:
    priori[i]  = class_data.count(i)/float(len(class_data))
print ("Priori Values: ", priori)


# In[4]:


from tqdm import tqdm
pred = []
for index, row in tqdm(test.iterrows(), total=test.shape[0]):
    hypothesis = {}
    new_dict = {}
    for col in df.columns[0:8]:
        hypothesis[col] = row[col]
    for priori_val in priori:
        for item in hypothesis:
            new_dict[priori_val] = 1
            filter1 = (train[item]==hypothesis[item]) & (train['target']== priori_val)
            filter2 = (train['target']==priori_val)
            new_dict[priori_val] = new_dict[priori_val]*round(len(train[filter1])/(len(train[filter2])), 3)
            #print(item, hypothesis[item], priori_val, round(len(df[filter1])/(len(df[filter2])), 3), priori[priori_val])
        new_dict[priori_val] =  new_dict[priori_val]*round(priori[priori_val], 3)
    #print(new_dict)
    summ = sum(new_dict.values())
    for i in new_dict:
        new_dict[i] = new_dict[i]/summ
    prediction =  max(new_dict, key=lambda key: new_dict[key])
    pred.append(prediction)


# In[5]:


def getAccuracy(testSet, predictions):
    correct = 0
    for x in range(len(testSet)):
        if testSet[x] == predictions[x]:
            correct += 1
    return (correct/float(len(testSet))) * 100.0


# In[6]:


testSet = list(test['target'])


# In[7]:


print('Accuracy: ', getAccuracy(testSet, pred))


# In[ ]:




