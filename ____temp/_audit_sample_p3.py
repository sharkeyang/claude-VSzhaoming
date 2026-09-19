# -*- coding: utf-8 -*-
import csv, glob, sys, collections
sys.stdout.reconfigure(encoding='utf-8')
DATA_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = glob.glob(DATA_DIR + '/*.csv')

# 采样800个文件，检查列[26] 的 P3 分布
p3_all = 0
n_all = 0
bad_files = []
for fi, fp in enumerate(files[:800]):
    p3 = 0; n = 0
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f); next(r)
        for row in r:
            if len(row) < 27: continue
            try:
                v = float(row[26])
            except:
                continue
            n += 1
            if v >= 3: p3 += 1
    if n > 0:
        p3_all += p3; n_all += n
        if p3/n < 0.10:
            bad_files.append((fp, p3/n, n))
print(f'采样800文件: 总样本={n_all}, 总P3={p3_all/n_all*100:.1f}%')
print(f'P3<10% 的文件数: {len(bad_files)}')
for fp, r, n in bad_files[:10]:
    print(f'  {fp}: P3={r*100:.1f}% n={n}')
