# -*- coding: utf-8 -*-
"""
位置坐标系分析 — 旧高波池口径（含Qin）
对比新高波池（不含Qin）看数据变化
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

# 旧高波池口径（含Qin）
CORE_OLD = {'Qic', 'Qim', 'Qit', 'Qin'}
# 新高波池口径（不含Qin）
CORE_NEW = {'Qic', 'Qim', 'Qit'}

HX_MAP = {'甲': '甲', '乙': '乙', '丙': '丙', '丁': '丁', '戊': '戊', '己': '己'}

stats_old = defaultdict(lambda: [0, 0, 0, 0])
stats_new = defaultdict(lambda: [0, 0, 0, 0])

def add(stats, key, nxt, h1, h2, h3):
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

files_old = 0
files_new = 0
total_old = 0
total_new = 0

for fname in os.listdir('昭明算展/谕组日'):
    code = fname.replace('谕组日_', '').replace('.csv', '')
    board = CODE2BOARD.get(code, '')
    in_old = board in CORE_OLD
    in_new = board in CORE_NEW
    if not in_old and not in_new:
        continue

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

                hit1 = 1 if nxt_gf >= 1 else 0
                hit2 = 1 if nxt_gf >= 2 else 0
                hit3 = 1 if nxt_gf >= 3 else 0

                cond_bsha5 = bsha > 5
                cond_ly = btly > 0
                cond_men = zc > 0 and cd == '上'
                cond_zc_pos = zc > 0

                # 旧策略组合
                conds = {
                    'D1': cls == 'D1',
                    'D2': cls == 'D2',
                    'D3': cls == 'D3',
                    'D5': cls == 'D5',
                    'D6': cls == 'D6',
                    'D7': cls == 'D7',
                    'D1_BSHA5': cond_bsha5 and cls == 'D1',
                    'D2_BSHA5': cond_bsha5 and cls == 'D2',
                    'D3_BSHA5': cond_bsha5 and cls == 'D3',
                    'D5_BSHA5': cond_bsha5 and cls == 'D5',
                    'D6_BSHA5': cond_bsha5 and cls == 'D6',
                    'D7_BSHA5': cond_bsha5 and cls == 'D7',
                    'D1_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D1',
                    'D2_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D2',
                    'D3_BSHA5_LY_MEN': cond_bsha5 and cond_ly and cond_men and cls == 'D3',
                    # 新策略位置基准
                    'D1_ZCp_A': cls == 'D1' and cond_zc_pos and hx == '甲',
                    'D2_ZCp_B': cls == 'D2' and cond_zc_pos and hx == '乙',
                    'D3_ZCp_B': cls == 'D3' and cond_zc_pos and hx == '乙',
                    'D5_ZCp_B': cls == 'D5' and cond_zc_pos and hx == '乙',
                    'D7_ZCp_C': cls == 'D7' and cond_zc_pos and hx == '丙',
                    # 新策略位置+BSHA5
                    'D1_ZCp_A_BSHA5': cls == 'D1' and cond_zc_pos and hx == '甲' and cond_bsha5,
                    'D2_ZCp_B_BSHA5': cls == 'D2' and cond_zc_pos and hx == '乙' and cond_bsha5,
                    'D3_ZCp_B_BSHA5': cls == 'D3' and cond_zc_pos and hx == '乙' and cond_bsha5,
                    'D5_ZCp_B_BSHA5': cls == 'D5' and cond_zc_pos and hx == '乙' and cond_bsha5,
                    'D1_ZCp_A_BSHA5_LY': cls == 'D1' and cond_zc_pos and hx == '甲' and cond_bsha5 and cond_ly,
                    'D2_ZCp_B_BSHA5_LY': cls == 'D2' and cond_zc_pos and hx == '乙' and cond_bsha5 and cond_ly,
                    'D3_ZCp_B_BSHA5_LY': cls == 'D3' and cond_zc_pos and hx == '乙' and cond_bsha5 and cond_ly,
                    'D5_ZCp_B_BSHA5_LY': cls == 'D5' and cond_zc_pos and hx == '乙' and cond_bsha5 and cond_ly,
                }
                for cname, cval in conds.items():
                    if cval:
                        if in_old:
                            add(stats_old, cname, nxt_gf, hit1, hit2, hit3)
                            if in_old and not in_new:
                                pass  # 仅旧口径
                        if in_new:
                            add(stats_new, cname, nxt_gf, hit1, hit2, hit3)
        if in_old: files_old += 1
        if in_new: files_new += 1
    except Exception:
        pass

NAME_MAP = {
    'D1': '等1基准', 'D2': '等2基准', 'D3': '等3基准',
    'D5': '等5基准', 'D6': '等6基准', 'D7': '等7基准',
    'D1_BSHA5': '等1+BSHA5', 'D2_BSHA5': '等2+BSHA5', 'D3_BSHA5': '等3+BSHA5',
    'D5_BSHA5': '等5+BSHA5', 'D6_BSHA5': '等6+BSHA5', 'D7_BSHA5': '等7+BSHA5',
    'D1_BSHA5_LY_MEN': '等1+BSHA5+连+门',
    'D2_BSHA5_LY_MEN': '等2+BSHA5+连+门',
    'D3_BSHA5_LY_MEN': '等3+BSHA5+连+门',
    'D1_ZCp_A': '等1+ZC>0+甲',
    'D2_ZCp_B': '等2+ZC>0+乙',
    'D3_ZCp_B': '等3+ZC>0+乙',
    'D5_ZCp_B': '等5+ZC>0+乙',
    'D7_ZCp_C': '等7+ZC>0+丙',
    'D1_ZCp_A_BSHA5': '等1+ZC>0+甲+BSHA5',
    'D2_ZCp_B_BSHA5': '等2+ZC>0+乙+BSHA5',
    'D3_ZCp_B_BSHA5': '等3+ZC>0+乙+BSHA5',
    'D5_ZCp_B_BSHA5': '等5+ZC>0+乙+BSHA5',
    'D1_ZCp_A_BSHA5_LY': '等1+ZC>0+甲+BSHA5+连',
    'D2_ZCp_B_BSHA5_LY': '等2+ZC>0+乙+BSHA5+连',
    'D3_ZCp_B_BSHA5_LY': '等3+ZC>0+乙+BSHA5+连',
    'D5_ZCp_B_BSHA5_LY': '等5+ZC>0+乙+BSHA5+连',
}

print('=' * 110)
print('新旧高波池口径对比（含Qin vs 不含Qin）')
print('=' * 110)
print()
print(f'旧高波池（含Qin）: {files_old} 文件')
print(f'新高波池（不含Qin）: {files_new} 文件')
print()

# 输出对比表
print(f'{"策略":<35s} {"旧H2":>8s} {"旧样本":>10s} {"新H2":>8s} {"新样本":>10s} {"H2差":>8s}')
print('-' * 85)

keys = list(NAME_MAP.keys())
rows = []
for k in keys:
    so = stats_old.get(k)
    sn = stats_new.get(k)
    if so and sn and so[0] >= 1000 and sn[0] >= 1000:
        h2o = so[2] / so[0] * 100
        h2n = sn[2] / sn[0] * 100
        diff = h2o - h2n
        rows.append((diff, k, h2o, so[0], h2n, sn[0]))

# 按H2差排序
rows.sort(key=lambda x: -abs(x[0]))
for diff, k, h2o, no, h2n, nn in rows:
    name = NAME_MAP[k]
    print(f'{name:<35s} {h2o:>7.1f}% {no:>10,} {h2n:>7.1f}% {nn:>10,} {diff:>+7.2f}pp')

print()
print('=' * 110)
print('结论')
print('=' * 110)
print()
print('H2差 > 0 = 旧口径（含Qin）更高')
print('H2差 < 0 = 新口径（不含Qin）更高')
print()
print('如果差异 < 0.5pp，说明Qin不影响结论')
print('如果差异 > 1.0pp，说明Qin有显著影响')