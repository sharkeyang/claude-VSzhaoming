# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：镜面对称的"复发"分析
=====================================
DXCD 正交（多头）时：下破低级均线 → 能否"恢复"（重新站上）
DXCD 负交（空头）时：低级均线正交 → 能否"复发"（重新转下跌）

镜面对称：
| DXCD正交 | 下破低级均线(劫) | 恢复概率(重新站上) |
| DXCD负交 | 低级均线正交 | 复发概率(重新跌破) |

列映射：
  [8]  DXCD
  [13] 日ZA
  [14] 日ZC
  [15] 日ZE
  [62] DTZB
  [63] DTZD
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_复发镜面.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_cd = 8
i_za = 13
i_zc = 14
i_ze = 15
i_zb = 62
i_zd = 63

# 统计：DXCD负交时，低级均线正交后，未来N日复发（重新跌破）概率
# 复发 = 重新跌破对应均线
stats = defaultdict(lambda: {'n': 0, 'r5': 0, 'r10': 0, 'r20': 0})

files_done = 0
for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        cidl = fname.replace('谕组日_', '').replace('.csv', '')
        board = board_map.get(cidl, '')
        if board not in 高波池板块:
            continue
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            header = next(r)
            rows = []
            for row in r:
                if len(row) <= max(i_cd, i_za, i_zc, i_ze, i_zb, i_zd):
                    continue
                try:
                    cd = row[i_cd].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    zb = float(row[i_zb])
                    zd = float(row[i_zd])
                except (ValueError, IndexError):
                    continue
                rows.append((cd, za, zc, ze, zb, zd))

            n = len(rows)
            for i in range(n):
                cd, za, zc, ze, zb, zd = rows[i]
                # DXCD 负交（忠/忐/忑）
                if cd not in ('忠', '忐', '忑'):
                    continue
                # 低级均线正交：ZC>0（忠）、ZD>0（忐）
                # 复发 = 未来N日重新跌破（ZC<0 或 ZD<0）
                if zc > 0:
                    key = '忠(ZC>0但DXCD负交)'
                    stats[key]['n'] += 1
                    for horizon, hkey in [(5, 'r5'), (10, 'r10'), (20, 'r20')]:
                        rec = False
                        for j in range(i+1, min(i+horizon+1, n)):
                            if rows[j][2] < 0:  # ZC<0 复发下跌
                                rec = True
                                break
                        stats[key][hkey] += 1 if rec else 0
                if zd > 0:
                    key = '忐(ZD>0但DXCD负交)'
                    stats[key]['n'] += 1
                    for horizon, hkey in [(5, 'r5'), (10, 'r10'), (20, 'r20')]:
                        rec = False
                        for j in range(i+1, min(i+horizon+1, n)):
                            if rows[j][5] < 0:  # ZD<0 复发下跌
                                rec = True
                                break
                        stats[key][hkey] += 1 if rec else 0
                # 低级均线正交：ZA>0（忠/忐/忑 内）
                if za > 0:
                    key = '低级均线正交(ZA>0但DXCD负交)'
                    stats[key]['n'] += 1
                    for horizon, hkey in [(5, 'r5'), (10, 'r10'), (20, 'r20')]:
                        rec = False
                        for j in range(i+1, min(i+horizon+1, n)):
                            if rows[j][1] < 0:  # ZA<0 复发下跌
                                rec = True
                                break
                        stats[key][hkey] += 1 if rec else 0

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('镜面对称：DXCD 负交时，低级均线正交后的"复发"概率')
out('=' * 100)
out('')
out('复发 = 低级均线正交后，未来N日重新跌破（转下跌）')
out('')
out(f'| {"条件":<30s} | {"样本":>8s} | {"5日复发":>8s} | {"10日复发":>9s} | {"20日复发":>9s} |')
out(f'|{"":->30s}|{"":->8s}:|{"":->8s}:|{"":->9s}:|{"":->9s}:|')
for key in ['忠(ZC>0但DXCD负交)', '忐(ZD>0但DXCD负交)', '低级均线正交(ZA>0但DXCD负交)']:
    s = stats.get(key)
    if not s or s['n'] < 100:
        continue
    out(f'| {key:<30s} | {s["n"]:>8,d} | {s["r5"]/s["n"]*100:>7.1f}% | {s["r10"]/s["n"]*100:>8.1f}% | {s["r20"]/s["n"]*100:>8.1f}% |')

out('')
out('=' * 100)
out('镜面对称对比（恢复 vs 复发）')
out('=' * 100)
out('')
out('DXCD正交时下破均线 → 恢复概率（重新站上）：DJA 98% / DJB 88% / DJC 77.5% / DJD 62.3%')
out('DXCD负交时均线正交 → 复发概率（重新跌破）：见上表')
out('')

OUTF.close()
print('Done')