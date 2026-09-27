# -*- coding: utf-8 -*-
"""
验证（2026-09-26）：主战场内各种"劫"（DXZA/DXZB/DXAB 由正转负）有多大概率
最终导致 DXCD 由正转负（即不修复、一路走坏）？

核心判定（简化）：
- 主战场 = DXZE>0 + DXCD in (上,忐)
- 劫出现 = 某指标由正转负
- 扫描后续：
  - 若在劫修复（该指标重新转正）之前，DXCD 先转负（下/忑）→ "劫直接导致DXCD转负"
  - 若劫先修复（转正）→ "修复成功"
- 统计：劫出现后，DXCD 转负（未修复）的概率

列映射：
  [8]  DXCD
  [13] 日ZA = DTZA
  [14] 日ZC = DTZC
  [15] 日ZE = DTZE
  [62] DTZB
  [64] DTAB
"""
import csv, os, io, json
from collections import defaultdict

OUTF = io.open('____temp/_验证_劫导致DXCD转负.txt', 'w', encoding='utf-8')
def out(s=''):
    OUTF.write(s + '\n')

BOARD_MAP_PATH = '_产出物/MP1_花册分类映射.json'
with open(BOARD_MAP_PATH, 'r', encoding='utf-8') as f:
    board_map = json.load(f)
高波池板块 = {'Qic', 'Qim', 'Qit'}

i_cd = 8
i_za = 13
i_ze = 15
i_zb = 62
i_ab = 64

# 劫指标 → 列索引
KEY_COL = {'ZA': i_za, 'ZB': i_zb, 'AB': i_ab}

stats = defaultdict(lambda: {'total': 0, 'cd_neg': 0, 'repaired': 0, 'end': 0})
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
                if len(row) <= max(i_cd, i_za, i_ze, i_zb, i_ab):
                    continue
                try:
                    cd = row[i_cd].strip()
                    za = float(row[i_za])
                    ze = float(row[i_ze])
                    zb = float(row[i_zb])
                    ab = float(row[i_ab])
                except (ValueError, IndexError):
                    continue
                rows.append((cd, za, ze, zb, ab))

            n = len(rows)
            for i in range(n):
                cd, za, ze, zb, ab = rows[i]
                in_main = (ze > 0) and (cd in ('上', '忐'))
                if not in_main:
                    continue
                # 对每个劫指标
                for key, col in KEY_COL.items():
                    val = {'ZA': za, 'ZB': zb, 'AB': ab}[key]
                    if i > 0:
                        prev_val = {'ZA': rows[i-1][1], 'ZB': rows[i-1][3], 'AB': rows[i-1][4]}[key]
                        if prev_val > 0 and val <= 0:
                            # 劫出现，扫描后续
                            stats[key]['total'] += 1
                            outcome = 'end'  # 默认文件结束
                            for j in range(i+1, n):
                                jcd, jza, jze, jzb, jab = rows[j]
                                jval = {'ZA': jza, 'ZB': jzb, 'AB': jab}[key]
                                # 先检查劫是否修复（转正）
                                if jval > 0:
                                    outcome = 'repaired'
                                    break
                                # 再检查 DXCD 是否转负
                                if jcd in ('下', '忑'):
                                    outcome = 'cd_neg'
                                    break
                            stats[key][outcome] += 1
    except Exception:
        pass
    files_done += 1

out(f'文件数: {files_done}')
out('')
out('=' * 100)
out('主战场内各"劫"导致 DXCD 转负的概率（劫修复前 DXCD 先转负）')
out('=' * 100)
out('')
out(f'| {"劫":<6s} | {"出现次数":>10s} | {"DXCD转负":>10s} | {"转负率":>8s} | {"修复":>8s} | {"修复率":>8s} | {"文件结束":>8s} |')
out(f'|{"":->6s}|{"":->10s}:|{"":->10s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|')
for key in ['ZA', 'ZB', 'AB']:
    s = stats[key]
    total = s['total']
    if total == 0:
        continue
    cd_neg_rate = s['cd_neg'] / total * 100
    repair_rate = s['repaired'] / total * 100
    out(f'| {key:<6s} | {total:>10,d} | {s["cd_neg"]:>10,d} | {cd_neg_rate:>7.1f}% | {s["repaired"]:>8,d} | {repair_rate:>7.1f}% | {s["end"]:>8,d} |')

out('')
out('=' * 100)
out('解读')
out('=' * 100)
out('')
for key in ['ZA', 'ZB', 'AB']:
    s = stats[key]
    total = s['total']
    if total == 0:
        continue
    cd_neg_rate = s['cd_neg'] / total * 100
    repair_rate = s['repaired'] / total * 100
    out(f'{key}劫：出现 {total:,} 次')
    out(f'  → 直接导致DXCD转负（未修复）: {s["cd_neg"]:,} 次 = {cd_neg_rate:.1f}%')
    out(f'  → 修复成功（劫转正，DXCD保住）: {s["repaired"]:,} 次 = {repair_rate:.1f}%')
    out(f'  → 文件结束未定: {s["end"]:,} 次 = {s["end"]/total*100:.1f}%')

OUTF.close()
print('Done')