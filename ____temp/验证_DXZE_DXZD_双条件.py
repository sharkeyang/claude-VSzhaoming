# -*- coding: utf-8 -*-
"""
比较三个策略：DXZE>0、DXZD>0、DXZE>0且DXZD>0。
验证：正收益、跑赢、期望收益、年化、持有占比、进出次数、回撤。
"""
import os
import glob
import csv

COL_涨幅 = 5
COL_日ZE = 15
COL_DTZD = 67

def main():
    data_dir = r'昭明算展\谕组日'
    files = glob.glob(os.path.join(data_dir, '谕组日_*.csv'))
    print(f'文件数: {len(files)}')

    # 每只股票: (ZE累计, ZD累计, ZEZD累计, 始终累计)
    per_stock = []
    # 全局收益
    收益 = {'ZE': [], 'ZD': [], 'ZEZD': [], '始终': []}
    # 进出次数
    进出 = {'ZE': 0, 'ZD': 0, 'ZEZD': 0}
    # 回撤
    回撤 = {'ZE': [], 'ZD': [], 'ZEZD': []}

    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_DTZD:
                    rows.append(row)
        if not rows:
            continue
        累计 = {'ZE': 1.0, 'ZD': 1.0, 'ZEZD': 1.0, '始终': 1.0}
        持有 = {'ZE': False, 'ZD': False, 'ZEZD': False}
        峰值 = {'ZE': 1.0, 'ZD': 1.0, 'ZEZD': 1.0}
        净值 = {'ZE': 1.0, 'ZD': 1.0, 'ZEZD': 1.0}
        最大回撤 = {'ZE': 0.0, 'ZD': 0.0, 'ZEZD': 0.0}
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZE = int(row[COL_日ZE])
                DTZD = int(row[COL_DTZD])
            except (ValueError, IndexError):
                continue
            累计['始终'] *= (1 + 涨幅/100)
            收益['始终'].append(涨幅)
            # 三个策略
            conds = {
                'ZE': 日ZE > 0,
                'ZD': DTZD > 0,
                'ZEZD': 日ZE > 0 and DTZD > 0,
            }
            for 名, cond in conds.items():
                if cond:
                    if not 持有[名]:
                        进出[名] += 1
                        持有[名] = True
                    累计[名] *= (1 + 涨幅/100)
                    净值[名] *= (1 + 涨幅/100)
                    收益[名].append(涨幅)
                    if 净值[名] > 峰值[名]:
                        峰值[名] = 净值[名]
                    回撤v = (峰值[名] - 净值[名]) / 峰值[名] * 100
                    if 回撤v > 最大回撤[名]:
                        最大回撤[名] = 回撤v
                else:
                    持有[名] = False
        per_stock.append((累计['ZE'], 累计['ZD'], 累计['ZEZD'], 累计['始终']))
        回撤['ZE'].append(最大回撤['ZE'])
        回撤['ZD'].append(最大回撤['ZD'])
        回撤['ZEZD'].append(最大回撤['ZEZD'])

    n = len(per_stock)
    print(f'总股票数: {n}')
    print()
    print('=== ① 是否必赢 ===')
    for 名, idx in [('DXZE', 0), ('DXZD', 1), ('DXZE&DXZD', 2)]:
        正收益 = sum(1 for s in per_stock if s[idx] > 1)
        跑赢 = sum(1 for s in per_stock if s[idx] > s[3])
        几何 = sum(s[idx] for s in per_stock) / n
        始终几何 = sum(s[3] for s in per_stock) / n
        print(f'{名}: 正收益 {正收益/n*100:.1f}%, 跑赢始终 {跑赢/n*100:.1f}%, 平均累计 {几何:.2f}x, /始终 {几何/始终几何:.2f}x')
    print()
    print('=== ② 期望收益 ===')
    for 名 in ('ZE', 'ZD', 'ZEZD'):
        期望 = sum(收益[名])/len(收益[名])
        年化 = (1 + 期望/100)**250 - 1
        print(f'{名}: 平均日收益 {期望:.3f}%, 年化 {年化*100:.1f}%')
    print()
    print('=== ③ 持有占比与进出次数 ===')
    总日 = len(收益['始终'])
    for 名 in ('ZE', 'ZD', 'ZEZD'):
        持有日 = len(收益[名])
        print(f'{名}: 持有日占比 {持有日/总日*100:.1f}%, 进出次数 {进出[名]}')
    print()
    print('=== ④ 最大回撤 ===')
    for 名 in ('ZE', 'ZD', 'ZEZD'):
        平均回撤 = sum(回撤[名])/len(回撤[名])
        大回撤 = sum(1 for r in 回撤[名] if r > 30)
        print(f'{名}: 平均最大回撤 {平均回撤:.1f}%, 回撤>30% 股票 {大回撤/n*100:.1f}%')

if __name__ == '__main__':
    main()