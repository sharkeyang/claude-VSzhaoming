# -*- coding: utf-8 -*-
"""
操盘计划 vs 5.3.3位置决策表 相互印证 + 介入点/退出规则实战胜率验证
====================================================
1. 操盘计划核心介入点 vs 5.3.3位置决策表（H2口径 vs P≥3%口径）
2. BSHA5触发器增强效果
3. 等5超跌反弹（等5+ZC>0+乙+BSHA5）
4. 退出规则实战胜率（乙ZA<0/丙退出后，是否真的避免损失）
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

hxmap = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}

def to_f(v):
    try: return float(v)
    except: return None

def parse_dxab(dxab):
    if len(dxab) < 3: return ('','','',None)
    hx = hxmap.get(dxab[0], '')
    zj = dxab[2]
    dirch = dxab[3] if len(dxab) > 3 else ''
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    val = int(m.group(1)) if m else None
    return (hx, zj, dirch, val)

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

# ============ 统计容器 ============
# 1. 操盘计划核心介入点 vs 5.3.3（H2≥2% 和 P≥3% 双口径）
q1 = defaultdict(lambda: [0,0,0,0.0])  # key -> [n, h2>=2, hr>=3, sum_hr]
# 2. BSHA5增强
q2 = defaultdict(lambda: [0,0,0,0.0])
# 3. 等5超跌反弹
q3 = defaultdict(lambda: [0,0,0,0.0])
# 4. 退出规则实战胜率
q4 = defaultdict(lambda: [0,0,0,0.0])

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
    dxabs = [parse_dxab(rows[i][9].strip()) for i in range(n)]
    zas = [to_f(rows[i][13]) for i in range(n)]
    zcs = [to_f(rows[i][14]) for i in range(n)]
    hrs = [to_f(rows[i][26]) for i in range(n)]
    bshas = [to_f(rows[i][21]) for i in range(n)]
    dxcds = [rows[i][8].strip() if len(rows[i])>8 else '' for i in range(n)]
    中符串s = [rows[i][35].strip() if len(rows[i])>35 else '' for i in range(n)]

    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx: continue
        za = zas[i]; zc = zcs[i]; hr = hrs[i]; bsha = bshas[i]
        if za is None or zc is None or hr is None or bsha is None: continue
        if hr < -50 or hr > 50: continue
        末符 = 中符串s[i][-1] if 中符串s[i] else ''
        等型 = calc_等型(za, 末符)
        cd = dxcds[i]

        def add(d, key, hr):
            s = d[key]; s[0]+=1
            if hr>=2: s[1]+=1
            if hr>=3: s[2]+=1
            s[3]+=hr

        # ===== 1. 操盘计划核心介入点 vs 5.3.3 =====
        # 操盘计划核心：DJC丘+真正交+DJA丘
        if zc > 0 and val is not None and val > 0 and cd in ('上','忐') and za > 0:
            add(q1, '操盘|核心(DJC+真正交+DJA)', hr)
            if 等型:
                add(q1, f'操盘|核心+{等型}', hr)
        # 5.3.3最优：等1+ZC>0+甲
        if zc > 0 and 等型 == '等1' and hx == '甲':
            add(q1, '533|等1+ZC>0+甲', hr)
        # 5.3.3：等3+ZC>0+甲
        if zc > 0 and 等型 == '等3' and hx == '甲':
            add(q1, '533|等3+ZC>0+甲', hr)
        # 5.3.3：等1+ZC>0+甲乙己
        if zc > 0 and 等型 == '等1' and hx in ('甲','乙','己'):
            add(q1, '533|等1+ZC>0+甲乙己', hr)

        # ===== 2. BSHA5增强 =====
        # 操盘计划核心 + BSHA5
        if zc > 0 and val is not None and val > 0 and cd in ('上','忐') and za > 0:
            if bsha >= 5:
                add(q2, '操盘核心+BSHA5', hr)
            else:
                add(q2, '操盘核心+BSHA<5', hr)
            if 等型 == '等1':
                if bsha >= 5:
                    add(q2, '操盘核心等1+BSHA5', hr)
                else:
                    add(q2, '操盘核心等1+BSHA<5', hr)

        # ===== 3. 等5超跌反弹 =====
        if zc > 0 and 等型 == '等5' and hx == '乙':
            if bsha >= 5:
                add(q3, '等5+ZC>0+乙+BSHA5', hr)
            else:
                add(q3, '等5+ZC>0+乙+BSHA<5', hr)

        # ===== 4. 退出规则实战胜率 =====
        # 乙ZA<0/丙退出后，次日是否避免损失（次日高幅<0 或 转坏）
        if zc > 0:
            if hx == '乙' and za < 0:
                add(q4, '退出|乙ZA<0', hr)
            if hx == '丙':
                add(q4, '退出|丙', hr)
            # 对照：甲/乙ZA>0（持有）
            if hx == '甲':
                add(q4, '持有|甲', hr)
            if hx == '乙' and za > 0:
                add(q4, '持有|乙ZA>0', hr)

print(f'高波池文件: {files_core}')
print()

def show(d, title, keys):
    print('='*75)
    print(f'【{title}】')
    print('='*75)
    print(f'{"类别":<28} {"n":>10} {"H2(≥2%)":>8} {"P(≥3%)":>8} {"均高幅":>8}')
    print('-'*65)
    for k in keys:
        if k in d:
            s = d[k]
            if s[0] >= 100:
                print(f'{k:<28} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]*100:>7.2f}% {s[3]/s[0]:>7.2f}%')
    print()

show(q1, '1. 操盘计划核心 vs 5.3.3位置决策表', [
    '操盘|核心(DJC+真正交+DJA)', '操盘|核心+等1', '操盘|核心+等3',
    '533|等1+ZC>0+甲', '533|等3+ZC>0+甲', '533|等1+ZC>0+甲乙己'
])

show(q2, '2. BSHA5增强效果', [
    '操盘核心+BSHA5', '操盘核心+BSHA<5', '操盘核心等1+BSHA5', '操盘核心等1+BSHA<5'
])

show(q3, '3. 等5超跌反弹', [
    '等5+ZC>0+乙+BSHA5', '等5+ZC>0+乙+BSHA<5'
])

show(q4, '4. 退出规则实战胜率', [
    '退出|乙ZA<0', '退出|丙', '持有|甲', '持有|乙ZA>0'
])