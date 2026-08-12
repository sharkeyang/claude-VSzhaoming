# -*- coding: utf-8 -*-
"""移动3.4.5到四章，移动进度表到五章"""
with open('_主文档/MC3.3.4_研究日冲策略探索形态.md', 'r', encoding='utf-8') as f:
    content = f.read()

# ========== 任务1: 3.4.5 日周结合 → 移到四章开头 ==========
start_345 = content.find('### 3.4.5 日周结合：先周后日操作框架')
end_345 = content.find('## 四、日周联动（周', start_345)
if start_345 == -1 or end_345 == -1:
    print('3.4.5 定位失败')
else:
    section_345 = content[start_345:end_345]
    # 从原文删除
    content = content[:start_345] + content[end_345:]
    # 插入到四章开头
    insert_point = content.find('## 四、日周联动（周←→日映射）')
    insert_point = content.find('\n', insert_point) + 1  # 标题后换行
    # 重新编号
    new_section = section_345.replace('### 3.4.5', '### 4.0')
    content = content[:insert_point] + '\n' + new_section + '\n' + content[insert_point:]
    print('3.4.5 已移到四章开头')

# ========== 任务2: 探索进度表 → 移到五章，只保留探索路径一~七 ==========
# 进度表范围：从 "| 探索路径" 到 "更新方式" 行
start_tbl = content.find('| 探索路径 | 进度 | 完成 |')
end_tbl = content.find('更新方式：探索子项勾选', start_tbl)
end_tbl = content.find('\n', end_tbl) + 1  # 包含该行换行

if start_tbl == -1 or end_tbl == -1:
    print('进度表定位失败')
else:
    # 提取探索路径一~七的行
    lines = content[start_tbl:end_tbl].split('\n')
    kept = []
    for line in lines:
        if '探索路径' in line and '探索路径' not in line[:2]:
            # 表头行
            kept.append(line)
        elif '探索路径一' in line or '探索路径二' in line or '探索路径三' in line \
          or '探索路径四' in line or '探索路径五' in line or '探索路径六' in line \
          or '探索路径七' in line:
            kept.append(line)
    # 加入探索总计和更新方式
    kept.append('')
    kept.append('> **探索总计：** 44项探索子项，0项已完成。')
    kept.append('> 更新方式：探索子项勾选 `- [x]` 标记后，运行 `python _产出物/日级别探索进度板.py` 刷新此面板。')

    new_tbl = '\n'.join(kept) + '\n\n'

    # 从原文删除原进度表
    content = content[:start_tbl] + content[end_tbl:]

    # 插入到五章开头
    insert_5 = content.find('## 五、按形态探索')
    insert_5 = content.find('\n', insert_5) + 1

    content = content[:insert_5] + '\n' + new_tbl + content[insert_5:]
    print('进度表已移到五章')

with open('_主文档/MC3.3.4_研究日冲策略探索形态.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('完成')