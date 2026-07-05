with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Remove blank line before "重大待解决疑惑"
c = c.replace('```\n\n**重大待解决疑惑：**', '```\n**重大待解决疑惑：**')

# 2. Change 周级别浮仓机会 -> <周浮仓>机会
c = c.replace('周级别浮仓机会', '<周浮仓>机会')

# 3. Wrap specified fenced code blocks with <table border>
# Define sections to wrap: (start_marker, end_marker_or_condition)
# We need to find the fenced code blocks near these markers

sections = [
    # 持仓决策树
    ('**持仓决策树（2026-06-30重构：四区划 + 仓系统）：**', None),
    # 选股流程
    ('**选股流程（三种操作模式）：**', None),
    # 选股引擎结构
    ('**选股引擎结构：**', None),
    # 2.3.5 系统化评估流程
    ('#### 2.3.5 系统化评估流程（板块/期货通用）', None),
    # 系统化评估流程 (M9)
    ('**系统化评估流程：**', None),
    # 操盘计划模板
    ('**操盘计划模板：**', None),
    # 期货品种分类
    ('期货品种分类：', '轮动模式复制'),
    # 轮动模式复制
    ('轮动模式复制：', '预测输出'),
    # 3. 对VBA代码的影响
    ('**3. 对VBA代码的影响**', None),
]

import re

# Strategy: Find fenced code blocks that are near these markers, wrap them
# A fenced code block starts with ``` and ends with ```
# We need to find the ``` after each marker, then find its closing ```

lines = c.split('\n')
modified = list(lines)

for i, line in enumerate(lines):
    # Check if this line contains one of our marker sections
    for marker, _ in sections:
        if marker in line:
            # Find the next ``````
            code_start = None
            for j in range(i, min(i + 30, len(lines))):
                if lines[j].strip().startswith('```') or lines[j].strip().startswith('~~~'):
                    code_start = j
                    break
            if code_start is None:
                continue

            # Find the closing ```
            code_content = []
            k = code_start + 1
            while k < len(lines):
                if lines[k].strip() == '```' or lines[k].strip() == '~~~':
                    break
                code_content.append(lines[k])
                k += 1

            if k >= len(lines):
                continue  # no closing fence found

            # Create wrapped version
            wrapped = []
            wrapped.append('<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">')
            wrapped.append('<tr><td>')
            wrapped.append('')
            wrapped.append('```')
            for content_line in code_content:
                wrapped.append(content_line)
            wrapped.append('```')
            wrapped.append('')
            wrapped.append('</td></tr>')
            wrapped.append('</table>')

            # Replace the code block in modified
            # Keep the marker line as is, replace lines after it
            for idx in range(code_start, k + 1):
                modified[idx] = None  # mark for removal

            # Insert wrapped content after the marker line
            # Find where to insert
            insert_pos = i + 1
            while insert_pos < len(modified) and modified[insert_pos] is None:
                insert_pos += 1

            # Shift and insert
            new_lines = modified[:insert_pos] + wrapped + [l for l in modified[insert_pos:] if l is not None]
            # Rebuild modified list
            lines = new_lines
            modified = list(new_lines)
            break

# Join back
c = '\n'.join([l for l in modified if l is not None])

# Fix any empty lines issues
c = c.replace('\n\n\n', '\n\n')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')
