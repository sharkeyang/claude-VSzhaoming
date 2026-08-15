#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MC3.9m_地型新方案精确统计.py
=====================
精确统计新方案8类（过渡区样本按并符逻辑归入）。

方法：
1. 对ZA≥4的样本：直接用当前地型（0橅/1柜/2栅/3桮）
2. 对ZA<-3的样本：直接用当前地型（6娝/7姗/8姖/9妩）
3. 对过渡区（ZA=0~3和ZA=-1~-3）的样本：
   - 用波型主类作为并符的代理，训练一个从主类→并符类的映射
   - 映射基于ZA≥4和ZA<-3区域中，各主类在并符类中的分布比例
4. 对比新旧方案

用法：
    python _产出物/MC3.9m_地型新方案精确统计.py
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
print('MC3.9m 地型新方案精确统计')
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

m_za_pos = wk['ZA周'] > 0
m_za_neg = wk['ZA周'] < 0

# ============================================================
# 构建从主类→并符类的映射
# 基于ZA≥4区域（上端）和ZA<-3区域（下端）的训练数据
# ============================================================
print('\n[1] 构建主类→并符类映射')
print('=' * 60)

# 上端训练数据：ZA≥4的样本
m_train_up = wk['ZA周'] >= 4
# 下端训练数据：ZA<-3的样本
m_train_down = wk['ZA周'] < -3

# 统计每个主类在上端各并符类中的分布
up_map = {}  # 主类 → 最可能的并符类
for main_cls in wk.loc[m_train_up, '主类'].unique():
    m_mc = m_train_up & (wk['主类'] == main_cls)
    dist = {}
    for d in ['0橅', '1柜', '2栅', '3桮']:
        dist[d] = (m_mc & (wk['地型'] == d)).sum()
    total_mc = sum(dist.values())
    if total_mc > 0:
        best = max(dist, key=dist.get)
        up_map[main_cls] = (best, dist[best]/total_mc)

# 统计每个主类在下端各并符类中的分布
down_map = {}
for main_cls in wk.loc[m_train_down, '主类'].unique():
    m_mc = m_train_down & (wk['主类'] == main_cls)
    dist = {}
    for d in ['6娝', '7姗', '8姖', '9妩']:
        dist[d] = (m_mc & (wk['地型'] == d)).sum()
    total_mc = sum(dist.values())
    if total_mc > 0:
        best = max(dist, key=dist.get)
        down_map[main_cls] = (best, dist[best]/total_mc)

print('上端映射（ZA≥4训练）：')
for mc, (best, pct) in sorted(up_map.items(), key=lambda x: -x[1][1])[:15]:
    print(f'  {mc:20s} → {best} (占比{pct*100:.0f}%)')

print('\n下端映射（ZA<-3训练）：')
for mc, (best, pct) in sorted(down_map.items(), key=lambda x: -x[1][1])[:15]:
    print(f'  {mc:20s} → {best} (占比{pct*100:.0f}%)')

# ============================================================
# 应用映射：为所有样本分配新地型
# ============================================================
print('\n\n[2] 分配新地型')
print('=' * 60)

def get_new_dixing(row):
    """根据WTZA正负和主类，分配新地型"""
    dixing = row['地型']
    za = row['ZA周']
    main_cls = row['主类']

    # 远端样本：直接保留
    if za >= 4:
        return dixing  # 0橅/1柜/2栅/3桮
    if za < -3:
        return dixing  # 6娝/7姗/8姖/9妩

    # 过渡区样本：按主类映射
    if za > 0:  # ZA=1~3
        if main_cls in up_map:
            return up_map[main_cls][0]
        else:
            return '0橅'  # 默认
    elif za < 0:  # ZA=-1~-3
        if main_cls in down_map:
            return down_map[main_cls][0]
        else:
            return '9妩'  # 默认
    else:
        return '未知'

wk['新地型'] = wk.apply(get_new_dixing, axis=1)

# 统计新地型分布
print('新地型分布：')
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    n = (wk['新地型'] == d).sum()
    print(f'  {d}: {n:>10,} 行 ({n/total*100:.1f}%)')

# ============================================================
# 分析3：新方案8类P3
# ============================================================
print('\n\n[3] 新方案8类P3')
print('=' * 60)

items = []
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    items.append((f'【新】{d}', wk['新地型'] == d))
out = print_table('3. 新方案8类', items)
print(out); output.append(out)

# 计算新方案8类的P3范围
new_p3s = []
for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    p1, p3, avg, n = stats(wk['新地型'] == d)
    if p3 is not None: new_p3s.append((d, p3, n))

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
# 分析4：新旧方案逐类对比
# ============================================================
print('\n\n[4] 新旧方案逐类对比')
print('=' * 60)

# 旧方案各类的样本，在新方案中被分到了哪里？
print('旧方案→新方案 迁移矩阵：')
for d_old in ['4暂', '4蛀', '5暂', '5蛀']:
    m_old = wk['地型'] == d_old
    n_old = m_old.sum()
    dist = wk.loc[m_old, '新地型'].value_counts()
    print(f'\n{d_old} (n={n_old:,}):')
    for d_new, cnt in dist.items():
        print(f'  → {d_new}: {cnt} ({cnt/n_old*100:.1f}%)')

# ============================================================
# 分析5：新方案中各类的P3 vs 旧方案中对应类的P3
# ============================================================
print('\n\n[5] 新方案各类P3 vs 旧方案对应类P3')
print('=' * 60)

for d in ['0橅', '1柜', '2栅', '3桮', '6娝', '7姗', '8姖', '9妩']:
    p1_new, p3_new, avg_new, n_new = stats(wk['新地型'] == d)
    # 旧方案中对应的类（可能包含过渡区）
    if d in ['0橅','1柜','2栅','3桮']:
        m_old = m_za_pos & (wk['地型'] == d)
    else:
        m_old = m_za_neg & (wk['地型'] == d)
    p1_old, p3_old, avg_old, n_old = stats(m_old)

    if p3_new is not None and p3_old is not None:
        print(f'{d}: 新P3={p3_new:.1f}%(n={n_new:,}) vs 旧P3={p3_old:.1f}%(n={n_old:,}), 差={p3_new-p3_old:+.1f}pp')

# ============================================================
# 结论
# ============================================================
print()
print('=' * 60)
print('结论')
print('=' * 60)
print(f'''
新方案8类（按主类映射归入过渡区）vs 旧方案12类：

旧方案12类区分度: {old_max[1]-old_min[1]:.1f}pp
新方案8类区分度: {new_max[1]-new_min[1]:.1f}pp
差异: {(new_max[1]-new_min[1]) - (old_max[1]-old_min[1]):+.1f}pp

新方案8类定义：
  WTZA>0 → 0橅/1柜/2栅/3桮（按前4柱V/W计数）
  WTZA<0 → 6娝/7姗/8姖/9妩（按前4柱O/Q计数）
  过渡区样本按主类映射归入对应并符类
  完全删除4暂/4蛀/5暂/5蛀
''')

# 写入文件
outpath = os.path.join(OUTDIR, 'MC3.9m_地型新方案精确统计.txt')
with open(outpath, 'w', encoding='utf-8') as f:
    f.write('\n'.join(output))
    f.write('\n'.join([f'\n{"=" * 80}', '结论汇总', '=' * 80]))
print(f'\n结果已写入: {outpath}')