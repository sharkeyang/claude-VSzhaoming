# -*- coding: utf-8 -*-
"""
原策略 vs 新策略 直接对比
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
                ze = to_f(row[15])
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
                cond_ze_pos = ze > 0
                cond_zc_pos = zc > 0
                cond_hx_good = hx in HX_GOOD
                cond_hx_bad = hx in HX_BAD

                # 原策略最优组合
                conds = {
                    'OLD_D1_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D1',
                    'OLD_D2_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D2',
                    'OLD_D3_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D3',
                    'OLD_D5_BSHA5': cond_bsha5 and cls == 'D5',
                    'OLD_D6_BSHA5': cond_bsha5 and cls == 'D6',
                    'OLD_D7_BSHA5': cond_bsha5 and cls == 'D7',
                    'OLD_BSHA5': cond_bsha5,
                    'OLD_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men,

                    # 新策略最优组合
                    'NEW_D5_GOOD_BSHA5': cond_bsha5 and cls == 'D5' and cond_hx_good,
                    'NEW_D1_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D1',
                    'NEW_D2_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D2',
                    'NEW_D3_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D3',
                    'NEW_D5_BSHA5': cond_bsha5 and cls == 'D5',
                    'NEW_D6_BSHA5': cond_bsha5 and cls == 'D6',
                    'NEW_D7_BSHA5': cond_bsha5 and cls == 'D7',
                    'NEW_BSHA5_LY': cond_bsha5 and cond_ly,
                    'NEW_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men,
                    'NEW_GOOD_BSHA5_LY': cond_bsha5 and cond_ly and cond_hx_good,
                    'NEW_D5_GOOD_ZCpos_BSHA5': cond_bsha5 and cls == 'D5' and cond_hx_good and cond_zc_pos,
                    'NEW_D1_GOOD_BSHA5_LY': cond_bsha5 and cond_ly and cond_hx_good and cls == 'D1',
                    'NEW_D2_GOOD_BSHA5_LY': cond_bsha5 and cond_ly and cond_hx_good and cls == 'D2',
                    'NEW_D3_GOOD_BSHA5_LY': cond_bsha5 and cond_ly and cond_hx_good and cls == 'D3',
                    # 无BSHA时的最优
                    'NEW_MEN_noBSHA': cond_men and not cond_bsha5,
                    'NEW_LY_MEN_noBSHA': cond_ly and cond_men and not cond_bsha5,
                    'NEW_D1_MEN_noBSHA': cond_men and not cond_bsha5 and cls == 'D1',
                    'NEW_D2_MEN_noBSHA': cond_men and not cond_bsha5 and cls == 'D2',
                    'NEW_D3_MEN_noBSHA': cond_men and not cond_bsha5 and cls == 'D3',
                }
                for cname, cval in conds.items():
                    if cval:
                        add(cname, nxt_gf, hit1, hit2, hit3)
    except Exception:
        pass

# 名称映射
NAME_MAP = {
    'OLD_D1_BSHA5_LY_MEN': '【原】等1+BSHA5+连+门',
    'OLD_D2_BSHA5_LY_MEN': '【原】等2+BSHA5+连+门',
    'OLD_D3_BSHA5_LY_MEN': '【原】等3+BSHA5+连+门',
    'OLD_D5_BSHA5': '【原】等5+BSHA5',
    'OLD_D6_BSHA5': '【原】等6+BSHA5',
    'OLD_D7_BSHA5': '【原】等7+BSHA5',
    'OLD_BSHA5': '【原】BSHA5',
    'OLD_BSHA5_LY_MEN': '【原】BSHA5+连+门',
    'NEW_D5_GOOD_BSHA5': '【新】等5+甲乙己+BSHA5',
    'NEW_D1_BSHA5_LY_MEN': '【新】等1+BSHA5+连+门',
    'NEW_D2_BSHA5_LY_MEN': '【新】等2+BSHA5+连+门',
    'NEW_D3_BSHA5_LY_MEN': '【新】等3+BSHA5+连+门',
    'NEW_D5_BSHA5': '【新】等5+BSHA5',
    'NEW_D6_BSHA5': '【新】等6+BSHA5',
    'NEW_D7_BSHA5': '【新】等7+BSHA5',
    'NEW_BSHA5_LY': '【新】BSHA5+连',
    'NEW_BSHA5_LY_MEN': '【新】BSHA5+连+门',
    'NEW_GOOD_BSHA5_LY': '【新】甲乙己+BSHA5+连',
    'NEW_D5_GOOD_ZCpos_BSHA5': '【新】等5+甲乙己+ZC>0+BSHA5',
    'NEW_D1_GOOD_BSHA5_LY': '【新】等1+甲乙己+BSHA5+连',
    'NEW_D2_GOOD_BSHA5_LY': '【新】等2+甲乙己+BSHA5+连',
    'NEW_D3_GOOD_BSHA5_LY': '【新】等3+甲乙己+BSHA5+连',
    'NEW_MEN_noBSHA': '【新】门(无BSHA)',
    'NEW_LY_MEN_noBSHA': '【新】连+门(无BSHA)',
    'NEW_D1_MEN_noBSHA': '【新】等1+门(无BSHA)',
    'NEW_D2_MEN_noBSHA': '【新】等2+门(无BSHA)',
    'NEW_D3_MEN_noBSHA': '【新】等3+门(无BSHA)',
}

print(f'核心池文件: {files_core}, 总行数: {total_rows}')
print()
print('=' * 90)
print('原策略 vs 新策略 直接对比（下日高幅口径，高波池全量）')
print('=' * 90)
print()
print(f'{"策略":<40s} {"样本":>10s} {"H1":>7s} {"H2":>7s} {"H3":>7s}')
print('-' * 75)

rows = []
for k, (n, h1, h2, h3) in stats.items():
    if n >= 1000:
        p1 = h1 / n * 100
        p2 = h2 / n * 100
        p3 = h3 / n * 100
        rows.append((p2, k, n, p1, p3))

rows.sort(key=lambda x: (-x[0], -x[2]))
for p2, k, n, p1, p3 in rows:
    name = NAME_MAP.get(k, k)
    print(f'{name:<40s} {n:>10,} {p1:>6.1f}% {p2:>6.1f}% {p3:>6.1f}%')

print()
print('Done')