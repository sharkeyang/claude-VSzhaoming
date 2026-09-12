# -*- coding: utf-8 -*-
"""主题归位2: 将 2.4.2.12/2.4.2.13(DXAB负转正特权) 移到 §4.7，作为 4.7.8/4.7.9"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
f = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
lines = io.open(f, encoding='utf-8').read().split('\n')

# 1. 提取 2.4.2.12 到 2.4.2.13 结束（到 --- 前）
start = next(i for i, l in enumerate(lines) if l.startswith('**2.4.2.12 '))
# 找 --- 边界（2.4.2.13 之后）
dash = None
for i in range(start, len(lines)):
    if lines[i].strip() == '---':
        dash = i
        break
content_end = dash
while content_end > start and lines[content_end-1].strip() == '':
    content_end -= 1
section = lines[start:content_end]

# 2. 删除原位置（连同 --- 前的空行）
del lines[start:dash+1]

# 3. 重编号：2.4.2.12 -> 4.7.8, 2.4.2.13 -> 4.7.9, 子级顺延
section = [l.replace('**2.4.2.12.1 ', '**4.7.8.1 ')
             .replace('**2.4.2.12.2 ', '**4.7.8.2 ')
             .replace('**2.4.2.12.3 ', '**4.7.8.3 ')
             .replace('**2.4.2.12.4 ', '**4.7.8.4 ')
             .replace('**2.4.2.12 ', '**4.7.8 ')
             .replace('**2.4.2.13.1 ', '**4.7.9.1 ')
             .replace('**2.4.2.13.2 ', '**4.7.9.2 ')
             .replace('**2.4.2.13.3 ', '**4.7.9.3 ')
             .replace('**2.4.2.13.4 ', '**4.7.9.4 ')
             .replace('**2.4.2.13.5 ', '**4.7.9.5 ')
             .replace('**2.4.2.13 ', '**4.7.9 ') for l in section]

# 4. 定位 §4.8 起始，在 4.7.7 之后、4.8 之前插入
sec48 = next(i for i, l in enumerate(lines) if l.startswith('### 4.8 '))
# 在 sec48 前插入 section + 空行（原 sec48 前有 --- 分隔）
lines[sec48:sec48] = section + ['']

io.open(f, 'w', encoding='utf-8').write('\n'.join(lines))
print('2.4.2.12/2.4.2.13 -> 4.7.8/4.7.9 移动完成')

# 验证
lines2 = io.open(f, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines2, 1):
    if re.match(r'^\*\*4\.7\.(8|9) ', l):
        print(f'  L{i}: {l[:50]}')