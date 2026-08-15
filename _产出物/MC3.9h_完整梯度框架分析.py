#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9h_完整梯度框架分析.py
=====================
完整梯度框架：WXCD + WXAB + 周等型 + 地型 + 柱排
全量7461只/425万行验证。

输出：
- 下周冲高≥1%概率
- 下周冲高≥3%概率
- 下周期望冲高幅度（均值）
- 按梯度分层汇总

用法：
    python _产出物/MC3.9h_完整梯度框架分析.py
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
    wk['下周PR'] = wk.groupby('fid')['PR'].shift(-1)
    wk = wk.dropna(subset=['下周HR'])
    print(f'  [加载] 完成: {len(wfiles)} 文件, {len(wk)} 行', flush=True)
    return wk

def stats(mask):
    """返回 (P1%, P3%, 期望HR均值, 样本数)"""
    g = wk[mask]
    n = len(g)
    if n < MIN_SAMPLE:
        return None, None, None, n
    p1 = (g['下周HR'] >= 1).mean() * 100
    p3 = (g['下周HR'] >= 3).mean() * 100
    avg_hr = g['下周HR'].mean()
    return p1, p3, avg_hr, n

print('=' * 80)
print('MC3.9h 完整梯度框架分析')
print('=' * 80)
print()
wk = load_all()

baseline_p1 = (wk['下周HR'] >= 1).mean() * 100
baseline_p3 = (wk['下周HR'] >= 3).mean() * 100
baseline_avg = wk['下周HR'].mean()
total = len(wk)
print(f'\n全样本: {total} 行')
print(f'基线: P1={baseline_p1:.1f}%  P3={baseline_p3:.1f}%  期望HR={baseline_avg:.2f}%')
print('=' * 80)

output = []

# 拆分波型
def seg(w, i):
    if pd.isna(w): return ''
    parts = str(w).split('.')
    return parts[i] if len(parts) > i else ''

wk['地型'] = wk['波型'].apply(lambda w: seg(w, 0))
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['末位'] = wk['中符串周'].astype(str).str[-1]

# 6等
m1 = wk['ZA周'] == 1
m2 = (wk['ZA周'] >= 2) & (wk['末位'].isin(['C','D','E','F']))
m3 = (wk['ZA周'] >= 2) & (wk['末位'].isin(['A','B']))
m5 = wk['ZA周'] == -1
m6 = (wk['ZA周'] <= -2) & (wk['末位'].isin(['A','B','C','D']))
m7 = (wk['ZA周'] <= -2) & (wk['末位'].isin(['E','F']))

# 柱排方向
m_up = wk['柱排周'].str.contains('升', na=False)
m_dn = wk['柱排周'].str.contains('跌', na=False)
m_ren = ~(m_up | m_dn)

# WXCD
m_gold = wk['WXCD'].str.contains('金', na=False)
m_silver = wk['WXCD'].str.contains('银', na=False)
m_xi = wk['WXCD'].str.contains('唏', na=False)
m_xu = wk['WXCD'].str.contains('嘘', na=False)
m_niao = wk['WXCD'].str.contains('尿', na=False)
m_shi = wk['WXCD'].str.contains('屎', na=False)
m_cd_good = m_gold | m_silver
m_cd_bad = ~m_cd_good

# WXAB
m_ab_a = wk['WXAB'].str.contains('甲', na=False)
m_ab_b = wk['WXAB'].str.contains('乙', na=False)
m_ab_c = wk['WXAB'].str.contains('丙', na=False)
m_ab_d = wk['WXAB'].str.contains('丁', na=False)
m_ab_e = wk['WXAB'].str.contains('戊', na=False)
m_ab_ji = wk['WXAB'].str.contains('己', na=False)
m_ab_good = m_ab_a | m_ab_b | m_ab_ji
m_ab_bad = m_ab_c | m_ab_d | m_ab_e

# ZA分段
m_za4 = wk['ZA周'] >= 4
m_za04 = (wk['ZA周'] >= 0) & (wk['ZA周'] < 4)
m_zan3 = (wk['ZA周'] >= -3) & (wk['ZA周'] < 0)
m_zal3 = wk['ZA周'] < -3

