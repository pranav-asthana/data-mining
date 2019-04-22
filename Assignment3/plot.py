from preprocess import *
import pandas as pd
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 unused import

def convert_to_kD(points, k=2):
    pca = PCA(n_components=k)
    pca_result = pca.fit_transform(points.values)
    return pd.DataFrame(pca_result)

def main():
    data_dir = 'data/'
    transactions = read_data(data_dir, 'german.data-numeric')

    for i in range(5):
        print(transactions[i])

    points = pd.DataFrame([t.attr for t in transactions])
    labels = [t.label for t in transactions]

    print(set(points[23]))

    points2d = convert_to_kD(points, k=2)
    plt.scatter(points2d[0], points2d[1], c=['red' if l==2 else 'green' for l in labels], marker='.')
    plt.show()
    plt.close()

    # points3d = convert_to_kD(points, k=3)
    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # plt.scatter(points3d[0].values, points3d[1].values, points3d[2].values, c=['red' if l==2 else 'green' for l in labels])
    # plt.show()
    # plt.close()


if __name__ == '__main__':
    main()
