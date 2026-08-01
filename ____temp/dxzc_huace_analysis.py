# -*- coding: utf-8 -*-
"""
DXZC+DXAB 按花册分类分析
花册分类说明：沪深300/中证500/中证小盘/中证非/基金ETF/指数
"""
import csv, os, sys, io, json
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HU_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}
HU_ORDER = ['甲', '乙', '丙', '丁', '戊', '己']

# 加载花册映射
with open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8') as f:
    花册 = json.load(f)

# 有效花册分组（排除指数和基金ETF）
有效分组 = ['沪深300', '中证500', '中证小盘', '中证非']

datadir = r'昭明算展\谕组日'
files = sorted(os.listdir(datadir))

# 按 (花册组, ZC符号, 护型) 分组
hg = defaultdict(lambda: {
    'count': 0, 'sum_ret': 0.0, 'sum_ret_sq': 0.0,
    'win_ret': 0, 'sum_next_high': 0.0, 'win_next_high': 0
})

# 个股统计
stock_stats = defaultdict(lambda: defaultdict(lambda: {
    'count': 0, 'sum_ret': 0.0, 'win_ret': 0
}))

total = 0
花册分布 = Counter()
for fname in files:
    fp = os.path.join(datadir, fname)
    code = fname.replace('谕组日_', '').replace('.csv', '')
    # 查花册
    group = 花册.get(code, '未知')
    if group not in 有效分组:
        continue
    花册分布[group] += 1
    try:
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dxab_raw = str(row.get('DXAB', '')).strip()
                zc_raw = str(row.get('日ZC', '')).strip()
                ret_raw = str(row.get('涨幅', '')).strip()
                nh_raw = str(row.get('次日高幅', '')).strip()

                if not dxab_raw or not zc_raw:
                    continue
                first_char = dxab_raw[0] if dxab_raw else ''
                hu = HU_MAP.get(first_char, '')
                if not hu:
                    continue
                try:
                    zc = float(zc_raw)
                except ValueError:
                    continue
                try:
                    ret = float(ret_raw)
                except ValueError:
                    ret = 0.0
                try:
                    nh = float(nh_raw)
                except ValueError:
                    nh = None

                zc_sign = 'pos' if zc > 0 else ('neg' if zc < 0 else 'zero')

                key = (group, zc_sign, hu)
                hg[key]['count'] += 1
                hg[key]['sum_ret'] += ret
                hg[key]['sum_ret_sq'] += ret * ret
                if ret > 0: hg[key]['win_ret'] += 1
                if nh is not None:
                    hg[key]['sum_next_high'] += nh
                    if nh > 0: hg[key]['win_next_high'] += 1

                # 个股统计
                skey = (zc_sign, hu)
                if stock_stats[code][skey]['count'] == 0:
                    stock_stats[code][skey] = {'count': 0, 'sum_ret': 0.0, 'win_ret': 0}
                stock_stats[code][skey]['count'] += 1
                stock_stats[code][skey]['sum_ret'] += ret
                if ret > 0: stock_stats[code][skey]['win_ret'] += 1
                total += 1
    except:
        pass

print(f'总样本: {total:,}')
print()

# ============================================================
# 1. 花册分布
# ============================================================
print('=' * 80)
print('花册分布（有数据文件）')
print('=' * 80)
for g, cnt in 花册分布.most_common():
    print(f'  {g}: {cnt}只')

# ============================================================
# 2. 按花册分组的护型表现
# ============================================================
print('\n' + '=' * 80)
print('按花册分组的护型表现')
print('=' * 80)

