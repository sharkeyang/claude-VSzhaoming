# -*- coding: utf-8 -*-
"""Restore §2.1, fix §2.2 header, renumber 2.2.6<->2.2.7"""
import os
root = os.getcwd()
rules_dir = None
for item in os.listdir(root):
    if item.startswith('_') and os.path.isdir(os.path.join(root, item)):
        full = os.path.join(root, item)
        files = os.listdir(full)
        if '全局_C昭明路线图.md' in files:
            rules_dir = full
            break

c_path = os.path.join(rules_dir, '全局_C昭明路线图.md')

# Read current file
with open(c_path, 'r', encoding='utf-8') as f:
    current = f.read()

nl = '\n'

# ---- Step 1: Restore §2.1 from backup ----
backup_path = 'd:/@VSwork/VS昭明计划VBA优化/____temp/C_old_sec21.txt'
with open(backup_path, 'r', encoding='utf-8') as f:
    old = f.read()

# Update concepts in old content
old = old.replace('长基仓', '月基仓位')
old = old.replace('周浮仓', '周冲仓位')
old = old.replace('日浮仓', '日冲仓位')
old = old.replace('_多长策略', '月基策略')

# Replace old header
old = old.replace(
    '#### 2.1.1 四区划总览（从好到差）',
    '#### 2.1.1 四区划总览')

start = current.find('### 2.1')
end = current.find('### 2.2')
if start > 0 and end > start:
    current = current[:start] + old + current[end:]
    print(f'Restored §2.1: {len(old)} chars')
else:
    print('ERROR: §2.1 boundaries not found')
    exit(1)

# ---- Step 2: Fix §2.2 header ----
current = current.replace(
    '### 2.2 DXZE>0 区域的完整划分（待研究）',
    '### 2.2 DXZE>0 区域的完整划分')

# ---- Step 3: Renumber 2.2.6 <-> 2.2.7 ----
# The current order: 2.2.6=日柱排列, 2.2.7=日级别分类
# Desired order: 2.2.6=日级别分类, 2.2.7=日柱排列

# Use unique markers to avoid conflicts
# First: temporarly rename both to unique names
current = current.replace(
    '#### 2.2.6 日柱排列的介入时机',
    '#### 2.2.6_TEMP_日柱排列')
current = current.replace(
    '#### 2.2.7 日级别分类的初步统计',
    '#### 2.2.7_TEMP_日级别分类')

# Now swap numbers
current = current.replace(
    '#### 2.2.6_TEMP_日柱排列',
    '#### 2.2.7 日柱排列的介入时机')
current = current.replace(
    '#### 2.2.7_TEMP_日级别分类',
    '#### 2.2.6 日级别分类的初步统计')

# ---- Step 4: Update TOC ----
current = current.replace(
    '- [2.2.6 日柱排列的介入时机](#226-日柱排列的介入时机)',
    '- [2.2.6_TEMP_日柱排列')
current = current.replace(
    '- [2.2.7 日级别分类的初步统计](#227-日级别分类的初步统计)',
    '- [2.2.7_TEMP_日级别分类')

# Now swap
current = current.replace(
    '- [2.2.6_TEMP_日柱排列',
    '- [2.2.7 日柱排列的介入时机](#227-日柱排列的介入时机)')
current = current.replace(
    '- [2.2.7_TEMP_日级别分类',
    '- [2.2.6 日级别分类的初步统计](#226-日级别分类的初步统计)')

# Fix TOC anchors
current = current.replace(
    '(#226-日柱排列的介入时机)', '(#227-日柱排列的介入时机)')
current = current.replace(
    '(#227-日级别分类的初步统计)', '(#226-日级别分类的初步统计)')

with open(c_path, 'w', encoding='utf-8') as f:
    f.write(current)

print('Done')
with open(c_path, 'r', encoding='utf-8') as f:
    result = f.read()

# Verify
for h in ['#### 2.2.6 日级别分类', '#### 2.2.7 日柱排列']:
    if h in result:
        print(f'  OK: {h}')
    else:
        print(f'  MISSING: {h}')

print(f'Total: {len(result)} chars')
print(f'Contain 警示一: {result.count("警示一")}')
print(f'Contain 四区划总览表: {result.count("<table")}')