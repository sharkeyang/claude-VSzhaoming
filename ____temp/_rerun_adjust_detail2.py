# -*- coding: utf-8 -*-
"""
DXZC>25 调整模式 更多细分
====================================================
6. 调整深度（下破DJB的深度分档）
7. 按 DXZC 区间（25-30/30-40/40+）
8. 再次触顶后未来3天继续触顶率
9. 调整模式 × 是否下破DJB（下破DJB vs 未下破DJB 的P3对比）
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

def ema12(prices):
    if not prices: return []
    k = 2/13
    ema = [prices[0]]
    for p in prices[1:]:
        ema.append(p*k + ema[-1]*(1-k))
    return ema

# 6. 调整深度（下破DJB的深度分档）-> 深度档 -> [n, p3]
depth_p3 = defaultdict(lambda: [0,0])
# 7. DXZC区间 -> 模式 -> [n, p3]
zc_mode = defaultdict(lambda: defaultdict(lambda: [0,0]))
# 8. 再次触顶后未来3天继续触顶率 -> 模式 -> [n, cont3]
mode_cont3 = defaultdict(lambda: [0,0])
# 9. 下破DJB vs 未下破DJB -> [n, p3]
djb_p3 = defaultdict(lambda: [0,0])

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
    prices = []
    for row in rows:
        p = to_f(row[1]) if len(row)>1 else None
        prices.append(p if p is not None else 0)
    emas = ema12(prices)

    for i in range(n):
        row = rows[i]
        if len(row) < 31: continue
        zc = to_f(row[14])
        if zc is None or zc <= 25: continue
        sf = row[30].strip()
        if not sf or sf[-1] == 'A': continue
        # 找未来LOOKAHEAD天内再次触顶
        retouch_idx = None
        for j in range(i+1, min(i+1+LOOKAHEAD, n)):
            sfj = rows[j][30].strip() if len(rows[j])>30 else ''
            if sfj and sfj[-1] == 'A':
                retouch_idx = j
                break
        if retouch_idx is None: continue

        # 调整期是否下破DJB
        broke_djb = False
        min_depth = 0  # 最大下破深度（%）
        for j in range(i+1, retouch_idx):
            close = to_f(rows[j][1]) if len(rows[j])>1 else None
            if close is not None and emas[j] is not None and close < emas[j]:
                broke_djb = True
                depth = (emas[j] - close) / emas[j] * 100
                if depth > min_depth: min_depth = depth
        # 再次触顶后P3
        nxt = to_f(rows[retouch_idx][26]) if len(rows[retouch_idx])>26 else None
        p3_hit = (nxt is not None and nxt >= 3)

        # 6. 调整深度分档
        if broke_djb:
            if min_depth < 2: d = '下破DJB<2%'
            elif min_depth < 5: d = '下破DJB2-5%'
            elif min_depth < 10: d = '下破DJB5-10%'
            else: d = '下破DJB≥10%'
            depth_p3[d][0] += 1
            if p3_hit: depth_p3[d][1] += 1
        else:
            depth_p3['未下破DJB'][0] += 1
            if p3_hit: depth_p3['未下破DJB'][1] += 1

        # 7. DXZC区间
        if zc <= 30: zseg = 'ZC25-30'
        elif zc <= 40: zseg = 'ZC30-40'
        else: zseg = 'ZC40+'
        if broke_djb: m = '下破DJB'
        else: m = '未下破DJB'
        zc_mode[zseg][m][0] += 1
        if p3_hit: zc_mode[zseg][m][1] += 1

        # 8. 再次触顶后未来3天继续触顶
        cont3 = 0
        for j in range(retouch_idx+1, min(retouch_idx+4, n)):
            sfj = rows[j][30].strip() if len(rows[j])>30 else ''
            if sfj and sfj[-1] == 'A': cont3 += 1
        mode_cont3['下破DJB' if broke_djb else '未下破DJB'][0] += 1
        if cont3 >= 1: mode_cont3['下破DJB' if broke_djb else '未下破DJB'][1] += 1

        # 9. 下破DJB vs 未下破DJB
        djb_p3['下破DJB' if broke_djb else '未下破DJB'][0] += 1
        if p3_hit: djb_p3['下破DJB' if broke_djb else '未下破DJB'][1] += 1

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('【6】调整深度（下破DJB的深度分档）× P3')
print('='*70)
print(f'{"深度":<18}{"n":>10}{"P3":>8}')
for d, (n, p3) in sorted(depth_p3.items(), key=lambda x: -x[1][0]):
    print(f'{d:<18}{n:>10,}{p3/n*100:>7.1f}%')

print()
print('='*70)
print('【7】DXZC区间 × 是否下破DJB × P3')
print('='*70)
print(f'{"ZC区间":<10}{"模式":<12}{"n":>10}{"P3":>8}')
for zseg in ['ZC25-30','ZC30-40','ZC40+']:
    for m in ['下破DJB','未下破DJB']:
        if m in zc_mode[zseg]:
            n, p3 = zc_mode[zseg][m]
            print(f'{zseg:<10}{m:<12}{n:>10,}{p3/n*100:>7.1f}%')

print()
print('='*70)
print('【8】再次触顶后未来3天继续触顶率')
print('='*70)
print(f'{"模式":<12}{"n":>10}{"3天继续触顶率":>12}')
for m, (n, cont) in sorted(mode_cont3.items(), key=lambda x: -x[1][0]):
    print(f'{m:<12}{n:>10,}{cont/n*100:>11.1f}%')

print()
print('='*70)
print('【9】下破DJB vs 未下破DJB × P3')
print('='*70)
print(f'{"模式":<12}{"n":>10}{"P3":>8}')
for m, (n, p3) in sorted(djb_p3.items(), key=lambda x: -x[1][0]):
    print(f'{m:<12}{n:>10,}{p3/n*100:>7.1f}%')
