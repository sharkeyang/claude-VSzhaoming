# -*- coding: utf-8 -*-
"""
前一柱触顶 + 此柱阴柱：跌孕 vs 跌吞 规律分析
====================================================
用户问题：前一柱为触顶，此柱为阴柱，若此柱是跌孕或跌吞，各自有什么规律？

假设（[[甲护型遇阴柱差异化处理]]）：跌吞+触顶=洗盘持有，跌孕+触顶=转坏

分析：
  ① 操作区域内，前一柱触顶 + 此柱阴柱，按柱排(跌孕/跌吞/其他)分组
  ② 对比 P(≥3%)/均高幅
  ③ 对比 前一柱触顶 vs 非触顶

磁盘CSV列序：1=收, 2=开, 8=DXCD, 9=DXAB, 10=柱排, 13=日ZA, 26=次日高幅, 30=上符串
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

def in_region(dxcd, hx):
    if dxcd not in ('上', '忐'): return False
    if hx in ('甲', '乙', '己'): return True
    return False

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾连'): return '跌连'
    if '人' in s: return '人排'
    return '其他'

def has_touch(sfs):
    return 'A' in sfs  # 触顶

# 统计: (前触顶, 柱排) -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0, 0, 0.0])
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    prev_sfs = None
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 30: continue
                dxcd = row[8].strip()
                dxab = row[9].strip()
                close = to_f(row[1])
                open_ = to_f(row[2])
                hr = to_f(row[26])
                if close is None or open_ is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                cur_sfs = row[30].strip()
                # 此柱为阴柱
                is_yin = close < open_
                # 前一柱触顶
                prev_touch = has_touch(prev_sfs) if prev_sfs is not None else False
                if in_region(dxcd, hx) and is_yin:
                    zp = classify_zp(row[10])
                    key = f'{"前触顶" if prev_touch else "前非触顶"}-{zp}'
                    stats[key][0]+=1; stats[key][1]+= (1 if hr>=3 else 0); stats[key][2]+=hr
                prev_sfs = cur_sfs
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('=' * 70)
print('操作区域内 阴柱：前一柱触顶 vs 非触顶 × 柱排')
print('=' * 70)
print(f'{"类别":<18} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 50)
# 排序：P(≥3%) 从低到高
rows = [(k, s) for k, s in stats.items() if s[0] >= 500]
rows.sort(key=lambda x: x[1][1]/x[1][0])
for k, s in rows:
    print(f'{k:<18} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

print()
print('=' * 70)
print('重点对比：跌孕 vs 跌吞（前一柱触顶）')
print('=' * 70)
for zp in ['跌孕', '跌吞']:
    for touch in ['前触顶', '前非触顶']:
        k = f'{touch}-{zp}'
        s = stats[k]
        if s[0] == 0: continue
        print(f'{k:<18} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
