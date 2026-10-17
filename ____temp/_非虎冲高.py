# -*- coding: utf-8 -*-
"""
WXZC>0 非虎下柱冲高分析（2026-10-15 新数据 63列）
====================================================
问题：WXZC>0 时，是否所有非虎（龙/武/雀）都有下柱冲高？哪些情况没有？
下柱冲高 = 下周 HR≥3%

列索引：主期[0] 周涨[1] HR[3] 护型[4] 地型[5] 等周[6] 波型[7] 柱排周[8] 大局[9]
        ZB周[17] ZC周[18] AB周[22] 并符串周[51]
"""
import csv, glob, io, sys, os, collections
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_非虎冲高_result.txt'

C_HR, C_HX, C_地型, C_等, C_波型, C_柱排, C_大局 = 3, 4, 5, 6, 7, 8, 9
C_ZB, C_ZC, C_AB, C_并符 = 17, 18, 22, 51

def 四波(ab, zb):
    if ab > 0 and zb > 0: return '龙'
    if ab < 0 and zb > 0: return '武'
    if ab < 0 and zb < 0: return '虎'
    if ab > 0 and zb < 0: return '雀'
    return '?'

# 统计：{key: {n, ge3}}
stats = defaultdict(lambda: {'n': 0, 'ge3': 0})

files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

for fi, fp in enumerate(files):
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        try: next(r)
        except StopIteration: continue
        for row in r:
            if len(row) <= C_并符: continue
            try:
                hr = float(row[C_HR].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                zc = int(row[C_ZC].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except (ValueError, IndexError):
                continue
            if zc <= 0: continue  # 只分析 WXZC>0
            hx = row[C_HX].strip()
            护级 = hx[3] if len(hx) >= 4 else '?'
            sibo = 四波(ab, zb)
            if sibo == '虎': continue  # 只分析非虎
            tail = row[C_并符].strip()[-1] if row[C_并符].strip() else ''
            地型 = row[C_地型].strip()
            等 = row[C_等].strip()
            柱排 = row[C_柱排].strip()
            波型 = row[C_波型].strip()

            # 整体
            s = stats[f'{sibo}×整体']
            s['n'] += 1
            if hr >= 3.0: s['ge3'] += 1
            # 按护级
            s = stats[f'{sibo}×护级{护级}']
            s['n'] += 1
            if hr >= 3.0: s['ge3'] += 1
            # 按柱排
            s = stats[f'{sibo}×柱排{tail}']
            s['n'] += 1
            if hr >= 3.0: s['ge3'] += 1
            # 按等
            s = stats[f'{sibo}×等{等}']
            s['n'] += 1
            if hr >= 3.0: s['ge3'] += 1
    if fi % 1000 == 0 and fi > 0:
        print(f'  已处理 {fi}/{len(files)}', flush=True)

lines = []
lines.append('=' * 80)
lines.append('WXZC>0 非虎（龙/武/雀）下柱冲高分析（2026-10-15 新数据）')
lines.append('=' * 80)
lines.append('')
lines.append('下柱冲高 = 下周 HR≥3%')
lines.append('')

def fmt(key):
    s = stats[key]
    n = s['n']
    if n == 0: return f'{key:<20} n=0'
    return f'{key:<20} n={n:>8,}  下柱冲高率={s["ge3"]/n*100:6.2f}%'

# ============ 1. 整体 ============
lines.append('=' * 80)
lines.append('1. WXZC>0 非虎整体下柱冲高率')
lines.append('=' * 80)
lines.append('')
for sibo in ['龙', '武', '雀']:
    lines.append(fmt(f'{sibo}×整体'))
lines.append('')

# ============ 2. 按护级细分 ============
lines.append('=' * 80)
lines.append('2. 按护级细分（上/中/下/忐/忠/忑）')
lines.append('=' * 80)
lines.append('')
for sibo in ['龙', '武', '雀']:
    lines.append(f'--- {sibo} ---')
    for 护级 in ['上', '中', '下', '忐', '忠', '忑']:
        lines.append(fmt(f'{sibo}×护级{护级}'))
    lines.append('')

# ============ 3. 按柱排细分 ============
lines.append('=' * 80)
lines.append('3. 按柱排细分（Q升连/W跌连/O升吞/o升孕/V跌吞/v跌孕）')
lines.append('=' * 80)
lines.append('')
for sibo in ['龙', '武', '雀']:
    lines.append(f'--- {sibo} ---')
    for tail in ['Q', 'W', 'O', 'o', 'V', 'v']:
        lines.append(fmt(f'{sibo}×柱排{tail}'))
    lines.append('')

# ============ 4. 按等细分 ============
lines.append('=' * 80)
lines.append('4. 按等细分（等1-6）')
lines.append('=' * 80)
lines.append('')
for sibo in ['龙', '武', '雀']:
    lines.append(f'--- {sibo} ---')
    for 等 in ['等1', '等2', '等3', '等4', '等5', '等6']:
        lines.append(fmt(f'{sibo}×等{等}'))
    lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('\n完成，结果写入', OUT)