# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
with open(path, encoding='utf-8') as f:
    lines = f.read().split('\n')

# 定位
s864 = next(i for i,l in enumerate(lines) if l.startswith('#### 8.6.4 '))
s865 = next(i for i,l in enumerate(lines) if l.startswith('#### 8.6.5 '))
s7 = next(i for i,l in enumerate(lines) if l.startswith('### 8.7 '))
s9 = next(i for i,l in enumerate(lines) if l.startswith('## 九'))
print(f'8.6.4:{s864+1} 8.6.5:{s865+1} 8.7:{s7+1} 九:{s9+1}')

# 提取 8.6.4 和 8.6.5 内容
sec864 = lines[s864:s865]   # 8.6.4
sec865 = lines[s865:s7]     # 8.6.5 (到 8.7 前)

# 重编号 8.6.4->8.7.5, 8.6.5->8.7.6
def renum(sec, old, new):
    out=[]
    for l in sec:
        if l.startswith(f'#### {old} '):
            l = l.replace(f'#### {old} ', f'#### {new} ', 1)
        out.append(l)
    return out
sec864_new = renum(sec864, '8.6.4', '8.7.5')
sec865_new = renum(sec865, '8.6.5', '8.7.6')

# 8.7 原有内容: 8.7.1-8.7.4
sec87 = lines[s7:s9]
# 重编号 8.7.3->8.7.7, 8.7.4->8.7.8
def renum87(sec):
    out=[]
    for l in sec:
        if l.startswith('**8.7.3 '):
            l = l.replace('**8.7.3 ', '**8.7.7 ', 1)
        elif l.startswith('**8.7.4 '):
            l = l.replace('**8.7.4 ', '**8.7.8 ', 1)
        out.append(l)
    return out
sec87_new = renum87(sec87)

# 组装新文件
# 8.6 删除 8.6.4/8.6.5 (只剩 8.6.1-8.6.3)
# 8.7 = 原8.7.1-8.7.4(重编号) + 8.7.5(原8.6.4) + 8.7.6(原8.6.5)
new_lines = lines[:s864] + sec87_new + [''] + sec864_new + [''] + sec865_new + lines[s9:]
open(path, 'w', encoding='utf-8').write('\n'.join(new_lines))
print('8.6.4/8.6.5 移入 8.7 完成')
