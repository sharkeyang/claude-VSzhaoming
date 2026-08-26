# -*- coding: utf-8 -*-
"""验证：周地型×周等型×周柱排×周顶型 能否完整描述 WXAB护型(甲/乙ZA>0)"""
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

def parse_地型(波型):
    if not 波型: return None
    parts = 波型.split('.')
    if len(parts) < 1: return None
    return parts[0]

def parse_等型(za, 中符串):
    """周等型：周ZA + 周中符串末位"""
    try: za_f = float(za)
    except: return None
    # 中符串末位
    if not 中符串: return None
    末位 = 中符串.strip()[-1] if 中符串.strip() else ''
    if za_f == 1:
        return '等1'
    elif za_f >= 2:
        if 末位 in 'CDEF': return '等2'
        elif 末位 in 'AB': return '等3'
        else: return '等3'  # 兜底
    elif za_f == -1:
        return '等5'
    elif za_f <= -2:
        if 末位 in 'ABCD': return '等6'
        elif 末位 in 'EF': return '等7'
        else: return '等7'  # 兜底
    return None

def parse_柱排(柱排周):
    if not 柱排周: return None
    c = 柱排周[0]
    if c in '升人跌': return c
    return None

def parse_顶型(顶周, 合顶周):
    try: 顶 = int(顶周)
    except: 顶 = 0
    try: 合顶 = int(合顶周)
    except: 合顶 = 0
    触顶 = '触顶' if 顶 > 0 else '未触'
    合顶 = '合顶' if 合顶 > 0 else '未合'
    return f'{触顶}.{合顶}'

# 统计：四维组合 → 护型分布
combo_hx = defaultdict(lambda: defaultdict(int))
combo_total = defaultdict(int)

