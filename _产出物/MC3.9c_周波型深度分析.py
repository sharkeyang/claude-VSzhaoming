#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9c_周波型深度分析.py
=====================
周波型全量深度分析，探索优化空间。

分析维度：
1. 波型主类完整分布 + 下周P3（全量7461只）
2. 波型三段（地型/主类/层界）各自区分力
3. 波型 × WXCD 交互
4. 波型 × WXAB 交互
5. 波型主类内部细分（龙猪/震正/头正 的根/芽/〇细分）
6. 层界（破/储/初/再/主）对波型的调节

用法：
    python _产出物/MC3.9c_周波型深度分析.py

输出：
    - 控制台 + _产出物/MC3.9c_周波型深度分析.txt
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

def table(title, items, label_width=26):
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
print('MC3.9c 周波型深度分析')
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

# ── 1. 波型主类完整分布 ──
print('\n[1] 波型主类完整分布')
mainclasses = sorted(wk['主类'].dropna().unique())
items = [(mc, wk['主类'] == mc) for mc in mainclasses]
out = table('1. 波型主类完整分布（全量7461只）', items)
print(out); output.append(out)

# ── 2. 三段各自区分力 ──
print('\n[2] 波型三段各自区分力')
# 地型
dixing = sorted(wk['地型'].dropna().unique())
items = [(f'地型={d}', wk['地型'] == d) for d in dixing]
out = table('2a. 地型（位1）区分力', items)
print(out); output.append(out)
# 层界
cengjie = sorted(wk['层界'].dropna().unique())
items = [(f'层界={c}', wk['层界'] == c) for c in cengjie]
out = table('2b. 层界（位3）区分力', items)
print(out); output.append(out)

# ── 3. 波型 × WXCD 交互 ──
print('\n[3] 波型 × WXCD 交互')
m_good = wk['WXCD'].str.contains('金|银', na=False)
m_bad = ~wk['WXCD'].str.contains('金|银', na=False)
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Fd震正芽', 'Ff震负', 'Df头负', 'Dd头正芽', 'De头正根', 'Bc龙管栅', 'Be龙管根', 'Bd龙管杂', 'Bb龙管杂']:
    m = wk['主类'] == mc
    items = [
        (f'{mc}+金/银升', m & m_good),
        (f'{mc}+唏嘘尿屎', m & m_bad),
    ]
    out = table(f'3. {mc} × WXCD', items)
    print(out); output.append(out)

# ── 4. 波型 × WXAB 交互 ──
print('\n[4] 波型 × WXAB 交互')
m_ab_good = wk['WXAB'].str.contains('甲|乙|己', na=False)
m_ab_bad = wk['WXAB'].str.contains('丙|丁|戊', na=False)
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Fd震正芽', 'Ff震负', 'Df头负', 'Dd头正芽', 'Bc龙管栅']:
    m = wk['主类'] == mc
    items = [
        (f'{mc}+甲乙己', m & m_ab_good),
        (f'{mc}+丙丁戊', m & m_ab_bad),
    ]
    out = table(f'4. {mc} × WXAB', items)
    print(out); output.append(out)

# ── 5. 主类内部细分（根/芽/〇） ──
print('\n[5] 主类内部细分')
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Fd震正芽', 'Dd头正芽', 'De头正根', 'Df头负', 'Ff震负']:
    m = wk['主类'] == mc
    p, n = rep(m)
    if p is not None:
        print(f'  {mc:<12s} n={n:>9,d}  P3={p:>5.1f}%  vs基线{p-baseline:>+5.1f}pp')

# ── 6. 层界对主类的调节 ──
print('\n[6] 层界对主类的调节')
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Fd震正芽', 'Ff震负', 'Df头负']:
    m = wk['主类'] == mc
    items = []
    for cj in ['破', '储', '初', '再', '主']:
        items.append((f'{mc}+{cj}', m & wk['层界'].str.startswith(cj, na=False)))
    out = table(f'6. {mc} × 层界', items)
    print(out); output.append(out)

# ── 写入文件 ──
outpath = os.path.join(OUTDIR, 'MC3.9c_周波型深度分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')