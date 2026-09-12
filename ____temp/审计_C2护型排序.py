# -*- coding: utf-8 -*-
"""
审计C2文档护型排序数据（高波池）
====================================================
用谕组日CSV验证C2文档的护型排序数据（DXZC>0）
关键数据点：今均涨幅/今涨率/次高>3%
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
# 用谕组日CSV验证C2文档护型排序（DXZC>0）
q = defaultdict(lambda: [0,0,0.0,0.0])  # key: 护型|ZA -> [n, 今涨率(涨幅>0), 今均涨幅, 次高>3%]

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
        zf = to_f(row[5]); zc = to_f(row[14]); za = to_f(row[13]); hr = to_f(row[26])
        if zf is None or zc is None or za is None or hr is None: continue
        if zc <= 0: continue  # 只统计DXZC>0
        if hr < -50 or hr > 50: continue
        hx = parse_hx(row[9].strip())
        if not hx: continue
        # 乙/戊按ZA拆分
        if hx in ('乙','戊'):
            key = f'{hx}(ZA>0)' if za > 0 else f'{hx}(ZA≤0)'
        else:
            key = hx
        q[key][0]+=1
        if zf > 0: q[key][1]+=1
        q[key][2]+=zf
        if hr >= 3: q[key][3]+=1

print(f'高波池文件: {files_core}')
print()

print('【C2文档护型排序验证（DXZC>0）】')
print(f'{"护型":<12} {"n":>10} {"今涨率":>8} {"今均涨幅":>8} {"次高>3%":>8}')
print('-'*50)
for key in ['甲','乙(ZA>0)','己','戊(ZA>0)','丁','乙(ZA≤0)','丙','戊(ZA≤0)']:
    if key in q:
        s = q[key]
        if s[0] >= 100:
            print(f'{key:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}% {s[3]/s[0]*100:>7.2f}%')
print()