path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 删除 §8.1.5（从 '#### 8.1.5 日类操作的一大误区' 到 '#### 8.1.6 周日联合' 之前）
start = content.find('#### 8.1.5 日类操作的一大误区')
end = content.find('#### 8.1.6 周日联合')
if start != -1 and end != -1:
    removed = content[start:end]
    content = content[:start] + content[end:]
    print(f'删除 §8.1.5，长度 {len(removed)} 字符')
else:
    print(f'未找到: start={start}, end={end}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
