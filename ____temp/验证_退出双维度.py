# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：退出机会 长期+短期 双维度评估，区分情况
=========================================================
用户框架：
- 长期：下破某均线后，恢复概率低 = 长期退出好选择
- 短期：下破后次日高幅低 = 短期退出好选择
- 区分情况：首下破DJA 也分「前柱升连触顶」（好介入）vs「离顶跌连」（好退出）

列映射：
  [8]  DXCD
  [9]  DXAB 护型
  [10] 柱排
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

OUTF = io.open('____temp/_验证_退出双维度.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_cd = 8
i_dxab = 9
i_zp = 10
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

def is_触顶(sfs):
    return sfs and sfs.rstrip().endswith('A')

def is_离顶(sfs):
    return sfs and not sfs.rstrip().endswith('A')

def is_升连(zp):
    return zp and zp.startswith('升')

def is_跌连(zp):
    return zp and zp.startswith('跌')

# 统计：每个条件 → {次日高幅列表, 未来N日恢复概率}
# 恢复 = 重新站上DJA（ZA>0）
stats = defaultdict(lambda: {'nhr': [], 'recover5': [], 'recover10': [], 'recover20': []})

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
                if len(row) <= max(i_cd, i_dxab, i_zp, i_za, i_zc, i_ze, i_nhr, i_sfs, i_zb):
                    continue
                try:
                    cd = row[i_cd].strip()
                    dxab = row[i_dxab].strip()
                    zp = row[i_zp].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    nhr = float(row[i_nhr])
                    sfs = row[i_sfs].strip()
                    zb = float(row[i_zb])
                except (ValueError, IndexError):
                    continue
                rows.append((cd, dxab, zp, za, zc, ze, nhr, sfs, zb))

            n = len(rows)
            for i in range(n):
                cd, dxab, zp, za, zc, ze, nhr, sfs, zb = rows[i]
                hx = parse_hx(dxab, za)
                if i == 0:
                    continue
                prev = rows[i-1]
                prev_hx = parse_hx(prev[1], prev[2])
                prev_za = prev[3]
                prev_zp = prev[2]
                prev_sfs = prev[7]

                # === 首下破 DJA（前一日 ZA>0，今日 ZA<0）===
                if prev_za > 0 and za < 0:
                    # 区分前柱条件
                    if is_升连(prev_zp) and is_触顶(prev_sfs):
                        key = '首下破DJA_前柱升连触顶'
                    elif is_离顶(prev_sfs) and is_跌连(prev_zp):
                        key = '首下破DJA_前柱离顶跌连'
                    elif is_升连(prev_zp):
                        key = '首下破DJA_前柱升连'
                    elif is_跌连(prev_zp):
                        key = '首下破DJA_前柱跌连'
                    else:
                        key = '首下破DJA_其他'
                    stats[key]['nhr'].append(nhr)
                    # 长期恢复：未来5/10/20日重新站上DJA
                    for horizon, hkey in [(5, 'recover5'), (10, 'recover10'), (20, 'recover20')]:
                        recovered = False
                        for j in range(i+1, min(i+horizon+1, n)):
                            if rows[j][3] > 0:
                                recovered = True
                                break
                        stats[key][hkey].append(1 if recovered else 0)

                # === 下破 DJB（甲乙己→丙丁戊）===
                if is_甲乙己(prev_hx) and is_丙丁戊(hx):
                    # 区分首次/非首次（前一段是否刚正交）
                    # 简化：看前一日是否刚转甲乙己（前前日非甲乙己）
                    if i >= 2:
                        prev2_hx = parse_hx(rows[i-2][1], rows[i-2][2])
                        if not is_甲乙己(prev2_hx):
                            key = '下破DJB_首次(刚正交后)'
                        else:
                            key = '下破DJB_非首次'
                    else:
                        key = '下破DJB_非首次'
                    stats[key]['nhr'].append(nhr)
                    for horizon, hkey in [(5, 'recover5'), (10, 'recover10'), (20, 'recover20')]:
                        recovered = False
                        for j in range(i+1, min(i+horizon+1, n)):
                            if is_甲乙己(parse_hx(rows[j][1], rows[j][2])):
                                recovered = True
                                break
                        stats[key][hkey].append(1 if recovered else 0)

                # === 下破 DJD（DXCD=下）===
                if cd == '下':
                    stats['下破DJD(DXCD=下)']['nhr'].append(nhr)
                    for horizon, hkey in [(5, 'recover5'), (10, 'recover10'), (20, 'recover20')]:
                        recovered = False
                        for j in range(i+1, min(i+horizon+1, n)):
                            if rows[j][0] in ('上', '中', '忐'):
                                recovered = True
                                break
                        stats['下破DJD(DXCD=下)'][hkey].append(1 if recovered else 0)

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('退出机会 长期+短期 双维度评估（区分情况）')
out('=' * 100)
out('')
out('短期 = 次日高≥3%；长期 = 未来N日恢复概率（重新站上对应均线）')
out('')
out(f'| {"条件":<28s} | {"样本":>8s} | {"次日高≥3%":>9s} | {"5日恢复":>8s} | {"10日恢复":>9s} | {"20日恢复":>9s} |')
out(f'|{"":->28s}|{"":->8s}:|{"":->9s}:|{"":->8s}:|{"":->9s}:|{"":->9s}:|')
for key in ['首下破DJA_前柱升连触顶', '首下破DJA_前柱离顶跌连', '首下破DJA_前柱升连', '首下破DJA_前柱跌连', '首下破DJA_其他',
            '下破DJB_首次(刚正交后)', '下破DJB_非首次', '下破DJD(DXCD=下)']:
    s = stats.get(key)
    if not s or len(s['nhr']) < 100:
        continue
    nhr = np.array(s['nhr'])
    p3 = (nhr>=3).sum()/len(nhr)*100
    r5 = np.mean(s['recover5'])*100
    r10 = np.mean(s['recover10'])*100
    r20 = np.mean(s['recover20'])*100
    out(f'| {key:<28s} | {len(nhr):>8,d} | {p3:>8.1f}% | {r5:>7.1f}% | {r10:>8.1f}% | {r20:>8.1f}% |')

out('')
out('=' * 100)
out('评分（长期+短期综合）')
out('=' * 100)
out('')
out('退出好选择 = 短期次日高≥3%低 + 长期恢复概率低')
out('介入好选择 = 短期次日高≥3%高 + 长期恢复概率高')
out('')

OUTF.close()
print('Done')