#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9b_波型柱排组合P3.py
=====================
波型×柱排 二维组合下周P3验证，对标 MC3.1 §9.1（月基分周基础分查表）。

组合：
- 波型：龙猪 / 头正 / 震正 / 其他
- 柱排：升排 / 跌排 / 其他

用法：
    python _产出物/MC3.9b_波型柱排组合P3.py

输出：
    - 控制台 + _产出物/MC3.9b_波型柱排组合P3.txt
"""

import pandas as pd, os, glob, sys, warnings
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物'
MIN_SAMPLE = 100
os.makedirs(OUTDIR, exist_ok=True)

def load_all():
    """加载所有周CSV为一个DataFrame，附加下周HR"""
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
        return None, n, 0
    nh3 = (g['下周HR'] >= 3).mean() * 100
    return nh3, n, sum(g['下周HR'] >= 3)

print('=' * 80)
print('MC3.9b 波型×柱排 组合P3验证')
print('=' * 80)
print()
wk = load_all()

baseline = (wk['下周HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n全样本: {total} 行, 基线下周P3 = {baseline:.1f}%')
print('=' * 80)

# 波型分类
m_lz = wk['波型'].str.contains('龙猪', na=False)          # 龙猪
m_tz = wk['波型'].str.contains('头正', na=False)          # 头正
m_zz = wk['波型'].str.contains('震正', na=False)          # 震正
m_other = ~(m_lz | m_tz | m_zz)                          # 其他

# 柱排分类
m_up = wk['柱排周'].str.contains('升', na=False)          # 升排
m_dn = wk['柱排周'].str.contains('跌', na=False)          # 跌排
m_other_p = ~(m_up | m_dn)                               # 其他柱排

combos = [
    ('龙猪+升排', m_lz & m_up),
    ('龙猪+跌排', m_lz & m_dn),
    ('龙猪+其他排', m_lz & m_other_p),
    ('头正+升排', m_tz & m_up),
    ('头正+跌排', m_tz & m_dn),
    ('头正+其他排', m_tz & m_other_p),
    ('震正+升排', m_zz & m_up),
    ('震正+跌排', m_zz & m_dn),
    ('震正+其他排', m_zz & m_other_p),
    ('其他+升排', m_other & m_up),
    ('其他+跌排', m_other & m_dn),
    ('其他+其他排', m_other & m_other_p),
]

lines = [f'\n{"=" * 80}', '波型×柱排 组合下周P3', '=' * 80,
         f'{"组合":<14s}  {"样本":>9s}  {"P3%":>7s}  {"vs基线":>7s}',
         '-' * 50]
results = []
for name, mask in combos:
    p, n, s = rep(mask)
    if p is None:
        lines.append(f'{name:<14s}  {n:>9,d}  {"-":>7s}  {"-":>7s}  (样本不足)')
    else:
        diff = p - baseline
        lines.append(f'{name:<14s}  {n:>9,d}  {p:>6.1f}%  {diff:>+7.1f}pp')
        results.append((p, name, n))

lines.append('')
out = '\n'.join(lines)
print(out)

# 排序汇总
results.sort(key=lambda x: -x[0])
lines2 = ['\n' + '=' * 80, '组合排序（按下周P3降序）', '=' * 80,
          f'{"排序":>4s}  {"组合":<14s}  {"样本":>9s}  {"P3%":>7s}  {"vs基线":>7s}',
          '-' * 50]
for rank, (p, name, n) in enumerate(results, 1):
    diff = p - baseline
    lines2.append(f'{rank:>4d}  {name:<14s}  {n:>9,d}  {p:>6.1f}%  {diff:>+7.1f}pp')
lines2.append('')
out2 = '\n'.join(lines2)
print(out2)

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9b_波型柱排组合P3.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(out + out2)
print(f'\n结果已写入: {outpath}')