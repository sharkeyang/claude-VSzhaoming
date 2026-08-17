#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9o_地型柱排组合区分度.py
============================
对比：周地型8类 vs 周柱排 vs 周地型×周柱排 的区分度。

用全量周CSV（7460文件，425万行）验证：
1. 单独周地型8类区分度
2. 单独周柱排区分度
3. 周地型×周柱排组合区分度
4. 周地型×周柱排(主类) 组合区分度

判断：组合是否比单独地型区分度更好？
"""

import pandas as pd, os, glob, sys, warnings
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物'
MIN_SAMPLE = 500
os.makedirs(OUTDIR, exist_ok=True)

def load_all():
    wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组周_*.csv')))
    dfs = []
    for i, f in enumerate(wfiles):
        if i % 1000 == 0:
            print(f'  [加载] {i}/{len(wfiles)} 文件...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) >= 2:
                df['fid'] = i
                dfs.append(df)
        except:
            continue
    wk = pd.concat(dfs, ignore_index=True)
    wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
    wk = wk.dropna(subset=['下周HR'])
    print(f'  [加载] 完成: {len(wfiles)} 文件, {len(wk)} 行', flush=True)
    return wk

def seg(w, i):
    if pd.isna(w): return ''
    parts = str(w).split('.')
    return parts[i] if len(parts) > i else ''

print('=' * 80)
print('MC3.9o 地型×柱排组合区分度')
print('=' * 80)
print()
wk = load_all()

# 拆分波型列
wk['地型'] = wk['波型'].apply(lambda w: seg(w, 0))
wk['主类'] = wk['波型'].apply(lambda w: seg(w, 1))

# 拆分柱排列
wk['柱排'] = wk['柱排周'].astype(str)
wk['柱排主'] = wk['柱排'].apply(lambda w: seg(w, 0))   # 升/跌/人
wk['柱排形'] = wk['柱排'].apply(lambda w: seg(w, 1))   # 尾连/尾吞/连后吞...

baseline_p3 = (wk['下周HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n全样本: {total} 行, 基线下周P3 = {baseline_p3:.1f}%')
print('=' * 80)

output = []

def stats(mask):
    g = wk[mask]
    n = len(g)
    if n < MIN_SAMPLE:
        return None, None, None, n
    p1 = (g['下周HR'] >= 1).mean() * 100
    p3 = (g['下周HR'] >= 3).mean() * 100
    avg_hr = g['下周HR'].mean()
    return p1, p3, avg_hr, n

def print_table(title, items, label_width=46):
    lines = [f'\n{"=" * 80}', title, '=' * 80,
             f'{"条件":<{label_width}s}  {"样本":>9s}  {"P1%":>7s}  {"P3%":>7s}  {"期望HR":>7s}',
             '-' * (label_width + 40)]
    for name, mask in items:
        p1, p3, avg, n = stats(mask)
        if p1 is None:
            lines.append(f'{name:<{label_width}s}  {n:>9,d}  {"-":>7s}  {"-":>7s}  {"-":>7s}  (样本不足)')
        else:
            lines.append(f'{name:<{label_width}s}  {n:>9,d}  {p1:>6.1f}%  {p3:>6.1f}%  {avg:>6.2f}%')
    lines.append('')
    return '\n'.join(lines)

def range_p3(items):
    """计算一组条件的P3范围（区分度）"""
    ps = []
    for name, mask in items:
        p1, p3, avg, n = stats(mask)
        if p3 is not None:
            ps.append((name, p3, n))
    if not ps: return None
    mn = min(ps, key=lambda x: x[1])
    mx = max(ps, key=lambda x: x[1])
    return mn, mx, mx[1] - mn[1]

# ============================================================
# 分析1：单独周地型8类
# ============================================================
print('\n[1] 单独周地型8类')
print('=' * 60)
dixing_items = []
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    dixing_items.append((f'地型{d}', wk['地型'] == d))
out = print_table('1. 周地型8类', dixing_items)
print(out); output.append(out)
r = range_p3(dixing_items)
print(f'周地型8类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n周地型8类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 分析2：单独周柱排（主类：升/跌/人）
# ============================================================
print('\n[2] 单独周柱排主类（升/跌/人）')
print('=' * 60)
zhupai_main_items = []
for m in ['升', '跌', '人']:
    zhupai_main_items.append((f'柱排{m}', wk['柱排主'] == m))
out = print_table('2. 周柱排主类', zhupai_main_items)
print(out); output.append(out)
r = range_p3(zhupai_main_items)
print(f'周柱排主类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n周柱排主类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 分析3：单独周柱排（完整49类）
# ============================================================
print('\n[3] 单独周柱排（完整分类）')
print('=' * 60)
zhupai_full_items = []
for v in wk['柱排'].value_counts().index:
    if wk['柱排'].eq(v).sum() >= MIN_SAMPLE:
        zhupai_full_items.append((f'柱排{v}', wk['柱排'] == v))
out = print_table('3. 周柱排完整分类', zhupai_full_items)
print(out); output.append(out)
r = range_p3(zhupai_full_items)
print(f'周柱排完整分类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n周柱排完整分类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 分析4：周地型 × 周柱排主类（升/跌/人）
# ============================================================
print('\n[4] 周地型 × 周柱排主类')
print('=' * 60)
comb1_items = []
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    for m in ['升', '跌', '人']:
        comb1_items.append((f'{d}+{m}', (wk['地型'] == d) & (wk['柱排主'] == m)))
out = print_table('4. 地型×柱排主类', comb1_items)
print(out); output.append(out)
r = range_p3(comb1_items)
print(f'地型×柱排主类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n地型×柱排主类区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 分析5：周地型 × 周柱排完整分类
# ============================================================
print('\n[5] 周地型 × 周柱排完整分类')
print('=' * 60)
comb2_items = []
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    for v in wk['柱排'].value_counts().index:
        m = (wk['地型'] == d) & (wk['柱排'] == v)
        if m.sum() >= MIN_SAMPLE:
            comb2_items.append((f'{d}+{v}', m))
out = print_table('5. 地型×柱排完整', comb2_items)
print(out); output.append(out)
r = range_p3(comb2_items)
print(f'地型×柱排完整区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')
output.append(f'\n地型×柱排完整区分度: {r[0][1]:.1f}%({r[0][0]}) ~ {r[1][1]:.1f}%({r[1][0]}), 范围={r[2]:.1f}pp')

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)

# 汇总各方案区分度
summary = []
for title, items in [
    ('周地型8类', dixing_items),
    ('周柱排主类', zhupai_main_items),
    ('周柱排完整', zhupai_full_items),
    ('地型×柱排主类', comb1_items),
    ('地型×柱排完整', comb2_items),
]:
    r = range_p3(items)
    if r:
        summary.append((title, r[0][1], r[1][1], r[2], r[0][0], r[1][0]))

print(f'\n{"方案":<16s}  {"最低P3":>7s}  {"最高P3":>7s}  {"区分度":>6s}')
print('-' * 45)
for title, lo, hi, span, lon, hin in summary:
    print(f'{title:<16s}  {lo:>6.1f}%  {hi:>6.1f}%  {span:>5.1f}pp')
output.append('\n' + '=' * 60)
output.append('方案对比汇总')
output.append('=' * 60)
output.append(f'{"方案":<16s}  {"最低P3":>7s}  {"最高P3":>7s}  {"区分度":>6s}')
output.append('-' * 45)
for title, lo, hi, span, lon, hin in summary:
    output.append(f'{title:<16s}  {lo:>6.1f}%  {hi:>6.1f}%  {span:>5.1f}pp')

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9o_地型柱排组合区分度.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')