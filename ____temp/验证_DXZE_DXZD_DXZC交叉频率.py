# -*- coding: utf-8 -*-
"""
统计DXZE、DXZD、DXZC的交叉数量，并按存续总日柱数计算交叉频率（多少柱交叉一次）。
交叉 = BT变量符号变化（由正转负 或 由负转正）。
"""
import os
import glob
import csv

COL_日ZC = 14
COL_日ZE = 15
COL_DTZD = 67

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 全局统计
    总日柱 = 0
    交叉 = {'DXZE': 0, 'DXZD': 0, 'DXZC': 0}
    # 每只股票的交叉数和存续日柱数
    per_stock = {名: [] for 名 in ('DXZE', 'DXZD', 'DXZC')}  # 每只股票: [交叉数, 存续日柱数]

    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_DTZD:
                    rows.append(row)
        if not rows:
            continue
        存续日柱 = len(rows)
        总日柱 += 存续日柱
        前值 = {'DXZE': None, 'DXZD': None, 'DXZC': None}
        交叉数 = {'DXZE': 0, 'DXZD': 0, 'DXZC': 0}
        for row in rows:
            try:
                日ZC = int(row[COL_日ZC])
                日ZE = int(row[COL_日ZE])
                DTZD = int(row[COL_DTZD])
            except (ValueError, IndexError):
                continue
            值 = {'DXZE': 日ZE, 'DXZD': DTZD, 'DXZC': 日ZC}
            for 名 in ('DXZE', 'DXZD', 'DXZC'):
                if 前值[名] is not None and 值[名] != 前值[名]:
                    # 符号变化 = 交叉
                    if (前值[名] > 0 and 值[名] < 0) or (前值[名] < 0 and 值[名] > 0):
                        交叉[名] += 1
                        交叉数[名] += 1
                前值[名] = 值[名]
        for 名 in ('DXZE', 'DXZD', 'DXZC'):
            per_stock[名].append((交叉数[名], 存续日柱))

    print(f'总存续日柱数: {总日柱}')
    print()
    print('=== 交叉数量与频率 ===')
    for 名 in ('DXZE', 'DXZD', 'DXZC'):
        总交叉 = 交叉[名]
        频率 = 总日柱 / 总交叉 if 总交叉 > 0 else float('inf')
        print(f'{名}: 总交叉 {总交叉}, 平均每 {频率:.1f} 柱交叉一次')
    print()
    print('=== 每只股票的交叉频率（多少柱交叉一次） ===')
    for 名 in ('DXZE', 'DXZD', 'DXZC'):
        频率列表 = [存续/交叉 for 交叉, 存续 in per_stock[名] if 交叉 > 0]
        平均频率 = sum(频率列表)/len(频率列表) if 频率列表 else 0
        中位频率 = sorted(频率列表)[len(频率列表)//2] if 频率列表 else 0
        print(f'{名}: 平均每 {平均频率:.1f} 柱交叉一次, 中位数每 {中位频率:.1f} 柱交叉一次')
    print()
    print('=== 交叉频率对比（多少柱交叉一次，越小越频繁） ===')
    频率 = {}
    for 名 in ('DXZE', 'DXZD', 'DXZC'):
        频率[名] = 总日柱 / 交叉[名] if 交叉[名] > 0 else float('inf')
    print(f'DXZE: 每 {频率["DXZE"]:.1f} 柱交叉一次')
    print(f'DXZD: 每 {频率["DXZD"]:.1f} 柱交叉一次')
    print(f'DXZC: 每 {频率["DXZC"]:.1f} 柱交叉一次')
    print(f'DXZD/DXZE 频率比: {频率["DXZD"]/频率["DXZE"]:.2f}x')
    print(f'DXZC/DXZE 频率比: {频率["DXZC"]/频率["DXZE"]:.2f}x')

if __name__ == '__main__':
    main()