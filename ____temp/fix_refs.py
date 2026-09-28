import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 交叉引用错误修正
repl = [
    ('与10.1一致', '与2.1一致'),
    ('（见3.4.1）', '（见2.4.1）'),
    ('与4.7.1一致', '与2.8.3一致'),
    ('与2.4.2.4口径一致', '与4.3.2.4口径一致'),
    ('与2.4.2.8', '与4.3.2.8'),
]
changed = 0
for old, new in repl:
    if old in content:
        content = content.replace(old, new)
        changed += 1
print(f'交叉引用修正 {changed} 处')
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
