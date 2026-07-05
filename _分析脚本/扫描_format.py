import re

for fname in ['全局_C昭明路线图.md', '全局_B交易体系.md', '全局_A盯盘警示卡.md']:
    filepath = f'd:/@VSwork/VS昭明计划VBA优化/_规则文档/{fname}'
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f'=== {fname} ===')

    # Check 1: Unmatched HTML tags
    opens = content.count('<table')
    closes = content.count('</table>')
    print(f'  <table>: {opens}, </table>: {closes} -> {"OK" if opens == closes else "MISMATCH!"}')

    tr_opens = content.count('<tr>')
    tr_closes = content.count('</tr>')
    print(f'  <tr>: {tr_opens}, </tr>: {tr_closes} -> {"OK" if tr_opens == tr_closes else "MISMATCH!"}')

    td_opens = content.count('<td>')
    td_closes = content.count('</td>')
    print(f'  <td>: {td_opens}, </td>: {td_closes} -> {"OK" if td_opens == td_closes else "MISMATCH!"}')

    # Check 2: Code fences (count triple backticks)
    fences = len(re.findall(r'```', content))
    print(f'  ``` fences: {fences} -> {"OK" if fences % 2 == 0 else "UNBALANCED!"}')

    # Check 3: Duplicate table separator lines (same as header)
    lines = content.split('\n')
    dup_seps = 0
    for i in range(len(lines) - 1):
        if lines[i].startswith('|') and '|' in lines[i]:
            if re.match(r'^\|:[-]+\|', lines[i]) and i > 0 and lines[i-1] == lines[i]:
                dup_seps += 1
                print(f'  Duplicate sep at line {i+1}: {lines[i][:40]}')

    # Check 4: Stray HTML tags (not between <table> and </table>)
    # Simple check: count tags outside any <table> block
    print()
