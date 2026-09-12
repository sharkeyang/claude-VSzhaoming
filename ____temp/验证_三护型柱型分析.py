# -*- coding: utf-8 -*-
"""
己/甲/乙(DXZA>0) 三个护型 × 柱型大类 × 柱排类型 的全面分析
========================================================
柱型[27] 编码 .NN描述，NN第一位数字 = 大类：
  9=线下 5=根 4=枝 0=梯 1=栏 2=栅 3=杂
柱排[10] 类型：
  升排(升连/升吞) 跌吞 跌连 跌孕 人排(阴阳阴)

输出：次日冲高率 P(≥3%) + 转坏率（次日护型非本护型）
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

def classify_zp(zp):
    s = zp.strip()
    if s.startswith('跌.尾连'): return '跌连'
    if '尾吞' in s or '连后吞' in s: return '跌吞'
    if s.startswith('跌.尾反孕'): return '跌孕'
    if '人' in s: return '人排(阴阳阴)'
    if s.startswith('升'): return '升排'
    return '其他'

def classify_zx(zx):
    """柱型大类"""
    s = zx.strip()
    if not s or len(s) < 2: return None
    # 编码 .NN描述，NN 第一位数字
    if s.startswith('.'):
        d = s[1]
        if d == '9': return '线下'
        if d == '5': return '根'
        if d == '4': return '枝'
        if d == '0': return '梯'
        if d == '1': return '栏'
        if d == '2': return '栅'
        if d == '3': return '杂'
    return None

def hu_type(dxab):
    c = dxab.strip()[:1]
    return {'a':'甲','b':'乙','r':'己'}.get(c)

# 统计：护型 -> 柱型大类 -> [n, P3count, sum_hr, 转坏count]
stats = defaultdict(lambda: defaultdict(lambda: [0,0,0.0,0]))

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
            for i,row in enumerate(rows):
                if len(row) <= 30: continue
                ht = hu_type(row[9])
                if ht is None: continue
                # 乙需 DXZA>0
                if ht == '乙':
                    zpa = to_f(row[13])
                    if zpa is None or zpa <= 0: continue
                zx = classify_zx(row[27])
                if zx is None: continue
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                next_ht = hu_type(rows[i+1][9]) if i+1 < len(rows) else None
                is_bad = (next_ht != ht) if next_ht is not None else False
                s = stats[ht][zx]
                s[0]+=1
                s[1]+=(1 if hr>=3 else 0)
                s[2]+=hr
                s[3]+=(1 if is_bad else 0)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('='*80)
print('己/甲/乙(DXZA>0) × 柱型大类：次日冲高率 + 转坏率')
print('='*80)
for ht in ['甲','乙','己']:
    print(f'\n【{ht}护型】')
    print(f'{"柱型大类":<10} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"转坏率":>8}')
    print('-'*50)
    for zx in ['线下','根','枝','梯','栏','栅','杂']:
        if zx in stats[ht]:
            s = stats[ht][zx]
            p3 = s[1]/s[0]*100 if s[0] else 0
            avg = s[2]/s[0] if s[0] else 0
            bad = s[3]/s[0]*100 if s[0] else 0
            print(f'{zx:<10} {s[0]:>10,} {p3:>7.2f}% {avg:>7.2f}% {bad:>7.2f}%')
