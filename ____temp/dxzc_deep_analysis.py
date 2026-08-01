# -*- coding: utf-8 -*-
"""
DXZC+DXAB 多维度深度分析
维度1: DXZC数值分级
维度2: DXAB×DXCD联动
维度3: 次日冲高分析
维度4: DXZC拐点分析
维度5: DXAB变化序列
"""
import csv, os, sys, io, json
from collections import defaultdict, Counter
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HU_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}
HU_ORDER = ['甲', '乙', '丙', '丁', '戊', '己']

datadir = r'昭明算展\谕组日'
files = sorted(os.listdir(datadir))

# ============================================================
# 维度1: DXZC数值分级
# ============================================================
print('=' * 80)
print('维度1: DXZC数值分级 — 护型效果随ZC值的变化')
print('=' * 80)

# ZC区间定义
ZC_BINS = [
    (-999, -10, 'ZC≤-10'),
    (-10, -5, '-10<ZC≤-5'),
    (-5, -2, '-5<ZC≤-2'),
    (-2, -1, '-2<ZC≤-1'),
    (-1, 0, '-1<ZC<0'),
    (0, 1, '0<ZC<1'),
    (1, 2, '1≤ZC<2'),
    (2, 5, '2≤ZC<5'),
    (5, 10, '5≤ZC<10'),
    (10, 999, 'ZC≥10'),
]

zc_groups = defaultdict(lambda: defaultdict(lambda: {
    'count': 0, 'sum_ret': 0.0, 'win_ret': 0,
    'sum_next_high': 0.0, 'win_next_high': 0
}))

total = 0
for fname in files[:500]:
    fp = os.path.join(datadir, fname)
    try:
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dxab_raw = str(row.get('DXAB', '')).strip()
                zc_raw = str(row.get('日ZC', '')).strip()
                ret_raw = str(row.get('涨幅', '')).strip()
                nh_raw = str(row.get('次日高幅', '')).strip()

                if not dxab_raw or not zc_raw: continue
                first_char = dxab_raw[0] if dxab_raw else ''
                hu = HU_MAP.get(first_char, '')
                if not hu: continue
                try: zc = float(zc_raw)
                except: continue
                try: ret = float(ret_raw)
                except: ret = 0.0
                try: nh = float(nh_raw)
                except: nh = None

                # 找ZC区间
                for lo, hi, label in ZC_BINS:
                    if lo < zc <= hi:
                        zc_groups[label][hu]['count'] += 1
                        zc_groups[label][hu]['sum_ret'] += ret
                        if ret > 0: zc_groups[label][hu]['win_ret'] += 1
                        if nh is not None:
                            zc_groups[label][hu]['sum_next_high'] += nh
                            if nh > 0: zc_groups[label][hu]['win_next_high'] += 1
                        break
                total += 1
    except:
        pass

print(f'总样本: {total:,}')
print()

# 输出各ZC区间的护型表现
for label in [z[2] for z in ZC_BINS]:
    print(f'\n【{label}】')
    print(f'{"护型":>4} {"样本":>8} {"均涨幅":>8} {"涨率%":>8} {"均次日高":>8} {"次高率%":>8}')
    # 按均涨幅排序
    items = [(hu, zc_groups[label][hu]) for hu in HU_ORDER if zc_groups[label][hu]['count'] > 0]
    items.sort(key=lambda x: x[1]['sum_ret']/x[1]['count'], reverse=True)
    for hu, g in items:
        avg_ret = g['sum_ret'] / g['count']
        wr = g['win_ret'] / g['count'] * 100
        avg_nh = g['sum_next_high'] / g['count'] if g['count'] else 0
        nh_rate = g['win_next_high'] / g['count'] * 100 if g['count'] else 0
        print(f'{hu:>4} {g["count"]:>8,} {avg_ret:>8.2f} {wr:>8.1f} {avg_nh:>8.2f} {nh_rate:>8.1f}')

# ============================================================
# 维度2: DXAB×DXCD 联动
# ============================================================
print('\n\n' + '=' * 80)
print('维度2: DXAB×DXCD 联动 — 护型与护级二维组合')
print('=' * 80)

# DXCD护级映射: 从DXCD列的第一个字符
CD_MAP = {'上': '上', '中': '中', '下': '下', '忐': '忐', '忠': '忠', '忑': '忑'}
# 实际上DXCD列是类似"上"或"上(金升)"这样的格式

