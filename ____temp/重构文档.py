# -*- coding: utf-8 -*-
"""文档重构：月基策略 + 日冲策略"""
import re

# ========== 读取两个文档 ==========
月基 = open('_主文档/MC3.1_研究月基策略.md', 'r', encoding='utf-8').read()
日冲 = open('_主文档/MC3.3_研究日冲策略.md', 'r', encoding='utf-8').read()

# ========== 提取日冲中需要移入月基的内容 ==========

# 1. 8格分类(月基带日核心) - 从日冲§3.0提取
# 定位 '### 3.0 三级别甲乙己/丙丁戊分类系统' 到 '### 3.1 基础概率验证'
m30_start = 日冲.find('### 3.0 三级别甲乙己/丙丁戊分类系统')
m31_start = 日冲.find('### 3.1 基础概率验证')
八格内容 = 日冲[m30_start:m31_start]

# 2. 216分支概率表 - 从日冲§3.1提取
m_end_small = 日冲.find('### 3.5 小样本分布规律')
m31_35 = 日冲[m31_start:m_end_small]

# 3. 规则验证 - 从日冲§3.8提取
m38_start = 日冲.find('### 3.8 四级别分类规则验证')
m39_start = 日冲.find('### 3.9 新旧变量预测能力对比')
m38 = 日冲[m38_start:m39_start]

# 4. 核心决策规则 + 月基映射 + 为什么G级 - 从日冲提取
m_rule_start = 日冲.find('### 核心决策规则')
m_new_start = 日冲.find('### 3.9 新旧变量')
核心规则 = 日冲[m_rule_start:m_new_start]

# ========== 写入月基文档 ==========
# 在第五章前插入 §4.5 月基带日 和 §5 数据支撑
marker = '## 第五章：VBA实施计划'

# 构造 §4.5 月基带日
s45 = '''
### 4.5 月基带日：日级别看盘工具

> 月基带日本质是"用日级别数据做月基分类"，将周级别的WXCD体系映射到日级别（DXAB→DXCD→DXEF三级带动）。即使按月持有，也要一天一天持续考察日级别指标。

''' + 八格内容

# 构造 §5 数据支撑
s5 = '''
## 第五章：数据支撑（216分支全量验证）

> 月基带日分类的底层数据支撑，日冲策略引用本章时以"短期冲高"视角展开。

### 5.1 216分支全量概率表

''' + m31_35 + '''

### 5.2 四级别分类规则验证

''' + m38 + '''

### 5.3 核心决策规则与月基四域映射

''' + 核心规则

# 插入
月基_new = 月基.replace(marker, s45 + '\n\n' + s5 + '\n\n' + marker)

# 删掉 §4.1 三变量联合决策（因为第四章改名为变量框架，§4.1可能过时，保留）
# 注：保留原内容，只改标题

open('_主文档/MC3.1_研究月基策略.md', 'w', encoding='utf-8').write(月基_new)

# ========== 写入日冲文档 ==========
# 移除已移入月基的内容
日冲_new = 日冲

# 删除 §2.1 DXEF-DXCD 日级别执行框架（8格分类）
s21_start = 日冲_new.find('### 2.1 DXEF-DXCD 日级别执行框架')
s2_end = 日冲_new.find('## 三、216分支深度分析')
if s21_start > 0 and s2_end > s21_start:
    日冲_new = 日冲_new[:s21_start] + 日冲_new[s2_end:]

# 删除 §3.0-3.8 (216分支+规则验证)
s3_start = 日冲_new.find('## 三、216分支深度分析')
s4_start = 日冲_new.find('## 四、按形态探索')
if s3_start > 0 and s4_start > s3_start:
    日冲_new = 日冲_new[:s3_start] + 日冲_new[s4_start:]

# 删除核心决策规则+月基映射（在§3.9前后）
rule_start = 日冲_new.find('### 核心决策规则')
if rule_start > 0:
    # 找到下一个 ## 或 ### 3.9
    rule_end = 日冲_new.find('\n### 3.9', rule_start)
    if rule_end > rule_start:
        日冲_new = 日冲_new[:rule_start] + 日冲_new[rule_end:]

open('_主文档/MC3.3_研究日冲策略.md', 'w', encoding='utf-8').write(日冲_new)

print('重构完成')
print(f'月基新大小: {len(月基_new)}')
print(f'日冲新大小: {len(日冲_new)}')