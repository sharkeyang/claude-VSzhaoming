# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：DJA入口 用BSHA判断离顶程度
=============================================
用户观察：离顶时上破DJA是诱多。
用 BSHA（偏离DJA，列19）判断离顶程度，重新验证。
BSHA 大 = 偏离DJA多 = 接近顶部。

列映射：
  [8]  DXCD
  [9]  DXAB 护型
  [13] 日ZA
  [14] 日ZC
  [15] 日ZE
  [19] BSHA（偏离DJA）
  [26] 次日高幅
  [30] 上符串
  [62] DTZB
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_DJA入口BSHA.txt', 'w', encoding='utf-8')
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
i_bsha = 19
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

# 统计：DJA入口，按BSHA分档
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
                if len(row) <= max(i_cd, i_dxab, i_za, i_zc, i_ze, i_bsha, i_nhr, i_sfs, i_zb):
                    continue
                try:
                    cd = row[i_cd].strip()
                    dxab = row[i_dxab].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    bsha = float(row[i_bsha])
                    nhr = float(row[i_nhr])
                    sfs = row[i_sfs].strip()
                    zb = float(row[i_zb])
                except (ValueError, IndexError):
                    continue
                rows.append((cd, dxab, za, zc, ze, bsha, nhr, sfs, zb))

            n = len(rows)
            for i in range(n):
                cd, dxab, za, zc, ze, bsha, nhr, sfs, zb = rows[i]
                if zc <= 0:
                    continue
                # DJA入口：ZA由负转正
                if i > 0 and rows[i-1][2] <= 0 and za > 0:
                    # 按BSHA分档（偏离DJA程度）
                    if bsha >= 8:
                        stats['DJA入口_BSHA≥8(高离顶)'].append(nhr)
                    elif bsha >= 5:
                        stats['DJA入口_BSHA5-8'].append(nhr)
                    elif bsha >= 3:
                        stats['DJA入口_BSHA3-5'].append(nhr)
                    else:
                        stats['DJA入口_BSHA<3(低离顶)'].append(nhr)
                    # 上符串触顶
                    if 'A' in sfs:
                        stats['DJA入口_触顶A'].append(nhr)
                    else:
                        stats['DJA入口_非触顶'].append(nhr)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('DJA入口：按 BSHA（偏离DJA）分档（DXZC>0 区域）')
out('=' * 100)
out('')
out(f'| {"条件":<24s} | {"样本":>10s} | {"均次日高":>8s} | {"高≥3%":>7s} |')
out(f'|{"":->24s}|{"":->10s}:|{"":->8s}:|{"":->7s}:|')
for key in ['DJA入口_BSHA≥8(高离顶)', 'DJA入口_BSHA5-8', 'DJA入口_BSHA3-5', 'DJA入口_BSHA<3(低离顶)',
            'DJA入口_触顶A', 'DJA入口_非触顶']:
    vals = np.array(stats.get(key, []))
    if len(vals) < 100:
        continue
    out(f'| {key:<24s} | {len(vals):>10,d} | {np.mean(vals):>7.2f}% | {(vals>=3).sum()/len(vals)*100:>6.1f}% |')

out('')
out('=' * 100)
out('关键对比')
out('=' * 100)
out('')
if stats.get('DJA入口_BSHA≥8(高离顶)') and stats.get('DJA入口_BSHA<3(低离顶)'):
    a = np.array(stats['DJA入口_BSHA≥8(高离顶)'])
    b = np.array(stats['DJA入口_BSHA<3(低离顶)'])
    out(f'DJA入口 BSHA≥8(高离顶) vs BSHA<3(低离顶)：')
    out(f'  均次日高差: {np.mean(a)-np.mean(b):+.2f}pp')
    out(f'  高≥3%差: {(a>=3).sum()/len(a)*100 - (b>=3).sum()/len(b)*100:+.1f}pp')

OUTF.close()
print('Done')