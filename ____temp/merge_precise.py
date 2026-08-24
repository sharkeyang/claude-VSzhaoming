# -*- coding: utf-8 -*-
"""
精确合并MC3.2.1到MC3.1
1. 读取2f496f9版本的MC3.1（从git）
2. 读取MC3.2.1
3. 将MC3.2.1插入为第三章
4. 原第三章~第五章顺延为第四章~第六章
5. 更新所有章节编号
"""
import re

# 读取2f496f9版本的MC3.1
with open('____temp/mc31_2f496f9.md', 'r', encoding='utf-8') as f:
    mc31 = f.read()

# 读取MC3.2.1
with open('_主文档/MC3.2.1_研究周策略WXAB.md', 'r', encoding='utf-8') as f:
    mc321 = f.read()

# 1. 找到原第三章~第五章
ch3_start = mc31.find('## 第三章：月基策略操作规则')
ch4_start = mc31.find('## 第四章：月基策略变量框架')
ch5_start = mc31.find('## 第五章：月基带日')

# 提取原第三章~第五章
old_ch3 = mc31[ch3_start:ch4_start]
old_ch4 = mc31[ch4_start:ch5_start]
old_ch5 = mc31[ch5_start:]

# 2. 提取MC3.2.1正文（去掉目录）
mc321_body = mc321
if mc321_body.startswith('## 目录'):
    toc_end = mc321_body.find('\n---\n', 10)
    if toc_end > 0:
        mc321_body = mc321_body[toc_end+5:]

# 3. MC3.2.1的2.x改为3.x
for old_n, new_n in [('2.0','3.1'),('2.1','3.2'),('2.2','3.3'),('2.3','3.4'),('2.4','3.5'),('2.5','3.6'),('2.6','3.7')]:
    mc321_body = mc321_body.replace(f'## {old_n}', f'## {new_n}')
    mc321_body = mc321_body.replace(f'### {old_n}', f'### {new_n}')
    mc321_body = mc321_body.replace(f'#### {old_n}', f'#### {new_n}')

mc321_body = mc321_body.replace('#### 2.6.1.1', '#### 3.7.1.1')
mc321_body = mc321_body.replace('#### 2.6.1.2', '#### 3.7.1.2')
mc321_body = mc321_body.replace('#### 2.6.1.3', '#### 3.7.1.3')
mc321_body = mc321_body.replace('#### 2.6.1.4', '#### 3.7.1.4')
mc321_body = mc321_body.replace('#### 2.6.1.5', '#### 3.7.1.5')
mc321_body = mc321_body.replace('#### 2.6.1.6', '#### 3.7.1.6')
mc321_body = mc321_body.replace('#### 2.6.1.7', '#### 3.7.1.7')

# 4. 原第三章改为第四章（3.x -> 4.x）
old_ch3 = old_ch3.replace('## 第三章：月基策略操作规则', '## 第四章：月基策略操作规则')
old_ch3 = old_ch3.replace('### 3.', '### 4.')

# 5. 原第四章改为第五章（4.x -> 5.x）
old_ch4 = old_ch4.replace('## 第四章：月基策略变量框架', '## 第五章：月基策略变量框架')
old_ch4 = old_ch4.replace('### 4.', '### 5.')

# 6. 原第五章改为第六章（5.x -> 6.x）
old_ch5 = old_ch5.replace('## 第五章：月基带日', '## 第六章：月基带日')
old_ch5 = old_ch5.replace('### 5.', '### 6.')

# 7. 构建新文档
new_mc31 = mc31[:ch3_start]
new_mc31 += '## 第三章 周级别WXZC+WXAB全维度分析\n\n'
new_mc31 += mc321_body
new_mc31 += '\n\n---\n\n'
new_mc31 += old_ch3
new_mc31 += '\n\n---\n\n'
new_mc31 += old_ch4
new_mc31 += '\n\n---\n\n'
new_mc31 += old_ch5

# 8. 写入
with open('_主文档/MC3.1_研究月基策略.md', 'w', encoding='utf-8') as f:
    f.write(new_mc31)

print('合并完成')
print(f'新文档长度: {len(new_mc31)} 字符')

# 验证
for ch in ['第三章', '第四章', '第五章', '第六章']:
    if ch in new_mc31:
        print(f'  {ch} OK')
    else:
        print(f'  {ch} MISSING!')
for i in range(1, 6):
    if f'### 4.{i}' in new_mc31:
        print(f'  ### 4.{i} OK')
    else:
        print(f'  ### 4.{i} MISSING!')