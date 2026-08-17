#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一月基查分文件命名：月基分命→月策分命，月基分日→月策分日
"""

import os

# ============================================================
# 1. 神谕.bas — 更新文件路径和注释
# ============================================================
with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas', 'r', encoding='utf-8') as f:
    content = f.read()

# 文件路径
content = content.replace('vba月基分命表.csv', 'vba月策分命表.csv')
content = content.replace('vba月基分日表_市板.csv', 'vba月策分日表_市板.csv')

# 注释中的旧名
content = content.replace('月基分命表', '月策分命表')
content = content.replace('月基分日表', '月策分日表')

with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas', 'w', encoding='utf-8') as f:
    f.write(content)
print('神谕.bas 更新完成')

# ============================================================
# 2. 重命名外部文件
# ============================================================
file_renames = [
    ('_产出物/_工具/vba月基分命表.csv', '_产出物/_工具/vba月策分命表.csv'),
    ('_产出物/_工具/vba月基分日表.csv', '_产出物/_工具/vba月策分日表.csv'),
    ('_产出物/_工具/vba月基分日表_市板.csv', '_产出物/_工具/vba月策分日表_市板.csv'),
]

for old_path, new_path in file_renames:
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f'{os.path.basename(old_path)} → {os.path.basename(new_path)}')
    else:
        print(f'{old_path} 不存在，跳过')

print()
print('全部完成')