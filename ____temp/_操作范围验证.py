# -*- coding: utf-8 -*-
"""
操作范围框架验证（2026-10-15 新数据 63列）
====================================================
用户框架：
  WXZC>0：龙/雀/武 可操作，虎 不主动操作（镜面对称：WXZC>0虎 ↔ WXZC<0龙）
  WXZC<0：虎坚决不碰、雀不考虑、武诱多、只有龙可考虑
  三类介入点：①WJC入口(刚上破WXZC>0) ②WJC之上调整后连升 ③WXZC<0的龙(即将上破)

列索引：主期[0] 周涨[1] HR[3] 护型[4] ZB周[17] ZC周[18] AB周[22]
"""
import csv, glob, io, sys, os, collections
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_操作范围验证_result.txt'

C_HR, C_周涨, C_HX, C_ZB, C_ZC, C_AB = 3, 1, 4, 17, 18, 22

def 四波(ab, zb):
    if ab > 0 and zb > 0: return '龙(升主)'
    if ab < 0 and zb > 0: return '武(降转)'
    if ab < 0 and zb < 0: return '虎(降主)'
    if ab > 0 and zb < 0: return '雀(升转)'
    return '?'

# 统计：{key: {n, ge3, sum_hr, sum_涨, gt0}}
stats = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'sum_涨': 0.0, 'gt0': 0})

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
                涨 = float(row[C_周涨].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                zc = int(row[C_ZC].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except (ValueError, IndexError):
                continue
            sibo = 四波(ab, zb)
            # 按 WXZC 正负 + 四波 分组
            if zc > 0:
                key = f'ZC>0×{sibo}'
            elif zc < 0:
                key = f'ZC<0×{sibo}'
            else:
                key = f'ZC=0×{sibo}'
            s = stats[key]
            s['n'] += 1
            s['sum_hr'] += hr
            s['sum_涨'] += 涨
            if hr >= 3.0: s['ge3'] += 1
            if 涨 > 0: s['gt0'] += 1
    if fi % 1000 == 0 and fi > 0:
        print(f'  已处理 {fi}/{len(files)}', flush=True)

lines = []
lines.append('=' * 80)
lines.append('操作范围框架验证（2026-10-15 新数据 3449文件）')
lines.append('=' * 80)
lines.append('')

def fmt(key):
    s = stats[key]
    n = s['n']
    if n == 0: return f'{key:<16} n=0'
    return (f'{key:<16} n={n:>9,}  P(≥3%)={s["ge3"]/n*100:6.2f}%  '
            f'均涨幅={s["sum_涨"]/n:7.3f}%  上涨率={s["gt0"]/n*100:6.2f}%  均高幅={s["sum_hr"]/n:6.3f}%')

# ============ 1. WXZC>0 四波操作价值 ============
lines.append('=' * 80)
lines.append('1. WXZC>0（沃土侧）四波操作价值')
lines.append('=' * 80)
lines.append('')
for sibo in ['龙(升主)', '武(降转)', '雀(升转)', '虎(降主)']:
    lines.append(fmt(f'ZC>0×{sibo}'))
lines.append('')

# ============ 2. WXZC<0 四波操作价值 ============
lines.append('=' * 80)
lines.append('2. WXZC<0（禁土侧）四波操作价值')
lines.append('=' * 80)
lines.append('')
for sibo in ['龙(升主)', '武(降转)', '雀(升转)', '虎(降主)']:
    lines.append(fmt(f'ZC<0×{sibo}'))
lines.append('')

# ============ 3. 镜面对称验证 ============
lines.append('=' * 80)
lines.append('3. 镜面对称验证：WXZC>0的虎 ↔ WXZC<0的龙')
lines.append('=' * 80)
lines.append('')
lines.append(fmt('ZC>0×虎(降主)'))
lines.append(fmt('ZC<0×龙(升主)'))
lines.append('')

# ============ 4. 三类介入点 ============
lines.append('=' * 80)
lines.append('4. 三类介入点')
lines.append('=' * 80)
lines.append('')
lines.append('介入点①：WJC入口（刚上破 WXZC>0，WXZC 0-2）')
lines.append('介入点③：WXZC<0 的龙（即将上破 WJC）')
lines.append('')

# 介入点①：WXZC>0 且 0-2（刚上破）
# 介入点③：WXZC<0 且 接近0（-2~-1，即将上破）
介入1 = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'sum_涨': 0.0, 'gt0': 0})
介入3 = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'sum_涨': 0.0, 'gt0': 0})
for fp in files:
    with open(fp, encoding='gbk', errors='replace') as f:
        r = csv.reader(f)
        try: next(r)
        except StopIteration: continue
        for row in r:
            if len(row) <= C_AB: continue
            try:
                hr = float(row[C_HR].strip() or 0)
                涨 = float(row[C_周涨].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                zc = int(row[C_ZC].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except: continue
            sibo = 四波(ab, zb)
            # 介入点①：WXZC>0 且 0-2（刚上破 WJC）
            if 0 < zc <= 2:
                s = 介入1[sibo]
                s['n'] += 1; s['sum_涨'] += 涨; s['sum_hr'] += hr
                if hr >= 3.0: s['ge3'] += 1
                if 涨 > 0: s['gt0'] += 1
            # 介入点③：WXZC<0 且 接近0（-2~-1，即将上破）
            if -2 <= zc < 0:
                s = 介入3[sibo]
                s['n'] += 1; s['sum_涨'] += 涨; s['sum_hr'] += hr
                if hr >= 3.0: s['ge3'] += 1
                if 涨 > 0: s['gt0'] += 1

lines.append('--- 介入点①：WJC入口（WXZC 0-2，刚上破）---')
for sibo in ['龙(升主)', '武(降转)', '雀(升转)', '虎(降主)']:
    s = 介入1[sibo]
    n = s['n']
    if n == 0:
        lines.append(f'  {sibo:<12} n=0')
    else:
        lines.append(f'  {sibo:<12} n={n:>9,}  P(≥3%)={s["ge3"]/n*100:6.2f}%  均涨幅={s["sum_涨"]/n:7.3f}%  上涨率={s["gt0"]/n*100:6.2f}%')
lines.append('')

lines.append('--- 介入点③：WXZC<0 的龙（WXZC -2~-1，即将上破）---')
for sibo in ['龙(升主)', '武(降转)', '雀(升转)', '虎(降主)']:
    s = 介入3[sibo]
    n = s['n']
    if n == 0:
        lines.append(f'  {sibo:<12} n=0')
    else:
        lines.append(f'  {sibo:<12} n={n:>9,}  P(≥3%)={s["ge3"]/n*100:6.2f}%  均涨幅={s["sum_涨"]/n:7.3f}%  上涨率={s["gt0"]/n*100:6.2f}%')
lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('\n完成，结果写入', OUT)