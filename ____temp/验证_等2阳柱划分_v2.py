# -*- coding: utf-8 -*-
"""
验证等2且为阳柱的划分（高波池）v2
====================================================
用户猜想：等2且为阳柱通常代表向上，但如果该阳柱是"阴柱之后的升孕"，
其实很可能是跌排的一部分。需要区分等2阳柱的不同类型。

日等型来源：BT连阳列（index 44）= 等1/等2/等3/等5/等6/等7
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

def classify_zp_detail(zp):
    """柱排细分类"""
    s = str(zp).strip()
    if '尾反孕' in s:
        if s.startswith('升'): return '升尾反孕'
        if s.startswith('跌'): return '跌尾反孕'
        return '尾反孕'
    if '孕孕' in s:
        return '孕孕'
    if '尾连' in s and s.startswith('升'): return '升尾连'
    if '尾连' in s and s.startswith('跌'): return '跌尾连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    if s.startswith('跌'): return '跌排'
    return '其他'

# ============ 统计容器 ============
# 1. 等2阳柱的柱排细分类
q1 = defaultdict(lambda: [0,0,0.0])  # key: 柱排分类 -> [n, hr>=3, sum_hr]
# 2. 等2阴柱 vs 阳柱
q2 = defaultdict(lambda: [0,0,0.0])
# 3. 等2阳柱中孕线 vs 非孕
q3 = defaultdict(lambda: [0,0,0.0])
# 4. 等2阳柱中"升孕"（升尾反孕/孕孕）vs 其他
q4 = defaultdict(lambda: [0,0,0.0])
# 5. 等2阳柱中"升孕" vs "升排" vs "跌排" 对比
q5 = defaultdict(lambda: [0,0,0.0])

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

        # 1. 等2阳柱的柱排细分类
        if zf > 0:
            q1[zp_detail][0]+=1; q1[zp_detail][1]+= (1 if hr>=3 else 0); q1[zp_detail][2]+=hr
            # 3. 孕线 vs 非孕
            if '孕' in zp:
                q3['等2阳+孕线'][0]+=1; q3['等2阳+孕线'][1]+= (1 if hr>=3 else 0); q3['等2阳+孕线'][2]+=hr
            else:
                q3['等2阳+非孕'][0]+=1; q3['等2阳+非孕'][1]+= (1 if hr>=3 else 0); q3['等2阳+非孕'][2]+=hr
            # 4. 升孕 vs 其他
            if '升' in zp and '孕' in zp:
                q4['等2阳+升孕'][0]+=1; q4['等2阳+升孕'][1]+= (1 if hr>=3 else 0); q4['等2阳+升孕'][2]+=hr
            else:
                q4['等2阳+非升孕'][0]+=1; q4['等2阳+非升孕'][1]+= (1 if hr>=3 else 0); q4['等2阳+非升孕'][2]+=hr
            # 5. 升孕 vs 升排 vs 跌排
            if '升' in zp and '孕' in zp:
                q5['升孕'][0]+=1; q5['升孕'][1]+= (1 if hr>=3 else 0); q5['升孕'][2]+=hr
            elif zp_detail == '升排' or zp_detail == '升尾连':
                q5['升排'][0]+=1; q5['升排'][1]+= (1 if hr>=3 else 0); q5['升排'][2]+=hr
            elif zp_detail in ('跌排','跌尾连','跌吞','跌尾反孕'):
                q5['跌排'][0]+=1; q5['跌排'][1]+= (1 if hr>=3 else 0); q5['跌排'][2]+=hr
        # 2. 等2阴柱 vs 阳柱
        if zf > 0:
            q2['等2阳柱'][0]+=1; q2['等2阳柱'][1]+= (1 if hr>=3 else 0); q2['等2阳柱'][2]+=hr
        else:
            q2['等2阴柱'][0]+=1; q2['等2阴柱'][1]+= (1 if hr>=3 else 0); q2['等2阴柱'][2]+=hr

print(f'高波池文件: {files_core}')
print()

def show(d, title, keys):
    print('='*75)
    print(f'【{title}】')
    print('='*75)
    print(f'{"类别":<16} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*50)
    for k in keys:
        if k in d:
            s = d[k]
            if s[0] >= 100:
                print(f'{k:<16} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
    print()

show(q1, '1. 等2阳柱的柱排细分类', ['升排','升尾连','升尾反孕','孕孕','人排','跌排','跌尾连','跌吞','跌尾反孕','其他'])
show(q2, '2. 等2阴柱 vs 阳柱', ['等2阳柱','等2阴柱'])
show(q3, '3. 等2阳柱中孕线 vs 非孕', ['等2阳+孕线','等2阳+非孕'])
show(q4, '4. 等2阳柱中升孕 vs 非升孕', ['等2阳+升孕','等2阳+非升孕'])
show(q5, '5. 等2阳柱中升孕 vs 升排 vs 跌排', ['升孕','升排','跌排'])