# -*- coding: utf-8 -*-
"""
DXZC>25 调整模式 深入细分（第六批）
====================================================
用户洞察：柱排可能决定"调整后是否触顶"（触顶概率），而非"触顶后冲高幅度"。
分析未触顶日柱排/等型/顶型 × 未来10天是否触顶（触顶概率）。
24. 未触顶日柱排 × 未来10天触顶概率
25. 未触顶日等型 × 未来10天触顶概率
26. 未触顶日顶型 × 未来10天触顶概率
27. 未触顶日柱排 × 未来10天触顶概率 × 触顶后P3
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

def zp_class(zp):
    if not zp: return '空'
    if '跌孕' in zp: return '跌孕'
    if '跌吞' in zp: return '跌吞'
    if '跌连' in zp: return '跌连'
    if '阴阳阴' in zp or '人' in zp: return '阴阳阴'
    if zp.startswith('升') or zp.startswith('(升)'): return '升排'
    return '其他'

def ding_class(ding):
    if not ding: return '空'
    d = ding.strip()
    for p in ['_K','_L','K','L','_']:
        if d.startswith(p):
            d = d[len(p):]
            break
    if '龙' in d: return '龙'
    if '虎' in d: return '虎'
    if '雀' in d: return '雀'
    if '篪' in d: return '篪'
    if '武' in d: return '武'
    if '非' in d: return '非'
    return '其他'

# 24. 柱排 -> [n, 触顶数]
zp_touch = defaultdict(lambda: [0,0])
# 25. 等型 -> [n, 触顶数]
den_touch = defaultdict(lambda: [0,0])
# 26. 顶型 -> [n, 触顶数]
ding_touch = defaultdict(lambda: [0,0])
# 27. 柱排 -> 触顶后P3
zp_touch_p3 = defaultdict(lambda: [0,0])

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
        if not sf or sf[-1] == 'A': continue  # 当日未触顶
        # 未触顶日柱排/等型/顶型
        zp = row[10].strip() if len(row)>10 else ''
        den = row[44].strip() if len(row)>44 else ''
        ding = row[43].strip() if len(row)>43 else ''
        zpc = zp_class(zp)
        dc = den if den else '空'
        dgc = ding_class(ding)

        # 未来10天是否触顶
        retouch_idx = None
        for j in range(i+1, min(i+1+LOOKAHEAD, n)):
            sfj = rows[j][30].strip() if len(rows[j])>30 else ''
            if sfj and sfj[-1] == 'A':
                retouch_idx = j
                break
        touched = (retouch_idx is not None)

        zp_touch[zpc][0] += 1
        if touched: zp_touch[zpc][1] += 1
        den_touch[dc][0] += 1
        if touched: den_touch[dc][1] += 1
        ding_touch[dgc][0] += 1
        if touched: ding_touch[dgc][1] += 1

        # 触顶后P3
        if touched:
            nxt = to_f(rows[retouch_idx][26]) if len(rows[retouch_idx])>26 else None
            zp_touch_p3[zpc][0] += 1
            if nxt is not None and nxt >= 3: zp_touch_p3[zpc][1] += 1

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('【24】未触顶日柱排 × 未来10天触顶概率')
print('='*70)
print(f'{"柱排":<10}{"n":>10}{"触顶概率":>10}')
for k, (n, t) in sorted(zp_touch.items(), key=lambda x: -x[1][0]):
    if n < 1000: continue
    print(f'{k:<10}{n:>10,}{t/n*100:>9.1f}%')

print()
print('='*70)
print('【25】未触顶日等型 × 未来10天触顶概率')
print('='*70)
print(f'{"等型":<10}{"n":>10}{"触顶概率":>10}')
for k, (n, t) in sorted(den_touch.items(), key=lambda x: -x[1][0]):
    if n < 1000: continue
    print(f'{k:<10}{n:>10,}{t/n*100:>9.1f}%')

print()
print('='*70)
print('【26】未触顶日顶型 × 未来10天触顶概率')
print('='*70)
print(f'{"顶型":<10}{"n":>10}{"触顶概率":>10}')
for k, (n, t) in sorted(ding_touch.items(), key=lambda x: -x[1][0]):
    if n < 1000: continue
    print(f'{k:<10}{n:>10,}{t/n*100:>9.1f}%')

print()
print('='*70)
print('【27】未触顶日柱排 × 触顶后P3（仅触顶样本）')
print('='*70)
print(f'{"柱排":<10}{"n":>10}{"P3":>8}')
for k, (n, p3) in sorted(zp_touch_p3.items(), key=lambda x: -x[1][0]):
    if n < 1000: continue
    print(f'{k:<10}{n:>10,}{p3/n*100:>7.1f}%')
