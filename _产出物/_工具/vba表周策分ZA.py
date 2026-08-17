#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表周策分ZA.txt
基于WXZA维持概率研究（柱排+顶触+盈提示三维分类）
输出：名称\t编码（期望HR取整+G/_+维持率取整）
"""
import glob, pandas as pd, os
from collections import defaultdict

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物/_工具'
MIN_SAMPLE = 100

def load():
    files = sorted(glob.glob(os.path.join(DATADIR, '谕组周_*.csv')))
    dfs = []
    for i, f in enumerate(files):
        if i % 1000 == 0: print(f'  [加载] {i}/{len(files)}...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk', usecols=['ZA周','柱排周','顶触周','盈提示','HR'])
            if len(df) >= 2:
                df['fid'] = i
                dfs.append(df)
        except: pass
    wk = pd.concat(dfs, ignore_index=True)
    wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
    wk = wk.dropna(subset=['下周HR'])
    print(f'  完成: {len(wk)} 行')
    return wk

def encode(keep_rate):
    """编码：期望HR取整 + G/_ + 维持率取整
    keep_rate = 维持WXZA>0概率（%），如 78.7
    编码格式：期望HR取整(0-9) + G/_ + 维持率取整(00-99)
    """
    h = int(keep_rate / 10) if keep_rate >= 0 else 0
    if h > 9: h = 9
    if keep_rate >= 50: g = 'G'
    else: g = '_'
    return f'{h}{g}{int(keep_rate):02d}'

def seg_zp(zp):
    if pd.isna(zp): return '其他'
    s = str(zp)
    if s.startswith('跌.尾连'): return '连跌'
    elif s.startswith('跌.尾吞'): return '跌吞'
    elif '吞吞' in s: return '阴阳阴'
    elif s.startswith('跌.尾反孕'): return '跌反孕'
    elif s.startswith('升.尾连'): return '连阳'
    elif s.startswith('升.尾吞'): return '升吞'
    elif s.startswith('升.尾反孕'): return '升反孕'
    elif '孕孕' in s: return '孕孕'
    else: return '其他'

def seg_dc(dc):
    if pd.isna(dc): return '其他'
    s = str(dc)
    if '高' in s: return '触高'
    elif '撤' in s: return '离撤'
    else: return '其他'

def seg_yt(yt):
    if pd.isna(yt) or str(yt).strip() == '': return '其他'
    s = str(yt)
    if '宽高连3' in s: return '宽高连3'
    elif '连3' in s: return '连3'
    elif '宽高' in s: return '宽高'
    elif '高' in s: return '高'
    elif '宽' in s: return '宽'
    else: return '其他'

print('=== 生成 vba表周策分ZA.txt ===')
wk = load()
# 先计算下周ZA，再过滤ZA>0
wk['下周ZA'] = wk.groupby('fid')['ZA周'].shift(-1)
wk = wk.dropna(subset=['下周ZA'])
# 只分析ZA>0（站上WJA）的样本
wk = wk[wk['ZA周'] > 0].copy()
wk['柱排'] = wk['柱排周'].apply(seg_zp)
wk['顶触'] = wk['顶触周'].apply(seg_dc)
wk['盈提示'] = wk['盈提示'].apply(seg_yt)
wk['维持'] = (wk['下周ZA'] >= 0).astype(int)

results = []
# 按柱排+顶触+盈提示分组
for zp_name in ['连阳','升吞','升反孕','阴阳阴','孕孕','跌反孕','跌吞','连跌','其他']:
    for dc_name in ['触高','离撤','其他']:
        for yt_name in ['宽高连3','连3','宽高','高','宽','其他']:
            mask = (wk['柱排'] == zp_name) & (wk['顶触'] == dc_name) & (wk['盈提示'] == yt_name)
            n = mask.sum()
            if n >= MIN_SAMPLE:
                g = wk[mask]
                keep_rate = round(g['维持'].mean() * 100, 1)
                code = encode(keep_rate)
                name = f'{zp_name}|{dc_name}|{yt_name}'
                results.append((keep_rate, code, name, n))

results.sort(key=lambda x: -x[0])
lines = ['名称\t编码']
for keep_rate, code, name, n in results:
    lines.append(f'{name}\t{code}')
outpath = os.path.join(OUTDIR, 'vba表周策分ZA.txt')
with open(outpath, 'w', encoding='gbk') as f:
    f.write('\n'.join(lines))
print(f'  共{len(results)}个组合 -> {outpath}')