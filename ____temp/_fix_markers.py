# -*- coding: utf-8 -*-
"""Fix duplicate code markers and diagram blank lines"""
import os, re
root = os.getcwd()
rules_dir = None
for item in os.listdir(root):
    if item.startswith('_') and os.path.isdir(os.path.join(root, item)):
        full = os.path.join(root, item)
        files = os.listdir(full)
        if '全局_C昭明路线图.md' in files:
            rules_dir = full
            break

c_path = os.path.join(rules_dir, '全局_C昭明路线图.md')
with open(c_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Step 1: Collapse consecutive ``` markers
result = []
prev_code = False
for l in lines:
    s = l.strip()
    is_code = s.startswith('```')
    if is_code and prev_code:
        continue
    result.append(l)
    prev_code = is_code if is_code else False

# Step 2: Fix code block diagram blank lines
content = ''.join(result)
nl = '\n'
code_lines = content.split(nl)

result2 = []
in_code = False
buf = []

for l in code_lines:
    s = l.strip()
    if s.startswith('```'):
        if in_code:
            cleaned = []
            for i, cl in enumerate(buf):
                is_blank = (cl.strip() == '')
                pc = i > 0 and buf[i-1].strip() != ''
                nc = i < len(buf)-1 and buf[i+1].strip() != ''
                if is_blank and pc and nc:
                    continue
                cleaned.append(cl)
            result2.append('```')
            for cl in cleaned:
                result2.append(cl)
            result2.append('```')
            buf = []
        else:
            result2.append('```')
        in_code = not in_code
        continue
    if in_code:
        buf.append(l)
    else:
        result2.append(l)

new_content = nl.join(result2)

with open(c_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

new_lines = new_content.split(nl)
total = len(new_lines)
blank = sum(1 for l in new_lines if l.strip() == '')
print(f'Lines: {len(code_lines)} -> {total}')
print(f'Blanks: {blank} ({blank*100//total}%)')

# Check §2.2.4 diagram
idx224 = new_content.find('#### 2.2.4')
idx225 = new_content.find('#### 2.2.5', idx224)
sec = new_content[idx224:idx225]
in_code = False
for l in sec.split(nl):
    if l.strip().startswith('```'):
        in_code = not in_code
        continue
    if in_code and l.strip():
        print(f'  {l.strip()[:70]}')