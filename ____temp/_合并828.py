# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
with open(path, encoding='utf-8') as f:
    lines = f.read().split('\n')

# 定位
s2 = next(i for i,l in enumerate(lines) if l.startswith('### 8.2 '))
s3 = next(i for i,l in enumerate(lines) if l.startswith('### 8.3 '))
s8 = next(i for i,l in enumerate(lines) if l.startswith('### 8.8 '))
s9 = next(i for i,l in enumerate(lines) if l.startswith('### 8.9 '))
print(f'8.2: {s2+1}-{s3}  8.8: {s8+1}-{s9}')

# 8.8 内容（去掉标题行，保留子节）
sec88 = lines[s8+1:s9]  # 去掉 '### 8.8' 标题行
# 8.8 的子节标题改为 8.2.x
import re
new_sec88 = []
for l in sec88:
    if l.startswith('#### 8.8.'):
        # 8.8.1 -> 8.2.6, 8.8.2 -> 8.2.7 等（8.2 已有 8.2.1-8.2.5）
        m = re.match(r'#### 8\.8\.(\d+)', l)
        if m:
            n = int(m.group(1)) + 5  # 8.2 已有 5 个子节
            l = l.replace(f'#### 8.8.{m.group(1)}', f'#### 8.2.{n}')
    new_sec88.append(l)

# 在 8.2 末尾（s3 前）插入 8.8 内容
# 8.2 末尾是 </td></tr></table> 或 --- 分隔
# 找到 8.2 末尾的 '---' 分隔符（s3 前最后一个）
insert_at = s3
# 在 8.2 末尾插入一个分隔 + 8.8 内容
merged = lines[:insert_at] + ['', '---', ''] + new_sec88 + lines[s9:]

# 更新 8.2 标题
merged[s2] = '### 8.2 周类护型转移矩阵与马尔可夫链分析（2026-09-26 全量验证，2026-10-17 合并 8.8）'

with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(merged))
print('合并完成')
