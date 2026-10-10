#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表周策分P3.txt
全量7461只周CSV → 按四态策略匹配计算P3概率
输出：策略\t编码（期望HR取整(截断9)+等级(A-F)+P3取整）
四态（2026-10-07 替换金银）：龙/虎/武/雀
"""

import glob, pandas as pd, os

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物/_工具'
MIN_SAMPLE = 100

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
    """四态策略匹配（2026-10-07 替换金银）。
    四态：龙=WXAB>0且WXZB>0、武=WXAB<0且WXZB>0、虎=WXAB<0且WXZB<0、雀=WXAB>0且WXZB<0。
    每个四态叠加柱排/盈提示等条件形成策略。
    """
    wxab = row.get('AB周', 0)
    wxzb = row.get('ZB周', 0)
    if pd.isna(wxab): wxab = 0
    if pd.isna(wxzb): wxzb = 0
    zp = str(row.get('柱排周', '')) if pd.notna(row.get('柱排周')) else ''
    zy = str(row.get('盈提示', '')) if pd.notna(row.get('盈提示')) else ''
    # 四态判定
    if wxab > 0 and wxzb > 0:
        sitai = '龙'  # 升主龙
    elif wxab < 0 and wxzb > 0:
        sitai = '武'  # 降转武
    elif wxab < 0 and wxzb < 0:
        sitai = '虎'  # 降主虎
    elif wxab > 0 and wxzb < 0:
        sitai = '雀'  # 升转雀
    else:
        return ''
    # 四态策略：叠加柱排/盈提示
    if sitai == '龙':
        if zp.startswith('升'): return '龙升'
        elif '高' in zy or '宽' in zy: return '龙盈'
        else: return '龙长'
    elif sitai == '武':
        if zp.startswith('升'): return '武升'
        elif '高' in zy or '宽' in zy: return '武盈'
        else: return '武长'
    elif sitai == '虎':
        if zp.startswith('跌'): return '虎跌'
        else: return '虎长'
    else:  # 雀
        return '雀'

print('=== 生成 vba表周策分P3.txt ===')
wk = load()
wk['策略'] = wk.apply(match_strategy, axis=1)
valid = wk[wk['策略'] != '']
print(f'  有策略: {len(valid)} 行')

strategies = ['全量基准', '龙最优(全部)', '龙升', '龙盈', '龙长', '武升', '武盈', '武长', '虎跌', '虎长', '雀']
results = []
for s in strategies:
    if s == '全量基准':
        m = wk  # 全量基准用全部行
    elif s == '龙最优(全部)':
        m = valid[valid['策略'].isin(['龙升', '龙盈', '龙长'])]
    else:
        m = valid[valid['策略'] == s]
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