# -*- coding: utf-8 -*-
"""算全部样本基线（下周P3）"""
import io, sys, glob, os

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组周'
files = glob.glob(os.path.join(DATA_DIR, '谕组周_*.csv'))

total = 0
p3 = 0
for fp in files:
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        rows = []
        for line in f:
            r = line.strip().split(',')
            if len(r) < 4: continue
            rows.append(r)
        for i, r in enumerate(rows):
            if i+1 >= len(rows): continue
            nxt = rows[i+1]
            try:
                nxt_hr = float(nxt[3])
            except:
                continue
            total += 1
            if nxt_hr >= 3: p3 += 1

print(f'全部样本: n={total}, 下周P3%={p3/total*100:.1f}%', flush=True)
