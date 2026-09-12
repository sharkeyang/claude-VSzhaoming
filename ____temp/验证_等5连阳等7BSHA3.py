# -*- coding: utf-8 -*-
"""验证用户质疑的数据点：等5连阳、等7/等6 BSHA<3"""
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

# 等型[44]=BT连阳, 柱型[27], BSHA[19], 日ZA[13], 日ZC[14], 次日高幅[26]
# 1. 等5 连阳 数据（DXZA<0）
# 2. 等7/等6 BSHA<3 数据
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
                deng = row[44].strip()  # BT连阳 等型
                zx = row[27].strip()    # 柱型
                bsha = to_f(row[19])    # BSHA
                za = to_f(row[13])
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                # 等5 连阳
                if deng == '等5' and '连' in zx:
                    stats['等5连阳'][0]+=1; stats['等5连阳'][1]+= (1 if hr>=3 else 0); stats['等5连阳'][2]+=hr
                if deng == '等5':
                    stats['等5全部'][0]+=1; stats['等5全部'][1]+= (1 if hr>=3 else 0); stats['等5全部'][2]+=hr
                # 等7/等6 BSHA<3
                if deng in ('等7','等6') and bsha is not None and bsha < 3:
                    stats[f'{deng}BSHA<3'][0]+=1; stats[f'{deng}BSHA<3'][1]+= (1 if hr>=3 else 0); stats[f'{deng}BSHA<3'][2]+=hr
                if deng in ('等7','等6'):
                    stats[f'{deng}全部'][0]+=1; stats[f'{deng}全部'][1]+= (1 if hr>=3 else 0); stats[f'{deng}全部'][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
for k in ['等5连阳','等5全部','等7BSHA<3','等7全部','等6BSHA<3','等6全部']:
    s = stats[k]
    if s[0] > 0:
        print(f'{k}: n={s[0]:,} P(≥3%)={s[1]/s[0]*100:.2f}% 均高幅={s[2]/s[0]:.2f}%')