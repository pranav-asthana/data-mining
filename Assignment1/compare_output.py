import sys
import re
from pprint import pprint

d1 = open(sys.argv[1], 'r').read()
d2 = open(sys.argv[2], 'r').read()

fAitems = list(filter(lambda x: re.search('.*\([0-9]*\).*', x), d1.split('\n')))
fBitems = list(filter(lambda x: re.search('.*\([0-9]*\).*', x), d2.split('\n')))

fA = {frozenset(l.split('(')[0].strip().split(',')): l.split('(')[1].split(')')[0] for l in fAitems}
fB = {frozenset(l.split('(')[0].strip().split(',')): l.split('(')[1].split(')')[0] for l in fBitems}

fA = set(fA.items())
fB = set(fB.items())

print(len(fA))
print(len(fB))

print(len(fA-fB))
print(len(fB-fA))
