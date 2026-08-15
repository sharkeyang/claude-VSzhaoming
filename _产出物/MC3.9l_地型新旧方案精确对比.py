#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9l_地型新旧方案精确对比.py
=====================
精确对比：新方案8类（过渡区样本按并符归入远端类）vs 旧方案12类

由于CSV中没有原始并符串，无法精确分配过渡区样本。
但可以用近似方法：
1. 假设过渡区样本的并符分布与远端区相同
2. 按比例分配过渡区样本到各并符类
3. 计算加权P3

同时，用波型主类信息做辅助验证。

用法：
    python _产出物/MC3.9l_地型新旧方案精确对比.py
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
print('MC3.9l 地型新旧方案精确对比')
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
wk['层界'] = wk['波型'].apply(lambda w: seg(w, 2))
wk['ZA周'] = pd.to_numeric(wk['ZA周'], errors='coerce')

m_za_pos = wk['ZA周'] > 0
m_za_neg = wk['ZA周'] < 0

# ============================================================
# 分析1：远端区各并符类的并符特征分布
# 用波型主类作为并符特征的近似
# ============================================================
print('\n[1] 远端区各并符类的波型主类分布')
print('=' * 60)

for d in ['0橅', '1柜', '2栅', '3桮']:
    m_d = m_za_pos & (wk['地型'] == d)
    total_d = m_d.sum()
    main_classes = wk.loc[m_d, '主类'].value_counts()
    print(f'\n{d} (n={total_d:,}):')
    for cls, cnt in main_classes.head(5).items():
        print(f'  {cls}: {cnt} ({cnt/total_d*100:.1f}%)')

print('\n--- 下端 ---')
for d in ['6娝', '7姗', '8姖', '9妩']:
    m_d = m_za_neg & (wk['地型'] == d)
    total_d = m_d.sum()
    main_classes = wk.loc[m_d, '主类'].value_counts()
    print(f'\n{d} (n={total_d:,}):')
    for cls, cnt in main_classes.head(5).items():
        print(f'  {cls}: {cnt} ({cnt/total_d*100:.1f}%)')

# ============================================================
# 分析2：过渡区样本的波型主类分布
# ============================================================
print('\n\n[2] 过渡区样本的波型主类分布')
print('=' * 60)

for d in ['4暂', '4蛀', '5暂', '5蛀']:
    m_d = wk['地型'] == d
    total_d = m_d.sum()
    main_classes = wk.loc[m_d, '主类'].value_counts()
    print(f'\n{d} (n={total_d:,}):')
    for cls, cnt in main_classes.head(5).items():
        print(f'  {cls}: {cnt} ({cnt/total_d*100:.1f}%)')

# ============================================================
# 分析3：按波型主类近似分配过渡区样本
# 假设：过渡区样本中，主类分布接近的并符类就是它应归入的类
# 例如：4暂中"龙猪"占比高 → 应归入0橅（龙猪占比也高）
# ============================================================
print('\n\n[3] 过渡区样本按主类相似度分配')
print('=' * 60)

# 计算远端各并符类的主类分布向量
def get_main_dist(mask):
    dist = wk.loc[mask, '主类'].value_counts(normalize=True)
    return dist.to_dict()

远端分布 = {}
for d in ['0橅', '1柜', '2栅', '3桮']:
    远端分布[d] = get_main_dist(m_za_pos & (wk['地型'] == d))
for d in ['6娝', '7姗', '8姖', '9妩']:
    远端分布[d] = get_main_dist(m_za_neg & (wk['地型'] == d))

# 计算过渡区样本的主类分布
过渡分布 = {}
for d in ['4暂', '4蛀', '5暂', '5蛀']:
    过渡分布[d] = get_main_dist(wk['地型'] == d)

# 找最相似的并符类
def cosine_sim(d1, d2):
    all_keys = set(d1.keys()) | set(d2.keys())
    dot = sum(d1.get(k,0) * d2.get(k,0) for k in all_keys)
    n1 = sum(v*v for v in d1.values()) ** 0.5
    n2 = sum(v*v for v in d2.values()) ** 0.5
    return dot / (n1 * n2) if n1 * n2 > 0 else 0

print('过渡区 → 最相似远端并符类：')
for d_trans in ['4暂', '4蛀', '5暂', '5蛀']:
    best_sim = -1
    best_class = ''
    for d_far, dist_far in 远端分布.items():
        sim = cosine_sim(过渡分布[d_trans], dist_far)
        if sim > best_sim:
            best_sim = sim
            best_class = d_far
    print(f'  {d_trans} → {best_class} (相似度={best_sim:.3f})')

# ============================================================
# 分析4：新方案8类的P3（过渡区按主类相似度归入）
# ============================================================
print('\n\n[4] 新方案8类P3（过渡区归入后）')
print('=' * 60)

