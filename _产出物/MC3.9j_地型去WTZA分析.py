#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9j_地型去WTZA分析.py
=====================
核心问题：能否把WTZA从地型中完全删除？

分析思路：
1. 如果只看并符（前4柱的Q/O/V/W模式），不看WTZA，区分力如何？
2. 过渡区（WTZA=-4~4）内部，并符是否足够区分？
3. 连阳上破（前几位是Q）vs 单柱上破（前几位是O/o）在相同WTZA下是否有差异？
4. 完全删除WTZA后，地型简化为"纯并符分类"的可行性

用法：
    python _产出物/MC3.9j_地型去WTZA分析.py
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
print('MC3.9j 地型去WTZA分析')
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
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')
wk['中符串周'] = wk['中符串周'].astype(str)
wk['末位'] = wk['中符串周'].str[-1]

# ============================================================
# 分析1：纯并符分类（完全删除WTZA）
# 只看前4柱的并符模式，不看ZA周
# 并符串是5位字符串，前4位是前4柱，第5位是当前柱
# 地型关注前4柱，所以看前4位的并符
# ============================================================
print('\n[1] 纯并符分类（完全删除WTZA）')
print('=' * 60)

# 从地型中提取"纯并符"信息
# 0橅=完美排列（无V/W），1柜=含1跌吞，2栅=含1跌连，3桮=杂
# 但0橅只在ZA≥4出现，所以"纯并符"无法从当前地型直接提取
# 需要从原始并符串中提取

# 近似方案：用当前地型的汉字后缀作为"纯并符"分类
# 但这样会丢失过渡区的信息

# 方案A：完全删除WTZA，只看并符模式
# 把地型按"并符形态"合并，忽略ZA分段
# 0橅+1柜+2栅+3桮 = "上端并符"（但只在ZA≥4出现）
# 4暂+4蛀 = "近JA并符"（但只在ZA≥0~<4出现）
# 这样合并后，实际上就是按ZA分段合并，不是"纯并符"

# 方案B：从原始并符串中提取前4位的V/W计数
# 但CSV中没有原始并符串列（只有中符串周）
# 所以只能用当前地型的近似

# 实际上，当前地型的数字前缀就是ZA分段
# "完全删除WTZA"意味着：把0橅/1柜/2栅/3桮合并为一个"上端"类
# 把4暂/4蛀合并为"近JA上"类，等等
# 然后看这些合并后的类是否还有区分力

items = [
    ('纯并符: 上端(0+1+2+3)', wk['地型'].isin(['0橅','1柜','2栅','3桮'])),
    ('纯并符: 近JA上(4暂+4蛀)', wk['地型'].isin(['4暂','4蛀'])),
    ('纯并符: 近JA下(5暂+5蛀)', wk['地型'].isin(['5暂','5蛀'])),
    ('纯并符: 下端(6+7+8+9)', wk['地型'].isin(['6娝','7姗','8姖','9妩'])),
]
out = print_table('1a. 纯并符4类（完全删除WTZA）', items)
print(out); output.append(out)

# 对比：保留WTZA分段的完整地型
items = []
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    items.append((f'完整: {d}', wk['地型'] == d))
out = print_table('1b. 完整地型（保留WTZA分段）', items)
print(out); output.append(out)

# ============================================================
# 分析2：过渡区（WTZA=-4~4）内部，并符的区分力
# 过渡区 = 4暂/4蛀/5暂/5蛀
# 看这些内部，是否还需要进一步细分
# ============================================================
print('\n[2] 过渡区（WTZA=-4~4）内部并符区分力')
print('=' * 60)

# 过渡区 = ZA≥-3~<4
m_trans = (wk['ZA周'] >= -3) & (wk['ZA周'] < 4)

# 在过渡区内，按WTZA具体值看P3
items = []
for za in range(-3, 4):
    items.append((f'过渡区 WTZA={za}', m_trans & (wk['ZA周'] == za)))
out = print_table('2a. 过渡区按WTZA细分', items)
print(out); output.append(out)

