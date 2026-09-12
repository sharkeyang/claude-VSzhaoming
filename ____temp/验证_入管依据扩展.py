# -*- coding: utf-8 -*-
"""
入管依据扩展探索：DTZA 持续天数 × 其他指标
====================================================
探索更多入管依据组合：
- DTZA≥3 + 升连/升排/人排/跌吞
- DTZA≥3 + BSHA≥5
- DTZA≥3 + 触顶
- DTZA≥2 + 升连 + BSHA≥5
- 等型(等1/等2/等3) + DTZA≥3
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

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('升') and '连' in s: return '升连'
    if s.startswith('升') and '排' in s: return '升排'
    if '人' in s: return '人排'
    if s.startswith('跌') and '吞' in s: return '跌吞'
    return '其他'

def has_touch(sfs):
    return 'A' in sfs

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
                if len(row) <= 44: continue
                za = to_f(row[13])
                hr = to_f(row[26])
                if za is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                zp = classify_zp(row[10])
                bsha = to_f(row[19])
                sfs = row[30].strip()
                deng = row[44].strip()
                # 基线
                stats['基线'][0]+=1; stats['基线'][1]+= (1 if hr>=3 else 0); stats['基线'][2]+=hr
                # DTZA≥3 组合
                if za >= 3:
                    stats['DTZA≥3'][0]+=1; stats['DTZA≥3'][1]+= (1 if hr>=3 else 0); stats['DTZA≥3'][2]+=hr
                    if zp == '升连':
                        stats['DTZA≥3+升连'][0]+=1; stats['DTZA≥3+升连'][1]+= (1 if hr>=3 else 0); stats['DTZA≥3+升连'][2]+=hr
                    if zp == '升排':
                        stats['DTZA≥3+升排'][0]+=1; stats['DTZA≥3+升排'][1]+= (1 if hr>=3 else 0); stats['DTZA≥3+升排'][2]+=hr
                    if zp == '人排':
                        stats['DTZA≥3+人排'][0]+=1; stats['DTZA≥3+人排'][1]+= (1 if hr>=3 else 0); stats['DTZA≥3+人排'][2]+=hr
                    if zp == '跌吞':
                        stats['DTZA≥3+跌吞'][0]+=1; stats['DTZA≥3+跌吞'][1]+= (1 if hr>=3 else 0); stats['DTZA≥3+跌吞'][2]+=hr
                    if bsha is not None and bsha >= 5:
                        stats['DTZA≥3+BSHA5'][0]+=1; stats['DTZA≥3+BSHA5'][1]+= (1 if hr>=3 else 0); stats['DTZA≥3+BSHA5'][2]+=hr
                    if has_touch(sfs):
                        stats['DTZA≥3+触顶'][0]+=1; stats['DTZA≥3+触顶'][1]+= (1 if hr>=3 else 0); stats['DTZA≥3+触顶'][2]+=hr
                    if deng in ('等1', '等2', '等3'):
                        stats[f'DTZA≥3+{deng}'][0]+=1; stats[f'DTZA≥3+{deng}'][1]+= (1 if hr>=3 else 0); stats[f'DTZA≥3+{deng}'][2]+=hr
                # DTZA≥2 + 升连 + BSHA5
                if za >= 2 and zp == '升连' and bsha is not None and bsha >= 5:
                    stats['DTZA≥2+升连+BSHA5'][0]+=1; stats['DTZA≥2+升连+BSHA5'][1]+= (1 if hr>=3 else 0); stats['DTZA≥2+升连+BSHA5'][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('=' * 60)
print('入管依据扩展探索')
print('=' * 60)
print(f'{"条件":<22} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 55)
# 按 P(≥3%) 排序
rows = [(k, s) for k, s in stats.items() if s[0] >= 1000]
rows.sort(key=lambda x: x[1][1]/x[1][0], reverse=True)
for k, s in rows:
    print(f'{k:<22} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')