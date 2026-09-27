# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：状态机帐篷模式 + 四类机会（真正的曾触哼判定）
=============================================================
状态机（§6.7.2.1）：由非甲乙己变为甲乙己后，只要未触哼就不入升管；
触哼后入升管；保持甲乙己就在升管中；变非甲乙己出升管。

帐篷 = 在升管中（甲乙己+曾触哼），回落DJA后救回。

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

OUTF = io.open('____temp/_验证_帐篷状态机.txt', 'w', encoding='utf-8')
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
            # 状态机：跟踪升管状态
            in_升管 = False  # 是否在升管中（甲乙己+曾触哼）
            for i in range(n):
                cd, dxab, za, zc, ze, nhr, sfs, zb = rows[i]
                hx = parse_hx(dxab, za)
                cur_甲乙己 = is_甲乙己(hx)
                cur_触哼 = is_触哼(sfs)

                # 状态机更新
                if not cur_甲乙己:
                    in_升管 = False  # 变非甲乙己出升管
                else:
                    if cur_触哼:
                        in_升管 = True  # 触哼入升管
                    # 保持甲乙己就在升管中（in_升管 保持）

                if zc <= 0:
                    continue
                if not in_升管:
                    continue

                # 在升管中，识别四类机会
                # (1) 连续触哼
                if cur_触哼:
                    stats['连续触哼'].append(nhr)
                # (2) 等3帐篷：DJA之上阴柱（ZA>0 但非触顶）
                if za > 0 and not (sfs and sfs.rstrip().endswith('A')):
                    stats['等3帐篷(DJA之上非触顶)'].append(nhr)
                # (3) 等2帐篷：回归DJA（ZA=2）
                if za == 2:
                    stats['等2帐篷(ZA=2)'].append(nhr)
                # (4) 等5帐篷：下破DJA 1-3柱后站上
                if i > 0 and rows[i-1][2] < 0 and za > 0:
                    j = i - 1
                    down_days = 0
                    while j >= 0 and rows[j][2] < 0:
                        down_days += 1
                        j -= 1
                    if 1 <= down_days <= 3:
                        stats['等5帐篷(下破1-3柱后站上)'].append(nhr)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('四类主要机会（状态机：升管=甲乙己+曾触哼，DXZC>0）')
out('=' * 100)
out('')
out(f'| {"机会":<28s} | {"样本":>10s} | {"均次日高":>8s} | {"高≥3%":>7s} |')
out(f'|{"":->28s}|{"":->10s}:|{"":->8s}:|{"":->7s}:|')
for key in ['连续触哼', '等3帐篷(DJA之上非触顶)', '等2帐篷(ZA=2)', '等5帐篷(下破1-3柱后站上)']:
    vals = np.array(stats.get(key, []))
    if len(vals) < 100:
        continue
    out(f'| {key:<28s} | {len(vals):>10,d} | {np.mean(vals):>7.2f}% | {(vals>=3).sum()/len(vals)*100:>6.1f}% |')

out('')
out('=' * 100)
out('关键对比')
out('=' * 100)
out('')
if stats.get('等5帐篷(下破1-3柱后站上)'):
    a = np.array(stats['等5帐篷(下破1-3柱后站上)'])
    out(f'等5帐篷(状态机): 高≥3% {(a>=3).sum()/len(a)*100:.1f}%')
    out(f'  对比等5整体(首下破) 20.78%（§6.8.4）')

OUTF.close()
print('Done')