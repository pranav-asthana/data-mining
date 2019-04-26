%%writefile knn.py

# %load knn.py
#!/usr/bin/env python

# In[ ]:


import pandas as pd
import numpy as np
from tqdm import tqdm
import os.path
from sklearn.model_selection import train_test_split
from scipy.interpolate import make_interp_spline, BSpline
import matplotlib.pyplot as plt
import sys
from collections import Counter

#preprocess data to convert each column into multiple one hot encoded columns
def preprocess(df):
    new_cols = []
    df_tr = pd.DataFrame()
    for item in df.columns[0:len(df.columns)-1]:
        df_tr = pd.concat([df_tr, pd.get_dummies(df[item], prefix=item)], axis=1)
    df_tr[df.columns[len(df.columns)-1]] = df[df.columns[len(df.columns)-1]]
    return df_tr


#returns accuracy of model
def get_accuracy(testSet, predictions):
    correct = 0
    for x in range(len(testSet)):
        if testSet[x] == predictions[x]:
            correct += 1
    return (correct/float(len(testSet))) * 100.0


#creates a distance matrix from the one hot encoded preprocessed matrix
def get_dist_matrix(df):
    np_df = np.array(df)[:,0:27]
    df_dist = pd.DataFrame()
    df_dist.cols = [i for i in range(0,len(df))]
    
    if(os.path.isfile('distance_matrix.csv')):
        print('Distance matrix loading..')
        df_dist = pd.read_csv('distance_matrix.csv')
    else:    
        print('Creating distance matrix...')
        for i in tqdm(range(0,len(np_df))):
            c = abs(np_df - np_df[i])
            df_dist[i] = list(c.sum(axis=1))
        print('Saving distance matrix to disk...')    
        df_dist.to_csv('distance_matrix.csv') 
        
    return df_dist


#getting the performance graph for different values of k
def get_performance_graph(accuracy, k_min, k_max, k_step):
    T = np.array([i for i in range(k_min, k_max, k_step)])
    xnew = np.linspace(k_min,k_max,300) 
    spl = make_interp_spline(T, np.array(accuracy), k=3) #BSpline object
    power_smooth = spl(xnew)
    plt.plot(xnew,power_smooth)
    print('k versus accuracy plot')
    plt.show()
    
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
        
#main driver function  
def main():
    
    k_min = int(sys.argv[1])
    k_max = int(sys.argv[2])
    k_step = int(sys.argv[3])
    
    df = pd.read_csv('nursery.csv')
    df.columns = ['parents', 'has_nurs', 'form', 'children', 'housing', 'finance', 'social', 'health', 'target']
    df = preprocess(df)
    df_dist = get_dist_matrix(df)


    #splitting the data into train and test data
    train, test = train_test_split(df, test_size=0.2)
    test['indexes'] = test.index
    df_dist = df_dist.drop(list(test['indexes']))


    #calculating predictions of knn model for a range of k values
    accuracy = []
    for k in range(k_min, k_max, k_step):
        print('Running for k = ', k)
        preds = []
        for item in tqdm(list(test['indexes'])):    
            index_list = list(df_dist[str(item)].sort_values().index[0:k])
            neighbors = list(df.iloc[index_list]['target'])
            prediction = Counter(neighbors).most_common(1)[0][0]
            preds.append(prediction)
        acc = get_accuracy(list(test['target']), preds)
        print('Accuracy: ', acc)   
        print()
        get_metrics(list(test['target']),preds)
        accuracy.append(acc)
        
    get_performance_graph(accuracy, k_min, k_max, k_step)
    
if __name__ == '__main__':
    main()

