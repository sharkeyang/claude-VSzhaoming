# -*- coding: utf-8 -*-
"""§6.8 框架专项介入条件验证（跨行逻辑，look-ahead）
验证框架里提出的具体介入条件：
1. 等3 扩管>60 按柱排细分（确认计划数据）
2. 等3 管宽哼JA空 的信号（新发现）
3. 等2 正交初期回落DJA反弹（继续触顶形成垒升）
4. 等4 DTZA=-2第二柱阳柱（次日是否再站DJA）
5. 等1 第1柱诱多/出管惯性（第2柱行为）
6. 等3 平管十字星下柱冲高
列映射（VBA权威，勿信表头）：
col8=DXCD, col9=DXAB, col10=柱排, col13=日ZA, col14=日ZC, col19=BSHA,
col23=管宽哼JA(脸哼JA), col26=次日高幅, col30=上符串(触顶A), col44=BT连阳
"""
import io, sys, glob, os
from collections import defaultdict

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

DATA_DIR = '昭明算展/谕组日'
files = glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

def zhupai_class(zp):
    if zp.startswith('升.'):
        if '尾连' in zp: return '升连'
        elif '尾吞' in zp: return '升吞'
        elif '尾反孕' in zp: return '升孕'
        else: return '升排其他'
    elif zp.startswith('跌.'):
        if '尾连' in zp: return '跌连'
        elif '尾吞' in zp: return '跌吞'
        elif '尾反孕' in zp: return '跌孕'
        else: return '跌排其他'
    elif zp.startswith('('):
        return '人排'
    else:
        return '其他'

stats = defaultdict(lambda: {'n':0,'p3':0,'sum_nh':0})

def add(label, nh):
    st = stats[label]; st['n']+=1
    if nh>=3: st['p3']+=1
    st['sum_nh']+=nh

def report(label):
    st = stats[label]
    if st['n']==0: return
    print(f'{label}: n={st["n"]}, 次日P3%={st["p3"]/st["n"]*100:.2f}%, 均高幅={st["sum_nh"]/st["n"]:.2f}%', flush=True)

def parse_row(row):
    """解析一行，返回 dict 或 None"""
    if len(row) < 31: return None
    try:
        return {
            'ab': row[9], 'zp': row[10], 'za': int(row[13]), 'zc': int(row[14]),
            'gk': row[23].strip(), 'nh': float(row[26]), 'sf': row[30], 'col44': row[44],
        }
    except:
        return None

for fp in files:
    rows = []
    with io.open(fp, encoding='gbk', errors='replace') as f:
        f.readline()
        for line in f:
            r = parse_row(line.strip().split(','))
            if r is not None:
                rows.append(r)
    # 逐行处理，用下一行作为"次日"（look-ahead）
    for i, cur in enumerate(rows):
        nxt = rows[i+1] if i+1 < len(rows) else None
        hx = cur['ab'][0] if cur['ab'] else ''
        zpc = zhupai_class(cur['zp'])
        touch = 'A' in cur['sf']
        if cur['gk'] == '':
            gk_class = '空'
        else:
            gkv = float(cur['gk'])
            if gkv > 60: gk_class = '扩管>60'
            elif gkv >= 0: gk_class = '平管0-60'
            else: gk_class = '窄管<0'
        nh = cur['nh']

        # ===== 验证1：等3 扩管>60 按柱排细分 =====
        if cur['za'] >= 3 and hx in ('a','b','r'):
            add('等3_基线', nh)
            if gk_class == '扩管>60':
                add(f'等3_扩管_{zpc}', nh)
            elif gk_class == '平管0-60':
                add(f'等3_平管_{zpc}', nh)
            elif gk_class == '空':
                add('等3_管宽空', nh)

        # ===== 验证2：等2 正交初期回落DJA反弹 =====
        # 正交初期回落DJA：当日日ZA=2 且 前一日日ZA=1（刚上穿后回落）
        if cur['za'] == 2 and hx in ('a','b','r'):
            add('等2_基线', nh)
            if touch: add('等2_触顶', nh)
            else: add('等2_未触顶', nh)
            # 前一日日ZA=1（用上一行）
            if i > 0 and rows[i-1]['za'] == 1:
                add('等2_正交初期回落DJA', nh)
                if touch: add('等2_正交初期回落DJA_触顶', nh)

        # ===== 验证3：等4 等6 第二柱阳柱 =====
        # 当日日ZA=-2 且 当日为阳柱（升排），看次日是否再站DJA（次日日ZA>0）
        if cur['za'] == -2 and hx == 'b':
            add('等4_等6_基线', nh)
            if cur['zp'].startswith('升.'):
                add('等4_等6_第二柱阳柱', nh)
                if nxt is not None and nxt['za'] > 0:
                    add('等4_等6_第二柱阳柱_次日再站DJA', nh)

        # ===== 验证4：等1 第1柱诱多/出管惯性 =====
        # 第1柱 = 日ZA=1，看第2柱（下一行）行为
        if cur['za'] == 1 and hx in ('a','b','r'):
            add('等1_基线', nh)
            add(f'等1_{zpc}', nh)
            # 第2柱行为：下一行日ZA
            if nxt is not None:
                if nxt['za'] > 1:
                    add('等1_第2柱维持升管(ZA>1)', nh)
                elif nxt['za'] == 1:
                    add('等1_第2柱持平(ZA=1)', nh)
                elif nxt['za'] <= 0:
                    add('等1_第2柱回落(ZA<=0)', nh)

        # ===== 验证5：等3 平管十字星下柱冲高 =====
        if cur['za'] >= 3 and hx in ('a','b','r') and gk_class == '平管0-60':
            if '孕' in cur['zp'] or '十字' in cur['zp']:
                add('等3_平管_十字星', nh)

print('\n=== 验证1：等3 扩管>60 按柱排细分 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('等3_扩管') or label.startswith('等3_平管') or label=='等3_基线' or label=='等3_管宽空':
        report(label)

print('\n=== 验证2：等2 正交初期回落DJA反弹 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('等2'):
        report(label)

print('\n=== 验证3：等4 等6 第二柱阳柱 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('等4'):
        report(label)

print('\n=== 验证4：等1 第1柱 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('等1'):
        report(label)

print('\n=== 验证5：等3 平管十字星 ===', flush=True)
for label in sorted(stats.keys()):
    if label.startswith('等3_平管_十字星'):
        report(label)
