# -*- coding: utf-8 -*-
"""§4.8 拆分为 4.8定型框架 / 4.9周级别 / 4.10微观验证"""
import io, re, sys
sys.stdout.reconfigure(encoding='utf-8')
f = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
lines = io.open(f, encoding='utf-8').read().split('\n')

# 1. 插入章节标题
# 4.9 周级别映射：在 4.8.9 前插入
idx_49 = next(i for i, l in enumerate(lines) if l.startswith('**4.8.9 '))
lines.insert(idx_49, '### 4.9 周级别映射：日级别分析是否适用于周类（2026-09-08 验证）')
lines.insert(idx_49+1, '')
# 4.10 微观指标验证：在 4.8.11 前插入（注意行号已变，重新找）
idx_410 = next(i for i, l in enumerate(lines) if l.startswith('**4.8.11 '))
lines.insert(idx_410, '### 4.10 微观指标验证：操作区域内各微观指标的获利性（2026-09-08 验证）')
lines.insert(idx_410+1, '')

# 2. 重编号 4.8.9-4.8.10 -> 4.9.1-4.9.2（含子级 4.8.10.x -> 4.9.2.x）
# 3. 重编号 4.8.11-4.8.17 -> 4.10.1-4.10.7（含子级）
# 注意顺序：先处理 4.8.10.x（更深的），再 4.8.10，避免 4.8.10 被 4.8.1 误伤
# 用正则精确匹配 **4.8.N 或 **4.8.N.M
def renum(lines, old_n, new_n):
    # 处理子级 old_n.M -> new_n.M
    for i, l in enumerate(lines):
        lines[i] = re.sub(rf'^\*\*4\.8\.{old_n}\.(\d+) ', rf'**4.{new_n}.\1 ', l)
    # 处理顶层 old_n -> new_n
    for i, l in enumerate(lines):
        lines[i] = re.sub(rf'^\*\*4\.8\.{old_n} ', rf'**4.{new_n} ', l)

# 4.8.9 -> 4.9.1
renum(lines, 9, '9.1')
# 4.8.10 -> 4.9.2
renum(lines, 10, '9.2')
# 4.8.11 -> 4.10.1
renum(lines, 11, '10.1')
# 4.8.12 -> 4.10.2
renum(lines, 12, '10.2')
# 4.8.13 -> 4.10.3
renum(lines, 13, '10.3')
# 4.8.14 -> 4.10.4
renum(lines, 14, '10.4')
# 4.8.15 -> 4.10.5
renum(lines, 15, '10.5')
# 4.8.16 -> 4.10.6
renum(lines, 16, '10.6')
# 4.8.17 -> 4.10.7
renum(lines, 17, '10.7')

io.open(f, 'w', encoding='utf-8').write('\n'.join(lines))
print('§4.8 拆分完成')

# 验证
lines2 = io.open(f, encoding='utf-8').read().split('\n')
for i, l in enumerate(lines2, 1):
    if l.startswith('### 4.8 ') or l.startswith('### 4.9 ') or l.startswith('### 4.10 ') or re.match(r'^\*\*4\.(9|10)\.\d+ ', l):
        print(f'  L{i}: {l[:55]}')