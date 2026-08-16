#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9n_新地型全量验证.py
=====================
验证新导出的周CSV中，新地型8类（二元WTZA+纯并符）的区分度。

对比：
- 新方案8类：0橅/1柜/2栅/3桮/6娝/7姗/8姖/9妩
- 旧方案12类：含4暂/4蛀/5暂/5蛀

用法：
    python _产出物/MC3.9n_新地型全量验证.py
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
print('MC3.9n 新地型全量验证')
print('=' * 80)
print()
wk = load_all()

baseline_p3 = (wk['下周HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n全样本: {total} 行, 基线下周P3 = {baseline_p3:.1f}%')
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

# ============================================================
# 分析1：新地型8类分布 + P3
# ============================================================
print('\n[1] 新地型8类分布 + P3')
print('=' * 60)

# 检查是否有旧地型残留
old_dixing = wk['地型'].isin(['4暂','4蛀','5暂','5蛀'])
print(f'旧地型残留(4暂/4蛀/5暂/5蛀): {old_dixing.sum()} 行 ({old_dixing.sum()/total*100:.2f}%)')
print()

items = []
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    items.append((f'【新】{d}', wk['地型'] == d))
out = print_table('1. 新地型8类', items)
print(out); output.append(out)

# ============================================================
# 分析2：新地型8类 vs 旧方案12类 区分度对比
# ============================================================
print('\n[2] 区分度对比')
print('=' * 60)

new_p3s = []
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    p1, p3, avg, n = stats(wk['地型'] == d)
    if p3 is not None: new_p3s.append((d, p3, n))

new_min = min(new_p3s, key=lambda x: x[1])
new_max = max(new_p3s, key=lambda x: x[1])
print(f'新方案8类: P3={new_min[1]:.1f}%({new_min[0]})~{new_max[1]:.1f}%({new_max[0]}), 区分度={new_max[1]-new_min[1]:.1f}pp')

# 旧方案12类（用历史数据，从MC3.9k结果）
print(f'旧方案12类: 区分度=13.9pp (历史数据)')
print(f'差异: {new_max[1]-new_min[1] - 13.9:+.1f}pp')

# ============================================================
# 分析3：新地型 × WXZC（升势/跌势）
# ============================================================
print('\n[3] 新地型 × WXZC（升势/跌势）')
print('=' * 60)

wk['升势'] = ~wk['主类'].str.startswith('__', na=False)
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    m = wk['地型'] == d
    items = [
        (f'{d}+升势', m & wk['升势']),
        (f'{d}+跌势', m & ~wk['升势']),
    ]
    out = print_table(f'3. {d} × WXZC', items)
    print(out); output.append(out)

# ============================================================
# 分析4：新地型 × WXAB
# ============================================================
print('\n[4] 新地型 × WXAB')
print('=' * 60)

m_ab_good = wk['WXAB'].str.contains('甲|乙|己', na=False)
m_ab_bad = wk['WXAB'].str.contains('丙|丁|戊', na=False)
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    m = wk['地型'] == d
    items = [
        (f'{d}+甲乙己', m & m_ab_good),
        (f'{d}+丙丁戊', m & m_ab_bad),
    ]
    out = print_table(f'4. {d} × WXAB', items)
    print(out); output.append(out)

# ============================================================
# 分析5：新地型 × 柱排
# ============================================================
print('\n[5] 新地型 × 柱排')
print('=' * 60)

wk['柱排周'] = wk['柱排周'].astype(str)
m_up = wk['柱排周'].str.contains('升', na=False)
m_dn = wk['柱排周'].str.contains('跌', na=False)
m_ren = ~(m_up | m_dn)
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    m = wk['地型'] == d
    items = [
        (f'{d}+升排', m & m_up),
        (f'{d}+人排', m & m_ren),
        (f'{d}+跌排', m & m_dn),
    ]
    out = print_table(f'5. {d} × 柱排', items)
    print(out); output.append(out)

# ============================================================
# 分析6：新地型 × 周等型
# ============================================================
print('\n[6] 新地型 × 周等型')
print('=' * 60)

wk['末位'] = wk['中符串周'].astype(str).str[-1]
m1 = wk['ZA周'] == 1
m2 = (wk['ZA周'] >= 2) & (wk['末位'].isin(['C','D','E','F']))
m3 = (wk['ZA周'] >= 2) & (wk['末位'].isin(['A','B']))
m5 = wk['ZA周'] == -1
m6 = (wk['ZA周'] <= -2) & (wk['末位'].isin(['A','B','C','D']))
m7 = (wk['ZA周'] <= -2) & (wk['末位'].isin(['E','F']))

items = [
    ('等3+0橅', m3 & (wk['地型'] == '0橅')),
    ('等3+1柜', m3 & (wk['地型'] == '1柜')),
    ('等3+2栅', m3 & (wk['地型'] == '2栅')),
    ('等2+0橅', m2 & (wk['地型'] == '0橅')),
    ('等2+1柜', m2 & (wk['地型'] == '1柜')),
    ('等2+2栅', m2 & (wk['地型'] == '2栅')),
    ('等7+7姗', m7 & (wk['地型'] == '7姗')),
    ('等7+8姖', m7 & (wk['地型'] == '8姖')),
    ('等7+9妩', m7 & (wk['地型'] == '9妩')),
]
out = print_table('6. 新地型×周等型', items)
print(out); output.append(out)

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
新地型8类（二元WTZA+纯并符）全量验证：

区分度: {new_max[1]-new_min[1]:.1f}pp (旧方案13.9pp)
差异: {new_max[1]-new_min[1] - 13.9:+.1f}pp

新地型8类定义：
  WTZA>0 → 0橅/1柜/2栅/3桮（按前4柱V/W计数）
  WTZA<0 → 6娝/7姗/8姖/9妩（按前4柱O/Q计数）
  已删除4暂/4蛀/5暂/5蛀
''')

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9n_新地型全量验证.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
    f.write('\n'.join([f'\n{"=" * 80}', '结论汇总', '=' * 80]))
print(f'\n结果已写入: {outpath}')