# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
path = '_主文档/MC3.3_C7日交易规则.md'
with open(path, encoding='utf-8') as f:
    lines = f.read().split('\n')

# 定位各节
s3 = next(i for i,l in enumerate(lines) if l.startswith('### 8.3 '))
s4 = next(i for i,l in enumerate(lines) if l.startswith('### 8.4 '))
s5 = next(i for i,l in enumerate(lines) if l.startswith('### 8.5 '))
s6 = next(i for i,l in enumerate(lines) if l.startswith('### 8.6 '))
s7 = next(i for i,l in enumerate(lines) if l.startswith('### 8.7 '))
s9 = next(i for i,l in enumerate(lines) if l.startswith('### 8.9 '))
s10 = next(i for i,l in enumerate(lines) if l.startswith('### 8.10 '))
s11 = next(i for i,l in enumerate(lines) if l.startswith('### 8.11 '))
s9j = next(i for i,l in enumerate(lines) if l.startswith('## 九'))
print(f'8.3:{s3+1} 8.4:{s4+1} 8.5:{s5+1} 8.6:{s6+1} 8.7:{s7+1} 8.9:{s9+1} 8.10:{s10+1} 8.11:{s11+1} 九:{s9j+1}')

# 提取各节内容（去掉标题行）
sec83 = lines[s3+1:s4]   # WXAB正交
sec84 = lines[s4+1:s5]   # 主升条件探索(含8.4.1-8.4.11)
sec85 = lines[s5+1:s6]   # 主升区域表现(含8.5.1-8.5.5)
sec86 = lines[s6+1:s7]   # 主升定稿(含8.6.1-8.6.4)
sec87 = lines[s7+1:s9]   # 周管
sec89 = lines[s9+1:s10]  # 升连研究
sec810 = lines[s10+1:s11] # 操作规则
sec811 = lines[s11+1:s9j] # 最小阻力动向

# 重编号
# 8.4.1-8.4.6 -> 8.3.2.x (主升前置)
# 8.4.7-8.4.11 -> 8.3.3.x (主升条件)
# 8.5.1-8.5.5 -> 8.3.4.x (主升区域)
# 8.6.1-8.6.4 -> 8.3.5.x (主升定稿)
def renum_sec(sec, old_prefix, new_prefix):
    new = []
    for l in sec:
        # 匹配 **8.4.1 或 #### 8.4.1 等
        m = re.match(r'^(\*{1,2}|#{3,5}) ' + re.escape(old_prefix) + r'\.(\d+)', l)
        if m:
            n = int(m.group(2))
            l = l.replace(f'{old_prefix}.{n}', f'{new_prefix}.{n}', 1)
        new.append(l)
    return new

# 8.4 内容: 8.4.1-8.4.6 -> 8.3.2.x, 8.4.7-8.4.11 -> 8.3.3.x
# 先处理 8.4.7-8.4.11 (条件探索)
sec84_cond = []
sec84_pre = []
for l in sec84:
    m = re.match(r'^(\*{1,2}|#{3,5}) 8\.4\.(\d+)', l)
    if m:
        n = int(m.group(2))
        if n >= 7:
            l = l.replace(f'8.4.{n}', f'8.3.3.{n-6}', 1)
            sec84_cond.append(l)
        else:
            l = l.replace(f'8.4.{n}', f'8.3.2.{n}', 1)
            sec84_pre.append(l)
    else:
        # 非标题行, 按当前处理
        if sec84_cond or any('8.3.3' in x for x in sec84_cond):
            sec84_cond.append(l)
        else:
            sec84_pre.append(l)

# 8.5 -> 8.3.4.x
sec85_new = renum_sec(sec85, '8.5', '8.3.4')
# 8.6 -> 8.3.5.x
sec86_new = renum_sec(sec86, '8.6', '8.3.5')

# 组装新 8.3 主升研究
new_83 = ['### 8.3 🎯 主升研究（合并 8.3-8.6，2026-10-17）']
new_83 += ['', '#### 8.3.1 主升驱动力：WXAB 正交（2026-09-26 用户定稿，重要课题）'] + sec83
new_83 += ['', '#### 8.3.2 主升前置状态（原 8.4.1-8.4.6）'] + sec84_pre
new_83 += ['', '#### 8.3.3 主升条件探索（原 8.4.7-8.4.11）'] + sec84_cond
new_83 += ['', '#### 8.3.4 主升区域表现（原 8.5）'] + sec85_new
new_83 += ['', '#### 8.3.5 主升定稿与深化（原 8.6）'] + sec86_new

# 后续节重编号: 8.7->8.4, 8.9->8.5, 8.10->8.6, 8.11->8.7
def renum_sec_full(sec, old_prefix, new_prefix):
    new = []
    for l in sec:
        m = re.match(r'^(\*{1,2}|#{3,5}) ' + re.escape(old_prefix) + r'\.(\d+)', l)
        if m:
            n = int(m.group(2))
            l = l.replace(f'{old_prefix}.{n}', f'{new_prefix}.{n}', 1)
        new.append(l)
    return new

sec87_new = renum_sec_full(sec87, '8.7', '8.4')
sec89_new = renum_sec_full(sec89, '8.9', '8.5')
sec810_new = renum_sec_full(sec810, '8.10', '8.6')
sec811_new = renum_sec_full(sec811, '8.11', '8.7')

# 组装新文件
new_lines = lines[:s3] + new_83 + [''] + ['### 8.4 周管（四波龙/四波虎，2026-10-03 新增）'] + sec87_new + [''] + ['### 8.5 周级别升连研究（2026-10-09 全量验证）'] + sec89_new + [''] + ['### 8.6 🎯 周类操作规则（2026-10-12 用户定稿，2026-10-17 从 8.9 独立）'] + sec810_new + [''] + ['### 8.7 🎯 最小阻力动向理论（2026-10-17 用户理论，全量 236.3 万行验证）'] + sec811_new + lines[s9j:]

with open(path, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))
print('8.3-8.6 合并完成')
