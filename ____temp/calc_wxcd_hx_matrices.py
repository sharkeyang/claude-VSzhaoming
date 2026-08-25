# -*- coding: utf-8 -*-
"""Calculate worsen/improve matrices for WXCD×护型"""
import os, csv, json
from collections import defaultdict

board_map = json.load(open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8'))
高波池 = {'Qic','Qim','Qit'}
files = sorted(os.listdir('昭明算展/谕组周0825'))
files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]
gb_files = [f for f in files if board_map.get(f.replace('谕组周_','').replace('.csv',''), '') in 高波池]

HX_MAP = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}

def hx_key(dxab, za):
    if len(dxab) < 2: return None
    c = dxab[0]
    if c not in HX_MAP: return None
    hx = HX_MAP[c]
    if hx in '乙戊':
        try: za_f = float(za)
        except: return None
        return f'{hx}(ZA>0)' if za_f > 0 else f'{hx}(ZA≤0)'
    return hx

# 转坏去向
BAD_PATHS = {
    '甲': ['乙(ZA≤0)', '丙', '丁'],
    '乙(ZA>0)': ['乙(ZA≤0)', '丙', '丁'],
    '乙(ZA≤0)': ['丙', '丁'],
    '丙': ['丁'],
    '丁': ['戊(ZA>0)', '戊(ZA≤0)'],
    '戊(ZA>0)': ['戊(ZA≤0)'],
    '戊(ZA≤0)': ['戊(ZA≤0)'],  # 已最差，维持也算转坏
    '己': ['戊(ZA>0)', '戊(ZA≤0)'],
}

# 转好去向：只算→甲或→乙(ZA>0)
GOOD_PATHS = {
    '甲': ['甲'],              # 维持自身
    '乙(ZA>0)': ['乙(ZA>0)'],  # 维持自身
    '乙(ZA≤0)': ['乙(ZA>0)', '甲'],
    '丙': ['甲', '乙(ZA>0)'],
    '丁': ['甲', '乙(ZA>0)'],
    '戊(ZA>0)': ['甲', '乙(ZA>0)'],
    '戊(ZA≤0)': ['甲', '乙(ZA>0)'],
    '己': ['甲', '乙(ZA>0)'],
}

stats = defaultdict(lambda: {'total':0, '转坏':0, '转好':0, '去向': defaultdict(int)})

