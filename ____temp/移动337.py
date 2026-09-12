# -*- coding: utf-8 -*-
"""M2: 将 3.3.2(突破日坡度) 提升为独立章节 3.7，移到第三章末尾(3.6之后)"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
f = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
lines = io.open(f, encoding='utf-8').read().split('\n')

# 1. 定位 3.3.2 区块（start 到 3.4 前，去掉尾部空行）
start = next(i for i, l in enumerate(lines) if l.startswith('### 3.3.2'))
end_34 = next(i for i, l in enumerate(lines) if l.startswith('### 3.4 '))
content_end = end_34
while content_end > start and lines[content_end-1].strip() == '':
    content_end -= 1
section = lines[start:content_end]

# 2. 删除原区块
del lines[start:content_end]

# 3. 重编号
section = [l.replace('### 3.3.2 ', '### 3.7 ')
             .replace('**3.3.2.1 ', '**3.7.1 ')
             .replace('**3.3.2.2 ', '**3.7.2 ') for l in section]

# 4. 定位第三章末尾的 ---（## 四 之前）
ch4 = next(i for i, l in enumerate(lines) if l.startswith('## 四、操盘计划'))
dash = None
for i in range(ch4-1, 0, -1):
    if lines[i].strip() == '---':
        dash = i
        break

# 5. 在 --- 前插入 section + 一个尾部空行（原 --- 前已有空行作分隔）
lines[dash:dash] = section + ['']

io.open(f, 'w', encoding='utf-8').write('\n'.join(lines))
print('3.3.2->3.7 移动完成。')

# 验证：显示新位置
lines2 = io.open(f, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines2, 1):
    if l.startswith('### 3.7') or l.startswith('### 3.4 ') or l.startswith('### 3.6 '):
        print(f'  L{i}: {l}')
