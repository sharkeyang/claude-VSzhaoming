# -*- coding: utf-8 -*-
"""
日冲策略三级组合验证脚本 - v2 (净版)
基于216分支全量概率表(2000万样本)
"""
import csv
import sys

# Force UTF-8 output
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))

DXAB_TO_HU = {
    '上': '甲', '中': '乙', '忠': '丁',
    '下': '丙', '忐': '己', '快': '戊'
}
# Actually, let me use the actual characters
QIANG = ['上', '中', '忐']  # 上中忐 = 甲乙己
RUO = ['下', '忠', '快']    # 下忠忑 = 丙丁戊... wait, 忑 is not 夬

# Let me just use read the actual characters
with open('____temp/DXEF_DXCD_DXAB_完整概率表2.csv', 'r', encoding='utf-8-sig') as f:
    header = f.readline().strip().split(',')
    print("CSV columns:", header)