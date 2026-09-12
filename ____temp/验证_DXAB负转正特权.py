# -*- coding: utf-8 -*-
"""
验证DXAB由负转正后的特权（高波池）
====================================================
用户假设：DXAB由负转正（BTAB从<0转为>0）后，即使遇到阴柱回调至DJA附近，
也会再次上升，不会马上导致DXAB负交。

分情况：全局、DXZE>0、DXZE≤0

验证：
1. DXAB由负转正后，遇到阴柱回调至DJA附近（日ZA=1/0/-1），后续是否上升
2. 后续N天内是否转负（BTAB<0）
3. 分DXZE>0/DXZE≤0
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

def parse_dxab(dxab):
    if len(dxab) < 3: return ('','','',None)
    hx = hxmap.get(dxab[0], '')
    zj = dxab[2]
    dirch = dxab[3] if len(dxab) > 3 else ''
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    val = int(m.group(1)) if m else None
    return (hx, zj, dirch, val)

# ============ 统计容器 ============
# 1. DXAB由负转正后，遇到阴柱回调至DJA附近（日ZA=1/0/-1），后续是否上升
# 场景：找到DXAB由负转正点，然后在其后找第一个"阴柱回调至DJA附近"（日ZA<=1且阴柱），看后续
q1 = defaultdict(lambda: [0,0,0.0])  # key: 情况 -> [n, 后续上升(次日hr>=3), sum_hr]
# 2. 后续N天内是否转负
q2 = defaultdict(lambda: [0,0])  # key: 情况|N天 -> [n, 转负]
# 3. 回调至DJA附近后，是否再次上升（后续3天内有hr>=3）
q3 = defaultdict(lambda: [0,0])  # key: 情况 -> [n, 3天内上升]

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
    dxabs = [parse_dxab(rows[i][9].strip()) for i in range(n)]
    zas = [to_f(rows[i][13]) for i in range(n)]
    zes = [to_f(rows[i][15]) for i in range(n)]
    hrs = [to_f(rows[i][26]) for i in range(n)]
    zfs = [to_f(rows[i][5]) for i in range(n)]

    # 找DXAB由负转正点
    for i in range(1, n):
        hx_prev, zj_prev, dirch_prev, val_prev = dxabs[i-1]
        hx, zj, dirch, val = dxabs[i]
        if val is None or val_prev is None: continue
        if not (val_prev < 0 and val > 0): continue  # 由负转正
        # 在其后找第一个"阴柱回调至DJA附近"（日ZA<=1且阴柱）
        for j in range(i, n):
            za = zas[j]
            zf = zfs[j]
            if za is None or zf is None: continue
            if za <= 1 and zf < 0:  # 阴柱回调至DJA附近
                # 记录后续
                hr = hrs[j]
                ze = zes[j]
                if hr is None: break
                if hr < -50 or hr > 50: break
                # 分情况
                if ze is None:
                    case = '全局'
                elif ze > 0:
                    case = 'DXZE>0'
                else:
                    case = 'DXZE≤0'
                # 1. 次日冲高
                q1[case][0]+=1; q1[case][1]+= (1 if hr>=3 else 0); q1[case][2]+=hr
                # 2. 后续N天内转负
                for N in [1,2,3,5]:
                    turned = False
                    for k in range(1, N+1):
                        if j+k >= n: break
                        hx2, zj2, dirch2, val2 = dxabs[j+k]
                        if val2 is not None and val2 < 0:
                            turned = True; break
                    if turned:
                        q2[f'{case}|{N}天'][0]+=1; q2[f'{case}|{N}天'][1]+=1
                    else:
                        q2[f'{case}|{N}天'][0]+=1
                # 3. 后续3天内是否上升（hr>=3）
                rose = False
                for k in range(1, 4):
                    if j+k >= n: break
                    hr2 = hrs[j+k]
                    if hr2 is not None and hr2 >= 3:
                        rose = True; break
                if rose:
                    q3[f'{case}'][0]+=1; q3[f'{case}'][1]+=1
                else:
                    q3[f'{case}'][0]+=1
                break  # 只找第一个回调点

print(f'高波池文件: {files_core}')
print()

def show(d, title, keys, is_q2=False):
    print('='*75)
    print(f'【{title}】')
    print('='*75)
    if is_q2:
        print(f'{"类别":<16} {"n":>10} {"转负":>10} {"转负率":>8}')
        print('-'*50)
        for k in keys:
            if k in d:
                s = d[k]
                if s[0] >= 100:
                    print(f'{k:<16} {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
    else:
        print(f'{"类别":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
        print('-'*45)
        for k in keys:
            if k in d:
                s = d[k]
                if s[0] >= 100:
                    print(f'{k:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
    print()

show(q1, '1. DXAB负转正后阴柱回调至DJA附近，次日冲高率', ['全局','DXZE>0','DXZE≤0'])
show(q2, '2. 回调后N天内转负概率', ['全局|1天','全局|2天','全局|3天','全局|5天','DXZE>0|1天','DXZE>0|2天','DXZE>0|3天','DXZE>0|5天','DXZE≤0|1天','DXZE≤0|2天','DXZE≤0|3天','DXZE≤0|5天'], is_q2=True)
show(q3, '3. 回调后3天内是否再次上升', ['全局','DXZE>0','DXZE≤0'])