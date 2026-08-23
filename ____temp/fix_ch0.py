# -*- coding: utf-8 -*-
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = '_主文档/MC3.3_研究日冲策略.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 删除游离的决策树（第67-94行，在"## 第〇章"标题之前）
# 找到"---\n\n### 0.1 完整操盘决策树"（游离的）
free_start = content.index('### 0.1 完整操盘决策树')
# 找到它前面的"---\n\n"
prev_sep = content.rindex('\n---\n\n', 0, free_start)
# 找到游离决策树结束（下一个"## 第〇章"）
ch0_pos = content.index('## 第〇章 从月策略日到必赢算法', free_start)
# 删除从prev_sep到ch0_pos的内容
content = content[:prev_sep] + content[ch0_pos:]

# 2. 修复0.0表格列头（缺 →ZE>0 列）
old_header = '| 等级 | DXEF | DXCD | DXAB | 当前位置 |  | 含义 |'
new_header = '| 等级 | DXEF | DXCD | DXAB | 当前位置 | `→ZE>0` | 含义 |'
content = content.replace(old_header, new_header)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('done')