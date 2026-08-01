# -*- coding: utf-8 -*-
"""
DXZC+DXAB 分市板 + 个体差异分析
"""
import csv, os, sys, io
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HU_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}
HU_ORDER = ['甲', '乙', '丙', '丁', '戊', '己']

datadir = r'昭明算展\谕组日'
files = sorted(os.listdir(datadir))

# 市板分类
def get_board(code):
    if code.startswith('sh'):
        # 上海：sh600=沪主板, sh000=指数, sh688=科创板
        if code.startswith('sh68'):
            return '科创板'
        elif code.startswith('sh60'):
            return '沪主板'
        elif code.startswith('sh00'):
            return '指数'
        else:
            return '沪其他'
    elif code.startswith('sz'):
        # 深圳：sz00=深主板, sz30=创业板
        if code.startswith('sz30'):
            return '创业板'
        elif code.startswith('sz00'):
            return '深主板'
        else:
            return '深其他'
    elif code.startswith('bj'):
        return '北交所'
    return '其他'

# 按 (市板, ZC符号, 护型) 分组
board_groups = defaultdict(lambda: {
    'count': 0, 'sum_ret': 0.0, 'sum_ret_sq': 0.0,
    'win_ret': 0, 'sum_next_high': 0.0, 'win_next_high': 0
})

# 按股票统计（用于个体差异分析）
stock_stats = defaultdict(lambda: defaultdict(lambda: {
    'count': 0, 'sum_ret': 0.0, 'win_ret': 0
}))

total = 0
for fname in files:
    fp = os.path.join(datadir, fname)
    code = fname.replace('谕组日_', '').replace('.csv', '')
    board = get_board(code)
    if board == '指数' or board == '其他':
        continue
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

                # 市板统计
                key = (board, zc_sign, hu)
                board_groups[key]['count'] += 1
                board_groups[key]['sum_ret'] += ret
                board_groups[key]['sum_ret_sq'] += ret * ret
                if ret > 0: board_groups[key]['win_ret'] += 1
                if nh is not None:
                    board_groups[key]['sum_next_high'] += nh
                    if nh > 0: board_groups[key]['win_next_high'] += 1

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
# 1. 分市板对比
# ============================================================
print('=' * 80)
print('分市板对比')
print('=' * 80)

boards = ['沪主板', '深主板', '创业板', '科创板', '北交所']
for board in boards:
    print(f'\n【{board}】')
    print(f'{"护型":>4} {"ZC>0均涨":>8} {"ZC>0涨率":>8} {"ZC>0样本":>8} {"ZC<0均涨":>8} {"ZC<0涨率":>8} {"ZC<0样本":>8}')
    for hu in HU_ORDER:
        pk = (board, 'pos', hu)
        nk = (board, 'neg', hu)
        pg = board_groups[pk]
        ng = board_groups[nk]
        p_ret = pg['sum_ret'] / pg['count'] if pg['count'] else 0
        n_ret = ng['sum_ret'] / ng['count'] if ng['count'] else 0
        p_wr = pg['win_ret'] / pg['count'] * 100 if pg['count'] else 0
        n_wr = ng['win_ret'] / ng['count'] * 100 if ng['count'] else 0
        print(f'{hu:>4} {p_ret:>8.2f} {p_wr:>8.1f} {pg["count"]:>8,} {n_ret:>8.2f} {n_wr:>8.1f} {ng["count"]:>8,}')

# ============================================================
# 2. 个股差异分析
# ============================================================
print('\n' + '=' * 80)
print('个体差异分析')
print('=' * 80)

# 分析每个护型在ZC>0时，个股之间表现的差异
for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    print(f'\n【{zc_label} 个股差异】')
    print(f'{"护型":>4} {"有数据股票":>8} {"均值中位数":>10} {"均值P25":>8} {"均值P75":>8} {"均值±σ":>8} {"涨率中位数":>10} {"涨率P25":>8} {"涨率P75":>8}')

    for hu in HU_ORDER:
        code_avgs = []
        code_wrs = []
        for code, data in stock_stats.items():
            key = (zc_sign, hu)
            if key in data and data[key]['count'] >= 10:  # 至少10个样本
                d = data[key]
                code_avgs.append(d['sum_ret'] / d['count'])
                code_wrs.append(d['win_ret'] / d['count'] * 100)

        if len(code_avgs) < 10:
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

        # 标准差
        mean_avg = sum(code_avgs) / n
        variance = sum((x - mean_avg) ** 2 for x in code_avgs) / n
        std = variance ** 0.5

        print(f'{hu:>4} {n:>8} {med_avg:>10.2f} {p25_avg:>8.2f} {p75_avg:>8.2f} {std:>8.2f} {med_wr:>10.1f} {p25_wr:>8.1f} {p75_wr:>8.1f}')

# ============================================================
# 3. 护型排序稳定性分析
# ============================================================
print('\n' + '=' * 80)
print('护型排序稳定性（按市板）')
print('=' * 80)

for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    print(f'\n【{zc_label} 各市板护型排序】')
    for board in boards:
        board_scores = []
        for hu in HU_ORDER:
            key = (board, zc_sign, hu)
            g = board_groups[key]
            if g['count'] > 0:
                avg_ret = g['sum_ret'] / g['count']
                board_scores.append((hu, avg_ret))

        board_scores.sort(key=lambda x: x[1], reverse=True)
        rank_str = ' > '.join([f'{hu}({ret:.2f})' for hu, ret in board_scores])
        print(f'  {board}: {rank_str}')

# ============================================================
# 4. 己 vs 甲乙 对比 - 各市板
# ============================================================
print('\n' + '=' * 80)
print('己 vs 甲乙 对比（各市板）')
print('=' * 80)

for board in boards:
    print(f'\n【{board}】')
    for tag, hus in [('己', ['己']), ('甲乙', ['甲', '乙']), ('丙丁', ['丙', '丁']), ('戊', ['戊'])]:
        for zc_sign, zc_label in [('pos', 'ZC>0'), ('neg', 'ZC<0')]:
            total_c = 0
            total_ret = 0
            total_win = 0
            for hu in hus:
                g = board_groups[(board, zc_sign, hu)]
                total_c += g['count']
                total_ret += g['sum_ret']
                total_win += g['win_ret']
            if total_c:
                avg_ret = total_ret / total_c
                wr = total_win / total_c * 100
                print(f'  {tag} {zc_label}: 样本={total_c:>8,} 均涨={avg_ret:.2f}% 涨率={wr:.1f}%')

# ============================================================
# 5. 总结
# ============================================================
print('\n' + '=' * 80)
print('结论')
print('=' * 80)

# 计算跨市板的一致性
print('\n跨市板排序一致性检验：')
for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    # 各市板的护型排序
    all_ranks = defaultdict(list)
    for board in boards:
        board_scores = []
        for hu in HU_ORDER:
            key = (board, zc_sign, hu)
            g = board_groups[key]
            if g['count'] > 0:
                board_scores.append((hu, g['sum_ret'] / g['count']))
        board_scores.sort(key=lambda x: x[1], reverse=True)
        for rank, (hu, _) in enumerate(board_scores):
            all_ranks[hu].append(rank)

    print(f'\n  {zc_label}:')
    for hu in HU_ORDER:
        ranks = all_ranks.get(hu, [])
        if ranks:
            avg_rank = sum(ranks) / len(ranks)
            rank_range = max(ranks) - min(ranks)
            print(f'    {hu}: 平均排名={avg_rank:.1f} 排名跨度={rank_range}')