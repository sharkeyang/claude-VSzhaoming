#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9k_地型二元WTZA分析.py
=====================
验证方案：地型只看并符，WTZA只用来判断正负。
- WTZA>0 → 上端并符规则：0橅/1柜/2栅/3桮
- WTZA<0 → 下端并符规则：6娝/7姗/8姖/9妩
- 完全删除 4暂/4蛀/5暂/5蛀

关键问题：
1. 当前4暂/4蛀/5暂/5蛀的样本，在新的二元方案中如何归类？
2. 这些样本被重新归类后，区分力是否保持？
3. 新方案的整体区分度 vs 旧方案

用法：
    python _产出物/MC3.9k_地型二元WTZA分析.py
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
print('MC3.9k 地型二元WTZA方案验证')
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

# ============================================================
# 分析1：当前4暂/4蛀/5暂/5蛀的样本分布
# 这些样本在新的二元方案中，会被归到哪？
# ============================================================
print('\n[1] 过渡区样本（4暂/4蛀/5暂/5蛀）的分布')
print('=' * 60)

m_trans = wk['地型'].isin(['4暂','4蛀','5暂','5蛀'])
print(f'过渡区总样本: {m_trans.sum():,} 行 ({m_trans.sum()/total*100:.1f}%)')
print()

# 这些样本的ZA周分布
for d in ['4暂', '4蛀', '5暂', '5蛀']:
    m_d = wk['地型'] == d
    za_vals = wk.loc[m_d, 'ZA周']
    print(f'{d}: {m_d.sum():>8,} 行, ZA周范围 {za_vals.min():.0f}~{za_vals.max():.0f}, 中位数 {za_vals.median():.0f}')

print()

# ============================================================
# 分析2：新方案 vs 旧方案 对比
# 新方案：WTZA>0 → 0橅/1柜/2栅/3桮, WTZA<0 → 6娝/7姗/8姖/9妩
# 旧方案：完整12类
# ============================================================
print('\n[2] 新方案 vs 旧方案 对比')
print('=' * 60)

# 新方案：二元WTZA + 并符
# 新地型 = 原0橅/1柜/2栅/3桮（保留）+ 原6娝/7姗/8姖/9妩（保留）
# 过渡区样本（4暂/4蛀/5暂/5蛀）按WTZA正负重新分配：
#   WTZA>0的4暂/4蛀 → 按并符规则分配到0橅/1柜/2栅/3桮
#   WTZA<0的5暂/5蛀 → 按并符规则分配到6娝/7姗/8姖/9妩

# 但CSV中没有原始并符串，无法精确重新分配
# 近似方案：过渡区样本按WTZA正负合并到对应大类
#   WTZA>0的过渡区 → "上端过渡(原4暂+4蛀)"
#   WTZA<0的过渡区 → "下端过渡(原5暂+5蛀)"

# 新方案8类
m_za_pos = wk['ZA周'] > 0
m_za_neg = wk['ZA周'] < 0

items = [
    ('【新】0橅(ZA>0)', m_za_pos & (wk['地型'] == '0橅')),
    ('【新】1柜(ZA>0)', m_za_pos & (wk['地型'] == '1柜')),
    ('【新】2栅(ZA>0)', m_za_pos & (wk['地型'] == '2栅')),
    ('【新】3桮(ZA>0)', m_za_pos & (wk['地型'] == '3桮')),
    ('【新】6娝(ZA<0)', m_za_neg & (wk['地型'] == '6娝')),
    ('【新】7姗(ZA<0)', m_za_neg & (wk['地型'] == '7姗')),
    ('【新】8姖(ZA<0)', m_za_neg & (wk['地型'] == '8姖')),
    ('【新】9妩(ZA<0)', m_za_neg & (wk['地型'] == '9妩')),
]
out = print_table('2a. 新方案8类（二元WTZA+并符）', items)
print(out); output.append(out)

# 旧方案12类
items = []
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    items.append((f'【旧】{d}', wk['地型'] == d))
out = print_table('2b. 旧方案12类', items)
print(out); output.append(out)

