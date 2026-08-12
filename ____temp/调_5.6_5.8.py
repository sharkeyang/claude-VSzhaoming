# -*- coding: utf-8 -*-
"""调整：§5.6并入§5.5，删5.8.3/5.8.4，重编号"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
path = '_主文档/MC3.1_研究月基策略.md'
text = open(path, encoding='utf-8').read()

# 找边界
s55_start = text.find('### 5.5 日类操作规则的数据验证')   # §5.5 开始
s56_start = text.find('### 5.6 核心决策规则与月基四域映射') # §5.6 开始
s57_start = text.find('### 5.7 综合结论')                  # §5.7 开始
s58_start = text.find('### 5.8 新旧变量预测能力对比')       # §5.8 开始
s59_start = text.find('### 5.9 技术细节')                  # §5.9 开始

# ===== 步骤1：提取 §5.6 内容，重编号，插入 §5.5 =====
s56_block = text[s56_start:s57_start]
s56_block = s56_block.replace('### 5.6 核心决策规则与月基四域映射\n\n', '')
s56_block = s56_block.replace('#### 5.6.1 核心决策规则（WXZC × WXAB）', '#### 5.5.2 核心决策规则（WXZC × WXAB）')
s56_block = s56_block.replace('#### 5.6.2 月基四域 ←→ 带日五层 映射', '#### 5.5.3 月基四域 ←→ 带日五层 映射')
s56_block = s56_block.replace('#### 5.6.3 ⚠️ 为什么G级需要单独处理为"傻吃屎豆"', '#### 5.5.4 ⚠️ 为什么G级需要单独处理为"傻吃屎豆"')

# 重组：§5.5开头 + §5.6内容(重编号) + §5.7开始
text = text[:s56_start] + s56_block + text[s57_start:]

# ===== 步骤2：删除 §5.8.3 和 §5.8.4 =====
# 重新找边界（内容变了）
s583 = text.find('#### 5.8.3 位谕of日层联动 — 20级DJE走势等级详解')
s585 = text.find('#### 5.8.5 待验证事项')
text = text[:s583] + text[s585:]
text = text.replace('#### 5.8.5 待验证事项', '#### 5.8.3 待验证事项')

# ===== 步骤3：重编号 5.9→5.8, 5.8→5.7, 5.7→5.6（从高到低） =====
# 5.9 → 5.8
text = text.replace('### 5.9 技术细节', '### 5.8 技术细节')
text = text.replace('#### 5.9.1 列映射', '#### 5.8.1 列映射')
text = text.replace('#### 5.9.2 概率列定义', '#### 5.8.2 概率列定义')
# 5.8 → 5.7
text = text.replace('### 5.8 新旧变量预测能力对比', '### 5.7 新旧变量预测能力对比')
text = text.replace('#### 5.8.1 对比结果', '#### 5.7.1 对比结果')
text = text.replace('#### 5.8.2 位谕of日层联动 — 变量与等级总览', '#### 5.7.2 位谕of日层联动 — 变量与等级总览')
text = text.replace('#### 5.8.3 待验证事项', '#### 5.7.3 待验证事项')
# 5.7 → 5.6
text = text.replace('### 5.7 综合结论', '### 5.6 综合结论')
text = text.replace('#### 5.7.1 框架有效性', '#### 5.6.1 框架有效性')
text = text.replace('#### 5.7.2 操作条件', '#### 5.6.2 操作条件')
text = text.replace('#### 5.7.3 筛选条件', '#### 5.6.3 筛选条件')
text = text.replace('#### 5.7.4 冲高条件', '#### 5.6.4 冲高条件')
text = text.replace('#### 5.7.5 数据可靠性', '#### 5.6.5 数据可靠性')
text = text.replace('#### 5.7.6 下日冲高概率结论', '#### 5.6.6 下日冲高概率结论')

open(path, 'w', encoding='utf-8').write(text)
print('完成')

# 验证
print('\n=== §5 完整结构 ===')
for line in text.split('\n'):
    if re.match(r'^### 5\.|^#### 5\.5', line):
        print(line)
PYEOF