# Fix strategy names and wrap sections with table borders
with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_B交易体系.md', 'r', encoding='utf-8') as f:
    b = f.read()

# Add <> to strategy names in B file
b = b.replace('### 🟢 策略一：长基仓策略', '### 🟢 策略一：<长基仓策略>')
b = b.replace('### 🟡 策略二：周浮仓策略', '### 🟡 策略二：<周浮仓策略>')
b = b.replace('### 🔵 策略三：日浮仓策略', '### 🔵 策略三：<日浮仓策略>')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_B交易体系.md', 'w', encoding='utf-8') as f:
    f.write(b)
print('B done')

# Now the big task: wrap sections in C file
with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Helper function to wrap a section content inside a <table border>
def wrap_with_table(content, start_marker, end_marker_or_next_header):
    """Wrap content between two markers with <table border>"""
    start = content.find(start_marker)
    if start < 0:
        return content

    if isinstance(end_marker_or_next_header, str):
        end = content.find(end_marker_or_next_header, start + len(start_marker))
    else:
        end = end_marker_or_next_header

    if end < 0:
        return content

    # Add table tags before start marker
    table_start = '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">\n<tr><td>\n\n'
    table_end = '\n\n</td></tr>\n</table>'

    before = content[:start]
    section_content = content[start:end]
    after = content[end:]

    return before + table_start + section_content + table_end + after

# Wrap specific sections
sections_to_wrap = [
    ('#### M8：资讯爬虫预警（3天）', '#### M9：'),
    ('**小传结构（每只推荐标的输出）：**', '---'),
    ('#### 2.3.2 板块轮动分析逻辑', '#### 2.3.3'),
    ('**输出格式（小传）：**', '#### 2.2.4'),
    ('#### 2.2.2 第一部分：已有持仓操作提示', '#### 2.2.3'),
    ('**2.6 数据验证（10只股票37661行遍历结果）：**', '## 附录一'),
]

for start, end in sections_to_wrap:
    old = c
    c = wrap_with_table(c, start, end)
    if c != old:
        print(f'Wrapped: {start[:30]}')

# Wrap 流水线 section
c = wrap_with_table(c, '**流水线：**', '---')

# Wrap 操盘计划模板
c = wrap_with_table(c, '**操盘计划模板：**', '### 附录一')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('C done')
