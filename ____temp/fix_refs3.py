import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# §8.2.4 下的小节编号 7.2.4.x → 8.2.4.x（仅标题行）
# 用正则匹配标题行
content = re.sub(r'^(\*\*|#{2,6} )7\.2\.4\.', r'\18.2.4.', content, flags=re.M)
print('8.2.4 编号修正完成')
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
