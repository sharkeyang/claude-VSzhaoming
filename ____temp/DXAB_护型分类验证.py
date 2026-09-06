# -*- coding: utf-8 -*-
"""
DXAB 正交护型分类验证（高波池）
假设1：DXAB 正交护型分类
- 可能负转正：己、戊(DXZA>0)
- 正交：甲、乙(DXZA>0)、乙(DXZA<0)
- 可能正转负：戊
- 无需持有：丁、戊(DXZA<0)
验证：各护型在 DXZC>0 / DXZC<0 下的次日冲高≥3% 概率
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

# 高波池
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

# 统计: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0,0,0.0])
def add(key, hr):
    s = stats[key]; s[0]+=1
    if hr>=3: s[1]+=1
    s[2]+=hr

def parse_dxab(dxab):
    """解析DXAB编码，返回(护型汉字, 正交符号)"""
    if len(dxab) < 3: return ('','')
    hx = dxab[1]  # 第2位：甲/乙/丙/己/戊/丁
    zj = dxab[2]  # 第3位：↗/→/↘
    return (hx, zj)

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
                if len(row) <= 28: continue
                def to_f(v):
                    try: return float(v)
                    except: return None
                dxab = row[9].strip()
                zc = to_f(row[14])
                hr = to_f(row[26])  # 次日高幅（索引26，表头错位但数据正确）
                if zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx, zj = parse_dxab(dxab)
                if hx == '': continue
                # 按护型×ZC方向统计
                zc_key = 'ZC>0' if zc > 0 else 'ZC<=0'
                add(f'{hx}|{zc_key}', hr)
                add(f'{hx}|全部', hr)
                add(f'基线|{zc_key}', hr)
                add('基线|全部', hr)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('=== 各护型 × ZC方向 次日冲高≥3% ===')
print(f'{"护型":<6} {"ZC方向":<8} {"n":>10} {"P(≥3%)":>8} {"平均高幅":>8}')
print('-'*50)
for hx in ['甲','乙','丙','己','戊','丁']:
    for zc_key in ['ZC>0','ZC<=0','全部']:
        key = f'{hx}|{zc_key}'
        if key in stats:
            s = stats[key]
            print(f'{hx:<6} {zc_key:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print('-'*50)
for zc_key in ['ZC>0','ZC<=0','全部']:
    key = f'基线|{zc_key}'
    if key in stats:
        s = stats[key]
        print(f'{"基线":<6} {zc_key:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')