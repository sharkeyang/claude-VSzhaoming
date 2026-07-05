import re

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'r', encoding='utf-8') as f:
    c = f.read()

# Find all section boundaries
ch1_start = c.find('\n## 一、使命与目标')
ch2_start = c.find('\n## 二、做成什么样：工程目标与产出物原型')
ch3_start = c.find('\n## 三、什么时候做：实施步骤')
ch4_start = c.find('\n## 第四章 专题讨论')
ch5_start = c.find('\n## 第五章 待完成零碎工作')
app1_start = c.find('\n## 附录一 三文件分工与偏差检查')
app2_start = c.find('\n## 附录二 启动资产基线')
eof = len(c)

# Extract each section's content
ch1 = c[ch1_start:ch2_start]
ch2_old = c[ch2_start:ch3_start]
ch3_old = c[ch3_start:ch4_start]
ch4 = c[ch4_start:ch5_start]
ch5 = c[ch5_start:app1_start]
app1 = c[app1_start:app2_start]
app2 = c[app2_start:]

# Rename headings
# 二→三, 三→四
ch2_new_header = '\n## 三、做成什么样：工程目标与产出物原型'
ch3_new_header = '\n## 四、什么时候做：实施步骤'

ch2_new = ch2_new_header + ch2_old[ch2_old.index('\n'):]
ch3_new = ch3_new_header + ch3_old[ch3_old.index('\n'):]

# Rename 第四章→二、操盘方法专题讨论 (fix sub-headings too)
ch4 = ch4.replace('## 第四章 专题讨论', '## 二、操盘方法专题讨论')
# Promote ### 专题 to proper ### level (already correct)
# Just ensure they're properly formatted

# Rename 第五章→五、待完成零碎任务 (from 第五章 to 五、)
ch5 = ch5.replace('## 第五章 待完成零碎工作', '## 五、待完成零碎任务')

# Also fix any references to "第五章" in the content itself
ch5 = ch5.replace('第五章 待完成零碎工作', '五、待完成零碎任务')

# Reassemble in new order: ch1, ch4(new ch2), ch2(old becomes ch3), ch3(old becomes ch4), ch5, app1, app2
new_c = ch1 + ch4 + ch2_new + ch3_new + ch5 + app1 + app2

with open(r'd:/@VSwork/VS昭明计划VBA优化/_规则文档/全局_C昭明路线图.md', 'w', encoding='utf-8') as f:
    f.write(new_c)
print('Done')