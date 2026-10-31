# -*- coding: utf-8 -*-
"""
验证：DXZC进出的收益是否主要来自主升（沃土）阶段，虎/震荡阶段收益很少。
按四土（沃/禁/念/肋）分组，看DXZC进出的收益分布。
"""
import os
import glob
import csv
import math
from collections import defaultdict

COL_涨幅 = 5
COL_日ZC = 14
COL_周护型 = 73
COL_周ZC = 87

def 提取护级(护型):
    if len(护型) >= 4:
        return 护型[3]
    return ''

def 算四土(周ZC, 护级):
    if 周ZC < 0 and 护级 in ('下', '忑'):
        return '禁'
    elif 护级 in ('中', '下', '忑'):
        return '念'
    elif 周ZC > 0 and 护级 in ('上', '忐'):
        return '沃'
    else:
        return '肋'

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 按四土分组，DXZC进出的收益
    收益 = defaultdict(list)
    持有日 = defaultdict(int)
    正日 = defaultdict(int)
    进出 = defaultdict(int)

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
        持有 = False
        当前土 = None
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZC = int(row[COL_日ZC])
                周ZC = int(row[COL_周ZC])
            except (ValueError, IndexError):
                continue
            护级 = 提取护级(row[COL_周护型])
            土 = 算四土(周ZC, 护级)
            # 按DXZC进出
            if 日ZC > 0:
                if not 持有:
                    进出[土] += 1
                    持有 = True
                收益[土].append(涨幅)
                持有日[土] += 1
                if 涨幅 > 0:
                    正日[土] += 1
            else:
                持有 = False

    print('=== 按四土分组，DXZC进出的收益 ===')
    print(f'{"四土":<4}{"持有日":>8}{"占比":>8}{"平均日收益":>12}{"上涨率":>8}{"进出次数":>8}')
    for 土 in ('沃', '禁', '念', '肋'):
        if 持有日[土] == 0:
            continue
        平均 = sum(收益[土])/len(收益[土])
        上涨率 = 正日[土]/持有日[土]*100
        占比 = 持有日[土]/sum(持有日.values())*100
        print(f'{土:<4}{持有日[土]:>8}{占比:>7.1f}%{平均:>11.3f}%{上涨率:>7.1f}%{进出[土]:>8}')
    print()
    print('=== 涨幅贡献（各四土对DXZC总收益的贡献） ===')
    总涨幅 = sum(sum(v) for v in 收益.values())
    for 土 in ('沃', '禁', '念', '肋'):
        if 收益[土]:
            涨幅 = sum(收益[土])
            print(f'{土}: 涨幅 {涨幅:.1f}% ({涨幅/总涨幅*100:.1f}%)')

if __name__ == '__main__':
    main()