cd_groups = defaultdict(lambda: {'count': 0, 'sum_ret': 0.0, 'win_ret': 0})

cd_total = 0
for fname in files[:500]:
    fp = os.path.join(datadir, fname)
    try:
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dxab_raw = str(row.get('DXAB', '')).strip()
                dxcd_raw = str(row.get('DXCD', '')).strip()
                zc_raw = str(row.get('日ZC', '')).strip()
                ret_raw = str(row.get('涨幅', '')).strip()

                if not dxab_raw or not dxcd_raw or not zc_raw: continue
                first_char = dxab_raw[0] if dxab_raw else ''
                hu = HU_MAP.get(first_char, '')
                if not hu: continue
                # DXCD取第一个字符（上中下忐忠忑）
                cd = dxcd_raw[0] if dxcd_raw else ''
                if cd not in CD_MAP: continue
                try: zc = float(zc_raw)
                except: continue
                try: ret = float(ret_raw)
                except: ret = 0.0

                zc_sign = 'pos' if zc > 0 else ('neg' if zc < 0 else 'zero')
                key = (zc_sign, hu, cd)
                cd_groups[key]['count'] += 1
                cd_groups[key]['sum_ret'] += ret
                if ret > 0: cd_groups[key]['win_ret'] += 1
                cd_total += 1
    except:
        pass

print(f'总样本: {cd_total:,}')
print()

for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    print(f'\n【{zc_label}】')
    print(f'{"护型":>4} ', end='')
    for cd in ['上', '忐', '中', '忠', '下', '忑']:
        print(f'  {cd}均涨   {cd}涨率  ', end='')
    print()
    for hu in HU_ORDER:
        print(f'{hu:>4} ', end='')
        for cd in ['上', '忐', '中', '忠', '下', '忑']:
            key = (zc_sign, hu, cd)
            g = cd_groups[key]
            if g['count'] > 0:
                avg_ret = g['sum_ret'] / g['count']
                wr = g['win_ret'] / g['count'] * 100
                print(f'{avg_ret:>6.2f} {wr:>6.1f}% ', end='')
            else:
                print(f'   N/A    N/A ', end='')
        print()

# ============================================================
# 维度3: 次日冲高分析
# ============================================================
print('\n\n' + '=' * 80)
print('维度3: 次日冲高分析 — 各护型在不同ZC条件下的次日表现')
print('=' * 80)

nh_groups = defaultdict(lambda: {'count': 0, 'sum_nh': 0.0, 'nh_gt0': 0, 'nh_gt1': 0, 'nh_gt2': 0, 'nh_gt3': 0, 'nh_gt5': 0})

nh_total = 0
for fname in files[:500]:
    fp = os.path.join(datadir, fname)
    try:
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                dxab_raw = str(row.get('DXAB', '')).strip()
                zc_raw = str(row.get('日ZC', '')).strip()
                ret_raw = str(row.get('涨幅', '')).strip()
                nh_raw = str(row.get('次日高幅', '')).strip()

                if not dxab_raw or not zc_raw or not nh_raw: continue
                first_char = dxab_raw[0] if dxab_raw else ''
                hu = HU_MAP.get(first_char, '')
                if not hu: continue
                try: zc = float(zc_raw)
                except: continue
                try: ret = float(ret_raw)
                except: ret = 0.0
                try: nh = float(nh_raw)
                except: continue

                zc_sign = 'pos' if zc > 0 else ('neg' if zc < 0 else 'zero')
                key = (zc_sign, hu)
                nh_groups[key]['count'] += 1
                nh_groups[key]['sum_nh'] += nh
                if nh > 0: nh_groups[key]['nh_gt0'] += 1
                if nh > 1: nh_groups[key]['nh_gt1'] += 1
                if nh > 2: nh_groups[key]['nh_gt2'] += 1
                if nh > 3: nh_groups[key]['nh_gt3'] += 1
                if nh > 5: nh_groups[key]['nh_gt5'] += 1
                nh_total += 1
    except:
        pass

