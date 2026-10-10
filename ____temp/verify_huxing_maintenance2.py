# -*- coding: utf-8 -*-
import os, glob, csv
from collections import defaultdict

code2name = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

def compute(dirpath, hx_col, date_col, sample_n=500, label=""):
    files = sorted(glob.glob(os.path.join(dirpath, "*.csv")))[:sample_n]
    same = defaultdict(int)
    total = defaultdict(int)
    for f in files:
        rows = []
        with open(f, encoding='gbk', errors='replace') as fh:
            reader = csv.reader(fh)
            next(reader, None)
            for r in reader:
                if len(r) <= hx_col:
                    continue
                date = r[date_col]
                hx = r[hx_col]
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
    out = [f"=== {label} (sample {sample_n} files) ==="]
    out.append(f"{'code':<4}{'name':<4}{'trans':<10}{'same':<8}{'rate':<8}")
    for code in ['a','b','c','z','y','r']:
        t = total[code]; s = same[code]
        rate = s/t*100 if t else 0
        out.append(f"{code:<4}{code2name[code]:<4}{t:<10}{s:<8}{rate:.1f}%")
    return "\n".join(out)

# 周类: 护型 col4, date col0
print(compute(r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组周", 4, 0, 500, "周类 护型维持率(下周仍为同护型)"))
print()
# 日类: 护型 DXAB col9, date col0
print(compute(r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日", 9, 0, 500, "日类 护型维持率(次日仍为同护型)"))
