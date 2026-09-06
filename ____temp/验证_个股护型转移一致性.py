# -*- coding: utf-8 -*-
"""
个股护型转移矩阵 vs 综合矩阵一致性验证
========================================
问题：
1. 每个个股的护型转移矩阵是否与综合概率转移矩阵一致？差别有多大？
2. 综合概率矩阵是否能应用于个股预测？

方法：
- 综合矩阵：全高波池股票合并计算的 P(次日护型 | 当前护型)
- 个股矩阵：单只股票自己的 P(次日护型 | 当前护型)
- 对比指标：
  a) 平均绝对偏差 MAD（个股 vs 综合，按护型）
  b) argmax 一致率（综合最可能次日护型 vs 个股最可能次日护型）
  c) 预测准确率：综合矩阵 argmax 预测实际次日护型的命中率
  d) 样本量效应：按个股转移次数分组，看 MAD 如何随样本量变化

列序（旧列序）：[9]DXAB [13]日ZA [14]日ZC
"""
import csv, os, sys, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

HX_MAP = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
HX_ORDER = ['甲','乙','丙','丁','戊','己']

# 花册映射
with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

# 综合转移计数: (cur_hx, next_hx) -> count
agg_trans = defaultdict(int)
agg_row_total = defaultdict(int)
# 个股转移计数: (code, cur_hx, next_hx) -> count
stock_trans = defaultdict(int)
stock_row_total = defaultdict(int)
# 个股总转移次数
stock_total = defaultdict(int)

files_done = 0
for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        if board_map.get(cidl, '') not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            prev_hx = None
            for row in r:
                if len(row) < 15:
                    continue
                dxab = row[9]
                if len(dxab) < 1:
                    continue
                cur_hx = HX_MAP.get(dxab[0])
                if cur_hx is None:
                    continue
                if prev_hx is not None:
                    agg_trans[(prev_hx, cur_hx)] += 1
                    agg_row_total[prev_hx] += 1
                    stock_trans[(cidl, prev_hx, cur_hx)] += 1
                    stock_row_total[(cidl, prev_hx)] += 1
                    stock_total[cidl] += 1
                prev_hx = cur_hx
    except Exception:
        pass
    files_done += 1

print(f'高波池文件: {files_done}')

# ============ 1. 综合矩阵 ============
print('\n' + '='*80)
print('一、综合护型转移矩阵（高波池全量）')
print('='*80)
agg_p = {}
print(f'{"当前":<6} {"样本":>10} | ' + ' | '.join(f'{hx:>6}' for hx in HX_ORDER) + ' | 维持')
print('-'*80)
for cur in HX_ORDER:
    total = agg_row_total[cur]
    if total < 100:
        continue
    row = []
    for nxt in HX_ORDER:
        p = agg_trans[(cur, nxt)] / total * 100
        agg_p[(cur, nxt)] = p
        row.append(f'{p:>6.1f}')
    mr = agg_trans[(cur, cur)] / total * 100
    print(f'{cur:<6} {total:>10,} | ' + ' | '.join(row) + f' | {mr:>5.1f}%')

# ============ 2. 个股矩阵 vs 综合矩阵 ============
print('\n' + '='*80)
print('二、个股 vs 综合：平均绝对偏差 MAD（按护型）')
print('='*80)
# 对每只股票，计算每个当前护型的转移概率向量，与综合比较
# MAD_cur = mean over stocks of mean over next of |P_stock - P_agg|
mad_by_hx = defaultdict(list)  # cur_hx -> list of MAD values (per stock)
argmax_agree = defaultdict(lambda: [0,0])  # cur_hx -> [agree, total]
n_stocks_with_data = 0

for cidl in stock_total:
    # 该股票每个当前护型的转移
    for cur in HX_ORDER:
        total = stock_row_total[(cidl, cur)]
        if total < 20:  # 样本太少不比较
            continue
        # 该股票的转移概率向量
        stock_vec = []
        agg_vec = []
        for nxt in HX_ORDER:
            sp = stock_trans[(cidl, cur, nxt)] / total * 100
            ap = agg_p.get((cur, nxt), 0)
            stock_vec.append(sp)
            agg_vec.append(ap)
        # MAD
        mad = sum(abs(s-a) for s,a in zip(stock_vec, agg_vec)) / len(HX_ORDER)
        mad_by_hx[cur].append(mad)
        # argmax 一致率
        stock_argmax = HX_ORDER[stock_vec.index(max(stock_vec))]
        agg_argmax = HX_ORDER[agg_vec.index(max(agg_vec))]
        argmax_agree[cur][0] += (1 if stock_argmax == agg_argmax else 0)
        argmax_agree[cur][1] += 1
    n_stocks_with_data += 1