for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    print(f'\n【{zc_label} 次日冲高】')
    print(f'{"护型":>4} {"样本":>8} {"均次高":>8} {"次高>0%":>8} {"次高>1%":>8} {"次高>2%":>8} {"次高>3%":>8} {"次高>5%":>8} {"均今涨":>8}')
    for hu in HU_ORDER:
        key = (zc_sign, hu)
        g = nh_groups[key]
        if g['count'] == 0: continue
        avg_nh = g['sum_nh'] / g['count']
        r0 = g['nh_gt0'] / g['count'] * 100
        r1 = g['nh_gt1'] / g['count'] * 100
        r2 = g['nh_gt2'] / g['count'] * 100
        r3 = g['nh_gt3'] / g['count'] * 100
        r5 = g['nh_gt5'] / g['count'] * 100
        print(f'{hu:>4} {g["count"]:>8,} {avg_nh:>8.2f} {r0:>8.1f} {r1:>8.1f} {r2:>8.1f} {r3:>8.1f} {r5:>8.1f} {"-":>8}')

# ============================================================
# 维度4: DXZC拐点分析
# ============================================================
print('\n\n' + '=' * 80)
print('维度4: DXZC拐点 — ZC从正转负/从负转正时的护型变化')
print('=' * 80)

# 需要读取时间序列，按股票逐行分析
# 拐点分析：前一日ZC>0且当日ZC≤0（正转负），或反之

turn_groups = defaultdict(lambda: {'count': 0, 'sum_ret': 0.0, 'win_ret': 0, 'sum_nh': 0.0, 'nh_gt0': 0})

turn_total = 0
for fname in files[:500]:
    fp = os.path.join(datadir, fname)
    try:
        rows = []
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        # 逐行分析，需要前一行数据
        for i in range(1, len(rows)):
            curr = rows[i]
            prev = rows[i-1]
            dxab_raw = str(curr.get('DXAB', '')).strip()
            zc_curr_raw = str(curr.get('日ZC', '')).strip()
            zc_prev_raw = str(prev.get('日ZC', '')).strip()
            ret_raw = str(curr.get('涨幅', '')).strip()
            nh_raw = str(curr.get('次日高幅', '')).strip()

            if not dxab_raw or not zc_curr_raw or not zc_prev_raw: continue
            first_char = dxab_raw[0] if dxab_raw else ''
            hu = HU_MAP.get(first_char, '')
            if not hu: continue
            try: zc_curr = float(zc_curr_raw)
            except: continue
            try: zc_prev = float(zc_prev_raw)
            except: continue
            try: ret = float(ret_raw)
            except: ret = 0.0
            try: nh = float(nh_raw)
            except: nh = None

            # 判断拐点
            if zc_prev > 0 and zc_curr <= 0:
                turn_type = '正转负'
            elif zc_prev <= 0 and zc_curr > 0:
                turn_type = '负转正'
            else:
                continue

            key = (turn_type, hu)
            turn_groups[key]['count'] += 1
            turn_groups[key]['sum_ret'] += ret
            if ret > 0: turn_groups[key]['win_ret'] += 1
            if nh is not None:
                turn_groups[key]['sum_nh'] += nh
                if nh > 0: turn_groups[key]['nh_gt0'] += 1
            turn_total += 1
    except:
        pass

print(f'总拐点样本: {turn_total:,}')
print()

for turn_type in ['正转负', '负转正']:
    print(f'\n【{turn_type} 时各护型表现】')
    print(f'{"护型":>4} {"样本":>8} {"均涨幅":>8} {"涨率%":>8} {"均次高":>8} {"次高率%":>8}')
    items = [(hu, turn_groups[(turn_type, hu)]) for hu in HU_ORDER if turn_groups[(turn_type, hu)]['count'] > 0]
    items.sort(key=lambda x: x[1]['sum_ret']/x[1]['count'], reverse=True)
    for hu, g in items:
        avg_ret = g['sum_ret'] / g['count']
        wr = g['win_ret'] / g['count'] * 100
        avg_nh = g['sum_nh'] / g['count'] if g['count'] else 0
        nh_rate = g['nh_gt0'] / g['count'] * 100 if g['count'] else 0
        print(f'{hu:>4} {g["count"]:>8,} {avg_ret:>8.2f} {wr:>8.1f} {avg_nh:>8.2f} {nh_rate:>8.1f}')

# ============================================================
# 维度5: DXAB变化序列 — 护型变化路径
# ============================================================
print('\n\n' + '=' * 80)
print('维度5: DXAB变化序列 — 护型变化的预测能力')
print('=' * 80)

# 分析：今日护型 → 明日护型的转移概率，以及今日护型+ZC → 明日涨幅
trans_groups = defaultdict(lambda: {'count': 0, 'sum_next_ret': 0.0, 'next_win': 0})

