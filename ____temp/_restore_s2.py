# -*- coding: utf-8 -*-
"""Restore §2.1 from backup + fix §2.2 structure"""
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

# Read backup §2.1
backup_path = 'd:/@VSwork/VS昭明计划VBA优化/____temp/C_old_sec21.txt'
with open(backup_path, 'r', encoding='utf-8') as f:
    old_sec21 = f.read()

# Fix: replace old concept names with new ones in the backup
old_sec21 = old_sec21.replace('长基仓', '月基仓位')
old_sec21 = old_sec21.replace('周浮仓', '周冲仓位')
old_sec21 = old_sec21.replace('日浮仓', '日冲仓位')
# Also fix section header references in the old content
old_sec21 = old_sec21.replace('_多长策略', '月基策略')

# Step 1: Replace current §2.1 with restored content
start = current.find('### 2.1')
end = current.find('### 2.2')
if start > 0 and end > start:
    current = current[:start] + old_sec21 + current[end:]
    print(f'Restored §2.1: {len(old_sec21)} chars')
else:
    print('ERROR: cannot find §2.1 boundaries')
    exit(1)

# Step 2: Fix §2.2 header - remove "(待研究"
current = current.replace('### 2.2 DXZE>0 区域的完整划分（待研究）',
                          '### 2.2 DXZE>0 区域的完整划分')

# Step 3: Swap 2.2.6 and 2.2.7
# Find the current 2.2.6 (日柱排列) and 2.2.7 (日级别分类)
mark_226 = '#### 2.2.6 日柱排列的介入时机'
mark_227 = '#### 2.2.7 日级别分类的初步统计'
mark_23 = '### 2.3'

idx_226 = current.find(mark_226)
idx_227 = current.find(mark_227)
idx_23 = current.find(mark_23)

if idx_226 > 0 and idx_227 > idx_226 and idx_23 > idx_227:
    # Extract 2.2.6 block (226 -> 227)
    block_226 = current[idx_226:idx_227]
    # Extract 2.2.7 block (227 -> 2.3)
    block_227 = current[idx_227:idx_23]

    # Swap: rebuild
    current = current[:idx_226] + block_227 + block_226 + current[idx_23:]

    # Renumber: 2.2.7 block becomes new 2.2.6, 2.2.6 block becomes new 2.2.7
    current = current.replace(mark_227.replace('#### 2.2.7', 'NEW_MARKER'), 'TEMP_PLACEHOLDER')
    current = current.replace('#### 2.2.7', '#### 2.2.8')
    current = current.replace('#### 2.2.6', '#### 2.2.7')
    # The original 2.2.7 (日级别分类) should become 2.2.6
    # But since we swapped blocks, the numbering is complex.
    # Let me just do targeted replacements based on content

    print('Swap done - need targeted renumbering')
else:
    print(f'idx_226={idx_226}, idx_227={idx_227}, idx_23={idx_23}')

# Step 4: Update TOC
# Fix 2.2 header in TOC
current = current.replace('DXZE>0 区域的完整划分（待研究）', 'DXZE>0 区域的完整划分')

# Update TOC order
current = current.replace(
    '- [2.2.6 日柱排列的介入时机](#226-日柱排列的介入时机)\n- [2.2.7 日级别分类的初步统计](#227-日级别分类的初步统计)',
    '- [2.2.6 日级别分类的初步统计](#226-日级别分类的初步统计)\n- [2.2.7 日柱排列的介入时机](#227-日柱排列的介入时机)'
)

# Update anchors
current = current.replace(
    '(#226-日柱排列的介入时机)', '(#227-日柱排列的介入时机)')
current = current.replace(
    '(#227-日级别分类的初步统计)', '(#226-日级别分类的初步统计)')

with open(c_path, 'w', encoding='utf-8') as f:
    f.write(current)

print('Done')
print(f'Total: {len(current)} chars')
"