# -*- coding: utf-8 -*-
"""
验证日类只按DXZE或DXZD入出操作是否必赢。
DXZE策略：日ZE>0持有，日ZE<0空仓。
DXZD策略：DTZD>0持有，DTZD<0空仓。
对比始终持有。
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

    # 每只股票统计: (DXZE策略累计, DXZD策略累计, 始终累计, DXZE正周, DXZE总周, DXZD正周, DXZD总周)
    per_stock = []
    # 全局收益列表
    ZE_收益 = []
    ZD_收益 = []
    始终_收益 = []

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
        ZE累计 = 1.0
        ZD累计 = 1.0
        始终累计 = 1.0
        ZE正 = 0
        ZE总 = 0
        ZD正 = 0
        ZD总 = 0
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZE = int(row[COL_日ZE])
                DTZD = int(row[COL_DTZD])
            except (ValueError, IndexError):
                continue
            始终累计 *= (1 + 涨幅/100)
            始终_收益.append(涨幅)
            if 日ZE > 0:
                ZE累计 *= (1 + 涨幅/100)
                ZE总 += 1
                ZE_收益.append(涨幅)
                if 涨幅 > 0:
                    ZE正 += 1
            if DTZD > 0:
                ZD累计 *= (1 + 涨幅/100)
                ZD总 += 1
                ZD_收益.append(涨幅)
                if 涨幅 > 0:
                    ZD正 += 1
        per_stock.append((ZE累计, ZD累计, 始终累计, ZE正, ZE总, ZD正, ZD总))

    n = len(per_stock)
    ZE正收益 = sum(1 for s in per_stock if s[0] > 1)
    ZD正收益 = sum(1 for s in per_stock if s[1] > 1)
    始终正收益 = sum(1 for s in per_stock if s[2] > 1)
    ZE跑赢 = sum(1 for s in per_stock if s[0] > s[2])
    ZD跑赢 = sum(1 for s in per_stock if s[1] > s[2])
    ZE几何 = sum(s[0] for s in per_stock) / n
    ZD几何 = sum(s[1] for s in per_stock) / n
    始终几何 = sum(s[2] for s in per_stock) / n

    ZE期望 = sum(ZE_收益)/len(ZE_收益)
    ZD期望 = sum(ZD_收益)/len(ZD_收益)
    始终期望 = sum(始终_收益)/len(始终_收益)
    ZE年化 = (1 + ZE期望/100)**250 - 1
    ZD年化 = (1 + ZD期望/100)**250 - 1
    始终年化 = (1 + 始终期望/100)**250 - 1

    print(f'总股票数: {n}')
    print()
    print('=== ① 是否必赢 ===')
    print(f'DXZE策略正收益股票: {ZE正收益}/{n} = {ZE正收益/n*100:.1f}%')
    print(f'DXZD策略正收益股票: {ZD正收益}/{n} = {ZD正收益/n*100:.1f}%')
    print(f'始终持有正收益股票: {始终正收益}/{n} = {始终正收益/n*100:.1f}%')
    print(f'DXZE跑赢始终持有: {ZE跑赢}/{n} = {ZE跑赢/n*100:.1f}%')
    print(f'DXZD跑赢始终持有: {ZD跑赢}/{n} = {ZD跑赢/n*100:.1f}%')
    print(f'DXZE平均累计: {ZE几何:.2f}x, DXZD平均累计: {ZD几何:.2f}x, 始终: {始终几何:.2f}x')
    print(f'DXZE/始终 累计涨幅比: {ZE几何/始终几何:.2f}x')
    print(f'DXZD/始终 累计涨幅比: {ZD几何/始终几何:.2f}x')
    print()
    print('=== ② 期望收益 ===')
    print(f'DXZE: 平均日收益 {ZE期望:.3f}%, 年化 {ZE年化*100:.1f}%')
    print(f'DXZD: 平均日收益 {ZD期望:.3f}%, 年化 {ZD年化*100:.1f}%')
    print(f'始终持有: 平均日收益 {始终期望:.3f}%, 年化 {始终年化*100:.1f}%')
    print()
    print('=== ③ 持有占比 ===')
    ZE总日 = sum(s[4] for s in per_stock)
    ZD总日 = sum(s[6] for s in per_stock)
    总日 = len(始终_收益)
    print(f'DXZE持有日占比: {ZE总日}/{总日} = {ZE总日/总日*100:.1f}%')
    print(f'DXZD持有日占比: {ZD总日}/{总日} = {ZD总日/总日*100:.1f}%')

if __name__ == '__main__':
    main()