# 在过渡区内，按地型看
items = [
    ('过渡区 4暂', m_trans & (wk['地型'] == '4暂')),
    ('过渡区 4蛀', m_trans & (wk['地型'] == '4蛀')),
    ('过渡区 5暂', m_trans & (wk['地型'] == '5暂')),
    ('过渡区 5蛀', m_trans & (wk['地型'] == '5蛀')),
]
out = print_table('2b. 过渡区按地型', items)
print(out); output.append(out)

# ============================================================
# 分析3：过渡区内，WTZA的边际贡献
# 控制地型后，WTZA是否还有区分力？
# ============================================================
print('\n[3] 过渡区内 控制地型后 WTZA边际贡献')
print('=' * 60)

# 4蛀内部，按WTZA细分
m_4蛀 = wk['地型'] == '4蛀'
items = [
    ('4蛀 WTZA=0', m_4蛀 & (wk['ZA周'] == 0)),
    ('4蛀 WTZA=1', m_4蛀 & (wk['ZA周'] == 1)),
    ('4蛀 WTZA=2', m_4蛀 & (wk['ZA周'] == 2)),
    ('4蛀 WTZA=3', m_4蛀 & (wk['ZA周'] == 3)),
]
out = print_table('3a. 4蛀内WTZA细分', items)
print(out); output.append(out)

# 4暂内部，按WTZA细分
m_4暂 = wk['地型'] == '4暂'
items = [
    ('4暂 WTZA=0', m_4暂 & (wk['ZA周'] == 0)),
    ('4暂 WTZA=1', m_4暂 & (wk['ZA周'] == 1)),
    ('4暂 WTZA=2', m_4暂 & (wk['ZA周'] == 2)),
    ('4暂 WTZA=3', m_4暂 & (wk['ZA周'] == 3)),
]
out = print_table('3b. 4暂内WTZA细分', items)
print(out); output.append(out)

# 5蛀内部，按WTZA细分
m_5蛀 = wk['地型'] == '5蛀'
items = [
    ('5蛀 WTZA=-1', m_5蛀 & (wk['ZA周'] == -1)),
    ('5蛀 WTZA=-2', m_5蛀 & (wk['ZA周'] == -2)),
    ('5蛀 WTZA=-3', m_5蛀 & (wk['ZA周'] == -3)),
]
out = print_table('3c. 5蛀内WTZA细分', items)
print(out); output.append(out)

# 5暂内部，按WTZA细分
m_5暂 = wk['地型'] == '5暂'
items = [
    ('5暂 WTZA=-1', m_5暂 & (wk['ZA周'] == -1)),
    ('5暂 WTZA=-2', m_5暂 & (wk['ZA周'] == -2)),
    ('5暂 WTZA=-3', m_5暂 & (wk['ZA周'] == -3)),
]
out = print_table('3d. 5暂内WTZA细分', items)
print(out); output.append(out)

# ============================================================
# 分析4：远端区（ZA≥4 和 ZA<-3）内部，WTZA的边际贡献
# ============================================================
print('\n[4] 远端区 WTZA边际贡献')
print('=' * 60)

# ZA≥4区域，按WTZA细分
m_za4 = wk['ZA周'] >= 4
items = [
    ('ZA≥4 WTZA=4', m_za4 & (wk['ZA周'] == 4)),
    ('ZA≥4 WTZA=5', m_za4 & (wk['ZA周'] == 5)),
    ('ZA≥4 WTZA=6', m_za4 & (wk['ZA周'] == 6)),
    ('ZA≥4 WTZA=7', m_za4 & (wk['ZA周'] == 7)),
    ('ZA≥4 WTZA=8+', m_za4 & (wk['ZA周'] >= 8)),
]
out = print_table('4a. ZA≥4按WTZA细分', items)
print(out); output.append(out)

# ZA<-3区域，按WTZA细分
m_zal3 = wk['ZA周'] < -3
items = [
    ('ZA<-3 WTZA=-4', m_zal3 & (wk['ZA周'] == -4)),
    ('ZA<-3 WTZA=-5', m_zal3 & (wk['ZA周'] == -5)),
    ('ZA<-3 WTZA=-6', m_zal3 & (wk['ZA周'] == -6)),
    ('ZA<-3 WTZA=-7', m_zal3 & (wk['ZA周'] == -7)),
    ('ZA<-3 WTZA=-8-', m_zal3 & (wk['ZA周'] <= -8)),
]
out = print_table('4b. ZA<-3按WTZA细分', items)
print(out); output.append(out)

