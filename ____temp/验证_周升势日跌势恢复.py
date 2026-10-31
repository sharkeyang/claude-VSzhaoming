# -*- coding: utf-8 -*-
"""
验证：周类升势确定（周ZC>0 且非虎）时，日线跌势迹象（下破DXZC/DXAB/DXZB/DXZA）后，
是否会"尽快结束跌势、回到升势轨道"（遵从先周后日原则）。
对比：周类升势 vs 周类非升势，日线跌势的恢复速度（5日/10日回升率、5日/10日累计收益）。
"""
import os
import glob
import csv
from collections import defaultdict

COL_收 = 1
COL_日ZA = 13
COL_日ZC = 14
COL_DTZB = 66
COL_DTAB = 68
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

    # 统计: (周状态, 均线) -> [下破次数, 5日回升次数, 10日回升次数, 5日累计收益列表, 10日累计收益列表]
    stats = defaultdict(lambda: defaultdict(lambda: [0, 0, 0, [], []]))

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
        for i, row in enumerate(rows):
            try:
                收 = float(row[COL_收])
                日ZA = int(row[COL_日ZA])
                日ZC = int(row[COL_日ZC])
                DTZB = int(row[COL_DTZB])
                DTAB = int(row[COL_DTAB])
                周ZC = int(row[COL_周ZC])
            except (ValueError, IndexError):
                continue
            四波 = 提取四波(row[COL_周波型])
            周升势 = (周ZC > 0) and (四波 != '虎')
            周状态 = '周升势' if 周升势 else '周非升势'

            均线BT = {
                'DXZC': (日ZC, COL_日ZC),
                'DXAB': (DTAB, COL_DTAB),
                'DXZB': (DTZB, COL_DTZB),
                'DXZA': (日ZA, COL_日ZA),
            }
            for 名, (bt_val, col) in 均线BT.items():
                if i > 0:
                    try:
                        前bt = int(rows[i-1][col])
                    except (ValueError, IndexError):
                        前bt = None
                    if 前bt is not None and 前bt > 0 and bt_val < 0:
                        # 下破事件
                        stats[周状态][名][0] += 1
                        # 5日/10日回升（k日内任一日重上）
                        for k in (5, 10):
                            k_idx = 1 if k == 5 else 2
                            回升 = False
                            for j in range(i+1, min(i+k+1, len(rows))):
                                try:
                                    if int(rows[j][col]) > 0:
                                        回升 = True
                                        break
                                except (ValueError, IndexError):
                                    pass
                            if 回升:
                                stats[周状态][名][k_idx] += 1
                        # 5日累计收益（用收盘价）
                        if i + 5 < len(rows):
                            try:
                                五日收 = float(rows[i+5][COL_收])
                                stats[周状态][名][3].append((五日收 - 收) / 收 * 100)
                            except (ValueError, IndexError):
                                pass
                        # 10日累计收益
                        if i + 10 < len(rows):
                            try:
                                十日收 = float(rows[i+10][COL_收])
                                stats[周状态][名][4].append((十日收 - 收) / 收 * 100)
                            except (ValueError, IndexError):
                                pass

    print('=== 周类升势确定时，日线跌势迹象后的恢复 ===')
    print(f'{"均线":<6}{"周状态":<10}{"下破次数":>8}{"5日回升率":>10}{"10日回升率":>10}{"5日累计":>10}{"10日累计":>10}')
    for 名 in ('DXZC', 'DXAB', 'DXZB', 'DXZA'):
        for 周状态 in ('周升势', '周非升势'):
            if 名 in stats[周状态]:
                破, 回升5, 回升10, 五日, 十日 = stats[周状态][名]
                if 破 == 0:
                    continue
                回升率5 = 回升5/破*100
                回升率10 = 回升10/破*100
                五日均 = sum(五日)/len(五日) if 五日 else 0
                十日均 = sum(十日)/len(十日) if 十日 else 0
                print(f'{名:<6}{周状态:<10}{破:>8}{回升率5:>9.1f}%{回升率10:>9.1f}%{五日均:>9.3f}%{十日均:>9.3f}%')

if __name__ == '__main__':
    main()