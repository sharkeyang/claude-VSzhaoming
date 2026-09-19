# -*- coding: utf-8 -*-
"""
DXZC>25 调整模式 深入细分（第二批）
====================================================
9. 调整模式 × 再次触顶后未来5天最大高幅（≥3%/≥5%）
10. 调整模式 × 调整期内柱排类型（跌孕/跌吞/跌连/阴阳阴/升排）
11. 调整模式 × 再次触顶后未来5天继续升管率
12. 调整模式 × 再次触顶后冲高幅度均值
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

def classify_adj(rows, emas, i, retouch_idx):
    adj_len = retouch_idx - i - 1
    if adj_len == 0:
        return '0柱(次日直接触顶)', 0, []
    broke_dja = False
    broke_djb = False
    adj_zp = []
    for j in range(i+1, retouch_idx):
        za = to_f(rows[j][13]) if len(rows[j])>13 else None
        close = to_f(rows[j][1]) if len(rows[j])>1 else None
        zp = rows[j][10].strip() if len(rows[j])>10 else ''
        adj_zp.append(zp)
        if za is not None and za < 0: broke_dja = True
        if close is not None and emas[j] is not None and close < emas[j]: broke_djb = True
    if broke_djb:
        mode = '下破DJB调整'
    elif broke_dja:
        mode = '下破DJA调整'
    elif adj_len == 1:
        mode = 'DJA之上单柱调整'
    else:
        mode = 'DJA之上多柱调整'
    return mode, adj_len, adj_zp

def zp_class(zp):
    if not zp: return '空'
    if '跌孕' in zp: return '跌孕'
    if '跌吞' in zp: return '跌吞'
    if '跌连' in zp: return '跌连'
    if '阴阳阴' in zp or '人' in zp: return '阴阳阴'
    if zp.startswith('升') or zp.startswith('(升)'): return '升排'
    return '其他'

# 9. 模式 -> [n, max5>=3, max5>=5]
mode_max5 = defaultdict(lambda: [0,0,0])
# 10. 模式 -> 调整期内柱排类型计数
mode_adjzp = defaultdict(lambda: defaultdict(int))
# 11. 模式 -> [n, 未来5天继续升管]
mode_cont5 = defaultdict(lambda: [0,0])
# 12. 模式 -> [n, 次日高幅总和]
mode_avg = defaultdict(lambda: [0,0.0])

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

        mode, adj_len, adj_zp = classify_adj(rows, emas, i, retouch_idx)

        # 9. 未来5天最大高幅
        max5 = 0
        for j in range(retouch_idx, min(retouch_idx+5, n)):
            h = to_f(rows[j][26]) if len(rows[j])>26 else None
            if h is not None and h > max5: max5 = h
        mode_max5[mode][0] += 1
        if max5 >= 3: mode_max5[mode][1] += 1
        if max5 >= 5: mode_max5[mode][2] += 1

        # 10. 调整期内柱排类型
        for zp in adj_zp:
            mode_adjzp[mode][zp_class(zp)] += 1

        # 11. 未来5天继续升管（日ZA>0）
        cont5 = True
        for j in range(retouch_idx, min(retouch_idx+5, n)):
            za = to_f(rows[j][13]) if len(rows[j])>13 else None
            if za is None or za <= 0:
                cont5 = False
                break
        mode_cont5[mode][0] += 1
        if cont5: mode_cont5[mode][1] += 1

        # 12. 次日高幅均值
        nxt = to_f(rows[retouch_idx][26]) if len(rows[retouch_idx])>26 else None
        if nxt is not None:
            mode_avg[mode][0] += 1
            mode_avg[mode][1] += nxt

print(f'高波池文件: {files_core}')
print()
print('='*70)
print('【9】调整模式 × 再次触顶后未来5天最大高幅')
print('='*70)
print(f'{"模式":<20}{"n":>10}{"≥3%":>8}{"≥5%":>8}')
for mode, (n, g3, g5) in sorted(mode_max5.items(), key=lambda x: -x[1][0]):
    print(f'{mode:<20}{n:>10,}{g3/n*100:>7.1f}%{g5/n*100:>7.1f}%')

print()
print('='*70)
print('【10】调整模式 × 调整期内柱排类型')
print('='*70)
print(f'{"模式":<20}{"跌孕":>8}{"跌吞":>8}{"跌连":>8}{"阴阳阴":>8}{"升排":>8}{"其他":>8}')
for mode, zpc in sorted(mode_adjzp.items(), key=lambda x: -sum(x[1].values())):
    total = sum(zpc.values())
    if total == 0: continue
    print(f'{mode:<20}{zpc.get("跌孕",0)/total*100:>7.1f}%{zpc.get("跌吞",0)/total*100:>7.1f}%{zpc.get("跌连",0)/total*100:>7.1f}%{zpc.get("阴阳阴",0)/total*100:>7.1f}%{zpc.get("升排",0)/total*100:>7.1f}%{zpc.get("其他",0)/total*100:>7.1f}%')

print()
print('='*70)
print('【11】调整模式 × 再次触顶后未来5天继续升管率')
print('='*70)
print(f'{"模式":<20}{"n":>10}{"5天继续升管":>12}')
for mode, (n, cont) in sorted(mode_cont5.items(), key=lambda x: -x[1][0]):
    print(f'{mode:<20}{n:>10,}{cont/n*100:>11.1f}%')

print()
print('='*70)
print('【12】调整模式 × 再次触顶后次日高幅均值')
print('='*70)
print(f'{"模式":<20}{"n":>10}{"次日高幅均值":>12}')
for mode, (n, s) in sorted(mode_avg.items(), key=lambda x: -x[1][0]):
    print(f'{mode:<20}{n:>10,}{s/n:>11.2f}%')
