import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 把 > 验证结果（...）： 和 > 已验证数据（...）： 改回加粗标题式
content = re.sub(r'^> (验证结果（[^\n]*？)：)', r'**\1**', content, flags=re.M)
content = re.sub(r'^> (已验证数据（[^\n]*？)：)', r'**\1**', content, flags=re.M)
content = re.sub(r'^> (验证数据（[^\n]*？)：)', r'**\1**', content, flags=re.M)
print('统一为加粗标题式完成')
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
