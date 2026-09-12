# -*- coding: utf-8 -*-
"""
验证：DXZC>0 + DXAB=甲 + 等型3 是否坚决持有（不退出）能稳定盈利
等型[44]：等3=远强
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

stats = defaultdict(lambda: [0,0,0.0])  # 等型 -> [n, P3count, sum_hr]
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
            for i,row in enumerate(rows):
                if len(row) <= 44: continue
                if not row[9].strip().startswith('a'): continue  # 甲
                zc = to_f(row[14])
                if zc is None or zc <= 0: continue  # DXZC>0
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                dx = row[44].strip()
                if not dx: continue
                s = stats[dx]
                s[0]+=1; s[1]+=(1 if hr>=3 else 0); s[2]+=hr
    except Exception: pass

print('DXZC>0 + 甲 各等型的次日冲高率')
print(f'{"等型":<8} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
for k in sorted(stats.keys()):
    s = stats[k]
    if s[0] < 1000: continue
    print(f'{k:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
