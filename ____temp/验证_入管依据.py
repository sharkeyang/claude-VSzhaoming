# -*- coding: utf-8 -*-
"""
入管依据验证：DTZA 持续天数 vs P(≥3%)
====================================================
假设：
1. 柱连续>3柱在DJA之上（DTZA>0持续>3天）= 升管
2. 柱连续>3柱在DJA之下（DTZA<0持续>3天）= 跌管
3. DTZA≥3 可作为入管依据
4. DTZA≥2 且升连 可作为入管依据

DTZA = 日ZA = 价格 vs DJA(EMA5) 交叉天数（col13）
柱排[10]：升连 = 以"升"开头且含"连"
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

def to_f(v):
    try: return float(v)
    except: return None

def is_shenglian(zp):
    s = zp.strip()
    return s.startswith('升') and '连' in s

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0, 0, 0.0])
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 26: continue
                za = to_f(row[13])
                hr = to_f(row[26])
                if za is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                zp = row[10].strip()
                # 基线
                stats['基线'][0]+=1; stats['基线'][1]+= (1 if hr>=3 else 0); stats['基线'][2]+=hr
                # DTZA 分桶
                if za >= 3:
                    stats['DTZA≥3'][0]+=1; stats['DTZA≥3'][1]+= (1 if hr>=3 else 0); stats['DTZA≥3'][2]+=hr
                if za >= 2:
                    stats['DTZA≥2'][0]+=1; stats['DTZA≥2'][1]+= (1 if hr>=3 else 0); stats['DTZA≥2'][2]+=hr
                    if is_shenglian(zp):
                        stats['DTZA≥2+升连'][0]+=1; stats['DTZA≥2+升连'][1]+= (1 if hr>=3 else 0); stats['DTZA≥2+升连'][2]+=hr
                if za >= 1:
                    stats['DTZA≥1'][0]+=1; stats['DTZA≥1'][1]+= (1 if hr>=3 else 0); stats['DTZA≥1'][2]+=hr
                if za >= 4:
                    stats['DTZA≥4'][0]+=1; stats['DTZA≥4'][1]+= (1 if hr>=3 else 0); stats['DTZA≥4'][2]+=hr
                if za >= 5:
                    stats['DTZA≥5'][0]+=1; stats['DTZA≥5'][1]+= (1 if hr>=3 else 0); stats['DTZA≥5'][2]+=hr
                # 升连（不限DTZA）
                if is_shenglian(zp):
                    stats['升连'][0]+=1; stats['升连'][1]+= (1 if hr>=3 else 0); stats['升连'][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('=' * 60)
print('入管依据验证：DTZA 持续天数 vs P(≥3%)')
print('=' * 60)
print(f'{"条件":<16} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 50)
for k in ['基线', 'DTZA≥1', 'DTZA≥2', 'DTZA≥3', 'DTZA≥4', 'DTZA≥5', '升连', 'DTZA≥2+升连']:
    s = stats[k]
    if s[0] == 0: continue
    print(f'{k:<16} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')