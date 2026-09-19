# -*- coding: utf-8 -*-
"""
DXZC>25 调整模式 深入细分（第三批）
====================================================
聚焦"调整深度"核心变量的交叉分析 + 更长持有期：
13. 调整深度 × 未来5天继续升管率
14. 调整深度 × 护型
15. 调整深度 × 未来10天最大高幅
16. 调整深度 × 再次触顶后未来5天最大高幅
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

hxmap = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}
def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

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
    """返回调整深度分档"""
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

# 13. 深度 -> [n, 5天继续升管]
depth_cont5 = defaultdict(lambda: [0,0])
# 14. 深度 -> 护型计数
depth_hx = defaultdict(lambda: defaultdict(int))
# 15. 深度 -> [n, 10天最大高幅>=3, >=5]
depth_max10 = defaultdict(lambda: [0,0,0])
# 16. 深度 -> [n, 5天最大高幅>=3, >=5]
depth_max5 = defaultdict(lambda: [0,0,0])

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
        # 护型
        dxab = row[9].strip() if len(row)>9 else ''
        hx = parse_hx(dxab)

        # 13. 5天继续升管
        cont5 = True
        for j in range(retouch_idx, min(retouch_idx+5, n)):
            za = to_f(rows[j][13]) if len(rows[j])>13 else None
            if za is None or za <= 0:
                cont5 = False
                break
        depth_cont5[d][0] += 1
        if cont5: depth_cont5[d][1] += 1

        # 14. 护型
        if hx: depth_hx[d][hx] += 1

        # 15. 10天最大高幅
        max10 = 0
        for j in range(retouch_idx, min(retouch_idx+10, n)):
            h = to_f(rows[j][26]) if len(rows[j])>26 else None
            if h is not None and h > max10: max10 = h
        depth_max10[d][0] += 1
        if max10 >= 3: depth_max10[d][1] += 1
        if max10 >= 5: depth_max10[d][2] += 1

        # 16. 5天最大高幅
        max5 = 0
        for j in range(retouch_idx, min(retouch_idx+5, n)):
            h = to_f(rows[j][26]) if len(rows[j])>26 else None
            if h is not None and h > max5: max5 = h
        depth_max5[d][0] += 1
        if max5 >= 3: depth_max5[d][1] += 1
        if max5 >= 5: depth_max5[d][2] += 1

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('【13】调整深度 × 未来5天继续升管率')
print('='*70)
print(f'{"深度":<16}{"n":>10}{"5天继续升管":>12}')
for d in ['未下破DJB','下破DJB<2%','下破DJB2-5%','下破DJB5-10%','下破DJB≥10%']:
    if d in depth_cont5:
        n, cont = depth_cont5[d]
        print(f'{d:<16}{n:>10,}{cont/n*100:>11.1f}%')

print()
print('='*70)
print('【14】调整深度 × 护型')
print('='*70)
print(f'{"深度":<16}{"甲":>8}{"乙":>8}{"己":>8}{"戊":>8}{"丙":>8}{"丁":>8}')
for d in ['未下破DJB','下破DJB<2%','下破DJB2-5%','下破DJB5-10%','下破DJB≥10%']:
    if d in depth_hx:
        hxc = depth_hx[d]
        total = sum(hxc.values())
        if total == 0: continue
        print(f'{d:<16}{hxc.get("甲",0)/total*100:>7.1f}%{hxc.get("乙",0)/total*100:>7.1f}%{hxc.get("己",0)/total*100:>7.1f}%{hxc.get("戊",0)/total*100:>7.1f}%{hxc.get("丙",0)/total*100:>7.1f}%{hxc.get("丁",0)/total*100:>7.1f}%')

print()
print('='*70)
print('【15】调整深度 × 未来10天最大高幅')
print('='*70)
print(f'{"深度":<16}{"n":>10}{"≥3%":>8}{"≥5%":>8}')
for d in ['未下破DJB','下破DJB<2%','下破DJB2-5%','下破DJB5-10%','下破DJB≥10%']:
    if d in depth_max10:
        n, g3, g5 = depth_max10[d]
        print(f'{d:<16}{n:>10,}{g3/n*100:>7.1f}%{g5/n*100:>7.1f}%')

print()
print('='*70)
print('【16】调整深度 × 未来5天最大高幅')
print('='*70)
print(f'{"深度":<16}{"n":>10}{"≥3%":>8}{"≥5%":>8}')
for d in ['未下破DJB','下破DJB<2%','下破DJB2-5%','下破DJB5-10%','下破DJB≥10%']:
    if d in depth_max5:
        n, g3, g5 = depth_max5[d]
        print(f'{d:<16}{n:>10,}{g3/n*100:>7.1f}%{g5/n*100:>7.1f}%')
