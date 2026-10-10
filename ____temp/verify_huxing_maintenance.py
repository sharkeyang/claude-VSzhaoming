# -*- coding: utf-8 -*-
import os, glob, csv
from collections import defaultdict

DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组周"
files = sorted(glob.glob(os.path.join(DIR, "*.csv")))
print("total files:", len(files))

sample = files[:500]

code2name = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

same = defaultdict(int)
total = defaultdict(int)

for f in sample:
    rows = []
    with open(f, encoding='gbk', errors='replace') as fh:
        reader = csv.reader(fh)
        header = next(reader, None)
        for r in reader:
            if len(r) < 5:
                continue
            date = r[0]
            hx = r[4]  # 护型 is index 4
            if not hx:
                continue
            code = hx[0]
            if code not in code2name:
                continue
            rows.append((date, code))
    rows.sort(key=lambda x: x[0])
    for i in range(len(rows)-1):
        cur = rows[i][1]
        nxt = rows[i+1][1]
        total[cur] += 1
        if cur == nxt:
            same[cur] += 1

out = []
out.append("护型维持率（下周仍为同护型）— 抽样前500文件")
out.append(f"{'code':<4}{'name':<4}{'transitions':<12}{'same':<10}{'rate':<10}")
for code in ['a','b','c','z','y','r']:
    t = total[code]
    s = same[code]
    rate = s/t*100 if t else 0
    out.append(f"{code:<4}{code2name[code]:<4}{t:<12}{s:<10}{rate:.1f}%")
print("\n".join(out))
