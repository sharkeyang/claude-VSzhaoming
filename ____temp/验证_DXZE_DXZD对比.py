# -*- coding: utf-8 -*-
"""
对比DXZE(EMA120)和DXZD(EMA60)策略：交易频率、最大回撤、持有期间上涨率。
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

    # 全局统计
    ZE_进出 = 0
    ZD_进出 = 0
    ZE_持有上涨 = 0
    ZE_持有总 = 0
    ZD_持有上涨 = 0
    ZD_持有总 = 0
    # 每只股票的最大回撤
    ZE_回撤 = []
    ZD_回撤 = []

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
        # 逐日，判断进出
        ZE持有 = False
        ZD持有 = False
        ZE_峰值 = 1.0
        ZD_峰值 = 1.0
        ZE_净值 = 1.0
        ZD_净值 = 1.0
        ZE_最大回撤 = 0.0
        ZD_最大回撤 = 0.0
        for row in rows:
            try:
                涨幅 = float(row[COL_涨幅])
                日ZE = int(row[COL_日ZE])
                DTZD = int(row[COL_DTZD])
            except (ValueError, IndexError):
                continue
            # DXZE策略
            if 日ZE > 0:
                if not ZE持有:
                    ZE_进出 += 1
                    ZE持有 = True
                ZE_净值 *= (1 + 涨幅/100)
                ZE_持有总 += 1
                if 涨幅 > 0:
                    ZE_持有上涨 += 1
                if ZE_净值 > ZE_峰值:
                    ZE_峰值 = ZE_净值
                回撤 = (ZE_峰值 - ZE_净值) / ZE_峰值 * 100
                if 回撤 > ZE_最大回撤:
                    ZE_最大回撤 = 回撤
            else:
                ZE持有 = False
            # DXZD策略
            if DTZD > 0:
                if not ZD持有:
                    ZD_进出 += 1
                    ZD持有 = True
                ZD_净值 *= (1 + 涨幅/100)
                ZD_持有总 += 1
                if 涨幅 > 0:
                    ZD_持有上涨 += 1
                if ZD_净值 > ZD_峰值:
                    ZD_峰值 = ZD_净值
                回撤 = (ZD_峰值 - ZD_净值) / ZD_峰值 * 100
                if 回撤 > ZD_最大回撤:
                    ZD_最大回撤 = 回撤
            else:
                ZD持有 = False
        ZE_回撤.append(ZE_最大回撤)
        ZD_回撤.append(ZD_最大回撤)

    print(f'总股票数: {len(ZE_回撤)}')
    print()
    print('=== 交易频率 ===')
    print(f'DXZE 进出次数: {ZE_进出}')
    print(f'DXZD 进出次数: {ZD_进出}')
    print(f'DXZD/DXZE 进出比: {ZD_进出/ZE_进出:.2f}x')
    print()
    print('=== 持有期间上涨率 ===')
    print(f'DXZE 持有期间上涨率: {ZE_持有上涨/ZE_持有总*100:.1f}%')
    print(f'DXZD 持有期间上涨率: {ZD_持有上涨/ZD_持有总*100:.1f}%')
    print()
    print('=== 最大回撤（每只股票的最大回撤，取平均） ===')
    print(f'DXZE 平均最大回撤: {sum(ZE_回撤)/len(ZE_回撤):.1f}%')
    print(f'DXZD 平均最大回撤: {sum(ZD_回撤)/len(ZD_回撤):.1f}%')
    # 回撤分布
    ZE_大回撤 = sum(1 for r in ZE_回撤 if r > 30)
    ZD_大回撤 = sum(1 for r in ZD_回撤 if r > 30)
    print(f'DXZE 最大回撤>30% 股票数: {ZE_大回撤} ({ZE_大回撤/len(ZE_回撤)*100:.1f}%)')
    print(f'DXZD 最大回撤>30% 股票数: {ZD_大回撤} ({ZD_大回撤/len(ZD_回撤)*100:.1f}%)')

if __name__ == '__main__':
    main()