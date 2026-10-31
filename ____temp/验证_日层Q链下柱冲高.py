# -*- coding: utf-8 -*-
"""
验证：日级别 Q链①/②/③/④ 是否存在下柱冲高机会；日层大局/日层Q链对日级别是否适用。
方法：用谕组日CSV现有列重建日层大局(A/H/P/Z)与日层Q链(①/②/③/④)，统计下柱冲高率(次日高幅>=3%)。
重建逻辑严格复现 神谕.bas 2558-2630 行。
"""
import os
import glob
import csv
import sys
from collections import defaultdict

# 列索引（0-based，来自元数据_vba数据映射_日类.md）
COL_日期 = 0
COL_波型 = 11      # 日层波型
COL_日ZC = 14      # 日类BTZC
COL_次日高幅 = 26  # 次日高幅
COL_层界 = 28      # 日层界
COL_并符串 = 34    # 日类并符串
COL_DXAB = 9       # 日层护型（第4字符=护级AB）

# 并符编码
Q = 'Q'  # 升连
O = 'O'  # 升吞
o = 'o'  # 升孕
W = 'W'  # 跌连
V = 'V'  # 跌吞
v = 'v'  # 跌孕

def 提取护级AB(dxab):
    """DXAB格式: 护型字母+甲乙丙丁戊己+方向+护级+数字+后缀，护级在第4字符"""
    if len(dxab) >= 4:
        return dxab[3]
    return ''

def 提取值日四波(波型):
    """含'虎'取第5字符，否则取第3字符"""
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def 算日层大局(日ZC, 日AB护级, 值日四波, 层界):
    """复现神谕.bas 2561-2606"""
    if 日ZC < 0 and 日AB护级 in ('下', '忑'):
        return 'Z退z禁'
    elif 日ZC < 0:
        if 日AB护级 in ('中', '下', '忑'):
            return 'P备A2储'
        elif 日AB护级 in ('忠', '上', '忐'):
            if 值日四波 == '龙':
                return 'P备A1储'
            elif 值日四波 == '武':
                return 'P备B3储'
            else:
                return 'Z退x弃'
    else:
        if 日AB护级 == '忠':
            return 'P备B2再'
        elif 日AB护级 in ('上', '忐'):
            if 值日四波 == '武':
                return 'P备B1初'
            elif 层界 and 层界[0] == '初':
                return 'A入A初'
            elif 层界 and 层界[0] == '再':
                return 'A入B再'
            else:
                return 'H持G主'
        elif 日AB护级 in ('中', '下', '忑'):
            if 值日四波 == '龙':
                return 'H持e根'
            elif 值日四波 == '雀':
                return 'H持v破'
            else:
                return 'Z退y虎'
    return ''

def 算日层Q链(大局, 并符串):
    """复现神谕.bas 2612-2630"""
    if not 大局:
        return '_'
    首 = 大局[0]
    if 首 not in ('A', 'H', 'P'):
        return '_'
    if not 并符串:
        return '_'
    # ③: 右3位 = QvO/Qvo/QVO/QVo
    if 并符串[-3:] in ('QvO', 'Qvo', 'QVO', 'QVo'):
        return 首 + '③'
    # ①: 右1位 = Q
    if 并符串[-1:] == 'Q':
        return 首 + '①'
    # ②: 右2位 = Qv/QV
    if 并符串[-2:] in ('Qv', 'QV'):
        return 首 + '②'
    # ④: 右3位 = QvW/QVW
    if 并符串[-3:] in ('QvW', 'QVW'):
        return 首 + '④'
    return '_'

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 统计: Q链 -> (总样本, 冲高样本)
    q_stats = defaultdict(lambda: [0, 0])
    # 按 大局首字符 x Q链 分组
    q_by_首 = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    # 大局首字符分布
    首_stats = defaultdict(lambda: [0, 0])
    # 四波分布
    四波_stats = defaultdict(int)
    # 无Q链(_)统计
    noq_stats = [0, 0]
    # 整体基准
    all_stats = [0, 0]
    # 按Q链数字(①/②/③/④)汇总，不分大局首字符
    qnum_stats = defaultdict(lambda: [0, 0])

    n_rows = 0
    for fi, f in enumerate(files):
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            for row in reader:
                if len(row) <= COL_次日高幅:
                    continue
                n_rows += 1
                try:
                    次日高幅 = float(row[COL_次日高幅])
                except (ValueError, IndexError):
                    continue
                try:
                    日ZC = int(row[COL_日ZC])
                except (ValueError, IndexError):
                    continue
                波型 = row[COL_波型]
                层界 = row[COL_层界]
                并符串 = row[COL_并符串]
                dxab = row[COL_DXAB]
                日AB护级 = 提取护级AB(dxab)
                值日四波 = 提取值日四波(波型)
                四波_stats[值日四波] += 1

                # 整体基准
                all_stats[0] += 1
                if 次日高幅 >= 3:
                    all_stats[1] += 1

                大局 = 算日层大局(日ZC, 日AB护级, 值日四波, 层界)
                首 = 大局[0] if 大局 else ''
                首_stats[首][0] += 1
                if 次日高幅 >= 3:
                    首_stats[首][1] += 1

                q链 = 算日层Q链(大局, 并符串)
                if q链 != '_':
                    q_stats[q链][0] += 1
                    if 次日高幅 >= 3:
                        q_stats[q链][1] += 1
                    q_by_首[首][q链][0] += 1
                    if 次日高幅 >= 3:
                        q_by_首[首][q链][1] += 1
                    # 按Q链数字汇总
                    qnum = q链[1:]
                    qnum_stats[qnum][0] += 1
                    if 次日高幅 >= 3:
                        qnum_stats[qnum][1] += 1
                else:
                    noq_stats[0] += 1
                    if 次日高幅 >= 3:
                        noq_stats[1] += 1

    print(f'总行数: {n_rows}')
    print()
    tot, hit = all_stats
    print(f'=== 整体基准: {tot} 行, 下柱冲高率 {hit/tot*100:.2f}% ===')
    print()
    print('=== 无Q链(_) ===')
    tot, hit = noq_stats
    print(f'  _: {tot} 行, 冲高率 {hit/tot*100:.2f}%')
    print()
    print('=== 按Q链数字汇总（不分大局首字符） ===')
    for q in sorted(qnum_stats):
        tot, hit = qnum_stats[q]
        if tot:
            print(f'  {q}: {tot} 行, 冲高率 {hit/tot*100:.2f}%')
    print()
    print('=== 日层大局首字符分布 ===')
    for 首 in sorted(首_stats):
        tot, hit = 首_stats[首]
        if tot:
            print(f'  {首}: {tot} 行, 下柱冲高率 {hit/tot*100:.2f}%')

    print()
    print('=== 日层Q链 下柱冲高率（次日高幅>=3%） ===')
    print(f'{"Q链":<6}{"样本":>10}{"冲高":>8}{"冲高率":>10}')
    for q in sorted(q_stats):
        tot, hit = q_stats[q]
        if tot:
            print(f'{q:<6}{tot:>10}{hit:>8}{hit/tot*100:>9.2f}%')

    print()
    print('=== 按 大局首字符 x Q链 下柱冲高率 ===')
    for 首 in sorted(q_by_首):
        for q in sorted(q_by_首[首]):
            tot, hit = q_by_首[首][q]
            if tot:
                print(f'  {首} {q}: {tot} 行, 冲高率 {hit/tot*100:.2f}%')

    print()
    print('=== 值日四波分布 ===')
    for w in sorted(四波_stats):
        print(f'  {w}: {四波_stats[w]}')

if __name__ == '__main__':
    main()