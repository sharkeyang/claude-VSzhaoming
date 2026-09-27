# -*- coding: utf-8 -*-
"""
诊断（2026-09-26）：
A. DXCD 各状态内 ZC>0 / ZD>0 比例（验证"主战场内ZC恒正"是否成立，尤其"忐"内ZC）
B. DXCD 状态转移矩阵（今日DXCD → 次日DXCD），验证"忐大部分转上"？
C. 各状态次日高幅（短期 vs 一段时期）
"""
import csv, os, io, json
from collections import defaultdict
import numpy as np

OUTF = io.open('____temp/_验证_诊断状态转移.txt', 'w', encoding='utf-8')
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

# A. 各DXCD状态内 ZC/ZD 正比例
state_zc = defaultdict(lambda: {'n': 0, 'zc_pos': 0, 'zd_pos': 0})
# B. 状态转移
trans = defaultdict(lambda: defaultdict(int))
# C. 各状态次日高幅
state_nhr = defaultdict(list)

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
            prev_cd = None
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
                # A. 各状态 ZC/ZD 正比例
                if cd in ('上', '中', '下', '忐', '忠', '忑'):
                    state_zc[cd]['n'] += 1
                    if zc > 0:
                        state_zc[cd]['zc_pos'] += 1
                    if zd > 0:
                        state_zc[cd]['zd_pos'] += 1
                # C. 各状态次日高幅
                state_nhr[cd].append(nhr)
                # B. 转移
                if prev_cd is not None:
                    trans[prev_cd][cd] += 1
                prev_cd = cd
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
out('B. DXCD 状态转移概率（今日 → 次日）')
out('=' * 100)
out('')
out(f'| {"今日/次日":<10s} | {"上":>8s} | {"中":>8s} | {"下":>8s} | {"忐":>8s} | {"忠":>8s} | {"忑":>8s} |')
out(f'|{"":->10s}|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|{"":->8s}:|')
for cd in ['上', '中', '下', '忐', '忠', '忑']:
    row = trans[cd]
    total = sum(row.values())
    if total == 0:
        continue
    cells = []
    for tgt in ['上', '中', '下', '忐', '忠', '忑']:
        cells.append(f'{row[tgt]/total*100:>7.1f}%')
    out(f'| {cd:<10s} | ' + ' | '.join(cells) + ' |')

out('')
out('=' * 100)
out('C. 各 DXCD 状态次日高幅')
out('=' * 100)
out('')
out(f'| {"DXCD":<6s} | {"样本":>10s} | {"均次日高":>8s} | {"高≥3%":>7s} |')
out(f'|{"":->6s}|{"":->10s}:|{"":->8s}:|{"":->7s}:|')
for cd in ['上', '中', '下', '忐', '忠', '忑']:
    vals = np.array(state_nhr[cd])
    if len(vals) < 100:
        continue
    out(f'| {cd:<6s} | {len(vals):>10,d} | {np.mean(vals):>7.2f}% | {(vals>=3).sum()/len(vals)*100:>6.1f}% |')

OUTF.close()
print('Done')