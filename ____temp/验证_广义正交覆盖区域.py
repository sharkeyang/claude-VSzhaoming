# -*- coding: utf-8 -*-
"""
问题2补充验证：广义正交护型作为"覆盖上涨区域"的框架
核心逻辑：广义正交护型覆盖DXZC>0的97.25%，先划定可能上涨的区域，再在其中找机会更有把握。

磁盘CSV列序：8=DXCD, 9=DXAB, 13=日ZA, 14=日ZC, 15=日ZE, 26=次日高幅
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

护型映射 = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}
# 广义正交 = 甲、乙、己、戊（所有ZA）；非广义 = 丁、丙
广义 = {'甲','乙','己','戊'}

def to_f(v):
    try: return float(v)
    except: return None

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0,0,0.0])

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
            for row in r:
                if len(row) <= 26: continue
                dxab = row[9].strip()
                zc = to_f(row[14])
                hr = to_f(row[26])
                if zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx: continue
                zc_key = 'ZC>0' if zc>0 else 'ZC<=0'
                # 广义正交 vs 非广义
                if hx in 广义:
                    stats[f'广义|{zc_key}'][0]+=1; stats[f'广义|{zc_key}'][1]+= (1 if hr>=3 else 0); stats[f'广义|{zc_key}'][2]+=hr
                else:
                    stats[f'非广义|{zc_key}'][0]+=1; stats[f'非广义|{zc_key}'][1]+= (1 if hr>=3 else 0); stats[f'非广义|{zc_key}'][2]+=hr
                stats[f'基线|{zc_key}'][0]+=1; stats[f'基线|{zc_key}'][1]+= (1 if hr>=3 else 0); stats[f'基线|{zc_key}'][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('='*70)
print('广义正交护型 vs 非广义（丁/丙）vs 基线')
print('='*70)
print(f'{"类别":<8} {"ZC":<6} {"n":>10} {"P(≥3%)":>8} {"平均高幅":>8} {"占比":>8}')
print('-'*60)
for cat in ['广义','非广义','基线']:
    for zc_key in ['ZC>0','ZC<=0']:
        key = f'{cat}|{zc_key}'
        if key in stats:
            s = stats[key]
            pct = s[0]/stats[f'基线|{zc_key}'][0]*100 if stats[f'基线|{zc_key}'][0]>0 else 0
            print(f'{cat:<8} {zc_key:<6} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}% {pct:>7.1f}%')
    print('-'*60)

print()
print('='*70)
print('广义正交区域内，各护型次日冲高率（找机会）')
print('='*70)
print(f'{"护型":<6} {"ZC":<6} {"n":>10} {"P(≥3%)":>8} {"vs基线":>8}')
print('-'*55)
# 需要重新统计各护型
stats2 = defaultdict(lambda: [0,0])
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 26: continue
                dxab = row[9].strip()
                zc = to_f(row[14])
                hr = to_f(row[26])
                if zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx: continue
                if zc > 0:
                    stats2[hx][0]+=1; stats2[hx][1]+= (1 if hr>=3 else 0)
    except Exception:
        pass
base = stats['基线|ZC>0']
base_p = base[1]/base[0]*100
for hx in ['乙','甲','己','戊','丁','丙']:
    if hx in stats2:
        s = stats2[hx]
        if s[0] >= 500:
            p = s[1]/s[0]*100
            print(f'{hx:<6} {"ZC>0":<6} {s[0]:>10,} {p:>7.2f}% {p-base_p:>+7.2f}pp')
