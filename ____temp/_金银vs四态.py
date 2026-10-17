# -*- coding: utf-8 -*-
"""
金银(WXCD势型) vs 四态(WXAB&WXZB) 对比（2026-10-15 新数据 63列）
====================================================
问题：金银分类基于 WXCD 势型（前缀），能否改为以四态（龙武虎雀=WXAB&WXZB）划分？差别大吗？

新63列：主期[0] 周涨[1] PR[2] HR[3] 护型[4] 地型[5] 等周[6] 波型[7] 柱排周[8] 大局[9]
        柱型周[10] 层界周[11] 周势型(WXCD护型)[12] ... ZA周[16] ZB周[17] ZC周[18] ... AB周[22]
"""
import csv, glob, io, sys, os, collections
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_金银vs四态_result.txt'

C_HR, C_势型, C_ZB, C_AB = 3, 12, 17, 22

# 统计：{key: {n, ge3, sum_hr}}
stats = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0})

files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
print(f'共 {len(files)} 个文件', flush=True)

for fi, fp in enumerate(files):
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        try: next(r)
        except StopIteration: continue
        for row in r:
            if len(row) <= C_AB: continue
            try:
                hr = float(row[C_HR].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except (ValueError, IndexError):
                continue
            势型 = row[C_势型].strip()
            # 金银分类（势型含金/银/唏/嘘/尿/屎）
            if '金' in 势型: jy = '金'
            elif '银' in 势型: jy = '银'
            elif '唏' in 势型: jy = '唏'
            elif '嘘' in 势型: jy = '嘘'
            elif '尿' in 势型: jy = '尿'
            elif '屎' in 势型: jy = '屎'
            else: jy = '?'
            # 四态
            if ab > 0 and zb > 0: sibo = '升主龙'
            elif ab < 0 and zb < 0: sibo = '降主虎'
            elif ab < 0 and zb > 0: sibo = '降转武'
            elif ab > 0 and zb < 0: sibo = '升转雀'
            else: sibo = '?'

            # 记录 金银×四态
            key = f'{jy}×{sibo}'
            s = stats[key]
            s['n'] += 1; s['sum_hr'] += hr
            if hr >= 3.0: s['ge3'] += 1
            # 记录 金银单独
            key = f'{jy}×整体'
            s = stats[key]
            s['n'] += 1; s['sum_hr'] += hr
            if hr >= 3.0: s['ge3'] += 1
            # 记录 四态单独
            key = f'整体×{sibo}'
            s = stats[key]
            s['n'] += 1; s['sum_hr'] += hr
            if hr >= 3.0: s['ge3'] += 1
    if fi % 1000 == 0 and fi > 0:
        print(f'  已处理 {fi}/{len(files)}', flush=True)

lines = []
lines.append('=' * 80)
lines.append('金银(WXCD势型) vs 四态(WXAB&WXZB) 对比（2026-10-15 新数据 3449文件）')
lines.append('=' * 80)
lines.append('')

def fmt(key):
    s = stats[key]
    n = s['n']
    if n == 0: return f'{key:<16} n=0'
    return f'{key:<16} n={n:>9,}  P(≥3%)={s["ge3"]/n*100:6.2f}%  均高幅={s["sum_hr"]/n:6.3f}%'

# ============ 1. 金银单独 ============
lines.append('=' * 80)
lines.append('1. 金银（WXCD势型）单独')
lines.append('=' * 80)
lines.append('')
for jy in ['金', '银', '唏', '嘘', '尿', '屎']:
    lines.append(fmt(f'{jy}×整体'))
lines.append('')

# ============ 2. 四态单独 ============
lines.append('=' * 80)
lines.append('2. 四态（WXAB&WXZB）单独')
lines.append('=' * 80)
lines.append('')
for sibo in ['升主龙', '降主虎', '降转武', '升转雀']:
    lines.append(fmt(f'整体×{sibo}'))
lines.append('')

# ============ 3. 金银内部按四态细分 ============
lines.append('=' * 80)
lines.append('3. 金银内部按四态细分（金银内部是否还有四态信息？）')
lines.append('=' * 80)
lines.append('')
for jy in ['金', '银', '唏', '嘘', '尿', '屎']:
    lines.append(f'--- {jy} 内部按四态细分 ---')
    for sibo in ['升主龙', '降主虎', '降转武', '升转雀']:
        lines.append(fmt(f'{jy}×{sibo}'))
    lines.append('')

# ============ 4. 四态内部按金银细分 ============
lines.append('=' * 80)
lines.append('4. 四态内部按金银细分（四态内部是否还有金银信息？）')
lines.append('=' * 80)
lines.append('')
for sibo in ['升主龙', '降主虎', '降转武', '升转雀']:
    lines.append(f'--- {sibo} 内部按金银细分 ---')
    for jy in ['金', '银', '唏', '嘘', '尿', '屎']:
        lines.append(fmt(f'{jy}×{sibo}'))
    lines.append('')

# ============ 5. 区分度对比 ============
lines.append('=' * 80)
lines.append('5. 区分度对比（金银 vs 四态）')
lines.append('=' * 80)
lines.append('')
def 区分度(keys):
    vals = []
    for k in keys:
        s = stats[k]
        if s['n']: vals.append(s['ge3']/s['n']*100)
    if not vals: return 0
    return max(vals) - min(vals)
lines.append(f'金银区分度（金/银/唏/嘘/尿/屎 的 P(≥3%) 极差）= {区分度([f"{j}×整体" for j in ["金","银","唏","嘘","尿","屎"]])} pp')
lines.append(f'四态区分度（龙/虎/武/雀 的 P(≥3%) 极差）= {区分度([f"整体×{s}" for s in ["升主龙","降主虎","降转武","升转雀"]])} pp')
lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('\n完成，结果写入', OUT)