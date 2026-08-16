#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9p_日级别全量基线分析.py
=====================
日级别全量基线分析（剔除Qst后）。
分析维度：
1. 日级别基线（P1/P2/P3）
2. 等高线6等区分度
3. 日冲策略P2分布

用法：
    python _产出物/MC3.9p_日级别全量基线分析.py
"""

import pandas as pd, glob, os, sys, warnings
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组日'
OUTDIR = r'_产出物'
MIN_SAMPLE = 1000
os.makedirs(OUTDIR, exist_ok=True)

# 日CSV列名（与周CSV不同）
# 0:日期 1:周 2:月 3:年 4:代码 5:涨幅(PR) 6:高幅(HR) 7:DXEF 8:DXCD 9:DXAB
# 10:柱排 11:柱型 12:盈提示 13:日ZA 14:日ZC 15:日ZE
# 16:等型 17:日等级 18:波型 19:BSHA 20:BSAC
# 21:距JA 22:距JC 23:偏离JC 24:顶型 25:顶触
# 26:昨高幅 27:中符 28:并符 29:上符范 30:上符串
# 31:中符串 32:中符范 33:下符串 34:下符范 35:层类
# 36:距JC 37:BS 38:BSLA 39:距JC 40:BT类 41:BTZA 42:BT鼎 43:顶型

def load_all():
    wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组日_*.csv')))
    dfs = []
    for i, f in enumerate(wfiles):
        if i % 1000 == 0: print(f'  [加载] {i}/{len(wfiles)}...', flush=True)
        try:
            df = pd.read_csv(f, encoding='gbk')
            if len(df) >= 2:
                df['fid'] = i
                dfs.append(df)
        except Exception as e:
            continue
    wk = pd.concat(dfs, ignore_index=True)
    # 日CSV列：5=涨幅(PR), 6=高幅(HR), 13=日ZA, 14=日ZC, 15=日ZE
    # 10=柱排, 11=柱型, 12=盈提示, 18=波型, 19=BSHA
    # 31=中符串, 32=中符范
    wk.columns = ['日期','周','月','年','代码','PR','HR','DXEF','DXCD','DXAB',
                  '柱排','柱型','盈提示','日ZA','日ZC','日ZE',
                  '等型','日等级','波型','BSHA','BSAC',
                  '距JA','距JC','偏离JC','顶型','顶触',
                  '昨高幅','中符','并符','上符范','上符串',
                  '中符串','中符范','下符串','下符范','层类',
                  '距JC2','BS','BSLA','距JC3','BT类','BTZA','BT鼎','顶型2','fid']
    wk['下日HR'] = wk.groupby('fid')['HR'].shift(-1)
    wk = wk.dropna(subset=['下日HR'])
    print(f'  完成: {len(wk)} 行', flush=True)
    return wk

def stats(mask):
    g = wk[mask]
    n = len(g)
    if n < MIN_SAMPLE: return None, None, None, None, n
    p1 = (g['下日HR'] >= 1).mean() * 100
    p2 = (g['下日HR'] >= 2).mean() * 100
    p3 = (g['下日HR'] >= 3).mean() * 100
    avg = g['下日HR'].mean()
    return p1, p2, p3, avg, n

def print_table(title, items, label_width=42):
    lines = [f'\n{"=" * 80}', title, '=' * 80,
             f'{"条件":<{label_width}s}  {"样本":>9s}  {"P1%":>7s}  {"P2%":>7s}  {"P3%":>7s}  {"期望HR":>7s}',
             '-' * (label_width + 44)]
    for name, mask in items:
        p1, p2, p3, avg, n = stats(mask)
        if p1 is None:
            lines.append(f'{name:<{label_width}s}  {n:>9,d}  {"-":>7s}  {"-":>7s}  {"-":>7s}  {"-":>7s}  (样本不足)')
        else:
            lines.append(f'{name:<{label_width}s}  {n:>9,d}  {p1:>6.1f}%  {p2:>6.1f}%  {p3:>6.1f}%  {avg:>6.2f}%')
    lines.append('')
    return '\n'.join(lines)

print('=' * 80)
print('MC3.9p 日级别全量基线分析')
print('=' * 80)
print()
wk = load_all()

baseline_p1 = (wk['下日HR'] >= 1).mean() * 100
baseline_p2 = (wk['下日HR'] >= 2).mean() * 100
baseline_p3 = (wk['下日HR'] >= 3).mean() * 100
total = len(wk)
print(f'\n全样本: {total} 行')
print(f'基线: P1={baseline_p1:.1f}%  P2={baseline_p2:.1f}%  P3={baseline_p3:.1f}%')
print('=' * 80)

output = []

# 拆分波型
def seg(w, i):
    if pd.isna(w): return ''
    parts = str(w).split('.')
    return parts[i] if len(parts) > i else ''

wk['地型'] = wk['波型'].apply(lambda w: seg(w, 0))
wk['日ZA'] = pd.to_numeric(wk['日ZA'], errors='coerce')
wk['中符串'] = wk['中符串'].astype(str)
wk['末位'] = wk['中符串'].str[-1]

# ============================================================
# 分析1：等高线6等区分度
# ============================================================
print('\n[1] 等高线6等区分度')
print('=' * 60)

m1 = wk['日ZA'] == 1
m2 = (wk['日ZA'] >= 2) & (wk['末位'].isin(['C','D','E','F']))
m3 = (wk['日ZA'] >= 2) & (wk['末位'].isin(['A','B']))
m5 = wk['日ZA'] == -1
m6 = (wk['日ZA'] <= -2) & (wk['末位'].isin(['A','B','C','D']))
m7 = (wk['日ZA'] <= -2) & (wk['末位'].isin(['E','F']))

items = [
    ('等3(ZA≥2+AB)', m3),
    ('等2(ZA≥2+CDEF)', m2),
    ('等1(ZA=1)', m1),
    ('等7(ZA≤-2+EF)', m7),
    ('等6(ZA≤-2+ABCD)', m6),
    ('等5(ZA=-1)', m5),
]
out = print_table('1. 等高线6等', items)
print(out); output.append(out)

# ============================================================
# 分析2：等高线 × BSHA 组合
# ============================================================
print('\n[2] 等高线 × BSHA 组合')
print('=' * 60)

# 日CSV中没有BSHA列，用柱排近似
m_up = wk['柱排'].str.contains('升', na=False)
m_dn = wk['柱排'].str.contains('跌', na=False)
m_ren = ~(m_up | m_dn)

items = []
for eq_name, eq_mask in [('等3', m3), ('等2', m2), ('等1', m1), ('等7', m7), ('等6', m6), ('等5', m5)]:
    for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
        items.append((f'{eq_name}+{zp_name}', eq_mask & zp_mask))
out = print_table('2. 等高线×柱排', items)
print(out); output.append(out)

# ============================================================
# 分析3：日冲策略P2分布
# ============================================================
print('\n[3] 日冲策略P2分布（等高线+条件评分）')
print('=' * 60)

# 模拟日冲策略：等高线+BSHA+连阳+层主
# 用柱排和日ZA近似
# 等3+升排 = 最强
# 等5+跌排 = 最弱
items = [
    ('等3+升排(最强)', m3 & m_up),
    ('等3+人排', m3 & m_ren),
    ('等3+跌排', m3 & m_dn),
    ('等2+升排', m2 & m_up),
    ('等2+人排', m2 & m_ren),
    ('等2+跌排', m2 & m_dn),
    ('等1+升排', m1 & m_up),
    ('等1+人排', m1 & m_ren),
    ('等1+跌排', m1 & m_dn),
    ('等7+升排', m7 & m_up),
    ('等7+人排', m7 & m_ren),
    ('等7+跌排', m7 & m_dn),
    ('等6+升排', m6 & m_up),
    ('等6+人排', m6 & m_ren),
    ('等6+跌排', m6 & m_dn),
    ('等5+升排', m5 & m_up),
    ('等5+人排', m5 & m_ren),
    ('等5+跌排(最弱)', m5 & m_dn),
]
out = print_table('3. 日冲策略P2', items)
print(out); output.append(out)

# ============================================================
# 分析4：等高线 × ZE（月门）交叉
# ============================================================
print('\n[4] 等高线 × ZE（月门）交叉')
print('=' * 60)

m_ze_pos = wk['日ZE'] > 0
m_ze_neg = wk['日ZE'] <= 0

items = []
for eq_name, eq_mask in [('等3', m3), ('等2', m2), ('等1', m1), ('等7', m7), ('等6', m6), ('等5', m5)]:
    items.append((f'{eq_name}+ZE>0', eq_mask & m_ze_pos))
    items.append((f'{eq_name}+ZE≤0', eq_mask & m_ze_neg))
out = print_table('4. 等高线×ZE', items)
print(out); output.append(out)

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
日级别全量基线（剔除Qst后）：
P1={baseline_p1:.1f}%  P2={baseline_p2:.1f}%  P3={baseline_p3:.1f}%

等高线6等区分度（P3）：
等3 vs 等5 的P3差

日冲策略P2区分度：
等3+升排 vs 等5+跌排 的P3差

等高线 × ZE交叉：
ZE>0时等高线区分度是否翻倍
''')

outpath = os.path.join(OUTDIR, 'MC3.9p_日级别全量基线分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')