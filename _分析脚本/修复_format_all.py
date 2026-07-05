with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Fix 附录二 table - remove incorrect <table> wrapper around markdown table
old_appendix_table = '| 步骤 | 事项 | 状态 | 完成时间 |\n<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">\n<tr><td>\n\n```'
new_appendix_table = '| 步骤 | 事项 | 状态 | 完成时间 |\n|:----:|:-----|:----:|:--------:|'
c = c.replace(old_appendix_table, new_appendix_table)

# Find and remove the closing </td></tr></table> after the appendix table
c = c.replace('</td></tr>\n</table>\n\n### 期货应用', '\n\n### 期货应用')
c = c.replace('</td></tr>\n</table>\n\n## 附录三', '\n\n## 附录三')

# 2. Fix Step 3 inside system evaluation section
c = c.replace('```\nStep 3：决策映射\n```', '**Step 3：决策映射**')

# 3. Bold the Step 3 in 2.3.5 section
c = c.replace('Step 3：生成操盘计划（含三种预案）', '**Step 3：生成操盘计划（含三种预案）**')

# 4. Wrap 输出格式（小传） code block with <table border>
xiaozhuan_start = '**输出格式（小传）：**\n\n```DJC之上（DXZC>0）'
xiaozhuan_wrapped = '**输出格式（小传）：**\n\n<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">\n<tr><td>\n\n```DJC之上（DXZC>0）'
c = c.replace(xiaozhuan_start, xiaozhuan_wrapped)

# Find the end of xiaozhuan code block - it ends before 【场景：
c = c.replace('```\n\n【场景：下周冲高】', '```\n\n</td></tr>\n</table>\n\n【场景：下周冲高】')

# Also wrap the second scenario
c = c.replace('```\n\n【场景：下日冲高】', '```\n\n</td></tr>\n</table>\n\n【场景：下日冲高】')
c = c.replace('```\n\n【场景：长期持有(日漏)】', '```\n\n</td></tr>\n</table>\n\n【场景：长期持有(日漏)】')
c = c.replace('```\n\n【场景：疑似诱多】', '```\n\n</td></tr>\n</table>\n\n【场景：疑似诱多】')
# And the last one
c = c.replace('```\n\n---\n\n#### 2.2.4', '```\n\n</td></tr>\n</table>\n\n---\n\n#### 2.2.4')

# 5. Fix 附录二 M0-M9 table: add <nobr> to status and date columns
lines = c.split('\n')
in_appendix2 = False
for i, line in enumerate(lines):
    if '| 步骤 | 事项 | 状态 | 完成时间 |' in line:
        in_appendix2 = True
        continue
    if in_appendix2 and line.strip().startswith('|') and 'M' in line:
        parts = line.split('|')
        if len(parts) >= 6:
            status = parts[3].strip()
            date = parts[4].strip().rstrip()
            parts[3] = ' <nobr>' + status + '</nobr> '
            parts[4] = ' <nobr>' + date + '</nobr> '
            lines[i] = '|'.join(parts)
    if in_appendix2 and (line.startswith('##') or line.startswith('#') or line.startswith('-')):
        in_appendix2 = False

c = '\n'.join(lines)

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')