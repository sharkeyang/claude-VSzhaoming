# -*- coding: utf-8 -*-
"""方案X重构 - 4.3.2部分：
1. 4.3.2标题改为'两级别综合建议'
2. ④行 → 4.3.2.1子节标题
3. 第一段→范围级别, 第二段→等级级别, 两段式→两级别, 去掉⑤⑥编号
"""
import io

path = r'd:\@VSwork\VS昭明计划VBA优化\_主文档\MC3.3_C2日DXZC+DXAB全维度分析.md'
with io.open(path, encoding='utf-8') as f:
    lines = f.readlines()

def find(anchor, start=0):
    for i in range(start, len(lines)):
        if anchor in lines[i]:
            return i
    return -1

# 1. 4.3.2标题
i432 = find('#### 4.3.2 四维参数分工表')
assert i432 != -1
lines[i432] = '#### 4.3.2 两级别综合建议（范围级别 vs 等级级别）\n'

# 2. ④ 行 → 4.3.2.1 子节标题
i_d4 = find('**④ 综合建议：两段式（平衡风险与收益）**')
assert i_d4 != -1
lines[i_d4] = '#### 4.3.2.1 两级别综合建议（范围级别 vs 等级级别）\n'

# 3. 第一段 → 范围级别
i_d1 = find('**第一段 · 范围判定（能不能做）——DXCD + DXZC + DXAB：**')
assert i_d1 != -1
lines[i_d1] = '**范围级别（能不能做）——DXCD + DXZC + DXAB：**\n'

# 4. 第二段 → 等级级别
i_d2 = find('**第二段 · 等级划分（做得多好）——DXEF（DXEF 与 DXZE 的关系）：**')
assert i_d2 != -1
lines[i_d2] = '**等级级别（做得多好）——DXEF（DXEF 与 DXZE 的关系）：**\n'

# 5. 三条铁律融入两段式 → 两级别
i_tl = find('**三条铁律融入两段式：**')
if i_tl != -1:
    lines[i_tl] = '**三条铁律融入两级别：**\n'

# 6. ⑤ 结论 → 去掉编号，两段式→两级别
i_c5 = find('**⑤ 结论：')
if i_c5 != -1:
    lines[i_c5] = lines[i_c5].replace('**⑤ 结论：日类操作范围采用**两段式**', '**结论：日类操作范围采用**两级别**')

# 7. ⑥ 融合验证 → 去掉⑥编号
i_c6 = find('**⑥ 融合后范围全量验证')
if i_c6 != -1:
    lines[i_c6] = lines[i_c6].replace('**⑥ 融合后范围全量验证', '**融合后范围全量验证')

with io.open(path, 'w', encoding='utf-8') as f:
    f.writelines(lines)
print('第一步完成')
