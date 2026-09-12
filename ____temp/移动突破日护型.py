# -*- coding: utf-8 -*-
"""主题归位1: 将 2.4.2.9/2.4.2.10(突破日护型) 移到 §3.7，作为 3.7.1/3.7.2，原3.7.1/3.7.2顺延为3.7.3/3.7.4"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
f = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
lines = io.open(f, encoding='utf-8').read().split('\n')

# 1. 提取 2.4.2.9 到 2.4.2.11 前的内容（L442-506，0-indexed 441-505）
start = next(i for i, l in enumerate(lines) if l.startswith('**2.4.2.9 '))
end_11 = next(i for i, l in enumerate(lines) if l.startswith('**2.4.2.11 '))
# 去掉尾部空行
content_end = end_11
while content_end > start and lines[content_end-1].strip() == '':
    content_end -= 1
section = lines[start:content_end]

# 2. 删除原位置
del lines[start:content_end]

# 3. 重编号：2.4.2.9 -> 3.7.1, 2.4.2.10 -> 3.7.2, 2.4.2.10.x -> 3.7.2.x
section = [l.replace('**2.4.2.9 ', '**3.7.1 ')
             .replace('**2.4.2.10.1 ', '**3.7.2.1 ')
             .replace('**2.4.2.10.2 ', '**3.7.2.2 ')
             .replace('**2.4.2.10.3 ', '**3.7.2.3 ')
             .replace('**2.4.2.10 ', '**3.7.2 ') for l in section]

# 4. 定位 §3.7 的 3.7.1 起始（在删除后行号已变，重新找）
sec37 = next(i for i, l in enumerate(lines) if l.startswith('### 3.7 '))
# 找 3.7.1 起始（在 sec37 之后）
first_sub = next(i for i in range(sec37+1, len(lines)) if lines[i].startswith('**3.7.1 '))
# 在 first_sub 前插入 section + 空行
lines[first_sub:first_sub] = section + ['']

# 5. 原 3.7.1/3.7.2 顺延为 3.7.3/3.7.4
for i, l in enumerate(lines):
    if l.startswith('**3.7.1 ') and i > first_sub:
        lines[i] = l.replace('**3.7.1 ', '**3.7.3 ', 1)
    elif l.startswith('**3.7.2 ') and i > first_sub:
        lines[i] = l.replace('**3.7.2 ', '**3.7.4 ', 1)

io.open(f, 'w', encoding='utf-8').write('\n'.join(lines))
print('2.4.2.9/2.4.2.10 -> 3.7.1/3.7.2 移动完成')

# 验证
lines2 = io.open(f, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines2, 1):
    if re.match(r'^\*\*3\.7\.\d ', l):
        print(f'  L{i}: {l[:50]}')