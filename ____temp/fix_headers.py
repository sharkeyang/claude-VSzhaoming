# -*- coding: utf-8 -*-
with open('_主文档/MC3.3_研究日冲策略.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 修复第一章标题
old = '日顶型 → 辅助日级别主升的判断\n```\n\n### 1.1 核心主张'
new = '日顶型 → 辅助日级别主升的判断\n```\n\n---\n\n## 第一章 日类必赢算法V1：DXZE+DXZC\n\n> 基于DXZE>0+DXZC>0条件，从进入到退出持有期胜率93.1%的策略。\n> 高波池（Qic+Qim+Qit）验证（2026-08-17）。\n\n### 1.1 核心主张'
content = content.replace(old, new)

# 修复第三章标题
old3 = '## 第三章 日类必赢算法V2'
new3 = '## 第三章 日类必赢算法V2：DXCD+DXZC+DXAB'
content = content.replace(old3, new3)

with open('_主文档/MC3.3_研究日冲策略.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('done')