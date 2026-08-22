import re

with open('_主文档/MC3.3.4_研究日冲策略探索形态.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove orphan # lines
content = content.replace('\n#\n###', '\n###')
content = content.replace('\n#\n####', '\n####')

# 2. Fix 2.1.4 heading level
content = content.replace('### 2.1.4 个体差异分析', '#### 2.1.4 个体差异分析')

# 3. Fix 2.5 sub-section numbering (sequential 1-8)
s_25 = content.find('### 2.5 子专题：DXAB护型转移研究')
e_25 = content.find('## 附录', s_25)
sec_25 = content[s_25:e_25]
headings = []
for m in re.finditer(r'^#### 2\.5\.[0-9] (.*)', sec_25, re.MULTILINE):
    headings.append(m.group())
for i, full in enumerate(headings):
    new_num = i + 1
    text = full.split(' ', 2)[2]
    new_full = f'#### 2.5.{new_num} {text}'
    sec_25 = sec_25.replace(full, new_full)
content = content[:s_25] + sec_25 + content[e_25:]

# 4. Fix table format (broken 护型转移概率 table)
old_t = '| 当前护型 | 维持率 | 主要转移方向 |\n|:---\n### 2.5 深入探索方向'
new_t = '| 当前护型 | 维持率 | 主要转移方向 |\n|:-------:|:------:|:-----------|\n| **甲** | 83.2% | →乙10.1%（仍正交） |\n| **乙** | 84.4% | →丙13.9%（转负交） |\n| 丙 | 34.4% | →丁43.0%, →乙22.6%（转正交） |\n| **丁** | 84.5% | →戊9.4% |\n| **戊** | 86.2% | →己12.3% |\n| 己 | 35.9% | →甲42.9%（转正交）, →戊21.2% |\n\n#### 2.5.1 已验证的结论（详见 §一）'
content = content.replace(old_t, new_t)

# 5. Fix 6.12 broken table
old_612 = '| 窗口 | 均阳柱率 | 总样本 | 最佳参数 | 说明 |\n|:\n### 2.6 子专题：DXAB与DXZC分段'
new_612 = '| 窗口 | 均阳柱率 | 总样本 | 最佳参数 | 说明 |\n|:---:|:--------:|:------:|:---------|:-----|\n| **5** | **12.2%** | 1,517 | DS顶JA=12, 波动>=1%, DJB | ✅ 有效，样本充足 |\n| 10 | 16.7% | 272 | DS顶JA=5~8, DJB | ⚠️ 样本偏少 |\n| 15/20 | -- | <50 | 样本不足 | ❌ 不可靠 |\n\n**结论：**\n- 窄管条件确实有效，阳柱率从基准~4-8%提升到**12.2~16.7%**（+4~8pp）\n- **DS顶JA阈值越大越好**（12优于5），说明"窄管"的初始定义过严\n- 均幅涨/均幅高数据存在列偏移bug（显示-80%~-118%），**优先级较低，暂不处理**\n\n---\n\n### 2.6 子专题：DXAB与DXZC分段'
content = content.replace(old_612, new_612)

# 6. Update dimension 8 content
old_d8 = '> **核心发现：护型本身是DXZA持续时长的主导因素，外部条件（DXCD/DXZC/DXEF）的影响极小（<5%）。**'
new_d8 = '> **核心发现：护型本身是DXZA持续时长的主导因素——强势护型会持续强势，弱势护型会持续弱势。外部条件（DXCD/DXZC/DXEF）的影响极小（<5%）。**\n>\n> **分析意义：** 这个结论的实战价值在于——**护型本身已经包含了趋势持续性的信息，不需要额外看其他条件。** 己出现=强势会持续（均6~7天），丙出现=弱势会持续（均6~7天），外部条件改变不了这个格局。唯一的例外是DXZC>0可缩短负ZA持续，但幅度有限（7%）。'
content = content.replace(old_d8, new_d8)

# 7. Fix 2.6.1.1 heading level
content = content.replace('### 2.6.1.1 细分：乙的转移概率与DXZA的依赖关系', '##### 2.6.1.1 细分：乙的转移概率与DXZA的依赖关系')

# 8. Reorder sections: extract §四 §五 §六 and appendix, put in correct order
# Current order in backup: §一 → §二(2.0~2.7) → 附录 → §四 → §五 → §六
# Desired order: §一 → §二 → §四 → §五 → §六 → 附录

s_1 = content.find('## 一、日冲策略总览')
s_2 = content.find('## 二、DXZC+DXAB')
s_app = content.find('## 附录：DXZA全周期分类')
s_4 = content.find('## 四、基本条件')
s_5 = content.find('## 五、日周联动')
s_6 = content.find('## 六、按形态探索')

# Extract each section
sec_1 = content[s_1:s_2]
sec_2 = content[s_2:s_app]
sec_app = content[s_app:s_4]
sec_4 = content[s_4:s_5]
sec_5 = content[s_5:s_6]
sec_6 = content[s_6:]

# Rebuild in correct order
content = sec_1 + sec_2 + sec_4 + sec_5 + sec_6 + '\n\n' + sec_app

# 9. Update TOC
old_toc = '## 目录\n\n- [一、日冲策略总览](#一日冲策略总览)\n    - [1.1 策略定位](#11-策略定位)\n    - [1.2 现状与瓶颈](#12-现状与瓶颈)\n    - [1.3 下日冲高概率结论](#13-下日冲高概率结论)\n- [二、DXZC+DXAB 最小模型验证（全量数据结论）](#二dxzcdxab-最小模型验证)\n    - [2.0 核心准则（全量数据验证）](#20-核心准则)\n    - [2.1 核心验证结果](#21-核心验证结果)\n    - [2.2 子专题：DXAB特征统计数据](#22-子专题dxab特征统计数据)\n    - [2.6 子专题：DXAB与DXZC分段](#26-子专题dxab与dxzc分段)\n    - [2.7 子专题：DXAB与DXCD协同效应](#27-子专题dxab与dxcd协同效应)\n    - [2.5 子专题：DXAB护型转移研究](#25-子专题dxab护型转移研究)\n- [附录：DXZA全周期分类 — 22种状态完整报告](#附录dxza全周期分类-22种状态完整报告)\n- [四、基本条件：日类什么位置会有阳柱](#四基本条件日类什么位置会有阳柱)\n- [五、日周联动（周←→日映射）](#五日周联动)\n    - [5.1 日周结合：先周后日操作框架](#51-日周结合先周后日操作框架)\n    - [5.2 周←→日映射关系](#52-周日映射关系)\n    - [5.3 月基四域→日冲5层 完整映射](#53-月基四域日冲5层-完整映射)\n    - [5.4 日冲5层操作列表](#54-日冲5层操作列表)\n    - [5.5 为什么G级需要单独处理为"傻吃屎豆"](#55-为什么g级需要单独处理为傻吃屎豆)\n- [六、按形态探索](#六按形态探索)'
new_toc = '## 目录\n\n- [一、日冲策略总览](#一日冲策略总览)\n    - [1.1 策略定位](#11-策略定位)\n    - [1.2 现状与瓶颈](#12-现状与瓶颈)\n    - [1.3 下日冲高概率结论](#13-下日冲高概率结论)\n- [二、DXZC+DXAB 最小模型验证（全量数据结论）](#二dxzcdxab-最小模型验证)\n    - [2.0 核心准则（全量数据验证）](#20-核心准则)\n    - [2.1 核心验证结果](#21-核心验证结果)\n    - [2.2 子专题：DXAB特征统计数据](#22-子专题dxab特征统计数据)\n    - [2.5 子专题：DXAB护型转移研究](#25-子专题dxab护型转移研究)\n    - [2.6 子专题：DXAB与DXZC分段](#26-子专题dxab与dxzc分段)\n    - [2.7 子专题：DXAB与DXCD协同效应](#27-子专题dxab与dxcd协同效应)\n- [四、基本条件：日类什么位置会有阳柱](#四基本条件日类什么位置会有阳柱)\n- [五、日周联动（周←→日映射）](#五日周联动)\n    - [5.1 日周结合：先周后日操作框架](#51-日周结合先周后日操作框架)\n    - [5.2 周←→日映射关系](#52-周日映射关系)\n    - [5.3 月基四域→日冲5层 完整映射](#53-月基四域日冲5层-完整映射)\n    - [5.4 日冲5层操作列表](#54-日冲5层操作列表)\n    - [5.5 为什么G级需要单独处理为"傻吃屎豆"](#55-为什么g级需要单独处理为傻吃屎豆)\n- [六、按形态探索](#六按形态探索)\n- [附录：DXZA全周期分类 — 22种状态完整报告](#附录dxza全周期分类-22种状态完整报告)'
content = content.replace(old_toc, new_toc)

with open('_主文档/MC3.3.4_研究日冲策略探索形态.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('All fixes applied successfully')