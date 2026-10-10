# -*- coding: utf-8 -*-
"""
龙头分类 — 完整分析（含下周转甲率）
================================
对比两种分歧：
  当前：龙头根(BTZA<0) vs 龙头芽(BTZA>=0)
  新：龙头交(BTZB>=BTAB) vs 龙头芽(BTZB<BTAB)

指标：
  下周冲高率 P(下周高幅>=3%)
  下周均涨
  下周转甲率（下周护型首字符=a甲）
  下周转坏率（下周护型首字符=c丙/z丁/y戊）
"""
import csv, glob, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))

# 每个股票按日期排序，计算下周护型
def 统计(子集, 名称):
    n = len(子集)
    if n == 0:
        print(f'{名称}: n=0')
        return
    冲高 = [s['HR'] for s in 子集 if s['HR'] is not None]
    冲高率 = sum(1 for x in 冲高 if x >= 3) / len(冲高) * 100 if 冲高 else 0
    涨幅 = [s['PR'] for s in 子集 if s['PR'] is not None]
    均涨 = sum(涨幅) / len(涨幅) if 涨幅 else 0
    # 下周转甲率
    nxt = [s['nxt护型'] for s in 子集 if s['nxt护型']]
    转甲 = sum(1 for x in nxt if x.startswith('a'))
    转甲率 = 转甲 / len(nxt) * 100 if nxt else 0
    转坏 = sum(1 for x in nxt if x.startswith(('c', 'z', 'y')))
    转坏率 = 转坏 / len(nxt) * 100 if nxt else 0
    # 当前甲占比
    甲占比 = sum(1 for s in 子集 if s['护型'].startswith('a')) / n * 100
    print(f'{名称}: n={n}, 下周冲高率={冲高率:.2f}%, 下周均涨={均涨:.3f}%, 下周转甲率={转甲率:.2f}%, 下周转坏率={转坏率:.2f}%, 当前甲占比={甲占比:.1f}%')

样本 = []
for f in files:
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        rows = list(r)
    for i, row in enumerate(rows):
        if len(row) < 20:
            continue
        波型 = row[5]
        if not 波型.startswith('D'):
            continue
        try:
            BTZA = int(row[13])
            BTZB = int(row[14])
            BTAB = int(row[19])
            PR = float(row[2]) if row[2] else None
            HR = float(row[3]) if row[3] else None
            护型 = row[4]
        except (ValueError, IndexError):
            continue
        # 下周护型
        nxt护型 = rows[i+1][4] if i+1 < len(rows) else ''
        样本.append({'BTZA': BTZA, 'BTZB': BTZB, 'BTAB': BTAB,
                   'PR': PR, 'HR': HR, '护型': 护型, 'nxt护型': nxt护型})

print(f'龙头分支样本总数: {len(样本)}')
print()

print('=' * 80)
print('【当前分歧】按 BTZA（JZ vs JA）')
print('=' * 80)
统计([s for s in 样本 if s['BTZA'] < 0], '  龙头根 (BTZA<0)')
统计([s for s in 样本 if s['BTZA'] >= 0], '  龙头芽 (BTZA>=0)')

print()
print('=' * 80)
print('【新分歧】按 BTZB vs BTAB（JZ vs JB 对比 JA vs JB）')
print('=' * 80)
统计([s for s in 样本 if s['BTZB'] >= s['BTAB']], '  龙头交 (BTZB>=BTAB)')
统计([s for s in 样本 if s['BTZB'] < s['BTAB']], '  龙头芽 (BTZB<BTAB)')

print()
print('=' * 80)
print('【交叉对比】两种分歧的 2x2 组合')
print('=' * 80)
统计([s for s in 样本 if s['BTZA'] < 0 and s['BTZB'] >= s['BTAB']], '  根+交 (BTZA<0, BTZB>=BTAB)')
统计([s for s in 样本 if s['BTZA'] < 0 and s['BTZB'] < s['BTAB']], '  根+芽 (BTZA<0, BTZB<BTAB)')
统计([s for s in 样本 if s['BTZA'] >= 0 and s['BTZB'] >= s['BTAB']], '  芽+交 (BTZA>=0, BTZB>=BTAB)')
统计([s for s in 样本 if s['BTZA'] >= 0 and s['BTZB'] < s['BTAB']], '  芽+芽 (BTZA>=0, BTZB<BTAB)')

print()
print('=' * 80)
print('【分歧一致性】两种分歧的重叠程度')
print('=' * 80)
根 = [s for s in 样本 if s['BTZA'] < 0]
芽_当前 = [s for s in 样本 if s['BTZA'] >= 0]
交 = [s for s in 样本 if s['BTZB'] >= s['BTAB']]
芽_新 = [s for s in 样本 if s['BTZB'] < s['BTAB']]
print(f'当前分歧: 根={len(根)}, 芽={len(芽_当前)}')
print(f'新分歧:   交={len(交)}, 芽={len(芽_新)}')
根交 = sum(1 for s in 样本 if s['BTZA'] < 0 and s['BTZB'] >= s['BTAB'])
根芽 = sum(1 for s in 样本 if s['BTZA'] < 0 and s['BTZB'] < s['BTAB'])
芽交 = sum(1 for s in 样本 if s['BTZA'] >= 0 and s['BTZB'] >= s['BTAB'])
芽芽 = sum(1 for s in 样本 if s['BTZA'] >= 0 and s['BTZB'] < s['BTAB'])
print(f'根∩交={根交}, 根∩芽={根芽}, 芽∩交={芽交}, 芽∩芽={芽芽}')
print(f'一致性(根∩交+芽∩芽)={根交+芽芽} ({100*(根交+芽芽)/len(样本):.1f}%)')
print(f'分歧(根∩芽+芽∩交)={根芽+芽交} ({100*(根芽+芽交)/len(样本):.1f}%)')