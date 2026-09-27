import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 处理 > **操作规则：** 开头的行（护型操作结论）→ 指向第六章
changed = 0
for i, l in enumerate(lines):
    if re.match(r'^> \*\*操作规则：\*\*', l):
        new = re.sub(r'^> \*\*操作规则：\*\*', '> **操作结论（第六章 §6.7.1 已定型）：**', l)
        lines[i] = new
        changed += 1

print(f'修改 {changed} 行')
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
