# -*- coding: utf-8 -*-
"""
日冲策略位置坐标系 — DXZC/DXAB/等型 三维定位
============================================
核心思路：用 DXZC/DXAB/等型 构建位置坐标系，
在每个位置内评估 BSHA/连阳 的增强效果。

输出：每个位置的 H2 基准 + BSHA5 增强 + BSHA5+连 增强
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
                dxef = row[7].strip() if len(row) > 7 else ''

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
                cond_zc_pos = zc > 0
                cond_zc_neg = zc <= 0
                cond_hx_good = hx in HX_GOOD
                cond_hx_bad = hx in HX_BAD
                cond_ef_good = dxef in ('金','银','唏')
                cond_ef_bad = dxef in ('嘘','尿','屎')
                cond_cd_good = cd in ('上','中','忐')
                cond_cd_bad = cd in ('下','忠','忑')

                # ===== 位置坐标系 =====
                # 维度1: 等型（DJA位置）
                # 维度2: ZC符号（DJC位置）
                # 维度3: 护型（DXAB质量）
                # 在每个位置内，评估 BSHA5/连阳 的增强

                # 位置键
                zc_label = 'ZC>0' if cond_zc_pos else 'ZC<0'
                pos = f'{cls}|{zc_label}|{hx}'

                # 基准（该位置所有样本）
                add(f'基准|{pos}', nxt_gf, hit1, hit2, hit3)
                # BSHA5 增强
                if cond_bsha5:
                    add(f'BSHA5|{pos}', nxt_gf, hit1, hit2, hit3)
                # BSHA5+连 增强
                if cond_bsha5 and cond_ly:
                    add(f'BSHA5+连|{pos}', nxt_gf, hit1, hit2, hit3)
                # 连 增强
                if cond_ly:
                    add(f'连|{pos}', nxt_gf, hit1, hit2, hit3)

                # 也记录跨等型的汇总
                pos2 = f'{zc_label}|{hx}'
                add(f'基准|{pos2}', nxt_gf, hit1, hit2, hit3)
                if cond_bsha5:
                    add(f'BSHA5|{pos2}', nxt_gf, hit1, hit2, hit3)
                if cond_bsha5 and cond_ly:
                    add(f'BSHA5+连|{pos2}', nxt_gf, hit1, hit2, hit3)
    except Exception:
        pass

# ===== 输出 =====
MIN_N = 500

# 按等型分组输出
等型名 = {'D1':'等1','D2':'等2','D3':'等3','D5':'等5','D6':'等6','D7':'等7'}
护型序 = ['甲','乙','丙','丁','戊','己']

print(f'核心池文件: {files_core}, 总行数: {total_rows}')
print()
print('=' * 110)
print('日冲策略位置坐标系 — 每个位置内 BSHA5/连阳 的增强效果')
print('=' * 110)
print()
print('格式: H2%(样本) | 基准 → BSHA5 → BSHA5+连 → 连')
print()

for cls_code, cls_name in 等型名.items():
    print(f'--- {cls_name} ---')
    print(f'{"ZC":>4} {"护型":>4} {"基准H2":>20} {"→BSHA5":>20} {"→BSHA5+连":>20} {"→连":>20}')
    print('-' * 90)
    for zc_label in ['ZC>0', 'ZC<0']:
        for hx in 护型序:
            pos = f'{cls_code}|{zc_label}|{hx}'
            base = stats.get(f'基准|{pos}')
            b5 = stats.get(f'BSHA5|{pos}')
            b5ly = stats.get(f'BSHA5+连|{pos}')
            ly = stats.get(f'连|{pos}')

            def fmt(s):
                if s and s[0] >= MIN_N:
                    p2 = s[2] / s[0] * 100
                    return f'{p2:.1f}%({s[0]:,})'
                return '-'

            print(f'{zc_label:>4} {hx:>4} {fmt(base):>20} {fmt(b5):>20} {fmt(b5ly):>20} {fmt(ly):>20}')
    print()

# 跨等型汇总
print()
print('=' * 110)
print('跨等型汇总 — ZC × 护型 位置坐标系')
print('=' * 110)
print()
print(f'{"ZC":>4} {"护型":>4} {"基准H2":>20} {"→BSHA5":>20} {"→BSHA5+连":>20} {"→连":>20}')
print('-' * 70)
for zc_label in ['ZC>0', 'ZC<0']:
    for hx in 护型序:
        pos = f'{zc_label}|{hx}'
        base = stats.get(f'基准|{pos}')
        b5 = stats.get(f'BSHA5|{pos}')
        b5ly = stats.get(f'BSHA5+连|{pos}')
        ly = stats.get(f'连|{pos}')

        def fmt(s):
            if s and s[0] >= MIN_N:
                p2 = s[2] / s[0] * 100
                return f'{p2:.1f}%({s[0]:,})'
            return '-'

        print(f'{zc_label:>4} {hx:>4} {fmt(base):>20} {fmt(b5):>20} {fmt(b5ly):>20} {fmt(ly):>20}')

print()
print('Done')