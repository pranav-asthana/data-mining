#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
from sklearn.model_selection import train_test_split
from tqdm import tqdm


#return the accuracy of the model
def get_accuracy(testSet, predictions):
    correct = 0
    for x in range(len(testSet)):
        if testSet[x] == predictions[x]:
            correct += 1
    return (correct/float(len(testSet))) * 100.0


#prints the confusion matrix, precision and recall
def get_metrics(targets, predictions):
    y_actu = pd.Series(targets, name='Actual')
    y_pred = pd.Series(predictions, name='Predicted')
    df_confusion = pd.crosstab(y_actu, y_pred)
    print(df_confusion)
    print()
    for col in list(df_confusion.columns):
        print('Recall of ', col, ':', (df_confusion[col][col]/sum(list(df_confusion.loc[col,:])))*100)
        print('Precision of ', col, ':', (df_confusion[col][col]/sum(list(df_confusion.loc[:,col])))*100)
        print()
        
def main():
    df = pd.read_csv('C:/Users/Sahil/Downloads/nursery.csv')
    df.columns = ['parents', 'has_nurs', 'form', 'children', 'housing', 'finance', 'social', 'health', 'target']
    train, test = train_test_split(df, test_size=0.2)

    #calculating the priors of the model
    priori = {}
    class_values = list(set(train['target']))
    class_data =  list(train['target'])
    for i in class_values:
        priori[i]  = class_data.count(i)/float(len(class_data))
    print ("Priori Values: ", priori)

    pred = []
    #calculating the conditional probabilities and getting predictions
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
            new_dict[priori_val] =  new_dict[priori_val]*round(priori[priori_val], 3)
        summ = sum(new_dict.values())
        for i in new_dict:
            new_dict[i] = new_dict[i]/summ
        prediction =  max(new_dict, key=lambda key: new_dict[key])
        pred.append(prediction)

    #getting accuracy, confusion matrix, precision, recall
    test_set = list(test['target'])
    print('Accuracy: ', get_accuracy(test_set, pred))
    get_metrics(test_set, pred)

    if __name__ == '__main__':
        main()    

