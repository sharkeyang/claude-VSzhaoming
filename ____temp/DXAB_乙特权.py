# -*- coding: utf-8 -*-
"""
乙的特权验证 + 甲精细验证（高波池）
任务2精细：甲 + 阴柱 + 柱排含升（稳定升排，非冲高回落）
任务3：乙(DXZA>0) 需突破回踩(龙管)/启动结构才能拉升
任务4：乙(DXZA<0) 不要一下破DJA就想跑
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
    zj = dxab[2]
    m = re.search(r'[上中下忐忠忑]([+-]?\d+)', dxab)
    dxza = m.group(1) if m else ''
    return (hx, zj, dxza)

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
            rows = [row for row in r]
        for i in range(len(rows)):
            row = rows[i]
            if len(row) <= 26: continue
            dxab = row[9].strip()
            zc = to_f(row[14])
            za = to_f(row[13])
            zf = to_f(row[5])  # 涨幅
            hr = to_f(row[26])  # 次日高幅
            zhu = row[10].strip()  # 柱排
            bo = row[11].strip()  # 波型
            if zc is None or hr is None or zf is None: continue
            if hr < -50 or hr > 50: continue
            hx, zj, dxza_s = parse_dxab(dxab)
            dxza = to_f(dxza_s)
            # 任务2精细：甲 + 阴柱 + 柱排含升（稳定升排）
            if hx == '甲' and zf < 0 and '升' in zhu:
                add('2精:甲阴柱+升排', hr)
            # 任务3：乙(DXZA>0) 按波型结构
            if hx == '乙' and dxza is not None and dxza > 0:
                if '龙管' in bo:
                    add('3:乙ZA>0+龙管(突破回踩)', hr)
                elif '龙猪' in bo:
                    add('3:乙ZA>0+龙猪(主升)', hr)
                else:
                    add('3:乙ZA>0+其他', hr)
                add('3:乙ZA>0基线', hr)
            # 任务4：乙(DXZA<0)
            if hx == '乙' and dxza is not None and dxza < 0:
                add('4:乙ZA<0', hr)
                add('4:乙ZA<0基线', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('=== 任务2精细：甲阴柱+升排 ===')
for key in ['2精:甲阴柱+升排']:
    if key in stats:
        s = stats[key]
        print(f'{key:<25} n={s[0]:>10,} P(≥3%)={s[1]/s[0]*100:>6.2f}% 平均高幅={s[2]/s[0]:>5.2f}%')
print()
print('=== 任务3：乙(DXZA>0) 结构 ===')
for key in ['3:乙ZA>0+龙管(突破回踩)','3:乙ZA>0+龙猪(主升)','3:乙ZA>0+其他','3:乙ZA>0基线']:
    if key in stats:
        s = stats[key]
        print(f'{key:<25} n={s[0]:>10,} P(≥3%)={s[1]/s[0]*100:>6.2f}% 平均高幅={s[2]/s[0]:>5.2f}%')
print()
print('=== 任务4：乙(DXZA<0) ===')
for key in ['4:乙ZA<0','4:乙ZA<0基线']:
    if key in stats:
        s = stats[key]
        print(f'{key:<25} n={s[0]:>10,} P(≥3%)={s[1]/s[0]*100:>6.2f}% 平均高幅={s[2]/s[0]:>5.2f}%')