seq_total = 0
for fname in files[:500]:
    fp = os.path.join(datadir, fname)
    try:
        rows = []
        with open(fp, 'r', encoding='gbk') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)
        for i in range(len(rows) - 1):
            curr = rows[i]
            nxt = rows[i+1]
            dxab_curr = str(curr.get('DXAB', '')).strip()
            dxab_next = str(nxt.get('DXAB', '')).strip()
            zc_raw = str(curr.get('日ZC', '')).strip()
            ret_next = str(nxt.get('涨幅', '')).strip()

            if not dxab_curr or not dxab_next or not zc_raw: continue
            curr_hu = HU_MAP.get(dxab_curr[0] if dxab_curr else '', '')
            next_hu = HU_MAP.get(dxab_next[0] if dxab_next else '', '')
            if not curr_hu or not next_hu: continue
            try: zc = float(zc_raw)
            except: continue
            try: ret_next = float(ret_next)
            except: ret_next = 0.0

            zc_sign = 'pos' if zc > 0 else ('neg' if zc < 0 else 'zero')
            key = (zc_sign, curr_hu, next_hu)
            trans_groups[key]['count'] += 1
            trans_groups[key]['sum_next_ret'] += ret_next
            if ret_next > 0: trans_groups[key]['next_win'] += 1
            seq_total += 1
    except:
        pass

print(f'总序列样本: {seq_total:,}')
print()

# 转移矩阵：今日护型 → 明日护型
for zc_sign, zc_label in [('pos', 'DXZC>0'), ('neg', 'DXZC<0')]:
    print(f'\n【{zc_label} 护型转移矩阵】')
    print(f'{"今日->明日":>8}', end='')
    for hu_to in HU_ORDER:
        print(f'{hu_to:>8}', end='')
    print()
    for hu_from in HU_ORDER:
        # 统计该行总样本
        row_total = sum(trans_groups[(zc_sign, hu_from, hu_to)]['count'] for hu_to in HU_ORDER)
        if row_total == 0: continue
        print(f'{hu_from:>8}', end='')
        for hu_to in HU_ORDER:
            g = trans_groups[(zc_sign, hu_from, hu_to)]
            pct = g['count'] / row_total * 100 if row_total else 0
            print(f'{pct:>7.1f}%', end='')
        print()

# 转移后的收益
print(f'\n转移后次日涨幅:')
print(f'{"今日->明日":>8}', end='')
for hu_to in HU_ORDER:
    print(f'{hu_to:>8}', end='')
print()
for hu_from in HU_ORDER:
    print(f'{hu_from:>8}', end='')
    for hu_to in HU_ORDER:
        g = trans_groups[(zc_sign, hu_from, hu_to)]
        if g['count']:
            avg_ret = g['sum_next_ret'] / g['count']
            print(f'{avg_ret:>8.2f}', end='')
        else:
            print(f'    -  ', end='')
    print()

# 核心：今日护型→明日涨幅（不依赖明日护型）
print(f'\n【今日护型 → 明日涨幅（不依赖明日护型变化）】')
print(f'{"护型":>4} {"ZC>0样本":>8} {"ZC>0均明涨":>8} {"ZC>0明涨率":>8} {"ZC<0样本":>8} {"ZC<0均明涨":>8} {"ZC<0明涨率":>8}')
for hu in HU_ORDER:
    pg = trans_groups[('pos', hu, '')]  # placeholder, sum across all next_hu
    ng = trans_groups[('neg', hu, '')]
    # 实际需要求和
    p_total = sum(trans_groups[('pos', hu, to)]['count'] for to in HU_ORDER)
    p_sum = sum(trans_groups[('pos', hu, to)]['sum_next_ret'] for to in HU_ORDER)
    p_win = sum(trans_groups[('pos', hu, to)]['next_win'] for to in HU_ORDER)
    n_total = sum(trans_groups[('neg', hu, to)]['count'] for to in HU_ORDER)
    n_sum = sum(trans_groups[('neg', hu, to)]['sum_next_ret'] for to in HU_ORDER)
    n_win = sum(trans_groups[('neg', hu, to)]['next_win'] for to in HU_ORDER)
    if p_total:
        print(f'{hu:>4} {p_total:>8,} {p_sum/p_total:>8.2f} {p_win/p_total*100:>8.1f} {n_total:>8,} {n_sum/n_total:>8.2f} {n_win/n_total*100:>8.1f}')