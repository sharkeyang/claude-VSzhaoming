# -*- coding: utf-8 -*-
"""
DXZC>0 的跌连分布：相对 DJA（DXZA）位置
====================================================
问题：DXZC>0 的跌连是不是都集中在下破DJA（DTZA=-1）时？
      DXZA>0（DJA之上）的跌连占 DXZC>0 跌连总数的百分比？

磁盘CSV列序：9=DXAB, 10=柱排, 13=日ZA, 14=日ZC
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

def to_f(v):
    try: return float(v)
    except: return None

def is_dielian(zp):
    s = zp.strip()
    return s.startswith('跌') and '连' in s

# 统计: DXZA区间 -> 跌连数
dielian = defaultdict(int)
# 总跌连
total_dielian = 0
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 14: continue
                za = to_f(row[13])
                zc = to_f(row[14])
                if za is None or zc is None: continue
                if zc <= 0: continue  # 只统计 DXZC>0
                if not is_dielian(row[10]): continue
                total_dielian += 1
                if za > 0:
                    dielian['DXZA>0(DJA之上)'] += 1
                elif za == -1:
                    dielian['DXZA=-1(下破DJA)'] += 1
                elif za == 0:
                    dielian['DXZA=0'] += 1
                else:
                    dielian[f'DXZA={int(za)}(DJA之下)'] += 1
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('=' * 60)
print(f'DXZC>0 的跌连分布（相对 DJA/DXZA，总跌连 {total_dielian:,}）')
print('=' * 60)
print(f'{"DXZA区间":<22} {"跌连数":>10} {"占比":>8}')
print('-' * 45)
for k, c in sorted(dielian.items(), key=lambda x: -x[1]):
    print(f'{k:<22} {c:>10,} {c/total_dielian*100:>7.2f}%')

print()
print('=' * 60)
print('关键对比')
print('=' * 60)
pos = dielian['DXZA>0(DJA之上)']
neg1 = dielian['DXZA=-1(下破DJA)']
print(f'DXZA>0(DJA之上) 跌连: {pos:,} ({pos/total_dielian*100:.2f}%)')
print(f'DXZA=-1(下破DJA) 跌连: {neg1:,} ({neg1/total_dielian*100:.2f}%)')
print(f'DJA之下(含-1及以下) 跌连: {total_dielian-pos:,} ({(total_dielian-pos)/total_dielian*100:.2f}%)')