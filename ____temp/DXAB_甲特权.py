# -*- coding: utf-8 -*-
"""
甲的特权验证（高波池）
任务2a：0<DXAB≤4 阴柱转阳（甲护型）
任务2b：连阳后第一个阴柱（vV）后有阳柱（甲护型）
任务2c：首个 DXZA<0 后有反弹（甲护型）
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 高波池
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def parse_dxab(dxab):
    if len(dxab) < 3: return ('','','')
    hx = dxab[1]
    zj = dxab[2]
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    dxza = m.group(1) if m else ''
    return (hx, zj, dxza)

def to_f(v):
    try: return float(v)
    except: return None

# 统计
stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    s = stats[key]; s[0]+=1
    if hr>=3: s[1]+=1
    s[2]+=hr

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
            rows = [row for row in r]
        # 遍历，需要前一行判断连阳
        for i in range(len(rows)):
            row = rows[i]
            if len(row) <= 26: continue
            dxab = row[9].strip()
            zc = to_f(row[14])
            za = to_f(row[13])
            zf = to_f(row[5])  # 涨幅
            hr = to_f(row[26])  # 次日高幅
            if zc is None or hr is None or zf is None: continue
            if hr < -50 or hr > 50: continue
            hx, zj, dxza_s = parse_dxab(dxab)
            if hx != '甲': continue  # 只统计甲
            dxza = to_f(dxza_s)
            # 前一行（判断连阳）
            prev_zf = None
            if i > 0 and len(rows[i-1]) > 5:
                prev_zf = to_f(rows[i-1][5])
            # 2a: 0<DXAB≤4 阴柱转阳（甲，DXZA 1-4，当前阴柱）
            if dxza is not None and 0 < dxza <= 4 and zf < 0:
                add('2a:甲DXZA1-4阴柱', hr)
            # 2b: 连阳后第一个阴柱（vV）（甲，前阳柱，当前阴柱）
            if prev_zf is not None and prev_zf > 0 and zf < 0:
                add('2b:甲连阳后首阴', hr)
            # 2c: 首个DXZA<0后有反弹（甲，DXZA<0）
            if dxza is not None and dxza < 0:
                add('2c:甲DXZA<0', hr)
            # 基线：甲全部
            add('甲基线', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('=== 甲的特权验证 ===')
for key in ['2a:甲DXZA1-4阴柱','2b:甲连阳后首阴','2c:甲DXZA<0','甲基线']:
    if key in stats:
        s = stats[key]
        print(f'{key:<20} n={s[0]:>10,} P(≥3%)={s[1]/s[0]*100:>6.2f}% 平均高幅={s[2]/s[0]:>5.2f}%')