# -*- coding: utf-8 -*-
"""
DXZC>25 调整模式 深入细分（第四批）
====================================================
17. 调整期是否伴随跌排 × P3
18. 调整深度 × 调整期是否伴随跌排 × P3
19. 调整深度 × 再次触顶后是否突破前高
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

def is_diepai(zp):
    """是否跌排"""
    if not zp: return False
    return zp.startswith('跌') or zp.startswith('(跌)')

# 17. 调整期是否伴随跌排 -> [n, p3]
diepai_p3 = defaultdict(lambda: [0,0])
# 18. 深度 -> 是否跌排 -> [n, p3]
depth_diepai = defaultdict(lambda: defaultdict(lambda: [0,0]))
# 19. 深度 -> 是否突破前高 -> [n, p3]
depth_break = defaultdict(lambda: defaultdict(lambda: [0,0]))

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

        d = depth_class(rows, emas, i, retouch_idx)
        # 调整期是否伴随跌排
        has_diepai = False
        for j in range(i+1, retouch_idx):
            zp = rows[j][10].strip() if len(rows[j])>10 else ''
            if is_diepai(zp):
                has_diepai = True
                break
        # 再次触顶后P3
        nxt = to_f(rows[retouch_idx][26]) if len(rows[retouch_idx])>26 else None
        p3_hit = (nxt is not None and nxt >= 3)

        # 17. 调整期是否伴随跌排
        diepai_p3['有跌排' if has_diepai else '无跌排'][0] += 1
        if p3_hit: diepai_p3['有跌排' if has_diepai else '无跌排'][1] += 1

        # 18. 深度 × 是否跌排
        depth_diepai[d]['有跌排' if has_diepai else '无跌排'][0] += 1
        if p3_hit: depth_diepai[d]['有跌排' if has_diepai else '无跌排'][1] += 1

        # 19. 深度 × 是否突破前高（触顶日收盘 vs 未触顶前最高收盘）
        # 未触顶前最高收盘 = max(rows[0..i] 收盘)
        prev_high = 0
        for j in range(0, i+1):
            c = to_f(rows[j][1]) if len(rows[j])>1 else None
            if c is not None and c > prev_high: prev_high = c
        touch_close = to_f(rows[retouch_idx][1]) if len(rows[retouch_idx])>1 else None
        broke_high = (touch_close is not None and touch_close > prev_high)
        depth_break[d]['突破前高' if broke_high else '未突破'][0] += 1
        if p3_hit: depth_break[d]['突破前高' if broke_high else '未突破'][1] += 1

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('【17】调整期是否伴随跌排 × P3')
print('='*70)
print(f'{"调整期":<10}{"n":>10}{"P3":>8}')
for k, (n, p3) in sorted(diepai_p3.items(), key=lambda x: -x[1][0]):
    print(f'{k:<10}{n:>10,}{p3/n*100:>7.1f}%')

print()
print('='*70)
print('【18】调整深度 × 调整期是否伴随跌排 × P3')
print('='*70)
print(f'{"深度":<16}{"有跌排n":>10}{"有跌排P3":>10}{"无跌排n":>10}{"无跌排P3":>10}')
for d in ['未下破DJB','下破DJB<2%','下破DJB2-5%','下破DJB5-10%','下破DJB≥10%']:
    if d in depth_diepai:
        yn, yp = depth_diepai[d].get('有跌排',[0,0])
        nn, np_ = depth_diepai[d].get('无跌排',[0,0])
        ypct = f'{yp/yn*100:.1f}%' if yn else '-'
        npct = f'{np_/nn*100:.1f}%' if nn else '-'
        print(f'{d:<16}{yn:>10,}{ypct:>10}{nn:>10,}{npct:>10}')

print()
print('='*70)
print('【19】调整深度 × 再次触顶后是否突破前高 × P3')
print('='*70)
print(f'{"深度":<16}{"突破n":>10}{"突破P3":>10}{"未突破n":>10}{"未突破P3":>10}')
for d in ['未下破DJB','下破DJB<2%','下破DJB2-5%','下破DJB5-10%','下破DJB≥10%']:
    if d in depth_break:
        bn, bp = depth_break[d].get('突破前高',[0,0])
        nn, np_ = depth_break[d].get('未突破',[0,0])
        bpct = f'{bp/bn*100:.1f}%' if bn else '-'
        npct = f'{np_/nn*100:.1f}%' if nn else '-'
        print(f'{d:<16}{bn:>10,}{bpct:>10}{nn:>10,}{npct:>10}')
