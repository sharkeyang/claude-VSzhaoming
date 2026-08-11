# -*- coding: utf-8 -*-
"""合并 MC3.3 到 MC3.3.2：以 MC3.3.2 为根本，追加 + 前置"""
import re, sys
sys.stdout.reconfigure(encoding='utf-8')

base = open('_主文档/MC3.3.2_研究日级别探索路径.md', encoding='utf-8').read()
src = open('_主文档/MC3.3_研究日冲策略.md', encoding='utf-8').read()

# ========== 1. 提取 MC3.3 §1.1 + §1.2（前置到开头） ==========
s11 = '### 1.1 策略定位'
s13 = '### 1.3 待研究问题'
intro_block = src[src.find(s11):src.find(s13)]
# 重编号 1.1 → 〇.1, 1.2 → 〇.2
intro_block = intro_block.replace('### 1.1 策略定位', '## 〇、日冲策略总览\n\n### 〇.1 策略定位')
intro_block = intro_block.replace('### 1.2 现状与瓶颈', '### 〇.2 现状与瓶颈')

# ========== 2. 提取 MC3.3 §2-§5 并重编号 ==========
def extract_section(marker, next_marker):
    s = src.find(marker)
    e = src.find(next_marker, s)
    return src[s:e]

# §2 日周联动 → 十三
s2 = extract_section('## 二、日周联动', '## 三、日级别执行框架')
s2 = s2.replace('## 二、日周联动', '## 十三、日周联动')
s2 = s2.replace('### 2.1', '### 十三.1')
s2 = s2.replace('### 2.2', '### 十三.2')
s2 = s2.replace('### 2.3', '### 十三.3')
s2 = s2.replace('### 2.4', '### 十三.4')

# §3 日级别执行框架 → 十四
s3 = extract_section('## 三、日级别执行框架', '## 四、按形态探索')
s3 = s3.replace('## 三、日级别执行框架', '## 十四、日级别执行框架')
s3 = s3.replace('### 3.1', '### 十四.1')
s3 = s3.replace('#### 3.1.1', '#### 十四.1.1')
s3 = s3.replace('#### 3.1.2', '#### 十四.1.2')
s3 = s3.replace('#### 3.1.3', '#### 十四.1.3')
s3 = s3.replace('#### 3.1.4', '#### 十四.1.4')
s3 = s3.replace('#### 3.1.5', '#### 十四.1.5')

# §4 按形态探索 → 十五
s4 = extract_section('## 四、按形态探索', '## 五、日层联动')
s4 = s4.replace('## 四、按形态探索', '## 十五、按形态探索')
# 4.x → 十五.x，注意 4.1~4.6 但避免误替换 十四
s4 = s4.replace('### 4.1 ', '### 十五.1 ')
s4 = s4.replace('### 4.2 ', '### 十五.2 ')
s4 = s4.replace('### 4.3 ', '### 十五.3 ')
s4 = s4.replace('### 4.4 ', '### 十五.4 ')
s4 = s4.replace('### 4.5 ', '### 十五.5 ')
s4 = s4.replace('### 4.6 ', '### 十五.6 ')

# §5 日层联动 → 十六
s5 = extract_section('## 五、日层联动', '## 六、')
# 如果没找到六，就用文件末尾
if not s5 or s5 == '':
    s5 = src[src.find('## 五、日层联动'):]
s5 = s5.replace('## 五、日层联动', '## 十六、日层联动')
s5 = s5.replace('#### 5.1', '#### 十六.1')
s5 = s5.replace('#### 5.2', '#### 十六.2')
s5 = s5.replace('#### 5.3', '#### 十六.3')
s5 = s5.replace('#### 5.4', '#### 十六.4')
s5 = s5.replace('#### 5.5', '#### 十六.5')

# ========== 3. 组装 ==========
# 前置 §〇 到开头（在 header 后、进度板前）
marker_progress = '| 探索路径 | 进度 | 完成 |'
new_base = base.replace(marker_progress, intro_block + '\n---\n\n' + marker_progress)

# 追加 §十三~§十六 到末尾
new_base = new_base.rstrip() + '\n\n---\n\n' + s2 + '\n\n---\n\n' + s3 + '\n\n---\n\n' + s4 + '\n\n---\n\n' + s5

open('_主文档/MC3.3.2_研究日级别探索路径.md', 'w', encoding='utf-8').write(new_base)
print('合并完成')
print(f'原大小: {len(base)} → 新大小: {len(new_base)}')