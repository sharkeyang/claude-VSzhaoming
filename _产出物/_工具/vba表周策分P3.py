#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表周策分P3.txt
全量7461只周CSV → 按策略匹配计算P3概率
输出：策略\t编码（期望HR取整(截断9)+等级(A-F)+P3取整）
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
    if p3 >= 90: g = 'A'
    elif p3 >= 80: g = 'B'
    elif p3 >= 70: g = 'C'
    elif p3 >= 60: g = 'D'
    elif p3 >= 50: g = 'E'
    else: g = 'F'
    return f'{h}{g}{int(p3):02d}'

def match_strategy(row):
    cd2 = str(row.get('WXCD', ''))[:2]
    abh = str(row.get('WXAB', ''))[1:2] if pd.notna(row.get('WXAB')) else ''
    zp = str(row.get('柱排周', '')) if pd.notna(row.get('柱排周')) else ''
    zy = str(row.get('盈提示', '')) if pd.notna(row.get('盈提示')) else ''
    bx = str(row.get('波型', '')) if pd.notna(row.get('波型')) else ''
    za = row.get('ZA周', 0)
    if pd.isna(za): za = 0
    if '金' in cd2 and (abh in ['甲', '乙', '己']):
        if zp.startswith('升') and '尾反孕' not in zp:
            if '高' in str(zy):
                if '龙猪' in str(bx) or '龙管' in str(bx): return '金升非盈龙'
                else: return '金升非盈'
            else: return '金升非'
        elif zp.startswith('升'): return '金升'
        else: return '金长'
    elif '银' in cd2:
        if '高' in str(zy) or '宽' in str(zy): return '银盈'
        elif '己' in abh: return '银己'
        elif zp.startswith('升'): return '银升'
        elif '龙猪' in str(bx): return '银猪'
        elif za > 5 and za <= 10: return '银ZA'
    return ''

print('=== 生成 vba表周策分P3.txt ===')
wk = load()
wk['策略'] = wk.apply(match_strategy, axis=1)
valid = wk[wk['策略'] != '']
print(f'  有策略: {len(valid)} 行')

strategies = ['全量基准', '金最优(全部)', '金升非盈龙', '金升非盈', '金升非', '金升', '金长', '银盈', '银己', '银升', '银猪', '银ZA']
results = []
for s in strategies:
    if s == '全量基准':
        m = wk  # 全量基准用全部行
    elif s == '金最优(全部)':
        m = valid[valid['策略'].isin(['金升非盈龙', '金升非盈', '金升非', '金升'])]
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