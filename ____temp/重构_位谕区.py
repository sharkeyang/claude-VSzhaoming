"""
Refactor 位谕 constants in 神谕.bas:
Move 四域周/四域日/基本分类/信号分类 to 周层/日层区
Add 仓策略/仓小传
"""
import pathlib, re

p = pathlib.Path('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas')
c = p.read_text(encoding='utf-8')
lines = c.split('\n')

# ====== 1. Add 位谕of周层四域 after 位谕of周层大局 ======
for i, line in enumerate(lines):
    if '位谕of周层大局' in line and 'Const' in line:
        lines.insert(i+1, '')
        lines.insert(i+2, "Public Const 位谕of周层四域 = 位谕始of族周层 + 14      'WJC丘优化：四域判定（多长/多被/空长/空看）")
        print(f'Added 位谕of周层四域 at line {i+2}')
        break

# ====== 2. Add 位谕of日层四域 before 位谕of日层联动 ======
for i, line in enumerate(lines):
    if '位谕of日层联动' in line and 'Const' in line:
        lines.insert(i, "Public Const 位谕of日层四域 = 位谕始of族日层 + 0      '日级四域判定（多长/多被/空长/空看）")
        lines.insert(i+1, '')
        # Shift all existing日层位谕 by +1
        base = i + 2  # start after the inserted line
        for j in range(base, len(lines)):
            if '位谕始of族日层' in lines[j] and 'Const' in lines[j] and '+0' not in lines[j]:
                # Extract the current offset
                m = re.search(r'\位谕始of族日层\s*\+\s*(\d+)', lines[j])
                if m:
                    old_off = int(m.group(1))
                    new_off = old_off + 1
                    lines[j] = lines[j].replace(f'+ {old_off}', f'+ {new_off}')
                    lines[j] = lines[j].replace(f'+{old_off}', f'+{new_off}')
                    print(f'  Shifted 日层 at line {j+1}: +{old_off} -> +{new_off}')
        print(f'Added 位谕of日层四域 at line {i+1}')
        break

# ====== 3. Add 位谕of日层段 and 位谕of日层机警 after 位谕of日层盈提示 ======
for i, line in enumerate(lines):
    if '位谕of日层盈提示' in line and 'Const' in line:
        insert_pos = i + 1
        # Skip blank lines
        while insert_pos < len(lines) and lines[insert_pos].strip() == '':
            insert_pos += 1
        # Find current offset of next item
        for j in range(insert_pos, len(lines)):
            m = re.search(r'位谕始of族日层\s*\+\s*(\d+)', lines[j])
            if m and 'Const' in lines[j]:
                base_off = int(m.group(1))
                break

        lines.insert(insert_pos, '')
        lines.insert(insert_pos, f"Public Const 位谕of日层段 = 位谕始of族日层 + {base_off}      '日级别仓位段（买初/持主/持被/卖浮）")
        lines.insert(insert_pos+1, '')
        lines.insert(insert_pos+1, f"Public Const 位谕of日层机警 = 位谕始of族日层 + {base_off+1}      '日级别信号（警盈/警诱/漏日/漏周）")
        print(f'Added 位谕of日层段/+{base_off} and 位谕of日层机警/+{base_off+1} at line {insert_pos+1}')

        # Shift all subsequent日层位谕 by +2
        for j in range(insert_pos+2, len(lines)):
            if 'Const' in lines[j] and '位谕始of族日层' in lines[j]:
                m = re.search(r'\位谕始of族日层\s*\+\s*(\d+)', lines[j])
                if m:
                    old_off = int(m.group(1))
                    if old_off >= base_off:
                        new_off = old_off + 2
                        lines[j] = lines[j].replace(f'+{old_off}', f'+{new_off}')
        print(f'  Shifted subsequent 日层位谕 by +2')
        break

# ====== 4. Add 位谕of仓策略 and 位谕of仓小传 at end of 族仓 ======
for i, line in enumerate(lines):
    if '位谕终of族仓' in line and 'Const' in line:
        lines.insert(i, "Public Const 位谕of仓策略 = 位谕始of族仓 + 17      '策略决定（长基仓/周浮仓/日浮仓）")
        lines.insert(i+1, "Public Const 位谕of仓小传 = 位谕始of族仓 + 18      '小传综合信息，供Python读取")
        # Update 位谕终of族仓
        lines[i+2] = "Public Const 位谕终of族仓 = 位谕of仓小传"
        print(f'Added 位谕of仓策略/仓小传 near line {i+1}')
        break

# ====== 5. Replace old constant definitions ======
for i, line in enumerate(lines):
    if '位谕of四域周' in line and 'Const' in line:
        lines[i] = ''  # delete old line
        print(f'Deleted old 位谕of四域周 at line {i+1}')
    if '位谕of四域日' in line and 'Const' in line:
        lines[i] = ''
        print(f'Deleted old 位谕of四域日 at line {i+1}')
    if '位谕of基本分类' in line and 'Const' in line:
        lines[i] = ''
        print(f'Deleted old 位谕of基本分类 at line {i+1}')
    if '位谕of信号分类' in line and 'Const' in line:
        lines[i] = ''
        print(f'Deleted old 位谕of信号分类 at line {i+1}')

# ====== 6. Remove 位谕列终全部 if exists ======
for i, line in enumerate(lines):
    if '位谕列终全部' in line and 'Const' in line:
        lines[i] = ''
        print(f'Deleted 位谕列终全部 at line {i+1}')

# ====== 7. Update all name references ======
text = '\n'.join(lines)
replacements = [
    ('位谕of四域周', '位谕of周层四域'),
    ('位谕of四域日', '位谕of日层四域'),
    ('位谕of基本分类', '位谕of日层段'),
    ('位谕of信号分类', '位谕of日层机警'),
]
for old, new in replacements:
    cnt = text.count(old)
    text = text.replace(old, new)
    print(f'Renamed {old} -> {new} ({cnt} occurrences)')

# ====== 8. Remove extra blank lines (3+ consecutive) ======
while '\n\n\n\n' in text:
    text = text.replace('\n\n\n\n', '\n\n\n')

# ====== 9. Update 位谕列终全部 in 谕组 array dimensioning ======
# Find the ReDim line that uses位谕列终全部
old_dim = '1 To 位谕列终全部'
new_dim = '1 To 位谕of仓小传'
if old_dim in text:
    text = text.replace(old_dim, new_dim)
    print(f'Updated ReDim: {old_dim} -> {new_dim}')

p.write_text(text, encoding='utf-8')
print(f'\nDone: {len(text)} chars, {text.count(chr(10))} lines')
print(f'位谕of周层四域: {text.count("位谕of周层四域")}次')
print(f'位谕of日层四域: {text.count("位谕of日层四域")}次')
print(f'位谕of日层段: {text.count("位谕of日层段")}次')
print(f'位谕of日层机警: {text.count("位谕of日层机警")}次')
print(f'位谕of仓策略: {text.count("位谕of仓策略")}次')
print(f'位谕of仓小传: {text.count("位谕of仓小传")}次')