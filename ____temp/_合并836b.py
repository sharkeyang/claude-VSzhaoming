# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
with open(path, encoding='utf-8') as f:
    lines = f.read().split('\n')

# 定位
s3 = next(i for i,l in enumerate(lines) if l.startswith('### 8.3 '))
s4 = next(i for i,l in enumerate(lines) if l.startswith('### 8.4 '))
s5 = next(i for i,l in enumerate(lines) if l.startswith('### 8.5 '))
s6 = next(i for i,l in enumerate(lines) if l.startswith('### 8.6 '))
s7 = next(i for i,l in enumerate(lines) if l.startswith('### 8.7 '))
print(f'8.3:{s3+1} 8.4:{s4+1} 8.5:{s5+1} 8.6:{s6+1} 8.7:{s7+1}')

# 提取各节内容（去掉标题行）
sec83 = lines[s3+1:s4]   # WXAB正交
sec84 = lines[s4+1:s5]   # 主升条件探索
sec85 = lines[s5+1:s6]   # 主升区域表现
sec86 = lines[s6+1:s7]   # 主升定稿

# 8.4 内容拆分: 8.4.1-8.4.6(前置) -> 8.3.2.x, 8.4.7-8.4.11(条件) -> 8.3.3.x
sec84_pre = []
sec84_cond = []
in_cond = False
for l in sec84:
    m = re.match(r'^(\*{1,2}|#{3,5}) 8\.4\.(\d+)', l)
    if m:
        n = int(m.group(2))
        if n >= 7:
            in_cond = True
            l = l.replace(f'8.4.{n}', f'8.3.3.{n-6}', 1)
            sec84_cond.append(l)
        else:
            l = l.replace(f'8.4.{n}', f'8.3.2.{n}', 1)
            sec84_pre.append(l)
    else:
        if in_cond:
            sec84_cond.append(l)
        else:
            sec84_pre.append(l)

# 8.5 -> 8.3.4.x
def renum(sec, old, new):
    out=[]
    for l in sec:
        m = re.match(r'^(\*{1,2}|#{3,5}) ' + re.escape(old) + r'\.(\d+)', l)
        if m:
            n=int(m.group(2))
            l=l.replace(f'{old}.{n}', f'{new}.{n}', 1)
        out.append(l)
    return out
sec85_new = renum(sec85, '8.5', '8.3.4')
sec86_new = renum(sec86, '8.6', '8.3.5')

# 组装新 8.3 主升研究
new_83 = ['### 8.3 🎯 主升研究（合并 8.3-8.6，2026-10-17）']
new_83 += ['', '#### 8.3.1 主升驱动力：WXAB 正交（2026-09-26 用户定稿，重要课题）'] + sec83
new_83 += ['', '#### 8.3.2 主升前置状态（原 8.4.1-8.4.6）'] + sec84_pre
new_83 += ['', '#### 8.3.3 主升条件探索（原 8.4.7-8.4.11）'] + sec84_cond
new_83 += ['', '#### 8.3.4 主升区域表现（原 8.5）'] + sec85_new
new_83 += ['', '#### 8.3.5 主升定稿与深化（原 8.6）'] + sec86_new

# 组装新文件: 8.3主升研究 + 原8.7(保持) + 原8.9(保持) + 原8.10(保持) + 原8.11(保持)
new_lines = lines[:s3] + new_83 + lines[s7:]
with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
print('8.3-8.6 合并完成(8.7-8.11保持原编号)')
