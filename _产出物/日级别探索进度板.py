"""
生成日级别探索进度板，插入文档开头
"""
import re, os
from collections import OrderedDict

path = '_主文档/研究日级别探索路径.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')

# 按章节统计
current_section = '未分类'
sections = OrderedDict()
for line in lines:
    s = line.strip()
    # 检测 ## 标题
    m = re.match(r'^##\s+[一二三四五六七八九十]+[、.．]\s*(.+)$', s)
    if m:
        current_section = m.group(1).strip()
        if current_section not in sections:
            sections[current_section] = {'total': 0, 'done': 0}
        continue
    # 检测 - [ ] 和 - [x]
    if '- [ ]' in s or '- [x]' in s:
        if current_section not in sections:
            sections[current_section] = {'total': 0, 'done': 0}
        sections[current_section]['total'] += 1
        if '- [x]' in s:
            sections[current_section]['done'] += 1

# 章节名→显示名映射
SECTION_MAP = {
    '基本条件': '基本条件',
    '管中稳定': '管中稳定',
    '突破回踩': '突破回踩',
    '其他日机': '其他日机',
    '日警（风险预警）': '日警',
    '筛选日类机会': '筛选日类',
    '特殊形态汇总': '特殊形态',
    '向上突破 / 向下突破': '突破方向',
    '数据验证计划': '数据验证',
}

# 生成进度板
board_lines = []
board_lines.append('')
board_lines.append('| 探索路径 | 进度 | 完成 |')
board_lines.append('|:---------|:----:|:----:|')

total_items = 0
total_done = 0
for sec, data in sections.items():
    display = SECTION_MAP.get(sec, sec)
    total_items += data['total']
    total_done += data['done']
    if data['total'] == 0:
        continue
    pct = data['done'] / data['total'] * 100
    bar_len = 10
    filled = int(data['done'] / data['total'] * bar_len)
    bar = '█' * filled + '░' * (bar_len - filled)
    board_lines.append(f'| **{display}**（{data["total"]}项） | `[{bar}]` {pct:.0f}% | {data["done"]}/{data["total"]} |')

board_lines.append('')
pct = total_done / total_items * 100 if total_items > 0 else 0
board_lines.append(f'> **总计：** {total_items} 项探索子项，已完成 {total_done} 项（{pct:.0f}%）。{total_items - total_done} 项待探索。')
board_lines.append('')
board_lines.append(f'> 更新方式：勾选 `- [x]` 标记后，运行 `python _产出物/日级别探索进度板.py` 刷新此面板。')
board_lines.append('')

board = '\n'.join(board_lines)

# 移除旧的进度板（如果有的话）
old_start = None
old_end = None
for i, line in enumerate(lines):
    if '探索进度板' in line and i > 0 and i < 15:
        old_start = i
        # 找到面板结束位置
        for j in range(i, i+40):
            if j >= len(lines): break
            if '更新方式' in lines[j] or '更新此面板' in lines[j]:
                old_end = j + 1
                break
        break

if old_start and old_end:
    # 替换旧板
    new_lines = lines[:old_start] + [board] + lines[old_end:]
else:
    # 插入到文档开头：在第一个 --- 元数据分隔符之后
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.strip() == '---' and i > 0 and i < 10:
            insert_pos = i + 1
            break
    new_lines = lines[:insert_pos] + [board] + lines[insert_pos:]

new_content = '\n'.join(new_lines)
with open(path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print('进度板已更新')
print(f'统计: 共 {total_items} 项, {total_done} 已完成')
for sec, data in sections.items():
    if data['total'] > 0:
        print(f'  {SECTION_MAP.get(sec, sec)}: {data["done"]}/{data["total"]}')