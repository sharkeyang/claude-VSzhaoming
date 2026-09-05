#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9t_等高线内部稳定性验证.py
============================
验证"等高线各等类内部稳定性"——即同一等类（等1~等7）内的样本性质是否同质。
这是"底座标准"第3条（同类别稳定）的量化验证。

度量维度：
1. 各等类的下日冲高≥3%（P3）基线
2. 各等类内，再按 BSHA 分段，看 P3 是否大幅波动（波动大=不稳定）
3. 各等类内，再按 柱排方向（升/人/跌），看 P3 是否大幅波动
4. 各等类内，再按 日ZC 方向，看 P3 是否大幅波动
5. 各等类内下柱>0 占比（方向稳定性）

数据源：昭明算展/谕组日/谕组日_*.csv（62列格式）
高波池 = Qic+Qim+Qit（市板映射 MP1_花册分类映射.json）

用法：
    python _产出物/MC3.9t_等高线内部稳定性验证.py
"""

import pandas as pd, glob, os, sys, warnings, json
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组日'
OUTDIR = r'_产出物'
MIN_SAMPLE = 1000
os.makedirs(OUTDIR, exist_ok=True)

# 62列格式关键列索引
# 0:日期 5:涨幅(PR) 6:高幅(HR) 10:柱排 13:日ZA 14:日ZC
# 21:BSHA 24:宽哼JC 44:等高线(等1~等7) 45:顶型
USECOLS = [0, 5, 6, 10, 13, 14, 21, 24, 44, 45]

# 市板映射
with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    board_map = json.load(f)
GB = {'Qic', 'Qim', 'Qit'}

print('=' * 84)
print('MC3.9t 等高线内部稳定性验证（高波池 Qic+Qim+Qit）')
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
wk.columns = ['日期', 'PR', 'HR', '柱排', '日ZA', '日ZC',
              'BSHA', '宽哼JC', '等高线', '顶型', 'fid']
# 数值转换
for col in ['日ZA', '日ZC', 'BSHA', '宽哼JC']:
    wk[col] = pd.to_numeric(wk[col], errors='coerce')
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
# 下日高幅
wk['下日HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下日HR'])
wk['下日HR'] = pd.to_numeric(wk['下日HR'], errors='coerce')
# 等高线分类
wk['等高线_s'] = wk['等高线'].astype(str)
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
# 1. 各等类 P3 基线
# ============================================================
print('\n[1] 各等类 P3 基线')
print('=' * 60)

eq_items = []
for eq in ['等1', '等2', '等3', '等5', '等6', '等7']:
    eq_items.append((eq, wk['等高线_s'] == eq))
out = print_table('1. 各等类 P3 基线', eq_items)
print(out); output.append(out)

# ============================================================
# 2. 各等类内 × BSHA 分段（内部稳定性）
# ============================================================
print('\n[2] 各等类内 × BSHA 分段')
print('=' * 60)

m_bsha_lt3 = wk['BSHA'] < 3
m_bsha_ge3 = wk['BSHA'] >= 3
m_bsha_ge5 = wk['BSHA'] >= 5

items = []
for eq in ['等1', '等2', '等3', '等5', '等6', '等7']:
    m_eq = wk['等高线_s'] == eq
    items.append((f'{eq} 基线', m_eq))
    items.append((f'  {eq}+BSHA<3', m_eq & m_bsha_lt3))
    items.append((f'  {eq}+BSHA≥3', m_eq & m_bsha_ge3))
    items.append((f'  {eq}+BSHA≥5', m_eq & m_bsha_ge5))
out = print_table('2. 各等类内 × BSHA 分段', items)
print(out); output.append(out)

# ============================================================
# 3. 各等类内 × 柱排方向（内部稳定性）
# ============================================================
print('\n[3] 各等类内 × 柱排方向')
print('=' * 60)

wk['柱排_s'] = wk['柱排'].astype(str)
m_up = wk['柱排_s'].str.startswith('升', na=False)
m_dn = wk['柱排_s'].str.startswith('跌', na=False)
m_ren = ~(m_up | m_dn)

items = []
for eq in ['等1', '等2', '等3', '等5', '等6', '等7']:
    m_eq = wk['等高线_s'] == eq
    items.append((f'{eq} 基线', m_eq))
    items.append((f'  {eq}+升排', m_eq & m_up))
    items.append((f'  {eq}+人排', m_eq & m_ren))
    items.append((f'  {eq}+跌排', m_eq & m_dn))
out = print_table('3. 各等类内 × 柱排方向', items)
print(out); output.append(out)

# ============================================================
# 4. 各等类内 × 日ZC方向（内部稳定性）
# ============================================================
print('\n[4] 各等类内 × 日ZC方向')
print('=' * 60)

m_zc_pos = wk['日ZC'] > 0
m_zc_neg = wk['日ZC'] <= 0

items = []
for eq in ['等1', '等2', '等3', '等5', '等6', '等7']:
    m_eq = wk['等高线_s'] == eq
    items.append((f'{eq} 基线', m_eq))
    items.append((f'  {eq}+ZC>0', m_eq & m_zc_pos))
    items.append((f'  {eq}+ZC≤0', m_eq & m_zc_neg))
out = print_table('4. 各等类内 × 日ZC方向', items)
print(out); output.append(out)

# ============================================================
# 5. 各等类内下柱>0 占比（方向稳定性）
# ============================================================
print('\n[5] 各等类内下柱>0 占比')
print('=' * 60)

lines = [f'\n{"=" * 84}', '5. 各等类内下柱>0 占比（方向稳定性）', '=' * 84,
         f'{"条件":<20s}  {"样本":>9s}  {"下柱>0%":>9s}  {"下柱>0且≥3%":>12s}',
         '-' * 60]
for eq in ['等1', '等2', '等3', '等5', '等6', '等7']:
    m_eq = wk['等高线_s'] == eq
    g = wk[m_eq]
    n = len(g)
    if n < MIN_SAMPLE: continue
    p_pos = (g['下日HR'] > 0).mean() * 100
    p_pos3 = ((g['下日HR'] > 0) & (g['下日HR'] >= 3)).mean() * 100
    lines.append(f'{eq:<20s}  {n:>9,d}  {p_pos:>8.1f}%  {p_pos3:>11.1f}%')
lines.append('')
out = '\n'.join(lines)
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

等高线各等类内部稳定性：
- 各等类 P3 基线（等1~等7）
- 各等类内 × BSHA 分段：P3 波动幅度（波动大=不稳定）
- 各等类内 × 柱排方向：P3 波动幅度
- 各等类内 × 日ZC方向：P3 波动幅度
- 各等类内下柱>0 占比（方向稳定性）
''')

outpath = os.path.join(OUTDIR, 'MC3.9t_等高线内部稳定性验证.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')