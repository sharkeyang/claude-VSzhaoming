# -*- coding: utf-8 -*-
import re, sys

with open('IQQQ跨码_D据擎4跨码管理.备份08032200.bas', 'rb') as f:
    bak = f.read().decode('gbk').replace('\r\n', '\n')
with open('昭明计划VS优化_vba/IQQQ跨码_D据擎4跨码管理.bas', 'rb') as f:
    cur = f.read().decode('utf-8').replace('\r\n', '\n')

def normalize(t):
    t = re.sub(r'    Dim 概览始 As Integer: 概览始 = 末行 \+ 1\n', '', t)
    t = re.sub(r'    Dim 大盘始 As Integer: 大盘始 = 末行 \+ 1\n', '', t)
    t = re.sub(r'    Dim 仓位始 As Integer: 仓位始 = 末行 \+ 1\n', '', t)
    t = re.sub(r'    Dim 行业始 As Integer: 行业始 = 末行 \+ 2\n', '', t)
    t = re.sub(r'    末行 = 行业始\n', '', t)
    t = re.sub(r'    末行 = \d+\n', '', t)
    t = re.sub(r'    末行 = 末行 \+ 1\n', '', t)
    t = re.sub(r'    大盘行 = \d+\n', '', t)
    t = re.sub(r'    大盘行 = 大盘始 \+ 1\n', '', t)
    t = re.sub(r'    大盘行 = 大盘行 \+ 1\n', '', t)
    t = re.sub(r'    Dim 大盘行 As Integer\n', '', t)
    t = t.replace('WSTO.Cells(大盘始,', 'WSTO.Cells(17,')
    t = t.replace('WSTO.Rows(大盘始)', 'WSTO.Rows(17)')
    t = t.replace('WSTO.Rows(行业始)', 'WSTO.Rows(31)')
    t = t.replace('WSTO.Cells(末行,', 'WSTO.Cells(大盘行,')
    t = t.replace('WSTO.Rows(末行)', 'WSTO.Rows(大盘行)')
    t = t.replace('For X = 概览始 + 1 To 末行 - 1', 'For X = 6 To 13')
    t = t.replace('For X = 概览始 To 末行', 'For X = 5 To 17')
    t = t.replace('For X = 仓位始 To 末行', 'For X = 17 To 27')
    t = t.replace('For X = 行业始 To 末行整', 'For X = 31 To 末行整')
    t = t.replace('跨码管理_取名称值(', 'Evaluate(')
    return t

bak_n = normalize(bak)
cur_n = normalize(cur)

if bak_n == cur_n:
    print('完全一致！')
    sys.exit(0)

print(f'长度: bak={len(bak_n)} cur={len(cur_n)}')
diffs = 0
for i, (a, b) in enumerate(zip(bak_n, cur_n)):
    if a != b:
        ctx = 60
        print(f'\n差异 {diffs+1} 在字符 {i}:')
        print(f'  bak: {repr(bak_n[max(0,i-ctx):i+ctx])}')
        print(f'  cur: {repr(cur_n[max(0,i-ctx):i+ctx])}')
        diffs += 1
        if diffs >= 5:
            break