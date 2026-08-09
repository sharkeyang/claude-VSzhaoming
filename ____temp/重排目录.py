# -*- coding: utf-8 -*-
"""重排 MC3.3.5：目录移到最前，〇节移到目录后"""
with open('_主文档/MC3.3.5_日层等高线模型.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 定位〇节和目录
# 〇节从 "## 〇、适用范围" 到 "---" (分隔线)
# 目录从 "## 目录" 到 "## 一、分类系统设计" (不含 一)

start_〇 = content.find('## 〇、适用范围：日冲策略的股票池限定')
end_〇 = content.find('---', start_〇)
end_〇 = content.find('\n', end_〇) + 1  # 包含---换行

start_目录 = content.find('## 目录')
# 目录结束于下一个非子项的一级标题
end_目录 = content.find('\n## 一、分类系统设计', start_目录)

# 提取
if start_〇 == -1 or end_〇 == -1 or start_目录 == -1:
    print('定位失败')
    exit(1)

〇内容 = content[start_〇:end_〇]
目录内容 = content[start_目录:end_目录]

# 从原文删除〇和目录
rest = content[:start_〇] + content[end_〇:]
# 目录在rest中的位置
rest_目录 = rest.find('## 目录')
rest = rest[:rest_目录] + rest[rest.find('\n', rest_目录)+1:]  # 删目录

# 新顺序：目录 → 〇 → 其余
new_content = 目录内容 + '\n\n' + 〇内容 + '\n\n' + rest.strip()

# 清理多余空行
import re
new_content = re.sub(r'\n{4,}', '\n\n\n', new_content)

with open('_主文档/MC3.3.5_日层等高线模型.md', 'w', encoding='utf-8') as f:
    f.write(new_content)
print('重排完成')
