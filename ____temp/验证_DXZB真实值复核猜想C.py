# -*- coding: utf-8 -*-
"""
复核猜想C：用真实 DXZB（DTZB[62]）验证转换态判别
====================================================
原结论（柱与DJA三态理论验证）：DXZB无直接列，用护级编码替代
  DXZA>0且DXZB>0：92.90%（222万样本）
  DXZA>0且DXZB<0：88.31%（118万样本）
  差4.59pp

现在 DTZB[62] 已导出（JZ收盘价 vs JB/EMA12 交叉天数），用真实值复核。
逻辑：转换态(上破DJA 1-2柱, 日ZA=1或2) 5日内仍升管(日ZA>0)概率，按真实DXZB分组。
"""
import csv, glob, io
from collections import defaultdict

out = io.open('____temp/_DXZB_猜想C复核.txt', 'w', encoding='utf-8')

stats = defaultdict(lambda: [0, 0])  # key -> [仍升管数, 总数]

files_done = 0
for fp in glob.glob('昭明算展/谕组日/*.csv'):
    try:
        with open(fp, encoding='gbk') as f:
            r = csv.reader(f)
            next(r)
            rows = list(r)
        for i in range(len(rows) - 5):
            row = rows[i]
            if len(row) < 65:
                continue
            try:
                za = int(row[13])     # 日ZA
                dxzb = int(row[62])   # DTZB（JZ vs JB交叉天数）
            except (ValueError, IndexError):
                continue
            if za in (1, 2):  # 转换态（上破DJA 1-2柱）
                # 5日内仍升管（日ZA>0）
                still_up = False
                for j in range(i + 1, min(i + 6, len(rows))):
                    if len(rows[j]) > 13:
                        try:
                            if int(rows[j][13]) > 0:
                                still_up = True
                                break
                        except (ValueError, IndexError):
                            continue
                if dxzb > 0:
                    key = 'DXZB>0'
                elif dxzb < 0:
                    key = 'DXZB<0'
                else:
                    key = 'DXZB=0'
                stats[key][1] += 1
                if still_up:
                    stats[key][0] += 1
    except Exception:
        pass
    files_done += 1

out.write(f'文件数: {files_done}\n')
out.write('\n转换态(日ZA=1或2) 5日内仍升管概率，按真实DXZB分组：\n')
out.write(f'{"分组":<10} {"样本":>10} {"5日仍升管":>10} {"概率":>8}\n')
out.write('-' * 45 + '\n')
for key in ['DXZB>0', 'DXZB<0', 'DXZB=0']:
    n = stats[key][1]
    if n:
        p = stats[key][0] / n * 100
        out.write(f'{key:<10} {n:>10,} {stats[key][0]:>10,} {p:>7.2f}%\n')

# 对比
if stats['DXZB>0'][1] and stats['DXZB<0'][1]:
    p_pos = stats['DXZB>0'][0] / stats['DXZB>0'][1] * 100
    p_neg = stats['DXZB<0'][0] / stats['DXZB<0'][1] * 100
    out.write(f'\nDXZB>0 vs DXZB<0 差: {p_pos - p_neg:+.2f}pp\n')

out.close()
print('done')