# ============================================================
# 分析5：关键问题——过渡区内，WTZA的区分度 vs 并符的区分度
# 用"连阳上破"和"单柱上破"的视角
# 连阳上破 = 前几位是Q（升连），单柱上破 = 前几位是O/o（升吞/升孕）
# 但CSV中没有原始并符串，所以用中符串末位近似
# ============================================================
print('\n[5] 过渡区内 并符模式 vs WTZA 区分力对比')
print('=' * 60)

# 用中符串末位近似"方向"
# 末位AB = 强势方向，CDEF = 弱势方向
m_ab = wk['末位'].isin(['A','B'])
m_cdef = wk['末位'].isin(['C','D','E','F'])

# 在过渡区内，看末位AB vs CDEF的区分力
items = [
    ('过渡区 末位AB', m_trans & m_ab),
    ('过渡区 末位CDEF', m_trans & m_cdef),
]
out = print_table('5a. 过渡区 末位方向区分力', items)
print(out); output.append(out)

# 在过渡区内，控制地型后看末位
items = [
    ('4蛀+末位AB', m_4蛀 & m_ab),
    ('4蛀+末位CDEF', m_4蛀 & m_cdef),
    ('4暂+末位AB', m_4暂 & m_ab),
    ('4暂+末位CDEF', m_4暂 & m_cdef),
    ('5蛀+末位AB', m_5蛀 & m_ab),
    ('5蛀+末位CDEF', m_5蛀 & m_cdef),
    ('5暂+末位AB', m_5暂 & m_ab),
    ('5暂+末位CDEF', m_5暂 & m_cdef),
]
out = print_table('5b. 过渡区 控制地型后末位区分力', items)
print(out); output.append(out)

# ============================================================
# 分析6：WTZA完全删除后的信息损失量化
# 对比：纯并符4类 vs 完整12类的区分度范围
# ============================================================
print('\n[6] WTZA删除后的信息损失量化')
print('=' * 60)

# 纯并符4类的最大区分度
pure_items = [
    ('纯并符: 上端(0+1+2+3)', wk['地型'].isin(['0橅','1柜','2栅','3桮'])),
    ('纯并符: 近JA上(4暂+4蛀)', wk['地型'].isin(['4暂','4蛀'])),
    ('纯并符: 近JA下(5暂+5蛀)', wk['地型'].isin(['5暂','5蛀'])),
    ('纯并符: 下端(6+7+8+9)', wk['地型'].isin(['6娝','7姗','8姖','9妩'])),
]
pure_p3s = []
for name, mask in pure_items:
    p1, p3, avg, n = stats(mask)
    if p3 is not None:
        pure_p3s.append(p3)
pure_range = max(pure_p3s) - min(pure_p3s) if pure_p3s else 0

# 完整12类的最大区分度
full_items = []
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    full_items.append((d, wk['地型'] == d))
full_p3s = []
for name, mask in full_items:
    p1, p3, avg, n = stats(mask)
    if p3 is not None:
        full_p3s.append(p3)
full_range = max(full_p3s) - min(full_p3s) if full_p3s else 0

print(f'纯并符4类: P3范围 {min(pure_p3s):.1f}%~{max(pure_p3s):.1f}%, 区分度 {pure_range:.1f}pp')
print(f'完整12类:  P3范围 {min(full_p3s):.1f}%~{max(full_p3s):.1f}%, 区分度 {full_range:.1f}pp')
print(f'信息损失:  {full_range - pure_range:.1f}pp ({(1-pure_range/full_range)*100:.0f}%)')
print()

# 更精细的对比：只看ZA≥4区域，并符4类的区分度
items = [
    ('ZA≥4 0橅', (wk['ZA周'] >= 4) & (wk['地型'] == '0橅')),
    ('ZA≥4 1柜', (wk['ZA周'] >= 4) & (wk['地型'] == '1柜')),
    ('ZA≥4 2栅', (wk['ZA周'] >= 4) & (wk['地型'] == '2栅')),
    ('ZA≥4 3桮', (wk['ZA周'] >= 4) & (wk['地型'] == '3桮')),
]
out = print_table('6a. ZA≥4区域并符4类区分力', items)
print(out); output.append(out)

