#!/usr/bin/env python3
"""验证日层联动等级体系 — 快速版（采样50个文件）"""
import os, sys, re, glob
from collections import defaultdict
import openpyxl

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

SZ_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0718'
files = sorted(glob.glob(os.path.join(SZ_DIR, '算展.*.xlsx')))
print(f'共 {len(files)} 个算展文件，采样 50 个')

def compute_EV(ZE, CD, ZC, ZD, BC, AB, ZA, ZB):
    if ZE > 0:
        if CD > 0:
            if ZC > 0:
                if BC > 0 and AB > 0:
                    return 'E0上' if ZA > 0 else ('E2上' if ZB > 0 else 'E1上')
                elif BC > 0: return 'E3上'
                else: return 'E4上'
            elif ZD > 0: return 'e5中'
            else: return 'e6下'
        elif ZC <= 0: return 'e7忑'
        elif ZD <= 0: return 'e8忠'
        elif ZD > 0: return 'E9忐'
        else: return '>转空'
    else:
        if CD > 0:
            return 'V7上' if ZC > 0 else ('V8中' if ZD > 0 else 'v9下')
        elif ZD > 0: return 'V6忐'
        elif ZC > 0: return 'V5忠'
        elif BC > 0: return 'v4忑'
        elif AB > 0: return 'v3忑'
        elif ZB > 0: return 'v2忑'
        elif ZA > 0: return 'v1忑'
        else: return 'v0忑'

# 统计
stats = {
    'ev': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
    'head': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
    'suffix': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
    'comb': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
}

total = 0
sampled = files[:50]

for fi, fpath in enumerate(sampled):
    if fi % 10 == 0 and fi > 0:
        print(f'  处理 {fi}/{len(sampled)}...')
    try:
        wb = openpyxl.load_workbook(fpath, data_only=True, read_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if len(rows) < 2:
            wb.close(); continue
        for r in range(1, len(rows) - 1):
            row = rows[r]; nxt = rows[r+1]
            if len(row) < 274 or len(nxt) < 9: continue
            try:
                ZE = float(row[272] or 0); CD = float(row[273] or 0)
                ZC = float(row[267] or 0); ZD = float(row[271] or 0)
                BC = float(row[284] or 0) if len(row) > 284 else 0
                AB = float(row[268] or 0); ZA = float(row[265] or 0)
                ZB = float(row[266] or 0)
                hr = float(nxt[8] or 0)
            except (ValueError, TypeError, IndexError):
                continue
            ev = compute_EV(ZE, CD, ZC, ZD, BC, AB, ZA, ZB)
            total += 1
            # Update all stats
            for key, d in [(ev, stats['ev'][ev]),
                          (ev, stats['comb'][ev])]:
                d['n'] += 1; d['sum'] += hr
                if hr >= 3: d['h3'] += 1
                if hr >= 5: d['h5'] += 1
        wb.close()
    except Exception as e:
        print(f'  ! 跳过 {os.path.basename(fpath)}: {e}')

print(f'\n总行数: {total:,}')
print(f'{"="*70}')

# 排序输出
等级顺序 = ['E0上','E1上','E2上','E3上','E4上','e5中','e6下','e7忑','e8忠','E9忐','>转空',
           'V7上','V8中','v9下','V6忐','V5忠','v4忑','v3忑','v2忑','v1忑','v0忑']

print(f'\n【E/V等级 vs 下日冲高概率】')
print(f'{"等级":<6s} {"n":>8s} {"P>=3%":>7s} {"P>=5%":>7s} {"均涨":>6s}  {"柱状图"}')
print('-'*65)
for ev in 等级顺序:
    d = stats['ev'][ev]
    if d['n'] < 30: continue
    r3 = d['h3']/d['n']*100
    r5 = d['h5']/d['n']*100
    avg = d['sum']/d['n']
    bar = '█' * int(r3)
    print(f'{ev:<6s} {d["n"]:>8,} {r3:>6.1f}% {r5:>6.1f}% {avg:>5.2f}%  {bar}')

# 合并分析
print(f'\n【合并分析】')
groups = [
    ('强 (E0~E4+V7)', ['E0上','E1上','E2上','E3上','E4上','V7上']),
    ('中 (e5~E9+V8~V5)', ['e5中','e6下','e7忑','e8忠','E9忐','V8中','v9下','V6忐','V5忠']),
    ('弱 (v4~v0+转空)', ['v4忑','v3忑','v2忑','v1忑','v0忑','>转空']),
]
for label, levels in groups:
    n = sum(stats['ev'][k]['n'] for k in levels)
    h3 = sum(stats['ev'][k]['h3'] for k in levels)
    h5 = sum(stats['ev'][k]['h5'] for k in levels)
    sm = sum(stats['ev'][k]['sum'] for k in levels)
    if n > 0:
        print(f'  {label:<20s} n={n:>8,}  P>=3%={h3/n*100:>5.1f}%  P>=5%={h5/n*100:>5.1f}%  均涨={sm/n:.2f}%')

# 按 E/DJE之上 vs V/DJE之下 分类
print(f'\n【DJE之上 vs DJE之下】')
for label, prefix in [('E系列(DJE之上)', 'E'), ('e系列(DJE之上衰退)', 'e'),
                       ('V系列(DJE之下修复)', 'V'), ('v系列(DJE之下最弱)', 'v')]:
    n = sum(stats['ev'][k]['n'] for k in stats['ev'] if k.startswith(prefix))
    h3 = sum(stats['ev'][k]['h3'] for k in stats['ev'] if k.startswith(prefix))
    h5 = sum(stats['ev'][k]['h5'] for k in stats['ev'] if k.startswith(prefix))
    sm = sum(stats['ev'][k]['sum'] for k in stats['ev'] if k.startswith(prefix))
    if n > 0:
        print(f'  {label:<20s} n={n:>8,}  P>=3%={h3/n*100:>5.1f}%  P>=5%={h5/n*100:>5.1f}%  均涨={sm/n:.2f}%')

print(f'\n{"="*70}')
print('验证完成')