# -*- coding: utf-8 -*-
"""
按 VBA 定义重新分类柱排：当前柱（末位）形态
====================================================
VBA 柱排定义（L1661-1753）：
- 升.尾连：末2位 = 升连&升连 / 升吞&升连 / 升孕&升连 → 末位=升连(阳)
- 升.尾吞：末2位 = 跌孕&升吞 → 末位=升吞(阳)
- 升.尾反孕：末2位 = 升连&跌孕 / 跌孕&升吞&跌孕 → 末位=跌孕(阴)
- 跌.尾连：末2位 = 跌连&跌连 / 跌吞&跌连 / 跌孕&跌连 → 末位=跌连(阴)
- 跌.尾吞：末2位 = 升孕&跌吞 → 末位=跌吞(阴)
- 跌.尾反孕：末2位 = 跌连&升孕 / 升孕&跌吞&升孕 → 末位=升孕(阳)
- (升)人.连后吞：末2位 = 升连&跌吞 → 末位=跌吞(阴)
- (跌)人.连后吞：末2位 = 跌连&升吞 → 末位=升吞(阳)
- (升)人.吞吞 / (跌)人.吞吞 / (人)人.吞吞：末位=跌吞或升吞
- (升)人.孕孕 / (跌)人.孕孕 / (人)人.孕孕：末位=升孕或跌孕
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

# 末位形态 -> 当前柱阴阳
def last_char(zp):
    # 取柱排字符串最后一个字母（Q/O/o/W/V/v）
    for ch in reversed(zp):
        if ch in 'QOoWVv':
            return ch
    return ''

def yinyang(ch):
    # Q=升连 O=升吞 o=升孕 → 阳；W=跌连 V=跌吞 v=跌孕 → 阴
    if ch in 'QOo': return '阳'
    if ch in 'WVv': return '阴'
    return '?'

# 柱排 -> [n, 上破DJA, 站稳DJA, 触顶]
zp = defaultdict(lambda: [0,0,0,0])
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
        if not sf or sf[-1] == 'A': continue
        zpc = row[10].strip() if len(row)>10 else '空'
        if not zpc: zpc = '空'

        end = min(i+1+LOOKAHEAD, n)
        za_vals = []
        retouch = False
        for j in range(i+1, end):
            za = to_f(rows[j][13]) if len(rows[j])>13 else None
            if za is not None: za_vals.append(za)
            sfj = rows[j][30].strip() if len(rows[j])>30 else ''
            if sfj and sfj[-1] == 'A': retouch = True

        broke_up = False
        prev = to_f(row[13]) if len(row)>13 else None
        for za in za_vals:
            if prev is not None and prev <= 0 and za > 0:
                broke_up = True
                break
            prev = za
        stand = sum(1 for za in za_vals if za > 0) >= 5

        zp[zpc][0] += 1
        if broke_up: zp[zpc][1] += 1
        if stand: zp[zpc][2] += 1
        if retouch: zp[zpc][3] += 1

print(f'高波池文件: {files_core}')
print()
print('='*90)
print('柱排 × 当前柱阴阳 × 未来10天 上破DJA/站稳DJA/触顶')
print('='*90)
print(f'{"柱排":<26}{"阴阳":<4}{"n":>9}{"上破DJA":>9}{"站稳DJA":>9}{"触顶":>8}')
for k, (n, up, st, rt) in sorted(zp.items(), key=lambda x: -x[1][0]):
    if n < 5000: continue
    yy = yinyang(last_char(k))
    print(f'{k:<26}{yy:<4}{n:>9,}{up/n*100:>8.1f}%{st/n*100:>8.1f}%{rt/n*100:>7.1f}%')
