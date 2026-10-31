# -*- coding: utf-8 -*-
"""
验证：日B趋（DJC丘策略）是否涵盖周A/周B中所有主要上升机会（均上期权）。
对比：①周A趋（周ZC>0且非虎持有）②日B趋（周ZC>0且非虎 且 日ZC>0持有）。
验证：DJC之上是否覆盖主要上升机会；DJC之上退出能否提高收益。
"""
import os
import glob
import csv

COL_涨幅 = 5
COL_日ZC = 14
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

    # 周A趋持有：周ZC>0 且 非虎
    周A_收益 = []
    周A_正日 = 0
    周A_总日 = 0
    # 日B趋持有：周ZC>0 且 非虎 且 日ZC>0
    日B_收益 = []
    日B_正日 = 0
    日B_总日 = 0
    # 周A趋持有范围内，日ZC>0 的覆盖
    周A_内_日ZC正 = 0
    周A_内_上涨日 = 0
    周A_内_日ZC正_上涨 = 0
    # 周A趋持有范围内，上涨日的日ZC>0 覆盖
    周A_内_上涨日_日ZC正 = 0

    n_rows = 0

    for f in files:
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) <= COL_周ZC:
                    continue
                try:
                    涨幅 = float(row[COL_涨幅])
                    日ZC = int(row[COL_日ZC])
                    周ZC = int(row[COL_周ZC])
                except (ValueError, IndexError):
                    continue
                n_rows += 1
                四波 = 提取四波(row[COL_周波型])
                周A持有 = (周ZC > 0) and (四波 != '虎')

                if 周A持有:
                    周A_收益.append(涨幅)
                    周A_总日 += 1
                    if 涨幅 > 0:
                        周A_正日 += 1
                        周A_内_上涨日 += 1
                    # 周A持有范围内，日ZC>0 覆盖
                    if 日ZC > 0:
                        周A_内_日ZC正 += 1
                        if 涨幅 > 0:
                            周A_内_日ZC正_上涨 += 1
                            周A_内_上涨日_日ZC正 += 1

                    # 日B趋：周A持有 且 日ZC>0
                    if 日ZC > 0:
                        日B_收益.append(涨幅)
                        日B_总日 += 1
                        if 涨幅 > 0:
                            日B_正日 += 1

    # 周A趋期望收益
    周A_期望 = sum(周A_收益)/len(周A_收益)
    日B_期望 = sum(日B_收益)/len(日B_收益)
    周A_年化 = (1 + 周A_期望/100)**250 - 1
    日B_年化 = (1 + 日B_期望/100)**250 - 1

    print(f'总日数: {n_rows}')
    print()
    print('=== 周A趋持有范围内，DJC之上(日ZC>0)的覆盖 ===')
    print(f'周A趋持有日数: {周A_总日}')
    print(f'周A趋持有内 日ZC>0 日数: {周A_内_日ZC正} ({周A_内_日ZC正/周A_总日*100:.1f}%)')
    print(f'周A趋持有内 上涨日数: {周A_内_上涨日} ({周A_内_上涨日/周A_总日*100:.1f}%)')
    print(f'上涨日中 日ZC>0 覆盖: {周A_内_上涨日_日ZC正}/{周A_内_上涨日} = {周A_内_上涨日_日ZC正/周A_内_上涨日*100:.1f}%')
    print()
    print('=== 周A趋 vs 日B趋(DJC之上退出) 收益对比 ===')
    print(f'周A趋: 平均日收益 {周A_期望:.3f}%, 上涨率 {周A_正日/周A_总日*100:.1f}%, 年化 {周A_年化*100:.1f}%')
    print(f'日B趋: 平均日收益 {日B_期望:.3f}%, 上涨率 {日B_正日/日B_总日*100:.1f}%, 年化 {日B_年化*100:.1f}%')
    print(f'日B趋 vs 周A趋: {日B_期望 - 周A_期望:+.3f}pp/日')
    print()
    print('=== 关键：DJC之上退出能否提高收益？ ===')
    print(f'日B趋持有日占比: {日B_总日}/{周A_总日} = {日B_总日/周A_总日*100:.1f}%')
    print(f'日B趋覆盖上涨日: {日B_正日}/{周A_正日} = {日B_正日/周A_正日*100:.1f}%')

if __name__ == '__main__':
    main()