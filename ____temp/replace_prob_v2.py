"""替换§2.10概率表为正确顺序"""
with open('_主文档/MC3.2_研究周冲策略.md', 'r', encoding='utf-8') as f:
    content = f.read()

# 读取新表
with open('____temp/new_prob_table.txt', 'r', encoding='utf-8') as f:
    new_table = f.read().strip()

# 找到旧表范围
start_marker = '条件                        全量     Qd      Qe     Qif     Qic    Qimit    Qin'
# 从该行往前找 ```
# 从该行往后找 ``` 结束，再找 footnotes
start_idx = content.find(start_marker)
# 回溯到 ``` 开头
code_start = content.rfind('```', 0, start_idx)
# 找下一个 ``` 结束
code_end = content.find('```', start_idx) + 3

# 脚注范围：从 ``` 之后到 ### 全量条件概率表的发现
section_end = content.find('### 全量条件概率表的发现', code_end)

# 构建新内容
new_section = f'```\n{new_table}\n```\n\n> 注：金+多长+升排+非孕+盈高 和 金最优(全部) 为100% — 真均幅24.80%，全部样本HR≥3%，非数据问题。<br>\n> 中证小盘 = 中证1000(1000只) + 中证2000(1958只)，各条件差异<1%，合并为同类。<br>\n> **关于样本量：** 所有策略均基于同一个全量数据集（7463只×4229602周）统计。样本量不同 = 每个条件的命中次数不同（条件越严、命中越少），不是找了不同的数据集。<br>\n> **金最优(全部)定义：** 金+升排+非孕+盈高+龙猪/管（宽匹配，不限WXAB）。\n'

content = content[:code_start] + new_section + content[section_end:]

with open('_主文档/MC3.2_研究周冲策略.md', 'w', encoding='utf-8') as f:
    f.write(content)
print('替换完成')