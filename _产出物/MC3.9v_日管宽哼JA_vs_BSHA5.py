#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9v_日管宽哼JA vs BSHA5 有效性对比.py
============================
对比 日管宽哼JA>5 与 BSHA5 的预测力（P3 = 下日冲高≥3%）。
日管宽哼JA = (龟结哼 / 日类JA - 1) * 100，龟结哼 = 最近5根最高价最大值，日类JA = EMA5。

数据源：昭明算展/谕组日/谕组日_*.csv（62列格式）
高波池 = Qic+Qim+Qit

用法：
    python _产出物/MC3.9v_日管宽哼JA vs BSHA5 有效性对比.py
"""

import pandas as pd, glob, os, sys, warnings, json
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组日'
OUTDIR = r'_产出物'
MIN_SAMPLE = 1000
os.makedirs(OUTDIR, exist_ok=True)

# 62列格式关键列索引
# 0:日期 1:收 3:高 6:高幅(HR) 21:BSHA 24:宽哼JC
USECOLS = [0, 1, 3, 6, 21, 24]

# 市板映射
with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    board_map = json.load(f)
GB = {'Qic', 'Qim', 'Qit'}

print('=' * 84)
print('MC3.9v 日管宽哼JA vs BSHA5 有效性对比（高波池 Qic+Qim+Qit）')
print('=' * 84)
print()

# 加载数据，仅保留高波池
wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组日_*.csv')))
dfs = []
for i, f in enumerate(wfiles):
    if i % 1000 == 0: print(f'  [加载] {i}/{len(wfiles)}...', flush=True)
    try:
        code = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        if board_map.get(code) not in GB:
            continue
        df = pd.read_csv(f, encoding='gbk', usecols=USECOLS)
        if len(df) >= 2:
            df['fid'] = i
            dfs.append(df)
    except Exception as e:
        continue
wk = pd.concat(dfs, ignore_index=True)
wk.columns = ['日期', '收', '高', 'HR', 'BSHA', '宽哼JC', 'fid']

# 数值转换
for col in ['收', '高', 'HR', 'BSHA', '宽哼JC']:
    wk[col] = pd.to_numeric(wk[col], errors='coerce')

# 计算 日类JA = EMA5（按股票分组）
def ema(series, span):
    return series.ewm(span=span, adjust=False).mean()

wk['日类JA'] = wk.groupby('fid')['收'].transform(lambda s: ema(s, 5))

# 计算 龟结哼 = 最近5根最高价最大值（含今日，H0-H4）
wk['龟结哼'] = wk.groupby('fid')['高'].transform(lambda s: s.rolling(5, min_periods=1).max())

# 计算 日管宽哼JA
wk['日管宽哼JA'] = (wk['龟结哼'] / wk['日类JA'] - 1) * 100

# 下日高幅
wk['下日HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下日HR'])
wk['下日HR'] = pd.to_numeric(wk['下日HR'], errors='coerce')
print(f'  高波池: {len(wk)} 行', flush=True)

baseline_p3 = (wk['下日HR'] >= 3).mean() * 100
print(f'\n高波池全样本基线: P3={baseline_p3:.1f}%')
print('=' * 84)

output = []

def stats(mask):
    g = wk[mask]
    n = len(g)
    if n < MIN_SAMPLE: return None, None, None, None, n
    p1 = (g['下日HR'] >= 1).mean() * 100
    p2 = (g['下日HR'] >= 2).mean() * 100
    p3 = (g['下日HR'] >= 3).mean() * 100
    avg = g['下日HR'].mean()
    return p1, p2, p3, avg, n

def print_table(title, items, label_width=40):
    lines = [f'\n{"=" * 84}', title, '=' * 84,
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
# 1. 日管宽哼JA vs BSHA5 单独对比
# ============================================================
print('\n[1] 日管宽哼JA vs BSHA5 单独对比')
print('=' * 60)

m_bsha5 = wk['BSHA'] >= 5
m_gkja5 = wk['日管宽哼JA'] >= 5

items = [
    ('基线(高波池全量)', pd.Series(True, index=wk.index)),
    ('BSHA≥5', m_bsha5),
    ('日管宽哼JA≥5', m_gkja5),
    ('BSHA≥5 且 日管宽哼JA≥5', m_bsha5 & m_gkja5),
    ('BSHA≥5 但 日管宽哼JA<5', m_bsha5 & ~m_gkja5),
    ('日管宽哼JA≥5 但 BSHA<5', m_gkja5 & ~m_bsha5),
    ('BSHA<5 且 日管宽哼JA<5', ~m_bsha5 & ~m_gkja5),
]
out = print_table('1. 日管宽哼JA vs BSHA5 单独对比', items)
print(out); output.append(out)

# ============================================================
# 2. 日管宽哼JA 分段（P3 单调性）
# ============================================================
print('\n[2] 日管宽哼JA 分段')
print('=' * 60)

items = []
for lo, hi in [(0, 3), (3, 5), (5, 8), (8, 10), (10, 15), (15, 20), (20, 30), (30, 999)]:
    if hi == 999:
        items.append((f'日管宽哼JA≥{lo}', wk['日管宽哼JA'] >= lo))
    else:
        items.append((f'日管宽哼JA {lo}~{hi}', (wk['日管宽哼JA'] >= lo) & (wk['日管宽哼JA'] < hi)))
out = print_table('2. 日管宽哼JA 分段', items)
print(out); output.append(out)

# ============================================================
# 3. BSHA 分段（P3 单调性）
# ============================================================
print('\n[3] BSHA 分段')
print('=' * 60)

items = []
for lo, hi in [(0, 3), (3, 5), (5, 8), (8, 10), (10, 15), (15, 20), (20, 30), (30, 999)]:
    if hi == 999:
        items.append((f'BSHA≥{lo}', wk['BSHA'] >= lo))
    else:
        items.append((f'BSHA {lo}~{hi}', (wk['BSHA'] >= lo) & (wk['BSHA'] < hi)))
out = print_table('3. BSHA 分段', items)
print(out); output.append(out)

# ============================================================
# 4. 日管宽哼JA vs BSHA 交叉（同阈值对比）
# ============================================================
print('\n[4] 日管宽哼JA vs BSHA 交叉（同阈值）')
print('=' * 60)

items = [
    ('基线', pd.Series(True, index=wk.index)),
    ('日管宽哼JA≥5', m_gkja5),
    ('BSHA≥5', m_bsha5),
    ('日管宽哼JA≥8', wk['日管宽哼JA'] >= 8),
    ('BSHA≥8', wk['BSHA'] >= 8),
    ('日管宽哼JA≥10', wk['日管宽哼JA'] >= 10),
    ('BSHA≥10', wk['BSHA'] >= 10),
]
out = print_table('4. 日管宽哼JA vs BSHA 交叉', items)
print(out); output.append(out)

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
高波池全量基线：P3={baseline_p3:.1f}%

日管宽哼JA vs BSHA5 有效性对比：
- 单独 P3（BSHA≥5 vs 日管宽哼JA≥5）
- 分段单调性（日管宽哼JA 分段 vs BSHA 分段）
- 同阈值交叉（≥5/≥8/≥10）
''')

outpath = os.path.join(OUTDIR, 'MC3.9v_日管宽哼JA_vs_BSHA5.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')