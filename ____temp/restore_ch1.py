# -*- coding: utf-8 -*-
import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

# 读取efcdb8f版本的MC3.3.1第一章内容
with open('____temp/MC3.3.1_efcdb8f.md', 'r', encoding='utf-8') as f:
    ch1 = f.read()
ch1_start = ch1.index('## 第一章 必赢算法论证：DXZE+DXZC')
ch1_content = ch1[ch1_start:]

# 读取当前MC3.3
path = '_主文档/MC3.3_研究日冲策略.md'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到当前第一章标题位置
ch1_pos = content.index('## 第一章 日类必赢算法V1：DXZE+DXZC')
# 找到第二章标题位置
ch2_pos = content.index('## 第二章 日类基本模型验证：DXZC+DXAB')

# 替换第一章标题（保留V1标题），并插入完整内容
new_ch1 = '## 第一章 日类必赢算法V1：DXZE+DXZC\n\n' + ch1_content[ch1_content.index('\n'):]

# 删除旧的第一章（标题到第二章之间）
content = content[:ch1_pos] + new_ch1 + '\n\n' + content[ch2_pos:]

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)
print('done')