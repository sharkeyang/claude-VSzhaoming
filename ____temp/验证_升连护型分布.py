# -*- coding: utf-8 -*-
"""
验证DXZC>0时升连位置DXAB护型分布（高波池）
====================================================
用户猜想：DXZC>0时，升连发生位置对应的DXAB护型，甲最多，乙(DXZA>0)次之。

验证：
1. DXZC>0时，升连（柱排含'升.尾连'）位置各护型分布
2. 按DXCD划分区域后，各护型分布
3. 各护型的P(≥3%)
"""
import csv, os, sys, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

hxmap = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def to_f(v):
    try: return float(v)
    except: return None

def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

def parse_dxab_val(dxab):
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    return int(m.group(1)) if m else None

# ============ 统计容器 ============
# 1. DXZC>0时升连位置各护型分布
q1 = defaultdict(lambda: [0,0,0.0])  # key: 护型 -> [n, hr>=3, sum_hr]
# 2. 按DXCD划分
q2 = defaultdict(lambda: [0,0,0.0])  # key: DXCD|护型 -> [n, hr>=3, sum_hr]
# 3. 各护型P(≥3%)

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
        if len(row) <= 26: continue
        hr = to_f(row[26]); zc = to_f(row[14])
        if hr is None or zc is None: continue
        if hr < -50 or hr > 50: continue
        if zc <= 0: continue  # 只统计DXZC>0
        zp = row[10].strip()
        # 升连 = 柱排含'升.尾连'
        if '升.尾连' not in zp: continue
        hx = parse_hx(row[9].strip())
        if not hx: continue
        cd = row[8].strip()
        # 1. 各护型分布
        q1[hx][0]+=1; q1[hx][1]+= (1 if hr>=3 else 0); q1[hx][2]+=hr
        # 2. 按DXCD划分
        q2[f'{cd}|{hx}'][0]+=1; q2[f'{cd}|{hx}'][1]+= (1 if hr>=3 else 0); q2[f'{cd}|{hx}'][2]+=hr

print(f'高波池文件: {files_core}')
print()

# ===== 1输出 =====
print('='*75)
print('【1】DXZC>0时升连位置各护型分布')
print('='*75)
total = sum(v[0] for v in q1.values())
print(f'{"护型":<6} {"n":>10} {"占比":>8} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*45)
for hx in ['甲','乙','己','戊','丙','丁']:
    if hx in q1:
        s = q1[hx]
        if s[0] >= 100:
            print(f'{hx:<6} {s[0]:>10,} {s[0]/total*100:>7.2f}% {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print(f'{"全部":<6} {total:>10,} {100:>7.2f}%')
print()

# ===== 2输出 =====
print('='*75)
print('【2】DXZC>0时升连位置各护型分布 × DXCD')
print('='*75)
for cd in ['上','忐','忠','中','忑','下']:
    cd_total = sum(v[0] for k,v in q2.items() if k.startswith(f'{cd}|'))
    if cd_total == 0: continue
    print(f'--- DXCD={cd}（升连样本 {cd_total:,}）---')
    print(f'{"护型":<6} {"n":>10} {"占比":>8} {"P(≥3%)":>8}')
    print('-'*40)
    for hx in ['甲','乙','己','戊','丙','丁']:
        key = f'{cd}|{hx}'
        if key in q2:
            s = q2[key]
            if s[0] >= 100:
                print(f'{hx:<6} {s[0]:>10,} {s[0]/cd_total*100:>7.2f}% {s[1]/s[0]*100:>7.2f}%')
    print()
print()