count = 0
for fname in gb_files:
    count += 1
    if count % 500 == 0: print(f'  [{count}/{len(gb_files)}]...')
    with open(os.path.join('昭明算展/谕组周0825', fname), 'r', encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        header = next(r)
        for row in r:
            if len(row) < 53: continue
            wxab, 波型, 柱排周, 顶周, 合顶周, za, 中符串 = row[4], row[5], row[6], row[33], row[35], row[14], row[45]
            if len(wxab) < 2: continue
            cur = hx_key(wxab, za)
            if not cur: continue
            if cur not in ['甲', '乙(ZA>0)']: continue
            地型 = parse_地型(波型)
            等型 = parse_等型(za, 中符串)
            柱排 = parse_柱排(柱排周)
            顶型 = parse_顶型(顶周, 合顶周)
            if not 地型 or not 等型 or not 柱排 or not 顶型: continue
            key = (地型, 等型, 柱排, 顶型)
            combo_hx[key][cur] += 1
            combo_total[key] += 1

# 输出到文件
with open('____temp/_4dim_result.txt', 'w', encoding='utf-8') as out:
    out.write('='*110 + '\n')
    out.write('四维组合（地型×等型×柱排×顶型）→ 甲/乙(ZA>0) 分布\n')
    out.write('='*110 + '\n\n')
    out.write('| 地型 | 等型 | 柱排 | 顶型 | 总样本 | 甲占比 | 乙(ZA>0)占比 | 主导 |\n')
    out.write('|:----:|:----:|:----:|:----:|:------:|:------:|:-----------:|:----:|\n')
    for key, total in sorted(combo_total.items(), key=lambda x: -x[1]):
        if total < 100: continue
        地型, 等型, 柱排, 顶型 = key
        甲 = combo_hx[key]['甲']
        乙 = combo_hx[key]['乙(ZA>0)']
        甲pct = 甲/total*100
        乙pct = 乙/total*100
        主导 = '甲' if 甲 > 乙 else '乙(ZA>0)'
        out.write(f'| {地型} | {等型} | {柱排} | {顶型} | {total:,} | {甲pct:.1f}% | {乙pct:.1f}% | {主导} |\n')

    # 汇总：四维组合能否唯一确定护型？
    out.write('\n\n' + '='*110 + '\n')
    out.write('汇总分析：四维组合能否唯一确定护型？\n')
    out.write('='*110 + '\n\n')
    # 统计主导护型占比分布
    主导占比 = defaultdict(int)
    for key, total in combo_total.items():
        if total < 100: continue
        甲 = combo_hx[key]['甲']
        乙 = combo_hx[key]['乙(ZA>0)']
        主导pct = max(甲, 乙)/total*100
        # 分档
        if 主导pct >= 90: 档 = '≥90%（几乎唯一）'
        elif 主导pct >= 80: 档 = '80-90%（高度集中）'
        elif 主导pct >= 70: 档 = '70-80%（较集中）'
        elif 主导pct >= 60: 档 = '60-70%（中等）'
        else: 档 = '<60%（分散）'
        主导占比[档] += 1
    out.write('四维组合的主导护型占比分布（样本≥100的组合数）：\n')
    for 档 in ['≥90%（几乎唯一）', '80-90%（高度集中）', '70-80%（较集中）', '60-70%（中等）', '<60%（分散）']:
        out.write(f'  {档}: {主导占比[档]} 个组合\n')

    # 各维度单独区分度
    out.write('\n\n' + '='*110 + '\n')
    out.write('各维度单独区分度（甲 vs 乙(ZA>0)）\n')
    out.write('='*110 + '\n\n')
    # 地型
    out.write('【地型】\n')
    地型_hx = defaultdict(lambda: defaultdict(int))
    for key, total in combo_total.items():
        地型 = key[0]
        地型_hx[地型]['甲'] += combo_hx[key]['甲']
        地型_hx[地型]['乙(ZA>0)'] += combo_hx[key]['乙(ZA>0)']
    for 地型 in sorted(地型_hx.keys()):
        甲 = 地型_hx[地型]['甲']
        乙 = 地型_hx[地型]['乙(ZA>0)']
        total = 甲+乙
        if total < 100: continue
        out.write(f'  {地型}: 甲{甲/total*100:.1f}% vs 乙(ZA>0){乙/total*100:.1f}% (样本{total:,})\n')

    # 等型
    out.write('\n【等型】\n')
    等型_hx = defaultdict(lambda: defaultdict(int))
    for key, total in combo_total.items():
        等型 = key[1]
        等型_hx[等型]['甲'] += combo_hx[key]['甲']
        等型_hx[等型]['乙(ZA>0)'] += combo_hx[key]['乙(ZA>0)']
    for 等型 in sorted(等型_hx.keys()):
        甲 = 等型_hx[等型]['甲']
        乙 = 等型_hx[等型]['乙(ZA>0)']
        total = 甲+乙
        if total < 100: continue
        out.write(f'  {等型}: 甲{甲/total*100:.1f}% vs 乙(ZA>0){乙/total*100:.1f}% (样本{total:,})\n')

    # 柱排
    out.write('\n【柱排】\n')
    柱排_hx = defaultdict(lambda: defaultdict(int))
    for key, total in combo_total.items():
        柱排 = key[2]
        柱排_hx[柱排]['甲'] += combo_hx[key]['甲']
        柱排_hx[柱排]['乙(ZA>0)'] += combo_hx[key]['乙(ZA>0)']
    for 柱排 in sorted(柱排_hx.keys()):
        甲 = 柱排_hx[柱排]['甲']
        乙 = 柱排_hx[柱排]['乙(ZA>0)']
        total = 甲+乙
        if total < 100: continue
        out.write(f'  {柱排}: 甲{甲/total*100:.1f}% vs 乙(ZA>0){乙/total*100:.1f}% (样本{total:,})\n')

    # 顶型
    out.write('\n【顶型】\n')
    顶型_hx = defaultdict(lambda: defaultdict(int))
    for key, total in combo_total.items():
        顶型 = key[3]
        顶型_hx[顶型]['甲'] += combo_hx[key]['甲']
        顶型_hx[顶型]['乙(ZA>0)'] += combo_hx[key]['乙(ZA>0)']
    for 顶型 in sorted(顶型_hx.keys()):
        甲 = 顶型_hx[顶型]['甲']
        乙 = 顶型_hx[顶型]['乙(ZA>0)']
        total = 甲+乙
        if total < 100: continue
        out.write(f'  {顶型}: 甲{甲/total*100:.1f}% vs 乙(ZA>0){乙/total*100:.1f}% (样本{total:,})\n')

print('done')