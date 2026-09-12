# -*- coding: utf-8 -*-
"""清理 §2.8 末尾冗余空行（L2）+ 验证格式"""
import io, sys
sys.stdout.reconfigure(encoding='utf-8')
f = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
s = io.open(f, encoding='utf-8').read()

# L2: 清理冗余空行（3+连续空行 -> 1个）
before = s.count('\n\n\n')
s = s.replace('\n\n\n', '\n\n')
after = s.count('\n\n\n')
io.open(f, 'w', encoding='utf-8').write(s)
print(f'L2 清理: {before}处 -> {after}处 三连续空行')

# 验证：无编号 ### 标题
lines = s.split('\n')
import re
new_unnum = [f'L{i}:{l}' for i, l in enumerate(lines, 1) if l.startswith('### ') and not re.match(r'^### [\d.]+', l)]
print(f'无编号 ### 标题: {len(new_unnum)}')
for x in new_unnum:
    print(' ', x)

# 验证：无行首圈号标题
hdr_circled = [f'L{i}:{l[:30]}' for i, l in enumerate(lines, 1) if re.match(r'^\*\*[①-⑮]', l)]
print(f'行首圈号标题: {len(hdr_circled)}')
