import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()
# 找第六章起始（## 六）
ch6_start = None
for i, l in enumerate(lines):
    if re.match(r'^## 六', l):
        ch6_start = i
        break
print(f'第六章起始: 行 {ch6_start+1}')

# 第六章外（ch6_start 之前）含"操作规则"的行
print('=== 第六章外含"操作规则"的行 ===')
count = 0
for i in range(ch6_start):
    if '操作规则' in lines[i]:
        print(f'  [{i+1}]: {lines[i].strip()[:80]}')
        count += 1
print(f'  共 {count} 处')

# 验证新增内容
print('=== 新增内容验证 ===')
for needle in ['6.6.6 升管/跌管思维', '6.7.7 操盘成功率', '5.2 升管/跌管思维']:
    found = any(needle in l for l in lines)
    print(f'  {"✅" if found else "❌"} {needle}')
