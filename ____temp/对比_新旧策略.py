# -*- coding: utf-8 -*-
"""新旧策略直接对比（同口径）"""
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
                cond_men = zc > 0 and cd == '上'
                cond_zc_pos = zc > 0

                # 旧策略组合
                conds = {
                    'OLD_D1': cls == 'D1',
                    'OLD_D2': cls == 'D2',
                    'OLD_D3': cls == 'D3',
                    'OLD_D5': cls == 'D5',
                    'OLD_D6': cls == 'D6',
                    'OLD_D7': cls == 'D7',
                    'OLD_D1_BSHA5': cond_bsha5 and cls == 'D1',
                    'OLD_D2_BSHA5': cond_bsha5 and cls == 'D2',
                    'OLD_D3_BSHA5': cond_bsha5 and cls == 'D3',
                    'OLD_D5_BSHA5': cond_bsha5 and cls == 'D5',
                    'OLD_D6_BSHA5': cond_bsha5 and cls == 'D6',
                    'OLD_D7_BSHA5': cond_bsha5 and cls == 'D7',
                    'OLD_D1_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D1',
                    'OLD_D2_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D2',
                    'OLD_D3_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D3',

                    # 新策略组合
                    'NEW_D1_ZCp_A': cls == 'D1' and cond_zc_pos and hx == '甲',
                    'NEW_D2_ZCp_B': cls == 'D2' and cond_zc_pos and hx == '乙',
                    'NEW_D3_ZCp_B': cls == 'D3' and cond_zc_pos and hx == '乙',
                    'NEW_D5_ZCp_B': cls == 'D5' and cond_zc_pos and hx == '乙',
                    'NEW_D7_ZCp_C': cls == 'D7' and cond_zc_pos and hx == '丙',
                    'NEW_D1_ZCp_A_BSHA5': cls == 'D1' and cond_zc_pos and hx == '甲' and cond_bsha5,
                    'NEW_D2_ZCp_B_BSHA5': cls == 'D2' and cond_zc_pos and hx == '乙' and cond_bsha5,
                    'NEW_D3_ZCp_B_BSHA5': cls == 'D3' and cond_zc_pos and hx == '乙' and cond_bsha5,
                    'NEW_D5_ZCp_B_BSHA5': cls == 'D5' and cond_zc_pos and hx == '乙' and cond_bsha5,
                    'NEW_D1_ZCp_A_BSHA5_LY': cls == 'D1' and cond_zc_pos and hx == '甲' and cond_bsha5 and cond_ly,
                    'NEW_D2_ZCp_B_BSHA5_LY': cls == 'D2' and cond_zc_pos and hx == '乙' and cond_bsha5 and cond_ly,
                    'NEW_D3_ZCp_B_BSHA5_LY': cls == 'D3' and cond_zc_pos and hx == '乙' and cond_bsha5 and cond_ly,
                    'NEW_D5_ZCp_B_BSHA5_LY': cls == 'D5' and cond_zc_pos and hx == '乙' and cond_bsha5 and cond_ly,
                }
                for cname, cval in conds.items():
                    if cval:
                        add(cname, nxt_gf, hit1, hit2, hit3)
    except Exception:
        pass

NAME_MAP = {
    'OLD_D1': '【旧】等1基准',
    'OLD_D2': '【旧】等2基准',
    'OLD_D3': '【旧】等3基准',
    'OLD_D5': '【旧】等5基准',
    'OLD_D6': '【旧】等6基准',
    'OLD_D7': '【旧】等7基准',
    'OLD_D1_BSHA5': '【旧】等1+BSHA5',
    'OLD_D2_BSHA5': '【旧】等2+BSHA5',
    'OLD_D3_BSHA5': '【旧】等3+BSHA5',
    'OLD_D5_BSHA5': '【旧】等5+BSHA5',
    'OLD_D6_BSHA5': '【旧】等6+BSHA5',
    'OLD_D7_BSHA5': '【旧】等7+BSHA5',
    'OLD_D1_BSHA5_LY_MEN': '【旧】等1+BSHA5+连+门',
    'OLD_D2_BSHA5_LY_MEN': '【旧】等2+BSHA5+连+门',
    'OLD_D3_BSHA5_LY_MEN': '【旧】等3+BSHA5+连+门',
    'NEW_D1_ZCp_A': '【新】等1+ZC>0+甲',
    'NEW_D2_ZCp_B': '【新】等2+ZC>0+乙',
    'NEW_D3_ZCp_B': '【新】等3+ZC>0+乙',
    'NEW_D5_ZCp_B': '【新】等5+ZC>0+乙',
    'NEW_D7_ZCp_C': '【新】等7+ZC>0+丙',
    'NEW_D1_ZCp_A_BSHA5': '【新】等1+ZC>0+甲+BSHA5',
    'NEW_D2_ZCp_B_BSHA5': '【新】等2+ZC>0+乙+BSHA5',
    'NEW_D3_ZCp_B_BSHA5': '【新】等3+ZC>0+乙+BSHA5',
    'NEW_D5_ZCp_B_BSHA5': '【新】等5+ZC>0+乙+BSHA5',
    'NEW_D1_ZCp_A_BSHA5_LY': '【新】等1+ZC>0+甲+BSHA5+连',
    'NEW_D2_ZCp_B_BSHA5_LY': '【新】等2+ZC>0+乙+BSHA5+连',
    'NEW_D3_ZCp_B_BSHA5_LY': '【新】等3+ZC>0+乙+BSHA5+连',
    'NEW_D5_ZCp_B_BSHA5_LY': '【新】等5+ZC>0+乙+BSHA5+连',
}

print(f'核心池文件: {files_core}, 总行数: {total_rows}')
print()
print('=' * 100)
print('新旧策略直接对比（同口径：高波池3451文件，下日高幅）')
print('=' * 100)
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
print('=' * 100)
print('对比总结')
print('=' * 100)
print()
print('旧策略优势：')
print('  - 等型基准样本量大（等1=146万 vs 新策略等1+ZC>0+甲=5.4万）')
print('  - BSHA5+连+门 组合稳定（等1=59.9%/9万样本）')
print('  - 简单直接，按等型分组即可操作')
print()
print('新策略优势：')
print('  - 位置坐标系提供相对位置概念（ZC/DXAB/等型三维定位）')
print('  - 最优位置基准 H2 更高（等1+ZC>0+甲=45.8% vs 旧等1基准=38.8%）')
print('  - 等5+ZC>0+乙+BSHA5 是全场最强（61.5%/1.98万样本）')
print('  - 知道每个位置的基准和增强幅度，可精细化操作')
print()
print('本质区别：')
print('  旧策略：按等型分组 -> 叠加条件 -> 得到 H2')
print('  新策略：按 ZC x 护型 x 等型 定位 -> 知道位置基准 -> 再叠加 BSHA5')
print('  新策略多了一个维度（ZC+护型），但核心结论一致：BSHA5 是最强信号')