# 根据相似度分配：
# 4暂 → ？ 4蛀 → ？ 5暂 → ？ 5蛀 → ？
# 先看相似度结果再决定

# 实际上，更精确的方法：看过渡区样本的P3与哪个远端类最接近
print('过渡区P3 vs 远端类P3：')
trans_p3 = {}
for d in ['4暂', '4蛀', '5暂', '5蛀']:
    p1, p3, avg, n = stats(wk['地型'] == d)
    trans_p3[d] = p3
    print(f'  {d}: P3={p3:.1f}% (n={n:,})')

far_p3 = {}
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    if d in ['0橅','1柜','2栅','3桮']:
        p1, p3, avg, n = stats(m_za_pos & (wk['地型'] == d))
    else:
        p1, p3, avg, n = stats(m_za_neg & (wk['地型'] == d))
    far_p3[d] = p3
    print(f'  {d}: P3={p3:.1f}%')

print('\n按P3接近度分配：')
for d_trans in ['4暂', '4蛀', '5暂', '5蛀']:
    best_dist = 999
    best_class = ''
    for d_far, p3_far in far_p3.items():
        dist = abs(trans_p3[d_trans] - p3_far)
        if dist < best_dist:
            best_dist = dist
            best_class = d_far
    print(f'  {d_trans}(P3={trans_p3[d_trans]:.1f}%) → {best_class}(P3={far_p3[best_class]:.1f}%), 差={best_dist:.1f}pp')

# ============================================================
# 分析5：新方案8类（过渡区按P3接近度归入）vs 旧方案12类
# ============================================================
print('\n\n[5] 新旧方案P3对比')
print('=' * 60)

# 根据P3接近度：
# 4暂(53.4%) → 最接近 1柜(54.5%) 差1.1pp 或 2栅(54.1%) 差0.7pp
# 4蛀(53.5%) → 最接近 2栅(54.1%) 差0.6pp 或 1柜(54.5%) 差1.0pp
# 5暂(43.4%) → 最接近 8姖(46.6%) 差3.2pp
# 5蛀(47.4%) → 最接近 9妩(47.4%) 差0.0pp 或 7姗(48.8%) 差1.4pp

# 方案A：4暂→2栅, 4蛀→2栅, 5暂→8姖, 5蛀→9妩
m_new_0橅 = m_za_pos & (wk['地型'] == '0橅')
m_new_1柜 = m_za_pos & (wk['地型'] == '1柜')
m_new_2栅 = m_za_pos & ((wk['地型'] == '2栅') | (wk['地型'] == '4暂') | (wk['地型'] == '4蛀'))
m_new_3桮 = m_za_pos & (wk['地型'] == '3桮')
m_new_6娝 = m_za_neg & (wk['地型'] == '6娝')
m_new_7姗 = m_za_neg & (wk['地型'] == '7姗')
m_new_8姖 = m_za_neg & ((wk['地型'] == '8姖') | (wk['地型'] == '5暂'))
m_new_9妩 = m_za_neg & ((wk['地型'] == '9妩') | (wk['地型'] == '5蛀'))

items = [
    ('【新】0橅', m_new_0橅),
    ('【新】1柜', m_new_1柜),
    ('【新】2栅(含4暂+4蛀)', m_new_2栅),
    ('【新】3桮', m_new_3桮),
    ('【新】6娝', m_new_6娝),
    ('【新】7姗', m_new_7姗),
    ('【新】8姖(含5暂)', m_new_8姖),
    ('【新】9妩(含5蛀)', m_new_9妩),
]
out = print_table('5a. 新方案8类（过渡区归入后）', items)
print(out); output.append(out)

# 旧方案12类
items = []
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    items.append((f'【旧】{d}', wk['地型'] == d))
out = print_table('5b. 旧方案12类', items)
print(out); output.append(out)

# 计算新方案8类的P3范围
new_p3s = []
for name, mask in [
    ('0橅', m_new_0橅), ('1柜', m_new_1柜), ('2栅', m_new_2栅), ('3桮', m_new_3桮),
    ('6娝', m_new_6娝), ('7姗', m_new_7姗), ('8姖', m_new_8姖), ('9妩', m_new_9妩)
]:
    p1, p3, avg, n = stats(mask)
    if p3 is not None: new_p3s.append((name, p3, n))

# 旧方案12类的P3范围
old_p3s = []
for d in ['0橅', '1柜', '2栅', '3桮', '4暂', '4蛀', '5暂', '5蛀', '6娝', '7姗', '8姖', '9妩']:
    p1, p3, avg, n = stats(wk['地型'] == d)
    if p3 is not None: old_p3s.append((d, p3, n))

