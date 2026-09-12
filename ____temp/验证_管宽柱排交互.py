# -*- coding: utf-8 -*-
"""
验证用户假设（6.6.1 管宽领域）：
1. 管宽JC<10时，DJA之上的柱排（升排 vs 非升排）对次日冲高影响——是否非升排也不用担心
2. 管宽JC≥10时，DJA之上形成跌排是否预示要退出

磁盘CSV列序：8=DXCD, 9=DXAB, 10=柱排, 13=日ZA, 14=日ZC, 24=宽哼JC, 26=次日高幅
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0,0,0.0])

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
                zpa = to_f(row[13])  # 日ZA
                zc = to_f(row[14])
                kw = to_f(row[24])   # 宽哼JC
                hr = to_f(row[26])   # 次日高幅
                if zpa is None or zc is None or kw is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                # 只关注DJA之上（日ZA>0）
                if zpa <= 0: continue
                # 柱排
                zpaip = row[10].strip()
                is_sheng = '升' in zpaip
                is_die = '跌' in zpaip
                # 管宽分组
                if kw < 10:
                    kw_key = '管宽<10'
                else:
                    kw_key = '管宽≥10'
                # 柱排分组
                if is_sheng:
                    zp_key = '升排'
                elif is_die:
                    zp_key = '跌排'
                else:
                    zp_key = '非升非跌'
                # 统计
                stats[f'{kw_key}|{zp_key}'][0]+=1; stats[f'{kw_key}|{zp_key}'][1]+= (1 if hr>=3 else 0); stats[f'{kw_key}|{zp_key}'][2]+=hr
                stats[f'{kw_key}|全部'][0]+=1; stats[f'{kw_key}|全部'][1]+= (1 if hr>=3 else 0); stats[f'{kw_key}|全部'][2]+=hr
                stats[f'全部|{zp_key}'][0]+=1; stats[f'全部|{zp_key}'][1]+= (1 if hr>=3 else 0); stats[f'全部|{zp_key}'][2]+=hr
                stats['全部|全部'][0]+=1; stats['全部|全部'][1]+= (1 if hr>=3 else 0); stats['全部|全部'][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('='*70)
print('DJA之上（日ZA>0）：管宽 × 柱排 次日冲高率(≥3%)')
print('='*70)
print(f'{"管宽":<10} {"柱排":<10} {"n":>10} {"P(≥3%)":>8} {"平均高幅":>8}')
print('-'*55)
for kw_key in ['管宽<10','管宽≥10']:
    for zp_key in ['升排','非升非跌','跌排','全部']:
        key = f'{kw_key}|{zp_key}'
        if key in stats:
            s = stats[key]
            print(f'{kw_key:<10} {zp_key:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
    print('-'*55)
print('全部（DJA之上）:')
for zp_key in ['升排','非升非跌','跌排','全部']:
    key = f'全部|{zp_key}'
    if key in stats:
        s = stats[key]
        print(f'{"全部":<10} {zp_key:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
