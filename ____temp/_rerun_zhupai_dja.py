# -*- coding: utf-8 -*-
"""
柱排研究：哪些柱排对再次上破DJA/站稳DJA至关重要？哪些应回避？
====================================================
对 DXZC>25 且当日未触顶的样本，分析未触顶日具体柱排 × 未来10天：
1. 再次上破DJA（未来10天内日ZA从<=0变为>0）
2. 站稳DJA（未来10天内日ZA>0的天数>=5）
3. 再次触顶（上符串末位A）
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

# 柱排 -> [n, 上破DJA, 站稳DJA, 触顶]
zp = defaultdict(lambda: [0,0,0,0])
LOOKAHEAD = 10
files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
    except Exception:
        continue
    if len(rows) < 5: continue

    n = len(rows)
    for i in range(n):
        row = rows[i]
        if len(row) < 31: continue
        zc = to_f(row[14])
        if zc is None or zc <= 25: continue
        sf = row[30].strip()
        if not sf or sf[-1] == 'A': continue
        zpc = row[10].strip() if len(row)>10 else '空'
        if not zpc: zpc = '空'

        # 未来LOOKAHEAD天
        end = min(i+1+LOOKAHEAD, n)
        za_vals = []
        retouch = False
        for j in range(i+1, end):
            za = to_f(rows[j][13]) if len(rows[j])>13 else None
            if za is not None: za_vals.append(za)
            sfj = rows[j][30].strip() if len(rows[j])>30 else ''
            if sfj and sfj[-1] == 'A': retouch = True

        # 再次上破DJA：未来10天内出现日ZA从<=0变为>0
        broke_up = False
        prev = to_f(row[13]) if len(row)>13 else None
        for za in za_vals:
            if prev is not None and prev <= 0 and za > 0:
                broke_up = True
                break
            prev = za
        # 站稳DJA：未来10天内日ZA>0天数>=5
        stand = sum(1 for za in za_vals if za > 0) >= 5

        zp[zpc][0] += 1
        if broke_up: zp[zpc][1] += 1
        if stand: zp[zpc][2] += 1
        if retouch: zp[zpc][3] += 1

print(f'高波池文件: {files_core}')
print()
print('='*80)
print('未触顶日具体柱排 × 未来10天 上破DJA/站稳DJA/触顶')
print('='*80)
print(f'{"柱排":<28}{"n":>9}{"上破DJA":>9}{"站稳DJA":>9}{"触顶":>8}')
for k, (n, up, st, rt) in sorted(zp.items(), key=lambda x: -x[1][0]):
    if n < 5000: continue
    print(f'{k:<28}{n:>9,}{up/n*100:>8.1f}%{st/n*100:>8.1f}%{rt/n*100:>7.1f}%')
