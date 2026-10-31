# -*- coding: utf-8 -*-
"""
计算周A趋持有期间，DJC之上(日ZC>0)的涨幅贡献占比。
即：日ZC>0 的日子，其涨幅总和占总涨幅的比例。
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

    # 周A趋持有期间
    总涨幅 = 0.0          # 所有日子涨幅之和
    日ZC正涨幅 = 0.0      # 日ZC>0 日子涨幅之和
    日ZC负涨幅 = 0.0      # 日ZC<0 日子涨幅之和
    总日 = 0
    日ZC正日 = 0
    日ZC负日 = 0
    上涨日 = 0
    日ZC正上涨日 = 0
    日ZC负上涨日 = 0

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
                四波 = 提取四波(row[COL_周波型])
                周A持有 = (周ZC > 0) and (四波 != '虎')
                if not 周A持有:
                    continue
                总日 += 1
                总涨幅 += 涨幅
                if 日ZC > 0:
                    日ZC正日 += 1
                    日ZC正涨幅 += 涨幅
                    if 涨幅 > 0:
                        日ZC正上涨日 += 1
                else:
                    日ZC负日 += 1
                    日ZC负涨幅 += 涨幅
                    if 涨幅 > 0:
                        日ZC负上涨日 += 1
                if 涨幅 > 0:
                    上涨日 += 1

    print(f'周A趋持有总日数: {总日}')
    print(f'日ZC>0 日数: {日ZC正日} ({日ZC正日/总日*100:.1f}%)')
    print(f'日ZC<0 日数: {日ZC负日} ({日ZC负日/总日*100:.1f}%)')
    print()
    print('=== 涨幅贡献 ===')
    print(f'总涨幅: {总涨幅:.1f}%')
    print(f'日ZC>0 涨幅: {日ZC正涨幅:.1f}% ({日ZC正涨幅/总涨幅*100:.1f}%)')
    print(f'日ZC<0 涨幅: {日ZC负涨幅:.1f}% ({日ZC负涨幅/总涨幅*100:.1f}%)')
    print()
    print('=== 平均涨幅 ===')
    print(f'日ZC>0 平均涨幅: {日ZC正涨幅/日ZC正日:.3f}%')
    print(f'日ZC<0 平均涨幅: {日ZC负涨幅/日ZC负日:.3f}%')
    print()
    print('=== 上涨日 ===')
    print(f'上涨日数: {上涨日} ({上涨日/总日*100:.1f}%)')
    print(f'日ZC>0 上涨日: {日ZC正上涨日} ({日ZC正上涨日/上涨日*100:.1f}%)')
    print(f'日ZC<0 上涨日: {日ZC负上涨日} ({日ZC负上涨日/上涨日*100:.1f}%)')

if __name__ == '__main__':
    main()