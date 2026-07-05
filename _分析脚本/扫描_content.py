import re

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()
    lines = c.split('\n')

print('=== SCANNING FOR ISSUES ===\n')

issues = []

# 1. Check for duplicate headings at same level
headings = {}
for i, line in enumerate(lines):
    m = re.match(r'^(#{2,4}) (.+)', line.strip())
    if m:
        level = m.group(1)
        title = m.group(2).strip()
        key = (level, title)
        if key in headings:
            issues.append(f'DUPLICATE heading L{i+1}: {level} {title} (also at L{headings[key]})')
        else:
            headings[key] = i + 1

# 2. Check for broken markdown table separators
for i, line in enumerate(lines):
    stripped = line.strip()
    # A separator should only contain | - : and spaces
    if stripped.startswith('|') and re.match(r'^\|[-: |]+\|?$', stripped):
        # It's a separator line, check if it follows a header
        if i > 0:
            prev = lines[i-1].strip()
            if prev.startswith('|') and not re.match(r'^\|[-: |]+\|?$', prev):
                pass  # valid
            # If prev is also a separator, both are okay (markdown allows this)

# 3. Check for stray characters near HTML tags
for i, line in enumerate(lines):
    if '</table>' in line or '</td>' in line or '</tr>' in line:
        # Check if there's text before or after the tag on the same line
        tag_match = re.search(r'</?(table|td|tr)>', line)
        if tag_match:
            pos = tag_match.start()
            before = line[:pos].strip()
            after = line[tag_match.end():].strip()
            if before and not before.startswith('<') and before != '```':
                issues.append(f'STRAY TEXT before HTML tag L{i+1}: "{before[:30]}"')
            if after and not after.startswith('<') and after != '```':
                issues.append(f'STRAY TEXT after HTML tag L{i+1}: "{after[:30]}"')

# 4. Check for content between </table> and next section without blank line
for i, line in enumerate(lines):
    if line.strip() == '</table>':
        if i + 1 < len(lines):
            next_line = lines[i+1].strip()
            if next_line and not next_line.startswith('<') and not next_line.startswith('```'):
                if next_line.startswith('#'):
                    pass  # heading is fine
                elif not next_line.startswith('|'):
                    pass

# 5. Check for incomplete sentences / orphans
orphans = []
for i, line in enumerate(lines):
    stripped = line.strip()
    # A line that starts with lowercase letter after a blank line might be orphaned text
    if stripped and stripped[0].islower() and i > 0 and not lines[i-1].strip():
        if len(stripped) < 100:
            orphans.append((i+1, stripped[:60]))

# 6. Check for unmatched code fences
fence_count = 0
fence_issues = []
for i, line in enumerate(lines):
    if line.strip().startswith('```'):
        fence_count += 1

if fence_count % 2 != 0:
    issues.append(f'UNBALANCED code fences: {fence_count} (should be even)')

# 7. Check for consecutive blank lines (more than 3)
blank_count = 0
for i, line in enumerate(lines):
    if line.strip() == '':
        blank_count += 1
    else:
        if blank_count > 4:
            issues.append(f'EXCESSIVE blanks ({blank_count}) before L{i+1}: "{lines[i][:40]}"')
        blank_count = 0

# 8. Check for duplicated section headers (same text appearing twice)
all_headers = []
for i, line in enumerate(lines):
    m = re.match(r'^(#{1,4}) (.+)', line.strip())
    if m:
        all_headers.append((i+1, m.group(2).strip()))

# Find headers that appear more than once (same text)
header_texts = {}
for ln, text in all_headers:
    if text in header_texts:
        header_texts[text].append(ln)
    else:
        header_texts[text] = [ln]

for text, lns in header_texts.items():
    if len(lns) > 1:
        # Only flag if they're not sequential (which would be a TOC + section)
        if max(lns) - min(lns) > 50:
            issues.append(f'DUPLICATE section: "{text}" at lines {lns}')

# PRINT RESULTS
print(f'Found {len(issues)} potential issues:')
for issue in issues:
    print(f'  ⚠️  {issue}')

print(f'\nOrphaned single lines (may be normal text, review manually):')
for ln, text in orphans[:10]:
    print(f'  L{ln}: "{text}"')

print(f'\nTotal code fences: {fence_count} ({"OK" if fence_count % 2 == 0 else "UNBALANCED!"})')
print(f'Total headings: {len(all_headers)}')
print(f'Total lines: {len(lines)}')