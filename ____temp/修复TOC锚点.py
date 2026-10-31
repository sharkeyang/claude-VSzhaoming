# -*- coding: utf-8 -*-
"""修复TOC锚点：#63→#62, #64→#63, #65→#64, #66→#65, #67→#66。用占位符避免冲突。"""
import io

path = r'_主文档\全局_D昭明操盘规则.md'
with io.open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 用占位符避免冲突
content = content.replace('#67', '#6X7')
content = content.replace('#66', '#6X6')
content = content.replace('#65', '#6X5')
content = content.replace('#64', '#6X4')
content = content.replace('#63', '#6X3')
# 占位符替换回目标
content = content.replace('#6X7', '#66')
content = content.replace('#6X6', '#65')
content = content.replace('#6X5', '#64')
content = content.replace('#6X4', '#63')
content = content.replace('#6X3', '#62')

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print('TOC锚点修复完成')