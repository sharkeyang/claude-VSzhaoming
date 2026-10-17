# -*- coding: utf-8 -*-
"""
四波×四土 升连链修正分析（2026-10-15 新数据 63列）
====================================================
修正：升连链(含启动柱) 需逐股时序判定——
  连阳链 = 启动柱(O/o) + 连续升连(Q)，最小链长2
  某柱属于连阳链当且仅当：
    - 尾字符=Q（升连，链第2柱起），或
    - 尾字符∈{O,o}（启动柱）且 下一柱尾字符=Q
  孤立 O/o（下一柱非Q）不算连阳链。

列索引（新63列）：主期[0] 周涨[1] PR[2] HR[3] 护型[4] ZB周[17] ZC周[18] AB周[22] 并符串周[51]
"""
import csv, glob, io, sys, os, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_四波四土升连链修正_result.txt'

C_HR, C_HX, C_ZB, C_ZC, C_AB, C_并符, C_主期 = 3, 4, 17, 18, 22, 51, 0

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
            if len(row) <= C_并符: continue
            try:
                hr = float(row[C_HR].strip() or 0)
                zb = int(row[C_ZB].strip() or 0)
                zc = int(row[C_ZC].strip() or 0)
                ab = int(row[C_AB].strip() or 0)
            except (ValueError, IndexError):
                continue
            hx = row[C_HX].strip()
            护级 = hx[3] if len(hx) >= 4 else '?'
            tail = row[C_并符].strip()[-1] if row[C_并符].strip() else ''
            by_code[code].append({
                'date': parse_date(row[C_主期].strip()),
                'hr': hr, 'zb': zb, 'zc': zc, 'ab': ab,
                '护级': 护级, 'tail': tail,
            })
    if fi % 1000 == 0 and fi > 0:
        print(f'  已加载 {fi}/{len(files)}', flush=True)

# 统计：{key: {n, 链}}  key=四土×四波
stats = defaultdict(lambda: {'n': 0, '链': 0, 'Q': 0})
全局 = {'n': 0, '链': 0, 'Q': 0}

print('开始逐股判定连阳链...', flush=True)
for code, lst in by_code.items():
    lst.sort(key=lambda x: x['date'])
    for i, row in enumerate(lst):
        sibo = 四波(row['ab'], row['zb'])
        tu = 四土(row['zc'], row['护级'])
        key = f'{tu}×{sibo}'
        s = stats[key]
        s['n'] += 1
        全局['n'] += 1
        if row['tail'] == 'Q':
            s['Q'] += 1
            全局['Q'] += 1
        # 连阳链判定：Q 或 (O/o 且下一柱是Q)
        in_chain = False
        if row['tail'] == 'Q':
            in_chain = True
        elif row['tail'] in ('O', 'o'):
            if i + 1 < len(lst) and lst[i+1]['tail'] == 'Q':
                in_chain = True
        if in_chain:
            s['链'] += 1
            全局['链'] += 1

lines = []
lines.append('=' * 80)
lines.append('四波×四土 升连链修正分析（逐股时序判定，2026-10-15 新数据）')
lines.append('=' * 80)
lines.append('')
lines.append('连阳链 = 启动柱(O/o) + 连续升连(Q)，最小链长2')
lines.append('某柱属于连阳链：尾字符=Q，或 (尾字符∈{O,o} 且 下一柱尾字符=Q)')
lines.append('孤立 O/o（下一柱非Q）不算连阳链')
lines.append('')
lines.append(f'全量基线: n={全局["n"]:,}  升连Q={全局["Q"]:,}  连阳链柱(含启动柱)={全局["链"]:,}')
lines.append('')

# 升连(Q) 存在比例
lines.append('--- 升连(Q) 存在比例（该格Q数/该格样本）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["Q"]/s["n"]*100 if s["n"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

# 连阳链(含启动柱) 存在比例
lines.append('--- 连阳链柱(含启动柱O/o/Q) 存在比例（该格链柱数/该格样本）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["链"]/s["n"]*100 if s["n"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

# 增幅
lines.append('--- 连阳链 vs 升连(Q) 存在比例增幅（pp）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        if s['n']:
            diff = (s['链'] - s['Q'])/s['n']*100
        else:
            diff = 0
        row += f' {diff:>+11.2f}'
    lines.append(row)
lines.append('')

# 样本数
lines.append('--- 样本数 n ---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["n"]:>12,}'
    lines.append(row)
lines.append('')

with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))
print('\n完成，结果写入', OUT)