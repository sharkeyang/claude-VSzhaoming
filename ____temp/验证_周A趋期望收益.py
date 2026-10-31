# -*- coding: utf-8 -*-
"""
计算周A趋策略的期望收益：策略持有期间平均周收益、年化收益，对比始终持有。
"""
import os
import glob
import csv

COL_周涨 = 1
COL_波型 = 7
COL_ZC周 = 18

def 提取四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def main():
    data_dir = r'昭明算展\谕组周'
    files = glob.glob(os.path.join(data_dir, '谕组周_*.csv'))

    # 策略持有周收益列表、始终持有周收益列表
    策略收益 = []
    始终收益 = []
    策略正周 = 0
    策略总周 = 0
    始终正周 = 0
    始终总周 = 0

    for f in files:
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) <= COL_ZC周:
                    continue
                try:
                    周涨 = float(row[COL_周涨])
                    zc = int(row[COL_ZC周])
                except (ValueError, IndexError):
                    continue
                始终收益.append(周涨)
                始终总周 += 1
                if 周涨 > 0:
                    始终正周 += 1
                四波 = 提取四波(row[COL_波型])
                持有 = (zc > 0) and (四波 != '虎')
                if 持有:
                    策略收益.append(周涨)
                    策略总周 += 1
                    if 周涨 > 0:
                        策略正周 += 1

    # 期望收益（平均周收益）
    策略期望 = sum(策略收益) / len(策略收益)
    始终期望 = sum(始终收益) / len(始终收益)
    # 年化（52周）
    策略年化 = (1 + 策略期望/100)**52 - 1
    始终年化 = (1 + 始终期望/100)**52 - 1

    print(f'策略持有周数: {策略总周}, 始终持有周数: {始终总周}')
    print()
    print('=== 期望收益（平均周收益） ===')
    print(f'策略持有期间平均周收益: {策略期望:.3f}%')
    print(f'始终持有平均周收益: {始终期望:.3f}%')
    print(f'策略 vs 始终持有: {策略期望 - 始终期望:+.3f}pp')
    print()
    print('=== 年化收益（52周复利） ===')
    print(f'策略年化: {策略年化*100:.1f}%')
    print(f'始终持有年化: {始终年化*100:.1f}%')
    print()
    print('=== 上涨率 ===')
    print(f'策略持有期间上涨率: {策略正周/策略总周*100:.1f}%')
    print(f'始终持有上涨率: {始终正周/始终总周*100:.1f}%')

if __name__ == '__main__':
    main()