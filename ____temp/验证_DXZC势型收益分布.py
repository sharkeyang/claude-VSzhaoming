# -*- coding: utf-8 -*-
"""
验证：DXZC策略按势型（金银唏嘘屎尿）分组的收益分布。
突出：不能因全时域综合表现好，就在特定势型（唏/嘘/尿/屎）使用——用人不当。
"""
import os
import glob
import csv
from collections import defaultdict

COL_涨幅 = 5
COL_日ZC = 14
COL_周势型 = 81

def 提取势型(势型串):
    if len(势型串) >= 2:
        return 势型串[1]
    return ''

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

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
                if len(row) > COL_周势型:
                    rows.append(row)
        if not rows:
            continue
        持有 = False
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZC = int(row[COL_日ZC])
            except (ValueError, IndexError):
                continue
            势型 = 提取势型(row[COL_周势型])
            if 日ZC > 0:
                if not 持有:
                    进出[势型] += 1
                    持有 = True
                收益[势型].append(涨幅)
                持有日[势型] += 1
                if 涨幅 > 0:
                    正日[势型] += 1
            else:
                持有 = False

    print('=== 按势型分组，DXZC进出的收益 ===')
    print(f'{"势型":<4}{"持有日":>8}{"占比":>8}{"平均日收益":>12}{"上涨率":>8}{"进出次数":>8}')
    总持有 = sum(持有日.values())
    for 势 in ('金', '银', '唏', '嘘', '尿', '屎'):
        if 持有日[势] == 0:
            continue
        平均 = sum(收益[势])/len(收益[势])
        上涨率 = 正日[势]/持有日[势]*100
        占比 = 持有日[势]/总持有*100
        print(f'{势:<4}{持有日[势]:>8}{占比:>7.1f}%{平均:>11.3f}%{上涨率:>7.1f}%{进出[势]:>8}')
    print()
    print('=== 涨幅贡献（各势型对DXZC总收益的贡献） ===')
    总涨幅 = sum(sum(v) for v in 收益.values())
    for 势 in ('金', '银', '唏', '嘘', '尿', '屎'):
        if 收益[势]:
            涨幅 = sum(收益[势])
            print(f'{势}: 涨幅 {涨幅:.1f}% ({涨幅/总涨幅*100:.1f}%)')

if __name__ == '__main__':
    main()