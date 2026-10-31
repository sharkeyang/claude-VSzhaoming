# -*- coding: utf-8 -*-
"""
验证方法周B趋（WJB入口）：WXZC>0时劫后以龙骨转正(WXAB由负转正)+WXZB>0+升连周边再次介入，持有至WXZC<0或(WXZC>0且虎)。
验证：①是否必赢 ②能否抓住多数涨机会 ③期望收益。
"""
import os
import glob
import csv

COL_周涨 = 1
COL_波型 = 7
COL_ZB周 = 17
COL_ZC周 = 18
COL_AB周 = 22
COL_并符串周 = 51

def 提取四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def 是升连周边(并符串):
    """升连周边 = 尾字符 Q(升连)/O(升吞)/o(升孕)"""
    if not 并符串:
        return False
    return 并符串[-1] in ('Q', 'O', 'o')

def main():
    data_dir = r'昭明算展\谕组周'
    files = glob.glob(os.path.join(data_dir, '谕组周_*.csv'))
    print(f'文件数: {len(files)}')

    per_stock = []  # (策略累计, 始终累计, 策略正周, 策略总周, 上涨周, 覆盖上涨)
    策略收益 = []
    始终收益 = []
    total_rows = 0
    total_hold_rows = 0
    total_up_rows = 0
    total_covered_up = 0

    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_并符串周:
                    rows.append(row)
        if not rows:
            continue

        策略累计 = 1.0
        始终累计 = 1.0
        策略正周 = 0
        策略总周 = 0
        上涨周 = 0
        覆盖上涨 = 0
        持有 = False
        前AB = None

        for i, row in enumerate(rows):
            try:
                周涨 = float(row[COL_周涨])
                zc = int(row[COL_ZC周])
                ab = int(row[COL_AB周])
                zb = int(row[COL_ZB周])
            except (ValueError, IndexError):
                continue
            total_rows += 1
            始终累计 *= (1 + 周涨/100)
            if 周涨 > 0:
                上涨周 += 1
                total_up_rows += 1

            四波 = 提取四波(row[COL_波型])
            并符串 = row[COL_并符串周]

            # 退出条件：WXZC<0 或（WXZC>0 且虎）
            if 持有 and (zc < 0 or (zc > 0 and 四波 == '虎')):
                持有 = False

            # 介入条件：WXZC>0 且 AB由负转正 且 ZB>0 且 升连周边
            if not 持有:
                ab转正 = (前AB is not None and 前AB < 0 and ab > 0)
                if zc > 0 and ab转正 and zb > 0 and 是升连周边(并符串):
                    持有 = True

            if 持有:
                策略累计 *= (1 + 周涨/100)
                策略收益.append(周涨)
                策略总周 += 1
                total_hold_rows += 1
                if 周涨 > 0:
                    策略正周 += 1
                    覆盖上涨 += 1
                    total_covered_up += 1

            始终收益.append(周涨)
            前AB = ab

        per_stock.append((策略累计, 始终累计, 策略正周, 策略总周, 上涨周, 覆盖上涨))

    n = len(per_stock)
    策略正收益 = sum(1 for s in per_stock if s[0] > 1)
    始终正收益 = sum(1 for s in per_stock if s[1] > 1)
    跑赢 = sum(1 for s in per_stock if s[0] > s[1])
    策略几何 = sum(s[0] for s in per_stock) / n
    始终几何 = sum(s[1] for s in per_stock) / n
    策略期望 = sum(策略收益) / len(策略收益) if 策略收益 else 0
    始终期望 = sum(始终收益) / len(始终收益) if 始终收益 else 0
    策略年化 = (1 + 策略期望/100)**52 - 1
    始终年化 = (1 + 始终期望/100)**52 - 1

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
    空仓周 = total_rows - total_hold_rows
    空仓上涨 = total_up_rows - total_covered_up
    print(f'持有期间上涨率: {total_covered_up}/{total_hold_rows} = {total_covered_up/total_hold_rows*100:.1f}%')
    if 空仓周 > 0:
        print(f'空仓期间上涨率: {空仓上涨}/{空仓周} = {空仓上涨/空仓周*100:.1f}%')
    print()
    print('=== ③ 期望收益 ===')
    print(f'策略持有期间平均周收益: {策略期望:.3f}%')
    print(f'始终持有平均周收益: {始终期望:.3f}%')
    print(f'策略年化: {策略年化*100:.1f}%')
    print(f'始终持有年化: {始终年化*100:.1f}%')

if __name__ == '__main__':
    main()