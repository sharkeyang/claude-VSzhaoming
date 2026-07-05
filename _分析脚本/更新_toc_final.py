import re

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()
    lines = c.split('\n')

# Extract headings after frontmatter
headings = []
in_code_block = False
in_frontmatter = True

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == '---':
        if in_frontmatter:
            in_frontmatter = False
            continue
    if in_frontmatter:
        continue
    if stripped.startswith('```'):
        in_code_block = not in_code_block
        continue
    if in_code_block:
        continue

    m = re.match(r'^(#{1,4}) (.+)', stripped)
    if m:
        level = len(m.group(1))
        title = m.group(2).strip()
        if title.startswith('name:') or title.startswith('description:') or title.startswith('metadata'):
            continue
        if title == '昭明路线图 — 全流程量化交易系统':
            continue

        # Generate anchor: lowercase, remove non-word chars except Chinese
        anchor = re.sub(r'[^\w一-鿿]+', '', title).lower()
        headings.append((level, title, anchor))

# Build TOC with proper indentation
toc_lines = ['**目录：**']
for level, title, anchor in headings:
    indent = '  ' * (level - 2)
    toc_lines.append(f'{indent}- [{title}](#{anchor})')

toc = '\n'.join(toc_lines)

# Find and replace old TOC
start = c.find('**目录：**')
end = c.find('\n---\n\n\n# 昭明路线图', start)
if end < 0:
    end = c.find('\n---\n\n# 昭明路线图', start)

if start >= 0 and end >= 0:
    before = c[:start]
    after = c[end:]
    new_c = before + toc + '\n\n' + after
    with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
        f.write(new_c)
    print(f'Updated TOC: {len(headings)} headings')
else:
    print(f'Error: start={start}, end={end}')
