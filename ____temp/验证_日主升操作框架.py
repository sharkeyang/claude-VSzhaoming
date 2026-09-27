# -*- coding: utf-8 -*-
"""
深度验证（2026-09-26）：日主升区域操作框架
=========================================
用户主张：
1. (DXAB>0 且 DXZB>0) 是升势——不会导致 DXAB 负交
2. 三类入口：DJC入口/DJB入口/DJA入口
3. 珍惜 DXZC>0 每个阴柱
4. 甲乙己→丙丁戊 是否该退出？DXAB正交后第一次下跌DJB是否反弹？
5. DJA之下DJB之上：下破DJA两柱以上是否继续下跌？

列映射（元数据_vba数据映射_日类.md）：
  [8]  DXCD
  [9]  DXAB 护型
  [13] 日ZA
  [14] 日ZC
  [15] 日ZE
  [26] 次日高幅
  [62] DTZB
  [63] DTZD
  [64] DTAB
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_日主升操作框架.txt', 'w', encoding='utf-8')
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
i_zb = 62
i_zd = 63
i_ab = 64

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

# 统计容器
# 1. 甲乙己→丙丁戊 后的次日高幅（是否延续下跌）
# 2. DXAB正交后第一次下跌DJB 是否反弹
# 3. 三类入口获利性
# 4. 下破DJA两柱以上 是否继续下跌

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
                if len(row) <= max(i_cd, i_dxab, i_za, i_zc, i_ze, i_nhr, i_zb, i_zd, i_ab):
                    continue
                try:
                    cd = row[i_cd].strip()
                    dxab = row[i_dxab].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    nhr = float(row[i_nhr])
                    zb = float(row[i_zb])
                    zd = float(row[i_zd])
                    ab = float(row[i_ab])
                except (ValueError, IndexError):
                    continue
                rows.append((cd, dxab, za, zc, ze, nhr, zb, zd, ab))

            n = len(rows)
            for i in range(n):
                cd, dxab, za, zc, ze, nhr, zb, zd, ab = rows[i]
                hx = parse_hx(dxab, za)
                # 只在 DXZC>0 区域（主升）
                if zc <= 0:
                    continue
                # 1. 甲乙己→丙丁戊 后的次日高幅
                if i+1 < n:
                    next_hx = parse_hx(rows[i+1][1], rows[i+1][2])
                    next_nhr = rows[i+1][5]
                    # 甲乙己 → 丙丁戊（转坏）
                    if hx in ('甲', '乙(ZA>0)', '己') and next_hx in ('丙', '丁', '戊(ZA≤0)'):
                        stats['甲乙己→丙丁戊'].append(next_nhr)
                    # 甲乙己 维持（对照）
                    if hx in ('甲', '乙(ZA>0)', '己') and next_hx in ('甲', '乙(ZA>0)', '己'):
                        stats['甲乙己→甲乙己'].append(next_nhr)
                    # 丙丁戊 → 甲乙己（转好）
                    if hx in ('丙', '丁', '戊(ZA≤0)') and next_hx in ('甲', '乙(ZA>0)', '己'):
                        stats['丙丁戊→甲乙己'].append(next_nhr)
                    # 丙丁戊 维持（对照）
                    if hx in ('丙', '丁', '戊(ZA≤0)') and next_hx in ('丙', '丁', '戊(ZA≤0)'):
                        stats['丙丁戊→丙丁戊'].append(next_nhr)

                # 2. DXAB正交后第一次下跌DJB 是否反弹
                # DXAB正交 = 甲乙己；第一次下跌DJB = 转丙丁戊
                # 转丙丁戊后，看后续是否反弹回甲乙己
                if hx in ('甲', '乙(ZA>0)', '己') and i+1 < n:
                    next_hx = parse_hx(rows[i+1][1], rows[i+1][2])
                    if next_hx in ('丙', '丁', '戊(ZA≤0)'):
                        # 转坏后，扫描后续是否反弹回甲乙己
                        stats['正交后转坏_总数'].append(1)
                        rebound = False
                        for j in range(i+2, min(i+11, n)):
                            jhx = parse_hx(rows[j][1], rows[j][2])
                            if jhx in ('甲', '乙(ZA>0)', '己'):
                                rebound = True
                                break
                        stats['正交后转坏_反弹'].append(1 if rebound else 0)

                # 3. 三类入口获利性
                # DJC入口：ZC由负转正当天（初/储）
                if i > 0 and rows[i-1][3] <= 0 and zc > 0:
                    stats['DJC入口(ZC转正)'].append(nhr)
                # DJB入口：ZB由负转正（上破DJB）
                if i > 0 and rows[i-1][6] <= 0 and zb > 0:
                    stats['DJB入口(ZB转正)'].append(nhr)
                # DJA入口：ZA由负转正（上破DJA）
                if i > 0 and rows[i-1][2] <= 0 and za > 0:
                    stats['DJA入口(ZA转正)'].append(nhr)

                # 4. 下破DJA两柱以上 是否继续下跌
                # 下破DJA = ZA<0；两柱以上 = 连续ZA<0
                if za < 0 and i > 0 and rows[i-1][2] < 0:
                    stats['下破DJA两柱'].append(nhr)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('1. 甲乙己→丙丁戊 后的次日高幅（是否延续下跌？）')
out('=' * 100)
out('')
out(f'| {"转移":<16s} | {"样本":>10s} | {"均次日高":>8s} | {"高≥3%":>7s} |')
out(f'|{"":->16s}|{"":->10s}:|{"":->8s}:|{"":->7s}:|')
for key in ['甲乙己→丙丁戊', '甲乙己→甲乙己', '丙丁戊→甲乙己', '丙丁戊→丙丁戊']:
    vals = np.array(stats.get(key, []))
    if len(vals) < 100:
        continue
    out(f'| {key:<16s} | {len(vals):>10,d} | {np.mean(vals):>7.2f}% | {(vals>=3).sum()/len(vals)*100:>6.1f}% |')

out('')
out('=' * 100)
out('2. DXAB正交后第一次下跌DJB 是否反弹？')
out('=' * 100)
out('')
if stats.get('正交后转坏_总数'):
    total = len(stats['正交后转坏_总数'])
    rebound = sum(stats['正交后转坏_反弹'])
    out(f'正交后转坏总数: {total:,}')
    out(f'  10日内反弹回甲乙己: {rebound:,} = {rebound/total*100:.1f}%')
    out(f'  未反弹: {total-rebound:,} = {(total-rebound)/total*100:.1f}%')

out('')
out('=' * 100)
out('3. 三类入口获利性（DXZC>0 区域）')
out('=' * 100)
out('')
out(f'| {"入口":<20s} | {"样本":>10s} | {"均次日高":>8s} | {"高≥3%":>7s} |')
out(f'|{"":->20s}|{"":->10s}:|{"":->8s}:|{"":->7s}:|')
for key in ['DJC入口(ZC转正)', 'DJB入口(ZB转正)', 'DJA入口(ZA转正)']:
    vals = np.array(stats.get(key, []))
    if len(vals) < 100:
        continue
    out(f'| {key:<20s} | {len(vals):>10,d} | {np.mean(vals):>7.2f}% | {(vals>=3).sum()/len(vals)*100:>6.1f}% |')

out('')
out('=' * 100)
out('4. 下破DJA两柱以上 是否继续下跌？')
out('=' * 100)
out('')
vals = np.array(stats.get('下破DJA两柱', []))
if len(vals) >= 100:
    out(f'下破DJA两柱以上: 样本 {len(vals):,}，均次日高 {np.mean(vals):.2f}%，高≥3% {(vals>=3).sum()/len(vals)*100:.1f}%')

OUTF.close()
print('Done')