# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：DXCD 状态的"最终出路"（非维持率，而是离开后的去向）

核心逻辑：
- 识别每个 DXCD 状态段（连续相同状态的天数）
- 对每个段，看它"离开"时转向哪里
- 特别关注：忐段离开后，是转上（好）还是转下/转负（坏）？
- 同时统计：上段离开后去向、中段、下段、忠段、忑段

补充：DXZC 下破后持续关注的价值（下破后多久修复、修复后走多远）
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_状态最终出路.txt', 'w', encoding='utf-8')
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

# 状态段离开后的去向
# key = 起始状态, value = {目标状态: 次数}
exit_trans = defaultdict(lambda: defaultdict(int))
# 忐段离开后的去向（重点）
# 段内信息
seg_info = defaultdict(lambda: {'n': 0, 'durs': []})

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
                except (ValueError, IndexError):
                    continue
                rows.append((cd, za, zc, ze, nhr, zb, zd))

            n = len(rows)
            # 识别状态段
            i = 0
            while i < n:
                cd = rows[i][0]
                j = i
                while j < n and rows[j][0] == cd:
                    j += 1
                dur = j - i
                seg_info[cd]['n'] += 1
                seg_info[cd]['durs'].append(dur)
                # 段离开后的去向（若还有下一段）
                if j < n:
                    next_cd = rows[j][0]
                    exit_trans[cd][next_cd] += 1
                i = j

    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('DXCD 状态段"离开后"的去向（非维持率，而是最终出路）')
out('=' * 100)
out('')
out('说明：对每个状态段，统计它"离开"（转为其他状态）时的去向。')
out('')
for cd in ['上', '中', '下', '忐', '忠', '忑']:
    exits = exit_trans[cd]
    total_exit = sum(exits.values())
    if total_exit == 0:
        continue
    out(f'【{cd}】段数 {seg_info[cd]["n"]:,}，平均持续 {np.mean(seg_info[cd]["durs"]):.1f} 天')
    out(f'  离开后去向（共 {total_exit:,} 次离开）：')
    # 按去向排序
    for tgt in ['上', '中', '下', '忐', '忠', '忑']:
        cnt = exits[tgt]
        if cnt > 0:
            out(f'    → {tgt}: {cnt:,} 次 = {cnt/total_exit*100:.1f}%')
    out('')

out('=' * 100)
out('重点：忐段离开后的去向（你的理想：忐大概率转上）')
out('=' * 100)
out('')
exits = exit_trans['忐']
total_exit = sum(exits.values())
if total_exit > 0:
    up = exits['上']
    down = exits['中'] + exits['下'] + exits['忠'] + exits['忑']
    out(f'忐段共离开 {total_exit:,} 次')
    out(f'  → 转上: {up:,} 次 = {up/total_exit*100:.1f}%')
    out(f'  → 转坏(中/下/忠/忑): {down:,} 次 = {down/total_exit*100:.1f}%')
    out(f'  → 转忠: {exits["忠"]:,} 次 = {exits["忠"]/total_exit*100:.1f}%')
    out(f'  → 转忑: {exits["忑"]:,} 次 = {exits["忑"]/total_exit*100:.1f}%')
    out('')
    out(f'结论：忐离开后，转上概率 = {up/total_exit*100:.1f}%，转坏概率 = {down/total_exit*100:.1f}%')

out('')
out('=' * 100)
out('对照：上段离开后的去向（上的"最终出路"）')
out('=' * 100)
out('')
exits = exit_trans['上']
total_exit = sum(exits.values())
if total_exit > 0:
    out(f'上段共离开 {total_exit:,} 次')
    for tgt in ['中', '下', '忐', '忠', '忑']:
        cnt = exits[tgt]
        if cnt > 0:
            out(f'  → {tgt}: {cnt:,} 次 = {cnt/total_exit*100:.1f}%')

out('')
out('=' * 100)
out('对照：中/下段离开后的去向（DXZC入口的最终出路）')
out('=' * 100)
out('')
for cd in ['中', '下']:
    exits = exit_trans[cd]
    total_exit = sum(exits.values())
    if total_exit == 0:
        continue
    out(f'【{cd}】段共离开 {total_exit:,} 次')
    for tgt in ['上', '中', '下', '忐', '忠', '忑']:
        cnt = exits[tgt]
        if cnt > 0:
            out(f'  → {tgt}: {cnt:,} 次 = {cnt/total_exit*100:.1f}%')
    out('')

OUTF.close()
print('Done')