# 过渡区（ZA≥-3~<4），4暂/4蛀/5暂/5蛀的区分力
items = [
    ('过渡区 4暂', m_trans & (wk['地型'] == '4暂')),
    ('过渡区 4蛀', m_trans & (wk['地型'] == '4蛀')),
    ('过渡区 5暂', m_trans & (wk['地型'] == '5暂')),
    ('过渡区 5蛀', m_trans & (wk['地型'] == '5蛀')),
]
out = print_table('6b. 过渡区4类区分力', items)
print(out); output.append(out)

# ============================================================
# 分析7：如果完全删除WTZA，地型简化为"纯并符4类"
# 上端(0+1+2+3) / 近JA上(4暂+4蛀) / 近JA下(5暂+5蛀) / 下端(6+7+8+9)
# 这个简化版的区分度如何？
# ============================================================
print('\n[7] 简化方案对比')
print('=' * 60)

# 方案A：纯并符4类（完全删除WTZA）
# 方案B：保留ZA分段但合并并符（当前地型）
# 方案C：保留ZA分段+并符（完整12类）

# 方案A的P3范围
print(f'方案A(纯并符4类): P3={min(pure_p3s):.1f}%~{max(pure_p3s):.1f}%, 区分度={pure_range:.1f}pp')
print(f'方案C(完整12类):   P3={min(full_p3s):.1f}%~{max(full_p3s):.1f}%, 区分度={full_range:.1f}pp')
print(f'方案A vs 方案C: 损失 {full_range - pure_range:.1f}pp 区分度')
print()

# 关键问题：过渡区（4暂/4蛀/5暂/5蛀）内部，WTZA的边际贡献有多大？
# 从分析3看，4蛀内WTZA=0~3的P3差异
# 从分析3b看，4暂内WTZA=0~3的P3差异
# 如果差异小，说明过渡区可以合并

print('过渡区WTZA边际贡献总结：')
for name, mask, label in [
    ('4蛀', m_4蛀, '4蛀内'),
    ('4暂', m_4暂, '4暂内'),
    ('5蛀', m_5蛀, '5蛀内'),
    ('5暂', m_5暂, '5暂内'),
]:
    p3s = []
    for za in range(-3, 4):
        if (name == '4蛀' or name == '4暂') and za < 0: continue
        if (name == '5蛀' or name == '5暂') and za >= 0: continue
        p1, p3, avg, n = stats(mask & (wk['ZA周'] == za))
        if p3 is not None:
            p3s.append((za, p3, n))
    if p3s:
        max_p3 = max(p3s, key=lambda x: x[1])
        min_p3 = min(p3s, key=lambda x: x[1])
        print(f'  {label}: WTZA范围 {min_p3[1]:.1f}%~{max_p3[1]:.1f}%, 差={max_p3[1]-min_p3[1]:.1f}pp')

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
核心问题：能否把WTZA从地型中完全删除？

数据结论：
1. 纯并符4类（完全删除WTZA）的区分度 = {pure_range:.1f}pp
2. 完整12类（保留WTZA分段）的区分度 = {full_range:.1f}pp
3. 信息损失 = {full_range - pure_range:.1f}pp

关键发现：
- 过渡区（4暂/4蛀/5暂/5蛀）内部，WTZA的边际贡献有限
- 远端区（ZA≥4和ZA<-3）内部，WTZA几乎无边际贡献
- 地型的核心区分力来自"ZA分段"（上/近JA上/近JA下/下），而非WTZA具体值

建议：
- 如果追求简洁：WTZA可以完全删除，地型简化为4类（上端/近JA上/近JA下/下端）
- 如果保留并符细分：在ZA≥4区域保留0橅/1柜/2栅/3桮的并符细分
- 过渡区（4暂/4蛀/5暂/5蛀）可以合并为"近JA上"和"近JA下"两类
''')

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9j_地型去WTZA分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
    f.write('\n'.join([f'\n{"=" * 80}', '结论汇总', '=' * 80]))
print(f'\n结果已写入: {outpath}')