print(f'有数据的个股数: {n_stocks_with_data}')
print(f'{"当前护型":<8} {"个股数":>8} {"平均MAD(pp)":>12} {"MAD中位(pp)":>12} {"argmax一致率":>12}')
print('-'*60)
for cur in HX_ORDER:
    if cur not in mad_by_hx:
        continue
    vals = mad_by_hx[cur]
    vals_sorted = sorted(vals)
    med = vals_sorted[len(vals_sorted)//2]
    agree, tot = argmax_agree[cur]
    print(f'{cur:<8} {len(vals):>8} {sum(vals)/len(vals):>12.2f} {med:>12.2f} {agree/tot*100:>11.1f}%')

# ============ 3. 综合矩阵预测个股的准确率 ============
print('\n' + '='*80)
print('三、综合矩阵 argmax 预测个股次日护型的命中率')
print('='*80)
# 对每个转移 (cur -> actual next)，综合矩阵 argmax(cur) 是否= actual next
# 对比：个股自身 argmax 的命中率
agg_hit = defaultdict(lambda: [0,0])   # cur -> [hit, total]
stock_hit = defaultdict(lambda: [0,0]) # cur -> [hit, total]
for cidl in stock_total:
    for cur in HX_ORDER:
        total = stock_row_total[(cidl, cur)]
        if total < 20:
            continue
        # 综合 argmax
        agg_argmax = max(HX_ORDER, key=lambda hx: agg_p.get((cur, hx), 0))
        # 个股 argmax
        stock_argmax = max(HX_ORDER, key=lambda hx: stock_trans[(cidl, cur, hx)] / total)
        for nxt in HX_ORDER:
            cnt = stock_trans[(cidl, cur, nxt)]
            if cnt == 0:
                continue
            agg_hit[cur][1] += cnt
            if nxt == agg_argmax:
                agg_hit[cur][0] += cnt
            stock_hit[cur][1] += cnt
            if nxt == stock_argmax:
                stock_hit[cur][0] += cnt

print(f'{"当前护型":<8} {"综合argmax命中":>14} {"个股argmax命中":>14} {"提升":>8}')
print('-'*50)
for cur in HX_ORDER:
    if agg_hit[cur][1] == 0:
        continue
    ah = agg_hit[cur][0]/agg_hit[cur][1]*100
    sh = stock_hit[cur][0]/stock_hit[cur][1]*100
    print(f'{cur:<8} {ah:>13.1f}% {sh:>13.1f}% {sh-ah:>+7.1f}pp')

# ============ 4. 样本量效应 ============
print('\n' + '='*80)
print('四、样本量效应：个股转移次数 vs MAD')
print('='*80)
# 按个股总转移次数分组
bins = [(0,50),(50,200),(200,500),(500,1000),(1000,2000),(2000,5000),(5000,100000)]
bin_mad = defaultdict(list)
for cidl in stock_total:
    n = stock_total[cidl]
    for cur in HX_ORDER:
        total = stock_row_total[(cidl, cur)]
        if total < 20:
            continue
        stock_vec = [stock_trans[(cidl, cur, nxt)]/total*100 for nxt in HX_ORDER]
        agg_vec = [agg_p.get((cur, nxt), 0) for nxt in HX_ORDER]
        mad = sum(abs(s-a) for s,a in zip(stock_vec, agg_vec)) / len(HX_ORDER)
        for lo, hi in bins:
            if lo <= n < hi:
                bin_mad[(lo,hi)].append(mad)
                break
print(f'{"个股转移次数":<16} {"个股数":>8} {"平均MAD(pp)":>12}')
print('-'*40)
for lo, hi in bins:
    if (lo,hi) in bin_mad:
        vals = bin_mad[(lo,hi)]
        print(f'{lo}-{hi:<12} {len(vals):>8} {sum(vals)/len(vals):>12.2f}')

# ============ 5. 极端个股：MAD 最大/最小的股票 ============
print('\n' + '='*80)
print('五、MAD 最大/最小的个股（整体平均 MAD）')
print('='*80)
stock_avg_mad = {}
for cidl in stock_total:
    mads = []
    for cur in HX_ORDER:
        total = stock_row_total[(cidl, cur)]
        if total < 20:
            continue
        stock_vec = [stock_trans[(cidl, cur, nxt)]/total*100 for nxt in HX_ORDER]
        agg_vec = [agg_p.get((cur, nxt), 0) for nxt in HX_ORDER]
        mads.append(sum(abs(s-a) for s,a in zip(stock_vec, agg_vec)) / len(HX_ORDER))
    if mads:
        stock_avg_mad[cidl] = sum(mads)/len(mads)
sorted_mad = sorted(stock_avg_mad.items(), key=lambda x: x[1])
print('MAD 最小的 5 只（最接近综合）:')
for cidl, mad in sorted_mad[:5]:
    print(f'  {cidl}: MAD={mad:.2f}pp, 转移次数={stock_total[cidl]:,}')
print('MAD 最大的 5 只（最偏离综合）:')
for cidl, mad in sorted_mad[-5:]:
    print(f'  {cidl}: MAD={mad:.2f}pp, 转移次数={stock_total[cidl]:,}')
