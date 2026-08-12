# -*- coding: utf-8 -*-
"""DXAB乙 → 丙/丁 转移概率 + 乙(ZA<0)恢复分析"""
import csv, os, io
from collections import Counter

OUTF = io.open('____temp/_dxab_transition_result.txt', 'w', encoding='utf-8')

def out(s=''):
    OUTF.write(s + '\n')

HUE = ['a甲', 'b乙', 'c丙', 'r己', 'y戊', 'z丁']

# Q1/Q2: next-day transitions
next_trans = Counter()          # (cur, nxt) -> count
next_trans_za = Counter()       # (cur, nxt, cur_za_neg) -> count
乙_to_乙_neg = Counter()         # 乙(ZA<0) -> 乙(next day) : count by next-day ZA sign
乙_to_乙_pos = Counter()

# Episode tracking
in_ep = False
ep_neg_seen = False
ep_pos_seen = False
ep_outcomes = []

total_rows = 0
total_乙 = 0
files_done = 0

for fname in os.listdir('昭明算展/谕组日'):
    p = os.path.join('昭明算展/谕组日', fname)
    try:
        with open(p, 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            prev_dxab = None
            prev_za = None
            for row in r:
                if len(row) < 16:
                    continue
                dxab_raw = row[9]
                za_raw = row[13]
                if len(dxab_raw) < 2:
                    continue
                dxab = dxab_raw[:2]
                try:
                    za = float(za_raw)
                except:
                    continue
                total_rows += 1
                if dxab == 'b乙':
                    total_乙 += 1

                # transition bookkeeping
                if prev_dxab is not None:
                    next_trans[(prev_dxab, dxab)] += 1
                    if prev_za is not None:
                        next_trans_za[(prev_dxab, dxab, prev_za < 0)] += 1
                    # special: 乙 -> 乙, separated by prev ZA sign
                    if prev_dxab == 'b乙' and dxab == 'b乙' and prev_za is not None:
                        if prev_za < 0:
                            乙_to_乙_neg[za < 0] += 1
                        else:
                            乙_to_乙_pos[za < 0] += 1

                # episode tracking for 乙
                if dxab == 'b乙':
                    if not in_ep:
                        in_ep = True
                        ep_neg_seen = False
                        ep_pos_seen = False
                    if za < 0:
                        ep_neg_seen = True
                    else:
                        ep_pos_seen = True
                else:
                    if in_ep:
                        if ep_neg_seen:
                            if ep_pos_seen:
                                ep_outcomes.append('recover')
                            else:
                                ep_outcomes.append('exit_' + dxab[:2])
                        in_ep = False

                prev_dxab = dxab
                prev_za = za
            if in_ep:
                if ep_neg_seen:
                    if ep_pos_seen:
                        ep_outcomes.append('recover_ongoing')
                    else:
                        ep_outcomes.append('ongoing_no_recover')
                in_ep = False
    except Exception:
        pass
    files_done += 1

out('## Summary')
out(f'Files: {files_done}, Total rows: {total_rows}, Total 乙 days: {total_乙}')
out('')

# === Q1 ===
乙_trans = {k: v for k, v in next_trans.items() if k[0] == 'b乙'}
乙_total = sum(乙_trans.values())
out('=== Q1: DXAB乙 → next-day transition ===')
out(f'Total 乙→next: {乙_total}')
for state in HUE:
    k = ('b乙', state)
    if k in 乙_trans:
        out(f'  乙→{state}: {乙_trans[k]:>9d}  ({乙_trans[k]/乙_total*100:.2f}%)')
to_丙 = 乙_trans.get(('b乙', 'c丙'), 0)
to_丁 = 乙_trans.get(('b乙', 'z丁'), 0)
out(f'  乙→丙: {to_丙} ({to_丙/乙_total*100:.2f}%)')
out(f'  乙→丁: {to_丁} ({to_丁/乙_total*100:.2f}%)')
out(f'  乙→丙或丁: {to_丙+to_丁} ({(to_丙+to_丁)/乙_total*100:.2f}%)')
out('')

# === Q2: 乙(ZA<0) → next day ===
乙_neg_trans = {k: v for k, v in next_trans_za.items() if k[0] == 'b乙' and k[2]}
乙_neg_total = sum(乙_neg_trans.values())
out('=== Q2: DXAB乙 (ZA<0) → next day ===')
out(f'Total 乙(ZA<0)→next: {乙_neg_total}')
for state in HUE:
    k = ('b乙', state, True)
    if k in 乙_neg_trans:
        out(f'  乙(ZA<0)→{state}: {乙_neg_trans[k]:>9d}  ({乙_neg_trans[k]/乙_neg_total*100:.2f}%)')
to_丙 = 乙_neg_trans.get(('b乙', 'c丙', True), 0)
to_丁 = 乙_neg_trans.get(('b乙', 'z丁', True), 0)
out(f'  乙(ZA<0)→丙: {to_丙} ({to_丙/乙_neg_total*100:.2f}%)')
out(f'  乙(ZA<0)→丁: {to_丁} ({to_丁/乙_neg_total*100:.2f}%)')
out(f'  乙(ZA<0)→丙或丁: {to_丙+to_丁} ({(to_丙+to_丁)/乙_neg_total*100:.2f}%)')
out('')

# === Q3: 乙(ZA<0) → 乙 (next day) by ZA sign ===
乙neg_keep_total = 乙_to_乙_neg[True] + 乙_to_乙_pos[False] + 乙_to_乙_neg[False] + 乙_to_乙_pos[True]
# careful: 乙_to_乙_neg[za<0_next] counts 乙(ZA<0)->乙(next), keyed by next-day za sign
to_乙_again = sum(乙_to_乙_neg.values())
if to_乙_again:
    out('=== Q2b: 乙(ZA<0) → 乙 (next day), by next-day ZA sign ===')
    out(f'  乙(ZA<0)→乙(next day): {to_乙_again} ({to_乙_again/乙_neg_total*100:.2f}% of 乙(ZA<0))')
    out(f'    → 乙 with next ZA<0:  {乙_to_乙_neg.get(True, 0)}  ({乙_to_乙_neg.get(True,0)/to_乙_again*100:.2f}%)')
    out(f'    → 乙 with next ZA>=0: {乙_to_乙_neg.get(False, 0)}  ({乙_to_乙_neg.get(False,0)/to_乙_again*100:.2f}%)')
    out(f'     其中 next ZA>0 (strict): {乙_to_乙_neg.get(False, 0)} (含ZA=0)')
out('')

# === Episode analysis ===
out('=== Episode Analysis: 乙-runs starting with ZA<0 ===')
n_ep = len(ep_outcomes)
out(f'Total 乙 episodes with ZA<0 seen: {n_ep}')
if n_ep:
    ep_recover = sum(1 for x in ep_outcomes if x == 'recover')
    ep_rec_ongoing = sum(1 for x in ep_outcomes if x == 'recover_ongoing')
    ep_exit_丙 = sum(1 for x in ep_outcomes if x == 'exit_c丙')
    ep_exit_丁 = sum(1 for x in ep_outcomes if x == 'exit_z丁')
    ep_exit_other = sum(1 for x in ep_outcomes if x.startswith('exit_') and x not in ('exit_c丙', 'exit_z丁'))
    ep_ongoing_nr = sum(1 for x in ep_outcomes if x == 'ongoing_no_recover')
    out(f'  在乙簇内恢复至 ZA>0 (recover): {ep_recover} ({ep_recover/n_ep*100:.2f}%)')
    out(f'  退出到 丙: {ep_exit_丙} ({ep_exit_丙/n_ep*100:.2f}%)')
    out(f'  退出到 丁: {ep_exit_丁} ({ep_exit_丁/n_ep*100:.2f}%)')
    out(f'  退出到 其他: {ep_exit_other} ({ep_exit_other/n_ep*100:.2f}%)')
    out(f'  文件末尾仍在乙簇且未恢复: {ep_ongoing_nr} ({ep_ongoing_nr/n_ep*100:.2f}%)')
    out(f'  文件末尾仍在乙簇但已恢复: {ep_rec_ongoing} ({ep_rec_ongoing/n_ep*100:.2f}%)')

OUTF.close()
print('Done')