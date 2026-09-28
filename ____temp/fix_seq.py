path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 只处理 §8.1.4.4 和 §8.1.4.5 区域（5696-5790行，索引5695-5789）
# 找到 8.1.4.4 和 8.1.5 的位置
start = None
end = None
for i, l in enumerate(lines):
    if '8.1.4.4 WXAB 由负转正前置状态验证' in l:
        start = i
    if '#### 8.1.5 日类操作的一大误区' in l:
        end = i
        break
print(f'区域: {start+1} 到 {end+1}')

# 替换序号（只在该区域）
seq_map = {'①': '情况1', '②': '情况2', '③': '情况3', '④': '情况4'}
changed = 0
for i in range(start, end):
    for old, new in seq_map.items():
        if old in lines[i]:
            lines[i] = lines[i].replace(old, new)
            changed += 1
print(f'替换 {changed} 处')
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
