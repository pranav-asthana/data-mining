# Data mining - Assignment 2

## Usage

```
1. Agglomerative clustering
python3 agglomerative.py [linkage:{MIN,MAX,AVG}(default:MIN)] [file_name(default:AminoAcidSequences.fa)]
Example: python3 agglomerative.py MAX AminoAcidSequences.fa

2. Divisive clustering
python3 divisive.py [file_name(default:AminoAcidSequences.fa)]
Example: python3 divisive.py AminoAcidSequences.fa

3. k-means (k-medioids in actual implementation)
python3 kmeans.py [num_clusters(default:2)][[file_name(default:AminoAcidSequences.fa)]]
Example: python3 kmeans.py 5 AminoAcidSequences.fa

```

Results (dendrograms for heierarchical clustering and cluster members for kmeans) are stored at `Results/`.

## Requirements
scipy, matplotlib, numpy, pprint, tqdm
