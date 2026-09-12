# -*- coding: utf-8 -*-
"""
DJC丘完整生命周期研究（高波池）
====================================================
研究DXZC>0区域（DJC丘）的运行特征：
1. DXZC=1（刚转正）时护型分布
2. DXZC<5（初期）时DXAB/DXZA状态
3. 主升阶段（DXZC增大）时DXAB/DXZA状态
4. 顶部震荡（DXZC高位）时DXAB/DXZA交叉
5. 尾部（下破DJB）过程
6. 下破DJC过程
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

def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return hxmap.get(dxab[0],'')

def parse_dxab_val(dxab):
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    return int(m.group(1)) if m else None

# ============ 统计容器 ============
# 1. DXZC分段时护型分布
q1 = defaultdict(lambda: [0,0,0,0,0,0])  # key: ZC段 -> [甲,乙,己,戊,丙,丁]
# 2. DXZC分段时DXAB>0比例
q2 = defaultdict(lambda: [0,0])  # key: ZC段 -> [n, DXAB>0]
# 3. DXZC分段时DXZA>0比例
q3 = defaultdict(lambda: [0,0])  # key: ZC段 -> [n, DXZA>0]
# 4. DJC丘生命周期：从DXZC=1到DXZC转负，各阶段状态
q4 = defaultdict(lambda: [0,0,0,0])  # key: 阶段 -> [n, DXAB>0, DXZA>0, 甲护型]

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
        zc = to_f(row[14]); za = to_f(row[13])
        if zc is None or za is None: continue
        dxab = row[9].strip()
        hx = parse_hx(dxab)
        btab = parse_dxab_val(dxab)
        if not hx: continue

        # 1. DXZC分段时护型分布
        if zc > 0:
            if zc == 1: seg = 'ZC=1'
            elif zc < 5: seg = 'ZC2-4'
            elif zc < 10: seg = 'ZC5-9'
            elif zc < 20: seg = 'ZC10-19'
            elif zc < 30: seg = 'ZC20-29'
            else: seg = 'ZC≥30'
            hx_idx = {'甲':0,'乙':1,'己':2,'戊':3,'丙':4,'丁':5}[hx]
            q1[seg][hx_idx]+=1
            # 2. DXAB>0比例
            if btab is not None:
                q2[seg][0]+=1
                if btab > 0: q2[seg][1]+=1
            # 3. DXZA>0比例
            q3[seg][0]+=1
            if za > 0: q3[seg][1]+=1

    # 4. DJC丘生命周期
    # 找DXZC>0区域，按位置分段（首/初/中/顶/尾）
    i = 0
    while i < n:
        zc = to_f(rows[i][14]) if len(rows[i])>14 else None
        if zc is None or zc <= 0:
            i += 1; continue
        start = i
        while i < n:
            zc2 = to_f(rows[i][14]) if len(rows[i])>14 else None
            if zc2 is None or zc2 <= 0: break
            i += 1
        end = i
        length = end - start
        if length < 5: continue
        # 分段：首(0-10%)、初(10-30%)、中(30-70%)、顶(70-90%)、尾(90-100%)
        for j in range(start, end):
            pos = (j - start) / length
            za = to_f(rows[j][13]) if len(rows[j])>13 else None
            dxab = rows[j][9].strip() if len(rows[j])>9 else ''
            hx = parse_hx(dxab)
            btab = parse_dxab_val(dxab)
            if pos < 0.1: stage = '首(0-10%)'
            elif pos < 0.3: stage = '初(10-30%)'
            elif pos < 0.7: stage = '中(30-70%)'
            elif pos < 0.9: stage = '顶(70-90%)'
            else: stage = '尾(90-100%)'
            q4[stage][0]+=1
            if btab is not None and btab > 0: q4[stage][1]+=1
            if za is not None and za > 0: q4[stage][2]+=1
            if hx == '甲': q4[stage][3]+=1

print(f'高波池文件: {files_core}')
print()

# ===== 1输出 =====
print('='*75)
print('【1】DXZC分段时护型分布')
print('='*75)
print(f'{"ZC段":<8} {"甲":>8} {"乙":>8} {"己":>8} {"戊":>8} {"丙":>8} {"丁":>8}')
print('-'*55)
for seg in ['ZC=1','ZC2-4','ZC5-9','ZC10-19','ZC20-29','ZC≥30']:
    if seg in q1:
        s = q1[seg]
        total = sum(s)
        if total >= 100:
            print(f'{seg:<8} {s[0]/total*100:>7.1f}% {s[1]/total*100:>7.1f}% {s[2]/total*100:>7.1f}% {s[3]/total*100:>7.1f}% {s[4]/total*100:>7.1f}% {s[5]/total*100:>7.1f}%')
print()

# ===== 2/3输出 =====
print('='*75)
print('【2/3】DXZC分段时DXAB>0 / DXZA>0 比例')
print('='*75)
print(f'{"ZC段":<8} {"n":>10} {"DXAB>0":>8} {"DXZA>0":>8}')
print('-'*40)
for seg in ['ZC=1','ZC2-4','ZC5-9','ZC10-19','ZC20-29','ZC≥30']:
    if seg in q2 and seg in q3:
        s2 = q2[seg]; s3 = q3[seg]
        if s2[0] >= 100:
            print(f'{seg:<8} {s2[0]:>10,} {s2[1]/s2[0]*100:>7.2f}% {s3[1]/s3[0]*100:>7.2f}%')
print()

# ===== 4输出 =====
print('='*75)
print('【4】DJC丘生命周期各阶段状态')
print('='*75)
print(f'{"阶段":<12} {"n":>10} {"DXAB>0":>8} {"DXZA>0":>8} {"甲护型":>8}')
print('-'*50)
for stage in ['首(0-10%)','初(10-30%)','中(30-70%)','顶(70-90%)','尾(90-100%)']:
    if stage in q4:
        s = q4[stage]
        if s[0] >= 100:
            print(f'{stage:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]*100:>7.2f}% {s[3]/s[0]*100:>7.2f}%')
print()