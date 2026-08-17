#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9p_日级别全量基线分析_轻量版.py
=============================
日级别全量基线分析（轻量版，只加载必要列，分批处理）。
分析维度：
1. 日级别基线（P1/P2/P3）
2. 等高线6等区分度
3. 日冲策略P2分布
"""

import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组日'
OUTDIR = r'_产出物'
MIN_SAMPLE = 1000
os.makedirs(OUTDIR, exist_ok=True)

# 日CSV列：0=日期, 5=涨幅(PR), 6=高幅(HR), 7=DXEF, 8=DXCD, 9=DXAB
# 10=柱排, 11=波型, 12=盈提示, 13=日ZA, 14=日ZC, 15=日ZE
# 16=日段(持主/持被/卖浮), 17=日机警(仓位建议), 44=等高线(等1~等8)

def load_all():
    wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组日_*.csv')))
    dfs = []
    for i, f in enumerate(wfiles):
        if i % 1000 == 0: print(f'  [加载] {i}/{len(wfiles)}...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk', usecols=[0,5,6,7,8,9,10,11,12,13,14,15,16,17,44])
            if len(df) >= 2:
                df['fid'] = i
                dfs.append(df)
        except:
            continue
    wk = pd.concat(dfs, ignore_index=True)
    print(f'  [加载] 完成: {len(wfiles)} 文件, {len(wk)} 行', flush=True)
    return wk

print('=' * 80)
print('MC3.9p 日级别全量基线分析（轻量版）')
print('=' * 80)
print()
wk = load_all()

# 列重命名
wk = wk.rename(columns={
    wk.columns[0]: '日期', wk.columns[1]: 'PR', wk.columns[2]: 'HR',
    wk.columns[3]: 'DXEF', wk.columns[4]: 'DXCD', wk.columns[5]: 'DXAB',
    wk.columns[6]: '柱排', wk.columns[7]: '波型', wk.columns[8]: '盈提示',
    wk.columns[9]: '日ZA', wk.columns[10]: '日ZC', wk.columns[11]: '日ZE',
    wk.columns[12]: '日段', wk.columns[13]: '日机警',
    wk.columns[14]: '等高线',
})

# 下日HR
wk['下日HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下日HR'])

# 转换数值列
for col in ['日ZA', '日ZC', '日ZE']:
    wk[col] = pd.to_numeric(wk[col], errors='coerce')

total = len(wk)
p1 = (wk['下日HR'] >= 1).mean() * 100
p2 = (wk['下日HR'] >= 2).mean() * 100
p3 = (wk['下日HR'] >= 3).mean() * 100
avg_hr = wk['下日HR'].mean()
print(f'\n全样本: {total:,} 行')
print(f'基线: 下日P1={p1:.1f}% 下日P2={p2:.1f}% 下日P3={p3:.1f}% 期望HR={avg_hr:.2f}%')
print('=' * 80)

output = []

def stats(mask):
    g = wk[mask]; n = len(g)
    if n < MIN_SAMPLE: return None, None, None, None, n
    p1 = (g['下日HR'] >= 1).mean() * 100
    p2 = (g['下日HR'] >= 2).mean() * 100
    p3 = (g['下日HR'] >= 3).mean() * 100
    avg = g['下日HR'].mean()
    return p1, p2, p3, avg, n

def print_table(title, items, label_width=36):
    lines = [f'\n{"=" * 80}', title, '=' * 80,
             f'{"条件":<{label_width}s}  {"样本":>9s}  {"P1%":>7s}  {"P2%":>7s}  {"P3%":>7s}  {"期望HR":>7s}',
             '-' * (label_width + 44)]
    for name, mask in items:
        r = stats(mask)
        if r[0] is None:
            lines.append(f'{name:<{label_width}s}  {r[4]:>9,d}  {"-":>7s}  {"-":>7s}  {"-":>7s}  {"-":>7s}  (样本不足)')
        else:
            lines.append(f'{name:<{label_width}s}  {r[4]:>9,d}  {r[0]:>6.1f}%  {r[1]:>6.1f}%  {r[2]:>6.1f}%  {r[3]:>6.2f}%')
    lines.append('')
    return '\n'.join(lines)

# ============================================================
# 1. 日级别基线
# ============================================================
print('\n[1] 日级别基线')
print('=' * 60)

items = [
    ('日ZA>0(站上DJA)', wk['日ZA'] > 0),
    ('日ZA<=0(跌破DJA)', wk['日ZA'] <= 0),
    ('日ZA=1(刚站上)', wk['日ZA'] == 1),
    ('日ZA=2~3', (wk['日ZA'] >= 2) & (wk['日ZA'] <= 3)),
    ('日ZA>3', wk['日ZA'] > 3),
    ('日ZA=-1(刚跌破)', wk['日ZA'] == -1),
    ('日ZA=-2~-3', (wk['日ZA'] >= -3) & (wk['日ZA'] <= -2)),
    ('日ZA<-3', wk['日ZA'] < -3),
]
out = print_table('1. 日ZA分段', items)
print(out); output.append(out)

items = [
    ('日ZC>0(站上DJC)', wk['日ZC'] > 0),
    ('日ZC<=0(跌破DJC)', wk['日ZC'] <= 0),
]
out = print_table('1b. 日ZC分段', items)
print(out); output.append(out)

items = [
    ('日ZE>0(站上DJE)', wk['日ZE'] > 0),
    ('日ZE<=0(跌破DJE)', wk['日ZE'] <= 0),
]
out = print_table('1c. 日ZE分段', items)
print(out); output.append(out)

# ============================================================
# 2. 等高线6等区分度
# ============================================================
print('\n[2] 等高线6等区分度')
print('=' * 60)

wk['等高线_s'] = wk['等高线'].astype(str)
eq_items = []
for eq in ['等1', '等2', '等3', '等5', '等6', '等7']:
    eq_items.append((eq, wk['等高线_s'].str.contains(eq, na=False)))
out = print_table('2. 6等全对比', eq_items)
print(out); output.append(out)

# ============================================================
# 3. 日冲策略P2分布（日机警）
# ============================================================
print('\n[3] 日冲策略P2分布（日机警）')
print('=' * 60)

wk['日机警_s'] = wk['日机警'].astype(str)
grade_items = []
for grade in ['中性', '轻仓', '优选']:
    grade_items.append((grade, wk['日机警_s'].str.contains(grade, na=False)))
out = print_table('3. 日机警仓位建议', grade_items)
print(out); output.append(out)

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9p_日级别全量基线分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')