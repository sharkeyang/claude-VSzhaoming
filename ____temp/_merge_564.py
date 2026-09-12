# -*- coding: utf-8 -*-
"""融合 C6 §5.6.4 到 MC3.3.5 报告"""
import re

# 读取 MC3.3.5 报告
mc = open('_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md', encoding='utf-8').read()

# 读取 C6 §5.6.4 内容（第1242-1395行）
c6_lines = open('_主文档/MC3.3_C6研究日类微观形态.md', encoding='utf-8').read().split('\n')
# 5.6.4 从第1242行开始（索引1241），到第1395行（索引1394，即"---"前）
sec564 = c6_lines[1241:1395]
sec564_text = '\n'.join(sec564)

# 提取 5.6.4 的正文（去掉标题行，因为要重新编号）
# 标题行是 "#### 5.6.4 DXZC>0各护型介入点的可行性分析（2026-09-06 验证）"
body_lines = [l for l in sec564 if not l.startswith('#### 5.6.4')]
body = '\n'.join(body_lines).strip()

# 构造新章节（作为 MC3.3.5 的"二、各护型介入点"）
new_section = """
## 二、各护型介入点（DXZC>0，融合 C6 §5.6.4）

> **主题：** 针对日类稳定护型（甲乙(DXZA>0)，见 [5.6.3 日类稳定护型](MC3.3_C6研究日类微观形态.md#563-日类稳定护型dxzc0-口径)）及其他护型（己/戊(ZA>0)/丙/乙(ZA<0)/丁/戊(ZA<0)），**分别讨论何种情况会打破稳定、何种情况是好的介入点**。数据：高波池全量（Qic+Qim+Qit，3451 只，DXZC>0 口径）。

""" + body + """

---

"""

# 在 MC3.3.5 的"一 基础矩阵"章节之后插入新章节
# 找到"一 基础矩阵"章节的结束位置（下一个 "## " 之前）
lines = mc.split('\n')
insert_idx = None
for i, l in enumerate(lines):
    if l.startswith('## 二、等1'):
        insert_idx = i
        break

if insert_idx is None:
    print('ERROR: 未找到"## 二、等1"位置')
else:
    # 在"## 二、等1"之前插入新章节
    new_lines = lines[:insert_idx] + new_section.split('\n') + lines[insert_idx:]
    mc_new = '\n'.join(new_lines)

    # 调整章节编号：原"二~八"顺延为"三~九"
    # 原"二、等1"→"三、等1"，"三、等3"→"四、等3"，"四、等2"→"五、等2"
    # "五、等5"→"六、等5"，"六、等7"→"七、等7"，"七、等6"→"八、等6"，"八、综合结论"→"九、综合结论"
    renames = [
        ('## 二、等1', '## 三、等1'),
        ('## 三、等3', '## 四、等3'),
        ('## 四、等2', '## 五、等2'),
        ('## 五、等5', '## 六、等5'),
        ('## 六、等7', '## 七、等7'),
        ('## 七、等6', '## 八、等6'),
        ('## 八、综合结论', '## 九、综合结论'),
    ]
    for old, new in renames:
        mc_new = mc_new.replace(old, new)

    open('_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md', 'w', encoding='utf-8').write(mc_new)
    print('融合完成，新报告行数:', mc_new.count('\n'))
