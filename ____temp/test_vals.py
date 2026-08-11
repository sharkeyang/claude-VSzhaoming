# -*- coding: utf-8 -*-
"""
日冲策略三级组合验证脚本 - v2 (净版)
基于216分支全量概率表(2000万样本)
"""
import csv

# 读取CSV
with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

# 护型映射
QIANG = ['上', '中', '忐']  # 甲乙己(强)
RUO = ['下', '忠', '快']    # 丙丁戊(弱)
# NOTE: 快 should be 忑, but encoding issue in display. Let me check the actual DXAB values.

# Check actual DXAB values
dxab_vals = set()
for r in rows:
    dxab_vals.add(r['DXAB'])
print("DXAB values:", sorted(dxab_vals))

# 分组定义
EF_BAD = ['嘘', '尿', '屎']
CD_BAD = ['快', '中', '下']  # 快=忑, 小=下
CD_GOOD = ['上', '忠', '忐']
EF_GOOD = ['金', '银', '唏']

# Let me check actual values first
print("DXEF values:", sorted(set(r['DXEF'] for r in rows)))
print("DXCD values:", sorted(set(r['DXCD'] for r in rows)))