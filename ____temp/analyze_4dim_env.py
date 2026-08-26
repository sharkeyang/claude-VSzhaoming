# -*- coding: utf-8 -*-
"""四维组合（地型×等型×柱排×顶型）对甲/乙(ZA>0)的环境分类与风险机会提示"""
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

def parse_顶型(顶周, 合顶周):
    try: 顶 = int(顶周)
    except: 顶 = 0
    try: 合顶 = int(合顶周)
    except: 合顶 = 0
    触顶 = '触顶' if 顶 > 0 else '未触'
    合顶 = '合顶' if 合顶 > 0 else '未合'
    return f'{触顶}.{合顶}'

def describe_env(地型, 等型, 柱排, 顶型, hr3, prpos, prmean):
    """根据四维组合 + 下周表现，给出环境语义"""
    # 等型决定位置
    if 等型 in ['等1', '等2']:
        位置 = '回归WJA'
    elif 等型 == '等3':
        位置 = '远离WJA'
    else:
        位置 = 等型
    # 柱排决定方向
    if 柱排 == '升':
        方向 = '升排'
    elif 柱排 == '跌':
        方向 = '跌排'
    else:
        方向 = '人排'
    # 顶型
    if 顶型 == '触顶.合顶':
        顶 = '触顶'
    elif 顶型 == '未触.合顶':
        顶 = '合顶'
    else:
        顶 = '未触'
    # 下周表现判断（HR≥3% 是核心）
    if hr3 >= 68:
        表现 = '🟢强机会'
    elif hr3 >= 63:
        表现 = '🟢机会'
    elif hr3 >= 58:
        表现 = '🟡中性'
    elif hr3 >= 53:
        表现 = '🟠风险'
    else:
        表现 = '🔴高风险'
    # 组合语义
    if 等型 in ['等1','等2'] and 柱排 == '升' and 顶型 == '触顶.合顶':
        语义 = f'{位置}后{方向}触顶'
    elif 等型 in ['等1','等2'] and 柱排 == '升':
        语义 = f'{位置}后{方向}'
    elif 等型 == '等3' and 柱排 == '升':
        语义 = f'{位置}{方向}'
    elif 柱排 == '跌':
        语义 = f'{位置}{方向}'
    else:
        语义 = f'{位置}{方向}{顶}'
    return f'{语义} {表现}'

# 统计：四维组合 → 下周表现
# 下周表现 = 下一行的 PR/HR
combo = defaultdict(lambda: {'n':0, '下周HR3':0, '下周PRpos':0, '下周PRsum':0, '维持':0, '甲':0, '乙':0})

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
            combo[key]['n'] += 1
            combo[key]['甲'] += (cur == '甲')
            combo[key]['乙'] += (cur == '乙(ZA>0)')
            # 下周表现（下一行）
            if i+1 < len(rows):
                nxt = rows[i+1]
                if len(nxt) >= 4:
                    try:
                        nxt_hr = float(nxt[3])
                        nxt_pr = float(nxt[2])
                        if nxt_hr >= 3: combo[key]['下周HR3'] += 1
                        if nxt_pr > 0: combo[key]['下周PRpos'] += 1
                        combo[key]['下周PRsum'] += nxt_pr
                    except: pass
                # 下周护型（维持判断）
                if len(nxt) >= 15:
                    nxt_za = nxt[14]
                    nxt_hx = hx_key(nxt[4], nxt_za)
                    if nxt_hx == cur: combo[key]['维持'] += 1

# 输出
with open('____temp/_4dim_env.txt', 'w', encoding='utf-8') as out:
    out.write('='*120 + '\n')
    out.write('四维组合（地型×等型×柱排×顶型）对甲/乙(ZA>0)的环境分类与风险机会\n')
    out.write('='*120 + '\n\n')
    out.write('| 地型 | 等型 | 柱排 | 顶型 | 样本 | 甲% | 乙% | 下周HR≥3% | 下周PR>0 | 下周均PR | 维持率 | 环境语义 |\n')
    out.write('|:----:|:----:|:----:|:----:|:----:|:---:|:---:|:---------:|:--------:|:--------:|:------:|:---------|\n')

    for key, s in sorted(combo.items(), key=lambda x: -x[1]['n']):
        if s['n'] < 100: continue
        地型, 等型, 柱排, 顶型 = key
        甲pct = s['甲']/s['n']*100
        乙pct = s['乙']/s['n']*100
        hr3 = s['下周HR3']/s['n']*100
        prpos = s['下周PRpos']/s['n']*100
        prmean = s['下周PRsum']/s['n']
        维持 = s['维持']/s['n']*100
        # 环境语义
        env = describe_env(地型, 等型, 柱排, 顶型, hr3, prpos, prmean)
        out.write(f'| {地型} | {等型} | {柱排} | {顶型} | {s["n"]:,} | {甲pct:.0f}% | {乙pct:.0f}% | {hr3:.1f}% | {prpos:.1f}% | {prmean:+.2f}% | {维持:.1f}% | {env} |\n')

print('done')