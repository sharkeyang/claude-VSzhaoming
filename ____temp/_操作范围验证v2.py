# -*- coding: utf-8 -*-
"""
操作范围框架验证 v2：状态流转 + 长期收益（2026-10-15 新数据 63列）
====================================================
用户方法论：不能只看单柱期望收益，应看状态流转（转移矩阵）和长期收益。
验证：
  1. WXZC>0 的雀 → 下周四波转移（是否大多转回龙）
  2. WXZC>0 的虎 → 下周四波转移（是否大多下破 WJC）
  3. WXZC<0 的武 → 下周四波转移（是否大多转龙）
  4. WXZC<0 的龙 → 下周四波转移（是否大多转坏）
  5. 长期持有收益（介入后持有 N 周）

列索引：主期[0] 周涨[1] HR[3] 护型[4] ZB周[17] ZC周[18] AB周[22]
"""
import csv, glob, io, sys, os, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_操作范围验证v2_result.txt'

C_周涨, C_HX, C_ZB, C_ZC, C_AB, C_主期 = 1, 4, 17, 18, 22, 0

def 四波(ab, zb):
    if ab > 0 and zb > 0: return '龙'
    if ab < 0 and zb > 0: return '武'
    if ab < 0 and zb < 0: return '虎'
    if ab > 0 and zb < 0: return '雀'
    return '?'

def 状态(zc, ab, zb):
    """返回 状态 = WXZC正负 × 四波"""
    sibo = 四波(ab, zb)
    if zc > 0: return f'ZC>0×{sibo}'
    if zc < 0: return f'ZC<0×{sibo}'
    return f'ZC=0×{sibo}'

def parse_date(s):
    try: return datetime.datetime.strptime(s, '%Y/%m/%d')
    except: return datetime.datetime.max

# 逐股加载
by_code = defaultdict(list)
files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

for fi, fp in enumerate(files):
    code = fp.split('_')[-1].replace('.csv', '')
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        try: next(r)
        except StopIteration: continue
        for row in r:
            if len(row) <= C_AB: continue
            try:
                涨 = float(row[C_周涨].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                zc = int(row[C_ZC].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except (ValueError, IndexError):
                continue
            by_code[code].append({
                'date': parse_date(row[C_主期].strip()),
                '涨': 涨, 'zb': zb, 'zc': zc, 'ab': ab,
            })
    if fi % 1000 == 0 and fi > 0:
        print(f'  已加载 {fi}/{len(files)}', flush=True)

lines = []
lines.append('=' * 80)
lines.append('操作范围框架验证 v2：状态流转 + 长期收益（2026-10-15 新数据）')
lines.append('=' * 80)
lines.append('')

# ============ 1. 状态转移矩阵 ============
lines.append('=' * 80)
lines.append('1. 状态流转（本周状态 → 下周四波）')
lines.append('=' * 80)
lines.append('')

# 关注的状态：ZC>0×雀, ZC>0×虎, ZC<0×武, ZC<0×龙
关注状态 = ['ZC>0×雀', 'ZC>0×虎', 'ZC<0×武', 'ZC<0×龙']
转移 = {st: defaultdict(int) for st in 关注状态}
转移_周涨 = {st: defaultdict(float) for st in 关注状态}

for code, lst in by_code.items():
    lst.sort(key=lambda x: x['date'])
    for i in range(len(lst) - 1):
        cur = lst[i]
        nxt = lst[i+1]
        cur_st = 状态(cur['zc'], cur['ab'], cur['zb'])
        if cur_st in 关注状态:
            nxt_sibo = 四波(nxt['ab'], nxt['zb'])
            nxt_zc = 'ZC>0' if nxt['zc'] > 0 else ('ZC<0' if nxt['zc'] < 0 else 'ZC=0')
            nxt_st = f'{nxt_zc}×{nxt_sibo}'
            转移[cur_st][nxt_st] += 1
            转移_周涨[cur_st][nxt_st] += nxt['涨']

for st in 关注状态:
    tot = sum(转移[st].values())
    lines.append(f'--- {st} → 下周四波（n={tot:,}）---')
    if tot == 0:
        lines.append('  n=0')
        continue
    # 按占比排序
    items = sorted(转移[st].items(), key=lambda x: -x[1])
    for nxt_st, cnt in items[:8]:
        avg = 转移_周涨[st][nxt_st] / cnt if cnt else 0
        lines.append(f'  {nxt_st:<16} {cnt:>9,} ({cnt/tot*100:5.1f}%)  下周均涨={avg:+.3f}%')
    lines.append('')

# ============ 2. 长期持有收益 ============
lines.append('=' * 80)
lines.append('2. 长期持有收益（介入后持有 N 周累计涨幅）')
lines.append('=' * 80)
lines.append('')

# 对关注状态，计算介入后持有1/2/4/8周的累计涨幅
持有 = {st: defaultdict(list) for st in 关注状态}
for code, lst in by_code.items():
    lst.sort(key=lambda x: x['date'])
    for i in range(len(lst)):
        cur = lst[i]
        cur_st = 状态(cur['zc'], cur['ab'], cur['zb'])
        if cur_st in 关注状态:
            # 计算持有1/2/4/8周累计涨幅
            for weeks in [1, 2, 4, 8]:
                if i + weeks < len(lst):
                    cum = sum(lst[i+1+j]['涨'] for j in range(weeks))
                    持有[cur_st][weeks].append(cum)

for st in 关注状态:
    lines.append(f'--- {st} 长期持有累计涨幅 ---')
    for weeks in [1, 2, 4, 8]:
        arr = 持有[st][weeks]
        if not arr:
            lines.append(f'  持有{weeks}周: n=0')
            continue
        avg = sum(arr)/len(arr)
        pos = sum(1 for x in arr if x > 0)/len(arr)*100
        lines.append(f'  持有{weeks}周: n={len(arr):>8,}  累计均涨={avg:+.3f}%  正收益率={pos:.1f}%')
    lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('\n完成，结果写入', OUT)