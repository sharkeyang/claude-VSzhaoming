# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
with open(path, encoding='utf-8') as f:
    lines = f.read().split('\n')

# 定位
s5 = next(i for i,l in enumerate(lines) if l.startswith('### 8.5 '))
s6 = next(i for i,l in enumerate(lines) if l.startswith('### 8.6 '))
s7 = next(i for i,l in enumerate(lines) if l.startswith('### 8.7 '))
s9 = next(i for i,l in enumerate(lines) if l.startswith('## 九'))
print(f'8.5:{s5+1} 8.6:{s6+1} 8.7:{s7+1} 九:{s9+1}')

# 提取 8.6(操作规则) 和 8.7(最小阻力动向) 内容
sec86 = lines[s6:s7]   # 操作规则(含标题)
sec87 = lines[s7:s9]   # 最小阻力动向(含标题)

# 重编号
# 8.6(操作规则) -> 8.7: 子节 8.6.x -> 8.7.x
def renum_86(sec):
    out=[]
    for l in sec:
        if l.startswith('### 8.6 '):
            l = l.replace('### 8.6 ', '### 8.7 ', 1)
        elif l.startswith('#### 8.6.'):
            m = re.match(r'#### 8\.6\.(\d+)', l)
            if m:
                l = l.replace(f'#### 8.6.{m.group(1)}', f'#### 8.7.{m.group(1)}', 1)
        out.append(l)
    return out
# 8.7(最小阻力动向) -> 8.6: 子节 8.7.x -> 8.6.x
def renum_87(sec):
    out=[]
    for l in sec:
        if l.startswith('### 8.7 '):
            l = l.replace('### 8.7 ', '### 8.6 ', 1)
        elif l.startswith('**8.7.'):
            m = re.match(r'\*\*8\.7\.(\d+)', l)
            if m:
                l = l.replace(f'**8.7.{m.group(1)}', f'**8.6.{m.group(1)}', 1)
        elif l.startswith('#### 8.7.'):
            m = re.match(r'#### 8\.7\.(\d+)', l)
            if m:
                l = l.replace(f'#### 8.7.{m.group(1)}', f'#### 8.6.{m.group(1)}', 1)
        out.append(l)
    return out

sec86_new = renum_86(sec86)  # 操作规则 -> 8.7
sec87_new = renum_87(sec87)  # 最小阻力动向 -> 8.6

# 组装: 8.5 + 8.6(最小阻力动向) + 8.7(操作规则) + 九
new_lines = lines[:s6] + sec87_new + [''] + sec86_new + lines[s9:]
open(path, 'w', encoding='utf-8').write('\n'.join(new_lines))
print('8.6/8.7 对调完成')
