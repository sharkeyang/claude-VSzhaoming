# -*- coding: utf-8 -*-
"""
验证6.5方法日J漏（6.0-6.2，即DJA之下介入）是否获利。
周线主升基础上，DXZA<0（DJA之下）的收益 vs DXZA>0（DJA之上）。
"""
import os
import glob
import csv
from collections import defaultdict

COL_涨幅 = 5
COL_日ZA = 13
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

    # 周线主升基础上，DXZA<0 vs DXZA>0
    收益 = defaultdict(list)
    持有日 = defaultdict(int)
    正日 = defaultdict(int)

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
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZA = int(row[COL_日ZA])
                周ZC = int(row[COL_周ZC])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[COL_周波型])
            周主升 = (周ZC > 0) and (四波 != '虎')
            if not 周主升:
                continue
            if 日ZA < 0:  # DXZA<0（DJA之下，6.5低吸）
                收益['DXZA<0'].append(涨幅)
                持有日['DXZA<0'] += 1
                if 涨幅 > 0:
                    正日['DXZA<0'] += 1
            else:  # DXZA>0（DJA之上）
                收益['DXZA>0'].append(涨幅)
                持有日['DXZA>0'] += 1
                if 涨幅 > 0:
                    正日['DXZA>0'] += 1

    print('=== 周线主升基础上，DXZA<0（6.5低吸）vs DXZA>0 ===')
    for 名 in ('DXZA<0', 'DXZA>0'):
        平均 = sum(收益[名])/len(收益[名])
        上涨率 = 正日[名]/持有日[名]*100
        print(f'{名}: 持有日 {持有日[名]}, 平均日收益 {平均:.3f}%, 上涨率 {上涨率:.1f}%')
    print()
    print('=== 涨幅贡献 ===')
    总涨幅 = sum(sum(v) for v in 收益.values())
    for 名 in ('DXZA<0', 'DXZA>0'):
        涨幅 = sum(收益[名])
        print(f'{名}: 涨幅 {涨幅:.1f}% ({涨幅/总涨幅*100:.1f}%)')

if __name__ == '__main__':
    main()