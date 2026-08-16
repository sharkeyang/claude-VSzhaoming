#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9o_周策分P1与最后一柱验证.py
=====================
验证：周策分P1值很低时，是否代表"周类最后一柱"。

分析思路：
1. 从CSV中提取柱排周和柱型周，定义"最后一柱"特征
2. 用现有字段（ZA周、地型、柱排、WXCD、WXAB）模拟周策分P1
3. 看条件差时，柱排是否多为跌排、柱型是否多为末端形态
4. 看"最后一柱"后下周的HR分布

用法：
    python _产出物/MC3.9o_周策分P1与最后一柱验证.py
"""

import pandas as pd, os, glob, sys, warnings
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组周'
OUTDIR = r'_产出物'
MIN_SAMPLE = 100
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

print('=' * 80)
print('MC3.9o 周策分P1与最后一柱验证')
print('=' * 80)
print()
wk = load_all()

baseline_p1 = (wk['下周HR'] >= 1).mean() * 100
baseline_p3 = (wk['下周HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n全样本: {total} 行, 基线下周P1={baseline_p1:.1f}%, P3={baseline_p3:.1f}%')
print('=' * 80)

output = []

# 拆分波型
def seg(w, i):
    if pd.isna(w): return ''
    parts = str(w).split('.')
    return parts[i] if len(parts) > i else ''

wk['地型'] = wk['波型'].apply(lambda w: seg(w, 0))
wk['主类'] = wk['波型'].apply(lambda w: seg(w, 1))
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['柱排周'] = wk['柱排周'].astype(str)
wk['柱型周'] = wk['柱型周'].astype(str)

# ============================================================
# 分析1：定义"最后一柱"特征
# 柱排=跌排 且 柱型包含"根/贯/单"等末端形态
# ============================================================
print('\n[1] 柱排方向与下周P1')
print('=' * 60)

m_up = wk['柱排周'].str.contains('升', na=False)
m_dn = wk['柱排周'].str.contains('跌', na=False)
m_ren = ~(m_up | m_dn)

items = [
    ('柱排=升排', m_up),
    ('柱排=人排', m_ren),
    ('柱排=跌排', m_dn),
]
out = print_table('1. 柱排方向', items)
print(out); output.append(out)

# ============================================================
# 分析2：柱型末端形态与下周P1
# ============================================================
print('\n[2] 柱型末端形态与下周P1')
print('=' * 60)

# 柱型中包含"根"、"贯"、"单"等末端形态
m_root = wk['柱型周'].str.contains('根', na=False)
m_guan = wk['柱型周'].str.contains('贯', na=False)
m_dan = wk['柱型周'].str.contains('单', na=False)
m_lan = wk['柱型周'].str.contains('栏', na=False)
m_zha = wk['柱型周'].str.contains('栅', na=False)
m_ti = wk['柱型周'].str.contains('梯', na=False)
m_zhi = wk['柱型周'].str.contains('枝', na=False)

items = [
    ('柱型含"根"', m_root),
    ('柱型含"贯"', m_guan),
    ('柱型含"单"', m_dan),
    ('柱型含"栏"', m_lan),
    ('柱型含"栅"', m_zha),
    ('柱型含"梯"', m_ti),
    ('柱型含"枝"', m_zhi),
]
out = print_table('2. 柱型末端形态', items)
print(out); output.append(out)

# ============================================================
# 分析3：模拟周策分P1——用条件组合近似
# 最差条件组合：ZA<0 + 地型下端 + 柱排跌 + WXCD差 + WXAB差
# ============================================================
print('\n[3] 最差条件组合（模拟低P1值）')
print('=' * 60)

m_za_neg = wk['ZA周'] < 0
m_dixing_down = wk['地型'].isin(['6娝','7姗','8姖','9妩'])
m_wxcd_bad = wk['WXCD'].str.contains('唏|嘘|尿|屎', na=False)
m_wxab_bad = wk['WXAB'].str.contains('丙|丁|戊', na=False)

# 条件叠加
items = [
    ('ZA<0', m_za_neg),
    ('ZA<0+地型下端', m_za_neg & m_dixing_down),
    ('ZA<0+地型下端+跌排', m_za_neg & m_dixing_down & m_dn),
    ('ZA<0+地型下端+跌排+WXCD差', m_za_neg & m_dixing_down & m_dn & m_wxcd_bad),
    ('ZA<0+地型下端+跌排+WXCD差+WXAB差', m_za_neg & m_dixing_down & m_dn & m_wxcd_bad & m_wxab_bad),
]
out = print_table('3. 条件叠加', items)
print(out); output.append(out)

# ============================================================
# 分析4：最差条件组合的柱型分布
# ============================================================
print('\n[4] 最差条件组合的柱型分布')
print('=' * 60)

m_worst = m_za_neg & m_dixing_down & m_dn & m_wxcd_bad & m_wxab_bad
worst_zx = wk.loc[m_worst, '柱型周'].value_counts()
print(f'最差条件组合样本数: {m_worst.sum()}')
print('柱型分布TOP10:')
for zx, cnt in worst_zx.head(10).items():
    print(f'  {zx}: {cnt} ({cnt/m_worst.sum()*100:.1f}%)')

# ============================================================
# 分析5：最差条件组合的柱排分布
# ============================================================
print('\n[5] 最差条件组合的柱排分布')
print('=' * 60)

worst_zp = wk.loc[m_worst, '柱排周'].value_counts()
print('柱排分布TOP10:')
for zp, cnt in worst_zp.head(10).items():
    print(f'  {zp}: {cnt} ({cnt/m_worst.sum()*100:.1f}%)')

# ============================================================
# 分析6：最差条件组合的"最后一柱"特征
# 看这些样本中，柱排=跌排的比例，以及柱型=末端形态的比例
# ============================================================
print('\n[6] 最差条件组合的"最后一柱"特征')
print('=' * 60)

# 定义"最后一柱"特征：柱排=跌排 且 柱型含"根/贯/单"
m_last = m_dn & (m_root | m_guan | m_dan)
print(f'全样本中"最后一柱"比例: {m_last.sum()/total*100:.1f}%')
print(f'最差条件中"最后一柱"比例: {m_last[m_worst].sum()/m_worst.sum()*100:.1f}%')
print()

# 看"最后一柱"的P1
items = [
    ('最后一柱(跌排+根/贯/单)', m_last),
    ('非最后一柱', ~m_last),
]
out = print_table('6. 最后一柱 vs 非最后一柱', items)
print(out); output.append(out)

# ============================================================
# 分析7：按条件数量分层（模拟P1梯度）
# 条件越多越差，P1应该越低
# ============================================================
print('\n[7] 条件数量分层（模拟P1梯度）')
print('=' * 60)

# 定义5个坏条件
conditions = [
    ('ZA<0', m_za_neg),
    ('地型下端', m_dixing_down),
    ('柱排跌', m_dn),
    ('WXCD差', m_wxcd_bad),
    ('WXAB差', m_wxab_bad),
]

# 按坏条件数量分层
for n_bad in range(0, 6):
    mask = None
    for cond_name, cond_mask in conditions:
        if mask is None:
            mask = cond_mask if n_bad > 0 else ~cond_mask
        else:
            if n_bad > 0:
                # 至少n_bad个坏条件
                pass
    # 精确计数坏条件数量
    bad_count = sum(cond_mask.astype(int) for _, cond_mask in conditions)
    items = [(f'坏条件数={n_bad}', bad_count == n_bad)]
    out = print_table(f'7. 坏条件数={n_bad}', items)
    print(out); output.append(out)

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
验证：周策分P1值很低时，是否代表"周类最后一柱"？

分析结果：
1. 柱排方向区分度：升排 vs 跌排 的P1差
2. 柱型末端形态区分度：根/贯/单 vs 其他
3. 最差条件组合的柱型/柱排分布
4. "最后一柱"的P1 vs 非最后一柱

如果最差条件组合中，柱排=跌排比例显著高于全样本，
且柱型=根/贯/单比例显著高于全样本，
则说明"低P1值=最后一柱"的假设成立。
''')

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9o_周策分P1与最后一柱验证.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
    f.write('\n'.join([f'\n{"=" * 80}', '结论汇总', '=' * 80]))
print(f'\n结果已写入: {outpath}')