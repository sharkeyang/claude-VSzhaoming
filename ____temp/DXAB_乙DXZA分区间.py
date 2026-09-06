# -*- coding: utf-8 -*-
"""
乙护型 DXZA 分区间验证（高波池）
任务4：乙护型 DXZA 分区间（接近DJA vs 远离DJA）的次日冲高
验证"不要一下破DJA就想跑，很多都是机会"
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def parse_dxab(dxab):
    if len(dxab) < 3: return ('','','')
    hx = dxab[1]
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    dxza = m.group(1) if m else ''
    return (hx, '', dxza)

def to_f(v):
    try: return float(v)
    except: return None

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
            for row in r:
                if len(row) <= 26: continue
                dxab = row[9].strip()
                zc = to_f(row[14])
                hr = to_f(row[26])
                if zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx, _, dxza_s = parse_dxab(dxab)
                if hx != '乙': continue
                dxza = to_f(dxza_s)
                if dxza is None: continue
                # 分区间
                if dxza <= 5:
                    add('乙DXZA≤5(近DJA)', hr)
                elif dxza <= 10:
                    add('乙DXZA6-10', hr)
                elif dxza <= 20:
                    add('乙DXZA11-20', hr)
                else:
                    add('乙DXZA>20(远DJA)', hr)
                add('乙基线', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('=== 乙护型 DXZA 分区间 ===')
for key in ['乙DXZA≤5(近DJA)','乙DXZA6-10','乙DXZA11-20','乙DXZA>20(远DJA)','乙基线']:
    if key in stats:
        s = stats[key]
        print(f'{key:<20} n={s[0]:>10,} P(≥3%)={s[1]/s[0]*100:>6.2f}% 平均高幅={s[2]/s[0]:>5.2f}%')