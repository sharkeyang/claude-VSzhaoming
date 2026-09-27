# -*- coding: utf-8 -*-
"""
综合验证（2026-09-26）：
A. 各 DXCD 状态内 ZC>0 / ZD>0 比例（验证"主战场内ZC恒正"）
B. 一段时期收益：各状态 5日累计高幅（vs 次日高幅，验证"次日高幅是短期数据"）
C. DXZC/DXZD 劫在主战场外：DXCD>0 但 DXZC<0 的情况，及其导致 DXCD 转负的概率
D. DXCD正交时（上/忐），各劫（ZA/ZB/AB/ZC/ZD）的修复概率（明确化定义）
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_综合.txt', 'w', encoding='utf-8')
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
i_nhr = 26
i_zb = 62
i_zd = 63
i_ab = 64
i_cd2 = 65

# A. 各状态 ZC/ZD 正比例
state_zc = defaultdict(lambda: {'n': 0, 'zc_pos': 0, 'zd_pos': 0})
# B. 各状态 5日累计高幅（需要未来5天的高幅，用次日高幅近似累计）
# 实际：次日高幅是单日。5日累计需未来5天。这里用"次日高幅"作为单日代理，
# 另统计"状态持续时间"（连续处于该状态的天数）来反映一段时期
state_dur = defaultdict(list)  # 每个状态段的持续时间
# C. DXCD>0 但 DXZC<0 的情况
zc_neg_in_cdpos = defaultdict(lambda: {'n': 0, 'cd_neg': 0, 'repaired': 0, 'end': 0})
# D. DXCD正交时各劫修复概率
repair_stats = defaultdict(lambda: {'total': 0, 'cd_neg': 0, 'repaired': 0, 'end': 0})

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
                if len(row) <= max(i_cd, i_za, i_zc, i_ze, i_nhr, i_zb, i_zd, i_ab, i_cd2):
                    continue
                try:
                    cd = row[i_cd].strip()
                    za = float(row[i_za])
                    zc = float(row[i_zc])
                    ze = float(row[i_ze])
                    nhr = float(row[i_nhr])
                    zb = float(row[i_zb])
                    zd = float(row[i_zd])
                    ab = float(row[i_ab])
                    cd2 = float(row[i_cd2])
                except (ValueError, IndexError):
                    continue
                rows.append((cd, za, zc, ze, nhr, zb, zd, ab, cd2))

            n = len(rows)
            # A. 各状态 ZC/ZD 正比例
            for cd, za, zc, ze, nhr, zb, zd, ab, cd2 in rows:
                if cd in ('上', '中', '下', '忐', '忠', '忑'):
                    state_zc[cd]['n'] += 1
                    if zc > 0:
                        state_zc[cd]['zc_pos'] += 1
                    if zd > 0:
                        state_zc[cd]['zd_pos'] += 1

            # B. 状态持续时间（连续相同DXCD的天数）
            i = 0
            while i < n:
                cd = rows[i][0]
                j = i
                while j < n and rows[j][0] == cd:
                    j += 1
                state_dur[cd].append(j - i)
                i = j

            # C. DXCD>0 但 DXZC<0（主战场外，可能转主战场的备选）
            # DXCD>0 = 上/中/下（BTCD>0 多头排列）。DXZC<0 = 收盘跌破EMA26
            # 但"上"要求ZC>0，所以DXZC<0只可能出现在 中/下
            for i in range(n):
                cd, za, zc, ze, nhr, zb, zd, ab, cd2 = rows[i]
                # C: 中/下 状态（DXCD>0 但 ZC<=0）
                if cd in ('中', '下') and zc <= 0:
                    key = '中下_ZC<=0'
                    zc_neg_in_cdpos[key]['n'] += 1
                    # 扫描后续：DXCD转负（下→忑 或 中→下→忑）前，ZC是否修复
                    outcome = 'end'
                    for j in range(i+1, n):
                        jcd, jza, jzc, jze, jnhr, jzb, jzd, jab, jcd2 = rows[j]
                        if jzc > 0:
                            outcome = 'repaired'
                            break
                        if jcd in ('忑',):
                            outcome = 'cd_neg'
                            break
                        # 中→下 不算转负（仍DXCD>0），但下→忑才算
                        # 下状态本身是DXCD>0但ZC<0，若持续下，ZC一直<0
                    zc_neg_in_cdpos[key][outcome] += 1

                # D. DXCD正交（上/忐）时各劫修复概率
                if cd in ('上', '忐'):
                    for kname, kcol in [('ZA', 1), ('ZB', 5), ('AB', 7), ('ZC', 2), ('ZD', 6)]:
                        val = rows[i][kcol]
                        if i > 0:
                            prev_val = rows[i-1][kcol]
                            if prev_val > 0 and val <= 0:
                                repair_stats[kname]['total'] += 1
                                outcome = 'end'
                                for j in range(i+1, n):
                                    jcd, jza, jzc, jze, jnhr, jzb, jzd, jab, jcd2 = rows[j]
                                    jval = rows[j][kcol]
                                    if jval > 0:
                                        outcome = 'repaired'
                                        break
                                    if jcd in ('下', '忑'):
                                        outcome = 'cd_neg'
                                        break
                                repair_stats[kname][outcome] += 1

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('A. 各 DXCD 状态内 ZC>0 / ZD>0 比例')
out('=' * 100)
out('')
out(f'| {"DXCD":<6s} | {"样本":>10s} | {"ZC>0比例":>10s} | {"ZD>0比例":>10s} |')
out(f'|{"":->6s}|{"":->10s}:|{"":->10s}:|{"":->10s}:|')
for cd in ['上', '中', '下', '忐', '忠', '忑']:
    s = state_zc.get(cd)
    if not s or s['n'] == 0:
        continue
    out(f'| {cd:<6s} | {s["n"]:>10,d} | {s["zc_pos"]/s["n"]*100:>9.1f}% | {s["zd_pos"]/s["n"]*100:>9.1f}% |')

out('')
out('=' * 100)
out('B. 各 DXCD 状态持续时间（一段时期视角）')
out('=' * 100)
out('')
out(f'| {"DXCD":<6s} | {"段数":>8s} | {"平均持续":>8s} | {"中位持续":>8s} | {"P75":>6s} |')
out(f'|{"":->6s}|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->6s}:|')
for cd in ['上', '中', '下', '忐', '忠', '忑']:
    durs = np.array(state_dur.get(cd, []))
    if len(durs) < 100:
        continue
    out(f'| {cd:<6s} | {len(durs):>8,d} | {np.mean(durs):>7.1f} | {np.median(durs):>7.0f} | {np.percentile(durs,75):>5.0f} |')

out('')
out('=' * 100)
out('C. DXCD>0 但 DXZC<0（中/下状态，主战场外备选）→ 导致DXCD转负概率')
out('=' * 100)
out('')
for key in ['中下_ZC<=0']:
    s = zc_neg_in_cdpos[key]
    total = s['n']
    if total == 0:
        continue
    out(f'{key}: 出现 {total:,} 次')
    out(f'  → ZC修复（转正，重回主战场）: {s["repaired"]:,} 次 = {s["repaired"]/total*100:.1f}%')
    out(f'  → DXCD转负（下→忑）: {s["cd_neg"]:,} 次 = {s["cd_neg"]/total*100:.1f}%')
    out(f'  → 文件结束未定: {s["end"]:,} 次 = {s["end"]/total*100:.1f}%')

out('')
out('=' * 100)
out('D. DXCD正交（上/忐）时各劫修复概率（明确化定义）')
out('=' * 100)
out('')
out('定义：劫 = 该指标由正转负。修复 = 在DXCD转负(下/忑)前，该指标重新转正。')
out('')
out(f'| {"劫":<6s} | {"出现次数":>10s} | {"DXCD转负":>10s} | {"转负率":>8s} | {"修复":>8s} | {"修复率":>8s} |')
out(f'|{"":->6s}|{"":->10s}:|{"":->10s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|')
for key in ['ZA', 'ZB', 'AB', 'ZC', 'ZD']:
    s = repair_stats[key]
    total = s['total']
    if total == 0:
        continue
    out(f'| {key:<6s} | {total:>10,d} | {s["cd_neg"]:>10,d} | {s["cd_neg"]/total*100:>7.1f}% | {s["repaired"]:>8,d} | {s["repaired"]/total*100:>7.1f}% |')

OUTF.close()
print('Done')