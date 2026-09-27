import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 处理含"操作规则："的行（护型操作结论，在第六章外）
changed = 0
for i, l in enumerate(lines):
    if '操作规则：' in l and '**操作规则：**' in l:
        new = l.replace('**操作规则：**', '**操作结论（第六章 §6.7.1 已定型）：**')
        lines[i] = new
        changed += 1

print(f'修改 {changed} 行')
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
