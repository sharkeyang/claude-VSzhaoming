# Add angle brackets <> around operational terms in C file text
with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Define which terms to wrap in paragraphs (NOT in tables or code blocks)
terms = ['买漏周', '买漏日', '卖止盈', '卖诱多', '买初介', '持主动', '持被动', '卖止浮']

# Apply replacements in text sections (outside code blocks and tables)
# Simple approach: just replace specific word occurrences
replacements = [
    ('买漏周机会', '<买漏周>机会'),
    ('买漏周概率', '<买漏周>概率'),
]
for old, new in replacements:
    c = c.replace(old, new)

# For the discussion section (lines 1060-1081), wrap standalone terms
# These are in paragraph text, not in tables
# Define specific context patterns that appear in prose

prose_fixes = {
    '归类为"卖止浮"或"卖诱多"': '归类为"<卖止浮>"或"<卖诱多>"',
    '属于持主动范畴': '属于<持主动>范畴',
    '诱多后的反转（已有卖诱多覆盖）': '诱多后的反转（已有<卖诱多>覆盖）',
    '就是卖诱多的一部分（已有卖诱多覆盖）': '就是<卖诱多>的一部分（已有<卖诱多>覆盖）',
    '保持为持被动': '保持为<持被动>',
    '持被动，不单独归类为卖出': '<持被动>，不单独归类为卖出',
    '卖出的触发点应该是下破DJC（卖止浮）': '卖出的触发点应该是下破DJC（<卖止浮>）',
    '将其归为持被动是对的': '将其归为<持被动>是对的',
    '出现卖止盈或卖诱多信号': '出现<卖止盈>或<卖诱多>信号',
}

for old, new in prose_fixes.items():
    c = c.replace(old, new)

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(c)
print('Done')