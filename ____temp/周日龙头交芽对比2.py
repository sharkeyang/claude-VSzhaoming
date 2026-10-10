# -*- coding: utf-8 -*-
"""
周类 vs 日类 — 龙头交/龙头芽规律对比（高效版）
============================================
日类数据量大，抽样部分文件加速。
"""
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

def 分析(目录, 前缀, 波型列, BTZA列, BTZB列, BTAB列, PR列, HR列, 标签, 抽样=None):
    files = sorted(glob.glob(f'{目录}/{前缀}_*.csv'))
    if 抽样: files = files[:抽样]
    样本 = []
    for f in files:
        with open(f, encoding='gbk') as fh:
            r = csv.reader(fh)
            next(r)
            rows = list(r)
        for i, row in enumerate(rows):
            if len(row) <= max(BTAB列, HR列): continue
            波型 = row[波型列]
            if not 波型.startswith('D'): continue
            try:
                BTZA = int(row[BTZA列]); BTZB = int(row[BTZB列]); BTAB = int(row[BTAB列])
                PR = float(row[PR列]) if PR列 is not None and row[PR列] else None
                HR = float(row[HR列]) if row[HR列] else None
            except: continue
            后续 = [rows[j][波型列] for j in range(i+1, min(i+11, len(rows)))]
            样本.append({'交': BTZB >= BTAB, 'BTZA': BTZA, '后续': 后续, 'PR': PR, 'HR': HR})
    n = len(样本)
    print(f'\n{"="*80}')
    print(f'【{标签}】龙头分支样本: {n}（文件数={len(files)}）')
    print(f'{"="*80}')

    def 进扩(seq, k): return any(s.startswith('A') for s in seq[:k])
    def 进震(seq, k): return any(s.startswith('F') for s in seq[:k])
    def 转坏(seq, k): return any(s.startswith(('NN','NF','FN')) for s in seq[:k])

    for 名称, 子集 in [('龙头交', [s for s in 样本 if s['交']]),
                       ('龙头芽', [s for s in 样本 if not s['交']])]:
        m = len(子集)
        if m == 0: print(f'\n{名称}: n=0'); continue
        print(f'\n{名称}: n={m}')
        for k in [1, 2, 3, 5, 10]:
            e = sum(1 for s in 子集 if 进扩(s['后续'], k))/m*100
            z = sum(1 for s in 子集 if 进震(s['后续'], k))/m*100
            h = sum(1 for s in 子集 if 转坏(s['后续'], k))/m*100
            print(f'  后续{k}期: 进龙扩={e:.1f}%, 进龙震={z:.1f}%, 转坏={h:.1f}%')

    print(f'\n  --- 介入时机 ---')
    def stat(s, name):
        m=len(s)
        if m==0: print(f'  {name}: n=0'); return
        hr=[x['HR'] for x in s if x['HR'] is not None]
        pr=[x['PR'] for x in s if x['PR'] is not None]
        ch=sum(1 for x in hr if x>=3)/len(hr)*100 if hr else 0
        avg=sum(pr)/len(pr) if pr else 0
        if pr:
            print(f'  {name}: n={m}, 下期冲高(>=3%)={ch:.2f}%, 下期均涨={avg:.3f}%')
        else:
            print(f'  {name}: n={m}, 下期冲高(>=3%)={ch:.2f}%')
    stat([s for s in 样本 if s['交'] and s['BTZA']>=0], '龙头交+价在EMA5上')
    stat([s for s in 样本 if s['交'] and s['BTZA']<0], '龙头交+价在EMA5下')
    stat([s for s in 样本 if not s['交'] and s['BTZA']>=0], '龙头芽+价在EMA5上')
    stat([s for s in 样本 if not s['交'] and s['BTZA']<0], '龙头芽+价在EMA5下')

# 周类全量
分析('昭明算展/谕组周', '谕组周', 5, 13, 14, 19, 2, 3, '周类')
# 日类抽样前600个文件
分析('昭明算展/谕组日', '谕组日', 11, 13, 66, 68, None, 26, '日类(抽样600文件)', 抽样=600)