#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9u_候选底座P3与DXAB交叉验证.py
============================
补跑 日柱排/日顶型/管中形态 的 P3 + DXAB 交叉，解决 5.2.5 未决问题 1/2/3。
统一口径：P3 = 下日高幅 >= 3% 的概率（与等高线验证一致）。

候选底座：
1. 日柱排（升/人/跌）—— col 10 柱排
2. 日顶型（触顶/合顶）—— col 30 上符串末位A（触顶）
3. 管中形态（管宽分段）—— col 24 宽哼JC

每个候选计算：
- P3 基线
- P3 × DXAB（甲乙己 vs 非甲乙己，及按护型细分）

数据源：昭明算展/谕组日/谕组日_*.csv（62列格式）
高波池 = Qic+Qim+Qit

用法：
    python _产出物/MC3.9u_候选底座P3与DXAB交叉验证.py
"""

import pandas as pd, glob, os, sys, warnings, json
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组日'
OUTDIR = r'_产出物'
MIN_SAMPLE = 1000
os.makedirs(OUTDIR, exist_ok=True)

# 62列格式关键列索引
# 0:日期 5:涨幅(PR) 6:高幅(HR) 9:DXAB 10:柱排 13:日ZA 14:日ZC
# 21:BSHA 24:宽哼JC(管宽) 30:上符串(触顶) 44:等高线 45:顶型
USECOLS = [0, 5, 6, 9, 10, 13, 14, 21, 24, 30, 44, 45]

# 市板映射
with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    board_map = json.load(f)
GB = {'Qic', 'Qim', 'Qit'}

print('=' * 84)
print('MC3.9u 候选底座 P3 + DXAB 交叉验证（高波池 Qic+Qim+Qit）')
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
wk.columns = ['日期', 'PR', 'HR', 'DXAB', '柱排', '日ZA', '日ZC',
              'BSHA', '宽哼JC', '上符串', '等高线', '顶型', 'fid']
# 数值转换
for col in ['日ZA', '日ZC', 'BSHA', '宽哼JC']:
    wk[col] = pd.to_numeric(wk[col], errors='coerce')
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
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

def print_table(title, items, label_width=42):
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
# DXAB 护型分类
# ============================================================
# DXAB 格式：a甲↗上2.A4 / z乙↘下-1.Z-4 —— 第2字符 = 护型（甲乙丙丁戊己）
wk['DXAB_s'] = wk['DXAB'].astype(str)
wk['护型'] = wk['DXAB_s'].str[1]  # 第2字符 = 护型
# 甲乙己 vs 非甲乙己
m_jyj = wk['护型'].isin(['甲', '乙', '己'])
m_nonjyj = ~m_jyj

# ============================================================
# 1. 日柱排（升/人/跌）P3 + DXAB 交叉
# ============================================================
print('\n[1] 日柱排（升/人/跌）P3 + DXAB 交叉')
print('=' * 60)

wk['柱排_s'] = wk['柱排'].astype(str)
m_up = wk['柱排_s'].str.startswith('升', na=False)
m_dn = wk['柱排_s'].str.startswith('跌', na=False)
m_ren = ~(m_up | m_dn)

items = [
    ('基线(高波池全量)', pd.Series(True, index=wk.index)),
    ('升排', m_up),
    ('  升排+甲乙己', m_up & m_jyj),
    ('  升排+非甲乙己', m_up & m_nonjyj),
    ('人排', m_ren),
    ('  人排+甲乙己', m_ren & m_jyj),
    ('  人排+非甲乙己', m_ren & m_nonjyj),
    ('跌排', m_dn),
    ('  跌排+甲乙己', m_dn & m_jyj),
    ('  跌排+非甲乙己', m_dn & m_nonjyj),
]
out = print_table('1. 日柱排 P3 + DXAB 交叉', items)
print(out); output.append(out)

# ============================================================
# 2. 日顶型（触顶/合顶）P3 + DXAB 交叉
# ============================================================
print('\n[2] 日顶型（触顶/合顶）P3 + DXAB 交叉')
print('=' * 60)

wk['上符串_s'] = wk['上符串'].astype(str)
m_touch = wk['上符串_s'].str[-1] == 'A'  # 触顶
m_notouch = ~m_touch

items = [
    ('基线(高波池全量)', pd.Series(True, index=wk.index)),
    ('触顶', m_touch),
    ('  触顶+甲乙己', m_touch & m_jyj),
    ('  触顶+非甲乙己', m_touch & m_nonjyj),
    ('非触顶', m_notouch),
    ('  非触顶+甲乙己', m_notouch & m_jyj),
    ('  非触顶+非甲乙己', m_notouch & m_nonjyj),
]
out = print_table('2. 日顶型(触顶) P3 + DXAB 交叉', items)
print(out); output.append(out)

# ============================================================
# 3. 管中形态（管宽分段）P3 + DXAB 交叉
# ============================================================
print('\n[3] 管中形态（管宽分段）P3 + DXAB 交叉')
print('=' * 60)

# 管宽 = 宽哼JC
m_gk_lt5 = wk['宽哼JC'] < 5
m_gk_5_10 = (wk['宽哼JC'] >= 5) & (wk['宽哼JC'] < 10)
m_gk_10_20 = (wk['宽哼JC'] >= 10) & (wk['宽哼JC'] < 20)
m_gk_20_40 = (wk['宽哼JC'] >= 20) & (wk['宽哼JC'] < 40)
m_gk_ge40 = wk['宽哼JC'] >= 40

items = [
    ('基线(高波池全量)', pd.Series(True, index=wk.index)),
    ('管宽<5(窄管)', m_gk_lt5),
    ('  窄管+甲乙己', m_gk_lt5 & m_jyj),
    ('  窄管+非甲乙己', m_gk_lt5 & m_nonjyj),
    ('管宽5~10', m_gk_5_10),
    ('  管宽5~10+甲乙己', m_gk_5_10 & m_jyj),
    ('  管宽5~10+非甲乙己', m_gk_5_10 & m_nonjyj),
    ('管宽10~20', m_gk_10_20),
    ('  管宽10~20+甲乙己', m_gk_10_20 & m_jyj),
    ('  管宽10~20+非甲乙己', m_gk_10_20 & m_nonjyj),
    ('管宽20~40', m_gk_20_40),
    ('  管宽20~40+甲乙己', m_gk_20_40 & m_jyj),
    ('  管宽20~40+非甲乙己', m_gk_20_40 & m_nonjyj),
    ('管宽≥40', m_gk_ge40),
    ('  管宽≥40+甲乙己', m_gk_ge40 & m_jyj),
    ('  管宽≥40+非甲乙己', m_gk_ge40 & m_nonjyj),
]
out = print_table('3. 管中形态(管宽) P3 + DXAB 交叉', items)
print(out); output.append(out)

# ============================================================
# 4. 三候选 × 等高线 对比（统一口径 P3）
# ============================================================
print('\n[4] 三候选 × 等高线 对比（统一口径 P3）')
print('=' * 60)

wk['等高线_s'] = wk['等高线'].astype(str)
m_eq2 = wk['等高线_s'] == '等2'
m_eq3 = wk['等高线_s'] == '等3'

items = [
    ('基线(高波池全量)', pd.Series(True, index=wk.index)),
    ('等高线等2', m_eq2),
    ('等高线等3', m_eq3),
    ('日柱排升排', m_up),
    ('日顶型触顶', m_touch),
    ('管宽≥10', m_gk_10_20 | m_gk_20_40 | m_gk_ge40),
    ('管宽≥20', m_gk_20_40 | m_gk_ge40),
]
out = print_table('4. 三候选 × 等高线 对比', items)
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

候选底座 P3 + DXAB 交叉：
- 日柱排（升/人/跌）：P3 基线 + ×DXAB
- 日顶型（触顶/合顶）：P3 基线 + ×DXAB
- 管中形态（管宽分段）：P3 基线 + ×DXAB
- 三候选 × 等高线 对比（统一口径 P3）
''')

outpath = os.path.join(OUTDIR, 'MC3.9u_候选底座P3与DXAB交叉验证.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')