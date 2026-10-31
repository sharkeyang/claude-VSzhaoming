# -*- coding: utf-8 -*-
"""
验证：周A趋持有范围内（周ZC>0 且 周四波非虎），日线下破各级别均线（DJA/DJB/DJC/DJD/DJE）的情况。
统计：①下破频率 ②下破后次日/5日收益 ③下破后是否回升。
"""
import os
import glob
import csv
from collections import defaultdict

COL_日期 = 0
COL_收 = 1
COL_日ZA = 13
COL_日ZC = 14
COL_日ZE = 15
COL_DTZB = 66
COL_DTZD = 67
COL_周波型 = 76
COL_周ZC = 87

def 提取四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 统计: 均线 -> [持有范围内总日数, 下破次数]
    下破统计 = defaultdict(lambda: [0, 0])
    # 下破后次日/5日收益
    下破收益 = defaultdict(lambda: defaultdict(list))  # 均线 -> 口径 -> [收益列表]
    # 下破后是否回升（5日内重上）
    回升统计 = defaultdict(lambda: [0, 0])  # 均线 -> [下破次数, 5日回升次数]

    n_rows = 0
    n_hold_rows = 0

    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_周ZC:
                    rows.append(row)
        if not rows:
            continue

        for i, row in enumerate(rows):
            try:
                周ZC = int(row[COL_周ZC])
                收 = float(row[COL_收])
            except (ValueError, IndexError):
                continue
            n_rows += 1
            四波 = 提取四波(row[COL_周波型])
            持有 = (周ZC > 0) and (四波 != '虎')
            if not 持有:
                continue
            n_hold_rows += 1

            # 各级别均线 BT 变量
            均线BT = {
                'DJA': row[COL_日ZA],
                'DJB': row[COL_DTZB],
                'DJC': row[COL_日ZC],
                'DJD': row[COL_DTZD],
                'DJE': row[COL_日ZE],
            }
            for 名, bt in 均线BT.items():
                try:
                    bt_val = int(bt)
                except (ValueError, IndexError):
                    continue
                下破统计[名][0] += 1
                # 下破 = 前一日>0 且 当日<0
                if i > 0:
                    try:
                        前bt = int(rows[i-1][{ 'DJA': COL_日ZA, 'DJB': COL_DTZB, 'DJC': COL_日ZC, 'DJD': COL_DTZD, 'DJE': COL_日ZE }[名]])
                    except (ValueError, IndexError):
                        前bt = None
                    if 前bt is not None and 前bt > 0 and bt_val < 0:
                        下破统计[名][1] += 1
                        # 次日收益
                        if i + 1 < len(rows):
                            try:
                                次日收 = float(rows[i+1][COL_收])
                                下破收益[名]['次日'].append((次日收 - 收) / 收 * 100)
                            except (ValueError, IndexError):
                                pass
                        # 5日收益
                        if i + 5 < len(rows):
                            try:
                                五日收 = float(rows[i+5][COL_收])
                                下破收益[名]['5日'].append((五日收 - 收) / 收 * 100)
                            except (ValueError, IndexError):
                                pass
                        # 5日回升（5日内任一日重上）
                        回升 = False
                        for j in range(i+1, min(i+6, len(rows))):
                            try:
                                if int(rows[j][{ 'DJA': COL_日ZA, 'DJB': COL_DTZB, 'DJC': COL_日ZC, 'DJD': COL_DTZD, 'DJE': COL_日ZE }[名]]) > 0:
                                    回升 = True
                                    break
                            except (ValueError, IndexError):
                                pass
                        回升统计[名][0] += 1
                        if 回升:
                            回升统计[名][1] += 1

    print(f'总日数: {n_rows}, 周A趋持有范围内日数: {n_hold_rows} ({n_hold_rows/n_rows*100:.1f}%)')
    print()
    print('=== 周A趋持有范围内，日线下破各级别均线 ===')
    print(f'{"均线":<6}{"持有日数":>10}{"下破次数":>10}{"下破频率":>10}{"次日均收益":>12}{"5日均收益":>12}{"5日回升率":>10}')
    for 名 in ('DJA', 'DJB', 'DJC', 'DJD', 'DJE'):
        tot, 破 = 下破统计[名]
        if tot == 0:
            continue
        频率 = 破/tot*100
        次日 = sum(下破收益[名]['次日'])/len(下破收益[名]['次日']) if 下破收益[名]['次日'] else 0
        五日 = sum(下破收益[名]['5日'])/len(下破收益[名]['5日']) if 下破收益[名]['5日'] else 0
        回升率 = 回升统计[名][1]/回升统计[名][0]*100 if 回升统计[名][0] else 0
        print(f'{名:<6}{tot:>10}{破:>10}{频率:>9.2f}%{次日:>11.3f}%{五日:>11.3f}%{回升率:>9.1f}%')

if __name__ == '__main__':
    main()