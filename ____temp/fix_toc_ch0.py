# -*- coding: utf-8 -*-
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

path = '_主文档/MC3.3_研究日冲策略.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 修复目录结尾：4.5条目后补上 --- 和第〇章标题
old = '- [4.5 为什么G级需要单独处理为"傻吃屎豆"](#45-为什么g级需要单独处理为傻吃屎豆)----|:----|:----|:----|:-------|:-------:|:------|'
new = '- [4.5 为什么G级需要单独处理为"傻吃屎豆"](#45-为什么g级需要单独处理为傻吃屎豆)\n\n---\n\n## 第〇章 从月策略日到必赢算法\n\n> 本文档是 **月基策略（MC3.1）的日级别展开**，对应月基带日（第五章）的日级别执行框架。\n\n### 0.0 月策略日：8格分类系统\n\n月策略日（MC3.1§5）用DXEF→DXCD→DXAB三级带动，将日级别状态分为8格（A~H级）：\n\n| 等级 | DXEF | DXCD | DXAB | 当前位置 | `→ZE>0` | 含义 |'
content = content.replace(old, new)

# 2. 删除第64行重复的第〇章标题（在V1→V2路线图之后）
old2 = '- **第四章**：日周联动，将日级别操作纳入周级别框架\n## 第〇章 从月策略日到必赢算法\n\n> 本文档是 **月基策略（MC3.1）的日级别展开**，对应月基带日（第五章）的日级别执行框架。\n'
new2 = '- **第四章**：日周联动，将日级别操作纳入周级别框架\n'
content = content.replace(old2, new2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('done')