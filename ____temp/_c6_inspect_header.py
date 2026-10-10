# -*- coding: utf-8 -*-
import csv, glob, os
files = glob.glob('昭明算展/谕组日/谕组日_*.csv')
print('NFILES:', len(files))
with open(files[0], encoding='gbk') as f:
    r = csv.reader(f)
    header = next(r)
    print('NCOLS:', len(header))
    for i,h in enumerate(header):
        print(i, repr(h))
