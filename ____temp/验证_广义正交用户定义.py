# -*- coding: utf-8 -*-
"""
验证用户正确的广义正交护型定义：
DXAB广义正交护型 = 可能有负转正（己、戊(DXZA>0)）+ 正交（甲、乙(DXZA>0)、乙(DXZA<0)）+ 可能由正转负（丙）
= 己、戊(ZA>0)、甲、乙(ZA>0)、乙(ZA<0)、丙
非广义 = 戊(ZA<0)、丁

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

def to_f(v):
    try: return float(v)
    except: return None

def is_广义(hx, za):
    """用户定义：己、戊(ZA>0)、甲、乙(ZA>0)、乙(ZA<0)、丙"""
    if hx == '己': return True
    if hx == '戊': return za > 0
    if hx == '甲': return True  # 甲只有ZA>0
    if hx == '乙': return True  # 乙含ZA>0和ZA<0
    if hx == '丙': return True
    return False

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0,0,0.0])
# 各护型×ZA×ZC
stats_hx = defaultdict(lambda: [0,0])

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
                za = to_f(row[13])
                zc = to_f(row[14])
                hr = to_f(row[26])
                if zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not hx: continue
                if zc > 0:
                    if is_广义(hx, za):
                        stats['广义'][0]+=1; stats['广义'][1]+= (1 if hr>=3 else 0); stats['广义'][2]+=hr
                    else:
                        stats['非广义'][0]+=1; stats['非广义'][1]+= (1 if hr>=3 else 0); stats['非广义'][2]+=hr
                    stats['基线'][0]+=1; stats['基线'][1]+= (1 if hr>=3 else 0); stats['基线'][2]+=hr
                    # 各护型×ZA
                    za_key = 'ZA>0' if za>0 else ('ZA=0' if za==0 else 'ZA<0')
                    stats_hx[(hx, za_key)][0]+=1; stats_hx[(hx, za_key)][1]+= (1 if hr>=3 else 0)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('='*70)
print('广义正交护型（用户定义）vs 非广义 vs 基线（DXZC>0）')
print('='*70)
for k in ['广义','非广义','基线']:
    s = stats[k]
    pct = s[0]/stats['基线'][0]*100
    print(f'  {k}: n={s[0]:,}, P(≥3%)={s[1]/s[0]*100:.2f}%, 平均高幅={s[2]/s[0]:.2f}%, 占比={pct:.2f}%')

print()
print('='*70)
print('各护型×ZA 次日冲高率（DXZC>0）')
print('='*70)
print(f'{"护型":<6} {"ZA":<6} {"n":>10} {"P(≥3%)":>8}')
print('-'*45)
for hx in ['甲','乙','己','戊','丙','丁']:
    for za_key in ['ZA>0','ZA=0','ZA<0']:
        key = (hx, za_key)
        if key in stats_hx:
            s = stats_hx[key]
            if s[0] >= 500:
                print(f'{hx:<6} {za_key:<6} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}%')
