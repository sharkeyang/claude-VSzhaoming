# -*- coding: utf-8 -*-
"""优化2：把 4.3.1 的 ④⑤⑥(两段式综合建议+结论+融合验证) 移到 4.3.2 开头，
让 4.3.1 专注"三尝试演进+关键洞察"(①误区+②三尝试+③洞察)。
"""
import io

path = r'd:\@VSwork\VS昭明计划VBA优化\_主文档\MC3.3_C2日DXZC+DXAB全维度分析.md'
with io.open(path, encoding='utf-8') as f:
    lines = f.readlines()

def find_line(anchor, start=0):
    for i in range(start, len(lines)):
        if anchor in lines[i]:
            return i
    return -1

# 定位 ④ 开始
start_4 = find_line('**④ 综合建议：两段式')
assert start_4 != -1, '未找到 ④'
# 定位 4.3.2 标题
ch432 = find_line('#### 4.3.2 四维参数分工表')
assert ch432 != -1, '未找到 4.3.2'
# 4.3.2 标题下一行(其正文从下一行开始)
# 块 = 从 ④ 到 4.3.2 标题之前的所有行
block = lines[start_4:ch432]   # 含 ④⑤⑥ 及 4.3.2 前的空行

# 从原位置删除块(保留 4.3.2 标题)
del lines[start_4:ch432]

# 在 4.3.2 标题行后插入块，作为其开头
# 重新定位 4.3.2(行号已变)
ch432_new = find_line('#### 4.3.2 四维参数分工表')
assert ch432_new != -1, '未找到新的 4.3.2'
# 找到 4.3.2 标题后的空行/正文起点，插入块
insert_at = ch432_new + 1
# 跳过后面的空行
while insert_at < len(lines) and lines[insert_at].strip() == '':
    insert_at += 1
# 在 4.3.2 标题与正文之间插入块(块前面加空行)
new_block = ['\n'] + block
lines[insert_at:insert_at] = new_block

with io.open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('优化2完成：④⑤⑥已移到4.3.2开头')
