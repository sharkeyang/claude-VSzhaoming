# -*- coding: utf-8 -*-
"""
DXZC>0 时 甲/乙(ZA>0) 下破DJA（DTZA=-1）的柱排分布
====================================================
条件：DXZC>0 且 当日DTZA=-1 且 前一柱护型为 甲/乙(ZA>0)
问题：一般是什么柱排？都是跌连吗？还是阴阳阴(人排)？

磁盘CSV列序：8=DXCD, 9=DXAB, 10=柱排, 13=日ZA, 14=日ZC
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}

def to_f(v):
    try: return float(v)
    except: return None

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('升') and '连' in s: return '升连'
    if s.startswith('跌') and '连' in s: return '跌连'
    if s.startswith('升') and '孕' in s: return '升孕'
    if s.startswith('跌') and '孕' in s: return '跌孕'
    if s.startswith('升') and '吞' in s: return '升吞'
    if s.startswith('跌') and '吞' in s: return '跌吞'
    if '人' in s: return '人排(阴阳阴)'
    return '其他'

# 统计: 柱排 -> count
stats = defaultdict(int)
# 前一柱护型分布（用于确认）
prev_hx_stats = defaultdict(int)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    prev_hx = None
    prev_za = None
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 14: continue
                dxab = row[9].strip()
                za = to_f(row[13])
                zc = to_f(row[14])
                if za is None or zc is None: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                # 条件：DXZC>0 且 当日DTZA=-1 且 前一柱护型为 甲/乙(ZA>0)
                if zc > 0 and za == -1 and prev_hx in ('甲', '乙') and prev_za is not None and prev_za > 0:
                    zp = classify_zp(row[10])
                    stats[zp] += 1
                    prev_hx_stats[f'{prev_hx}(ZA>0)'] += 1
                # 更新前一柱
                if hx:
                    prev_hx = hx
                    prev_za = za
                else:
                    prev_hx = None
                    prev_za = None
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

total = sum(stats.values())
print('=' * 60)
print(f'DXZC>0 时 甲/乙(ZA>0) 下破DJA（DTZA=-1）柱排分布（n={total:,}）')
print('=' * 60)
print(f'{"柱排":<16} {"个数":>10} {"占比":>8}')
print('-' * 40)
for k, c in sorted(stats.items(), key=lambda x: -x[1]):
    print(f'{k:<16} {c:>10,} {c/total*100:>7.2f}%')

print()
print('=' * 60)
print('前一柱护型确认（应全为甲/乙ZA>0）')
print('=' * 60)
for k, c in sorted(prev_hx_stats.items(), key=lambda x: -x[1]):
    print(f'{k:<16} {c:>10,} {c/total*100:>7.2f}%')