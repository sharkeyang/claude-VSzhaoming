# -*- coding: utf-8 -*-
"""
日等型 × DXAB护型 × DXZC 三维交叉分析（下日高幅口径）
=====================================================
指标说明：
  - 下日高幅 = 次日高幅（下日盘中最高涨幅），非收盘涨幅
  - 下日高≥3% = 次日高幅 ≥ 3%（冲高概率）
  - 均下日高 = 次日高幅均值
"""
import numpy as np, pandas as pd, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 200

高波池板块 = {'Qic', 'Qim', 'Qit'}
护型序 = {'甲':0,'乙':1,'丙':2,'丁':3,'戊':4,'己':5}

def load_board_map():
    with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_hx(dxab_str):
    if len(dxab_str) >= 2 and dxab_str[1] in 护型序:
        return dxab_str[1]
    return ''

def calc_等型(dtza, 末符):
    if dtza == 1:
        return '等1'
    elif dtza > 0:
        if dtza >= 2 and 末符 in 'AB':
            return '等3'
        elif dtza >= 2 and 末符 in 'CDEF':
            return '等2'
    elif dtza == -1:
        return '等5'
    elif dtza < 0:
        if dtza <= -2 and 末符 in 'EF':
            return '等7'
        elif dtza <= -2 and 末符 in 'ABCD':
            return '等6'
    return ''

def zc_sign(zc):
    if zc > 0: return 'ZC>0'
    return 'ZC≤0'

def zc_5seg(zc):
    if zc <= -2: return 'ZC≤-2'
    elif zc < 0: return 'ZC=-1'
    elif zc < 1: return 'ZC=0'
    elif zc < 5: return '1≤ZC<5'
    else: return 'ZC≥5'

class Agg:
    def __init__(self):
        self.n = 0; self.sum_hr = 0.0; self.n_hr_gt3 = 0
    def add(self, hr):
        self.n += 1
        hr = float(hr)
        self.sum_hr += hr
        if hr > 3: self.n_hr_gt3 += 1
    def stats(self):
        if self.n < MIN_SAMPLE: return None
        return {'n': self.n, 'mean_hr': self.sum_hr/self.n,
                'hr_gt3': self.n_hr_gt3/self.n*100}

board_map = load_board_map()
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
print(f'文件数: {len(files)}', flush=True)

agg_等zc = defaultdict(Agg)
agg_护zc = defaultdict(Agg)
agg_3way = defaultdict(Agg)
agg_等zc5 = defaultdict(Agg)

for i, f in enumerate(files):
    if i % 1000 == 0:
        print(f'  [{i}/{len(files)}]...', flush=True)
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df) < 5: continue
    except: continue

    cidl = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
    board = board_map.get(cidl, '')
    if board not in 高波池板块: continue

    hxs = [parse_hx(s) for s in df['DXAB'].astype(str).values]
    dtza = df['日ZA'].astype(float).values
    中符串 = df['中符串'].astype(str).values
    zcs = df['日ZC'].astype(float).values
    hrs = df['次日高幅'].astype(float).values  # 下日高幅

    for j in range(len(df)):
        hx = hxs[j]
        if not hx: continue
        末符 = 中符串[j][-1] if len(中符串[j]) > 0 else ''
        等型 = calc_等型(dtza[j], 末符)
        if not 等型: continue
        zc = zcs[j]
        if pd.isna(zc): continue
        hr = hrs[j]
        if pd.isna(hr): continue

        zcsg = zc_sign(zc)
        zc5 = zc_5seg(zc)

        agg_等zc[(等型, zcsg)].add(hr)
        agg_护zc[(hx, zcsg)].add(hr)
        agg_3way[(等型, hx, zcsg)].add(hr)
        agg_等zc5[(等型, zc5)].add(hr)

print()
print('='*78)
print('日等型 × DXAB护型 × DXZC 三维交叉分析（下日高幅口径）')
print('高波池 Qic+Qim+Qit，全量文件')
print('='*78)

# ============ 1. 等型 × ZC符号 ============
print()
print('【1】等型 × ZC符号（均下日高幅 / 下日高≥3%）')
print('| 等型 | ZC>0 样本 | ZC>0 均下日高 | ZC>0 高≥3% | ZC≤0 样本 | ZC≤0 均下日高 | ZC≤0 高≥3% | 均高差 |')
print('|:----|:--------:|:-----------:|:----------:|:--------:|:-----------:|:----------:|:------:|')
for 等 in ['等1','等2','等3','等5','等6','等7']:
    sp = agg_等zc[(等, 'ZC>0')].stats()
    sn = agg_等zc[(等, 'ZC≤0')].stats()
    if sp and sn:
        diff = sp['mean_hr'] - sn['mean_hr']
        print(f'| {等} | {sp["n"]} | {sp["mean_hr"]:.2f}% | {sp["hr_gt3"]:.1f}% | {sn["n"]} | {sn["mean_hr"]:.2f}% | {sn["hr_gt3"]:.1f}% | {diff:+.2f}pp |')
    elif sp:
        print(f'| {等} | {sp["n"]} | {sp["mean_hr"]:.2f}% | {sp["hr_gt3"]:.1f}% | - | - | - | - |')
    elif sn:
        print(f'| {等} | - | - | - | {sn["n"]} | {sn["mean_hr"]:.2f}% | {sn["hr_gt3"]:.1f}% | - |')