for group in 有效分组:
    print(f'\n【{group}】')
    print(f'{"护型":>4} {"ZC>0均涨":>8} {"ZC>0涨率":>8} {"ZC>0样本":>8} {"ZC>0次高":>8} {"ZC<0均涨":>8} {"ZC<0涨率":>8} {"ZC<0样本":>8}')
    for hu in HU_ORDER:
        pk = (group, 'pos', hu)
        nk = (group, 'neg', hu)
        pg = hg[pk]
        ng = hg[nk]
        p_ret = pg['sum_ret'] / pg['count'] if pg['count'] else 0
        n_ret = ng['sum_ret'] / ng['count'] if ng['count'] else 0
        p_wr = pg['win_ret'] / pg['count'] * 100 if pg['count'] else 0
        n_wr = ng['win_ret'] / ng['count'] * 100 if ng['count'] else 0
        p_nh = pg['sum_next_high'] / pg['count'] if pg['count'] else 0
        print(f'{hu:>4} {p_ret:>8.2f} {p_wr:>8.1f} {pg["count"]:>8,} {p_nh:>8.2f} {n_ret:>8.2f} {n_wr:>8.1f} {ng["count"]:>8,}')

# ============================================================
# 3. 排序稳定性
# ============================================================
print('\n' + '=' * 80)
print('护型排序稳定性（按花册）')
print('=' * 80)

for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    print(f'\n【{zc_label}】')
    for group in 有效分组:
        scores = []
        for hu in HU_ORDER:
            key = (group, zc_sign, hu)
            g = hg[key]
            if g['count'] > 0:
                scores.append((hu, g['sum_ret'] / g['count']))
        scores.sort(key=lambda x: x[1], reverse=True)
        rank_str = ' > '.join([f'{hu}({ret:.2f})' for hu, ret in scores])
        print(f'  {group}: {rank_str}')

# ============================================================
# 4. 个体差异
# ============================================================
print('\n' + '=' * 80)
print('个体差异（按花册分组）')
print('=' * 80)

for group in 有效分组:
    print(f'\n【{group} 个股差异 - DXZC>0】')
    print(f'{"护型":>4} {"有数据":>6} {"均值中位":>8} {"P25":>6} {"P75":>6} {"σ":>6} {"涨率中位":>8} {"涨率P25":>8} {"涨率P75":>8}')
    for hu in HU_ORDER:
        code_avgs = []
        code_wrs = []
        # 只取属于该花册的股票
        for code, data in stock_stats.items():
            if 花册.get(code, '') != group:
                continue
            key = (zc_sign, hu)
            if key in data and data[key]['count'] >= 10:
                d = data[key]
                code_avgs.append(d['sum_ret'] / d['count'])
                code_wrs.append(d['win_ret'] / d['count'] * 100)

        if len(code_avgs) < 5:
            continue

        code_avgs.sort()
        code_wrs.sort()
        n = len(code_avgs)
        med_avg = code_avgs[n // 2]
        p25_avg = code_avgs[n // 4]
        p75_avg = code_avgs[3 * n // 4]
        med_wr = code_wrs[n // 2]
        p25_wr = code_wrs[n // 4]
        p75_wr = code_wrs[3 * n // 4]
        mean_avg = sum(code_avgs) / n
        variance = sum((x - mean_avg) ** 2 for x in code_avgs) / n
        std = variance ** 0.5

        print(f'{hu:>4} {n:>6} {med_avg:>8.2f} {p25_avg:>6.2f} {p75_avg:>6.2f} {std:>6.2f} {med_wr:>8.1f} {p25_wr:>8.1f} {p75_wr:>8.1f}')

# ============================================================
# 5. 结论汇总
# ============================================================
print('\n' + '=' * 80)
print('跨花册排序一致性检验')
print('=' * 80)

for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    all_ranks = defaultdict(list)
    for group in 有效分组:
        scores = []
        for hu in HU_ORDER:
            key = (group, zc_sign, hu)
            g = hg[key]
            if g['count'] > 0:
                scores.append((hu, g['sum_ret'] / g['count']))
        scores.sort(key=lambda x: x[1], reverse=True)
        for rank, (hu, _) in enumerate(scores):
            all_ranks[hu].append(rank)

    print(f'\n  {zc_label}:')
    for hu in HU_ORDER:
        ranks = all_ranks.get(hu, [])
        if ranks:
            avg_rank = sum(ranks) / len(ranks)
            span = max(ranks) - min(ranks)
            print(f'    {hu}: 平均排名={avg_rank:.1f} 排名跨度={span}')