# -*- coding: utf-8 -*-
"""
验证1.5.5.6结论：等6+触顶+BSHA5=52.5%是否准确
等高线(等N) × 触顶 × BSHA5 交叉验证
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
                if len(row) <= 44: continue
                zc = to_f(row[14])
                hr = to_f(row[26])  # 次日高幅
                bsha = to_f(row[21])  # BSHA
                if zc is None or hr is None or bsha is None: continue
                if hr < -50 or hr > 50: continue
                if zc <= 0: continue  # 只统计ZC>0
                deng = row[44].strip()  # 日等型
                shang = row[30].strip()  # 上符串
                chuding = shang.endswith('A')
                bsha5 = bsha > 5
                # 触顶+BSHA5
                if chuding and bsha5:
                    add(f'{deng}|触顶+BSHA5', hr)
                # 触顶（不含BSHA5）
                if chuding:
                    add(f'{deng}|触顶', hr)
                # 全部
                add(f'{deng}|全部', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('=== 等高线(等N) × 触顶 × BSHA5 交叉验证（ZC>0） ===')
print(f'{"等高线":<6} {"条件":<14} {"n":>10} {"P(≥3%)":>8} {"平均高幅":>8}')
print('-'*55)
for deng in ['等1','等2','等3','等5','等6','等7']:
    for cond in ['触顶+BSHA5','触顶','全部']:
        key = f'{deng}|{cond}'
        if key in stats:
            s = stats[key]
            print(f'{deng:<6} {cond:<14} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')