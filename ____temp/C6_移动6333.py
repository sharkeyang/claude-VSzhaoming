# -*- coding: utf-8 -*-
"""把6.3.3.3等2/等6回归确认性质从6.3.4之后移动到6.3.3.2之后"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = '_主文档/MC3.3_C6研究日类微观形态.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 定位6.3.3.3标题行
start = None
for i, l in enumerate(lines):
    if '##### 6.3.3.3 等2/等6 回归确认性质' in l:
        start = i
        break
assert start is not None, '未找到6.3.3.3'

# 找到6.3.3.3结束（下一个###或####或#####标题，或---分隔）
end = start + 1
while end < len(lines):
    if lines[end].startswith('### ') or lines[end].startswith('#### ') or lines[end].startswith('##### '):
        break
    end += 1
# 去掉末尾空行
while end > start and lines[end-1].strip() == '':
    end -= 1

block = lines[start:end]
print(f'6.3.3.3内容: 行{start+1}-{end}, 共{len(block)}行')
print('首行:', block[0].strip())
print('末行:', block[-1].strip())

# 从原位置删除
del lines[start:end]

# 定位6.3.3.2结论之后（6.3.4标题之前）插入
# 找6.3.4标题行
for i, l in enumerate(lines):
    if '#### 6.3.4 等高线的作用' in l:
        insert_at = i
        break
print(f'插入位置: 行{insert_at+1}前')

# 插入
lines[insert_at:insert_at] = block + ['\n']

with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('移动完成')
