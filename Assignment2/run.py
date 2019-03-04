import os

options = [
            (0, 1, 1),
            (0, 1, 2),
            (1, -1, -2),
            (2, -1, -2),
            (1, -1, -1),
            (2, -1, -1)
]

for o in options:
    cmd = 'python preprocess.py {} {} {}'.format(o[0], o[1], o[2])
    print(cmd)
    os.system(cmd)
