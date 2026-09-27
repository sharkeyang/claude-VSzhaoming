# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：退出机会分层（头脑风暴）
=========================================
找出哪些点是退出的好机会，分层次，用数据支持。

候选退出点：
A. 下破 DJB（甲乙己→丙丁戊）——后续走势
B. 下破 DJA 单柱 vs 两柱 vs 三柱——后续走势
C. 下破 DJD（DXCD=下）——后续走势
D. 已冲高/离顶后连阴——后续走势

列映射：
  [8]  DXCD
  [9]  DXAB 护型
  [13] 日ZA
  [14] 日ZC
  [15] 日ZE
  [26] 次日高幅
  [30] 上符串
  [62] DTZB
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_退出机会分层.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_cd = 8
i_dxab = 9
i_za = 13
i_zc = 14
i_ze = 15
i_nhr = 26
i_sfs = 30
i_zb = 62

HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}

def parse_hx(dxab, za):
    if not dxab or len(dxab) < 1:
        return None
    c = dxab[0]
    if c == 'a':
        return '甲'
    if c == 'b':
        return '乙(ZA>0)' if za > 0 else '乙(ZA≤0)'
    if c == 'c':
        return '丙'
    if c == 'z':
        return '丁'
    if c == 'y':
        return '戊(ZA>0)' if za > 0 else '戊(ZA≤0)'
    if c == 'r':
        return '己'
    return None

def is_甲乙己(hx):
    return hx in ('甲', '乙(ZA>0)', '己')

def is_丙丁戊(hx):
    return hx in ('丙', '丁', '戊(ZA≤0)')

def is_触哼(sfs):
    return sfs and 'B' in sfs

# 统计
stats = defaultdict(list)

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
                if len(row) <= max(i_cd, i_dxab, i_za, i_zc, i_ze, i_nhr, i_sfs, i_zb):
                    continue
                try:
                    cd = row[i_cd].strip()
                    dxab = row[i_dxab].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    nhr = float(row[i_nhr])
                    sfs = row[i_sfs].strip()
                    zb = float(row[i_zb])
                except (ValueError, IndexError):
                    continue
                rows.append((cd, dxab, za, zc, ze, nhr, sfs, zb))

            n = len(rows)
            for i in range(n):
                cd, dxab, za, zc, ze, nhr, sfs, zb = rows[i]
                hx = parse_hx(dxab, za)
                # A. 下破 DJB（甲乙己→丙丁戊）
                if i > 0:
                    prev_hx = parse_hx(rows[i-1][1], rows[i-1][2])
                    if is_甲乙己(prev_hx) and is_丙丁戊(hx):
                        stats['A_下破DJB(甲乙己→丙丁戊)'].append(nhr)
                # B. 下破 DJA 单柱/两柱/三柱
                if za < 0:
                    j = i
                    down_days = 0
                    while j >= 0 and rows[j][2] < 0:
                        down_days += 1
                        j -= 1
                    if down_days == 1:
                        stats['B_下破DJA单柱'].append(nhr)
                    elif down_days == 2:
                        stats['B_下破DJA两柱'].append(nhr)
                    elif down_days >= 3:
                        stats['B_下破DJA三柱+'].append(nhr)
                # C. 下破 DJD（DXCD=下）
                if cd == '下':
                    stats['C_下破DJD(DXCD=下)'].append(nhr)
                # D. 已冲高/离顶后连阴
                # 已冲高 = 上符串含A（触顶）；连阴 = 阴柱
                # 简化：触顶 + 非升排（可能连阴）
                if sfs and sfs.rstrip().endswith('A') and not is_甲乙己(hx):
                    stats['D_触顶后非甲乙己'].append(nhr)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('退出机会分层（次日高幅）')
out('=' * 100)
out('')
out(f'| {"退出点":<30s} | {"样本":>10s} | {"均次日高":>8s} | {"高≥3%":>7s} |')
out(f'|{"":->30s}|{"":->10s}:|{"":->8s}:|{"":->7s}:|')
for key in ['A_下破DJB(甲乙己→丙丁戊)', 'B_下破DJA单柱', 'B_下破DJA两柱', 'B_下破DJA三柱+',
            'C_下破DJD(DXCD=下)', 'D_触顶后非甲乙己']:
    vals = np.array(stats.get(key, []))
    if len(vals) < 100:
        continue
    out(f'| {key:<30s} | {len(vals):>10,d} | {np.mean(vals):>7.2f}% | {(vals>=3).sum()/len(vals)*100:>6.1f}% |')

out('')
out('=' * 100)
out('关键对比（基线 23.6%）')
out('=' * 100)
out('')
for key in ['A_下破DJB(甲乙己→丙丁戊)', 'B_下破DJA单柱', 'B_下破DJA两柱', 'B_下破DJA三柱+',
            'C_下破DJD(DXCD=下)', 'D_触顶后非甲乙己']:
    vals = np.array(stats.get(key, []))
    if len(vals) < 100:
        continue
    p3 = (vals>=3).sum()/len(vals)*100
    diff = p3 - 23.6
    out(f'{key}: 高≥3% {p3:.1f}% (vs 基线23.6% {diff:+.1f}pp)')

OUTF.close()
print('Done')