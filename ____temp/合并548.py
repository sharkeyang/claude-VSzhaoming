# -*- coding: utf-8 -*-
import re
f = '_主文档/MC3.3_C6研究日类微观形态.md'
lines = open(f, encoding='utf-8').read().split('\n')

# 定位标题行
i54 = next(i for i,l in enumerate(lines) if re.match(r'^### 5\.4 ', l))
i58 = next(i for i,l in enumerate(lines) if re.match(r'^### 5\.8 ', l))
i581 = next(i for i,l in enumerate(lines) if re.match(r'^#### 5\.8\.1 ', l))
i582 = next(i for i,l in enumerate(lines) if re.match(r'^#### 5\.8\.2 ', l))
i583 = next(i for i,l in enumerate(lines) if re.match(r'^#### 5\.8\.3 ', l))
i510 = next(i for i,l in enumerate(lines) if re.match(r'^### 5\.10 ', l))

# 1. 改 5.4 标题
lines[i54] = '### 5.4 触顶信号体系（高波池全量）'

# 2. 在 5.4 内容前插入 5.4.1 标题
# 5.4 内容从 i54+1 开始（主题说明），在主题说明后插入 5.4.1 标题
# 找到 5.4 主题说明结束（第一个空行后的 "> **目的" 之前）
# 实际：5.4 标题后是主题说明（L258），然后空行，然后 "> **目的"（L262）
# 在 "> **目的" 前插入 5.4.1 标题
insert_pos = None
for j in range(i54+1, i58):
    if lines[j].startswith('> **目的'):
        insert_pos = j
        break
if insert_pos is not None:
    # 在 insert_pos 前插入 5.4.1 标题 + 空行
    lines.insert(insert_pos, '#### 5.4.1 触顶信号的高波池全量验证')
    lines.insert(insert_pos+1, '')
    # 因为插入了2行，后续行号偏移
    i58 += 2
    i581 += 2
    i582 += 2
    i583 += 2
    i510 += 2

# 3. 改 5.8 标题为 5.4.2
lines[i58] = '#### 5.4.2 触顶信号的失败情形与最强增强'

# 4. 改 5.8.1/5.8.2/5.8.3 为 5.4.2.1/5.4.2.2/5.4.2.3
lines[i581] = '##### 5.4.2.1 失败情形：长上影/阴柱/十字星'
lines[i582] = '##### 5.4.2.2 十字星最强增强联合验证'
lines[i583] = '##### 5.4.2.3 冲顶星 VBA 落地'

open(f, 'w', encoding='utf-8').write('\n'.join(lines))
print('合并完成')
print(f'5.4标题: {lines[i54]}')
print(f'5.4.1标题: {lines[insert_pos]}')
print(f'5.4.2标题: {lines[i58]}')
print(f'5.4.2.1标题: {lines[i581]}')
print(f'5.4.2.2标题: {lines[i582]}')
print(f'5.4.2.3标题: {lines[i583]}')
