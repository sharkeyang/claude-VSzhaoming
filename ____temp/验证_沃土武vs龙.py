# -*- coding: utf-8 -*-
"""
验证：沃土+武 到底是"备选勿介入"还是"最强介入"？
周层大局把 沃土+武 → P备B1初（备选），但四波四土说 沃×武=84.04%最强。
用谕组周 CSV 重建周层土型+四波，统计 沃土+武 的下周冲高率(下周HR>=3%)，对比 沃土+龙。
"""
import os
import glob
import csv
from collections import defaultdict

COL_HR = 3
COL_护型 = 4
COL_波型 = 7
COL_ZC周 = 18

def 提取护级AB(护型):
    if len(护型) >= 4:
        return 护型[3]
    return ''

def 提取值周四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def 算周层土型(zc, 护级):
    """复现神谕.bas 2405-2416"""
    if zc < 0 and 护级 in ('下', '忑'):
        return '禁'
    elif 护级 in ('中', '下', '忑'):
        return '念'
    elif zc > 0 and 护级 in ('上', '忐'):
        return '沃'
    else:
        return '肋'

def main():
    data_dir = r'昭明算展\谕组周'
    files = glob.glob(os.path.join(data_dir, '谕组周_*.csv'))
    print(f'文件数: {len(files)}')

    # 统计: (土型, 四波) -> [总样本, 冲高样本]
    stats = defaultdict(lambda: [0, 0])
    # 沃土+武 的细分
    wu_stats = defaultdict(lambda: [0, 0])  # 按层界细分
    # 沃土+龙 对比
    long_stats = defaultdict(lambda: [0, 0])

    n_rows = 0
    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_ZC周:
                    rows.append(row)
        for i, row in enumerate(rows):
            try:
                hr = float(row[COL_HR])
            except (ValueError, IndexError):
                continue
            if i + 1 < len(rows):
                try:
                    next_hr = float(rows[i+1][COL_HR])
                except (ValueError, IndexError):
                    continue
            else:
                continue
            try:
                zc = int(row[COL_ZC周])
            except (ValueError, IndexError):
                continue
            n_rows += 1
            护级 = 提取护级AB(row[COL_护型])
            四波 = 提取值周四波(row[COL_波型])
            土型 = 算周层土型(zc, 护级)
            key = (土型, 四波)
            stats[key][0] += 1
            if next_hr >= 3:
                stats[key][1] += 1
            if 土型 == '沃' and 四波 == '武':
                wu_stats[0][0] += 1
                if next_hr >= 3:
                    wu_stats[0][1] += 1
            if 土型 == '沃' and 四波 == '龙':
                long_stats[0][0] += 1
                if next_hr >= 3:
                    long_stats[0][1] += 1

    print(f'总行数: {n_rows}')
    print()
    print('=== 沃土 × 四波 下周冲高率(下周HR>=3%) ===')
    for 土 in ('沃', '念', '肋', '禁'):
        for 波 in ('龙', '武', '虎', '雀'):
            key = (土, 波)
            if key in stats:
                tot, hit = stats[key]
                if tot:
                    print(f'  {土}土×{波}: {tot} 行, 冲高率 {hit/tot*100:.2f}%')
    print()
    print('=== 沃土+武 vs 沃土+龙 对比 ===')
    tot, hit = wu_stats[0]
    print(f'  沃土+武: {tot} 行, 冲高率 {hit/tot*100:.2f}%')
    tot, hit = long_stats[0]
    print(f'  沃土+龙: {tot} 行, 冲高率 {hit/tot*100:.2f}%')

if __name__ == '__main__':
    main()