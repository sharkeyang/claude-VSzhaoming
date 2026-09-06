# -*- coding: utf-8 -*-
"""6.3 章节合并：6.3.3+6.3.4+6.3.7->等高线的特性；6.3.5+6.3.6->等高线的作用"""
import sys, re
sys.stdout.reconfigure(encoding='utf-8')
path = '_主文档/MC3.3_C6研究日类微观形态.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 标题映射（按行内容精确替换）
repl = {
    '#### 6.3.3 分类分布（6等）': '#### 6.3.3 等高线的特性\n\n##### 6.3.3.1 分类分布（6等）',
    '#### 6.3.4 下日冲高≥0% ~ ≥5% 逐层对比（6等，高波池全量）': '##### 6.3.3.2 下日冲高≥0% ~ ≥5% 逐层对比（6等，高波池全量）',
    '#### 6.3.5 等高线不预测方向（核心发现）': '#### 6.3.4 等高线的作用\n\n##### 6.3.4.1 不预测方向（核心发现）',
    '#### 6.3.6 等高线预测什么？': '##### 6.3.4.2 预测什么？',
    '#### 6.3.7 等2/等6 回归确认性质（下柱DTZA方向）': '##### 6.3.3.3 等2/等6 回归确认性质（下柱DTZA方向）',
}

out = []
for line in lines:
    s = line.rstrip('\n')
    if s in repl:
        out.append(repl[s] + '\n')
    else:
        out.append(line)

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(out)
print('完成')
