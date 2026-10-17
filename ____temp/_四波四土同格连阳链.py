# -*- coding: utf-8 -*-
"""
四波×四土 同格连阳链修正分析（2026-10-15 新数据 63列）
====================================================
修正口径：连阳链柱必须与链伙伴在同一个四波×四土格内。
  某柱 i（在格X）属于格X的连阳链，当且仅当：
    - tail[i] == 'Q'（升连）：前一柱 i-1 也在格X 且 tail[i-1] ∈ {O,o,Q}
      （链在格X内延续，启动柱和续柱都在格X）
    - tail[i] ∈ {O,o}（启动柱）：下一柱 i+1 也在格X 且 tail[i+1] == 'Q'
      （启动柱的续柱在格X）
  跨格链（启动柱在格A、续柱在格B）不算任何格的连阳链柱。

列索引（新63列）：主期[0] 周涨[1] PR[2] HR[3] 护型[4] ZB周[17] ZC周[18] AB周[22] 并符串周[51]
"""
import csv, glob, io, sys, os, collections, datetime
from collections import defaultdict
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = '昭明算展/谕组周'
OUT = '____temp/_四波四土同格连阳链_result.txt'

C_HX, C_ZB, C_ZC, C_AB, C_并符, C_主期 = 4, 17, 18, 22, 51, 0

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
                'zb': zb, 'zc': zc, 'ab': ab, '护级': 护级, 'tail': tail,
            })
    if fi % 1000 == 0 and fi > 0:
        print(f'  已加载 {fi}/{len(files)}', flush=True)

# 统计：{key: {n, Q, 同格链}}
stats = defaultdict(lambda: {'n': 0, 'Q': 0, '链': 0})
全局 = {'n': 0, 'Q': 0, '链': 0}

print('开始逐股判定同格连阳链...', flush=True)
for code, lst in by_code.items():
    lst.sort(key=lambda x: x['date'])
    # 预计算每柱的格
    cells = []
    for row in lst:
        sibo = 四波(row['ab'], row['zb'])
        tu = 四土(row['zc'], row['护级'])
        cells.append(f'{tu}×{sibo}')
    for i, row in enumerate(lst):
        key = cells[i]
        s = stats[key]
        s['n'] += 1
        全局['n'] += 1
        if row['tail'] == 'Q':
            s['Q'] += 1
            全局['Q'] += 1
        # 同格连阳链判定
        in_chain = False
        if row['tail'] == 'Q':
            # 升连：前一柱在同格且是链的一部分(O/o/Q)
            if i > 0 and cells[i-1] == key and lst[i-1]['tail'] in ('O', 'o', 'Q'):
                in_chain = True
        elif row['tail'] in ('O', 'o'):
            # 启动柱：下一柱在同格且是Q
            if i + 1 < len(lst) and cells[i+1] == key and lst[i+1]['tail'] == 'Q':
                in_chain = True
        if in_chain:
            s['链'] += 1
            全局['链'] += 1

lines = []
lines.append('=' * 80)
lines.append('四波×四土 同格连阳链分析（启动柱与续柱必须在同格）')
lines.append('=' * 80)
lines.append('')
lines.append('同格连阳链柱：Q(前一柱同格且为O/o/Q) 或 O/o(下一柱同格且为Q)')
lines.append('跨格链（启动柱在格A、续柱在格B）不算任何格的连阳链柱')
lines.append('')
lines.append(f'全量基线: n={全局["n"]:,}  升连Q={全局["Q"]:,}  同格连阳链柱={全局["链"]:,}')
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

lines.append('--- 同格连阳链柱 存在比例（该格链柱数/该格样本）---')
lines.append(f'{"":<10} {"升主(龙)":>12} {"降转(武)":>12} {"降主(虎)":>12} {"升转(雀)":>12}')
for tu in ['沃土', '鸡肋土', '执念土', '禁土']:
    row = f'{tu:<10}'
    for sibo in ['升主(龙)', '降转(武)', '降主(虎)', '升转(雀)']:
        s = stats[f'{tu}×{sibo}']
        row += f' {s["链"]/s["n"]*100 if s["n"] else 0:>11.2f}%'
    lines.append(row)
lines.append('')

lines.append('--- 同格连阳链 vs 升连(Q) 存在比例增幅（pp）---')
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