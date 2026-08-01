# -*- coding: utf-8 -*-
"""
DXZC+DXAB 模型验证脚本
验证基于均线的最小模型：DXZC作为阈值，DXAB六种护型（甲乙丙丁戊己）的通用规律
"""

import csv, os, sys, io
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 护型映射
HU_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}
HU_ORDER = ['甲', '乙', '丙', '丁', '戊', '己']

# ============================================================
# 1. 日线数据验证
# ============================================================
print('=' * 80)
print('【日线 DXZC+DXAB 模型验证】')
print('=' * 80)

datadir = r'昭明算展\谕组日'
files = sorted(os.listdir(datadir))
print(f'共 {len(files)} 只股票')

# 收集数据：按 (ZC符号, 护型) 分组
# ZC符号: 'pos' (>0), 'neg' (<0), 'zero' (=0)
groups = defaultdict(lambda: {
    'count': 0, 'sum_ret': 0.0, 'sum_next_high': 0.0,
    'win_ret': 0, 'win_next_high': 0,
    'ret_gt1': 0, 'ret_gt2': 0, 'ret_gt3': 0, 'ret_gt5': 0,
    'next_high_gt1': 0, 'next_high_gt2': 0, 'next_high_gt3': 0, 'next_high_gt5': 0,
    'stocks': set()
})

total_rows = 0
for fname in files[:500]:  # 先跑500只进行快速验证
    fp = os.path.join(datadir, fname)
    code = fname.replace('谕组日_', '').replace('.csv', '')
    try:
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dxab_raw = str(row.get('DXAB', '')).strip()
                zc_raw = str(row.get('日ZC', '')).strip()
                ret_raw = str(row.get('涨幅', '')).strip()
                next_high_raw = str(row.get('次日高幅', '')).strip()

                if not dxab_raw or not zc_raw:
                    continue

                # 解析护型
                first_char = dxab_raw[0] if dxab_raw else ''
                hu = HU_MAP.get(first_char, '')
                if not hu:
                    continue

                # 解析ZC
                try:
                    zc = float(zc_raw)
                except ValueError:
                    continue

                # 解析收益率
                try:
                    ret = float(ret_raw)
                except ValueError:
                    ret = 0.0
                try:
                    next_high = float(next_high_raw)
                except ValueError:
                    next_high = None

                # ZC符号
                if zc > 0:
                    zc_sign = 'pos'
                elif zc < 0:
                    zc_sign = 'neg'
                else:
                    zc_sign = 'zero'

                key = (zc_sign, hu)
                groups[key]['count'] += 1
                groups[key]['sum_ret'] += ret
                groups[key]['stocks'].add(code)

                if ret > 0:
                    groups[key]['win_ret'] += 1
                if ret > 1: groups[key]['ret_gt1'] += 1
                if ret > 2: groups[key]['ret_gt2'] += 1
                if ret > 3: groups[key]['ret_gt3'] += 1
                if ret > 5: groups[key]['ret_gt5'] += 1

                if next_high is not None:
                    groups[key]['sum_next_high'] += next_high
                    if next_high > 0:
                        groups[key]['win_next_high'] += 1
                    if next_high > 1: groups[key]['next_high_gt1'] += 1
                    if next_high > 2: groups[key]['next_high_gt2'] += 1
                    if next_high > 3: groups[key]['next_high_gt3'] += 1
                    if next_high > 5: groups[key]['next_high_gt5'] += 1

                total_rows += 1
    except Exception:
        pass

print(f'总样本数: {total_rows:,}')
print()

# 输出结果
for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0'), ('zero', 'DXZC=0')]:
    print(f'\n{"─" * 70}')
    print(f'【{zc_label}】')
    print(f'{"护型":>4} {"样本":>8} {"涨幅%":>8} {"次日高%":>8} {"涨率%":>8} {"次日高率%":>8} {"次日高>1%":>8} {"次日高>3%":>8} {"次日高>5%":>8} {"股票数":>8}')
    print(f'{"─" * 70}')
    for hu in HU_ORDER:
        key = (zc_sign, hu)
        g = groups[key]
        if g['count'] == 0:
            continue
        avg_ret = g['sum_ret'] / g['count']
        avg_next_high = g['sum_next_high'] / g['count'] if g['count'] > 0 else 0
        win_rate = g['win_ret'] / g['count'] * 100
        next_high_rate = g['win_next_high'] / g['count'] * 100
        nh_gt1 = g['next_high_gt1'] / g['count'] * 100
        nh_gt3 = g['next_high_gt3'] / g['count'] * 100
        nh_gt5 = g['next_high_gt5'] / g['count'] * 100
        print(f'{hu:>4} {g["count"]:>8,} {avg_ret:>8.2f} {avg_next_high:>8.2f} {win_rate:>8.1f} {next_high_rate:>8.1f} {nh_gt1:>8.1f} {nh_gt3:>8.1f} {nh_gt5:>8.1f} {len(g["stocks"]):>8}')

