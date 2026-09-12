# -*- coding: utf-8 -*-
"""
操作区域内 柱排×顶型（含顶态G/K/L）获利性分析
====================================================
顶型完整格式：_ + [顶态G/K/L] + [核心顶型]
顶态：G=t顶>=-4(顶哼合并,好)/K=t顶>=-9(顶哼分离,中)/L=t顶<-9(未创新高已下跌,差)
核心顶型：f武/e非p-n/a龙/b龙/c雀/d虎劫/e篪/龙篪

输出：
  ① 顶态(G/K/L) 单独 P(≥3%)
  ② 核心顶型 单独 P(≥3%)
  ③ 顶态×核心顶型 组合 P(≥3%)

磁盘CSV列序：8=DXCD, 9=DXAB, 10=柱排, 13=日ZA, 26=次日高幅, 43=顶型
"""
import csv, os, sys, re
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}

def to_f(v):
    try: return float(v)
    except: return None

def in_region(dxcd, hx):
    if dxcd not in ('上', '忐'): return False
    if hx in ('甲', '乙', '己'): return True
    return False

def parse_dx(dx):
    """解析顶型：返回(顶态, 核心顶型)"""
    s = dx.strip()
    # 去掉前缀_
    if s.startswith('_'):
        s = s[1:]
    # 提取顶态 G/K/L（G无前缀，K/L有前缀）
    ta = 'G'
    if s.startswith('K'): ta = 'K'; s = s[1:]
    elif s.startswith('L'): ta = 'L'; s = s[1:]
    # 核心顶型
    if '龙' in s:
        if 'a龙' in s: core = '龙a'
        elif 'b龙' in s: core = '龙b'
        else: core = '龙'
    elif '雀' in s: core = '雀'
    elif '武' in s: core = '武'
    elif '虎' in s: core = '虎'
    elif '非' in s: core = '非'
    elif '篪' in s: core = '篪'
    else: core = '其他'
    return ta, core

# 统计
ta_stats = defaultdict(lambda: [0, 0, 0.0])  # 顶态
core_stats = defaultdict(lambda: [0, 0, 0.0])  # 核心顶型
combo_stats = defaultdict(lambda: [0, 0, 0.0])  # 顶态×核心
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
                if len(row) <= 43: continue
                dxcd = row[8].strip()
                dxab = row[9].strip()
                hr = to_f(row[26])
                if hr is None or hr < -50 or hr > 50: continue
                hx = 护型映射.get(dxab[0], '') if dxab else ''
                if not in_region(dxcd, hx): continue
                ta, core = parse_dx(row[43])
                if ta:
                    ta_stats[ta][0]+=1; ta_stats[ta][1]+= (1 if hr>=3 else 0); ta_stats[ta][2]+=hr
                if core:
                    core_stats[core][0]+=1; core_stats[core][1]+= (1 if hr>=3 else 0); core_stats[core][2]+=hr
                if ta and core:
                    combo_stats[f'{ta}×{core}'][0]+=1; combo_stats[f'{ta}×{core}'][1]+= (1 if hr>=3 else 0); combo_stats[f'{ta}×{core}'][2]+=hr
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('=' * 60)
print('① 顶态(G/K/L) 单独 P(≥3%)')
print('=' * 60)
print(f'{"顶态":<8} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 40)
for ta in ['G', 'K', 'L']:
    s = ta_stats[ta]
    if s[0] == 0: continue
    print(f'{ta:<8} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

print()
print('=' * 60)
print('② 核心顶型 单独 P(≥3%)')
print('=' * 60)
print(f'{"核心顶型":<10} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 40)
for core in ['龙a', '龙b', '雀', '虎', '篪', '非', '武']:
    s = core_stats[core]
    if s[0] == 0: continue
    print(f'{core:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')

print()
print('=' * 60)
print('③ 顶态×核心顶型 组合 P(≥3%)')
print('=' * 60)
print(f'{"组合":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 45)
rows = [(k, s) for k, s in combo_stats.items() if s[0] >= 300]
rows.sort(key=lambda x: x[1][1]/x[1][0])
for k, s in rows:
    print(f'{k:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
