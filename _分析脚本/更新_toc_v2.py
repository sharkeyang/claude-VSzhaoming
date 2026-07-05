import re

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()
    lines = c.split('\n')

# Find all ## and ### headings (after the frontmatter)
# Skip the TOC itself and headings inside code blocks
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

    m = re.match(r'^(#{2,3}) (.+)', stripped)
    if m:
        level = len(m.group(1))
        title = m.group(2).strip()
        # Skip the frontmatter metadata and the main title
        if title.startswith('name:') or title.startswith('description:') or title.startswith('metadata'):
            continue
        if title == '昭明路线图 — 全流程量化交易系统':
            continue

        # Generate anchor
        # Remove special characters, keep Chinese, letters, numbers
        anchor = re.sub(r'[^\w一-鿿]+', '', title).lower()
        headings.append((level, title, anchor))

# Build TOC
toc_lines = ['**目录：**']
for level, title, anchor in headings:
    if level == 2:
        toc_lines.append(f'- [{title}](#{anchor})')
    else:
        toc_lines.append(f'  - [{title}](#{anchor})')

toc = '\n'.join(toc_lines)

# Find and replace old TOC
start = c.find('**目录：**')
# Find the end of TOC (next --- after TOC)
after_toc = c.find('\n---', start)
if after_toc < 0:
    after_toc = c.find('\n\n\n#', start)

if start >= 0 and after_toc >= 0:
    before = c[:start]
    after = c[after_toc:]  # include the ---
    new_c = before + toc + '\n\n' + after
    with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
        f.write(new_c)
    print(f'Updated TOC: {len(headings)} headings ({sum(1 for h in headings if h[0]==2)} h2, {sum(1 for h in headings if h[0]==3)} h3)')
else:
    print(f'start={start}, after_toc={after_toc}')