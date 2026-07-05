import re

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()
    lines = c.split('\n')

# Find all ## headings (second level)
h2_headings = []
for i, line in enumerate(lines):
    m = re.match(r'^## (.+)', line.strip())
    if m:
        title = m.group(1).strip()
        # Create anchor: lowercase, replace spaces/special chars
        anchor = re.sub(r'[^\w一-鿿]+', '-', title).lower().strip('-')
        # Skip ones already in TOC
        h2_headings.append((title, anchor))

# Build new TOC
toc_lines = ['**目录：**']
for title, anchor in h2_headings:
    # Check if it's an appendix
    if title.startswith('附录') or title.startswith('附'):
        toc_lines.append(f'- [{title}](#{anchor})')
    else:
        toc_lines.append(f'- [{title}](#{anchor})')

toc = '\n'.join(toc_lines)

# Find old TOC and replace
start = c.find('**目录：**')
end = c.find('---\n\n\n# 昭明路线图', start)

if start >= 0 and end >= 0:
    before = c[:start]
    after = c[end:]
    new_c = before + toc + '\n\n' + after
    with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
        f.write(new_c)
    print(f'Updated TOC with {len(h2_headings)} entries')
else:
    print(f'start={start}, end={end}')
    # Try finding end differently
    # The pattern is: TOC then blank line then --- then blank lines then # 昭明路线图
    if start >= 0:
        end = c.find('\n# 昭明路线图', start)
        if end >= 0:
            before = c[:start]
            after = c[end:]
            new_c = before + toc + '\n\n' + after
            with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
                f.write(new_c)
            print(f'Updated TOC with {len(h2_headings)} entries (alt method)')
