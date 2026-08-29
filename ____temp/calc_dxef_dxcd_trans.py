# -*- coding: utf-8 -*-
"""计算 DXEF × DXCD 交叉下的护型转移矩阵，看 DXCD 在不同 DXEF 阶段是否表现不同"""
import csv, os, json, io
from collections import defaultdict

高波池板块 = {'Qic', 'Qim', 'Qit'}
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
DATA_DIR = '昭明算展/谕组日'
HX_MAP = {'a': '甲', 'b': '乙', 'c': '丙', 'z': '丁', 'y': '戊', 'r': '己'}
HX_ORDER = ['甲', '乙(ZA>0)', '乙(ZA≤0)', '丙', '丁', '戊(ZA>0)', '戊(ZA≤0)', '己']

def hx_key(dxab, za):
    if len(dxab) < 2:
        return None
    hx = HX_MAP.get(dxab[0])
    if not hx:
        return None
    try:
        za_f = float(za)
    except:
        za_f = 0
    if hx == '乙':
        return '乙(ZA>0)' if za_f > 0 else '乙(ZA≤0)'
    if hx == '戊':
        return '戊(ZA>0)' if za_f > 0 else '戊(ZA≤0)'
    return hx

def parse_mc(mc):
    if not mc or not mc.startswith('('):
        return None, None
    parts = mc.split('(')
    if len(parts) < 3:
        return None, None
    return parts[1][0], parts[2][0]

with open(BOARD_MAP_PATH, encoding='utf-8') as f:
    board_map = json.load(f)

files = sorted(os.listdir(DATA_DIR))
files = [f for f in files if f.startswith('谕组日_') and f.endswith('.csv')]

# (ef, cd, cur, nxt) -> count
trans = defaultdict(int)
for i, fname in enumerate(files):
    if i % 1000 == 0:
        print(f'  [加载] {i}/{len(files)}...')
    cidl = fname.replace('谕组日_', '').replace('.csv', '')
    if board_map.get(cidl, '') not in 高波池板块:
        continue
    with open(os.path.join(DATA_DIR, fname), encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        next(r)
        prev = None  # (hx, ef, cd)
        for row in r:
            if len(row) < 51:
                continue
            cur = hx_key(row[9], row[13])
            if not cur:
                prev = None
                continue
            ef, cd = parse_mc(row[50])
            if not ef or not cd:
                prev = None
                continue
            if prev:
                p_hx, p_ef, p_cd = prev
                trans[(p_ef, p_cd, p_hx, cur)] += 1
            prev = (cur, ef, cd)

out = io.open('____temp/_dxef_dxcd_trans.txt', 'w', encoding='utf-8')
def O(s=''):
    out.write(s + '\n')

EF = ['金', '银', '唏', '嘘', '尿', '屎']
CD = ['上', '中', '下', '忐', '忠', '忑']

# 对每个 DXCD 位置，看它在不同 DXEF 阶段的转移矩阵
# 关键指标：甲->甲 维持率、己->甲 升级率、丙->丁 恶化率
for cd in CD:
    O(f'===== DXCD={cd} 在不同 DXEF 阶段的转移 =====')
    O('| 指标 | 金 | 银 | 唏 | 嘘 | 尿 | 屎 | 极差 |')
    O('|:----|:----:|:----:|:----:|:----:|:----:|:----:|:----:|')
    # 甲->甲
    row = []
    for ef in EF:
        total = sum(v for (e, c, cur, nxt), v in trans.items() if e == ef and c == cd and cur == '甲')
        if total == 0:
            row.append('—')
        else:
            maint = trans.get((ef, cd, '甲', '甲'), 0) / total * 100
            row.append(f'{maint:.1f}%')
    O('| 甲→甲 | ' + ' | '.join(row) + ' |')
    # 己->甲
    row = []
    for ef in EF:
        total = sum(v for (e, c, cur, nxt), v in trans.items() if e == ef and c == cd and cur == '己')
        if total == 0:
            row.append('—')
        else:
            up = trans.get((ef, cd, '己', '甲'), 0) / total * 100
            row.append(f'{up:.1f}%')
    O('| 己→甲 | ' + ' | '.join(row) + ' |')
    # 丙->丁
    row = []
    for ef in EF:
        total = sum(v for (e, c, cur, nxt), v in trans.items() if e == ef and c == cd and cur == '丙')
        if total == 0:
            row.append('—')
        else:
            bad = trans.get((ef, cd, '丙', '丁'), 0) / total * 100
            row.append(f'{bad:.1f}%')
    O('| 丙→丁 | ' + ' | '.join(row) + ' |')
    O('')
out.close()
print('Done')