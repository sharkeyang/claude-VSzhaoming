# -*- coding: utf-8 -*-
"""Fix §2: header rename, trend strategy concept, remove duplicate, merge 2.1.4"""
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
with open(c_path, 'r', encoding='utf-8') as f:
    content = f.read()

nl = '\n'

# =========
# 1. §2.1 header
# =========
content = content.replace(
    '### 2.1 专题一：多长仓位与冲高策略的统一',
    '### 2.1 专题一：趋势策略与冲高策略的统一')

# Update TOC too
content = content.replace(
    '- [2.1 专题一：多长仓位与冲高策略的统一',
    '- [2.1 专题一：趋势策略与冲高策略的统一')

# =========
# 2. §2.1.2: 月基策略 -> 趋势策略
# =========
# Find the old header
old_header_212 = '#### 2.1.2 月基策略 = 多长底仓（长线持有）'
new_header_212 = '#### 2.1.2 趋势策略 = 多长底仓（长线持有）'
content = content.replace(old_header_212, new_header_212)
content = content.replace('- [2.1.2 月基策略 = 多长底仓（长线持有）', '- [2.1.2 趋势策略 = 多长底仓（长线持有）')

# Replace 月基策略 with 趋势策略 within §2.1.2 content only
# Find the boundaries of §2.1.2
idx_212 = content.find('#### 2.1.2 趋势策略')
idx_213 = content.find('#### 2.1.3 周冲/日冲策略')
if idx_212 > 0 and idx_213 > idx_212:
    sec_212 = content[idx_212:idx_213]
    sec_212_new = sec_212.replace('月基策略', '趋势策略')
    sec_212_new = sec_212_new.replace('月基评分', '趋势评分')
    sec_212_new = sec_212_new.replace('月基仓位', '趋势仓位')
    content = content[:idx_212] + sec_212_new + content[idx_213:]

# =========
# 3. Remove §2.1.4, merge content into §2.3.4
# =========
# Find and extract 2.1.4 content
idx_214 = content.find('#### 2.1.4 对已有代码的影响')
idx_215 = content.find('#### 2.1.5')
if idx_214 < 0:
    idx_214 = content.find('#### 2.1.4 对VBA代码的影响')
    idx_215 = content.find('#### 2.1.5')

if idx_214 > 0:
    # Extract 2.1.4 content
    sec_214 = content[idx_214:idx_215]
    # Save as appendix note for 2.3.4
    appendix_214 = nl + '> **附录：旧版VBA代码重构说明（来自原§2.1.4）**' + nl
    for line in sec_214.split(nl):
        if line.strip() and not line.strip().startswith('####'):
            appendix_214 += '> ' + line + nl
        elif line.strip().startswith('####'):
            appendix_214 += '> **' + line.strip().replace('#### ', '') + '**' + nl

    # Remove 2.1.4 from its current position
    content = content[:idx_214] + content[idx_215:]

    # Insert into 2.3.4 (before the last line)
    idx_234 = content.find('#### 2.3.4')
    # Find the end of 2.3.4 (next ### or ##)
    idx_next = content.find(nl + '### ', idx_234 + 20)
    if idx_next < 0:
        idx_next = content.find(nl + '## 三', idx_234 + 20)
    if idx_next > 0:
        content = content[:idx_next] + appendix_214 + content[idx_next:]

# =========
# 4. Fix §2.2: remove duplicate 2.2.8, reorder 2.2.6/2.2.7
# =========
# Current: 2.2.5 -> 2.2.7(日柱排列) -> 2.2.8(日柱排列-dup) -> 2.2.6(日级别分类)
# Desired: 2.2.5 -> 2.2.6(日级别分类) -> 2.2.7(日柱排列)

# Step A: Remove duplicate 2.2.8 (日柱排列)
mark_228 = '#### 2.2.8 日柱排列的介入时机'
mark_226 = '#### 2.2.6 日级别分类的初步统计'
# 2.2.8 is between 2.2.7 and 2.2.6
# The block: from 2.2.8 to 2.2.6
idx_228 = content.find(mark_228)
idx_226 = content.find(mark_226)
if idx_228 > 0 and idx_226 > idx_228:
    # Remove 2.2.8 block
    content = content[:idx_228] + content[idx_226:]
    print('Removed duplicate 2.2.8')

