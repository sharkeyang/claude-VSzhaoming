# -*- coding: utf-8 -*-
"""
周类 vs 日类 — 龙头交/龙头芽规律对比验证
========================================
定义：
  龙头交 = BTZB>=BTAB（WXAB由负到正，未触顶）
  龙头芽 = BTZB<BTAB（WXZB劫后上破WJB）
假设：龙头交→触顶主升，龙头芽→诱多/震荡

列映射：
  周类: 波型[5], BTZA[13], BTZB[14], BTAB[19], PR[2], HR[3]
  日类: 波型[11], BTZA[13], BTZB[66], BTAB[68], PR[?], HR[?]
"""
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

def 分析(目录, 前缀, 波型列, BTZA列, BTZB列, BTAB列, PR列, HR列, 标签):
    files = sorted(glob.glob(f'{目录}/{前缀}_*.csv'))
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
    print(f'【{标签}】龙头分支样本总数: {n}')
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

    # 介入时机
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

# 周类
分析('昭明算展/谕组周', '谕组周', 5, 13, 14, 19, 2, 3, '周类')
# 日类：下期高幅=次日高幅[26]，无下期涨幅列（PR列传None）
分析('昭明算展/谕组日', '谕组日', 11, 13, 66, 68, None, 26, '日类')