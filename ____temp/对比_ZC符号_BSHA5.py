# -*- coding: utf-8 -*-
"""ZC<0+BSHA5 vs ZC>0+BSHA5 对比"""
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
                btly = to_f(row[42]) if len(row) > 42 else 0.0
                bsha = to_f(row[19]) if len(row) > 19 else 0.0
                cx = row[33].strip()
                cd = row[8].strip()
                dxab = row[9].strip()

                cls = get_cls(dtza, cx)
                if cls is None: continue
                hx = parse_hx(dxab)
                if not hx: continue
                total_rows += 1

                hit1 = 1 if nxt_gf >= 1 else 0
                hit2 = 1 if nxt_gf >= 2 else 0
                hit3 = 1 if nxt_gf >= 3 else 0

                cond_bsha5 = bsha > 5
                cond_ly = btly > 0
                cond_zc_pos = zc > 0
                cond_zc_neg = zc <= 0

                cls_name = {'D1':'等1','D2':'等2','D3':'等3','D5':'等5','D6':'等6','D7':'等7'}[cls]

                # ZC>0+BSHA5
                if cond_zc_pos and cond_bsha5:
                    add(f'ZC>0+BSHA5|{cls_name}', nxt_gf, hit1, hit2, hit3)
                # ZC<0+BSHA5
                if cond_zc_neg and cond_bsha5:
                    add(f'ZC<0+BSHA5|{cls_name}', nxt_gf, hit1, hit2, hit3)
                # ZC>0+BSHA5+连
                if cond_zc_pos and cond_bsha5 and cond_ly:
                    add(f'ZC>0+BSHA5+连|{cls_name}', nxt_gf, hit1, hit2, hit3)
                # ZC<0+BSHA5+连
                if cond_zc_neg and cond_bsha5 and cond_ly:
                    add(f'ZC<0+BSHA5+连|{cls_name}', nxt_gf, hit1, hit2, hit3)
                # 全量汇总
                if cond_zc_pos and cond_bsha5:
                    add('ZC>0+BSHA5|全量', nxt_gf, hit1, hit2, hit3)
                if cond_zc_neg and cond_bsha5:
                    add('ZC<0+BSHA5|全量', nxt_gf, hit1, hit2, hit3)
    except Exception:
        pass

print(f'新高波池: {files_core} 文件, {total_rows} 行')
print()
print('=' * 100)
print('ZC>0+BSHA5 vs ZC<0+BSHA5 对比')
print('=' * 100)
print()
print(f'{"策略":<35s} {"样本":>10s} {"H1":>7s} {"H2":>7s} {"H3":>7s}')
print('-' * 70)

rows = []
for k, (n, h1, h2, h3) in stats.items():
    if n >= 200:
        p1 = h1 / n * 100
        p2 = h2 / n * 100
        p3 = h3 / n * 100
        rows.append((p2, k, n, p1, p3))

rows.sort(key=lambda x: (-x[0], -x[2]))
for p2, k, n, p1, p3 in rows:
    print(f'{k:<35s} {n:>10,} {p1:>6.1f}% {p2:>6.1f}% {p3:>6.1f}%')

print()
print('=' * 100)
print('对比总结')
print('=' * 100)
print()

# 计算每组的差异
for cls in ['等1','等2','等3','等5','等6','等7','全量']:
    zp = stats.get(f'ZC>0+BSHA5|{cls}')
    zn = stats.get(f'ZC<0+BSHA5|{cls}')
    if zp and zn and zp[0] >= 200 and zn[0] >= 200:
        h2p = zp[2] / zp[0] * 100
        h2n = zn[2] / zn[0] * 100
        diff = h2p - h2n
        print(f'{cls}: ZC>0+BSHA5={h2p:.1f}%(n={zp[0]:,}) vs ZC<0+BSHA5={h2n:.1f}%(n={zn[0]:,})  差={diff:+.1f}pp')
    elif zp and zp[0] >= 200:
        h2p = zp[2] / zp[0] * 100
        print(f'{cls}: ZC>0+BSHA5={h2p:.1f}%(n={zp[0]:,})  |  ZC<0+BSHA5: 样本不足')
    elif zn and zn[0] >= 200:
        h2n = zn[2] / zn[0] * 100
        print(f'{cls}: ZC>0+BSHA5: 样本不足  |  ZC<0+BSHA5={h2n:.1f}%(n={zn[0]:,})')

print()
print('Done')