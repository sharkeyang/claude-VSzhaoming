# -*- coding: utf-8 -*-
"""
验证：6.1方法日B趋（DXZC>0）范围更广，包含DXZA>0和DXZA<0。
6.1的核心目的是抓住DJC之上的均上期权。
对比：6.1范围内，DXZA>0（DJA之上）vs DXZA<0（DJA之下）的收益。
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

    # 6.1范围（DXZC>0）内，DXZA>0 vs DXZA<0
    收益 = defaultdict(list)
    持有日 = defaultdict(int)
    正日 = defaultdict(int)

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
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZA = int(row[COL_日ZA])
                日ZC = int(row[COL_日ZC])
            except (ValueError, IndexError):
                continue
            if 日ZC > 0:  # 6.1范围（DXZC>0）
                if 日ZA > 0:  # DXZA>0（DJA之上）
                    收益['DXZA>0'].append(涨幅)
                    持有日['DXZA>0'] += 1
                    if 涨幅 > 0:
                        正日['DXZA>0'] += 1
                else:  # DXZA<0（DJA之下）
                    收益['DXZA<0'].append(涨幅)
                    持有日['DXZA<0'] += 1
                    if 涨幅 > 0:
                        正日['DXZA<0'] += 1

    print('=== 6.1范围（DXZC>0）内，DXZA>0 vs DXZA<0 ===')
    总持有 = 持有日['DXZA>0'] + 持有日['DXZA<0']
    for 名 in ('DXZA>0', 'DXZA<0'):
        平均 = sum(收益[名])/len(收益[名])
        上涨率 = 正日[名]/持有日[名]*100
        占比 = 持有日[名]/总持有*100
        print(f'{名}: 持有日 {持有日[名]} ({占比:.1f}%), 平均日收益 {平均:.3f}%, 上涨率 {上涨率:.1f}%')
    print()
    print('=== 涨幅贡献 ===')
    总涨幅 = sum(sum(v) for v in 收益.values())
    for 名 in ('DXZA>0', 'DXZA<0'):
        涨幅 = sum(收益[名])
        print(f'{名}: 涨幅 {涨幅:.1f}% ({涨幅/总涨幅*100:.1f}%)')

if __name__ == '__main__':
    main()