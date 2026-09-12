# -*- coding: utf-8 -*-
"""
验证等2且为阳柱的划分（高波池）
====================================================
用户猜想：等2且为阳柱通常代表向上，但如果该阳柱是"阴柱之后的升孕"，
其实很可能是跌排的一部分。需要区分等2阳柱的不同类型。

验证：
1. 等2阳柱的柱排分布（升排/人排/跌连/跌吞/跌孕/升孕）
2. 等2阳柱各柱排的次日冲高率
3. 等2阳柱中"升孕"（尾反孕/孕孕）是否代表跌排
4. 等2阳柱 vs 等2阴柱 的对比
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

def calc_等型(dtza, 末符):
    if dtza == 1: return '等1'
    elif dtza > 0:
        if dtza >= 2 and 末符 in 'AB': return '等3'
        elif dtza >= 2 and 末符 in 'CDEF': return '等2'
        elif dtza > 3 and 末符 in 'CDEF': return '等4'
    elif dtza == -1: return '等5'
    elif dtza < 0:
        if dtza <= -2 and 末符 in 'EF': return '等7'
        elif dtza <= -2 and 末符 in 'ABCD': return '等6'
        elif dtza < -3 and 末符 in 'ABCD': return '等8'
    return ''

def classify_zp(zp):
    """柱排分类"""
    s = str(zp).strip()
    if '跌.尾连' in s or s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if '尾反孕' in s or '孕孕' in s: return '孕线'
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    if s.startswith('跌'): return '跌排'
    return '其他'

# 更细的柱排分类
def classify_zp_detail(zp):
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
# 1. 等2阳柱的柱排分布
q1 = defaultdict(lambda: [0,0,0.0])  # key: 柱排分类 -> [n, hr>=3, sum_hr]
# 2. 等2阳柱细分类
q2 = defaultdict(lambda: [0,0,0.0])
# 3. 等2阴柱 vs 阳柱
q3 = defaultdict(lambda: [0,0,0.0])
# 4. 等2阳柱中"升孕" vs 其他
q4 = defaultdict(lambda: [0,0,0.0])

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
        if len(row) <= 26: continue
        za = to_f(row[13])
        zc = to_f(row[14])
        hr = to_f(row[26])
        zf = to_f(row[5])
        if za is None or zc is None or hr is None or zf is None: continue
        if hr < -50 or hr > 50: continue
        中符串 = row[33].strip() if len(row) > 33 else ''
        末符 = 中符串[-1] if 中符串 else ''
        等型 = calc_等型(za, 末符)
        if 等型 != '等2': continue
        zp = row[10].strip()
        zp_cat = classify_zp(zp)
        zp_detail = classify_zp_detail(zp)

        # 1. 等2阳柱的柱排分类
        if zf > 0:
            q1[zp_cat][0]+=1; q1[zp_cat][1]+= (1 if hr>=3 else 0); q1[zp_cat][2]+=hr
            q2[zp_detail][0]+=1; q2[zp_detail][1]+= (1 if hr>=3 else 0); q2[zp_detail][2]+=hr
            # 4. 升孕 vs 其他
            if '孕' in zp:
                q4['等2阳+孕线'][0]+=1; q4['等2阳+孕线'][1]+= (1 if hr>=3 else 0); q4['等2阳+孕线'][2]+=hr
            else:
                q4['等2阳+非孕'][0]+=1; q4['等2阳+非孕'][1]+= (1 if hr>=3 else 0); q4['等2阳+非孕'][2]+=hr
        # 3. 等2阴柱 vs 阳柱
        if zf > 0:
            q3['等2阳柱'][0]+=1; q3['等2阳柱'][1]+= (1 if hr>=3 else 0); q3['等2阳柱'][2]+=hr
        else:
            q3['等2阴柱'][0]+=1; q3['等2阴柱'][1]+= (1 if hr>=3 else 0); q3['等2阴柱'][2]+=hr

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

show(q1, '1. 等2阳柱的柱排分类', ['升排','人排','跌连','跌吞','孕线','跌排','其他'])
show(q2, '2. 等2阳柱细分类', ['升尾反孕','跌尾反孕','尾反孕','孕孕','升尾连','跌尾连','跌吞','人排','升排','跌排','其他'])
show(q3, '3. 等2阴柱 vs 阳柱', ['等2阳柱','等2阴柱'])
show(q4, '4. 等2阳柱中孕线 vs 非孕', ['等2阳+孕线','等2阳+非孕'])