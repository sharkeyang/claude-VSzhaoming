# -*- coding: utf-8 -*-
"""
审计C6文档5.3.3位置决策表（高波池，H2口径）
====================================================
用BT连阳列[44]验证C6文档5.3.3的所有关键数据点（H2=下日高≥2%）
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

# ============ 统计容器 ============
# 用BT连阳列[44]验证C6文档5.3.3位置决策表
q = defaultdict(lambda: [0,0,0.0])  # key: 位置 -> [n, h2>=2, sum_hr]

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
        if len(row) <= 44: continue
        hr = to_f(row[26]); zc = to_f(row[14])
        if hr is None or zc is None: continue
        if hr < -50 or hr > 50: continue
        等型 = row[44].strip()
        hx = parse_hx(row[9].strip())
        if not hx: continue
        zc_key = 'ZC>0' if zc > 0 else 'ZC<0'
        key = f'{等型}+{zc_key}+{hx}'
        q[key][0]+=1; q[key][1]+= (1 if hr>=2 else 0); q[key][2]+=hr

print(f'高波池文件: {files_core}')
print()

# C6文档5.3.3的关键数据点
targets = [
    '等1+ZC>0+甲', '等2+ZC>0+乙', '等3+ZC>0+甲', '等5+ZC>0+乙',
    '等6+ZC>0+乙', '等2+ZC>0+己', '等6+ZC>0+丁', '等5+ZC>0+丙',
    '等1+ZC<0+甲', '等3+ZC>0+己',
    '等6+ZC<0+戊', '等3+ZC<0+戊', '等5+ZC<0+丁', '等5+ZC<0+戊',
    '等6+ZC<0+丁', '等6+ZC<0+丙', '等3+ZC<0+甲'
]
print('【C6文档5.3.3位置决策表验证（H2=下日高≥2%）】')
print(f'{"位置":<20} {"n":>10} {"H2(≥2%)":>8} {"C6文档H2":>8} {"C6样本":>8}')
print('-'*60)
for key in targets:
    if key in q:
        s = q[key]
        if s[0] >= 100:
            print(f'{key:<20} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {"?":>8} {"?":>8}')
print()