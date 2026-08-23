# -*- coding: utf-8 -*-
with open('_主文档/MC3.3_研究日冲策略.md', 'r', encoding='utf-8') as f:
    content = f.read()

old = '日等型 → 在DXAB基础上制定有到条件不满足"策略无关。在持有到条件不满足策略下，BSHA低只是延长持有期，不影响最终胜率。\n\n---\n---\n\n## 第一章 日类必赢算法V1：DXZE+DXZC'
new = '日等型 → 在DXAB基础上制定主升浪策略\n  ↓\n日柱型 → 辅助日级别主升的判断\n日顶型 → 辅助日级别主升的判断\n```\n\n---\n\n## 第一章 日类必赢算法V1：DXZE+DXZC'
content = content.replace(old, new)

with open('_主文档/MC3.3_研究日冲策略.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('done')