print()
print('=' * 80)
print('【关键假设验证】')
print('=' * 80)

# 假设1: DXZC<0时，仅甲乙己有效
print('\n▎假设1: DXZC<0时，仅甲乙己可操作')
for hu in ['甲', '乙', '己']:
    key = ('neg', hu)
    g = groups[key]
    avg_ret = g['sum_ret'] / g['count'] if g['count'] else 0
    avg_nh = g['sum_next_high'] / g['count'] if g['count'] else 0
    print(f'  {hu}: 样本={g["count"]:>8,} 涨幅={avg_ret:>6.2f}% 次日高={avg_nh:>6.2f}% 涨率={g["win_ret"]/g["count"]*100:.1f}%' if g['count'] else f'  {hu}: 无数据')
for hu in ['丙', '丁', '戊']:
    key = ('neg', hu)
    g = groups[key]
    avg_ret = g['sum_ret'] / g['count'] if g['count'] else 0
    avg_nh = g['sum_next_high'] / g['count'] if g['count'] else 0
    print(f'  {hu}: 样本={g["count"]:>8,} 涨幅={avg_ret:>6.2f}% 次日高={avg_nh:>6.2f}% 涨率={g["win_ret"]/g["count"]*100:.1f}% (对照)' if g['count'] else f'  {hu}: 无数据')

# 假设2: DXZC>0时，甲乙优选，丙丁被动，戊试仓，己基本
print('\n▎假设2: DXZC>0时，各护型表现分层')
for hu in HU_ORDER:
    key = ('pos', hu)
    g = groups[key]
    avg_ret = g['sum_ret'] / g['count'] if g['count'] else 0
    avg_nh = g['sum_next_high'] / g['count'] if g['count'] else 0
    nh_gt0 = g['win_next_high'] / g['count'] * 100 if g['count'] else 0
    nh_gt2 = g['next_high_gt2'] / g['count'] * 100 if g['count'] else 0
    print(f'  {hu}: 样本={g["count"]:>8,} 涨幅={avg_ret:>6.2f}% 次日高={avg_nh:>6.2f}% 涨率={g["win_ret"]/g["count"]*100:.1f}% 次日高率={nh_gt0:.1f}% 高>2%={nh_gt2:.1f}%')

# 假设3: 对比DXZC>0 vs DXZC<0 的各护型差异
print('\n▎假设3: DXZC>0 vs DXZC<0 护型效果对比')
print(f'{"护型":>4} {"ZC>0样本":>10} {"ZC>0涨率":>10} {"ZC>0均涨":>10} {"ZC<0样本":>10} {"ZC<0涨率":>10} {"ZC<0均涨":>10} {"差异":>8}')
for hu in HU_ORDER:
    pos_key = ('pos', hu)
    neg_key = ('neg', hu)
    pg = groups[pos_key]
    ng = groups[neg_key]
    p_ret = pg['sum_ret'] / pg['count'] if pg['count'] else 0
    n_ret = ng['sum_ret'] / ng['count'] if ng['count'] else 0
    p_wr = pg['win_ret'] / pg['count'] * 100 if pg['count'] else 0
    n_wr = ng['win_ret'] / ng['count'] * 100 if ng['count'] else 0
    diff = p_ret - n_ret
    print(f'{hu:>4} {pg["count"]:>10,} {p_wr:>10.1f} {p_ret:>10.2f} {ng["count"]:>10,} {n_wr:>10.1f} {n_ret:>10.2f} {diff:>+8.2f}')

# 假设4: 己 vs 甲乙 + 丙丁戊 对比
print('\n▎假设4: 己 作为介入基本条件的有效性')
# DXZC>0时: 己 vs 甲乙 vs 丙丁
for tag, hus in [('甲乙优选', ['甲','乙']), ('己(基本条件)', ['己']), ('丙丁被动', ['丙','丁']), ('戊(试仓)', ['戊'])]:
    key_pos = ('pos', '甲')
    total = 0
    sum_ret = 0
    sum_nh = 0
    win = 0
    nh_win = 0
    for hu in hus:
        g = groups[('pos', hu)]
        total += g['count']
        sum_ret += g['sum_ret']
        sum_nh += g['sum_next_high']
        win += g['win_ret']
        nh_win += g['win_next_high']
    if total:
        print(f'  {tag}: 样本={total:>8,} 均涨={sum_ret/total:>6.2f}% 均次高={sum_nh/total:>6.2f}% 涨率={win/total*100:.1f}% 次高率={nh_win/total*100:.1f}%')

