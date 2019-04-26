k-nearest neighbors and Naive Bayes classifier has been implemented in knn.py and nb.py

The nursery dataset has been used.

nb.py doesn't require any arguments to run.
knn.py requries 3 command line arguments k_min, k_max, k_scale

k_min: starting k value
k_max: ending k value
k_scale: increment in k value

For, example if you wish to run the code starting from k=1 to k=100 with an increment of 5 i.e 1,6,11,16 etc. run the following command:

python knn.py 1 100 5