new_min = min(new_p3s, key=lambda x: x[1])
new_max = max(new_p3s, key=lambda x: x[1])
old_min = min(old_p3s, key=lambda x: x[1])
old_max = max(old_p3s, key=lambda x: x[1])

print(f'\n新方案8类: P3={new_min[1]:.1f}%({new_min[0]})~{new_max[1]:.1f}%({new_max[0]}), 区分度={new_max[1]-new_min[1]:.1f}pp')
print(f'旧方案12类: P3={old_min[1]:.1f}%({old_min[0]})~{old_max[1]:.1f}%({old_max[0]}), 区分度={old_max[1]-old_min[1]:.1f}pp')
print(f'差异: {(new_max[1]-new_min[1]) - (old_max[1]-old_min[1]):+.1f}pp')

# ============================================================
# 分析6：方案B——4暂→1柜, 4蛀→2栅（按并符特征更合理）
# 4暂=暂下破，说明有跌吞/跌连，应归入1柜/2栅
# 4蛀=非暂，说明排列较好，应归入0橅/1柜
# ============================================================
print('\n\n[6] 方案B：按并符逻辑分配')
print('=' * 60)

# 方案B分配逻辑：
# 4暂(暂下破) → 含异常并符 → 2栅(含跌连) 或 1柜(含跌吞)
# 4蛀(非暂) → 排列较好 → 0橅(完美) 或 1柜(含1跌吞)
# 5暂(暂下破) → 含异常并符 → 7姗(含跌连) 或 8姖(含跌吞)
# 5蛀(非暂) → 排列较好 → 9妩(完美) 或 8姖(含1跌吞)

# 但无法精确知道每个过渡区样本的并符
# 所以用P3接近度作为近似

# 方案B-1：4暂→2栅, 4蛀→1柜, 5暂→7姗, 5蛀→8姖
m_b1_0橅 = m_za_pos & (wk['地型'] == '0橅')
m_b1_1柜 = m_za_pos & ((wk['地型'] == '1柜') | (wk['地型'] == '4蛀'))
m_b1_2栅 = m_za_pos & ((wk['地型'] == '2栅') | (wk['地型'] == '4暂'))
m_b1_3桮 = m_za_pos & (wk['地型'] == '3桮')
m_b1_6娝 = m_za_neg & (wk['地型'] == '6娝')
m_b1_7姗 = m_za_neg & ((wk['地型'] == '7姗') | (wk['地型'] == '5暂'))
m_b1_8姖 = m_za_neg & ((wk['地型'] == '8姖') | (wk['地型'] == '5蛀'))
m_b1_9妩 = m_za_neg & (wk['地型'] == '9妩')

items = [
    ('【B1】0橅', m_b1_0橅),
    ('【B1】1柜(含4蛀)', m_b1_1柜),
    ('【B1】2栅(含4暂)', m_b1_2栅),
    ('【B1】3桮', m_b1_3桮),
    ('【B1】6娝', m_b1_6娝),
    ('【B1】7姗(含5暂)', m_b1_7姗),
    ('【B1】8姖(含5蛀)', m_b1_8姖),
    ('【B1】9妩', m_b1_9妩),
]
out = print_table('6. 方案B1', items)
print(out); output.append(out)

b1_p3s = []
for name, mask in items:
    p1, p3, avg, n = stats(mask)
    if p3 is not None: b1_p3s.append((name, p3, n))
b1_min = min(b1_p3s, key=lambda x: x[1])
b1_max = max(b1_p3s, key=lambda x: x[1])
print(f'\n方案B1: P3={b1_min[1]:.1f}%({b1_min[0]})~{b1_max[1]:.1f}%({b1_max[0]}), 区分度={b1_max[1]-b1_min[1]:.1f}pp')

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
新方案8类（过渡区归入后）vs 旧方案12类：

旧方案12类区分度: {old_max[1]-old_min[1]:.1f}pp
新方案8类区分度: {new_max[1]-new_min[1]:.1f}pp (方案A)
方案B1区分度: {b1_max[1]-b1_min[1]:.1f}pp

关键发现：
1. 过渡区样本（4暂/4蛀/5暂/5蛀）的P3介于远端各并符类之间
2. 归入后，新方案8类的区分度略有变化但方向稳定
3. WTZA只保留二元（>0/<0）后，地型逻辑大幅简化

建议：
- 采用新方案8类：WTZA>0→0橅/1柜/2栅/3桮，WTZA<0→6娝/7姗/8姖/9妩
- 过渡区样本按并符特征归入对应类（V/W计数决定）
- 完全删除4暂/4蛀/5暂/5蛀的分类
''')

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9l_地型新旧方案精确对比.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
    f.write('\n'.join([f'\n{"=" * 80}', '结论汇总', '=' * 80]))
print(f'\n结果已写入: {outpath}')