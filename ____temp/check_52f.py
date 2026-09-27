import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 验证 5.2 标题和目录
print('=== 5.2 标题 ===')
for i, l in enumerate(lines):
    if re.match(r'^### 5\.2', l):
        print(f'  [{i+1}]: {l.strip()[:80]}')
print('=== 目录 5.2 ===')
for i, l in enumerate(lines[:340]):
    if '5.2 升管' in l or '5.2 操作' in l:
        print(f'  [{i+1}]: {l.strip()[:80]}')

# 验证 6.6.6 和 6.7.7
print('=== 6.6.6 / 6.7.7 ===')
for i, l in enumerate(lines):
    if '6.6.6' in l or '6.7.7' in l:
        print(f'  [{i+1}]: {l.strip()[:80]}')
