#!/usr/bin/env python3
"""验证 DXCD护段 vs 下日冲高概率 — 从算展xlsx验证日级别护段效果"""
import os, sys, glob, re
from collections import defaultdict
import openpyxl
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

SZ_DIR = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0718'
files = sorted(glob.glob(os.path.join(SZ_DIR, '算展.*.xlsx')))
print(f'共 {len(files)} 个算展文件，采样 50 个')

stats = {
    '首字': defaultdict(lambda: {'n':0,'h3':0,'sum':0.0}),
    'DXCD护段': defaultdict(lambda: {'n':0,'h3':0,'sum':0.0}),
    '首字_DXCD护段': defaultdict(lambda: {'n':0,'h3':0,'sum':0.0}),
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
            if len(row) < 88 or len(nxt) < 9: continue
            try:
                hr = float(nxt[8] or 0)
            except: continue
            total += 1

            # 日周联动 (col 86)
            lz = str(row[86] or '')
            首字 = lz[0] if lz else ''

            # 护型DXAB (col 87) — 格式如 "a甲↗上1.I"
            # 第1字=护段(a/b/c/r/y/z), 第2字=护型(甲/乙/丙/丁/戊/己)
            hx = str(row[87] or '')
            if len(hx) >= 2:
                dxcd_护段 = hx[0]  # a/b/c/r/y/z
                dxcd_护型 = hx[1]  # 甲/乙/丙/丁/戊/己
            else:
                dxcd_护段 = ''
                dxcd_护型 = ''

            # 统计各维度
            if 首字 in ('金','银','唏','嘘','尿','屎'):
                stats['首字'][首字]['n'] += 1
                if hr >= 3: stats['首字'][首字]['h3'] += 1
                stats['首字'][首字]['sum'] += hr

            if dxcd_护段 in ('a','b','c','r','y','z'):
                stats['DXCD护段'][dxcd_护段]['n'] += 1
                if hr >= 3: stats['DXCD护段'][dxcd_护段]['h3'] += 1
                stats['DXCD护段'][dxcd_护段]['sum'] += hr

            if 首字 and dxcd_护段:
                key = f'{首字}_{dxcd_护段}'
                stats['首字_DXCD护段'][key]['n'] += 1
                if hr >= 3: stats['首字_DXCD护段'][key]['h3'] += 1
                stats['首字_DXCD护段'][key]['sum'] += hr

        wb.close()
    except Exception as e:
        print(f'  ! 跳过 {os.path.basename(fpath)}: {e}')

print(f'\n总行数: {total:,}')
print(f'{"="*70}')

def print_dim(name, data, sort_key=None, min_n=50):
    print(f'\n【{name}】')
    print(f'{"分类":<10s} {"n":>8s} {"P>=3%":>7s} {"均涨":>6s}  {"柱状图"}')
    print('-'*55)
    items = sorted(data.items(), key=lambda x: sort_key(x) if sort_key else x[1]['h3']/x[1]['n'], reverse=True)
    for k, d in items:
        if d['n'] < min_n: continue
        r3 = d['h3']/d['n']*100
        avg = d['sum']/d['n']
        bar = '█' * int(r3)
        print(f'{k:<10s} {d["n"]:>8,} {r3:>6.1f}% {avg:>5.2f}%  {bar}')

print_dim('首字(金银唏嘘尿屎)', stats['首字'])
print_dim('DXCD护段(a/b/c/r/y/z)', stats['DXCD护段'])
print_dim('首字+DXCD护段组合', stats['首字_DXCD护段'], min_n=30)

print(f'\n{"="*70}')
print('验证完成')