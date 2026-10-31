# -*- coding: utf-8 -*-
"""
分析周A趋是否为右侧交易策略：
介入=WXZC由负转正+WXAB已正交；退出=WXZC由正转负 或 (WXZC>0且虎)。
分析：①介入时价格相对WJC已涨多少 ②退出时价格相对WJC已跌多少 ③介入后/退出后的收益。
"""
import os
import glob
import csv
from collections import defaultdict

COL_周涨 = 1
COL_HR = 3
COL_波型 = 7
COL_ZB周 = 17
COL_ZC周 = 18
COL_AB周 = 22

def 提取四波(波型):
    if '虎' in 波型:
        return 波型[4] if len(波型) >= 5 else ''
    return 波型[2] if len(波型) >= 3 else ''

def main():
    data_dir = r'昭明算展\谕组周'
    files = glob.glob(os.path.join(data_dir, '谕组周_*.csv'))
    print(f'文件数: {len(files)}')

    # 介入事件统计
    介入统计 = defaultdict(list)  # 口径 -> [值列表]
    # 退出事件统计
    退出统计 = defaultdict(list)
    # 介入后收益（持有到退出）
    介入后收益 = []
    # 退出后收益（退出后N周）
    退出后收益 = defaultdict(list)

    n_介入 = 0
    n_退出 = 0

    for f in files:
        rows = []
        with open(f, 'r', encoding='gbk', errors='replace') as fh:
            rd = csv.reader(fh)
            next(rd, None)
            for row in rd:
                if len(row) > COL_AB周:
                    rows.append(row)
        if not rows:
            continue

        持有 = False
        前ZC = None
        前AB = None
        介入周涨 = None  # 介入当周涨幅

        for i, row in enumerate(rows):
            try:
                周涨 = float(row[COL_周涨])
                zc = int(row[COL_ZC周])
                ab = int(row[COL_AB周])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[COL_波型])

            # 退出检测（持有中）
            if 持有:
                if zc < 0 or (zc > 0 and 四波 == '虎'):
                    # 退出：记录退出当周涨幅
                    退出统计['退出当周涨'].append(周涨)
                    # 退出后收益（1/2/4周）
                    for k in (1, 2, 4):
                        if i + k < len(rows):
                            try:
                                后涨 = float(rows[i+k][COL_周涨])
                                退出后收益[k].append(后涨)
                            except (ValueError, IndexError):
                                pass
                    # 介入后收益（从介入到退出前一周的累计）
                    if 介入周涨 is not None:
                        介入后收益.append(介入周涨)
                    持有 = False
                    n_退出 += 1

            # 介入检测（空仓中）
            if not 持有:
                # WXZC由负转正 且 WXAB已正交
                zc转正 = (前ZC is not None and 前ZC < 0 and zc > 0)
                ab正交 = (ab > 0)
                if zc转正 and ab正交:
                    持有 = True
                    介入周涨 = 周涨
                    介入统计['介入当周涨'].append(周涨)
                    # 介入时价格相对WJC位置（用ZC值近似，ZC>0表示站上WJC）
                    介入统计['介入时ZC'].append(zc)
                    n_介入 += 1

            前ZC = zc
            前AB = ab

    print(f'介入事件数: {n_介入}, 退出事件数: {n_退出}')
    print()
    print('=== 介入特征（右侧？） ===')
    if 介入统计['介入当周涨']:
        avg = sum(介入统计['介入当周涨'])/len(介入统计['介入当周涨'])
        print(f'介入当周平均涨幅: {avg:.3f}%')
        # 介入当周涨幅分布
        正 = sum(1 for x in 介入统计['介入当周涨'] if x > 0)
        print(f'介入当周上涨比例: {正}/{len(介入统计["介入当周涨"])} = {正/len(介入统计["介入当周涨"])*100:.1f}%')
    if 介入统计['介入时ZC']:
        avg_zc = sum(介入统计['介入时ZC'])/len(介入统计['介入时ZC'])
        print(f'介入时平均ZC值(站上WJC天数): {avg_zc:.1f}')
    print()
    print('=== 退出特征（右侧？） ===')
    if 退出统计['退出当周涨']:
        avg = sum(退出统计['退出当周涨'])/len(退出统计['退出当周涨'])
        print(f'退出当周平均涨幅: {avg:.3f}%')
        负 = sum(1 for x in 退出统计['退出当周涨'] if x < 0)
        print(f'退出当周下跌比例: {负}/{len(退出统计["退出当周涨"])} = {负/len(退出统计["退出当周涨"])*100:.1f}%')
    print()
    print('=== 介入后收益（持有到退出） ===')
    if 介入后收益:
        avg = sum(介入后收益)/len(介入后收益)
        print(f'介入当周平均涨幅: {avg:.3f}%')
    print()
    print('=== 退出后收益（退出后N周） ===')
    for k in (1, 2, 4):
        if 退出后收益[k]:
            avg = sum(退出后收益[k])/len(退出后收益[k])
            print(f'退出后{k}周平均涨幅: {avg:.3f}%')

if __name__ == '__main__':
    main()