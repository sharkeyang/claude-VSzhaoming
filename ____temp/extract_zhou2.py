# -*- coding: utf-8 -*-
"""制作周级别一页纸"""
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# 从MC3.1中提取第三章的关键数据
with open('_主文档/MC3.1_研究月基策略.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 提取护型排序表
ch3 = content[content.find('## 3.2 核心验证结果'):]
sort_section = ch3[ch3.find('WXZC>0 排序'):ch3.find('### 2.1.2')]
print(sort_section[:800])