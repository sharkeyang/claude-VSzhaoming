import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 把 **已验证数据（...）：** 改为 > 已验证数据（...）：
# 匹配行首 **已验证数据（...）：**
content = re.sub(r'^\*\*已验证数据（[^\n]*?）：\*\*', lambda m: '> ' + m.group(0).strip('*').strip('**'), content, flags=re.M)
# 更精确：去掉首尾 **
content = re.sub(r'^\*\*(已验证数据（[^\n]*?）)：\*\*', r'> \1：', content, flags=re.M)
print('已验证数据格式统一完成')
with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
