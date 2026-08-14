#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9f_波型周等型组合.py
=====================
波型 × 周等型 组合全量验证，探索能否通过叠加周等型优化波型。

分析：
1. 波型主类 × 6等 组合P3
2. 地型 × 6等 组合P3
3. 波型主类内部：等3 vs 非等3 的区分力
4. 地型内部：等3 vs 非等3 的区分力

用法：
    python _产出物/MC3.9f_波型周等型组合.py

输出：
    - 控制台 + _产出物/MC3.9f_波型周等型组合.txt
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
print('MC3.9f 波型×周等型 组合验证')
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

# 6等
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['末位'] = wk['中符串周'].astype(str).str[-1]
m1 = wk['ZA周'] == 1
m2 = (wk['ZA周'] >= 2) & (wk['末位'].isin(['C','D','E','F']))
m3 = (wk['ZA周'] >= 2) & (wk['末位'].isin(['A','B']))
m5 = wk['ZA周'] == -1
m6 = (wk['ZA周'] <= -2) & (wk['末位'].isin(['A','B','C','D']))
m7 = (wk['ZA周'] <= -2) & (wk['末位'].isin(['E','F']))

# 升势/跌势
m_up = ~wk['主类'].str.startswith('__', na=False)

# ── 1. 波型主类 × 6等 ──
print('\n[1] 波型主类 × 6等')
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Fd震正芽', 'Ff震负', 'Df头负', 'Dd头正芽', 'Bc龙管栅']:
    m_mc = wk['主类'] == mc
    items = [
        (f'{mc}+等3', m_mc & m3),
        (f'{mc}+等2', m_mc & m2),
        (f'{mc}+等1', m_mc & m1),
        (f'{mc}+等7', m_mc & m7),
        (f'{mc}+等6', m_mc & m6),
        (f'{mc}+等5', m_mc & m5),
    ]
    out = table(f'1. {mc} × 6等', items)
    print(out); output.append(out)

# ── 2. 地型 × 6等 ──
print('\n[2] 地型 × 6等')
for d in ['0橅', '1柜', '2栅', '4暂', '4蛀', '5暂', '5蛀', '9妩', '8姖', '7姗']:
    m_d = wk['地型'] == d
    items = [
        (f'{d}+等3', m_d & m3),
        (f'{d}+等2', m_d & m2),
        (f'{d}+等1', m_d & m1),
        (f'{d}+等7', m_d & m7),
        (f'{d}+等6', m_d & m6),
        (f'{d}+等5', m_d & m5),
    ]
    out = table(f'2. 地型{d} × 6等', items)
    print(out); output.append(out)

# ── 3. 波型主类内部：等3 vs 非等3 ──
print('\n[3] 波型主类内部：等3 vs 非等3')
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Fd震正芽', 'Ff震负', 'Df头负', 'Dd头正芽', 'Bc龙管栅']:
    m_mc = wk['主类'] == mc
    items = [
        (f'{mc}+等3', m_mc & m3),
        (f'{mc}+非等3', m_mc & ~m3),
    ]
    out = table(f'3. {mc} 等3 vs 非等3', items)
    print(out); output.append(out)

# ── 4. 地型内部：等3 vs 非等3 ──
print('\n[4] 地型内部：等3 vs 非等3')
for d in ['0橅', '1柜', '2栅', '4暂', '4蛀', '5暂', '5蛀', '9妩', '8姖', '7姗']:
    m_d = wk['地型'] == d
    items = [
        (f'{d}+等3', m_d & m3),
        (f'{d}+非等3', m_d & ~m3),
    ]
    out = table(f'4. 地型{d} 等3 vs 非等3', items)
    print(out); output.append(out)

# ── 写入文件 ──
outpath = os.path.join(OUTDIR, 'MC3.9f_波型周等型组合.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')