def print_table(title, items, label_width=36):
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

# ── 1. 单指标基线 ──
print('\n[1] 单指标基线')
items = [
    ('全样本', wk['下周HR'].notna()),
    ('WXCD 金升', m_gold),
    ('WXCD 银升', m_silver),
    ('WXCD 唏', m_xi),
    ('WXCD 嘘', m_xu),
    ('WXCD 尿', m_niao),
    ('WXCD 屎', m_shi),
    ('WXAB 甲', m_ab_a),
    ('WXAB 乙', m_ab_b),
    ('WXAB 丙', m_ab_c),
    ('WXAB 丁', m_ab_d),
    ('WXAB 戊', m_ab_e),
    ('WXAB 己', m_ab_ji),
    ('周等型 等3', m3),
    ('周等型 等2', m2),
    ('周等型 等1', m1),
    ('周等型 等7', m7),
    ('周等型 等6', m6),
    ('周等型 等5', m5),
    ('柱排 升排', m_up),
    ('柱排 人排', m_ren),
    ('柱排 跌排', m_dn),
]
out = print_table('1. 单指标基线', items)
print(out); output.append(out)

# ── 2. 周等型+柱排（无地型区域：ZA≥0~<4 和 ZA≥-3~<0）──
print('\n[2] 周等型+柱排（中间区域）')
items = []
# ZA≥0~<4
for eq_name, eq_mask in [('等3', m3), ('等2', m2), ('等1', m1)]:
    for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
        items.append((f'ZA≥0~<4 {eq_name}+{zp_name}', m_za04 & eq_mask & zp_mask))
# ZA≥-3~<0
for eq_name, eq_mask in [('等7', m7), ('等6', m6), ('等5', m5)]:
    for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
        items.append((f'ZA≥-3~<0 {eq_name}+{zp_name}', m_zan3 & eq_mask & zp_mask))
out = print_table('2. 周等型+柱排（中间区域）', items)
print(out); output.append(out)

# ── 3. 周等型+地型+柱排（有地型区域：ZA≥4 和 ZA<-3）──
print('\n[3] 周等型+地型+柱排（两端区域）')
items = []
# ZA≥4
for eq_name, eq_mask in [('等3', m3), ('等2', m2)]:
    for d in ['0橅', '1柜', '2栅', '3桮']:
        for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
            items.append((f'ZA≥4 {eq_name}+{d}+{zp_name}', m_za4 & eq_mask & (wk['地型'] == d) & zp_mask))
# ZA<-3
for eq_name, eq_mask in [('等7', m7), ('等6', m6)]:
    for d in ['9妩', '8姖', '7姗', '6娝']:
        for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
            items.append((f'ZA<-3 {eq_name}+{d}+{zp_name}', m_zal3 & eq_mask & (wk['地型'] == d) & zp_mask))
out = print_table('3. 周等型+地型+柱排（两端区域）', items)
print(out); output.append(out)

# ── 4. 叠加WXCD（宏观）──
print('\n[4] 叠加WXCD（宏观）')
items = []
# 最佳组合 + WXCD
best_combos = [
    ('ZA≥4 等3+0橅+升排', m_za4 & m3 & (wk['地型'] == '0橅') & m_up),
    ('ZA≥4 等2+0橅+升排', m_za4 & m2 & (wk['地型'] == '0橅') & m_up),
    ('ZA≥0~<4 等3+升排', m_za04 & m3 & m_up),
    ('ZA≥0~<4 等2+升排', m_za04 & m2 & m_up),
    ('ZA<-3 等7+7姗+升排', m_zal3 & m7 & (wk['地型'] == '7姗') & m_up),
    ('ZA<-3 等6+6娝+升排', m_zal3 & m6 & (wk['地型'] == '6娝') & m_up),
]
for name, mask in best_combos:
    for cd_name, cd_mask in [('+金升', m_gold), ('+银升', m_silver), ('+金银升', m_cd_good), ('+屎降', m_shi)]:
        items.append((name + cd_name, mask & cd_mask))
