import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 1. 表格行不应以 ** 开头
bad_table = [i for i, l in enumerate(lines) if l.startswith('|') and re.match(r'^\|\s*\*\*', l)]
print(f'表格行以**开头: {len(bad_table)}')

# 2. 残留 > ** 开头
leftover = [i for i, l in enumerate(lines) if re.match(r'^> \*\*', l)]
print(f'残留 > ** 开头: {len(leftover)}')

# 3. 代码块围栏配对
code_fences = [i for i, l in enumerate(lines) if l.strip().startswith('```')]
print(f'代码块围栏数（应偶数）: {len(code_fences)}')

# 4. 二级标题
h2 = [l.strip() for l in lines if re.match(r'^## ', l)]
print(f'二级标题数: {len(h2)}')
for h in h2:
    print(f'  {h}')
