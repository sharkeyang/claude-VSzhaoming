#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9s_日柱排全量验证.py
=====================
6.2 日柱排 全量数据验证（高波池 Qic+Qim+Qit）。
验证 6.2 节所有可量化主张：
  6.2.1 升排(升连/升吞/跌孕) vs 单阳柱 的 P3 区分度
  6.2.2 诱多识别规则（升吞+BSHA<3%、升吞+ZC≤0、单阳柱+触顶、单阳柱+宽哼JC<5、高位升吞）
  6.2.3-6.2.6 突破回踩/启动结构/四柱栅/悬阳升连

数据源：昭明算展/谕组日/谕组日_*.csv（62列格式）
P3 = 下日高幅(下日HR) >= 3% 的概率；期望HR = 下日高幅均值。
高波池 = Qic+Qim+Qit（市板映射 MP1_花册分类映射.json）。

柱排编码（col 10）：
  升.尾连* = 升连（连续阳柱，Q2+）
  升.尾吞* = 升吞（单阳柱吞没前阴）
  升.尾反孕* = 跌孕（单阳柱/十字星止跌）
  跌.尾连* = 跌连；跌.尾吞* = 跌吞；跌.尾反孕* = 跌孕
  (升)人/(跌)人/(人)人 = 人排（无明确方向）

用法：
    python _产出物/MC3.9s_日柱排全量验证.py
