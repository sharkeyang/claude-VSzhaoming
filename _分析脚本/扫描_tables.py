import re

for fname in ['全局_C昭明路线图.md', '全局_B交易体系.md', '全局_A盯盘警示卡.md']:
    filepath = f'd:/@VSwork/VS昭明计划VBA优化/_规则文档/{fname}'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f'=== {fname} ===')
    lines = content.split('\n')
    issues = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Check if line looks like a markdown table header (| header | header |)
        if stripped.startswith('|') and '|' in stripped[1:]:
            # Check if it's a header row (followed by separator)
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                # If this line has text headers and next line doesn't have separator
                if re.match(r'^\|.*[a-zA-Z一二三四五六七八九十].*\|', stripped):
                    # Check if next line is a separator
                    if not re.match(r'^\|[-:| ]+\|', next_line):
                        # Check if this is a data row (not header with separator)
                        # Actually, check if the PREVIOUS line is a separator
                        prev_line = lines[i - 1].strip() if i > 0 else ''
                        if not re.match(r'^\|[-:| ]+\|', prev_line):
                            # This might be a table row without a proper header
                            if '---' not in stripped and not stripped.startswith('|:'):
                                issues.append((i + 1, stripped[:60]))

    if issues:
        print(f'  Potential table issues ({len(issues)}):')
        for ln, text in issues:
            if not text.startswith('| <') and not text.startswith('|  '):
                print(f'    L{ln}: {text}')
    else:
        print('  All tables OK')
    print()