# ============================================================
# 2. 周线数据验证
# ============================================================
print('\n\n' + '=' * 80)
print('【周线 WXZC+WXAB 模型验证】')
print('=' * 80)

datadir_z = r'昭明算展\谕组周'
files_z = sorted(os.listdir(datadir_z))
print(f'共 {len(files_z)} 只股票')

# 周线护型映射（直接是中文）
WEEK_HU = ['甲', '乙', '丙', '丁', '戊', '己']

z_groups = defaultdict(lambda: {
    'count': 0, 'sum_ret': 0.0,
    'win_ret': 0,
    'ret_gt1': 0, 'ret_gt3': 0, 'ret_gt5': 0, 'ret_gt10': 0,
    'stocks': set()
})

z_total = 0
for fname in files_z[:500]:
    fp = os.path.join(datadir_z, fname)
    code = fname.replace('谕组周_', '').replace('.csv', '')
    try:
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                wxab = str(row.get('WXAB', '')).strip()
                zc_raw = str(row.get('ZC周', '')).strip()
                ret_raw = str(row.get('周涨', '')).strip()

                if not wxab or not zc_raw:
                    continue

                # 解析护型 - 周线也使用护段代码（a=甲, b=乙, c=丙, r=己, y=戊, z=丁）
                first_char = wxab[0] if wxab else ''
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

                zc_sign = 'pos' if zc > 0 else ('neg' if zc < 0 else 'zero')

                key = (zc_sign, hu)
                z_groups[key]['count'] += 1
                z_groups[key]['sum_ret'] += ret
                z_groups[key]['stocks'].add(code)
                if ret > 0: z_groups[key]['win_ret'] += 1
                if ret > 1: z_groups[key]['ret_gt1'] += 1
                if ret > 3: z_groups[key]['ret_gt3'] += 1
                if ret > 5: z_groups[key]['ret_gt5'] += 1
                if ret > 10: z_groups[key]['ret_gt10'] += 1
                z_total += 1
    except Exception as e:
        pass

print(f'总样本数: {z_total:,}')
print()

for zc_sign, zc_label in [('pos', 'WXZC>0'), ('neg', 'WXZC<0'), ('zero', 'WXZC=0')]:
    print(f'\n{"─" * 60}')
    print(f'【{zc_label}】')
    print(f'{"护型":>4} {"样本":>8} {"周涨%":>8} {"涨率%":>8} {"周涨>1%":>8} {"周涨>3%":>8} {"周涨>5%":>8} {"周涨>10%":>8}')
    print(f'{"─" * 60}')
    for hu in HU_ORDER:
        key = (zc_sign, hu)
        g = z_groups[key]
        if g['count'] == 0:
            continue
        avg_ret = g['sum_ret'] / g['count']
        wr = g['win_ret'] / g['count'] * 100
        gt1 = g['ret_gt1'] / g['count'] * 100
        gt3 = g['ret_gt3'] / g['count'] * 100
        gt5 = g['ret_gt5'] / g['count'] * 100
        gt10 = g['ret_gt10'] / g['count'] * 100
        print(f'{hu:>4} {g["count"]:>8,} {avg_ret:>8.2f} {wr:>8.1f} {gt1:>8.1f} {gt3:>8.1f} {gt5:>8.1f} {gt10:>8.1f}')

print('\n▎周线关键假设验证：')
print(f'{"护型":>4} {"WXZC>0涨率":>12} {"WXZC>0均涨":>12} {"WXZC<0涨率":>12} {"WXZC<0均涨":>12} {"差异":>8}')
for hu in HU_ORDER:
    pg = z_groups[('pos', hu)]
    ng = z_groups[('neg', hu)]
    p_ret = pg['sum_ret'] / pg['count'] if pg['count'] else 0
    n_ret = ng['sum_ret'] / ng['count'] if ng['count'] else 0
    p_wr = pg['win_ret'] / pg['count'] * 100 if pg['count'] else 0
    n_wr = ng['win_ret'] / ng['count'] * 100 if ng['count'] else 0
    diff = p_ret - n_ret
    print(f'{hu:>4} {p_wr:>12.1f} {p_ret:>12.2f} {n_wr:>12.1f} {n_ret:>12.2f} {diff:>+8.2f}')

