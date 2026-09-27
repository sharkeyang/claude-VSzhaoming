import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
ch6_start = None
for i, l in enumerate(lines):
    if re.match(r'^## 六', l):
        ch6_start = i
        break
print('第六章外含"操作规则"的行（最终）:')
count = 0
for i in range(ch6_start):
    if '操作规则' in lines[i]:
        print(f'  [{i+1}]: {lines[i].strip()[:95]}')
        count += 1
print(f'  共 {count} 处')
