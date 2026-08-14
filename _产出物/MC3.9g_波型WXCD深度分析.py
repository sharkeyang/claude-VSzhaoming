#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9g_波型WXCD深度分析.py
=====================
波型 × WXCD 组合全量深度分析。

分析维度：
1. 波型主类 × WXCD（金银升/唏嘘尿屎）全量P3
2. 地型 × WXCD 全量P3
3. 波型主类 × WXCD × 层界 三维组合
4. 波型主类 × WXCD × 地型 三维组合
5. 最优组合排序

用法：
    python _产出物/MC3.9g_波型WXCD深度分析.py

输出：
    - 控制台 + _产出物/MC3.9g_波型WXCD深度分析.txt
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

def table(title, items, label_width=34):
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
print('MC3.9g 波型×WXCD 深度分析')
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

# WXCD分类
m_gold = wk['WXCD'].str.contains('金', na=False)
m_silver = wk['WXCD'].str.contains('银', na=False)
m_xi = wk['WXCD'].str.contains('唏', na=False)
m_xu = wk['WXCD'].str.contains('嘘', na=False)
m_niao = wk['WXCD'].str.contains('尿', na=False)
m_shi = wk['WXCD'].str.contains('屎', na=False)
m_good = m_gold | m_silver
m_bad = ~m_good

# 升势/跌势
m_up = ~wk['主类'].str.startswith('__', na=False)

# ── 1. 波型主类 × WXCD 全量 ──
print('\n[1] 波型主类 × WXCD')
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Fd震正芽', 'Ff震负', 'Df头负', 'Dd头正芽', 'De头正根', 'Bc龙管栅', 'Be龙管根', 'Bb龙管杂']:
    m_mc = wk['主类'] == mc
    items = [
        (f'{mc}+金升', m_mc & m_gold),
        (f'{mc}+银升', m_mc & m_silver),
        (f'{mc}+唏', m_mc & m_xi),
        (f'{mc}+嘘', m_mc & m_xu),
        (f'{mc}+尿', m_mc & m_niao),
        (f'{mc}+屎', m_mc & m_shi),
    ]
    out = table(f'1. {mc} × WXCD', items)
    print(out); output.append(out)

# ── 2. 地型 × WXCD ──
print('\n[2] 地型 × WXCD')
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    m_d = wk['地型'] == d
    items = [
        (f'{d}+金升', m_d & m_gold),
        (f'{d}+银升', m_d & m_silver),
        (f'{d}+唏', m_d & m_xi),
        (f'{d}+嘘', m_d & m_xu),
        (f'{d}+尿', m_d & m_niao),
        (f'{d}+屎', m_d & m_shi),
    ]
    out = table(f'2. 地型{d} × WXCD', items)
    print(out); output.append(out)

# ── 3. 波型主类 × WXCD × 层界 三维 ──
print('\n[3] 波型主类 × WXCD × 层界')
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Df头负']:
    m_mc = wk['主类'] == mc
    for cj in ['破', '储', '初', '再', '主']:
        m_cj = wk['层界'].str.startswith(cj, na=False)
        items = [
            (f'{mc}+{cj}+金银升', m_mc & m_cj & m_good),
            (f'{mc}+{cj}+屎', m_mc & m_cj & m_shi),
        ]
        out = table(f'3. {mc}+{cj} × WXCD', items)
        print(out); output.append(out)

# ── 4. 最优组合排序 ──
print('\n[4] 最优组合排序（按下周P3降序）')
all_combos = []
# 波型主类 × WXCD
for mc in ['Aa龙猪', 'Fa震正〇', 'Fe震正根', 'Fd震正芽', 'Ff震负', 'Df头负', 'Dd头正芽', 'De头正根', 'Bc龙管栅', 'Be龙管根', 'Bb龙管杂']:
    m_mc = wk['主类'] == mc
    for cd_label, m_cd in [('金升', m_gold), ('银升', m_silver), ('唏', m_xi), ('嘘', m_xu), ('尿', m_niao), ('屎', m_shi)]:
        all_combos.append((f'{mc}+{cd_label}', m_mc & m_cd))
# 地型 × WXCD
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    m_d = wk['地型'] == d
    for cd_label, m_cd in [('金升', m_gold), ('银升', m_silver), ('屎', m_shi)]:
        all_combos.append((f'{d}+{cd_label}', m_d & m_cd))

results = []
for name, mask in all_combos:
    p, n = rep(mask)
    if p is not None:
        results.append((p, name, n))

results.sort(key=lambda x: -x[0])
lines = [f'\n{"=" * 80}',
         '4. 最优组合排序（按下周P3降序，全量7461只）',
         '=' * 80,
         f'{"排序":>4s}  {"组合":<28s}  {"样本":>9s}  {"P3%":>7s}  {"vs基线":>7s}',
         '-' * 60]
for rank, (p, name, n) in enumerate(results[:40], 1):
    diff = p - baseline
    lines.append(f'{rank:>4d}  {name:<28s}  {n:>9,d}  {p:>6.1f}%  {diff:>+7.1f}pp')
lines.append('')
out = '\n'.join(lines)
print(out); output.append(out)

# ── 写入文件 ──
outpath = os.path.join(OUTDIR, 'MC3.9g_波型WXCD深度分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')