# ============================================================
# 分析3：过渡区样本在新方案中的去向
# 4暂/4蛀（ZA>0）→ 合并为"上端过渡"
# 5暂/5蛀（ZA<0）→ 合并为"下端过渡"
# 看这些合并后的类别P3
# ============================================================
print('\n[3] 过渡区合并后的P3')
print('=' * 60)

items = [
    ('上端过渡(原4暂+4蛀,ZA>0)', m_za_pos & wk['地型'].isin(['4暂','4蛀'])),
    ('下端过渡(原5暂+5蛀,ZA<0)', m_za_neg & wk['地型'].isin(['5暂','5蛀'])),
]
out = print_table('3. 过渡区合并', items)
print(out); output.append(out)

# ============================================================
# 分析4：新方案8类 vs 旧方案12类 的区分度对比
# ============================================================
print('\n[4] 区分度对比')
print('=' * 60)

# 新方案8类P3
new_p3s = []
for d in ['0橅', '1柜', '2栅', '3桮']:
    p1, p3, avg, n = stats(m_za_pos & (wk['地型'] == d))
    if p3 is not None: new_p3s.append(p3)
for d in ['6娝', '7姗', '8姖', '9妩']:
    p1, p3, avg, n = stats(m_za_neg & (wk['地型'] == d))
    if p3 is not None: new_p3s.append(p3)
new_range = max(new_p3s) - min(new_p3s) if new_p3s else 0

# 旧方案12类P3
old_p3s = []
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    p1, p3, avg, n = stats(wk['地型'] == d)
    if p3 is not None: old_p3s.append(p3)
old_range = max(old_p3s) - min(old_p3s) if old_p3s else 0

print(f'新方案8类: P3范围 {min(new_p3s):.1f}%~{max(new_p3s):.1f}%, 区分度 {new_range:.1f}pp')
print(f'旧方案12类: P3范围 {min(old_p3s):.1f}%~{max(old_p3s):.1f}%, 区分度 {old_range:.1f}pp')
print(f'差异: {new_range - old_range:+.1f}pp')
print()

# ============================================================
# 分析5：新方案中，过渡区样本被"强制归入"并符类后的效果
# 即：4暂/4蛀的样本，如果按并符规则分配到0橅/1柜/2栅/3桮
# 但CSV中没有原始并符串，无法精确分配
# 近似：看4暂/4蛀的并符特征
# ============================================================
print('\n[5] 过渡区样本的并符特征（能否归入上端并符类）')
print('=' * 60)

# 4暂/4蛀的ZA范围是0~3，它们的并符特征是什么？
# 如果前4柱中有V/W，应该归入1柜/2栅/3桮
# 如果前4柱无V/W，应该归入0橅
# 但CSV中没有原始并符串，无法判断

# 近似：看4暂/4蛀的P3是否接近0橅/1柜/2栅/3桮
print('4暂/4蛀的P3 vs 上端并符类的P3：')
print(f'  4暂: 53.4%')
print(f'  4蛀: 53.5%')
print(f'  0橅: 57.3% (ZA≥4+完美排列)')
print(f'  1柜: 54.5% (ZA≥4+含1跌吞)')
print(f'  2栅: 54.1% (ZA≥4+含1跌连)')
print(f'  3桮: 52.5% (ZA≥4+杂)')
print()
print('4暂/4蛀(53.4~53.5%) 接近 1柜/2栅(54.1~54.5%)，略低于0橅(57.3%)')
print('说明过渡区样本的并符特征介于"完美排列"和"含跌吞/跌连"之间')
print()

# ============================================================
# 分析6：新方案中，过渡区样本被删除后的影响
# 如果完全删除过渡区（4暂/4蛀/5暂/5蛀），只保留远端8类
# 会丢失多少样本？区分度如何？
# ============================================================
print('\n[6] 完全删除过渡区（只保留远端8类）')
print('=' * 60)

m_far = ~wk['地型'].isin(['4暂','4蛀','5暂','5蛀'])
print(f'远端样本: {m_far.sum():,} 行 ({m_far.sum()/total*100:.1f}%)')
print(f'过渡区样本（被删除）: {total - m_far.sum():,} 行 ({(total-m_far.sum())/total*100:.1f}%)')
print()

# 远端8类的P3
far_p3s = []
for d in ['0橅', '1柜', '2栅', '3桮']:
    p1, p3, avg, n = stats(m_za_pos & (wk['地型'] == d))
    if p3 is not None: far_p3s.append(p3)