"""

import pandas as pd, glob, os, sys, warnings, json
warnings.simplefilter('ignore')

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

DATADIR = r'昭明算展/谕组日'
OUTDIR = r'_产出物'
MIN_SAMPLE = 1000
os.makedirs(OUTDIR, exist_ok=True)

# 62列格式关键列索引（注意：实际数据列头有错位，以下为实际内容映射）
# 0:日期 5:涨幅(PR) 6:高幅(HR) 8:DXCD 9:DXAB
# 10:柱排 13:日ZA 14:日ZC 21:BSHA 24:宽哼JC
# 30:上符串(A/B/v/w/_) 34:并符串(Q/O/o/W/V/v) 45:顶型 46:日等型
# 注意：股票代码不在数据列中，从文件名提取（谕组日_<代码>.csv）
USECOLS = [0, 5, 6, 8, 9, 10, 13, 14, 21, 24, 30, 34, 45, 46]

def stats(mask):
    g = wk[mask]
    n = len(g)
    if n < MIN_SAMPLE: return None, None, None, None, n
    p1 = (g['下日HR'] >= 1).mean() * 100
    p2 = (g['下日HR'] >= 2).mean() * 100
    p3 = (g['下日HR'] >= 3).mean() * 100
    avg = g['下日HR'].mean()
    return p1, p2, p3, avg, n

def print_table(title, items, label_width=46):
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

print('=' * 84)
print('MC3.9s 日柱排全量验证（高波池 Qic+Qim+Qit）')
print('=' * 84)
print()

# 市板映射，筛选高波池(Qic+Qim+Qit)
print('\n[过滤] 加载市板映射，筛选高波池(Qic+Qim+Qit)...', flush=True)
with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    board_map = json.load(f)
GB = {'Qic', 'Qim', 'Qit'}

# 加载数据，股票代码从文件名提取；仅保留高波池股票以省内存
wfiles = sorted(glob.glob(os.path.join(DATADIR, '谕组日_*.csv')))
dfs = []
for i, f in enumerate(wfiles):
    if i % 1000 == 0: print(f'  [加载] {i}/{len(wfiles)}...', flush=True)
    try:
        code = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        if board_map.get(code) not in GB:
            continue  # 非高波池，跳过
        df = pd.read_csv(f, encoding='gbk', usecols=USECOLS)
        if len(df) >= 2:
            df['代码'] = code
            df['fid'] = i
            dfs.append(df)
    except Exception as e:
        continue
wk = pd.concat(dfs, ignore_index=True)
wk.columns = ['日期', 'PR', 'HR', 'DXCD', 'DXAB', '柱排',
              '日ZA', '日ZC', 'BSHA', '宽哼JC', '上符串', '并符串',
              '顶型', '日等型', '代码', 'fid']
# 丢弃分析用不到的列，省内存
wk = wk.drop(columns=['日期', 'PR', 'DXCD', '顶型'])
# 数值转换（提前转，省内存）
for col in ['日ZA', '日ZC', 'BSHA', '宽哼JC']:
    wk[col] = pd.to_numeric(wk[col], errors='coerce')
wk['HR'] = pd.to_numeric(wk['HR'], errors='coerce')
# 下日高幅 = 下一行高幅
wk['下日HR'] = wk.groupby('fid')['HR'].shift(-1)
wk = wk.dropna(subset=['下日HR'])
wk['下日HR'] = pd.to_numeric(wk['下日HR'], errors='coerce')
print(f'  高波池: {len(wk)} 行', flush=True)

baseline_p3 = (wk['下日HR'] >= 3).mean() * 100
baseline_p2 = (wk['下日HR'] >= 2).mean() * 100
baseline_p1 = (wk['下日HR'] >= 1).mean() * 100
total = len(wk)
print(f'\n高波池全样本: {total:,} 行')
print(f'基线: P1={baseline_p1:.1f}%  P2={baseline_p2:.1f}%  P3={baseline_p3:.1f}%')
print('=' * 84)

output = []

# ============================================================
# 柱排方向分类
# ============================================================
wk['柱排_s'] = wk['柱排'].astype(str)
m_up = wk['柱排_s'].str.startswith('升', na=False)          # 升排
m_dn = wk['柱排_s'].str.startswith('跌', na=False)          # 跌排
m_ren = ~(m_up | m_dn)                                      # 人排

# 尾型分类（升排内）
m_up_lian = wk['柱排_s'].str.startswith('升.尾连', na=False)   # 升连（连续阳柱）
m_up_tun = wk['柱排_s'].str.startswith('升.尾吞', na=False)    # 升吞（单阳柱吞没）
m_up_fanyun = wk['柱排_s'].str.startswith('升.尾反孕', na=False)  # 跌孕（单阳柱止跌）

# 单阳柱（并符串判定）：今升(Q/O/o) 且 昨非升
wk['并符串_s'] = wk['并符串'].astype(str)
wk['今符'] = wk['并符串_s'].str[-1]
wk['昨符'] = wk['并符串_s'].str[-2]
up_chars = ['Q', 'O', 'o']
wk['今升'] = wk['今符'].isin(up_chars)
wk['昨升'] = wk['昨符'].isin(up_chars)
m_single_up = wk['今升'] & ~wk['昨升'] & m_up   # 单阳柱 = 今升昨非升 + 升排
m_consec_up = wk['今升'] & wk['昨升'] & m_up    # 连阳柱 = 今升昨升 + 升排

# ============================================================
# 6.2.1 升排 vs 单阳柱
# ============================================================
print('\n[6.2.1] 升排 vs 单阳柱')
print('=' * 60)

items = [
    ('基线(高波池全量)', pd.Series(True, index=wk.index)),
    ('升排(全部)', m_up),
    ('  升连(升.尾连*)', m_up_lian),
    ('  升吞(升.尾吞*)', m_up_tun),
    ('  跌孕(升.尾反孕*)', m_up_fanyun),
    ('单阳柱(并符串:今升昨非升)', m_single_up),
    ('连阳柱(并符串:今升昨升)', m_consec_up),
    ('跌排(全部)', m_dn),
    ('人排(全部)', m_ren),
]
out = print_table('6.2.1 升排 vs 单阳柱', items)
print(out); output.append(out)

# ============================================================
# 6.2.2 诱多识别
# ============================================================
print('\n[6.2.2] 诱多识别')
print('=' * 60)

# 升吞 + BSHA<3% → 冲不动，假信号
m_bsha_lt3 = wk['BSHA'] < 3
m_bsha_ge3 = wk['BSHA'] >= 3
# 升吞 + ZC≤0 → 逆势反弹
m_zc_pos = wk['日ZC'] > 0
m_zc_neg = wk['日ZC'] <= 0
# 单阳柱 + 触顶（上符串末位A）
wk['上符串_s'] = wk['上符串'].astype(str)
m_touch = wk['上符串_s'].str[-1] == 'A'
# 单阳柱 + 宽哼JC<5（刚突破哼JA）
m_jc_lt5 = wk['宽哼JC'] < 5
m_jc_ge5 = wk['宽哼JC'] >= 5
# 高位（日等型>=3）
wk['日等型_n'] = pd.to_numeric(wk['日等型'], errors='coerce')
m_high = wk['日等型_n'] >= 3

items = [
    ('升吞(基线)', m_up_tun),
    ('  升吞+BSHA<3%', m_up_tun & m_bsha_lt3),
    ('  升吞+BSHA≥3%', m_up_tun & m_bsha_ge3),
    ('  升吞+ZC>0', m_up_tun & m_zc_pos),
    ('  升吞+ZC≤0', m_up_tun & m_zc_neg),
    ('单阳柱(基线)', m_single_up),
    ('  单阳柱+触顶', m_single_up & m_touch),
    ('  单阳柱+宽哼JC<5', m_single_up & m_jc_lt5),
    ('  单阳柱+宽哼JC≥5', m_single_up & m_jc_ge5),
    ('高位升吞(等型≥3)', m_up_tun & m_high),
    ('  高位升吞+BSHA<5%', m_up_tun & m_high & (wk['BSHA'] < 5)),
    ('  高位升吞+BSHA≥5%', m_up_tun & m_high & (wk['BSHA'] >= 5)),
]
out = print_table('6.2.2 诱多识别', items)
print(out); output.append(out)

# ============================================================
# 6.2.3-6.2.6 突破回踩/启动/四柱栅/悬阳升连
# ============================================================
print('\n[6.2.3-6.2.6] 突破回踩/启动/四柱栅/悬阳升连')
print('=' * 60)

# 刚突破DJA：日ZA=1（刚站上）
m_just_up = wk['日ZA'] == 1
# 连阳后跌孕：升.尾反孕（升连后跌孕）
# 启动结构：第一柱上破DJA(日ZA=1) + 跌孕 + 继鼎
# 四柱栅：DJA之上(日ZA>0) + 中阳后跌孕 + 跌孕后小阳
# 悬阳升连：DXAB正交 + 从DJA之下上破DJA + DJA之上悬空

items = [
    ('刚突破DJA(日ZA=1)', m_just_up),
    ('  刚突破+跌孕(升.尾反孕)', m_just_up & m_up_fanyun),
    ('  刚突破+升连', m_just_up & m_up_lian),
    ('  刚突破+升吞', m_just_up & m_up_tun),
    ('DJA之上(日ZA>0)', wk['日ZA'] > 0),
    ('  日ZA>0+跌孕', (wk['日ZA'] > 0) & m_up_fanyun),
    ('  日ZA>0+升连', (wk['日ZA'] > 0) & m_up_lian),
    ('  日ZA>0+升吞', (wk['日ZA'] > 0) & m_up_tun),
    ('DXAB正交+升连', (wk['DXAB'].astype(str).str.contains('正交', na=False)) & m_up_lian),
    ('DXAB正交+升吞', (wk['DXAB'].astype(str).str.contains('正交', na=False)) & m_up_tun),
]
out = print_table('6.2.3-6.2.6 突破/启动/栅/悬阳', items)
print(out); output.append(out)

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
高波池全量基线：P1={baseline_p1:.1f}%  P2={baseline_p2:.1f}%  P3={baseline_p3:.1f}%

6.2.1 升排 vs 单阳柱：
- 升排 vs 单阳柱 的 P3 差
- 升连/升吞/跌孕 各自 P3

6.2.2 诱多识别：
- 升吞+BSHA<3% vs ≥3% 的 P3 差
- 升吞+ZC≤0 vs >0 的 P3 差
- 单阳柱+触顶 是否 P3 低
- 单阳柱+宽哼JC<5 是否 P3 低
- 高位升吞+BSHA<5% 是否诱多

6.2.3-6.2.6 突破结构：
- 刚突破DJA 各形态 P3
''')

outpath = os.path.join(OUTDIR, 'MC3.9s_日柱排全量验证.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')