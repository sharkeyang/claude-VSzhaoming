# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# 从备份恢复 8.3-8.8
bk = open('____temp/_C7备份_20261017.md', encoding='utf-8').read().split('\n')
s3 = next(i for i,l in enumerate(bk) if l.startswith('### 8.3 '))
s9 = next(i for i,l in enumerate(bk) if l.startswith('### 8.9 '))
sec838 = bk[s3:s9]  # 8.3-8.8 内容
print(f'备份 8.3-8.8: {len(sec838)} 行')

# 当前文件
path = '_主文档/MC3.3_C7日交易规则.md'
cur = open(path, encoding='utf-8').read().split('\n')
c9 = next(i for i,l in enumerate(cur) if l.startswith('### 8.9 '))
print(f'当前 8.9 位置: L{c9+1}')

# 在 8.9 前插入 8.3-8.8
new_lines = cur[:c9] + [''] + sec838 + [''] + cur[c9:]
open(path, 'w', encoding='utf-8').write('\n'.join(new_lines))
print('8.3-8.8 恢复完成')
