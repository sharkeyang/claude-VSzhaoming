# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
with open(path, encoding='utf-8') as f:
    lines = f.read().split('\n')

# 定位
s3 = next(i for i,l in enumerate(lines) if l.startswith('### 8.3 '))
s841 = next(i for i,l in enumerate(lines) if l.startswith('**8.4.1 周类操作原则'))
s4 = next(i for i,l in enumerate(lines) if l.startswith('### 8.4 '))
s5 = next(i for i,l in enumerate(lines) if l.startswith('### 8.5 '))
print(f'8.3: {s3+1}-{s4}  8.4.1: {s841+1}  8.4: {s4+1}-{s5}')

# 1. 8.3 WXAB正交内容（保留）
sec83 = lines[s3:s841]  # L7314-7352
# 2. 8.3 混入的 8.4.x（移到 8.4）
sec84x = lines[s841:s4]  # L7353-7633
# 3. 8.4 原有内容
sec84 = lines[s4:s5]  # L7634-7849

# 重编号 8.3 的 8.4.x -> 8.4.1-8.4.6（保持）
# 重编号 8.4 原有的 8.4.1-8.4.5 -> 8.4.7-8.4.11
renum84 = {
    '#### 8.4.1 ': '#### 8.4.7 ',
    '#### 8.4.2 ': '#### 8.4.8 ',
    '#### 8.4.3 ': '#### 8.4.9 ',
    '#### 8.4.4 ': '#### 8.4.10 ',
    '#### 8.4.5 ': '#### 8.4.11 ',
}
new_sec84 = []
for l in sec84:
    for old, new in renum84.items():
        if l.startswith(old):
            l = l.replace(old, new)
            break
    new_sec84.append(l)

# 8.4 节 = 移入的 8.4.x + 原有内容
# 但 8.4 原有开头有 WXZC 择时 + EMA 数学原理（不是 8.4.x 标题），应保留在 8.4 开头
# 所以 8.4 节 = 原有开头(WXZC择时+EMA) + 移入的8.4.x + 原有8.4.7-8.4.11
# 但移入的 8.4.x 是主升前置，应放在主升条件之前
# 结构: 8.4标题 + WXZC择时+EMA(原有开头) + 移入8.4.1-8.4.6 + 原有8.4.7-8.4.11

# 新 8.4 节
new_84 = ['### 8.4 主升条件探索（原 8.1.5.1-8.1.5.5）']
# 原有开头（WXZC择时+EMA，即 sec84 中 8.4.1 之前的部分）
# sec84 开头是 '### 8.4' 标题 + WXZC择时 + EMA + 8.4.1-8.4.5
# 提取 sec84 中 8.4.1 之前的部分（WXZC择时+EMA）
s84_1 = next(i for i,l in enumerate(sec84) if l.startswith('#### 8.4.1 '))
sec84_head = sec84[1:s84_1]  # 去掉 '### 8.4' 标题，保留 WXZC择时+EMA
# 原有 8.4.1-8.4.5（重编号后 8.4.7-8.4.11）
sec84_body = new_sec84[s84_1:]

# 组装新 8.4
new_84 = ['### 8.4 主升条件探索（原 8.1.5.1-8.1.5.5）'] + sec84_head + [''] + sec84x + [''] + sec84_body

# 组装新文件
new_lines = lines[:s3] + sec83 + [''] + new_84 + lines[s5:]

with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
print('8.3/8.4 修复完成')
