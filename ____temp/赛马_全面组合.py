# -*- coding: utf-8 -*-
"""
日冲策略条件组合赛马 — 全面头脑风暴
===================================
探索 DXCD/DXZC/DXAB/日等型/BSHA/连阳/BT鼎 等条件的各种组合，
找出最优策略组合。

指标：下日高≥2%（H2），下日高≥3%（H3）
数据：高波池（Qic+Qim+Qit），全量文件
"""
import csv, os, sys, io
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

# 护型映射
HX_MAP = {'甲': '甲', '乙': '乙', '丙': '丙', '丁': '丁', '戊': '戊', '己': '己'}
HX_GOOD = {'甲', '乙', '己'}  # 好护型
HX_BAD = {'丙', '丁', '戊'}   # 差护型

stats = defaultdict(lambda: [0, 0, 0, 0])

def add(key, nxt, h1, h2, h3):
    stats[key][0] += 1
    stats[key][1] += h1
    stats[key][2] += h2
    stats[key][3] += h3

def get_cls(dtza, cx):
    if not cx: return None
    mf = cx[-1]
    if dtza == 1: return '等1'
    elif dtza >= 2: return '等3' if mf in ('A','B') else '等2'
    elif dtza == -1: return '等5'
    elif dtza <= -2: return '等7' if mf in ('E','F') else '等6'
    return None

def parse_hx(dxab):
    """从 DXAB 字符串提取护型"""
    if len(dxab) >= 2 and dxab[1] in HX_MAP:
        return dxab[1]
    return ''

def zc_seg(zc):
    """ZC 五段式"""
    if zc <= -2: return 'ZC深负'
    elif zc < 0: return 'ZC=-1'
    elif zc < 1: return 'ZC=0'
    elif zc < 5: return 'ZC1~4'
    else: return 'ZC≥5'

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
                dxef = row[7].strip() if len(row) > 7 else ''

                cls = get_cls(dtza, cx)
                if cls is None: continue
                hx = parse_hx(dxab)
                if not hx: continue
                total_rows += 1

                hit1 = 1 if nxt_gf >= 1 else 0
                hit2 = 1 if nxt_gf >= 2 else 0
                hit3 = 1 if nxt_gf >= 3 else 0

                # ===== 基础条件 =====
                cond_bsha5 = bsha > 5
                cond_bsha3 = bsha > 3
                cond_ly = btly > 0
                cond_men = zc > 0 and cd == '上'  # 原"门"条件
                cond_cz = cengjie.startswith('主')
                cond_btding = btding > 0
                cond_sp = bx.startswith('升')
                cond_ze_pos = ze > 0  # DJE上方
                cond_zc_pos = zc > 0  # ZC>0
                cond_zc_neg = zc <= 0  # ZC≤0
                cond_hx_good = hx in HX_GOOD  # 甲乙己
                cond_hx_bad = hx in HX_BAD   # 丙丁戊
                cond_ef_good = dxef in ('金','银','唏')  # DXEF好
                cond_ef_bad = dxef in ('嘘','尿','屎')   # DXEF差
                cond_cd_good = cd in ('上','中','忐')    # DXCD好
                cond_cd_bad = cd in ('下','忠','忑')     # DXCD差

                # ===== 组合条件 =====
                conds = {
                    # --- 基准 ---
                    '基准': True,

                    # --- 单条件 ---
                    '偏5': cond_bsha5,
                    '偏3': cond_bsha3,
                    '连': cond_ly,
                    '门': cond_men,
                    '层主': cond_cz,
                    'BT鼎': cond_btding,
                    '升排': cond_sp,
                    'ZE>0': cond_ze_pos,
                    'ZC>0': cond_zc_pos,
                    '甲乙己': cond_hx_good,
                    'EF好': cond_ef_good,
                    'CD好': cond_cd_good,

                    # --- 等型 + ZC ---
                    f'{cls}+ZC>0': cond_zc_pos,
                    f'{cls}+ZC≤0': cond_zc_neg,
                    f'{cls}+ZC深负': zc <= -2,
                    f'{cls}+ZC1~4': 1 <= zc < 5,
                    f'{cls}+ZC≥5': zc >= 5,

                    # --- 等型 + 护型 ---
                    f'{cls}+甲乙己': cond_hx_good,
                    f'{cls}+丙丁戊': cond_hx_bad,

                    # --- 等型 + ZC + 护型 ---
                    f'{cls}+ZC>0+甲乙己': cond_zc_pos and cond_hx_good,
                    f'{cls}+ZC>0+丙丁戊': cond_zc_pos and cond_hx_bad,
                    f'{cls}+ZC≤0+甲乙己': cond_zc_neg and cond_hx_good,
                    f'{cls}+ZC≤0+丙丁戊': cond_zc_neg and cond_hx_bad,

                    # --- 等型 + BSHA ---
                    f'{cls}+偏5': cond_bsha5,
                    f'{cls}+偏3': cond_bsha3,
                    f'{cls}+偏5+连': cond_bsha5 and cond_ly,
                    f'{cls}+偏5+门': cond_bsha5 and cond_men,
                    f'{cls}+偏5+连+门': cond_bsha5 and cond_ly and cond_men,

                    # --- 等型 + ZC + BSHA ---
                    f'{cls}+ZC>0+偏5': cond_zc_pos and cond_bsha5,
                    f'{cls}+ZC>0+偏5+连': cond_zc_pos and cond_bsha5 and cond_ly,
                    f'{cls}+ZC1~4+偏5': (1 <= zc < 5) and cond_bsha5,

                    # --- 等型 + 护型 + BSHA ---
                    f'{cls}+甲乙己+偏5': cond_hx_good and cond_bsha5,
                    f'{cls}+甲乙己+偏5+连': cond_hx_good and cond_bsha5 and cond_ly,

                    # --- 等型 + 护型 + ZC + BSHA ---
                    f'{cls}+甲乙己+ZC>0+偏5': cond_hx_good and cond_zc_pos and cond_bsha5,
                    f'{cls}+甲乙己+ZC>0+偏5+连': cond_hx_good and cond_zc_pos and cond_bsha5 and cond_ly,

                    # --- 护型 + ZC ---
                    f'{hx}+ZC>0': cond_zc_pos,
                    f'{hx}+ZC≤0': cond_zc_neg,
                    f'{hx}+ZC深负': zc <= -2,
                    f'{hx}+ZC1~4': 1 <= zc < 5,
                    f'{hx}+ZC≥5': zc >= 5,
                    f'甲乙己+ZC>0': cond_hx_good and cond_zc_pos,
                    f'甲乙己+ZC≤0': cond_hx_good and cond_zc_neg,
                    f'丙丁戊+ZC>0': cond_hx_bad and cond_zc_pos,
                    f'丙丁戊+ZC≤0': cond_hx_bad and cond_zc_neg,

                    # --- 护型 + BSHA ---
                    f'{hx}+偏5': cond_bsha5,
                    f'{hx}+偏5+连': cond_bsha5 and cond_ly,
                    f'甲乙己+偏5': cond_hx_good and cond_bsha5,
                    f'甲乙己+偏5+连': cond_hx_good and cond_bsha5 and cond_ly,

                    # --- 护型 + ZC + BSHA ---
                    f'{hx}+ZC>0+偏5': cond_zc_pos and cond_bsha5,
                    f'甲乙己+ZC>0+偏5': cond_hx_good and cond_zc_pos and cond_bsha5,
                    f'甲乙己+ZC>0+偏5+连': cond_hx_good and cond_zc_pos and cond_bsha5 and cond_ly,

                    # --- DXEF + DXCD + 等型 ---
                    f'EF好+CD好+{cls}': cond_ef_good and cond_cd_good,
                    f'EF好+CD好+{cls}+甲乙己': cond_ef_good and cond_cd_good and cond_hx_good,
                    f'EF好+CD好+{cls}+ZC>0': cond_ef_good and cond_cd_good and cond_zc_pos,

                    # --- 等型 + 层主 ---
                    f'{cls}+层主': cond_cz,
                    f'{cls}+层主+门': cond_cz and cond_men,
                    f'{cls}+层主+升排': cond_cz and cond_sp,

                    # --- 等型 + BT鼎 ---
                    f'{cls}+BT鼎': cond_btding,
                    f'{cls}+BT鼎+门': cond_btding and cond_men,

                    # --- 等型 + 升排 ---
                    f'{cls}+升排': cond_sp,
                    f'{cls}+升排+门': cond_sp and cond_men,

                    # --- 等型 + 连 ---
                    f'{cls}+连': cond_ly,
                    f'{cls}+连+门': cond_ly and cond_men,

                    # --- 等型 + ZC五段 ---
                    f'{cls}+ZC深负': zc <= -2,
                    f'{cls}+ZC=-1': -2 < zc < 0,
                    f'{cls}+ZC1~4': 1 <= zc < 5,
                    f'{cls}+ZC≥5': zc >= 5,
                }
                for cname, cval in conds.items():
                    if cval:
                        add(cname, nxt_gf, hit1, hit2, hit3)
    except Exception:
        pass