count = 0
for fname in gb_files:
    count += 1
    if count % 500 == 0: print(f'  [{count}/{len(gb_files)}]...')
    with open(os.path.join('昭明算展/谕组周0825', fname), 'r', encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        header = next(r)
        prev = None
        for row in r:
            if len(row) < 27: continue
            dxab, za, zc = row[4], row[14], row[16]
            wxcd_full = row[13] if len(row) > 13 else ''
            if len(dxab) < 2: continue
            cur = hx_key(dxab, za)
            if not cur: continue
            try: zc_f = float(zc)
            except: continue
            zc_gt0 = zc_f > 0
            wxcd = wxcd_full[0] if wxcd_full and wxcd_full[0] in '金银唏嘘尿屎' else ''

            if prev is not None:
                p_hx, p_zc, p_wxcd = prev
                if p_wxcd and p_hx:
                    key = (p_wxcd, p_hx)
                    stats[key]['total'] += 1
                    stats[key]['去向'][cur] += 1
                    if cur in BAD_PATHS.get(p_hx, []):
                        stats[key]['转坏'] += 1
                    elif cur in GOOD_PATHS.get(p_hx, []):
                        stats[key]['转好'] += 1

            prev = (cur, zc_gt0, wxcd)

print()
print('='*120)
print('转坏率矩阵（按WXCD×护型）')
print('定义：当前护型向更差护型转移的概率')
print('='*120)
print()
print('| WXCD | 甲 | 乙(ZA>0) | 乙(ZA≤0) | 丙 | 丁 | 戊(ZA>0) | 戊(ZA≤0) | 己 |')
print('|:----:|:--:|:--------:|:--------:|:--:|:--:|:--------:|:--------:|:--:|')
for wxcd in ['金','银','唏','嘘','尿','屎']:
    vals = []
    for hx in ['甲','乙(ZA>0)','乙(ZA≤0)','丙','丁','戊(ZA>0)','戊(ZA≤0)','己']:
        s = stats[(wxcd, hx)]
        if s['total'] > 0:
            pct = s['转坏']/s['total']*100
            vals.append(f'{pct:.0f}')
        else:
            vals.append('-')
    print(f'| {wxcd} | ' + ' | '.join(vals) + ' |')

print()
print('='*120)
print('转好率矩阵（按WXCD×护型）')
print('定义：当前护型转为甲或乙(ZA>0)的概率')
print('甲/乙(ZA>0)的转好率=维持率（已最优）')
print('='*120)
print()
print('| WXCD | 甲 | 乙(ZA>0) | 乙(ZA≤0) | 丙 | 丁 | 戊(ZA>0) | 戊(ZA≤0) | 己 |')
print('|:----:|:--:|:--------:|:--------:|:--:|:--:|:--------:|:--------:|:--:|')
for wxcd in ['金','银','唏','嘘','尿','屎']:
    vals = []
    for hx in ['甲','乙(ZA>0)','乙(ZA≤0)','丙','丁','戊(ZA>0)','戊(ZA≤0)','己']:
        s = stats[(wxcd, hx)]
        if s['total'] > 0:
            pct = s['转好']/s['total']*100
            vals.append(f'{pct:.0f}')
        else:
            vals.append('-')
    print(f'| {wxcd} | ' + ' | '.join(vals) + ' |')

print()
print('='*120)
print('编码方案')
print('  周策分坏：W+转坏率取整（W=转坏率≥30%危险，_=安全）')
print('  周策分好：G+转好率取整（G=转好率≥30%值得关注，_=低于阈值）')
print('='*120)
print()
print('周策分坏编码表：')
print('| WXCD | 甲 | 乙(ZA>0) | 乙(ZA≤0) | 丙 | 丁 | 戊(ZA>0) | 戊(ZA≤0) | 己 |')
print('|:----:|:--:|:--------:|:--------:|:--:|:--:|:--------:|:--------:|:--:|')
for wxcd in ['金','银','唏','嘘','尿','屎']:
    vals = []
    for hx in ['甲','乙(ZA>0)','乙(ZA≤0)','丙','丁','戊(ZA>0)','戊(ZA≤0)','己']:
        s = stats[(wxcd, hx)]
        if s['total'] > 0:
            pct = s['转坏']/s['total']*100
            if pct >= 30:
                vals.append(f'W{pct:.0f}')
            else:
                vals.append(f'_{pct:.0f}')
        else:
            vals.append('-')
    print(f'| {wxcd} | ' + ' | '.join(vals) + ' |')

print()
print('周策分好编码表：')
print('| WXCD | 甲 | 乙(ZA>0) | 乙(ZA≤0) | 丙 | 丁 | 戊(ZA>0) | 戊(ZA≤0) | 己 |')
print('|:----:|:--:|:--------:|:--------:|:--:|:--:|:--------:|:--------:|:--:|')
for wxcd in ['金','银','唏','嘘','尿','屎']:
    vals = []
    for hx in ['甲','乙(ZA>0)','乙(ZA≤0)','丙','丁','戊(ZA>0)','戊(ZA≤0)','己']:
        s = stats[(wxcd, hx)]
        if s['total'] > 0:
            pct = s['转好']/s['total']*100
            if pct >= 30:
                vals.append(f'G{pct:.0f}')
            else:
                vals.append(f'_{pct:.0f}')
        else:
            vals.append('-')
    print(f'| {wxcd} | ' + ' | '.join(vals) + ' |')