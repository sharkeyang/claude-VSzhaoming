# -*- coding: utf-8 -*-
"""
DXZC>25 调整模式 深入细分（第五批）
====================================================
验证"柱排是调整模式中最重要的指标"：
比较调整期最后一柱的 柱排/等型/顶型 对再次触顶后P3的区分度。
20. 调整期最后一柱柱排 × P3
21. 调整期最后一柱等型 × P3
22. 调整期最后一柱顶型(核心) × P3
23. 调整深度 × 调整期最后一柱柱排 × P3
"""
import csv, os, sys, re
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

def depth_class(rows, emas, i, retouch_idx):
    broke_djb = False
    min_depth = 0
    for j in range(i+1, retouch_idx):
        close = to_f(rows[j][1]) if len(rows[j])>1 else None
        if close is not None and emas[j] is not None and close < emas[j]:
            broke_djb = True
            depth = (emas[j] - close) / emas[j] * 100
            if depth > min_depth: min_depth = depth
    if not broke_djb:
        return '未下破DJB'
    if min_depth < 2: return '下破DJB<2%'
    if min_depth < 5: return '下破DJB2-5%'
    if min_depth < 10: return '下破DJB5-10%'
    return '下破DJB≥10%'

def zp_class(zp):
    if not zp: return '空'
    if '跌孕' in zp: return '跌孕'
    if '跌吞' in zp: return '跌吞'
    if '跌连' in zp: return '跌连'
    if '阴阳阴' in zp or '人' in zp: return '阴阳阴'
    if zp.startswith('升') or zp.startswith('(升)'): return '升排'
    return '其他'

def ding_class(ding):
    """顶型核心分类（去前缀 _/K/L/_K/_L）"""
    if not ding: return '空'
    d = ding.strip()
    # 去前缀
    for p in ['_K','_L','K','L','_']:
        if d.startswith(p):
            d = d[len(p):]
            break
    # 核心顶型
    if '龙' in d: return '龙'
    if '虎' in d: return '虎'
    if '雀' in d: return '雀'
    if '篪' in d: return '篪'
    if '武' in d: return '武'
    if '非' in d: return '非'
    return '其他'

# 20. 柱排 -> [n, p3]
zp_p3 = defaultdict(lambda: [0,0])
# 21. 等型 -> [n, p3]
den_p3 = defaultdict(lambda: [0,0])
# 22. 顶型 -> [n, p3]
ding_p3 = defaultdict(lambda: [0,0])
# 23. 深度 -> 柱排 -> [n, p3]
depth_zp = defaultdict(lambda: defaultdict(lambda: [0,0]))

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
        retouch_idx = None
        for j in range(i+1, min(i+1+LOOKAHEAD, n)):
            sfj = rows[j][30].strip() if len(rows[j])>30 else ''
            if sfj and sfj[-1] == 'A':
                retouch_idx = j
                break
        if retouch_idx is None: continue
        if retouch_idx == i+1: continue  # 0柱无调整期，跳过（本批聚焦调整期最后一柱）

        d = depth_class(rows, emas, i, retouch_idx)
        # 调整期最后一柱
        last_idx = retouch_idx - 1
        zp = rows[last_idx][10].strip() if len(rows[last_idx])>10 else ''
        den = rows[last_idx][44].strip() if len(rows[last_idx])>44 else ''
        ding = rows[last_idx][43].strip() if len(rows[last_idx])>43 else ''
        # 再次触顶后P3
        nxt = to_f(rows[retouch_idx][26]) if len(rows[retouch_idx])>26 else None
        p3_hit = (nxt is not None and nxt >= 3)

        zpc = zp_class(zp)
        dc = den if den else '空'
        dgc = ding_class(ding)

        zp_p3[zpc][0] += 1
        if p3_hit: zp_p3[zpc][1] += 1
        den_p3[dc][0] += 1
        if p3_hit: den_p3[dc][1] += 1
        ding_p3[dgc][0] += 1
        if p3_hit: ding_p3[dgc][1] += 1
        depth_zp[d][zpc][0] += 1
        if p3_hit: depth_zp[d][zpc][1] += 1

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('【20】调整期最后一柱柱排 × P3（区分度）')
print('='*70)
print(f'{"柱排":<10}{"n":>10}{"P3":>8}')
for k, (n, p3) in sorted(zp_p3.items(), key=lambda x: -x[1][0]):
    if n < 1000: continue
    print(f'{k:<10}{n:>10,}{p3/n*100:>7.1f}%')

print()
print('='*70)
print('【21】调整期最后一柱等型 × P3（区分度）')
print('='*70)
print(f'{"等型":<10}{"n":>10}{"P3":>8}')
for k, (n, p3) in sorted(den_p3.items(), key=lambda x: -x[1][0]):
    if n < 1000: continue
    print(f'{k:<10}{n:>10,}{p3/n*100:>7.1f}%')

print()
print('='*70)
print('【22】调整期最后一柱顶型 × P3（区分度）')
print('='*70)
print(f'{"顶型":<10}{"n":>10}{"P3":>8}')
for k, (n, p3) in sorted(ding_p3.items(), key=lambda x: -x[1][0]):
    if n < 1000: continue
    print(f'{k:<10}{n:>10,}{p3/n*100:>7.1f}%')

print()
print('='*70)
print('【23】调整深度 × 调整期最后一柱柱排 × P3')
print('='*70)
print(f'{"深度":<16}{"升排P3":>10}{"阴阳阴P3":>10}{"其他P3":>10}')
for d in ['未下破DJB','下破DJB<2%','下破DJB2-5%','下破DJB5-10%','下破DJB≥10%']:
    if d in depth_zp:
        row = depth_zp[d]
        sp = row.get('升排',[0,0])
        yy = row.get('阴阳阴',[0,0])
        qt = row.get('其他',[0,0])
        spct = f'{sp[1]/sp[0]*100:.1f}%' if sp[0] else '-'
        yyct = f'{yy[1]/yy[0]*100:.1f}%' if yy[0] else '-'
        qtct = f'{qt[1]/qt[0]*100:.1f}%' if qt[0] else '-'
        print(f'{d:<16}{spct:>10}{yyct:>10}{qtct:>10}')
