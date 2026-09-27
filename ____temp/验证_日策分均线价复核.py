# -*- coding: utf-8 -*-
"""
复核：第三章操盘条件子集内日策分好/坏增量区分度（均线价进出）
====================================================
原结论（MC3.3 §3.5.4）：用收盘价进出，日策分好/坏增量区分度很弱（<0.2pp）。
数据局限：收盘价（复权价，相邻日期可能有复权跳变）≠ 均线价进出口径。
本次用均线价进出（前一日收盘价≈均线价）复核，谕组日CSV已含日策分好/坏列。

逻辑：
  1. 筛选第三章操盘条件子集：日ZC>0 且 DXAB首字符为甲乙己
  2. 按日策分好/坏分组（好类=日策分好[52]首字符，坏类=日策分坏[51]首字符）
  3. 持有10天收益，均线价进出：入场=前一日收盘价，出场=第10天前一日收盘价
  4. 对比各组合的涨率/均收益，判断增量区分度
"""
import csv, glob, io
from collections import defaultdict

out = io.open('____temp/_日策分均线价复核.txt', 'w', encoding='utf-8')

# 统计: key=(好类,坏类) -> [涨数, 总数, 收益和]
stats = defaultdict(lambda: [0, 0, 0.0])
全量 = [0, 0, 0.0]  # 第三章条件全量

files_done = 0
for fp in glob.glob('昭明算展/谕组日/*.csv'):
    try:
        with open(fp, encoding='gbk') as f:
            r = csv.reader(f)
            next(r)
            rows = list(r)
        for i in range(len(rows) - 10):
            row = rows[i]
            if len(row) < 65:
                continue
            try:
                zc = float(row[14])        # 日ZC
                dxab = row[9].strip()      # DXAB
                close = float(row[1])      # 收
                cehao = row[52].strip()    # 日策分好
                cehuai = row[51].strip()   # 日策分坏
            except (ValueError, IndexError):
                continue
            # 第三章条件：日ZC>0 且 DXAB首字符为甲乙己
            if zc <= 0:
                continue
            if not dxab or dxab[0] not in ('a', 'b', 'r'):
                continue
            # 均线价进出：入场=前一日收盘价，出场=第10天前一日收盘价
            entry = float(rows[i - 1][1]) if i >= 1 else close
            exit_price = float(rows[i + 9][1])
            ret = (exit_price - entry) / entry * 100 if entry else 0
            # 分组
            hao = cehao[0] if cehao else '_'
            huai = cehuai[0] if cehuai else '_'
            key = (hao, huai)
            stats[key][1] += 1
            stats[key][2] += ret
            if ret > 0:
                stats[key][0] += 1
            # 全量
            全量[1] += 1
            全量[2] += ret
            if ret > 0:
                全量[0] += 1
    except Exception:
        pass
    files_done += 1

out.write(f'文件数: {files_done}\n')
out.write('\n第三章操盘条件子集（日ZC>0+甲乙己）持有10天收益，均线价进出：\n')
out.write(f'{"好类":<6} {"坏类":<6} {"样本":>12} {"涨率%":>8} {"均收益%":>10}\n')
out.write('-' * 50 + '\n')
for key in [('G', '_'), ('_', 'W'), ('G', 'W')]:
    n = stats[key][1]
    if n:
        p = stats[key][0] / n * 100
        avg = stats[key][2] / n
        out.write(f'{key[0]:<6} {key[1]:<6} {n:>12,} {p:>7.2f} {avg:>9.3f}\n')

# 全量
if 全量[1]:
    p = 全量[0] / 全量[1] * 100
    avg = 全量[2] / 全量[1]
    out.write(f'{"全量":<6} {"":<6} {全量[1]:>12,} {p:>7.2f} {avg:>9.3f}\n')

# 对比
if stats[('G', '_')][1] and 全量[1]:
    diff = stats[('G', '_')][2] / stats[('G', '_')][1] - 全量[2] / 全量[1]
    out.write(f'\nG_ vs 全量 均收益差: {diff:+.3f}pp\n')

out.close()
print('done')
