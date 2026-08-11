# -*- coding: utf-8 -*-
"""MC3.1 章节重构：方案A — 月基带日独立成章 §5"""
import re

path = '_主文档/MC3.1_研究月基策略.md'
content = open(path, encoding='utf-8').read()

# ===== Step 1: 4.5 月基带日 → §5 主标题 =====
content = content.replace(
    '### 4.5 月基带日：日级别看盘工具\n\n> 月基带日本质是"用日级别数据做月基分类"，将周级别的WXCD体系映射到日级别（DXAB→DXCD→DXEF三级带动）。即使按月持有，也要一天一天持续考察日级别指标。',
    '## 第五章：月基带日（日级别看盘工具）\n\n> 月基带日本质是"用日级别数据做月基分类"，将周级别的WXCD体系映射到日级别（DXAB→DXCD→DXEF三级带动）。即使按月持有，也要一天一天持续考察日级别指标。'
)

# ===== Step 2: 4.5.1 → 5.1 =====
content = content.replace(
    '### 4.5.1 三级别甲乙己/丙丁戊分类系统（前置于分析）',
    '### 5.1 三级别甲乙己/丙丁戊分类系统（前置于分析）'
)

# ===== Step 3: 3.0.1 → 5.2 =====
content = content.replace(
    '#### 3.0.1 核心机制：趋势长度决定收益，而非单日概率',
    '### 5.2 核心机制：趋势长度决定收益，而非单日概率'
)

# ===== Step 4: 删除旧 §5 标题 + 引言 =====
content = content.replace(
    '## 第五章：数据支撑（216分支全量验证）\n\n> 月基带日分类的底层数据支撑，日冲策略引用本章时以"短期冲高"视角展开。\n\n',
    ''
)

# ===== Step 5: 5.1.x → 5.3.x, 3.x.x → 5.3.x  =====
content = content.replace('### 5.1 216分支全量概率表', '### 5.3 216分支全量概率表')
content = content.replace('### 5.1.1 基础概率验证', '### 5.3.1 基础概率验证')
content = content.replace('#### 3.1.1 完整216分支概率表', '#### 5.3.2 完整216分支概率表')
content = content.replace('#### 3.1.2 市板差异分析', '#### 5.3.3 市板差异分析')
content = content.replace('### 5.1.2 ZE阈值分析：主升区 vs 震荡区', '### 5.3.4 ZE阈值分析：主升区 vs 震荡区')
content = content.replace('#### 3.2.1 核心问题', '#### 5.3.4.1 核心问题')
content = content.replace('#### 3.2.2 分析方法', '#### 5.3.4.2 分析方法')
content = content.replace('#### 3.2.3 对比结果（全量7462只股票）', '#### 5.3.4.3 对比结果（全量7462只股票）')
content = content.replace('#### 3.2.4 结论', '#### 5.3.4.4 结论')
content = content.replace('### 5.1.3 216分支当前状态分类', '### 5.3.5 216分支当前状态分类')
content = content.replace('#### 3.3.1 分类依据', '#### 5.3.5.1 分类依据')
content = content.replace('#### 3.3.2 分类结果', '#### 5.3.5.2 分类结果')
content = content.replace('#### 3.3.3 中间态不能合并的验证', '#### 5.3.5.3 中间态不能合并的验证')
content = content.replace('#### 3.3.4 日冲筛选的硬条件', '#### 5.3.5.4 日冲筛选的硬条件')
content = content.replace('### 5.1.4 DSHR>1 梯度分布规律', '### 5.3.6 DSHR>1 梯度分布规律')
content = content.replace('#### 3.4.1 核心发现', '#### 5.3.6.1 核心发现')
content = content.replace('#### 3.4.3 发现', '#### 5.3.6.3 发现')

# ===== Step 6: 5.2.x → 5.4.x =====
content = content.replace('### 5.2 四级别分类规则验证', '### 5.4 四级别分类规则验证')
content = content.replace('### 5.2.1 四级别分类规则验证', '### 5.4.1 四级别分类规则验证')
content = content.replace('#### 3.8.1 规则①：DXEF=嘘尿屎 + DXCD=下忠忑 + DXAB=丙丁戊 → 绝对禁止？', '#### 5.4.1.1 规则①：DXEF=嘘尿屎 + DXCD=下忠忑 + DXAB=丙丁戊 → 绝对禁止？')
content = content.replace('#### 3.8.2 规则②：DXEF=嘘尿屎 + DXCD=下忠忑 + DXAB=甲乙己 → 可尝试？', '#### 5.4.1.2 规则②：DXEF=嘘尿屎 + DXCD=下忠忑 + DXAB=甲乙己 → 可尝试？')
content = content.replace('#### 3.8.3 规则③：DXEF=嘘尿屎 + DXCD=上忠忐 + 不限DXAB → 可参与？', '#### 5.4.1.3 规则③：DXEF=嘘尿屎 + DXCD=上忠忐 + 不限DXAB → 可参与？')
content = content.replace('#### 3.8.4 规则④（镜面对称）：DXEF=金银唏 + DXCD=上忠忐 + DXAB=甲乙己 → 优先？', '#### 5.4.1.4 规则④（镜面对称）：DXEF=金银唏 + DXCD=上忠忐 + DXAB=甲乙己 → 优先？')
content = content.replace('#### 3.8.5 四条规则总结与完整操作列表', '#### 5.4.1.5 四条规则总结与完整操作列表')

# ===== Step 7: 核心决策规则 → 5.5 =====
content = content.replace(
    '### 核心决策规则（WXZC × WXAB）',
    '### 5.5 核心决策规则与月基四域映射\n### 5.5.1 核心决策规则（WXZC × WXAB）'
)
content = content.replace('### 月基四域 ←→ 日冲五层 映射', '### 5.5.2 月基四域 ←→ 日冲五层 映射')
content = content.replace('### ⚠️ 为什么G级需要单独处理为"傻吃屎豆"', '### 5.5.3 ⚠️ 为什么G级需要单独处理为"傻吃屎豆"')

# ===== Step 8: 删除僵尸 ### 5.3 标题（在 §5.5.3 和 §6 之间） =====
content = content.replace('\n### 5.3 核心决策规则与月基四域映射\n\n## 第六章：VBA实施计划', '\n\n## 第六章：VBA实施计划')

# ===== Write =====
open(path, 'w', encoding='utf-8').write(content)
print('MC3.1 重构完成')