# Step B: Now we have 2.2.5 -> 2.2.7(日柱排列) -> 2.2.6(日级别分类)
# Renumber: 2.2.6(日级别分类) should come BEFORE 2.2.7(日柱排列)
# So: 2.2.6=日级别分类, 2.2.7=日柱排列
# Currently: 2.2.7 has 日柱排列 content, 2.2.6 has 日级别分类 content
# Just swap the numbers

# Find current positions again
idx_227_new = content.find('#### 2.2.7 日柱排列的介入时机')
idx_226_new = content.find('#### 2.2.6 日级别分类的初步统计')

if idx_227_new > 0 and idx_226_new > idx_227_new:
    # Content order: ...2.2.7(日柱排列)...2.2.6(日级别分类)...
    # Extract blocks
    mark_227b = '#### 2.2.7 日柱排列的介入时机'
    mark_226b = '#### 2.2.6 日级别分类的初步统计'
    mark_23b = '### 2.3'

    b227_s = content.find(mark_227b)
    b226_s = content.find(mark_226b)
    b23_s = content.find(mark_23b)

    if b227_s > 0 and b226_s > b227_s and b23_s > b226_s:
        block_227 = content[b227_s:b226_s]
        block_226 = content[b226_s:b23_s]

        # Swap: place 日级别分类 first, 日柱排列 second
        content = content[:b227_s] + block_226 + block_227 + content[b23_s:]

        # Now renumber
        # block_226 (日级别分类) becomes 2.2.6 (already correct)
        # block_227 (日柱排列) was 2.2.7, should become 2.2.7 (already correct after the swap)
        # Actually after the swap, 日级别分类 is at the 2.2.6 position and 日柱排列 is at the 2.2.7 position
        # No renumbering needed! The swap itself achieves the correct order.

        # But the HEADERS still say the old numbers. Let me fix them.
        # After swap: first section has header 2.2.6日级别分类, second has 2.2.7日柱排列
        # This is already correct!
        print('Swapped order - should be correct now')
else:
    print(f'Order check: 227 at {idx_227_new}, 226 at {idx_226_new}')

# =========
# 5. Update TOC
# =========
# Fix §2.2 TOC
# Remove 2.2.8 from TOC if present
content = content.replace('- [2.2.8 日柱排列的介入时机](#228-日柱排列的介入时机)\n', '')
content = content.replace('- [2.2.8 日柱排列的介入时机](#228-日柱排列的介入时机)', '')

# Ensure correct 2.2.6 and 2.2.7 in TOC
content = content.replace(
    '- [2.2.6 日级别分类的初步统计](#226-日级别分类的初步统计)',
    '- [2.2.6 日级别分类的初步统计](#226-日级别分类的初步统计)')
content = content.replace(
    '- [2.2.7 日柱排列的介入时机](#227-日柱排列的介入时机)',
    '- [2.2.7 日柱排列的介入时机](#227-日柱排列的介入时机)')

# Fix 2.1.2 TOC entry
content = content.replace('- [2.1.2 趋势策略 = 多长底仓（长线持有）', '- [2.1.2 趋势策略 = 多长底仓（长线持有）')

with open(c_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f'Total: {len(content)} chars')
with open(c_path, 'r', encoding='utf-8') as f:
    result = f.read()

for check in ['趋势策略与冲高策略的统一', '#### 2.1.2 趋势策略', '#### 2.2.6 日级别分类',
              '#### 2.2.7 日柱排列', '#### 2.2.8']:
    if check in result:
        print(f'  EXISTS: {check[:50]}')
    else:
        print(f'  REMOVED: {check[:50]}')

# Check duplicate count
cnt = result.count('日柱排列的介入时机')
print(f'日柱排列的介入时机 count: {cnt} (expected 2: TOC + section)')