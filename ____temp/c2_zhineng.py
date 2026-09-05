# -*- coding: utf-8 -*-
"""'级别' → '职能' 全面替换：两级别→两职能, 范围级别→范围职能, 等级级别→等级职能"""
import io

path = r'd:\@VSwork\VS昭明计划VBA优化\_主文档\MC3.3_C2日DXZC+DXAB全维度分析.md'
with io.open(path, encoding='utf-8') as f:
    content = f.read()

content = content.replace('两级别', '两职能')
content = content.replace('范围级别', '范围职能')
content = content.replace('等级级别', '等级职能')

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('替换完成')
