# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding='utf-8')
path = '_主文档/MC3.1_研究月基策略.md'
with open(path, encoding='utf-8') as f:
    content = f.read()

# 1. 把 '**① 宽范围（确定结论，依据护型 × WXZC）：**' 改为 '#### 4.1.3.1 宽范围表（护型 × WXZC）'
old_1 = '**① 宽范围（确定结论，依据护型 × WXZC）：**'
new_1 = '#### 4.1.3.1 宽范围表（护型 × WXZC）'
assert old_1 in content, '①未找到'
content = content.replace(old_1, new_1)

# 2. 移除禁区范围注记，改为独立 4.1.3.2
# 找到禁区范围注记的起止
start_marker = '> **⚠️ 禁区范围（做空主要区域，坚决不介入）：**'
end_marker = '**② WXCD 优选等级（在宽范围内优选，参考祖训）：**'
start_idx = content.find(start_marker)
end_idx = content.find(end_marker)
assert start_idx != -1, '禁区范围注记起始未找到'
assert end_idx != -1, '②未找到'

# 提取禁区范围注记内容（用于 4.1.3.2）
forbidden_note = content[start_idx:end_idx].strip()

# 移除禁区范围注记（保留 ②）
content = content[:start_idx] + content[end_idx:]

# 3. 在 ② WXCD 优选等级 之前插入 4.1.3.2 禁区范围 和 4.1.3.3 剩余范围
insert_before = '**② WXCD 优选等级（在宽范围内优选，参考祖训）：**'
new_sections = '''#### 4.1.3.2 禁区范围（WXZC<0 + 丙丁戊）

> **定义：`WXZC<0 + WXAB=丙丁戊(WXZA<0)` 是周类禁区范围——坚决不介入。**
>
> **逻辑：** 周线 DJC 之下（WXZC<0）+ 差护型（丙丁戊，WXZA<0）——趋势向下 + 差护型，是做空的主要区域。

**禁区范围（做空主要区域，坚决不介入）：** **WXZC<0 且 WXAB 护型为 丙丁戊(WXZA<0)** 是**禁区范围**——这是**做空的主要区域**，**坚决不要介入**。除此以外的**任意区域**（WXZC>0 任意护型、WXZC<0 但护型为 甲乙己/戊(ZA>0)/乙(ZA≤0)）都**或多或少有机会**——虽然在禁区范围以外的区域介入后**也有可能亏钱**，但只要**回避禁区范围，就能回避最危险的区域**。**注意：不是说突破了禁区范围就一定要介入，而是禁区范围坚决不要介入。** 此禁区范围与"**不下破 WJA 不退出**"形成**镜面映射**（WJA 是趋势生命线，跌破即进入危险区）。**可以观察图形：所有的主降级别的下跌都是在禁区范围完成的。**

> **⚠️ 角色判定原则：** 操作判定基于**转移矩阵（转好概率/转坏概率）+ 持续时间 + 冲高期望（HR）** 综合判定（详见 C3 §3.3、§3.5.2），**不是**由本周涨幅判定。完整论证见 C3 §3.5.2。

**与日类禁区范围对应：** 日类禁区范围 = **DXZE≤0 + DXCD=下/忑**；周类禁区范围 = **WXZC<0 + WXAB=丙丁戊(WXZA<0)**。对应关系：周类 WXZC<0 ↔ 日类 DXZE≤0（趋势向下）；周类 WXAB=丙丁戊 ↔ 日类 DXCD=下/忑（差护级）。

#### 4.1.3.3 剩余范围（WXZC>0 + 丙丁戊）

> **定义：剩余范围 = 全部 - 宽范围 - 禁区范围 = WXZC>0 + 丙丁戊（范围外但非禁区）。**
>
> **逻辑：** 宽范围表"范围外"（丁/戊(ZA≤0)/丙）中，WXZC>0 的部分既不在宽范围（范围内护型）也不在禁区范围（WXZC<0 + 丙丁戊），是剩余范围。

**剩余范围性质：** 剩余范围 = WXZC>0 + 丙丁戊（范围外但非禁区）——**范围外护型（丙丁戊）在 WXZC>0 时仍属范围外**（宽范围表明确"范围外"回避/退出），**不介入**。它与禁区范围（WXZC<0 + 丙丁戊）在 WXZC 维度上互斥，共同覆盖全部丙丁戊护型。

**② WXCD 优选等级（在宽范围内优选，参考祖训）：**'''
assert insert_before in content, '插入位置未找到'
content = content.replace(insert_before, new_sections, 1)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('已重构 4.1.3：添加 4.1.3.2 禁区范围 和 4.1.3.3 剩余范围')
