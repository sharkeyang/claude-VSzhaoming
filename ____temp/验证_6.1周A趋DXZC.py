# -*- coding: utf-8 -*-
"""
比较：纯日线DXZC vs 周A趋+DXZC（6.1方法日B趋）。
纯日线DXZC：日ZC>0持有。
周A趋+DXZC：周ZC>0且非虎 且 日ZC>0持有（6.1方法日B趋）。
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

    策略名 = ['纯日线DXZC', '周A趋+DXZC']
    per_stock = []
    收益 = {名: [] for 名 in 策略名}
    收益['始终'] = []
    进出 = {名: 0 for 名 in 策略名}
    回撤 = {名: [] for 名 in 策略名}

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
        累计 = {名: 1.0 for 名 in 策略名}
        累计['始终'] = 1.0
        持有 = {名: False for 名 in 策略名}
        峰值 = {名: 1.0 for 名 in 策略名}
        净值 = {名: 1.0 for 名 in 策略名}
        最大回撤 = {名: 0.0 for 名 in 策略名}
        持有天数 = {名: 0 for 名 in 策略名}
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZC = int(row[COL_日ZC])
                周ZC = int(row[COL_周ZC])
            except (ValueError, IndexError):
                continue
            累计['始终'] *= (1 + 涨幅/100)
            收益['始终'].append(涨幅)
            四波 = 提取四波(row[COL_周波型])
            周A持有 = (周ZC > 0) and (四波 != '虎')
            conds = {
                '纯日线DXZC': 日ZC > 0,
                '周A趋+DXZC': 周A持有 and 日ZC > 0,
            }
            for 名, cond in conds.items():
                if cond:
                    if not 持有[名]:
                        进出[名] += 1
                        持有[名] = True
                    累计[名] *= (1 + 涨幅/100)
                    净值[名] *= (1 + 涨幅/100)
                    收益[名].append(涨幅)
                    持有天数[名] += 1
                    if 净值[名] > 峰值[名]:
                        峰值[名] = 净值[名]
                    回撤v = (峰值[名] - 净值[名]) / 峰值[名] * 100
                    if 回撤v > 最大回撤[名]:
                        最大回撤[名] = 回撤v
                else:
                    持有[名] = False
        per_stock.append((累计['纯日线DXZC'], 累计['周A趋+DXZC'], 累计['始终'],
                          持有天数['纯日线DXZC'], 持有天数['周A趋+DXZC']))
        for 名 in 策略名:
            回撤[名].append(最大回撤[名])

    n = len(per_stock)
    始终几何 = math.exp(sum(math.log(s[2]) for s in per_stock) / n)
    print(f'总股票数: {n}')
    print()
    print('=== ① 是否必赢 ===')
    for i, 名 in enumerate(策略名):
        正收益 = sum(1 for s in per_stock if s[i] > 1)
        跑赢 = sum(1 for s in per_stock if s[i] > s[2])
        几何 = math.exp(sum(math.log(s[i]) for s in per_stock) / n)
        print(f'{名}: 正收益 {正收益/n*100:.1f}%, 跑赢始终 {跑赢/n*100:.1f}%, 几何平均累计 {几何:.2f}x, /始终 {几何/始终几何:.2f}x')
    print()
    print('=== ② 期望收益（几何平均年化） ===')
    for i, 名 in enumerate(策略名):
        几何累计 = math.exp(sum(math.log(s[i]) for s in per_stock) / n)
        平均持有天数 = sum(s[3+i] for s in per_stock) / n
        if 平均持有天数 > 0:
            年化 = 几何累计 ** (250 / 平均持有天数) - 1
        else:
            年化 = 0
        print(f'{名}: 几何平均累计 {几何累计:.2f}x, 平均持有天数 {平均持有天数:.0f}, 年化 {年化*100:.1f}%')
    print()
    print('=== ③ 持有占比与进出次数 ===')
    总日 = len(收益['始终'])
    for 名 in 策略名:
        持有日 = len(收益[名])
        print(f'{名}: 持有日占比 {持有日/总日*100:.1f}%, 进出次数 {进出[名]}')
    print()
    print('=== ④ 最大回撤 ===')
    for 名 in 策略名:
        平均回撤 = sum(回撤[名])/len(回撤[名])
        大回撤 = sum(1 for r in 回撤[名] if r > 30)
        print(f'{名}: 平均最大回撤 {平均回撤:.1f}%, 回撤>30% 股票 {大回撤/n*100:.1f}%')

if __name__ == '__main__':
    main()