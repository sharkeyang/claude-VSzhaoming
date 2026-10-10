# -*- coding: utf-8 -*-
"""
龙头分类 — 护型构成分析
================================
理解 BTZB vs BTAB 分歧为何能近乎完美分离甲护型
"""
import csv, glob, os, sys
from collections import Counter, defaultdict
sys.stdout.reconfigure(encoding='utf-8')

files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))

样本 = []
for f in files:
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        for row in r:
            if len(row) < 20:
                continue
            波型 = row[5]
            if not 波型.startswith('D'):
                continue
            try:
                BTZA = int(row[13])
                BTZB = int(row[14])
                BTAB = int(row[19])
                护型 = row[4]
            except (ValueError, IndexError):
                continue
            样本.append((BTZA, BTZB, BTAB, 护型))

print(f'龙头分支样本总数: {len(样本)}')
print()

def 护型构成(子集, 名称):
    n = len(子集)
    if n == 0:
        print(f'{名称}: n=0')
        return
    cnt = Counter(s[3][0] for s in 子集)  # 护型首字符
    total = sum(cnt.values())
    parts = ', '.join(f'{k}={v} ({100*v/total:.1f}%)' for k, v in cnt.most_common())
    print(f'{名称}: n={n}, 护型构成: {parts}')

print('=' * 80)
print('【当前分歧】BTZA')
print('=' * 80)
护型构成([s for s in 样本 if s[0] < 0], '  龙头根 (BTZA<0)')
护型构成([s for s in 样本 if s[0] >= 0], '  龙头芽 (BTZA>=0)')

print()
print('=' * 80)
print('【新分歧】BTZB vs BTAB')
print('=' * 80)
护型构成([s for s in 样本 if s[1] >= s[2]], '  龙头交 (BTZB>=BTAB)')
护型构成([s for s in 样本 if s[1] < s[2]], '  龙头芽 (BTZB<BTAB)')

print()
print('=' * 80)
print('【BTZB 与 BTAB 的关系】')
print('=' * 80)
# 检查 BTZB 和 BTAB 的分布
BTZB_vals = Counter(s[1] for s in 样本)
BTAB_vals = Counter(s[2] for s in 样本)
print('BTZB 分布 (top 15):', ', '.join(f'{k}={v}' for k, v in BTZB_vals.most_common(15)))
print('BTAB 分布 (top 15):', ', '.join(f'{k}={v}' for k, v in BTAB_vals.most_common(15)))

print()
print('=' * 80)
print('【BTZB vs BTAB 差值分布】')
print('=' * 80)
diff = Counter(s[1] - s[2] for s in 样本)
print('BTZB-BTAB 差值分布 (top 20):', ', '.join(f'{k}={v}' for k, v in diff.most_common(20)))

print()
print('=' * 80)
print('【护型与 BTZB/BTAB 关系】按护型首字符分组看 BTZB-BTAB 均值')
print('=' * 80)
by_护型 = defaultdict(list)
for s in 样本:
    by_护型[s[3][0]].append(s[1] - s[2])
for k, v in sorted(by_护型.items()):
    avg = sum(v) / len(v)
    print(f'  护型{k}: n={len(v)}, BTZB-BTAB均值={avg:.2f}')
