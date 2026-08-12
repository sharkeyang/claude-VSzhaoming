import re

with open(r'_主文档/MC3.1_研究月基策略.md', 'r', encoding='utf-8') as f:
    content = f.read()

# Find section boundaries in Chapter 3
ch3_start = content.index('## 第三章：月基策略操作规则')
ch3_title_end = content.index('\n', ch3_start)

# Find 3.1 end (after the code block)
sec_31_end = content.index('### 3.2 WXZB退出信号验证')

# Extract sections
sec_31 = content[ch3_title_end + 1:sec_31_end].strip()

# 3.2 WXZB退出信号验证 (硬退出)
sec_32_start = content.index('### 3.2 WXZB退出信号验证')
sec_33_start = content.index('### 3.3 WXZA>0延续性分析')
sec_32 = content[sec_32_start:sec_33_start]

# 3.3 WXZA>0延续性分析 (持仓检查)
sec_34_start = content.index('### 3.4 消极区操作细则')
sec_33 = content[sec_33_start:sec_34_start]

# 3.4 消极区操作细则 (软退出)
sec_35_start = content.index('### 3.5 退出阶段')
sec_34 = content[sec_34_start:sec_35_start]

# 3.5 退出阶段 (最终退出)
sec_36_start = content.index('### 3.6 月基退出预警VBA实现')
sec_35 = content[sec_35_start:sec_36_start]

# 3.6 月基退出预警VBA实现
ch4_start = content.index('## 第四章：三变量框架')
sec_36 = content[sec_36_start:ch4_start]

# New order: 3.1, 3.2(持仓), 3.3(软退出), 3.4(硬退出), 3.5(最终退出), 3.6(VBA)
# Rename:
sec_32_new = sec_32.replace('### 3.2 WXZB退出信号验证', '### 3.4 硬退出：WXZB退出信号验证')
sec_33_new = sec_33.replace('### 3.3 WXZA>0延续性分析', '### 3.2 持仓检查：WXZA>0延续性分析')
sec_34_new = sec_34.replace('### 3.4 消极区操作细则', '### 3.3 软退出：消极区操作细则')
sec_35_new = sec_35.replace('### 3.5 退出阶段', '### 3.5 最终退出：退出阶段')
sec_36_new = sec_36.replace('### 3.6 月基退出预警VBA实现', '### 3.6 月基退出预警VBA实现')

# Rebuild Chapter 3
ch3_body = '\n\n' + sec_31 + '\n\n'
ch3_body += sec_33_new.strip() + '\n\n'  # 持仓检查
ch3_body += sec_34_new.strip() + '\n\n'  # 软退出
ch3_body += sec_32_new.strip() + '\n\n'  # 硬退出
ch3_body += sec_35_new.strip() + '\n\n'  # 最终退出
ch3_body += sec_36_new.strip()           # VBA实现

# Rebuild document
before_ch3 = content[:ch3_title_end + 1]
after_ch3 = content[ch4_start:]

new_content = before_ch3 + ch3_body + '\n\n' + after_ch3

# Clean up
new_content = re.sub(r'\n{4,}', '\n\n\n', new_content)

with open(r'_主文档/MC3.1_研究月基策略.md', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('OK')