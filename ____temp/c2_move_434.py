# -*- coding: utf-8 -*-
"""优化3：把 4.3.4 执念范围探索 移到 4.3.5 初始介入 之后，
重编号为：4.3.3 基础范围 → 4.3.4 初始介入 → 4.3.5 执念范围(旁支)。
"""
import io

path = r'd:\@VSwork\VS昭明计划VBA优化\_主文档\MC3.3_C2日DXZC+DXAB全维度分析.md'
with io.open(path, encoding='utf-8') as f:
    content = f.read()

# 定位各锚点
m434 = content.find('#### 4.3.4 执念范围探索')
m435 = content.find('#### 4.3.5 初始介入条件')
m44  = content.find('### 4.4 第三阶段')
assert -1 not in (m434, m435, m44), '锚点定位失败'

# 剪切 执念范围块（从 4.3.4 标题 到 4.3.5 标题之前）
zhinian_block = content[m434:m435]
# 重命名：4.3.4 -> 4.3.5, 4.3.4.1 -> 4.3.5.1, 4.3.4.2 -> 4.3.5.2
zhinian_block = zhinian_block.replace('#### 4.3.4 执念范围探索', '#### 4.3.5 执念范围探索')
zhinian_block = zhinian_block.replace('#### 4.3.4.1', '#### 4.3.5.1')
zhinian_block = zhinian_block.replace('#### 4.3.4.2', '#### 4.3.5.2')

# 原 4.3.5 初始介入 重命名为 4.3.4（在删除执念块后的剩余内容中）
rest = content[:m434] + content[m435:]
rest = rest.replace('#### 4.3.5 初始介入条件', '#### 4.3.4 初始介入条件')

# 找到 rest 中 4.4 的位置，把执念块插到 4.4 之前（即 4.3.4 初始介入 之后）
m44_new = rest.find('### 4.4 第三阶段')
assert m44_new != -1, '新 4.4 定位失败'
new_content = rest[:m44_new] + zhinian_block + '\n' + rest[m44_new:]

with io.open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('优化3完成：执念范围已移到初始介入之后，重编号为4.3.5')
