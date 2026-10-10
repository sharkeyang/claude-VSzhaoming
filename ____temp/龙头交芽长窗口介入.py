# -*- coding: utf-8 -*-
"""
龙头交 vs 龙头芽 — 长时间窗口触顶主升率 + 介入时机（周类）
==========================================================
定义：
  龙头交 = BTZB>=BTAB（WXAB由负到正，未触顶）
  龙头芽 = BTZB<BTAB（WXZB劫后上破WJB）
"""
import csv, glob, sys
sys.stdout.reconfigure(encoding='utf-8')

files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))

样本 = []
for f in files:
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i, row in enumerate(rows):
        if len(row) < 20: continue
        波型 = row[5]
        if not 波型.startswith('D'): continue
        try:
            BTZB = int(row[14]); BTAB = int(row[19])
            PR = float(row[2]) if row[2] else None   # 下周涨幅
            HR = float(row[3]) if row[3] else None   # 下周高幅
            护型 = row[4]
        except: continue
        后续 = [rows[j][5] for j in range(i+1, min(i+21, len(rows)))]
        样本.append({'交': BTZB >= BTAB, '后续': 后续, 'PR': PR, 'HR': HR, '护型': 护型})

print(f'龙头分支样本总数: {len(样本)}')
print()

# ============ 1. 长时间窗口触顶主升率 ============
print('='*80)
print('【1】长时间窗口触顶主升率（进龙扩 A开头）')
print('='*80)
def 进扩(seq, k):
    return any(s.startswith('A') for s in seq[:k])
def 进震(seq, k):
    return any(s.startswith('F') for s in seq[:k])
def 转坏(seq, k):
    return any(s.startswith(('NN','NF','FN')) for s in seq[:k])

for 名称, 子集 in [('龙头交', [s for s in 样本 if s['交']]),
                   ('龙头芽', [s for s in 样本 if not s['交']])]:
    n = len(子集)
    print(f'\n{名称}: n={n}')
    for k in [1, 2, 3, 4, 6, 8, 12, 16, 20]:
        e = sum(1 for s in 子集 if 进扩(s['后续'], k))/n*100
        z = sum(1 for s in 子集 if 进震(s['后续'], k))/n*100
        h = sum(1 for s in 子集 if 转坏(s['后续'], k))/n*100
        print(f'  后续{k}周: 进龙扩={e:.1f}%, 进龙震={z:.1f}%, 转坏={h:.1f}%')

# ============ 2. 介入时机 ============
print()
print('='*80)
print('【2】介入时机（下周冲高/涨幅 + 护型构成）')
print('='*80)
def 统计(子集, 名称):
    n = len(子集)
    if n == 0: print(f'{名称}: n=0'); return
    hr = [s['HR'] for s in 子集 if s['HR'] is not None]
    pr = [s['PR'] for s in 子集 if s['PR'] is not None]
    冲高 = sum(1 for x in hr if x >= 3)/len(hr)*100 if hr else 0
    冲高5 = sum(1 for x in hr if x >= 5)/len(hr)*100 if hr else 0
    均涨 = sum(pr)/len(pr) if pr else 0
    甲 = sum(1 for s in 子集 if s['护型'].startswith('a'))/n*100
    乙 = sum(1 for s in 子集 if s['护型'].startswith('b'))/n*100
    print(f'{名称}: n={n}, 下周冲高率(>=3%)={冲高:.2f}%, 冲高率(>=5%)={冲高5:.2f}%, 下周均涨={均涨:.3f}%, 当前甲占比={甲:.1f}%, 乙占比={乙:.1f}%')

统计([s for s in 样本 if s['交']], '  龙头交')
统计([s for s in 样本 if not s['交']], '  龙头芽')

# 介入时机：龙头交内部，按 BTZA 再分（价格是否在EMA5上）
print()
print('  --- 龙头交内部按 BTZA 细分 ---')
# 需要重新读 BTZA
样本2 = []
for f in files:
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i, row in enumerate(rows):
        if len(row) < 20: continue
        if not row[5].startswith('D'): continue
        try:
            BTZA = int(row[13]); BTZB = int(row[14]); BTAB = int(row[19])
            PR = float(row[2]) if row[2] else None
            HR = float(row[3]) if row[3] else None
        except: continue
        样本2.append({'交': BTZB >= BTAB, 'BTZA': BTZA, 'PR': PR, 'HR': HR})

统计([s for s in 样本2 if s['交'] and s['BTZA'] >= 0], '  龙头交+BTZA>=0(价在EMA5上)')
统计([s for s in 样本2 if s['交'] and s['BTZA'] < 0], '  龙头交+BTZA<0(价在EMA5下)')
统计([s for s in 样本2 if not s['交'] and s['BTZA'] >= 0], '  龙头芽+BTZA>=0(价在EMA5上)')
统计([s for s in 样本2 if not s['交'] and s['BTZA'] < 0], '  龙头芽+BTZA<0(价在EMA5下)')