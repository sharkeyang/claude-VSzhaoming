#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成 vba表周策分P1.txt
全量7461只周CSV → 按完整梯度框架（ZA分段+等类+地型+柱排+WXCD+WXAB）计算P1概率
输出：名称\t编码（期望HR取整+等级(A-F)+P1取整）
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

def seg(w, i):
    if pd.isna(w): return ''
    parts = str(w).split('.')
    return parts[i] if len(parts) > i else ''

def encode(p1, avg):
    h = int(avg) if avg >= 0 else 0
    if h > 9: h = 9
    if p1 >= 78: g = 'G'
    else: g = '_'
    return f'{h}{g}{int(p1):02d}'

def make_name(eq, d, zp, cd, ab):
    return f'{eq}_{d}_{zp}_{{{cd}_{ab}}}'

print('=== 生成 vba表周策分P1.txt ===')
wk = load()
wk['地型'] = wk['波型'].apply(lambda w: seg(w, 0))
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['末位'] = wk['中符串周'].astype(str).str[-1]

m_up = wk['柱排周'].str.contains('升', na=False)
m_dn = wk['柱排周'].str.contains('跌', na=False)
m_ren = ~(m_up | m_dn)
m1 = wk['ZA周'] == 1
m2 = (wk['ZA周'] >= 2) & wk['末位'].isin(['C', 'D', 'E', 'F'])
m3 = (wk['ZA周'] >= 2) & wk['末位'].isin(['A', 'B'])
m5 = wk['ZA周'] == -1
m6 = (wk['ZA周'] <= -2) & wk['末位'].isin(['A', 'B', 'C', 'D'])
m7 = (wk['ZA周'] <= -2) & wk['末位'].isin(['E', 'F'])
m_za_pos = wk['ZA周'] > 0
m_za_neg = wk['ZA周'] < 0
m_gold = wk['WXCD'].str.contains('金', na=False)
m_silver = wk['WXCD'].str.contains('银', na=False)
m_xi = wk['WXCD'].str.contains('唏', na=False)
m_xu = wk['WXCD'].str.contains('嘘', na=False)
m_niao = wk['WXCD'].str.contains('尿', na=False)
m_shi = wk['WXCD'].str.contains('屎', na=False)
m_ab_good = wk['WXAB'].str.contains('甲|乙|己', na=False)
m_ab_bad = wk['WXAB'].str.contains('丙|丁|戊', na=False)

za_configs = [
    ('ZA>0', m_za_pos, [('等3', m3), ('等2', m2), ('等1', m1)], ['0橅', '1柜', '2栅', '3桮']),
    ('ZA<0', m_za_neg, [('等7', m7), ('等6', m6), ('等5', m5)], ['6娝', '7姗', '8姖', '9妩']),
]
wxcd_configs = [('金', m_gold), ('银', m_silver), ('唏', m_xi), ('嘘', m_xu), ('尿', m_niao), ('屎', m_shi)]
wxab_configs = [('甲乙己', m_ab_good), ('丙丁戊', m_ab_bad)]

results = []
for za_name, za_mask, eq_list, dx_list in za_configs:
    for eq_name, eq_mask in eq_list:
        for d in dx_list:
            for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
                for cd_name, cd_mask in wxcd_configs:
                    for ab_name, ab_mask in wxab_configs:
                        mask = za_mask & eq_mask & (wk['地型'] == d) & zp_mask & cd_mask & ab_mask
                        n = mask.sum()
                        if n >= MIN_SAMPLE:
                            g = wk.loc[mask]
                            p1 = round((g['下周HR'] >= 1).mean() * 100, 1)
                            avg = g['下周HR'].mean()
                            code = encode(p1, avg)
                            name = make_name(eq_name, d, zp_name, cd_name, ab_name)
                            results.append((p1, code, name, n))

results.sort(key=lambda x: -x[0])
lines = ['名称\t编码']
for p1, code, name, n in results:
    lines.append(f'{name}\t{code}')
outpath = os.path.join(OUTDIR, 'vba表周策分P1.txt')
with open(outpath, 'w', encoding='gbk') as f:
    f.write('\n'.join(lines))
print(f'  共{len(results)}个组合 -> {outpath}')