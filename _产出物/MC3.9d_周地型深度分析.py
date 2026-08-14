#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9d_周地型深度分析.py
=====================
周地型全量深度分析（正确理解：地型=BTZA×前四柱形态，是柱排的分类）。

分析维度：
1. 地型完整分布 + 下周P3（全量7461只）
2. 地型 × WXZC（升势/跌势）交互 —— 正确区分 __ 前缀
3. 地型 × WXAB 交互
4. 地型 × WXCD 交互
5. 地型内部：BTZA分段（>=4 / >=0 / >=-3 / <-3）各自区分力
6. 地型 × 波型主类（龙猪/震正/头）交互

用法：
    python _产出物/MC3.9d_周地型深度分析.py

输出：
    - 控制台 + _产出物/MC3.9d_周地型深度分析.txt
"""

import pandas as pd, os, glob, sys, warnings
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物'
MIN_SAMPLE = 100
os.makedirs(OUTDIR, exist_ok=True)

def load_all():
    wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组周_*.csv')))
    dfs = []
    for i, f in enumerate(wfiles):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(wfiles)} 文件...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) >= 2:
                df['fid'] = i
                dfs.append(df)
        except:
            continue
    wk = pd.concat(dfs, ignore_index=True)
    wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
    wk = wk.dropna(subset=['下周HR'])
    print(f'  [加载] 完成: {len(wfiles)} 文件, {len(wk)} 行', flush=True)
    return wk

def rep(mask):
    g = wk[mask]
    n = len(g)
    if n < MIN_SAMPLE:
        return None, n
    return (g['下周HR'] >= 3).mean() * 100, n

def table(title, items, label_width=30):
    lines = [f'\n{"=" * 80}', title, '=' * 80,
             f'{"条件":<{label_width}s}  {"样本":>9s}  {"P3%":>7s}  {"vs基线":>7s}',
             '-' * (label_width + 30)]
    for name, mask in items:
        p, n = rep(mask)
        if p is None:
            lines.append(f'{name:<{label_width}s}  {n:>9,d}  {"-":>7s}  {"-":>7s}  (样本不足)')
        else:
            lines.append(f'{name:<{label_width}s}  {n:>9,d}  {p:>6.1f}%  {p-baseline:>+7.1f}pp')
    lines.append('')
    return '\n'.join(lines)

print('=' * 80)
print('MC3.9d 周地型深度分析')
print('=' * 80)
print()
wk = load_all()

baseline = (wk['下周HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n全样本: {total} 行, 基线下周P3 = {baseline:.1f}%')
print('=' * 80)

output = []

# 拆分波型三段
def seg(w, i):
    if pd.isna(w): return ''
    parts = str(w).split('.')
    return parts[i] if len(parts) > i else ''

wk['地型'] = wk['波型'].apply(lambda w: seg(w, 0))
wk['主类'] = wk['波型'].apply(lambda w: seg(w, 1))
wk['层界'] = wk['波型'].apply(lambda w: seg(w, 2))

# WXZC升势/跌势（__前缀）
wk['升势'] = ~wk['主类'].str.startswith('__', na=False)

# ── 1. 地型完整分布 ──
print('\n[1] 地型完整分布')
dixing = sorted(wk['地型'].dropna().unique())
items = [(f'地型={d}', wk['地型'] == d) for d in dixing]
out = table('1. 地型完整分布（全量7461只）', items)
print(out); output.append(out)

# ── 2. 地型 × WXZC（升势/跌势） ──
print('\n[2] 地型 × WXZC（升势/跌势）')
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    m = wk['地型'] == d
    items = [
        (f'{d}+升势(WXZC≥0)', m & wk['升势']),
        (f'{d}+跌势(WXZC<0)', m & ~wk['升势']),
    ]
    out = table(f'2. 地型{d} × WXZC', items)
    print(out); output.append(out)

# ── 3. 地型 × WXAB ──
print('\n[3] 地型 × WXAB')
m_ab_good = wk['WXAB'].str.contains('甲|乙|己', na=False)
m_ab_bad = wk['WXAB'].str.contains('丙|丁|戊', na=False)
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    m = wk['地型'] == d
    items = [
        (f'{d}+甲乙己', m & m_ab_good),
        (f'{d}+丙丁戊', m & m_ab_bad),
    ]
    out = table(f'3. 地型{d} × WXAB', items)
    print(out); output.append(out)

# ── 4. 地型 × WXCD ──
print('\n[4] 地型 × WXCD')
m_cd_good = wk['WXCD'].str.contains('金|银', na=False)
m_cd_bad = ~wk['WXCD'].str.contains('金|银', na=False)
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    m = wk['地型'] == d
    items = [
        (f'{d}+金银升', m & m_cd_good),
        (f'{d}+唏嘘尿屎', m & m_cd_bad),
    ]
    out = table(f'4. 地型{d} × WXCD', items)
    print(out); output.append(out)

# ── 5. BTZA分段区分力 ──
print('\n[5] BTZA分段区分力')
# 用ZA周列（周BTZA）
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
items = [
    ('ZA周>=4（远离WJA上）', wk['ZA周'] >= 4),
    ('ZA周>=0（上破WJA内）', (wk['ZA周'] >= 0) & (wk['ZA周'] < 4)),
    ('ZA周>=-3（刚跌破）', (wk['ZA周'] >= -3) & (wk['ZA周'] < 0)),
    ('ZA周<-3（远离WJA下）', wk['ZA周'] < -3),
]
out = table('5. BTZA分段区分力', items)
print(out); output.append(out)

# ── 6. 地型 × 波型主类 ──
print('\n[6] 地型 × 波型主类（升势内）')
m_up = wk['升势']
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀']:
    m = wk['地型'] == d
    items = [
        (f'{d}+龙猪', m & m_up & wk['主类'].str.contains('龙猪', na=False)),
        (f'{d}+震正', m & m_up & wk['主类'].str.contains('震正', na=False)),
        (f'{d}+头', m & m_up & wk['主类'].str.contains('头', na=False)),
    ]
    out = table(f'6. 地型{d} × 波型主类（升势）', items)
    print(out); output.append(out)

# ── 写入文件 ──
outpath = os.path.join(OUTDIR, 'MC3.9d_周地型深度分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')