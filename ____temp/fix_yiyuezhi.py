# -*- coding: utf-8 -*-
"""整理一页纸章节编号"""
with open('_主文档/MC3.3.0_日级别DXZC×DXAB护型总结一页纸.md', 'rb') as f:
    data = f.read()

# 替换章节编号
# 一、二 保持不变（它们是##级别）
# ### 4.x -> ### 1.x
# ### 5.x -> ### 2.x
# 2.6.2 -> 1.2
# 2.6.3 -> 1.3

data = data.replace(b'### 4.1', b'### 1.1')
data = data.replace(b'### 4.2', b'### 1.2')
data = data.replace(b'### 4.3', b'### 1.3')
data = data.replace(b'### 4.4', b'### 1.4')
data = data.replace(b'### 5.1', b'### 2.1')
data = data.replace(b'### 5.2', b'### 2.2')
data = data.replace(b'### 5.3', b'### 2.3')
data = data.replace(b'### 5.4', b'### 2.4')
data = data.replace(b'### 5.5', b'### 2.5')
data = data.replace(b'### 5.6', b'### 2.6')
data = data.replace(b'### 5.7', b'### 2.7')

# 2.6.2 -> 1.2, 2.6.3 -> 1.3
data = data.replace(b'### 2.6.2', b'### 1.2')
data = data.replace(b'### 2.6.3', b'### 1.3')

# 子节编号
data = data.replace(b'#### 2.6.1.1', b'#### 1.1.1')
data = data.replace(b'#### 2.6.1.2', b'#### 1.1.2')
data = data.replace(b'#### 2.6.1.3', b'#### 1.1.3')
data = data.replace(b'#### 2.6.1.4', b'#### 1.1.4')
data = data.replace(b'#### 2.6.1.5', b'#### 1.1.5')
data = data.replace(b'#### 2.6.1.6', b'#### 1.1.6')
data = data.replace(b'#### 2.6.1.7', b'#### 1.1.7')

# DXZC>0时 / DXZC≤0时 的子标题
data = data.replace(b'#### DXZC>0\xe6\x97\xb6', b'#### 1.3.1 DXZC>0\xe6\x97\xb6')
data = data.replace(b'#### DXZC\xe2\x89\xa40\xe6\x97\xb6', b'#### 1.3.2 DXZC\xe2\x89\xa40\xe6\x97\xb6')

with open('_主文档/MC3.3.0_日级别DXZC×DXAB护型总结一页纸.md', 'wb') as f:
    f.write(data)

print('整理完成')