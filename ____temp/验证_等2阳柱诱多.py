# -*- coding: utf-8 -*-
"""
等2阳柱诱多识别（高波池）
====================================================
用户猜想：
1. 升孕是诱多（已验证）
2. 跌连之后忽然一个升吞，是否也是诱多？
3. 头脑风暴找出所有可能的诱多（非升排都验证）

验证：
1. 等2阳柱所有柱排类型的冲高率（找出诱多）
2. 跌连后升吞（前一天跌连，当前升吞）
3. 各柱排 vs 基线（等2阳柱整体28.97%）
"""
import csv, os, sys, re, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

def classify_zp(zp):
    """柱排粗分类"""
    s = str(zp).strip()
    if '尾反孕' in s or '孕孕' in s: return '孕线'
    if '尾吞' in s or '连后吞' in s or '吞吞' in s: return '吞线'
    if '尾连' in s: return '连阳'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    if s.startswith('跌'): return '跌排'
    return '其他'

def classify_zp_detail(zp):
    """柱排细分类"""
    s = str(zp).strip()
    # 升吞（升排中的尾吞）
    if s.startswith('升') and ('尾吞' in s or '吞' in s): return '升吞'
    # 升连（升排中的尾连）
    if s.startswith('升') and '尾连' in s: return '升连'
    # 升孕（升排中的孕）
    if s.startswith('升') and '孕' in s: return '升孕'
    # 跌孕
    if s.startswith('跌') and '孕' in s: return '跌孕'
    # 跌吞
    if s.startswith('跌') and '吞' in s: return '跌吞'
    # 人排吞
    if '人' in s and ('吞' in s or '连后吞' in s): return '人吞'
    # 人排孕
    if '人' in s and '孕' in s: return '人孕'
    # 人排其他
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    if s.startswith('跌'): return '跌排'
    return '其他'

# ============ 统计容器 ============
# 1. 等2阳柱各柱排细分类
q1 = defaultdict(lambda: [0,0,0.0])  # key: 柱排 -> [n, hr>=3, sum_hr]
# 2. 跌连后升吞（前一天跌连，当前升吞）
q2 = defaultdict(lambda: [0,0,0.0])
# 3. 各柱排 vs 基线
q3 = defaultdict(lambda: [0,0,0.0])

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
        if len(row) <= 44: continue
        hr = to_f(row[26])
        zf = to_f(row[5])
        if hr is None or zf is None: continue
        if hr < -50 or hr > 50: continue
        等型 = row[44].strip()
        if 等型 != '等2': continue
        zp = row[10].strip()
        zp_detail = classify_zp_detail(zp)
        zp_cat = classify_zp(zp)

        # 1. 等2阳柱各柱排细分类
        if zf > 0:
            q1[zp_detail][0]+=1; q1[zp_detail][1]+= (1 if hr>=3 else 0); q1[zp_detail][2]+=hr
            q3['等2阳柱基线'][0]+=1; q3['等2阳柱基线'][1]+= (1 if hr>=3 else 0); q3['等2阳柱基线'][2]+=hr

            # 2. 跌连后升吞（前一天跌连，当前升吞）
            if zp_detail == '升吞' and i > 0:
                prev_zp = rows[i-1][10].strip() if len(rows[i-1]) > 10 else ''
                prev_zf = to_f(rows[i-1][5])
                if '跌.尾连' in prev_zp or prev_zp.startswith('跌.尾连'):
                    q2['跌连后升吞'][0]+=1; q2['跌连后升吞'][1]+= (1 if hr>=3 else 0); q2['跌连后升吞'][2]+=hr
                elif '跌' in prev_zp:
                    q2['跌排后升吞'][0]+=1; q2['跌排后升吞'][1]+= (1 if hr>=3 else 0); q2['跌排后升吞'][2]+=hr
                else:
                    q2['非跌后升吞'][0]+=1; q2['非跌后升吞'][1]+= (1 if hr>=3 else 0); q2['非跌后升吞'][2]+=hr

print(f'高波池文件: {files_core}')
print()

def show(d, title, keys):
    print('='*75)
    print(f'【{title}】')
    print('='*75)
    print(f'{"类别":<16} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"vs基线":>8}')
    print('-'*60)
    base = d.get('等2阳柱基线', [0,0,0.0])
    base_p = base[1]/base[0]*100 if base[0] > 0 else 0
    for k in keys:
        if k in d:
            s = d[k]
            if s[0] >= 100:
                diff = s[1]/s[0]*100 - base_p
                print(f'{k:<16} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}% {diff:>+7.2f}pp')
    print()

show(q1, '1. 等2阳柱各柱排细分类（vs 基线28.97%）', [
    '升吞','升连','升孕','跌孕','跌吞','人吞','人孕','人排','升排','跌排','其他'
])
show(q2, '2. 跌连后升吞 vs 跌排后升吞 vs 非跌后升吞', [
    '跌连后升吞','跌排后升吞','非跌后升吞'
])
show(q3, '3. 等2阳柱基线', ['等2阳柱基线'])