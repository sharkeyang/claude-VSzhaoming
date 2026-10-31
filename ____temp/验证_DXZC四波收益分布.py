# -*- coding: utf-8 -*-
"""
验证：DXZC策略在不同四波区域（龙/武/虎/雀）的表现。
突出：不能因为全时域综合表现好，就在特定区域（虎/雀）使用——用人不当。
"""
import os
import glob
import csv
from collections import defaultdict

COL_涨幅 = 5
COL_日ZC = 14
COL_周波型 = 76

def 提取四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 按四波分组，DXZC进出的收益
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
                if len(row) > COL_周波型:
                    rows.append(row)
        if not rows:
            continue
        持有 = False
        当前波 = None
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZC = int(row[COL_日ZC])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[COL_周波型])
            # 按DXZC进出
            if 日ZC > 0:
                if not 持有:
                    进出[四波] += 1
                    持有 = True
                收益[四波].append(涨幅)
                持有日[四波] += 1
                if 涨幅 > 0:
                    正日[四波] += 1
            else:
                持有 = False

    print('=== 按四波分组，DXZC进出的收益 ===')
    print(f'{"四波":<4}{"持有日":>8}{"占比":>8}{"平均日收益":>12}{"上涨率":>8}{"进出次数":>8}')
    for 波 in ('龙', '武', '虎', '雀'):
        if 持有日[波] == 0:
            continue
        平均 = sum(收益[波])/len(收益[波])
        上涨率 = 正日[波]/持有日[波]*100
        占比 = 持有日[波]/sum(持有日.values())*100
        print(f'{波:<4}{持有日[波]:>8}{占比:>7.1f}%{平均:>11.3f}%{上涨率:>7.1f}%{进出[波]:>8}')
    print()
    print('=== 涨幅贡献（各四波对DXZC总收益的贡献） ===')
    总涨幅 = sum(sum(v) for v in 收益.values())
    for 波 in ('龙', '武', '虎', '雀'):
        if 收益[波]:
            涨幅 = sum(收益[波])
            print(f'{波}: 涨幅 {涨幅:.1f}% ({涨幅/总涨幅*100:.1f}%)')

if __name__ == '__main__':
    main()