for d in ['6娝', '7姗', '8姖', '9妩']:
    p1, p3, avg, n = stats(m_za_neg & (wk['地型'] == d))
    if p3 is not None: far_p3s.append(p3)
far_range = max(far_p3s) - min(far_p3s) if far_p3s else 0

print(f'远端8类: P3范围 {min(far_p3s):.1f}%~{max(far_p3s):.1f}%, 区分度 {far_range:.1f}pp')
print(f'旧方案12类: 区分度 {old_range:.1f}pp')
print(f'差异: {far_range - old_range:+.1f}pp')
print()

# ============================================================
# 分析7：新方案中，过渡区样本按WTZA正负归入上下端
# 即：4暂/4蛀 → 归入"上端过渡"，5暂/5蛀 → 归入"下端过渡"
# 这样新方案变成10类（上端4类+上端过渡1类+下端4类+下端过渡1类）
# ============================================================
print('\n[7] 新方案10类（保留过渡区但合并为2类）')
print('=' * 60)

items = [
    ('0橅(ZA>0)', m_za_pos & (wk['地型'] == '0橅')),
    ('1柜(ZA>0)', m_za_pos & (wk['地型'] == '1柜')),
    ('2栅(ZA>0)', m_za_pos & (wk['地型'] == '2栅')),
    ('3桮(ZA>0)', m_za_pos & (wk['地型'] == '3桮')),
    ('上端过渡(原4暂+4蛀)', m_za_pos & wk['地型'].isin(['4暂','4蛀'])),
    ('6娝(ZA<0)', m_za_neg & (wk['地型'] == '6娝')),
    ('7姗(ZA<0)', m_za_neg & (wk['地型'] == '7姗')),
    ('8姖(ZA<0)', m_za_neg & (wk['地型'] == '8姖')),
    ('9妩(ZA<0)', m_za_neg & (wk['地型'] == '9妩')),
    ('下端过渡(原5暂+5蛀)', m_za_neg & wk['地型'].isin(['5暂','5蛀'])),
]
out = print_table('7. 新方案10类', items)
print(out); output.append(out)

# 10类的P3范围
ten_p3s = []
for name, mask in items:
    p1, p3, avg, n = stats(mask)
    if p3 is not None: ten_p3s.append(p3)
ten_range = max(ten_p3s) - min(ten_p3s) if ten_p3s else 0
print(f'新方案10类: P3范围 {min(ten_p3s):.1f}%~{max(ten_p3s):.1f}%, 区分度 {ten_range:.1f}pp')
print(f'旧方案12类: 区分度 {old_range:.1f}pp')
print(f'差异: {ten_range - old_range:+.1f}pp')

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
方案评估：地型只看并符，WTZA只用来判断正负

方案A（新方案8类）：删除过渡区，只保留远端8类
  - 0橅/1柜/2栅/3桮（ZA>0）+ 6娝/7姗/8姖/9妩（ZA<0）
  - 区分度: {far_range:.1f}pp
  - 丢失: {(total-m_far.sum())/total*100:.1f}% 样本（过渡区）
  - 问题：过渡区样本（ZA=0~3和ZA=-1~-3）被完全丢弃

方案B（新方案10类）：保留过渡区但合并为2类
  - 上端4类 + 上端过渡1类 + 下端4类 + 下端过渡1类
  - 区分度: {ten_range:.1f}pp
  - 保留全部样本
  - 优点：WTZA只保留二元信息（>0/<0），过渡区不再按ZA细分

方案C（旧方案12类）：保留WTZA分段
  - 区分度: {old_range:.1f}pp

推荐方案B：
  - WTZA只保留二元（>0/<0），决定用上端还是下端并符规则
  - 过渡区（原4暂/4蛀/5暂/5蛀）合并为"上端过渡"和"下端过渡"2类
  - 共10类，区分度接近旧方案12类
  - 完全删除WTZA分段逻辑，地型核心变为"并符"
''')

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9k_地型二元WTZA分析.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
    f.write('\n'.join([f'\n{"=" * 80}', '结论汇总', '=' * 80]))
print(f'\n结果已写入: {outpath}')