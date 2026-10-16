#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表周策分P3.txt
全量周CSV → 按金银×四波×柱型 三维组合计算P3概率
输出：策略\t编码（期望HR取整(截断9)+等级(G/_)+P3取整）
金银：金/银/唏（WXZC>0下仅此三类）
四波：龙/武/虎/雀（WXAB&WXZB）
柱型：升吞O/升连Q/升孕o/跌吞V/跌连W/跌孕v（并符串周尾字符）
2026-10-16 新设计：从第一性原理（金银区分度最高18pp）恢复金银维度
"""

import glob, pandas as pd, os

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物/_工具'
MIN_SAMPLE = 1000

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

def match_strategy(row):
    """金银×四波×柱型 策略匹配（2026-10-16 新设计）。
    金银：周势型[12]第2字符（金/银/唏）
    四波：龙=WXAB>0且WXZB>0、武=WXAB<0且WXZB>0、虎=WXAB<0且WXZB<0、雀=WXAB>0且WXZB<0
    柱型：并符串周[51]尾字符（O升吞/Q升连/o升孕/V跌吞/W跌连/v跌孕）
    """
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
    # 柱型（并符串尾字符）
    bf = str(row.get('并符串周', '')) if pd.notna(row.get('并符串周')) else ''
    zx = bf[-1] if bf else ''
    zx_map = {'O': '升吞', 'Q': '升连', 'o': '升孕', 'V': '跌吞', 'W': '跌连', 'v': '跌孕'}
    zx_name = zx_map.get(zx, '')
    if not zx_name:
        return ''
    return f'{jy}{bo}{zx_name}'

print('=== 生成 vba表周策分P3.txt（金银×四波×柱型）===')
wk = load()
wk['策略'] = wk.apply(match_strategy, axis=1)
valid = wk[wk['策略'] != '']
print(f'  有策略: {len(valid)} 行 ({len(valid)/len(wk)*100:.1f}%)')

results = []
# 全量基准
n = len(wk)
p3 = round((wk['下周HR'] >= 3).mean() * 100, 1)
avg = wk['下周HR'].mean()
results.append(('全量基准', encode(p3, avg), n, p3, avg))

# 各策略组合（样本>=1000）
for s, m in valid.groupby('策略'):
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