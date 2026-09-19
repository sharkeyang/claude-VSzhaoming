# -*- coding: utf-8 -*-
"""第六章第二轮重组：四层漏斗 → 三层漏斗
6.1指导思想(用户操作理念) + 6.2三层漏斗总览 + 6.3第1层DXCD(含四类区域) + 6.4~6.11顺移 + 6.12旧内容
"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(SRC, encoding='utf-8') as f:
    lines = f.readlines()

# 定位第六章边界
ch6 = ch7 = None
for i, l in enumerate(lines):
    if l.startswith('## 六、'):
        ch6 = i
    if l.startswith('## 七、') and ch6 is not None:
        ch7 = i
        break
print(f'第六章: {ch6}-{ch7}')

def find(pat, start, end):
    for i in range(start, end):
        if re.match(pat, lines[i]):
            return i
    return None

# 各块边界（0-indexed）
s61   = find(r'^### 6\.1 ', ch6, ch7)      # 核心框架
s611  = find(r'^#### 6\.1\.1 ', ch6, ch7)  # 用户操作理念
s62   = find(r'^### 6\.2 ', ch6, ch7)      # 第1层DXCD
s63   = find(r'^### 6\.3 ', ch6, ch7)      # 第2层护型
s64   = find(r'^### 6\.4 ', ch6, ch7)      # 第3层介入时机
s65   = find(r'^### 6\.5 ', ch6, ch7)      # 定型规则
s66   = find(r'^### 6\.6 ', ch6, ch7)      # 期望收益
s67   = find(r'^### 6\.7 ', ch6, ch7)      # 持有条件
s68   = find(r'^### 6\.8 ', ch6, ch7)      # 少而精
s69   = find(r'^### 6\.9 ', ch6, ch7)      # 股性
s610  = find(r'^### 6\.10 ', ch6, ch7)     # 入管
s611q = find(r'^### 6\.11 ', ch6, ch7)     # 四类区域
s612  = find(r'^### 6\.12 ', ch6, ch7)     # 旧内容

print(f'6.1@{s61} 6.1.1@{s611} 6.2@{s62} 6.3@{s63} 6.4@{s64} 6.5@{s65}')
print(f'6.6@{s66} 6.7@{s67} 6.8@{s68} 6.9@{s69} 6.10@{s610} 6.11@{s611q} 6.12@{s612}')

# 提取块
ch6_header = lines[ch6:s61]                       # 第六章开头（含使用顺序说明）
sec_61  = lines[s61:s611]                          # 核心框架（四层漏斗表+漏斗图）
sec_611 = lines[s611:s62]                          # 用户操作理念（含6.1.1.1）
sec_62  = lines[s62:s63]                           # 第1层DXCD
sec_63  = lines[s63:s64]                           # 第2层护型
sec_64  = lines[s64:s65]                           # 第3层介入时机
sec_65  = lines[s65:s66]                           # 定型规则
sec_66  = lines[s66:s67]                           # 期望收益
sec_67  = lines[s67:s68]                           # 持有条件
sec_68  = lines[s68:s69]                           # 少而精
sec_69  = lines[s69:s610]                          # 股性
sec_610 = lines[s610:s611q]                        # 入管
sec_611q= lines[s611q:s612]                        # 四类区域
sec_612 = lines[s612:ch7]                          # 旧内容

print(f'块大小: 头={len(ch6_header)} 6.1={len(sec_61)} 6.1.1={len(sec_611)} 6.2={len(sec_62)}')
print(f'6.3={len(sec_63)} 6.4={len(sec_64)} 6.5={len(sec_65)} 6.6={len(sec_66)}')
print(f'6.7={len(sec_67)} 6.8={len(sec_68)} 6.9={len(sec_69)} 6.10={len(sec_610)} 6.11={len(sec_611q)} 6.12={len(sec_612)}')

# 重排：新第六章顺序
new_ch6 = []
new_ch6 += ch6_header          # 第六章开头
new_ch6 += sec_611             # 6.1 指导思想（用户操作理念）
new_ch6 += sec_61              # 6.2 三层漏斗总览（核心框架）
new_ch6 += sec_62              # 6.3 第1层DXCD选择
new_ch6 += sec_611q            # 6.3 四类区域（并入第1层）
new_ch6 += sec_63              # 6.4 第2层护型
new_ch6 += sec_64              # 6.5 第3层介入时机
new_ch6 += sec_65              # 6.6 定型规则
new_ch6 += sec_66              # 6.7 期望收益
new_ch6 += sec_67              # 6.8 持有条件
new_ch6 += sec_68              # 6.9 少而精
new_ch6 += sec_69              # 6.10 股性
new_ch6 += sec_610             # 6.11 入管
new_ch6 += sec_612             # 6.12 旧内容

# 编号映射（标题 + 正文引用共用）
num_map = {
    '6.1.1.1': '6.1.1',
    '6.1.1': '6.1',
    '6.1': '6.2',
    '6.2': '6.3',
    '6.3': '6.4',
    '6.4': '6.5',
    '6.5.2': '6.6.2',
    '6.5.1': '6.6.1',
    '6.5': '6.6',
    '6.6': '6.7',
    '6.7.2': '6.8.2',
    '6.7.1': '6.8.1',
    '6.7': '6.8',
    '6.8': '6.9',
    '6.9.3': '6.10.3',
    '6.9.2': '6.10.2',
    '6.9.1': '6.10.1',
    '6.9': '6.10',
    '6.10': '6.11',
    '6.11.1': '6.3',
    '6.11': '6.3',
    '6.12.4': '6.12.4',
    '6.12.3': '6.12.3',
    '6.12.2': '6.12.2',
    '6.12.1': '6.12.1',
    '6.12': '6.12',
}

def remap(m):
    key = m.group(0)
    return num_map.get(key, key)

# 处理标题行（### 6.x / #### 6.x / ##### 6.x）
def fix_title(line):
    m = re.match(r'^(#{2,5}) (6\.\d+(?:\.\d+)?)', line)
    if m:
        hashes, num = m.group(1), m.group(2)
        newnum = num_map.get(num, num)
        return f'{hashes} {newnum}' + line[m.end():]
    return line

# 处理正文引用（§6.x）
def fix_refs(text):
    return re.sub(r'§6\.\d+(?:\.\d+)?', remap, text)

# 应用标题编号 + 正文引用
new_ch6 = [fix_title(l) for l in new_ch6]
new_ch6 = [fix_refs(l) for l in new_ch6]

# 特殊处理：6.1 核心框架标题改为"三层漏斗总览"，6.1.1 改为"指导思想"
# 6.1 核心框架 → 6.2 三层漏斗总览
for i, l in enumerate(new_ch6):
    if re.match(r'^### 6\.2 核心框架', l):
        new_ch6[i] = l.replace('核心框架：四层漏斗 + 真假正交识别', '三层漏斗总览（核心框架）')
    if re.match(r'^### 6\.1 用户操作理念', l):
        new_ch6[i] = l.replace('用户操作理念：沃土→甲乙己不破DJB→升管→垒升→剔诱多', '指导思想：用户操作理念（沃土→甲乙己不破DJB→升管→垒升→剔诱多）')

# 替换原第六章
new_lines = lines[:ch6] + new_ch6 + lines[ch7:]

with open(SRC, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✅ 第六章已重排为三层漏斗结构')