out = print_table('4. 叠加WXCD', items)
print(out); output.append(out)

# ── 5. 叠加WXAB（中观）──
print('\n[5] 叠加WXAB（中观）')
items = []
for name, mask in best_combos:
    for ab_name, ab_mask in [('+甲乙己', m_ab_good), ('+丙丁戊', m_ab_bad)]:
        items.append((name + ab_name, mask & ab_mask))
out = print_table('5. 叠加WXAB', items)
print(out); output.append(out)

# ── 6. 完整梯度：WXCD+WXAB+周等型+地型+柱排 ──
print('\n[6] 完整梯度：WXCD+WXAB+周等型+地型+柱排')
items = []
for name, mask in best_combos:
    for cd_name, cd_mask in [('+金升', m_gold), ('+银升', m_silver)]:
        for ab_name, ab_mask in [('+甲乙己', m_ab_good)]:
            items.append((name + cd_name + ab_name, mask & cd_mask & ab_mask))
out = print_table('6. 完整梯度（Top组合）', items)
print(out); output.append(out)

# ── 7. 完整梯度排序（Top 30）──
print('\n[7] 完整梯度排序（Top 30）')
all_combos = []
# 所有组合遍历
for eq_name, eq_mask in [('等3', m3), ('等2', m2), ('等1', m1), ('等7', m7), ('等6', m6), ('等5', m5)]:
    for cd_name, cd_mask in [('金升', m_gold), ('银升', m_silver), ('金银升', m_cd_good), ('唏', m_xi), ('嘘', m_xu), ('尿', m_niao), ('屎', m_shi)]:
        for ab_name, ab_mask in [('甲乙己', m_ab_good), ('丙丁戊', m_ab_bad)]:
            # ZA≥4：加地型
            for d in ['0橅', '1柜', '2栅', '3桮']:
                for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
                    all_combos.append((f'{eq_name}+{d}+{zp_name}+{cd_name}+{ab_name}', m_za4 & eq_mask & (wk['地型'] == d) & zp_mask & cd_mask & ab_mask))
            # ZA≥0~<4：无地型
            for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
                all_combos.append((f'{eq_name}+4上WJA+{zp_name}+{cd_name}+{ab_name}', m_za04 & eq_mask & zp_mask & cd_mask & ab_mask))
            # ZA≥-3~<0：无地型
            for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
                all_combos.append((f'{eq_name}+5跌破+{zp_name}+{cd_name}+{ab_name}', m_zan3 & eq_mask & zp_mask & cd_mask & ab_mask))
            # ZA<-3：加地型
            for d in ['9妩', '8姖', '7姗', '6娝']:
                for zp_name, zp_mask in [('升排', m_up), ('人排', m_ren), ('跌排', m_dn)]:
                    all_combos.append((f'{eq_name}+{d}+{zp_name}+{cd_name}+{ab_name}', m_zal3 & eq_mask & (wk['地型'] == d) & zp_mask & cd_mask & ab_mask))

results = []
for name, mask in all_combos:
    p1, p3, avg, n = stats(mask)
    if p1 is not None:
        results.append((p3, p1, avg, name, n))
results.sort(key=lambda x: -x[0])

lines = [f'\n{"=" * 80}',
         '7. 完整梯度排序（Top 30，按下周P3降序）',
         '=' * 80,
         f'{"排序":>4s}  {"组合":<44s}  {"样本":>9s}  {"P1%":>7s}  {"P3%":>7s}  {"期望HR":>7s}',
         '-' * 85]
for rank, (p3, p1, avg, name, n) in enumerate(results[:30], 1):
    lines.append(f'{rank:>4d}  {name:<44s}  {n:>9,d}  {p1:>6.1f}%  {p3:>6.1f}%  {avg:>6.2f}%')
lines.append('')
out = '\n'.join(lines)
print(out); output.append(out)

# ── 写入文件 ──
outpath = os.path.join(OUTDIR, 'MC3.9h_完整梯度框架分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
print(f'\n结果已写入: {outpath}')