# -*- coding: utf-8 -*-
"""替换 禁止级→G级"""
with open('_主文档/MC3.3_研究日冲策略.md', 'r', encoding='utf-8') as f:
    text = f.read()

count = text.count('禁止级')
text = text.replace('禁止级', 'G级')

with open('_主文档/MC3.3_研究日冲策略.md', 'w', encoding='utf-8') as f:
    f.write(text)

print(f'共替换 {count} 处')