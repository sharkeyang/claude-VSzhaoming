def wrap_section(content, start_marker, end_marker, start_offset=0):
    """Wrap content between start_marker and end_marker with <table border>"""
    start = content.find(start_marker)
    if start < 0:
        return content, False
    start = start + start_offset

    if isinstance(end_marker, str):
        end = content.find(end_marker, start)
    else:
        end = end_marker

    if end < 0:
        return content, False

    table_start = '<table border="1" cellpadding="8" cellspacing="0" style="border-collapse:collapse;border:2px solid #888;margin:8px 0">\n<tr><td>\n\n'
    table_end = '\n\n</td></tr>\n</table>'

    before = content[:start]
    section = content[start:end]
    after = content[end:]

    return before + table_start + section + table_end + after, True

# ===== B文件 =====
with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_B交易体系.md', 'r', encoding='utf-8') as f:
    b = f.read()

# 1. 核心主次原则（全文核心思想） - 从 ## 二、 到 next ##
b, ok = wrap_section(b, '## 🟡 二、核心主次原则（全文核心思想）', '\n## 🟢 三、')
print(f'B: 核心主次原则 wrapped: {ok}')

# 2. 3.1 常规标准开仓 - from ### 3.1  to next ### 3.2
b, ok = wrap_section(b, '### 3.1 常规标准开仓（`DJE` 上方，主力仓位）', '\n### 3.2')
print(f'B: 3.1 wrapped: {ok}')

# 3. 3.2 特例试仓 - from ### 3.2 to next ##
b, ok = wrap_section(b, '### 3.2 特例试仓（`DJE` 下方仅允许极小仓位博弈）', '\n## 🔴 四、')
print(f'B: 3.2 wrapped: {ok}')

# 4. 5.3 浮仓特殊限制 - from ### 5.3 to next ### 5.4
b, ok = wrap_section(b, '### 5.3 浮仓特殊限制', '\n### 5.4')
print(f'B: 5.3 wrapped: {ok}')

# 5. 5.5 仓位心法——舍的功效 - from ### 5.5 to next ##
b, ok = wrap_section(b, '### 5.5 仓位心法 —— 舍的功效', '\n## 六、')
print(f'B: 5.5 wrapped: {ok}')

# 6. 七、伪代码 - from ## 七、 to next ##
b, ok = wrap_section(b, '## 七、伪代码（可直接改写为公式条件）', '\n## 八、')
print(f'B: 七 wrapped: {ok}')

# 7. 操作口诀 - from **操作口诀：** to next `---`
b, ok = wrap_section(b, '**操作口诀：**', '\n---')
print(f'B: 操作口诀 wrapped: {ok}')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_B交易体系.md', 'w', encoding='utf-8') as f:
    f.write(b)
print('B done')

# ===== A文件 =====
with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_A盯盘警示卡.md', 'r', encoding='utf-8') as f:
    a = f.read()

# 操作口诀 in A file - check if it exists
a, ok = wrap_section(a, '### 1.3 口诀（反复念）', '### 1.4')
print(f'A: 口诀 wrapped: {ok}')

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_A盯盘警示卡.md', 'w', encoding='utf-8') as f:
    f.write(a)
print('A done')