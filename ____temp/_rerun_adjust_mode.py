# -*- coding: utf-8 -*-
"""
DXZC>25 未触顶→再次触顶入管的调整模式分析
====================================================
对 DXZC>25 的样本，当日柱未触顶（上符串末位非A），未来N天内再次触顶（末位=A），
分析从"未触顶"到"再次触顶"之间的调整模式：
1. DJA之上单柱调整（调整期1柱，日ZA>0）
2. DJA之上多柱调整（调整期≥2柱，所有柱日ZA>0）
3. 下破DJA调整（调整期内有柱日ZA<0，但价格始终>EMA12）
4. 下破DJB调整（调整期内有柱价格<EMA12）
"""
import csv, os, sys, glob
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

modes = defaultdict(int)
total_untouch = 0
total_retouch = 0
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
        if not sf: continue
        if sf[-1] == 'A': continue  # 当日已触顶
        total_untouch += 1

        # 找未来LOOKAHEAD天内再次触顶
        retouch_idx = None
        for j in range(i+1, min(i+1+LOOKAHEAD, n)):
            sfj = rows[j][30].strip() if len(rows[j])>30 else ''
            if sfj and sfj[-1] == 'A':
                retouch_idx = j
                break
        if retouch_idx is None: continue
        total_retouch += 1

        # 调整期 = i+1 到 retouch_idx-1
        adj_len = retouch_idx - i - 1
        if adj_len == 0:
            mode = '0柱(次日直接触顶)'
        else:
            broke_dja = False
            broke_djb = False
            for j in range(i+1, retouch_idx):
                za = to_f(rows[j][13]) if len(rows[j])>13 else None
                close = to_f(rows[j][1]) if len(rows[j])>1 else None
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
        modes[mode] += 1

print(f'高波池文件: {files_core}')
print(f'DXZC>25 且当日未触顶: {total_untouch:,}')
print(f'其中未来{LOOKAHEAD}天内再次触顶: {total_retouch:,} ({total_retouch/max(total_untouch,1)*100:.1f}%)')
print()
print('=== 调整模式分布（再次触顶的样本） ===')
print(f'{"模式":<20}{"n":>10}{"占比":>8}')
for mode, n in sorted(modes.items(), key=lambda x: -x[1]):
    print(f'{mode:<20}{n:>10,}{n/max(total_retouch,1)*100:>7.1f}%')
