# -*- coding: utf-8 -*-
"""
孕柱按护型细分 + DXZC=1突破时护型分布（高波池）
====================================================
质疑1：孕柱是否都不好？按护型细分孕柱表现
质疑2：突破DXZC=1时DXAB护型的统计（甲/乙/己/其他）
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
# 质疑1: 孕柱按护型细分（等2阳柱中孕线）
q1 = defaultdict(lambda: [0,0,0.0])  # key: 护型|孕类型 -> [n, hr>=3, sum_hr]
# 质疑2: DXZC=1突破时护型分布
q2 = defaultdict(lambda: [0,0,0.0])  # key: 护型 -> [n, hr>=3, sum_hr]
q2_all = [0,0,0.0]  # 总样本

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
        zc = to_f(row[14])
        if hr is None or zf is None or zc is None: continue
        if hr < -50 or hr > 50: continue
        dxab = row[9].strip()
        hx = parse_hx(dxab)
        if not hx: continue
        等型 = row[44].strip()
        zp = row[10].strip()

        # ===== 质疑1: 孕柱按护型细分（等2阳柱中孕线） =====
        if 等型 == '等2' and zf > 0 and '孕' in zp:
            if '尾反孕' in zp:
                q1[f'{hx}|尾反孕'][0]+=1; q1[f'{hx}|尾反孕'][1]+= (1 if hr>=3 else 0); q1[f'{hx}|尾反孕'][2]+=hr
            elif '孕孕' in zp:
                q1[f'{hx}|孕孕'][0]+=1; q1[f'{hx}|孕孕'][1]+= (1 if hr>=3 else 0); q1[f'{hx}|孕孕'][2]+=hr

        # ===== 质疑2: DXZC=1突破时护型分布 =====
        # DXZC=1 = 价格刚上穿DJC（日ZC从0或负转为1）
        if zc == 1:
            q2[hx][0]+=1; q2[hx][1]+= (1 if hr>=3 else 0); q2[hx][2]+=hr
            q2_all[0]+=1; q2_all[1]+= (1 if hr>=3 else 0); q2_all[2]+=hr

print(f'高波池文件: {files_core}')
print()

# ===== 质疑1输出 =====
print('='*75)
print('【质疑1】孕柱按护型细分（等2阳柱中孕线）')
print('='*75)
print(f'{"护型":<4} {"孕类型":<8} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*45)
for hx in ['甲','乙','己','戊','丙','丁']:
    for pt in ['尾反孕','孕孕']:
        key = f'{hx}|{pt}'
        if key in q1:
            s = q1[key]
            if s[0] >= 100:
                print(f'{hx:<4} {pt:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print()

# ===== 质疑2输出 =====
print('='*75)
print('【质疑2】DXZC=1突破时DXAB护型分布')
print('='*75)
print(f'{"护型":<4} {"n":>10} {"占比":>8} {"P(≥3%)":>8} {"均高幅":>8}')
print('-'*45)
for hx in ['甲','乙','己','戊','丙','丁']:
    if hx in q2:
        s = q2[hx]
        if s[0] >= 100:
            print(f'{hx:<4} {s[0]:>10,} {s[0]/q2_all[0]*100:>7.2f}% {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print(f'{"全部":<4} {q2_all[0]:>10,} {100:>7.2f}% {q2_all[1]/q2_all[0]*100:>7.2f}% {q2_all[2]/q2_all[0]:>7.2f}%')
print()