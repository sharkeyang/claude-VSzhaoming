# -*- coding: utf-8 -*-
"""
龙头交 vs 龙头芽 — 后续波型演变验证（周类）
==========================================
定义（用户）：
  龙头交 = BTZB>=BTAB（WXAB由负到正，未触顶，未进管）
  龙头芽 = BTZB<BTAB（WXZB劫后上破WJB，未进管）
假设：
  龙头交 → 后续形成触顶主升（进入龙扩 A开头）
  龙头芽 → 诱多/震荡（进入龙震 F开头 或 转坏）
"""
import csv, glob, sys
from collections import Counter
sys.stdout.reconfigure(encoding='utf-8')

files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))

# 收集龙头分支样本（波型以 D 开头 = 未触顶未进管），记录后续波型演变
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
        except: continue
        # 后续波型序列（最多看后续10周）
        后续 = [rows[j][5] for j in range(i+1, min(i+11, len(rows)))]
        样本.append({'交': BTZB >= BTAB, '后续': 后续})

print(f'龙头分支样本总数: {len(样本)}')
print()

def 演变(子集, 名称):
    n = len(子集)
    if n == 0: print(f'{名称}: n=0'); return
    # 后续1周内是否进入龙扩(A开头=触顶主升)
    def 进扩(seq, k):
        return any(s.startswith('A') for s in seq[:k])
    def 进震(seq, k):
        return any(s.startswith('F') for s in seq[:k])
    def 转坏(seq, k):
        # 转坏 = 波型变 NN(虎) 或 NF(武) 或 FN(雀)
        return any(s.startswith(('NN','NF','FN')) for s in seq[:k])
    def 仍龙头(seq, k):
        return all(s.startswith('D') for s in seq[:k])
    print(f'{名称}: n={n}')
    for k in [1, 2, 3, 5, 10]:
        e = sum(1 for s in 子集 if 进扩(s['后续'], k))/n*100
        z = sum(1 for s in 子集 if 进震(s['后续'], k))/n*100
        h = sum(1 for s in 子集 if 转坏(s['后续'], k))/n*100
        l = sum(1 for s in 子集 if 仍龙头(s['后续'], k))/n*100
        print(f'  后续{k}周内: 进龙扩(触顶主升)={e:.1f}%, 进龙震(震荡)={z:.1f}%, 转坏(虎/武/雀)={h:.1f}%, 仍龙头={l:.1f}%')

print('='*80)
print('【龙头交】BTZB>=BTAB（WXAB由负到正，未触顶）')
print('='*80)
演变([s for s in 样本 if s['交']], '  龙头交')

print()
print('='*80)
print('【龙头芽】BTZB<BTAB（WXZB劫后上破WJB）')
print('='*80)
演变([s for s in 样本 if not s['交']], '  龙头芽')