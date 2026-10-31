# -*- coding: utf-8 -*-
"""
验证：下破DJA vs 上破DJA vs 上破DJC 的持有N日累计收益（DXCD=上 前提下）。
"""
import os
import glob
import csv
from collections import defaultdict

COL_收 = 1
COL_日ZA = 13
COL_日ZC = 14
COL_DXCD = 8

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 统计: 事件 -> 持有N日累计收益
    收益 = defaultdict(lambda: defaultdict(list))

    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_日ZC:
                    rows.append(row)
        if not rows:
            continue
        for i, row in enumerate(rows):
            try:
                收 = float(row[COL_收])
                日ZA = int(row[COL_日ZA])
                日ZC = int(row[COL_日ZC])
                DXCD = row[COL_DXCD]
            except (ValueError, IndexError):
                continue
            if DXCD != '上':
                continue
            if i > 0:
                try:
                    前ZA = int(rows[i-1][COL_日ZA])
                    前ZC = int(rows[i-1][COL_日ZC])
                except (ValueError, IndexError):
                    前ZA = None
                    前ZC = None
                # 下破DJA（前ZA>0 当ZA<0）
                if 前ZA is not None and 前ZA > 0 and 日ZA < 0:
                    for k in (3, 5, 10):
                        if i + k < len(rows):
                            try:
                                后收 = float(rows[i+k][COL_收])
                                收益['下破DJA'][k].append((后收 - 收) / 收 * 100)
                            except (ValueError, IndexError):
                                pass
                # 上破DJA（前ZA<0 当ZA>0）
                if 前ZA is not None and 前ZA < 0 and 日ZA > 0:
                    for k in (3, 5, 10):
                        if i + k < len(rows):
                            try:
                                后收 = float(rows[i+k][COL_收])
                                收益['上破DJA'][k].append((后收 - 收) / 收 * 100)
                            except (ValueError, IndexError):
                                pass
                # 上破DJC（前ZC<0 当ZC>0）
                if 前ZC is not None and 前ZC < 0 and 日ZC > 0:
                    for k in (3, 5, 10):
                        if i + k < len(rows):
                            try:
                                后收 = float(rows[i+k][COL_收])
                                收益['上破DJC'][k].append((后收 - 收) / 收 * 100)
                            except (ValueError, IndexError):
                                pass

    print('=== DXCD=上 前提下，下破DJA vs 上破DJA vs 上破DJC 持有N日累计收益 ===')
    print(f'{"事件":<10}{"持有3日":>12}{"持有5日":>12}{"持有10日":>12}')
    for 事件 in ('下破DJA', '上破DJA', '上破DJC'):
        r3 = sum(收益[事件][3])/len(收益[事件][3]) if 收益[事件][3] else 0
        r5 = sum(收益[事件][5])/len(收益[事件][5]) if 收益[事件][5] else 0
        r10 = sum(收益[事件][10])/len(收益[事件][10]) if 收益[事件][10] else 0
        n3 = len(收益[事件][3])
        print(f'{事件:<10}{r3:>11.2f}%{r5:>11.2f}%{r10:>11.2f}%  (n={n3})')

if __name__ == '__main__':
    main()