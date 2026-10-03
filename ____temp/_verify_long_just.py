# -*- coding: utf-8 -*-
"""验证：四态=龙 内部，AB周∈{1,2,3}(刚转正交) 是否特殊？
对比 四态=龙 内部各 AB周 区间的下周冲高(HR>=3%)概率
谕组周CSV: 主期[0] 周涨[1] PR[2] HR[3] WXAB[4] 波型[5] 柱排周[6] WXCD[13] ZA周[14] AB周[21] ZC周[16]
"""
import sys, csv, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

files = glob.glob('昭明算展/谕组周/谕组周_*.csv')

def sitai(wxab):
    if not wxab: return ''
    c = wxab[0]
    if c in 'ab': return '龙'
    if c == 'c': return '雀'
    if c in 'zy': return '虎'
    if c == 'r': return '武'
    return ''

# 统计: 四态=龙 内部，按AB周区间
# 区间: 1-3(刚转), 4-6, 7-10, 11-20, >20
bins = [
    ('AB=1-3(刚转正交)', 1, 3),
    ('AB=4-6', 4, 6),
    ('AB=7-10', 7, 10),
    ('AB=11-20', 11, 20),
    ('AB>20', 21, 999),
]
stats = {k: [0,0] for k,_,_ in bins}
# 额外: 龙内部 刚转 vs 非刚转
long_just = [0,0]  # 龙+AB1-3
long_other = [0,0]  # 龙+AB>3

for f in files:
    with open(f, encoding='gbk') as fh:
        reader = csv.reader(fh)
        next(reader)
        prev = None
        for row in reader:
            if len(row) < 22:
                prev = None; continue
            try:
                ab = int(row[21]); hr = float(row[3])
            except:
                prev = None; continue
            if prev is not None:
                p_ab, p_wxab = prev
                if sitai(p_wxab) == '龙' and p_ab > 0:
                    hit = 1 if hr >= 3 else 0
                    if 1 <= p_ab <= 3:
                        long_just[1] += 1; long_just[0] += hit
                    else:
                        long_other[1] += 1; long_other[0] += hit
                    for k, lo, hi in bins:
                        if lo <= p_ab <= hi:
                            stats[k][1] += 1; stats[k][0] += hit
                            break
            try:
                prev = (ab, row[4])
            except:
                prev = None

print('=== 四态=龙 内部，按AB周区间 ===')
print(f'{"区间":<20}{"样本":>8}{"下周HR≥3%":>10}{"概率":>8}')
for k,_,_ in bins:
    hit, total = stats[k]
    pct = hit/total*100 if total else 0
    print(f'{k:<20}{total:>8}{hit:>10}{pct:>7.1f}%')

print()
print('=== 龙内部 刚转 vs 非刚转 ===')
for name, arr in [('龙+AB1-3(刚转)', long_just), ('龙+AB>3(非刚转)', long_other)]:
    hit, total = arr
    pct = hit/total*100 if total else 0
    print(f'{name:<22}{total:>8}{hit:>10}{pct:>7.1f}%')

# 显著性检验（卡方）
import math
def chi2(a, b, c, d):
    # 2x2: [a b; c d]
    n = a+b+c+d
    if n == 0: return 0
    e1 = (a+c)*(a+b)/n
    e2 = (b+d)*(a+b)/n
    e3 = (a+c)*(c+d)/n
    e4 = (b+d)*(c+d)/n
    if min(e1,e2,e3,e4) < 5: return 0
    return ((a-e1)**2/e1 + (b-e2)**2/e2 + (c-e3)**2/e3 + (d-e4)**2/e4)

a = long_just[0]; b = long_just[1]-long_just[0]
c = long_other[0]; d = long_other[1]-long_other[0]
chi = chi2(a,b,c,d)
print(f'\n卡方检验: chi2={chi:.1f} (df=1, 3.84=0.05显著, 6.63=0.01显著)')