# ===== 输出 =====
BENCH = 37.1  # 全量基准 H2
MIN_N = 1000

rows = []
for k, (n, h1, h2, h3) in stats.items():
    p1 = h1 / n * 100 if n else 0
    p2 = h2 / n * 100 if n else 0
    p3 = h3 / n * 100 if n else 0
    if n >= MIN_N:
        rows.append((p2, k, n, p1, p3))

rows.sort(key=lambda x: (-x[0], -x[2]))

print(f'核心池文件: {files_core}, 总行数: {total_rows}')
print(f'策略数: {len(rows)}')
print()
print(f'=== 全量赛马排名（H2 ≥ {BENCH}%，n≥{MIN_N}）===')
print(f'{"排名":>4s} {"策略":<40s} {"样本":>10s} {"H1":>7s} {"H2":>7s} {"H3":>7s}')
print('-' * 78)

for i, (p2, k, n, p1, p3) in enumerate(rows, 1):
    if p2 >= BENCH:
        print(f'{i:>4d} {k:<40s} {n:>10,} {p1:>6.1f}% {p2:>6.1f}% {p3:>6.1f}%')

print()
print(f'=== 低于基准（H2 < {BENCH}%，n≥{MIN_N}）===')
for i, (p2, k, n, p1, p3) in enumerate(rows, 1):
    if p2 < BENCH:
        print(f'{i:>4d} {k:<40s} {n:>10,} {p1:>6.1f}% {p2:>6.1f}% {p3:>6.1f}%')
    if i > 200:  # 只显示前200个低于基准的
        print(f'  ... 还有 {len(rows)-200} 个')
        break

print(f'\nDone: {len(rows)} strategies, {total_rows} rows, {files_core} files')