# -*- coding: utf-8 -*-
"""分析好策略的共同规律"""
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

                # 单条件
                if cond_bsha5: add('BSHA5', nxt_gf, hit1, hit2, hit3)
                if cond_bsha3: add('BSHA3', nxt_gf, hit1, hit2, hit3)
                if cond_ly: add('连阳', nxt_gf, hit1, hit2, hit3)
                if cond_men: add('门', nxt_gf, hit1, hit2, hit3)
                if cond_zc_pos: add('ZC>0', nxt_gf, hit1, hit2, hit3)
                if cond_hx_good: add('甲乙己', nxt_gf, hit1, hit2, hit3)
                if cond_cz: add('层主', nxt_gf, hit1, hit2, hit3)
                if cond_btding: add('BT鼎', nxt_gf, hit1, hit2, hit3)
                if cond_sp: add('升排', nxt_gf, hit1, hit2, hit3)

                # 双条件
                if cond_bsha5 and cond_zc_pos: add('BSHA5+ZC>0', nxt_gf, hit1, hit2, hit3)
                if cond_bsha5 and cond_hx_good: add('BSHA5+甲乙己', nxt_gf, hit1, hit2, hit3)
                if cond_bsha5 and cond_ly: add('BSHA5+连', nxt_gf, hit1, hit2, hit3)
                if cond_bsha5 and cond_men: add('BSHA5+门', nxt_gf, hit1, hit2, hit3)
                if cond_ly and cond_men: add('连+门', nxt_gf, hit1, hit2, hit3)
                if cond_bsha3 and cond_ly: add('BSHA3+连', nxt_gf, hit1, hit2, hit3)
                if cond_bsha3 and cond_men: add('BSHA3+门', nxt_gf, hit1, hit2, hit3)

                # 三条件
                if cond_bsha5 and cond_ly and cond_men: add('BSHA5+连+门', nxt_gf, hit1, hit2, hit3)
                if cond_bsha5 and cond_zc_pos and cond_hx_good: add('BSHA5+ZC>0+甲乙己', nxt_gf, hit1, hit2, hit3)
                if cond_bsha5 and cond_zc_pos and cond_ly: add('BSHA5+ZC>0+连', nxt_gf, hit1, hit2, hit3)

    except Exception:
        pass

print('=' * 80)
print('各条件单独 vs 组合 的 H2 对比')
print('=' * 80)
print()
print(f'{"条件":<30s} {"样本":>10s} {"H1":>7s} {"H2":>7s} {"H3":>7s}')
print('-' * 65)

rows = []
for k, (n, h1, h2, h3) in stats.items():
    if n >= 1000:
        p1 = h1 / n * 100
        p2 = h2 / n * 100
        p3 = h3 / n * 100
        rows.append((p2, k, n, p1, p3))

rows.sort(key=lambda x: (-x[0], -x[2]))
for p2, k, n, p1, p3 in rows:
    print(f'{k:<30s} {n:>10,} {p1:>6.1f}% {p2:>6.1f}% {p3:>6.1f}%')

print()
print('=' * 80)
print('边际贡献分析')
print('=' * 80)
print()

base_h2 = 37.2

pairs = [
    ('BSHA5', None), ('BSHA3', None), ('连阳', None), ('门', None),
    ('ZC>0', None), ('甲乙己', None), ('层主', None), ('BT鼎', None), ('升排', None),
    ('BSHA5+ZC>0', 'BSHA5'), ('BSHA5+甲乙己', 'BSHA5'),
    ('BSHA5+连', 'BSHA5'), ('BSHA5+门', 'BSHA5'),
    ('连+门', '连阳'), ('BSHA3+连', 'BSHA3'), ('BSHA3+门', 'BSHA3'),
    ('BSHA5+连+门', 'BSHA5+连'),
    ('BSHA5+ZC>0+甲乙己', 'BSHA5+ZC>0'),
    ('BSHA5+ZC>0+连', 'BSHA5+ZC>0'),
]

for name, base_name in pairs:
    s = stats.get(name)
    if not s or s[0] < 1000: continue
    h2 = s[2] / s[0] * 100
    if base_name:
        sb = stats.get(base_name)
        if sb and sb[0] >= 1000:
            h2b = sb[2] / sb[0] * 100
            margin = h2 - h2b
            print(f'{name:<30s} H2={h2:.1f}%  (基准 {base_name}={h2b:.1f}%, 边际 +{margin:.1f}pp)')
    else:
        margin = h2 - base_h2
        print(f'{name:<30s} H2={h2:.1f}%  (全量基准={base_h2:.1f}%, 边际 +{margin:.1f}pp)')

print()
print('Done')