#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表周策分P3.txt
全量周CSV → 按金银×四波×柱型 计算P3概率，输出两个维度：
  维度1（周策略P3列）：金银×四波×柱型（不含盈提示），P≥3%≥60% → 13组合，策略名如"金龙Q"
  维度2（筛选）：金银×四波×柱型+盈提示"高"，P≥3%≥70% → 11组合，策略名如"金龙Q高"
输出：策略\t编码（期望HR取整(截断9)+等级(G/_)+P3取整）
金银：金/银/唏（WXZC>0下仅此三类）
四波：龙/武/虎/雀（WXAB&WXZB）
柱型：升吞O/升连Q/升孕o/跌吞V/跌连W/跌孕v（并符串周尾字符）
2026-10-19 双维度分层：周策略P3列范围大(≥60%)，筛选把握大(≥70%)
"""

import glob, pandas as pd, os

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物/_工具'
MIN_SAMPLE = 1000

# 维度1：13组合（不含盈提示，P≥3%≥60%）
DIM1_BASE = ('金龙Q', '金龙O', '银龙Q', '金龙v', '银龙v', '金武Q', '金武O',
             '金武v', '金武o', '银龙O', '银武Q', '唏龙Q', '唏武O')
# 维度2：11组合（含盈提示"高"，P≥3%≥70%）
DIM2_BASE = ('金龙Q', '银龙Q', '金龙O', '唏龙Q', '金龙o', '唏武Q', '金武Q',
             '银龙O', '金武O', '金龙v', '唏龙O')

def load():
    files = sorted(glob.glob(os.path.join(DATADIR, '谕组周_*.csv')))
    dfs = []
    for i, f in enumerate(files):
        if i % 1000 == 0: print(f'  [加载] {i}/{len(files)}...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) >= 2:
                df['fid'] = i
                dfs.append(df)
        except: pass
    wk = pd.concat(dfs, ignore_index=True)
    wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
    wk = wk.dropna(subset=['下周HR'])
    print(f'  完成: {len(wk)} 行')
    return wk

def encode(p3, avg):
    h = int(avg) if avg >= 0 else 0
    if h > 9: h = 9
    if p3 >= 51: g = 'G'
    else: g = '_'
    return f'{h}{g}{int(p3):02d}'

def get_combo(row):
    """计算金银×四波×柱型字母 组合名（不含盈提示）。"""
    wxab = row.get('AB周', 0)
    wxzb = row.get('ZB周', 0)
    if pd.isna(wxab): wxab = 0
    if pd.isna(wxzb): wxzb = 0
    # 金银
    jy = str(row.get('周势型(WXCD护型)', '')) if pd.notna(row.get('周势型(WXCD护型)')) else ''
    jy = jy[1] if len(jy) >= 2 else ''
    if jy not in ('金', '银', '唏'):
        return ''
    # 四波
    if wxab > 0 and wxzb > 0:
        bo = '龙'
    elif wxab < 0 and wxzb > 0:
        bo = '武'
    elif wxab < 0 and wxzb < 0:
        bo = '虎'
    elif wxab > 0 and wxzb < 0:
        bo = '雀'
    else:
        return ''
    # 柱型（并符串尾字符，字母）
    bf = str(row.get('并符串周', '')) if pd.notna(row.get('并符串周')) else ''
    zx = bf[-1] if bf else ''
    if zx not in ('O', 'Q', 'o', 'V', 'W', 'v'):
        return ''
    return f'{jy}{bo}{zx}'

def get_strategies(row):
    """返回 (维度1策略名, 维度2策略名)。维度1不含盈提示，维度2含盈提示"高"。"""
    combo = get_combo(row)
    if not combo:
        return ('', '')
    # 维度1：combo 在13组合base名单中（不含盈提示）
    s1 = combo if combo in DIM1_BASE else ''
    # 维度2：combo 在11组合base名单中 且 盈提示含"高"
    yt = str(row.get('盈提示', '')) if pd.notna(row.get('盈提示')) else ''
    s2 = (combo + '高') if (combo in DIM2_BASE and '高' in yt) else ''
    return (s1, s2)

print('=== 生成 vba表周策分P3.txt（双维度：周策略P3列≥60% + 筛选≥70%）===')
wk = load()
strat = wk.apply(get_strategies, axis=1)
wk['策略1'] = [s[0] for s in strat]   # 维度1：周策略P3列
wk['策略2'] = [s[1] for s in strat]   # 维度2：筛选

results = []
# 全量基准
n = len(wk)
p3 = round((wk['下周HR'] >= 3).mean() * 100, 1)
avg = wk['下周HR'].mean()
results.append(('全量基准', encode(p3, avg), n, p3, avg))

# 维度1：13组合（不含盈提示）
for s, m in wk[wk['策略1'] != ''].groupby('策略1'):
    n = len(m)
    if n >= MIN_SAMPLE:
        p3 = round((m['下周HR'] >= 3).mean() * 100, 1)
        avg = m['下周HR'].mean()
        code = encode(p3, avg)
        results.append((s, code, n, p3, avg))

# 维度2：11组合（含盈提示"高"）
for s, m in wk[wk['策略2'] != ''].groupby('策略2'):
    n = len(m)
    if n >= MIN_SAMPLE:
        p3 = round((m['下周HR'] >= 3).mean() * 100, 1)
        avg = m['下周HR'].mean()
        code = encode(p3, avg)
        results.append((s, code, n, p3, avg))

results.sort(key=lambda x: -x[3])
lines = ['策略\t编码']
for s, code, n, p3, avg in results:
    lines.append(f'{s}\t{code}')
outpath = os.path.join(OUTDIR, 'vba表周策分P3.txt')
with open(outpath, 'w', encoding='gbk') as f:
    f.write('\n'.join(lines))
print(f'  共{len(results)}个策略 -> {outpath}')
