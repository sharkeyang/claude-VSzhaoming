# -*- coding: utf-8 -*-
"""
验证周A趋方法（WJC入口）：WXZC>0持有，WXZC<0或(WXZC>0且虎)退出。
验证：①是否必赢（正收益股票占比、策略/始终持有累计涨幅比）②能否抓住多数涨机会（覆盖上涨周占比）。
"""
import os
import glob
import csv
from collections import defaultdict

COL_周涨 = 1
COL_HR = 3
COL_护型 = 4
COL_波型 = 7
COL_ZB周 = 17
COL_ZC周 = 18
COL_AB周 = 22

def 提取四波(波型):
    """含'虎'取第5字符，否则取第3字符"""
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def main():
    data_dir = r'昭明算展\谕组周'
    files = glob.glob(os.path.join(data_dir, '谕组周_*.csv'))
    print(f'文件数: {len(files)}')

    # 每只股票的统计
    per_stock = []  # (策略累计, 始终持有累计, 策略正周数, 策略总周数, 上涨周数, 覆盖上涨周数)
    total_rows = 0
    total_hold_rows = 0  # 策略持有周数
    total_up_rows = 0    # 上涨周数
    total_covered_up = 0 # 策略覆盖的上涨周数

    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_AB周:
                    rows.append(row)
        if not rows:
            continue

        # 策略累计收益（复利）
        策略累计 = 1.0
        始终累计 = 1.0
        策略正周 = 0
        策略总周 = 0
        上涨周 = 0
        覆盖上涨 = 0

        for row in rows:
            try:
                周涨 = float(row[COL_周涨])
                zc = int(row[COL_ZC周])
            except (ValueError, IndexError):
                continue
            total_rows += 1
            始终累计 *= (1 + 周涨/100)
            if 周涨 > 0:
                上涨周 += 1
                total_up_rows += 1

            # 判断是否持有（WXZC>0 且非虎）
            四波 = 提取四波(row[COL_波型])
            持有 = (zc > 0) and (四波 != '虎')
            if 持有:
                策略累计 *= (1 + 周涨/100)
                策略总周 += 1
                total_hold_rows += 1
                if 周涨 > 0:
                    策略正周 += 1
                    覆盖上涨 += 1
                    total_covered_up += 1

        per_stock.append((策略累计, 始终累计, 策略正周, 策略总周, 上涨周, 覆盖上涨))

    n = len(per_stock)
    # 正收益股票占比
    策略正收益 = sum(1 for s in per_stock if s[0] > 1)
    始终正收益 = sum(1 for s in per_stock if s[1] > 1)
    # 策略跑赢始终持有
    跑赢 = sum(1 for s in per_stock if s[0] > s[1])
    # 策略/始终持有 累计涨幅比（几何平均）
    策略几何 = sum(s[0] for s in per_stock) / n
    始终几何 = sum(s[1] for s in per_stock) / n

    print(f'总股票数: {n}')
    print(f'总周数: {total_rows}')
    print()
    print('=== ① 是否必赢 ===')
    print(f'策略正收益股票: {策略正收益}/{n} = {策略正收益/n*100:.1f}%')
    print(f'始终持有正收益股票: {始终正收益}/{n} = {始终正收益/n*100:.1f}%')
    print(f'策略跑赢始终持有: {跑赢}/{n} = {跑赢/n*100:.1f}%')
    print(f'策略平均累计: {策略几何:.2f}x, 始终持有平均累计: {始终几何:.2f}x')
    print(f'策略/始终持有 累计涨幅比: {策略几何/始终几何:.2f}x')
    print()
    print('=== ② 能否抓住多数涨机会 ===')
    print(f'策略持有周占比: {total_hold_rows}/{total_rows} = {total_hold_rows/total_rows*100:.1f}%')
    print(f'上涨周占比: {total_up_rows}/{total_rows} = {total_up_rows/total_rows*100:.1f}%')
    print(f'策略覆盖上涨周: {total_covered_up}/{total_up_rows} = {total_covered_up/total_up_rows*100:.1f}%')
    # 策略持有期间上涨率 vs 空仓期间上涨率
    空仓周 = total_rows - total_hold_rows
    空仓上涨 = total_up_rows - total_covered_up
    print(f'持有期间上涨率: {total_covered_up}/{total_hold_rows} = {total_covered_up/total_hold_rows*100:.1f}%')
    if 空仓周 > 0:
        print(f'空仓期间上涨率: {空仓上涨}/{空仓周} = {空仓上涨/空仓周*100:.1f}%')

if __name__ == '__main__':
    main()