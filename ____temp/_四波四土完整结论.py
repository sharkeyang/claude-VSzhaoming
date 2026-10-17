# -*- coding: utf-8 -*-
"""
四波×四土 完整结论报告（2026-10-15 新数据 63列）
====================================================
只考虑显性升连(Q)和跌连(W)，不考虑启动柱。
1. 四土×四波交叉表：P(≥3%) + 期望均高幅 + 期望均涨幅
2. 升连(Q) 存在比例 + 分布比例 + 升连样本获利
3. 跌连(W) 存在比例 + 分布比例 + 跌连样本获利

列索引（新63列）：主期[0] 周涨[1] PR[2] HR[3] 护型[4] ZB周[17] ZC周[18] AB周[22] 并符串周[51]
并符串尾字符：Q=升连 W=跌连
"""
import csv, glob, io, sys, os, collections
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_四波四土完整结论_result.txt'

C_HR, C_HX, C_ZB, C_ZC, C_AB, C_并符, C_周涨 = 3, 4, 17, 18, 22, 51, 1

def 四波(ab, zb):
    if ab > 0 and zb > 0: return '升主(龙)'
    if ab < 0 and zb > 0: return '降转(武)'
    if ab < 0 and zb < 0: return '降主(虎)'
    if ab > 0 and zb < 0: return '升转(雀)'
    return '?'

def 四土(zc, 护级):
    if 护级 == '忠': return '鸡肋土'
    if 护级 == '中': return '执念土'
    if 护级 in ('上', '忐'):
        return '沃土' if zc > 0 else '鸡肋土'
    if 护级 in ('下', '忑'):
        return '禁土' if zc < 0 else '执念土'
    return '?'

# stats[key] = {n, ge3, sum_hr, sum_涨, Q, Q_ge3, W, W_ge3}
stats = defaultdict(lambda: {'n': 0, 'ge3': 0, 'sum_hr': 0.0, 'sum_涨': 0.0,
                             'Q': 0, 'Q_ge3': 0, 'W': 0, 'W_ge3': 0})
全局 = {'n': 0, 'Q': 0, 'W': 0}

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
                涨 = float(row[C_周涨].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                zc = int(row[C_ZC].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except (ValueError, IndexError):
                continue
            hx = row[C_HX].strip()
            护级 = hx[3] if len(hx) >= 4 else '?'
            sibo = 四波(ab, zb)
            tu = 四土(zc, 护级)
            key = f'{tu}×{sibo}'
            s = stats[key]
            s['n'] += 1
            s['sum_hr'] += hr
            s['sum_涨'] += 涨
            if hr >= 3.0: s['ge3'] += 1
            tail = row[C_并符].strip()[-1] if row[C_并符].strip() else ''
            if tail == 'Q':
                s['Q'] += 1
                全局['Q'] += 1
                if hr >= 3.0: s['Q_ge3'] += 1
            elif tail == 'W':
                s['W'] += 1
                全局['W'] += 1
                if hr >= 3.0: s['W_ge3'] += 1
            全局['n'] += 1
    if fi % 1000 == 0 and fi > 0:
        print(f'  已处理 {fi}/{len(files)}', flush=True)

lines = []
lines.append('=' * 80)
lines.append('四波×四土 完整结论报告（2026-10-15 新数据 3449文件）')
lines.append('=' * 80)
lines.append('')
lines.append(f'全量基线: n={全局["n"]:,}  升连Q={全局["Q"]:,} ({全局["Q"]/全局["n"]*100:.2f}%)  跌连W={全局["W"]:,} ({全局["W"]/全局["n"]*100:.2f}%)')
lines.append('')

def cell(key):
    s = stats[key]
    if s['n'] == 0: return None
    return {'n': s['n'], 'p3': s['ge3']/s['n']*100, 'hr': s['sum_hr']/s['n'], '涨': s['sum_涨']/s['n']}

# ============ 1. 四土×四波交叉表 ============
lines.append('=' * 80)
lines.append('1. 四土×四波交叉表')
lines.append('=' * 80)
lines.append('')

lines.append('--- P(≥3%) ---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        c = cell(f'{tu}×{sibo}')
        row += f' {c["p3"] if c else 0:>11.2f}%'
    lines.append(row)
lines.append('')

lines.append('--- 期望均高幅（下周HR均值%）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        c = cell(f'{tu}×{sibo}')
        row += f' {c["hr"] if c else 0:>11.3f}%'
    lines.append(row)
lines.append('')

lines.append('--- 期望均涨幅（下周周涨均值%）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        c = cell(f'{tu}×{sibo}')
        row += f' {c["涨"] if c else 0:>11.3f}%'
    lines.append(row)
lines.append('')

lines.append('--- 样本数 n ---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        c = cell(f'{tu}×{sibo}')
        row += f' {c["n"] if c else 0:>12,}'
    lines.append(row)
lines.append('')

# ============ 2. 升连(Q) 分析 ============
lines.append('=' * 80)
lines.append('2. 升连(Q) 分析')
lines.append('=' * 80)
lines.append('')

lines.append('--- 升连(Q) 存在比例（该格Q数/该格样本）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["Q"]/s["n"]*100 if s["n"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

lines.append('--- 升连(Q) 分布比例（该格Q数/全局Q总数）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["Q"]/全局["Q"]*100 if 全局["Q"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

lines.append('--- 升连(Q) 样本的 P(≥3%)（该格Q样本中HR≥3%比例）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["Q_ge3"]/s["Q"]*100 if s["Q"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

# ============ 3. 跌连(W) 分析 ============
lines.append('=' * 80)
lines.append('3. 跌连(W) 分析')
lines.append('=' * 80)
lines.append('')

lines.append('--- 跌连(W) 存在比例（该格W数/该格样本）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["W"]/s["n"]*100 if s["n"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

lines.append('--- 跌连(W) 分布比例（该格W数/全局W总数）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["W"]/全局["W"]*100 if 全局["W"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

lines.append('--- 跌连(W) 样本的 P(≥3%)（该格W样本中HR≥3%比例）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["W_ge3"]/s["W"]*100 if s["W"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('\n完成，结果写入', OUT)