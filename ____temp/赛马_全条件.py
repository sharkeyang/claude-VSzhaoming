# -*- coding: utf-8 -*-
"""
策略赛马 — 全条件排名（新高波池口径）
包含 BSHA5/BSHA3/连阳/门/层主/BT鼎/升排 等条件
"""
import csv, os, sys
from collections import defaultdict

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

CODE2BOARD = {}
with open('____temp/市板映射.csv', 'r', encoding='utf-8-sig') as f:
    r = csv.reader(f)
    next(r)
    for row in r:
        if len(row) >= 2:
            CODE2BOARD[row[0].strip()] = row[1].strip()
CORE = {'Qic', 'Qim', 'Qit'}

HX_MAP = {'甲': '甲', '乙': '乙', '丙': '丙', '丁': '丁', '戊': '戊', '己': '己'}
HX_GOOD = {'甲', '乙', '己'}
HX_BAD = {'丙', '丁', '戊'}

stats = defaultdict(lambda: [0, 0, 0, 0])

def add(key, nxt, h1, h2, h3):
    stats[key][0] += 1
    stats[key][1] += h1
    stats[key][2] += h2
    stats[key][3] += h3

def get_cls(dtza, cx):
    if not cx: return None
    mf = cx[-1]
    if dtza == 1: return 'D1'
    elif dtza >= 2: return 'D3' if mf in ('A','B') else 'D2'
    elif dtza == -1: return 'D5'
    elif dtza <= -2: return 'D7' if mf in ('E','F') else 'D6'
    return None

def parse_hx(dxab):
    if len(dxab) >= 2 and dxab[1] in HX_MAP:
        return dxab[1]
    return ''

files_core = 0
total_rows = 0

for fname in os.listdir('昭明算展/谕组日'):
    code = fname.replace('谕组日_', '').replace('.csv', '')
    if CODE2BOARD.get(code, '') not in CORE:
        continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日', fname), 'r', encoding='gbk', errors='replace') as f:
            r = csv.reader(f)
            next(r)
            for row in r:
                if len(row) < 35: continue
                def to_f(v):
                    try: return float(v)
                    except: return 0.0
                nxt_gf = to_f(row[26])
                dtza = to_f(row[13])
                zc = to_f(row[14])
                btding = to_f(row[40]) if len(row) > 40 else 0.0
                btly = to_f(row[42]) if len(row) > 42 else 0.0
                bsha = to_f(row[19]) if len(row) > 19 else 0.0
                cx = row[33].strip()
                cd = row[8].strip()
                dxab = row[9].strip()
                cengjie = row[28].strip() if len(row) > 28 else ''
                bx = row[11].strip() if len(row) > 11 else ''

                cls = get_cls(dtza, cx)
                if cls is None: continue
                hx = parse_hx(dxab)
                if not hx: continue
                total_rows += 1

                hit1 = 1 if nxt_gf >= 1 else 0
                hit2 = 1 if nxt_gf >= 2 else 0
                hit3 = 1 if nxt_gf >= 3 else 0

                cond_bsha5 = bsha > 5
                cond_bsha3 = bsha > 3
                cond_ly = btly > 0
                cond_men = zc > 0 and cd == '上'
                cond_cz = cengjie.startswith('主')
                cond_btding = btding > 0
                cond_sp = bx.startswith('升')
                cond_zc_pos = zc > 0
                cond_hx_good = hx in HX_GOOD
                cond_hx_bad = hx in HX_BAD

                cls_name = {'D1':'等1','D2':'等2','D3':'等3','D5':'等5','D6':'等6','D7':'等7'}[cls]

                # ===== 位置基准（不附加条件） =====
                add(f'基准|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+ZC>0 =====
                if cond_zc_pos:
                    add(f'ZC>0|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+ZC>0+甲乙己 =====
                if cond_zc_pos and cond_hx_good:
                    add(f'ZC>0+甲乙己|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+BSHA5 =====
                if cond_bsha5:
                    add(f'BSHA5|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+BSHA3 =====
                if cond_bsha3:
                    add(f'BSHA3|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+连阳 =====
                if cond_ly:
                    add(f'连|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+门 =====
                if cond_men:
                    add(f'门|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+层主 =====
                if cond_cz:
                    add(f'层主|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+BT鼎 =====
                if cond_btding:
                    add(f'BT鼎|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+升排 =====
                if cond_sp:
                    add(f'升排|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+BSHA5+连 =====
                if cond_bsha5 and cond_ly:
                    add(f'BSHA5+连|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+BSHA5+门 =====
                if cond_bsha5 and cond_men:
                    add(f'BSHA5+门|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+BSHA5+连+门 =====
                if cond_bsha5 and cond_ly and cond_men:
                    add(f'BSHA5+连+门|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+ZC>0+BSHA5 =====
                if cond_zc_pos and cond_bsha5:
                    add(f'ZC>0+BSHA5|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+ZC>0+甲乙己+BSHA5 =====
                if cond_zc_pos and cond_hx_good and cond_bsha5:
                    add(f'ZC>0+甲乙己+BSHA5|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+ZC>0+甲乙己+BSHA5+连 =====
                if cond_zc_pos and cond_hx_good and cond_bsha5 and cond_ly:
                    add(f'ZC>0+甲乙己+BSHA5+连|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+连+门 =====
                if cond_ly and cond_men:
                    add(f'连+门|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+层主+门 =====
                if cond_cz and cond_men:
                    add(f'层主+门|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+BT鼎+门 =====
                if cond_btding and cond_men:
                    add(f'BT鼎+门|{cls_name}', nxt_gf, hit1, hit2, hit3)

                # ===== 位置+升排+门 =====
                if cond_sp and cond_men:
                    add(f'升排+门|{cls_name}', nxt_gf, hit1, hit2, hit3)

    except Exception:
        pass

# ===== 输出 =====
MIN_N = 1000
BENCH = 37.2

rows = []
for k, (n, h1, h2, h3) in stats.items():
    if n >= MIN_N:
        p1 = h1 / n * 100
        p2 = h2 / n * 100
        p3 = h3 / n * 100
        rows.append((p2, k, n, p1, p3))

rows.sort(key=lambda x: (-x[0], -x[2]))

print(f'新高波池口径: {files_core} 文件, {total_rows} 行')
print(f'全量基准 H2: {BENCH}%')
print()
print(f'=== 全条件赛马排名（H2 ≥ {BENCH}%，n≥{MIN_N}）===')
print(f'{"排名":>4s} {"策略":<45s} {"样本":>10s} {"H1":>7s} {"H2":>7s} {"H3":>7s}')
print('-' * 80)

for i, (p2, k, n, p1, p3) in enumerate(rows, 1):
    if p2 >= BENCH:
        print(f'{i:>4d} {k:<45s} {n:>10,} {p1:>6.1f}% {p2:>6.1f}% {p3:>6.1f}%')

print()
print(f'=== 低于基准（H2 < {BENCH}%，n≥{MIN_N}）===')
for i, (p2, k, n, p1, p3) in enumerate(rows, 1):
    if p2 < BENCH:
        print(f'{i:>4d} {k:<45s} {n:>10,} {p1:>6.1f}% {p2:>6.1f}% {p3:>6.1f}%')
    if i > 250:
        print(f'  ... 还有 {len(rows)-250} 个')
        break

print(f'\nDone: {len(rows)} strategies')