# ============================================================
# 3. 综合结论
# ============================================================
print('\n\n' + '=' * 80)
print('【综合结论】')
print('=' * 80)

# 全量验证
print('\n正在全量验证...')
files_all = sorted(os.listdir(r'昭明算展\谕组日'))
total_stocks = len(files_all)
print(f'日线: {total_stocks} 只股票')

# 全量日线 - 使用更大的样本
all_groups = defaultdict(lambda: {
    'count': 0, 'sum_ret': 0.0, 'sum_next_high': 0.0,
    'win_ret': 0, 'win_next_high': 0,
    'sum_ret_sq': 0.0,  # 平方和，用于标准差
})

all_total = 0
for fname in files_all:
    fp = os.path.join(r'昭明算展\谕组日', fname)
    try:
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dxab_raw = str(row.get('DXAB', '')).strip()
                zc_raw = str(row.get('日ZC', '')).strip()
                ret_raw = str(row.get('涨幅', '')).strip()
                next_high_raw = str(row.get('次日高幅', '')).strip()

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
                    next_high = float(next_high_raw)
                except ValueError:
                    next_high = None

                zc_sign = 'pos' if zc > 0 else ('neg' if zc < 0 else 'zero')
                key = (zc_sign, hu)
                all_groups[key]['count'] += 1
                all_groups[key]['sum_ret'] += ret
                all_groups[key]['sum_ret_sq'] += ret * ret
                if ret > 0: all_groups[key]['win_ret'] += 1
                if next_high is not None:
                    all_groups[key]['sum_next_high'] += next_high
                    if next_high > 0: all_groups[key]['win_next_high'] += 1
                all_total += 1
    except:
        pass

print(f'总样本: {all_total:,}')
print()

# 输出全量结论
for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    print(f'\n【{zc_label} 全量】')
    print(f'{"护型":>4} {"样本":>10} {"均涨幅":>8} {"涨幅σ":>8} {"涨率":>8} {"均次高":>8} {"次高率":>8} {"夏普":>8}')
    for hu in HU_ORDER:
        key = (zc_sign, hu)
        g = all_groups[key]
        if g['count'] == 0:
            continue
        n = g['count']
        avg_ret = g['sum_ret'] / n
        avg_nh = g['sum_next_high'] / n
        win_rate = g['win_ret'] / n * 100
        nh_rate = g['win_next_high'] / n * 100
        # 标准差
        variance = (g['sum_ret_sq'] / n) - (avg_ret * avg_ret)
        std = (variance ** 0.5) if variance > 0 else 0
        sharpe = avg_ret / std * 100 if std > 0 else 0  # 日夏普(×100)
        print(f'{hu:>4} {n:>10,} {avg_ret:>8.2f} {std:>8.2f} {win_rate:>8.1f} {avg_nh:>8.2f} {nh_rate:>8.1f} {sharpe:>8.2f}')

# 模型总结
print('\n' + '=' * 80)
print('模型验证结论')
print('=' * 80)

# 对每个ZC条件，对各护型按均涨幅排序
print('\n【DXZC>0 护型排序 (按均涨幅)】')
pos_sorted = sorted([(hu, all_groups[('pos', hu)]) for hu in HU_ORDER if all_groups[('pos', hu)]['count'] > 0],
                    key=lambda x: x[1]['sum_ret']/x[1]['count'], reverse=True)
for i, (hu, g) in enumerate(pos_sorted):
    avg_ret = g['sum_ret'] / g['count']
    wr = g['win_ret'] / g['count'] * 100
    print(f'  {i+1}. {hu}: 均涨={avg_ret:.2f}% 涨率={wr:.1f}% 样本={g["count"]:,}')

print('\n【DXZC<0 护型排序 (按均涨幅)】')
neg_sorted = sorted([(hu, all_groups[('neg', hu)]) for hu in HU_ORDER if all_groups[('neg', hu)]['count'] > 0],
                    key=lambda x: x[1]['sum_ret']/x[1]['count'], reverse=True)
for i, (hu, g) in enumerate(neg_sorted):
    avg_ret = g['sum_ret'] / g['count']
    wr = g['win_ret'] / g['count'] * 100
    print(f'  {i+1}. {hu}: 均涨={avg_ret:.2f}% 涨率={wr:.1f}% 样本={g["count"]:,}')