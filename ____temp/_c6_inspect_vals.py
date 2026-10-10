# -*- coding: utf-8 -*-
import csv, glob
from collections import Counter
files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
zhupai = Counter()
shangfu = Counter()
dza = Counter()
dengxing = Counter()
huxing = Counter()
n=0
for f in files[:200]:
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        for row in r:
            if len(row)<70: continue
            n+=1
            zhupai[row[10]]+=1
            shangfu[row[30]]+=1
            dza[row[13]]+=1
            dengxing[row[43]]+=1
            huxing[row[9]]+=1
print('rows:', n)
print('\n柱排[10] top values:')
for k,v in zhupai.most_common(30):
    print(' ', repr(k), v)
print('\n上符串[30] top values:')
for k,v in shangfu.most_common(30):
    print(' ', repr(k), v)
print('\n日ZA[13] values:')
for k,v in dza.most_common(20):
    print(' ', repr(k), v)
print('\n日等型[43] top:')
for k,v in dengxing.most_common(20):
    print(' ', repr(k), v)
print('\n护型[9] top:')
for k,v in huxing.most_common(10):
    print(' ', repr(k), v)
