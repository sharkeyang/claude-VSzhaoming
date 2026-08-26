# -*- coding: utf-8 -*-
"""验证周地型 vs 周等型是否信息等价（独立维度）"""
import os, csv, json
from collections import defaultdict

board_map = json.load(open('_产出物/MP1_花册分类映射.json', 'r', encoding='utf-8'))
高波池 = {'Qic','Qim','Qit'}
files = sorted(os.listdir('昭明算展/谕组周0825'))
files = [f for f in files if f.startswith('谕组周_') and f.endswith('.csv')]
gb_files = [f for f in files if board_map.get(f.replace('谕组周_','').replace('.csv',''), '') in 高波池]

def parse_地型(波型):
    if not 波型: return None
    parts = 波型.split('.')
    if len(parts) < 1: return None
    return parts[0]

def parse_等型(za, 中符串):
    try: za_f = float(za)
    except: return None
    if not 中符串: return None
    末位 = 中符串.strip()[-1] if 中符串.strip() else ''
    if za_f == 1: return '等1'
    elif za_f >= 2:
        return '等2' if 末位 in 'CDEF' else '等3'
    elif za_f == -1: return '等5'
    elif za_f <= -2:
        return '等6' if 末位 in 'ABCD' else '等7'
    return None

# 统计：地型×等型 交叉分布 + 各自P3
cross = defaultdict(lambda: {'n':0, 'p3':0})
地型_p3 = defaultdict(lambda: {'n':0, 'p3':0})
等型_p3 = defaultdict(lambda: {'n':0, 'p3':0})

count = 0
for fname in gb_files:
    count += 1
    if count % 500 == 0: print(f'  [{count}/{len(gb_files)}]...')
    with open(os.path.join('昭明算展/谕组周0825', fname), 'r', encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        header = next(r)
        rows = list(r)
        for i, row in enumerate(rows):
            if len(row) < 53: continue
            波型, za, 中符串 = row[5], row[14], row[45]
            if i+1 >= len(rows): continue
            nxt = rows[i+1]
            if len(nxt) < 4: continue
            try: nxt_hr = float(nxt[3])
            except: continue
            p3 = 1 if nxt_hr >= 3 else 0
            地型 = parse_地型(波型)
            等型 = parse_等型(za, 中符串)
            if not 地型 or not 等型: continue
            cross[(地型, 等型)]['n'] += 1
            cross[(地型, 等型)]['p3'] += p3
            地型_p3[地型]['n'] += 1
            地型_p3[地型]['p3'] += p3
            等型_p3[等型]['n'] += 1
            等型_p3[等型]['p3'] += p3

with open('____temp/_地型等型.txt', 'w', encoding='utf-8') as out:
    out.write('='*100 + '\n')
    out.write('周地型 vs 周等型：是否信息等价？\n')
    out.write('='*100 + '\n\n')

    # 1. 各自区分度
    out.write('【各自区分度】\n')
    地型_items = [(k, v['n'], v['p3']/v['n']*100) for k, v in 地型_p3.items() if v['n'] >= 100]
    地型_items.sort(key=lambda x: -x[2])
    等型_items = [(k, v['n'], v['p3']/v['n']*100) for k, v in 等型_p3.items() if v['n'] >= 100]
    等型_items.sort(key=lambda x: -x[2])
    out.write(f'  地型: {地型_items[0][2]-地型_items[-1][2]:.1f}pp（{地型_items[0][0]}={地型_items[0][2]:.1f}% vs {地型_items[-1][0]}={地型_items[-1][2]:.1f}%）\n')
    out.write(f'  等型: {等型_items[0][2]-等型_items[-1][2]:.1f}pp（{等型_items[0][0]}={等型_items[0][2]:.1f}% vs {等型_items[-1][0]}={等型_items[-1][2]:.1f}%）\n')

    # 2. 交叉分布：地型×等型 是否独立
    out.write('\n【地型×等型 交叉分布（样本≥1000）】\n')
    out.write('| 地型 | 等型 | 样本 | P3 |\n')
    out.write('|:----:|:----:|:----:|:--:|\n')
    for (地型, 等型), v in sorted(cross.items(), key=lambda x: -x[1]['n']):
        if v['n'] < 1000: continue
        out.write(f'| {地型} | {等型} | {v["n"]:,} | {v["p3"]/v["n"]*100:.1f}% |\n')

    # 3. 组合区分度 vs 单独区分度
    out.write('\n【组合区分度 vs 单独区分度】\n')
    combo_items = [(k, v['n'], v['p3']/v['n']*100) for k, v in cross.items() if v['n'] >= 100]
    combo_items.sort(key=lambda x: -x[2])
    if combo_items:
        out.write(f'  地型×等型组合: {combo_items[0][2]-combo_items[-1][2]:.1f}pp（{combo_items[0][0]}={combo_items[0][2]:.1f}% vs {combo_items[-1][0]}={combo_items[-1][2]:.1f}%）\n')
        out.write(f'  地型单独: {地型_items[0][2]-地型_items[-1][2]:.1f}pp\n')
        out.write(f'  等型单独: {等型_items[0][2]-等型_items[-1][2]:.1f}pp\n')
        out.write(f'  组合增量: {combo_items[0][2]-combo_items[-1][2] - max(地型_items[0][2]-地型_items[-1][2], 等型_items[0][2]-等型_items[-1][2]):.1f}pp\n')

print('done')