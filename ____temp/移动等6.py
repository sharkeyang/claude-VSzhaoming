# -*- coding: utf-8 -*-
"""主题归位3: 将 2.4.2.11.2(等6) 移到 §2.7，作为 2.7.2"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
f = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
lines = io.open(f, encoding='utf-8').read().split('\n')

# 1. 提取 2.4.2.11.2 内容（到 2.4.2.11.3 前）
start = next(i for i, l in enumerate(lines) if l.startswith('**2.4.2.11.2 '))
end_113 = next(i for i, l in enumerate(lines) if l.startswith('**2.4.2.11.3 '))
content_end = end_113
while content_end > start and lines[content_end-1].strip() == '':
    content_end -= 1
section = lines[start:content_end]

# 2. 删除原位置
del lines[start:content_end]

# 3. 重编号：2.4.2.11.2 -> 2.7.2
section = [l.replace('**2.4.2.11.2 ', '**2.7.2 ') for l in section]

# 4. 定位 §2.7 的 2.7.1 之后，插入 2.7.2
sec27 = next(i for i, l in enumerate(lines) if l.startswith('### 2.7 '))
# 找 2.7.1 结束（到 2.8 前）
sec28 = next(i for i, l in enumerate(lines) if l.startswith('### 2.8 '))
# 在 sec28 前插入 section + 空行
lines[sec28:sec28] = section + ['']

io.open(f, 'w', encoding='utf-8').write('\n'.join(lines))
print('2.4.2.11.2(等6) -> 2.7.2 移动完成')

# 验证
lines2 = io.open(f, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines2, 1):
    if re.match(r'^#### 2\.7\.\d', l):
        print(f'  L{i}: {l[:50]}')