# ============ 2. 护型 × ZC符号 ============
print()
print('【2】DXAB护型 × ZC符号（均下日高幅 / 下日高≥3%）')
print('| 护型 | ZC>0 样本 | ZC>0 均下日高 | ZC>0 高≥3% | ZC≤0 样本 | ZC≤0 均下日高 | ZC≤0 高≥3% | 均高差 |')
print('|:----|:--------:|:-----------:|:----------:|:--------:|:-----------:|:----------:|:------:|')
for hx in '甲乙丙丁戊己':
    sp = agg_护zc[(hx, 'ZC>0')].stats()
    sn = agg_护zc[(hx, 'ZC≤0')].stats()
    if sp and sn:
        diff = sp['mean_hr'] - sn['mean_hr']
        print(f'| {hx} | {sp["n"]} | {sp["mean_hr"]:.2f}% | {sp["hr_gt3"]:.1f}% | {sn["n"]} | {sn["mean_hr"]:.2f}% | {sn["hr_gt3"]:.1f}% | {diff:+.2f}pp |')
    elif sp:
        print(f'| {hx} | {sp["n"]} | {sp["mean_hr"]:.2f}% | {sp["hr_gt3"]:.1f}% | - | - | - | - |')
    elif sn:
        print(f'| {hx} | - | - | - | {sn["n"]} | {sn["mean_hr"]:.2f}% | {sn["hr_gt3"]:.1f}% | - |')

# ============ 3. 等型 × 护型 × ZC符号（3way） ============
print()
print('【3】等型 × 护型 × ZC符号（均下日高幅 / 下日高≥3%）')
for 等 in ['等1','等2','等3','等5','等6','等7']:
    print(f'  --- {等} ---')
    print('  | 护型 | ZC>0 均下日高 | ZC>0 高≥3% | ZC≤0 均下日高 | ZC≤0 高≥3% |')
    print('  |:----|:-----------:|:----------:|:-----------:|:----------:|')
    for hx in '甲乙丙丁戊己':
        sp = agg_3way[(等, hx, 'ZC>0')].stats()
        sn = agg_3way[(等, hx, 'ZC≤0')].stats()
        sp_str = f'{sp["mean_hr"]:.2f}%/{sp["hr_gt3"]:.0f}%' if sp else '-'
        sn_str = f'{sn["mean_hr"]:.2f}%/{sn["hr_gt3"]:.0f}%' if sn else '-'
        print(f'  | {hx} | {sp_str} | {sn_str} |')

# ============ 4. ZC五段式 × 等型 ============
print()
print('【4】ZC五段式 × 等型（均下日高幅 / 下日高≥3%）')
print('| 等型 | ZC≤-2 | ZC=-1 | 1≤ZC<5 | ZC≥5 |')
print('|:----|:-----:|:-----:|:------:|:----:|')
for 等 in ['等1','等2','等3','等5','等6','等7']:
    row = []
    for seg in ['ZC≤-2','ZC=-1','1≤ZC<5','ZC≥5']:
        s = agg_等zc5[(等, seg)].stats()
        if s:
            row.append(f'{s["mean_hr"]:.2f}%/{s["hr_gt3"]:.0f}%')
        else:
            row.append('-')
    print(f'| {等} | ' + ' | '.join(row) + ' |')

# ============ 5. 关键场景 ============
print()
print('【5】关键交叉场景（均下日高幅 / 下日高≥3%）')
print('| 场景 | 样本 | 均下日高 | 高≥3% |')
print('|:----|:----:|:-------:|:-----:|')

def show(label, key):
    s = agg_3way[key].stats()
    if s:
        print(f'| {label} | {s["n"]} | {s["mean_hr"]:.2f}% | {s["hr_gt3"]:.1f}% |')

# 最优组合
show('等1+甲+ZC>0', ('等1','甲','ZC>0'))
show('等1+己+ZC>0', ('等1','己','ZC>0'))
show('等1+乙+ZC>0', ('等1','乙','ZC>0'))
show('等2+己+ZC>0', ('等2','己','ZC>0'))
show('等2+甲+ZC>0', ('等2','甲','ZC>0'))
show('等3+己+ZC>0', ('等3','己','ZC>0'))
show('等3+甲+ZC>0', ('等3','甲','ZC>0'))
# 最差组合
show('等7+丙+ZC≤0', ('等7','丙','ZC≤0'))
show('等7+丁+ZC≤0', ('等7','丁','ZC≤0'))
show('等6+丙+ZC≤0', ('等6','丙','ZC≤0'))
show('等5+丙+ZC≤0', ('等5','丙','ZC≤0'))
# 特殊：己在ZC≤0
show('等1+己+ZC≤0', ('等1','己','ZC≤0'))
show('等2+己+ZC≤0', ('等2','己','ZC≤0'))
show('等3+己+ZC≤0', ('等3','己','ZC≤0'))
# 特殊：甲在ZC≤0
show('等1+甲+ZC≤0', ('等1','甲','ZC≤0'))
show('等2+甲+ZC≤0', ('等2','甲','ZC≤0'))
show('等3+甲+ZC≤0', ('等3','甲','ZC≤0'))
# 等6/等7 在ZC>0
show('等6+乙+ZC>0', ('等6','乙','ZC>0'))
show('等6+丁+ZC>0', ('等6','丁','ZC>0'))
show('等6+戊+ZC>0', ('等6','戊','ZC>0'))
show('等7+乙+ZC>0', ('等7','乙','ZC>0'))
show('等7+丁+ZC>0', ('等7','丁','ZC>0'))

print()
print('完成')