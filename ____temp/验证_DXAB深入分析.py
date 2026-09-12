# -*- coding: utf-8 -*-
"""
DXAB正交深入分析（高波池）
====================================================
问题3/4: DXAB>0/<0持续时间 × DXCD 叠加
问题6: DXZC>0区域内DXAB交叉次数分布（最多/最少/与DXCD）
问题7: 快速负交的DXEF/DXCD展开分析
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

def extract_ef(月策带日):
    if not 月策带日: return ''
    m = re.search(r'\(([^)]+)\)', 月策带日)
    return m.group(1) if m else ''

# ============ 统计容器 ============
# 问题3/4: BTAB>0/<0持续时间 × DXCD
dur_pos_cd = defaultdict(lambda: [0,0.0])  # key: DXCD -> [run数, 总天数]
dur_neg_cd = defaultdict(lambda: [0,0.0])
# 问题6: DXZC>0区域内DXAB交叉次数分布
cross_dist = defaultdict(lambda: [0,0])  # key: 交叉次数 -> [区域数, 总天数]
cross_cd = defaultdict(lambda: [0,0])  # key: DXCD -> [区域数, 交叉次数]
cross_max = [0, 0]  # [最大交叉次数, 区域数]
# 问题7: 快速负交的DXEF/DXCD展开
q7_efcd = defaultdict(lambda: [0,0])  # key: EF|CD -> [DXAB>0样本, 快速负交]
q7_ef = defaultdict(lambda: [0,0])
q7_cd = defaultdict(lambda: [0,0])
# 快速负交的护型分布
q7_hx = defaultdict(lambda: [0,0])
# 快速负交的日ZA深度
q7_za = defaultdict(lambda: [0,0])

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
    zcs = [to_f(rows[i][14]) for i in range(n)]
    zas = [to_f(rows[i][13]) for i in range(n)]
    dxcds = [rows[i][8].strip() if len(rows[i])>8 else '' for i in range(n)]
    月策带日s = [rows[i][50].strip() if len(rows[i])>50 else '' for i in range(n)]

    # ===== 问题3/4: BTAB>0/<0持续时间 × DXCD =====
    # 记录每个run的DXCD（取run内出现最多的DXCD）
    i = 0
    while i < n:
        hx, zj, dirch, val = dxabs[i]
        if not hx or val is None:
            i += 1; continue
        if val > 0:
            start = i
            cd_count = defaultdict(int)
            while i < n:
                hx2, zj2, dirch2, val2 = dxabs[i]
                if val2 is None or val2 <= 0: break
                cd_count[dxcds[i]] += 1
                i += 1
            length = i - start
            main_cd = max(cd_count, key=cd_count.get) if cd_count else ''
            if main_cd:
                dur_pos_cd[main_cd][0]+=1; dur_pos_cd[main_cd][1]+=length
        elif val < 0:
            start = i
            cd_count = defaultdict(int)
            while i < n:
                hx2, zj2, dirch2, val2 = dxabs[i]
                if val2 is None or val2 >= 0: break
                cd_count[dxcds[i]] += 1
                i += 1
            length = i - start
            main_cd = max(cd_count, key=cd_count.get) if cd_count else ''
            if main_cd:
                dur_neg_cd[main_cd][0]+=1; dur_neg_cd[main_cd][1]+=length
        else:
            i += 1

    # ===== 问题6: DXZC>0区域内DXAB交叉次数分布 =====
    i = 0
    while i < n:
        zc = zcs[i]
        if zc is None or zc <= 0:
            i += 1; continue
        start = i
        cd_count = defaultdict(int)
        while i < n and zcs[i] is not None and zcs[i] > 0:
            cd_count[dxcds[i]] += 1
            i += 1
        end = i
        # 统计交叉次数
        crossings = 0
        prev_sign = None
        for j in range(start, end):
            hx2, zj2, dirch2, val2 = dxabs[j]
            if val2 is None: continue
            sign = 1 if val2 > 0 else (-1 if val2 < 0 else 0)
            if prev_sign is not None and sign != 0 and prev_sign != 0 and sign != prev_sign:
                crossings += 1
            if sign != 0:
                prev_sign = sign
        cross_dist[crossings][0]+=1
        cross_dist[crossings][1]+=(end-start)
        main_cd = max(cd_count, key=cd_count.get) if cd_count else ''
        if main_cd:
            cross_cd[main_cd][0]+=1; cross_cd[main_cd][1]+=crossings
        if crossings > cross_max[0]:
            cross_max = [crossings, 1]
        elif crossings == cross_max[0]:
            cross_max[1]+=1

    # ===== 问题7: 快速负交的DXEF/DXCD展开 =====
    for i in range(n):
        hx, zj, dirch, val = dxabs[i]
        if not hx or val is None or val <= 0: continue
        ef = extract_ef(月策带日s[i]); cd = dxcds[i]
        za = zas[i]
        quick_neg = False
        for k in range(1, 6):
            if i+k >= n: break
            hx2, zj2, dirch2, val2 = dxabs[i+k]
            if val2 is not None and val2 < 0:
                quick_neg = True; break
        q7_efcd[f'{ef}|{cd}'][0]+=1
        q7_ef[ef][0]+=1
        q7_cd[cd][0]+=1
        q7_hx[hx][0]+=1
        if za is not None:
            if za <= 4: q7_za['ZA≤4'][0]+=1
            else: q7_za['ZA>4'][0]+=1
        if quick_neg:
            q7_efcd[f'{ef}|{cd}'][1]+=1
            q7_ef[ef][1]+=1
            q7_cd[cd][1]+=1
            q7_hx[hx][1]+=1
            if za is not None:
                if za <= 4: q7_za['ZA≤4'][1]+=1
                else: q7_za['ZA>4'][1]+=1

print(f'高波池文件: {files_core}')
print()

# ===== 问题3/4输出 =====
print('='*75)
print('【问题3/4】DXAB>0/<0持续时间 × DXCD 叠加')
print('='*75)
print(f'{"DXCD":<4} {"方向":<6} {"run数":>10} {"平均天数":>10}')
print('-'*40)
for cd in ['上','忐','忠','中','忑','下']:
    if cd in dur_pos_cd:
        s = dur_pos_cd[cd]
        print(f'{cd:<4} {"正>0":<6} {s[0]:>10,} {s[1]/s[0]:>9.2f}')
    if cd in dur_neg_cd:
        s = dur_neg_cd[cd]
        print(f'{cd:<4} {"负<0":<6} {s[0]:>10,} {s[1]/s[0]:>9.2f}')
print()

# ===== 问题6输出 =====
print('='*75)
print('【问题6】DXZC>0区域内DXAB交叉次数分布')
print('='*75)
print(f'{"交叉次数":<8} {"区域数":>10} {"占比":>8} {"平均天数":>10}')
print('-'*45)
total_regions = sum(v[0] for v in cross_dist.values())
for c in sorted(cross_dist.keys()):
    s = cross_dist[c]
    print(f'{c:<8} {s[0]:>10,} {s[0]/total_regions*100:>7.2f}% {s[1]/s[0]:>9.2f}')
print(f'最大交叉次数: {cross_max[0]}（{cross_max[1]}个区域）')
print()
print('【DXZC>0区域内DXAB交叉次数 × DXCD】')
print(f'{"DXCD":<4} {"区域数":>10} {"总交叉":>10} {"平均交叉/区域":>14}')
print('-'*45)
for cd in ['上','忐','忠','中','忑','下']:
    if cd in cross_cd:
        s = cross_cd[cd]
        if s[0] >= 100:
            print(f'{cd:<4} {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]:>13.2f}')
print()

# ===== 问题7输出 =====
print('='*75)
print('【问题7】快速负交(≤5天)的DXEF/DXCD展开')
print('='*75)
print('【按DXEF×DXCD】')
print(f'{"DXEF":<4} {"DXCD":<4} {"DXAB>0":>10} {"快速负交":>10} {"率":>8}')
print('-'*50)
for ef in ['金','银','唏','嘘','屎','尿']:
    for cd in ['上','忐','忠','中','忑','下']:
        key = f'{ef}|{cd}'
        if key in q7_efcd:
            s = q7_efcd[key]
            if s[0] >= 100:
                print(f'{ef:<4} {cd:<4} {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
print()
print('【按护型】')
print(f'{"护型":<4} {"DXAB>0":>10} {"快速负交":>10} {"率":>8}')
print('-'*40)
for hx in ['甲','乙','己','戊','丙','丁']:
    if hx in q7_hx:
        s = q7_hx[hx]
        if s[0] >= 100:
            print(f'{hx:<4} {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
print()
print('【按日ZA深度】')
print(f'{"日ZA":<6} {"DXAB>0":>10} {"快速负交":>10} {"率":>8}')
print('-'*40)
for k in ['ZA≤4','ZA>4']:
    if k in q7_za:
        s = q7_za[k]
        if s[0] >= 100:
            print(f'{k:<6} {s[0]:>10,} {s[1]:>10,} {s[1]/s[0]*100:>7.2f}%')
print()