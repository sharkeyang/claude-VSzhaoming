# -*- coding: utf-8 -*-
"""
己/甲/乙(DXZA>0) × 柱型大类 × 柱排类型 全面分析（修正乙转坏判定）
柱型[27] 第一位数字：9=线下 5=根 4=枝 0=梯 1=栏 2=栅 3=杂
柱排[10]：升排/跌吞/跌连/跌孕/人排(阴阳阴)
转坏判定：甲=次日非a；乙(DXZA>0)=次日非b 或 (b且日ZA<=0)；己=次日非r
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
    if '人' in s: return '人排'
    if s.startswith('升'): return '升排'
    return '其他'

def classify_zx(zx):
    s = zx.strip()
    if s.startswith('.'):
        d = s[1]
        return {'9':'线下','5':'根','4':'枝','0':'梯','1':'栏','2':'栅','3':'杂'}.get(d)
    return None

def hu(dxab):
    return {'a':'甲','b':'乙','r':'己'}.get(dxab.strip()[:1])

# 柱型大类统计
stats_zx = defaultdict(lambda: defaultdict(lambda: [0,0,0.0,0]))
# 柱排类型统计
stats_zp = defaultdict(lambda: defaultdict(lambda: [0,0,0.0,0]))

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
                ht = hu(row[9])
                if ht is None: continue
                zpa = to_f(row[13])
                if ht == '乙' and (zpa is None or zpa <= 0): continue
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                # 转坏判定
                if i+1 < len(rows):
                    nht = hu(rows[i+1][9])
                    nzpa = to_f(rows[i+1][13])
                    if ht == '乙':
                        is_bad = (nht != '乙') or (nht == '乙' and nzpa is not None and nzpa <= 0)
                    else:
                        is_bad = (nht != ht)
                else:
                    is_bad = False
                # 柱型大类
                zx = classify_zx(row[27])
                if zx:
                    s = stats_zx[ht][zx]
                    s[0]+=1; s[1]+=(1 if hr>=3 else 0); s[2]+=hr; s[3]+=(1 if is_bad else 0)
                # 柱排类型
                zp = classify_zp(row[10])
                if zp != '其他':
                    s = stats_zp[ht][zp]
                    s[0]+=1; s[1]+=(1 if hr>=3 else 0); s[2]+=hr; s[3]+=(1 if is_bad else 0)
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()
print('='*80)
print('【柱型大类】己/甲/乙(DXZA>0) × 柱型大类')
print('='*80)
for ht in ['甲','乙','己']:
    print(f'\n{ht}护型:')
    print(f'{"柱型":<8} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"转坏率":>8}')
    for zx in ['线下','根','枝','梯','栏','栅','杂']:
        if zx in stats_zx[ht]:
            s = stats_zx[ht][zx]
            print(f'{zx:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}% {s[3]/s[0]*100:>7.2f}%')

print()
print('='*80)
print('【柱排类型】己/甲/乙(DXZA>0) × 柱排类型')
print('='*80)
for ht in ['甲','乙','己']:
    print(f'\n{ht}护型:')
    print(f'{"柱排":<10} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8} {"转坏率":>8}')
    for zp in ['升排','跌吞','跌连','跌孕','人排']:
        if zp in stats_zp[ht]:
            s = stats_zp[ht][zp]
            print(f'{zp:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}% {s[3]/s[0]*100:>7.2f}%')
