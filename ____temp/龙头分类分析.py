# -*- coding: utf-8 -*-
"""
龙头分类分析 — 对比两种分歧
================================
当前分歧（BTZA）：龙头根(BTZA<0) vs 龙头芽(BTZA>=0)
新分歧（BTZB vs BTAB）：龙头交(BTZB>=BTAB) vs 龙头芽(BTZB<BTAB)

数据：谕组周 CSV（GBK）
列：波型[5], ZA周[13]=WXZA, ZB周[14]=WXZB, AB周[19]=WXAB,
    护型[4], PR[2]=下周涨幅, HR[3]=下周高幅
"""
import csv, glob, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))

# 收集龙头分支样本
# 龙头分支 = 波型以 "D" 开头（De龙头根 / Dd龙头芽）
样本 = []  # (BTZA, BTZB, BTAB, 下周涨幅, 下周高幅, 护型)
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
                下周涨幅 = float(row[2]) if row[2] else None
                下周高幅 = float(row[3]) if row[3] else None
                护型 = row[4]
            except (ValueError, IndexError):
                continue
            样本.append((BTZA, BTZB, BTAB, 下周涨幅, 下周高幅, 护型))

print(f'龙头分支样本总数: {len(样本)}')
print()

def 统计(子集, 名称):
    n = len(子集)
    if n == 0:
        print(f'{名称}: n=0')
        return
    # 下周冲高 P(高幅>=3%)
    冲高 = [s[4] for s in 子集 if s[4] is not None]
    冲高率 = sum(1 for x in 冲高 if x >= 3) / len(冲高) * 100 if 冲高 else 0
    # 下周涨幅均值
    涨幅 = [s[3] for s in 子集 if s[3] is not None]
    均涨 = sum(涨幅) / len(涨幅) if 涨幅 else 0
    # 转甲率（护型首字符为 a甲）
    甲 = sum(1 for s in 子集 if s[5].startswith('a'))
    甲率 = 甲 / n * 100
    # 转坏率（护型首字符为 c丙/z丁/y戊，即非甲乙己）
    坏 = sum(1 for s in 子集 if s[5].startswith(('c', 'z', 'y')))
    坏率 = 坏 / n * 100
    print(f'{名称}: n={n}, 下周冲高率={冲高率:.2f}%, 下周均涨={均涨:.3f}%, 转甲率={甲率:.2f}%, 转坏率={坏率:.2f}%')

print('=' * 80)
print('【当前分歧】按 BTZA（JZ vs JA）')
print('=' * 80)
统计([s for s in 样本 if s[0] < 0], '  龙头根 (BTZA<0)')
统计([s for s in 样本 if s[0] >= 0], '  龙头芽 (BTZA>=0)')

print()
print('=' * 80)
print('【新分歧】按 BTZB vs BTAB（JZ vs JB 对比 JA vs JB）')
print('=' * 80)
统计([s for s in 样本 if s[1] >= s[2]], '  龙头交 (BTZB>=BTAB)')
统计([s for s in 样本 if s[1] < s[2]], '  龙头芽 (BTZB<BTAB)')

print()
print('=' * 80)
print('【交叉对比】两种分歧的 2x2 组合')
print('=' * 80)
统计([s for s in 样本 if s[0] < 0 and s[1] >= s[2]], '  根+交 (BTZA<0, BTZB>=BTAB)')
统计([s for s in 样本 if s[0] < 0 and s[1] < s[2]], '  根+芽 (BTZA<0, BTZB<BTAB)')
统计([s for s in 样本 if s[0] >= 0 and s[1] >= s[2]], '  芽+交 (BTZA>=0, BTZB>=BTAB)')
统计([s for s in 样本 if s[0] >= 0 and s[1] < s[2]], '  芽+芽 (BTZA>=0, BTZB<BTAB)')

print()
print('=' * 80)
print('【分歧一致性】两种分歧的重叠程度')
print('=' * 80)
# 当前分歧：根(BTZA<0) vs 芽(BTZA>=0)
# 新分歧：交(BTZB>=BTAB) vs 芽(BTZB<BTAB)
根 = [s for s in 样本 if s[0] < 0]
芽_当前 = [s for s in 样本 if s[0] >= 0]
交 = [s for s in 样本 if s[1] >= s[2]]
芽_新 = [s for s in 样本 if s[1] < s[2]]
print(f'当前分歧: 根={len(根)}, 芽={len(芽_当前)}')
print(f'新分歧:   交={len(交)}, 芽={len(芽_新)}')
# 重叠：根∩交, 根∩芽, 芽∩交, 芽∩芽
根交 = sum(1 for s in 样本 if s[0] < 0 and s[1] >= s[2])
根芽 = sum(1 for s in 样本 if s[0] < 0 and s[1] < s[2])
芽交 = sum(1 for s in 样本 if s[0] >= 0 and s[1] >= s[2])
芽芽 = sum(1 for s in 样本 if s[0] >= 0 and s[1] < s[2])
print(f'根∩交={根交}, 根∩芽={根芽}, 芽∩交={芽交}, 芽∩芽={芽芽}')
print(f'一致性(根∩交+芽∩芽)={根交+芽芽} ({100*(根交+芽芽)/len(样本):.1f}%)')
print(f'分歧(根∩芽+芽∩交)={根芽+芽交} ({100*(根芽+芽交)/len(样本):.1f}%)')
