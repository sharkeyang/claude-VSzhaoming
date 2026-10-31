# -*- coding: utf-8 -*-
"""
对比：日B趋（周A趋+DXZC，限定区域）vs 纯日线DXZC（全时域）。
验证：限定区域后应用DXZC是否效率更高（每次进出收益、回撤、胜率、摩擦成本）。
"""
import os
import glob
import csv
import math

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

    策略名 = ['纯日线DXZC', '日B趋(周A趋+DXZC)']
    # 每次进出的收益（一个丘 = 一次进出）
    丘收益 = {名: [] for 名 in 策略名}
    进出 = {名: 0 for 名 in 策略名}
    回撤 = {名: [] for 名 in 策略名}
    持有日 = {名: 0 for 名 in 策略名}

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
        持有 = {名: False for 名 in 策略名}
        丘累计 = {名: 1.0 for 名 in 策略名}
        峰值 = {名: 1.0 for 名 in 策略名}
        净值 = {名: 1.0 for 名 in 策略名}
        最大回撤 = {名: 0.0 for 名 in 策略名}
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZC = int(row[COL_日ZC])
                周ZC = int(row[COL_周ZC])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[COL_周波型])
            周A持有 = (周ZC > 0) and (四波 != '虎')
            conds = {
                '纯日线DXZC': 日ZC > 0,
                '日B趋(周A趋+DXZC)': 周A持有 and 日ZC > 0,
            }
            for 名, cond in conds.items():
                if cond:
                    if not 持有[名]:
                        # 结束上一个丘
                        if 丘累计[名] > 1.0:
                            丘收益[名].append(丘累计[名] - 1)
                        丘累计[名] = 1.0
                        进出[名] += 1
                        持有[名] = True
                    丘累计[名] *= (1 + 涨幅/100)
                    净值[名] *= (1 + 涨幅/100)
                    持有日[名] += 1
                    if 净值[名] > 峰值[名]:
                        峰值[名] = 净值[名]
                    回撤v = (峰值[名] - 净值[名]) / 峰值[名] * 100
                    if 回撤v > 最大回撤[名]:
                        最大回撤[名] = 回撤v
                else:
                    if 持有[名] and 丘累计[名] > 1.0:
                        丘收益[名].append(丘累计[名] - 1)
                    丘累计[名] = 1.0
                    持有[名] = False
        # 结束最后一个丘
        for 名 in 策略名:
            if 丘累计[名] > 1.0:
                丘收益[名].append(丘累计[名] - 1)
            回撤[名].append(最大回撤[名])

    print('=== 日B趋(限定区域) vs 纯日线DXZC(全时域) ===')
    for 名 in 策略名:
        丘数 = len(丘收益[名])
        丘正 = sum(1 for r in 丘收益[名] if r > 0)
        丘平均 = sum(丘收益[名])/丘数 if 丘数 else 0
        丘中位 = sorted(丘收益[名])[丘数//2] if 丘数 else 0
        平均回撤 = sum(回撤[名])/len(回撤[名])
        大回撤 = sum(1 for r in 回撤[名] if r > 30)
        print(f'\n{名}:')
        print(f'  进出次数(丘数): {丘数}')
        print(f'  每次进出平均收益: {丘平均*100:.2f}%')
        print(f'  每次进出中位收益: {丘中位*100:.2f}%')
        print(f'  丘正收益占比: {丘正/丘数*100:.1f}%')
        print(f'  平均最大回撤: {平均回撤:.1f}%')
        print(f'  回撤>30% 股票: {大回撤/len(回撤[名])*100:.1f}%')
        print(f'  持有日: {持有日[名]}')

if __name__ == '__main__':
    main()