import re
path = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# 第八章从 5158 行（索引5157）开始
# 修正 7.x 标题 -> 8.x（只改标题行）
changed = 0
for i in range(5157, len(lines)):
    new = lines[i]
    # 标题行：### 7.x / #### 7.x.x / ##### 7.x.x.x -> 8.x
    new = re.sub(r'^(#{3,6}) 7\.', r'\1 8.', new)
    if new != lines[i]:
        lines[i] = new
        changed += 1

print(f'修正 {changed} 行标题')
with open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
