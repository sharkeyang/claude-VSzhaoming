# -*- coding: utf-8 -*-
"""交换6.5和6.6：原6.5(J漏)→6.6(N漏)，原6.6(K漏)→6.5(M漏)。用占位符避免冲突。"""
import io

path = r'_主文档\全局_D昭明操盘规则.md'
with io.open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 第一步：用占位符标记
# 原6.5(J漏) → 6X5，原6.6(K漏) → 6X6
content = content.replace('### 6.5 方法日J漏', '### 6X5 方法日J漏')
content = content.replace('#### 6.5.1 特征概览', '#### 6X5.1 特征概览')
content = content.replace('#### 6.5.2 完整操作流程', '#### 6X5.2 完整操作流程')
content = content.replace('#### 6.5.3 期望收益', '#### 6X5.3 期望收益')
content = content.replace('### 6.6 方法日K漏', '### 6X6 方法日K漏')

# 第二步：占位符替换为目标编号
# 原6.5(J漏) → 6.6(N漏)
content = content.replace('### 6X5 方法日J漏', '### 6.6 方法日N漏')
content = content.replace('#### 6X5.1 特征概览', '#### 6.6.1 特征概览')
content = content.replace('#### 6X5.2 完整操作流程', '#### 6.6.2 完整操作流程')
content = content.replace('#### 6X5.3 期望收益', '#### 6.6.3 期望收益')
# 原6.6(K漏) → 6.5(M漏)
content = content.replace('### 6X6 方法日K漏', '### 6.5 方法日M漏')

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('交换完成')