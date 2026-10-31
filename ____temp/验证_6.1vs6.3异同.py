# -*- coding: utf-8 -*-
"""
分析6.1（DJC丘）vs 6.3（DJA之上）的异同。
验证：6.1范围内DXZA的波动（劫/诱多），6.3在DJA之上介入的摩擦成本。
"""
import os
import glob
import csv
from collections import defaultdict

COL_涨幅 = 5
COL_日ZA = 13
COL_日ZC = 14

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 6.1范围（DXZC>0）内，DXZA的波动
    下破DJA次数 = 0       # DXZA由正转负
    下破后5日回升 = 0     # 下破DJA后5日回升
    上破DJA次数 = 0       # DXZA由负转正
    上破后5日跌破 = 0     # 上破DJA后5日跌破（诱多）
    上破后5日维持 = 0     # 上破DJA后5日维持（真突破）
    # 6.1范围内总日数
    总日 = 0

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
                日ZA = int(row[COL_日ZA])
                日ZC = int(row[COL_日ZC])
            except (ValueError, IndexError):
                continue
            if 日ZC <= 0:
                continue
            总日 += 1
            if i > 0:
                try:
                    前ZA = int(rows[i-1][COL_日ZA])
                except (ValueError, IndexError):
                    前ZA = None
                if 前ZA is not None:
                    # 下破DJA（前>0 当<0）
                    if 前ZA > 0 and 日ZA < 0:
                        下破DJA次数 += 1
                        # 5日回升
                        回升 = False
                        for j in range(i+1, min(i+6, len(rows))):
                            try:
                                if int(rows[j][COL_日ZA]) > 0:
                                    回升 = True
                                    break
                            except (ValueError, IndexError):
                                pass
                        if 回升:
                            下破后5日回升 += 1
                    # 上破DJA（前<0 当>0）
                    if 前ZA < 0 and 日ZA > 0:
                        上破DJA次数 += 1
                        # 5日维持（5日后仍>0）
                        维持 = False
                        if i + 5 < len(rows):
                            try:
                                if int(rows[i+5][COL_日ZA]) > 0:
                                    维持 = True
                            except (ValueError, IndexError):
                                pass
                        if 维持:
                            上破后5日维持 += 1
                        else:
                            上破后5日跌破 += 1

    print(f'6.1范围（DXZC>0）总日数: {总日}')
    print()
    print('=== 6.1范围内，DXZA的波动（劫/诱多） ===')
    print(f'下破DJA次数（DXZA由正转负）: {下破DJA次数} ({下破DJA次数/总日*100:.1f}%)')
    print(f'下破DJA后5日回升: {下破后5日回升}/{下破DJA次数} = {下破后5日回升/下破DJA次数*100:.1f}%')
    print(f'上破DJA次数（DXZA由负转正）: {上破DJA次数} ({上破DJA次数/总日*100:.1f}%)')
    print(f'上破DJA后5日维持（真突破）: {上破后5日维持}/{上破DJA次数} = {上破后5日维持/上破DJA次数*100:.1f}%')
    print(f'上破DJA后5日跌破（诱多）: {上破后5日跌破}/{上破DJA次数} = {上破后5日跌破/上破DJA次数*100:.1f}%')

if __name__ == '__main__':
    main()