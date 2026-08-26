# -*- coding: utf-8 -*-
"""验证新框架（周地型×周柱型×周柱排×周顶型）能否替代原文框架"""
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

def parse_柱排(柱排周):
    if not 柱排周: return None
    c = 柱排周[0]
    if c in '升人跌': return c
    return None

def parse_柱型(柱型周):
    """柱型周格式 '.44枝贯连待X'，第4字符是柱型分类"""
    if not 柱型周: return None
    s = 柱型周.strip()
    if len(s) < 4: return None
    c = s[3]
    if c in '梯栅枝根杂': return c
    return None

def parse_顶型(顶周, 合顶周):
    try: 顶 = int(顶周)
    except: 顶 = 0
    try: 合顶 = int(合顶周)
    except: 合顶 = 0
    触顶 = '触顶' if 顶 > 0 else '未触'
    合顶 = '合顶' if 合顶 > 0 else '未合'
    return f'{触顶}.{合顶}'

def parse_波型主类(波型):
    if not 波型: return None
    parts = 波型.split('.')
    if len(parts) < 2: return None
    return parts[1]

# 统计各维度 → 下周P3（HR≥3%）
# 用下周HR≥3%作为P3近似
dim_stats = {
    '地型': defaultdict(lambda: {'n':0, 'p3':0}),
    '等型': defaultdict(lambda: {'n':0, 'p3':0}),
    '柱排': defaultdict(lambda: {'n':0, 'p3':0}),
    '柱型': defaultdict(lambda: {'n':0, 'p3':0}),
    '顶型': defaultdict(lambda: {'n':0, 'p3':0}),
    '波型主类': defaultdict(lambda: {'n':0, 'p3':0}),
}

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
            波型, 柱排周, 柱型周, 顶周, 合顶周, za, 中符串 = row[5], row[6], row[7], row[33], row[35], row[14], row[45]
            # 下周P3（下一行HR≥3%）
            if i+1 >= len(rows): continue
            nxt = rows[i+1]
            if len(nxt) < 4: continue
            try: nxt_hr = float(nxt[3])
            except: continue
            p3 = 1 if nxt_hr >= 3 else 0

            地型 = parse_地型(波型)
            等型 = parse_等型(za, 中符串)
            柱排 = parse_柱排(柱排周)
            柱型 = parse_柱型(柱型周)
            顶型 = parse_顶型(顶周, 合顶周)
            主类 = parse_波型主类(波型)

            if 地型: dim_stats['地型'][地型]['n'] += 1; dim_stats['地型'][地型]['p3'] += p3
            if 等型: dim_stats['等型'][等型]['n'] += 1; dim_stats['等型'][等型]['p3'] += p3
            if 柱排: dim_stats['柱排'][柱排]['n'] += 1; dim_stats['柱排'][柱排]['p3'] += p3
            if 柱型: dim_stats['柱型'][柱型]['n'] += 1; dim_stats['柱型'][柱型]['p3'] += p3
            if 顶型: dim_stats['顶型'][顶型]['n'] += 1; dim_stats['顶型'][顶型]['p3'] += p3
            if 主类: dim_stats['波型主类'][主类]['n'] += 1; dim_stats['波型主类'][主类]['p3'] += p3

# 输出各维度区分度
with open('____temp/_框架对比.txt', 'w', encoding='utf-8') as out:
    out.write('='*100 + '\n')
    out.write('新框架（周地型×周柱型×周柱排×周顶型）vs 原文框架 区分度对比\n')
    out.write('='*100 + '\n\n')

    for dim in ['地型', '等型', '柱排', '柱型', '顶型', '波型主类']:
        out.write(f'\n【{dim}】\n')
        items = [(k, v['n'], v['p3']/v['n']*100) for k, v in dim_stats[dim].items() if v['n'] >= 100]
        items.sort(key=lambda x: -x[2])
        if not items: continue
        best = items[0]
        worst = items[-1]
        区分度 = best[2] - worst[2]
        out.write(f'  区分度: {区分度:.1f}pp（{best[0]}={best[2]:.1f}% vs {worst[0]}={worst[2]:.1f}%）\n')
        for k, n, pct in items[:5]:
            out.write(f'    {k}: {pct:.1f}% (样本{n:,})\n')
        out.write(f'    ...\n')
        for k, n, pct in items[-3:]:
            out.write(f'    {k}: {pct:.1f}% (样本{n:,})\n')

print('done')