#!/usr/bin/env python3
"""验证日层联动各维度分类效果 — 谕组CSV全量数据"""
import os, sys, glob, csv, re
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

CSV_DIR = r'D:\@VSwork\VS昭明计划VBA优化\____temp\谕组'
files = sorted(glob.glob(os.path.join(CSV_DIR, '谕组_*.csv')))
print(f'共 {len(files)} 个谕组CSV文件')

# 统计：按各种维度
stats = {
    '首字': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
    'WXAB_首': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
    '波型_首': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
    '盈提示': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
    '首字_WXAB': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
    '柱排_首': defaultdict(lambda: {'n':0, 'h3':0, 'h5':0, 'sum':0.0}),
}

total = 0
for fi, fpath in enumerate(files):
    if fi % 1000 == 0 and fi > 0:
        print(f'  处理 {fi}/{len(files)}...')
    try:
        with open(fpath, 'r', encoding='gbk', errors='ignore') as fh:
            reader = csv.DictReader(fh)
            prev = None
            for row in reader:
                hr = row.get('HR', '')
                wxab = row.get('WXAB', '')
                bx = row.get('波型', '')
                yt = row.get('盈提示', '')
                zpx = row.get('柱排周', '')
                wxcd = row.get('WXCD', '')
                if not hr: continue
                try:
                    hr_val = float(hr)
                except:
                    continue
                total += 1
                # 首字：从WXCD提取
                head = wxcd[0] if wxcd else ''
                if head in ('金','银','唏','嘘','尿','屎','铜'):
                    stats['首字'][head]['n'] += 1
                    if hr_val >= 3: stats['首字'][head]['h3'] += 1
                    if hr_val >= 5: stats['首字'][head]['h5'] += 1
                    stats['首字'][head]['sum'] += hr_val
                # WXAB首字
                wxab_h = wxab[0] if wxab else ''
                if wxab_h in ('甲','乙','丙','丁','戊','己'):
                    stats['WXAB_首'][wxab_h]['n'] += 1
                    if hr_val >= 3: stats['WXAB_首'][wxab_h]['h3'] += 1
                    if hr_val >= 5: stats['WXAB_首'][wxab_h]['h5'] += 1
                    stats['WXAB_首'][wxab_h]['sum'] += hr_val
                # 波型首字
                bx_h = bx[0] if bx else ''
                stats['波型_首'][bx_h]['n'] += 1
                if hr_val >= 3: stats['波型_首'][bx_h]['h3'] += 1
                if hr_val >= 5: stats['波型_首'][bx_h]['h5'] += 1
                stats['波型_首'][bx_h]['sum'] += hr_val
                # 盈提示
                yt_v = yt if yt else '(无)'
                stats['盈提示'][yt_v]['n'] += 1
                if hr_val >= 3: stats['盈提示'][yt_v]['h3'] += 1
                if hr_val >= 5: stats['盈提示'][yt_v]['h5'] += 1
                stats['盈提示'][yt_v]['sum'] += hr_val
                # 首字+WXAB组合
                if head and wxab_h:
                    key = f'{head}_{wxab_h}'
                    stats['首字_WXAB'][key]['n'] += 1
                    if hr_val >= 3: stats['首字_WXAB'][key]['h3'] += 1
                    if hr_val >= 5: stats['首字_WXAB'][key]['h5'] += 1
                    stats['首字_WXAB'][key]['sum'] += hr_val
                # 柱排首字
                if zpx:
                    zp_h = zpx[0]
                    stats['柱排_首'][zp_h]['n'] += 1
                    if hr_val >= 3: stats['柱排_首'][zp_h]['h3'] += 1
                    if hr_val >= 5: stats['柱排_首'][zp_h]['h5'] += 1
                    stats['柱排_首'][zp_h]['sum'] += hr_val
    except Exception as e:
        print(f'  错误 {fpath}: {e}')
        continue

print(f'\n总行数: {total:,}')
print(f'{"="*70}')

# 输出各维度
def print_dim(name, data, sort_key=None, min_n=100):
    print(f'\n【{name}】')
    print(f'{"分类":<10s} {"n":>10s} {"P>=3%":>7s} {"P>=5%":>7s} {"均涨":>6s}  {"柱状图"}')
    print('-'*65)
    items = sorted(data.items(), key=lambda x: sort_key(x) if sort_key else x[1]['n'], reverse=True)
    for k, d in items:
        if d['n'] < min_n: continue
        r3 = d['h3']/d['n']*100
        r5 = d['h5']/d['n']*100
        avg = d['sum']/d['n']
        bar = '█' * int(r3)
        print(f'{k:<10s} {d["n"]:>10,} {r3:>6.1f}% {r5:>6.1f}% {avg:>5.2f}%  {bar}')

print_dim('首字(金银唏嘘尿屎)—WXCD前缀', stats['首字'])
print_dim('WXAB护型首字', stats['WXAB_首'])
print_dim('波型首字', stats['波型_首'])
print_dim('盈提示', stats['盈提示'])
print_dim('柱排周首字', stats['柱排_首'])
print_dim('首字+WXAB组合(Top30)', stats['首字_WXAB'], sort_key=lambda x: x[1]['h3']/x[1]['n'], min_n=200)

print(f'\n{"="*70}')
print('验证完成')