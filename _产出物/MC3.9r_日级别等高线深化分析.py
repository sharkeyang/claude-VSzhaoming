#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9r_日级别等高线深化分析.py
=============================
日级别等高线深化分析（全量日CSV）。
分析维度：
1. 等高线8等基线（P1/P2/P3）
2. 等高线×波型主类 组合区分度
3. 等高线×柱排主类 组合区分度
4. 等高线×日ZA/ZC/ZE 分段
5. 等高线合并简化（等1+等2+等3+等4 vs 等5+等6+等7+等8）
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
# 16=日段, 17=日机警, 44=等高线(等1~等8)

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

def seg(w, i):
    if pd.isna(w): return ''
    parts = str(w).split('.')
    return parts[i] if len(parts) > i else ''

print('=' * 80)
print('MC3.9r 日级别等高线深化分析')
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

# 解析波型
wk['地型'] = wk['波型'].apply(lambda w: seg(w, 0))
wk['波型主'] = wk['波型'].apply(lambda w: seg(w, 1))

# 解析柱排
wk['柱排主'] = wk['柱排'].astype(str).apply(lambda w: seg(w, 0))

# 等高线
wk['等高线_s'] = wk['等高线'].astype(str)

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

def range_p3(items):
    ps = [(n, p3, n) for n, m in items for p1, p2, p3, avg, n in [stats(m)] if p3 is not None]
    if not ps: return None
    mn = min(ps, key=lambda x: x[1])
    mx = max(ps, key=lambda x: x[1])
    return mn, mx, mx[1] - mn[1]

# ============================================================
# 1. 等高线8等基线
# ============================================================
print('\n[1] 等高线8等基线')
print('=' * 60)

eq_items = []
for eq in ['等1', '等2', '等3', '等4', '等5', '等6', '等7', '等8']:
    eq_items.append((eq, wk['等高线_s'].str.contains(eq, na=False)))
out = print_table('1. 等高线8等', eq_items)
print(out); output.append(out)
r = range_p3(eq_items)
print(f'等高线8等区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n等高线8等区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# 合并简化：上侧(等1~等4) vs 下侧(等5~等8)
m_up = wk['等高线_s'].str.contains('等1|等2|等3|等4', na=False)
m_dn = wk['等高线_s'].str.contains('等5|等6|等7|等8', na=False)
items = [('上侧(等1~等4)', m_up), ('下侧(等5~等8)', m_dn)]
out = print_table('1b. 等高线合并简化', items)
print(out); output.append(out)
r = range_p3(items)
print(f'等高线合并区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n等高线合并区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 2. 等高线×波型主类
# ============================================================
print('\n[2] 等高线×波型主类')
print('=' * 60)

comb_items = []
for eq in ['等1', '等2', '等3', '等4', '等5', '等6', '等7', '等8']:
    for bx in ['Aa龙猪', 'Bb龙管杂', 'Bc龙管栅', 'Be龙管根', 'Dd头正芽', 'Df头负', 'Fa震正〇', 'Fd震正芽', 'Fe震正根', 'Ff震负']:
        m = wk['等高线_s'].str.contains(eq, na=False) & wk['波型主'].str.contains(bx, na=False)
        if m.sum() >= MIN_SAMPLE:
            comb_items.append((f'{eq}+{bx}', m))
out = print_table('2. 等高线×波型主类', comb_items)
print(out); output.append(out)
r = range_p3(comb_items)
print(f'等高线×波型主类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n等高线×波型主类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 3. 等高线×柱排主类
# ============================================================
print('\n[3] 等高线×柱排主类')
print('=' * 60)

comb2_items = []
for eq in ['等1', '等2', '等3', '等4', '等5', '等6', '等7', '等8']:
    for zp in ['升', '跌']:
        m = wk['等高线_s'].str.contains(eq, na=False) & (wk['柱排主'] == zp)
        if m.sum() >= MIN_SAMPLE:
            comb2_items.append((f'{eq}+{zp}排', m))
out = print_table('3. 等高线×柱排主类', comb2_items)
print(out); output.append(out)
r = range_p3(comb2_items)
print(f'等高线×柱排主类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n等高线×柱排主类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 4. 等高线×日ZA/ZC/ZE
# ============================================================
print('\n[4] 等高线×日ZA/ZC/ZE')
print('=' * 60)

for col_name, col in [('日ZA', '日ZA'), ('日ZC', '日ZC'), ('日ZE', '日ZE')]:
    items = [
        (f'上侧+{col_name}>0', m_up & (wk[col] > 0)),
        (f'上侧+{col_name}<=0', m_up & (wk[col] <= 0)),
        (f'下侧+{col_name}>0', m_dn & (wk[col] > 0)),
        (f'下侧+{col_name}<=0', m_dn & (wk[col] <= 0)),
    ]
    out = print_table(f'4. 等高线合并×{col_name}', items)
    print(out); output.append(out)

# ============================================================
# 5. 等高线合并简化 vs 8等完整 对比
# ============================================================
print('\n[5] 等高线合并 vs 8等 对比')
print('=' * 60)

# 上侧细分
up_items = []
for eq in ['等1', '等2', '等3', '等4']:
    up_items.append((eq, wk['等高线_s'].str.contains(eq, na=False)))
out = print_table('5a. 上侧细分', up_items)
print(out); output.append(out)
r = range_p3(up_items)
print(f'上侧细分区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n上侧细分区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

dn_items = []
for eq in ['等5', '等6', '等7', '等8']:
    dn_items.append((eq, wk['等高线_s'].str.contains(eq, na=False)))
out = print_table('5b. 下侧细分', dn_items)
print(out); output.append(out)
r = range_p3(dn_items)
print(f'下侧细分区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n下侧细分区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)

summary = []
for title, items in [
    ('等高线8等', eq_items),
    ('等高线合并(上/下)', [('上侧', m_up), ('下侧', m_dn)]),
    ('等高线×波型主类', comb_items),
    ('等高线×柱排主类', comb2_items),
]:
    r = range_p3(items)
    if r:
        summary.append((title, r[0][1], r[1][1], r[2], r[0][0], r[1][0]))

print(f'\n{"方案":<20s}  {"最低P3":>7s}  {"最高P3":>7s}  {"区分度":>6s}')
print('-' * 48)
for title, lo, hi, span, lon, hin in summary:
    print(f'{title:<20s}  {lo:>6.1f}%  {hi:>6.1f}%  {span:>5.1f}pp')
output.append('\n' + '=' * 60)
output.append('方案对比汇总')
output.append('=' * 60)
output.append(f'{"方案":<20s}  {"最低P3":>7s}  {"最高P3":>7s}  {"区分度":>6s}')
output.append('-' * 48)
for title, lo, hi, span, lon, hin in summary:
    output.append(f'{title:<20s}  {lo:>6.1f}%  {hi:>6.1f}%  {span:>5.1f}pp')

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9r_日级别等高线深化分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')