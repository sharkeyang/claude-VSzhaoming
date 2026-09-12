# -*- coding: utf-8 -*-
"""
操作区域内 柱排×顶型 获利性分析
====================================================
操作区域：DXCD=上/忐 + 甲/乙ZA>0/己/乙ZA<0
柱排[10]：跌连/跌孕/跌吞/人排/升排/其他
顶型[43]：龙(a触顶/b近顶)/雀/武/虎/非/篪

输出：操作区域内 柱排×顶型 P(≥3%)，识别获利/不获利组合

磁盘CSV列序：8=DXCD, 9=DXAB, 10=柱排, 13=日ZA, 26=次日高幅, 43=顶型
"""
import csv, os, sys, re
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
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

def classify_dx(dx):
    """提取顶型核心：龙(a/b)/雀/武/虎/非/篪"""
    s = dx.strip()
    if '龙' in s:
        if 'a龙' in s: return '龙a(触顶)'
        if 'b龙' in s: return '龙b(近顶)'
        return '龙'
    if '雀' in s: return '雀'
    if '武' in s: return '武'
    if '虎' in s: return '虎'
    if '非' in s: return '非'
    if '篪' in s: return '篪'
    return '其他'

# 统计: (柱排, 顶型) -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0, 0, 0.0])
# 基线
baseline = [0, 0, 0.0]
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
                if len(row) <= 43: continue
                dxcd = row[8].strip()
                dxab = row[9].strip()
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                baseline[0]+=1; baseline[1]+= (1 if hr>=3 else 0); baseline[2]+=hr
                if not in_region(dxcd, hx): continue
                zp = classify_zp(row[10])
                dx = classify_dx(row[43])
                key = f'{zp}×{dx}'
                stats[key][0]+=1; stats[key][1]+= (1 if hr>=3 else 0); stats[key][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print(f'基线: P(≥3%)={baseline[1]/baseline[0]*100:.2f}%, 均高幅={baseline[2]/baseline[0]:.2f}%')
print()

print('=' * 70)
print('操作区域内 柱排×顶型 P(≥3%)（从低到高）')
print('=' * 70)
print(f'{"柱排×顶型":<18} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 50)
rows = [(k, s) for k, s in stats.items() if s[0] >= 300]
rows.sort(key=lambda x: x[1][1]/x[1][0])
for k, s in rows:
    print(f'{k:<18} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
