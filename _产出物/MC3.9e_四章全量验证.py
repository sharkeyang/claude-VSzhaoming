#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9e_四章全量验证.py
=====================
用全量7461只周CSV更新 MC3.1 §四（验证结果）所需数据。

计算：
1. 6等全量P3（等1/等2/等3/等5/等6/等7，按ZA周+中符串周末位）
2. ZA周正负区分度
3. WXCD × 波型组合
4. 各指标全量P3汇总

用法：
    python _产出物/MC3.9e_四章全量验证.py

输出：
    - 控制台 + _产出物/MC3.9e_四章全量验证.txt
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

print('=' * 80)
print('MC3.9e 四章全量验证')
print('=' * 80)
print()
wk = load_all()

baseline = (wk['下周HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n全样本: {total} 行, 基线下周P3 = {baseline:.1f}%')
print('=' * 80)

output = []

# 确认列名
print('\n[0] 列名确认')
for c in ['ZA周', '中符串周', '波型', '柱排周', 'WXCD', 'WXAB', 'HR']:
    print(f'  {c}: {"OK" if c in wk.columns else "MISSING"}')

# ── 1. 6等全量P3 ──
print('\n[1] 6等全量P3')
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['末位'] = wk['中符串周'].astype(str).str[-1] if '中符串周' in wk.columns else ''

def deng(mask):
    p, n = rep(mask)
    return p, n

# 6等定义
m1 = wk['ZA周'] == 1
m2 = (wk['ZA周'] >= 2) & (wk['末位'].isin(['C','D','E','F']))
m3 = (wk['ZA周'] >= 2) & (wk['末位'].isin(['A','B']))
m5 = wk['ZA周'] == -1
m6 = (wk['ZA周'] <= -2) & (wk['末位'].isin(['A','B','C','D']))
m7 = (wk['ZA周'] <= -2) & (wk['末位'].isin(['E','F']))

deng_items = [
    ('等1 (ZA=1)', m1),
    ('等2 (ZA≥2+CDEF)', m2),
    ('等3 (ZA≥2+AB)', m3),
    ('等5 (ZA=-1)', m5),
    ('等6 (ZA≤-2+ABCD)', m6),
    ('等7 (ZA≤-2+EF)', m7),
]
lines = [f'\n{"=" * 80}', '1. 6等全量P3（全量7461只）', '=' * 80,
         f'{"等级":<22s}  {"样本":>9s}  {"P3%":>7s}  {"vs基线":>7s}',
         '-' * 50]
for name, mask in deng_items:
    p, n = deng(mask)
    if p is None:
        lines.append(f'{name:<22s}  {n:>9,d}  {"-":>7s}  {"-":>7s}  (样本不足)')
    else:
        lines.append(f'{name:<22s}  {n:>9,d}  {p:>6.1f}%  {p-baseline:>+7.1f}pp')
lines.append('')
out = '\n'.join(lines)
print(out); output.append(out)

# ── 2. ZA周正负区分度 ──
print('\n[2] ZA周正负区分度')
items = [
    ('ZA周>0（站上WJA）', wk['ZA周'] > 0),
    ('ZA周≤0（跌破WJA）', wk['ZA周'] <= 0),
    ('ZA周>3（远离WJA）', wk['ZA周'] > 3),
    ('ZA周=-1（刚跌破）', wk['ZA周'] == -1),
]
lines = [f'\n{"=" * 80}', '2. ZA周正负区分度', '=' * 80,
         f'{"条件":<22s}  {"样本":>9s}  {"P3%":>7s}  {"vs基线":>7s}',
         '-' * 50]
for name, mask in items:
    p, n = rep(mask)
    if p is None:
        lines.append(f'{name:<22s}  {n:>9,d}  {"-":>7s}  {"-":>7s}')
    else:
        lines.append(f'{name:<22s}  {n:>9,d}  {p:>6.1f}%  {p-baseline:>+7.1f}pp')
lines.append('')
out = '\n'.join(lines)
print(out); output.append(out)

# ── 3. WXCD × 波型组合 ──
print('\n[3] WXCD × 波型组合')
m_cd_good = wk['WXCD'].str.contains('金|银', na=False)
m_cd_bad = ~wk['WXCD'].str.contains('金|银', na=False)
m_lz = wk['波型'].str.contains('Aa龙猪', na=False)
items = [
    ('金银升+Aa龙猪', m_cd_good & m_lz),
    ('屎降+Aa龙猪', wk['WXCD'].str.contains('屎', na=False) & m_lz),
    ('唏嘘尿屎+Aa龙猪', m_cd_bad & m_lz),
    ('金银升+Fa震正〇', m_cd_good & wk['波型'].str.contains('Fa震正〇', na=False)),
    ('屎降+Fa震正〇', wk['WXCD'].str.contains('屎', na=False) & wk['波型'].str.contains('Fa震正〇', na=False)),
]
lines = [f'\n{"=" * 80}', '3. WXCD × 波型组合', '=' * 80,
         f'{"组合":<22s}  {"样本":>9s}  {"P3%":>7s}  {"vs基线":>7s}',
         '-' * 50]
for name, mask in items:
    p, n = rep(mask)
    if p is None:
        lines.append(f'{name:<22s}  {n:>9,d}  {"-":>7s}  {"-":>7s}')
    else:
        lines.append(f'{name:<22s}  {n:>9,d}  {p:>6.1f}%  {p-baseline:>+7.1f}pp')
lines.append('')
out = '\n'.join(lines)
print(out); output.append(out)

# ── 4. 各指标全量P3汇总 ──
print('\n[4] 各指标全量P3汇总')
items = [
    ('周波型 Aa龙猪', wk['波型'].str.contains('Aa龙猪', na=False)),
    ('周波型 Fa震正〇', wk['波型'].str.contains('Fa震正〇', na=False)),
    ('周柱排 升.尾反孕', wk['柱排周'].str.contains('升.尾反孕', na=False)),
    ('周柱排 跌.尾吞', wk['柱排周'].str.contains('跌.尾吞', na=False)),
    ('WXCD 金/银升', m_cd_good),
    ('WXCD 屎降', wk['WXCD'].str.contains('屎', na=False)),
    ('WXAB 甲', wk['WXAB'].str.contains('甲', na=False)),
    ('WXAB 丙', wk['WXAB'].str.contains('丙', na=False)),
]
lines = [f'\n{"=" * 80}', '4. 各指标全量P3汇总', '=' * 80,
         f'{"指标":<22s}  {"样本":>9s}  {"P3%":>7s}  {"vs基线":>7s}',
         '-' * 50]
for name, mask in items:
    p, n = rep(mask)
    if p is None:
        lines.append(f'{name:<22s}  {n:>9,d}  {"-":>7s}  {"-":>7s}')
    else:
        lines.append(f'{name:<22s}  {n:>9,d}  {p:>6.1f}%  {p-baseline:>+7.1f}pp')
lines.append('')
out = '\n'.join(lines)
print(out); output.append(out)

# ── 写入文件 ──
outpath = os.path.join(OUTDIR, 'MC3.9e_四章全量验证.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')