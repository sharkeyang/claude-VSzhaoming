# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
with open(path, encoding='utf-8') as f:
    lines = f.read().split('\n')

# 定位
s8 = next(i for i,l in enumerate(lines) if l.startswith('#### 8.9.8 '))   # 操作规则开始
s10 = next(i for i,l in enumerate(lines) if l.startswith('### 8.10 '))    # 最小阻力动向开始
s9 = next(i for i,l in enumerate(lines) if l.startswith('### 8.9 '))      # 8.9 开始
print(f'8.9.8: {s8+1}  8.10: {s10+1}  8.9: {s9+1}')

# 提取 8.9.8-8.9.11.1 内容（s8 到 s10 前）
sec = lines[s8:s10]
# 重编号 8.9.8->8.10.1, 8.9.9->8.10.2, 8.9.10->8.10.3, 8.9.11->8.10.4, 8.9.11.1->8.10.5
renum = {
    '#### 8.9.8 ': '#### 8.10.1 ',
    '#### 8.9.9 ': '#### 8.10.2 ',
    '#### 8.9.10 ': '#### 8.10.3 ',
    '#### 8.9.11 ': '#### 8.10.4 ',
    '#### 8.9.11.1 ': '#### 8.10.5 ',
}
new_sec = []
for l in sec:
    for old, new in renum.items():
        if l.startswith(old):
            l = l.replace(old, new)
            break
    new_sec.append(l)

# 新操作规则节标题
op_title = '### 8.10 🎯 周类操作规则（2026-10-12 用户定稿，2026-10-17 从 8.9 独立）'

# 原 8.10 最小阻力动向 -> 8.11
new_lines = []
for i, l in enumerate(lines):
    if i == s10:
        new_lines.append('### 8.11 🎯 最小阻力动向理论（2026-10-17 用户理论，全量 236.3 万行验证）')
    elif s8 <= i < s10:
        continue  # 跳过 8.9.8-8.9.11.1（已移出）
    else:
        new_lines.append(l)

# 在 8.9 之后插入操作规则节
# 找到 8.9 的结尾（8.9.7 之后、原 8.9.8 之前）
# 新结构: ...8.9.7... | 8.10操作规则 | 8.11最小阻力动向
# 在 s8 位置插入操作规则节（s8 现在是 8.11 的位置之前）
insert_at = s8
new_lines = new_lines[:insert_at] + [op_title, ''] + new_sec + new_lines[insert_at:]

with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
print('移动完成')
