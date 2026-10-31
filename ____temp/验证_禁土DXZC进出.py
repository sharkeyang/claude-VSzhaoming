# -*- coding: utf-8 -*-
"""
验证：按DXZC进出，在四土=禁土中是否也会进出，实际能否盈利。
禁土 = 周ZC<0 且 周护级=下/忑。
对比：禁土中DXZC进出的收益 vs 非禁土中DXZC进出的收益。
"""
import os
import glob
import csv
import math

COL_涨幅 = 5
COL_日ZC = 14
COL_周护型 = 73
COL_周ZC = 87

def 提取护级(护型):
    if len(护型) >= 4:
        return 护型[3]
    return ''

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 统计: 禁土中DXZC进出 vs 非禁土中DXZC进出
    禁土_收益 = []
    非禁土_收益 = []
    禁土_进出 = 0
    非禁土_进出 = 0
    禁土_持有日 = 0
    非禁土_持有日 = 0
    禁土_正日 = 0
    非禁土_正日 = 0

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
        持有禁土 = False
        持有非禁土 = False
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZC = int(row[COL_日ZC])
                周ZC = int(row[COL_周ZC])
            except (ValueError, IndexError):
                continue
            护级 = 提取护级(row[COL_周护型])
            禁土 = (周ZC < 0) and (护级 in ('下', '忑'))
            # 按DXZC进出
            if 日ZC > 0:
                if 禁土:
                    if not 持有禁土:
                        禁土_进出 += 1
                        持有禁土 = True
                    禁土_收益.append(涨幅)
                    禁土_持有日 += 1
                    if 涨幅 > 0:
                        禁土_正日 += 1
                else:
                    if not 持有非禁土:
                        非禁土_进出 += 1
                        持有非禁土 = True
                    非禁土_收益.append(涨幅)
                    非禁土_持有日 += 1
                    if 涨幅 > 0:
                        非禁土_正日 += 1
            else:
                持有禁土 = False
                持有非禁土 = False

    print('=== 按DXZC进出，禁土 vs 非禁土 ===')
    print(f'禁土: 进出次数 {禁土_进出}, 持有日 {禁土_持有日}, 平均日收益 {sum(禁土_收益)/len(禁土_收益):.3f}%, 上涨率 {禁土_正日/禁土_持有日*100:.1f}%')
    print(f'非禁土: 进出次数 {非禁土_进出}, 持有日 {非禁土_持有日}, 平均日收益 {sum(非禁土_收益)/len(非禁土_收益):.3f}%, 上涨率 {非禁土_正日/非禁土_持有日*100:.1f}%')
    print()
    print('=== 禁土中DXZC进出的累计收益（复利） ===')
    禁土累计 = 1.0
    for r in 禁土_收益:
        禁土累计 *= (1 + r/100)
    print(f'禁土中DXZC进出累计: {禁土累计:.4f}x')
    print(f'禁土中DXZC进出年化(按持有日): {(禁土累计 ** (250/禁土_持有日) - 1)*100:.1f}%' if 禁土_持有日 > 0 else '无持有')
    print()
    print('=== 禁土中DXZC进出的正收益股票占比 ===')
    # 按股票统计禁土中DXZC进出的正收益
    禁土_股票 = {}
    for f in files:
        fid = os.path.basename(f).replace('谕组日_', '').replace('.csv', '')
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_周ZC:
                    rows.append(row)
        累计 = 1.0
        有禁土 = False
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZC = int(row[COL_日ZC])
                周ZC = int(row[COL_周ZC])
            except (ValueError, IndexError):
                continue
            护级 = 提取护级(row[COL_周护型])
            禁土 = (周ZC < 0) and (护级 in ('下', '忑'))
            if 禁土 and 日ZC > 0:
                累计 *= (1 + 涨幅/100)
                有禁土 = True
        if 有禁土:
            禁土_股票[fid] = 累计
    n = len(禁土_股票)
    正 = sum(1 for v in 禁土_股票.values() if v > 1)
    print(f'禁土中DXZC进出的股票数: {n}')
    print(f'禁土中DXZC进出正收益股票: {正}/{n} = {正/n*100:.1f}%')

if __name__ == '__main__':
    main()