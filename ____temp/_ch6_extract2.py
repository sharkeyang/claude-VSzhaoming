# -*- coding: utf-8 -*-
"""第六章精简重组：主线6.1~6.5，旧内容6.12"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(SRC, encoding='utf-8') as f:
    lines = f.readlines()

# 定位第六章边界
ch6_start = ch7_start = None
for i, l in enumerate(lines):
    if l.startswith('## 六、'):
        ch6_start = i
    if l.startswith('## 七、') and ch6_start is not None:
        ch7_start = i
        break

def find(pattern, start, end):
    for i in range(start, end):
        if re.match(pattern, lines[i]):
            return i
    return None

# 各块起点
s61 = find(r'^### 6\.1 ', ch6_start, ch7_start)      # 指导思想
s611 = find(r'^#### 6\.1\.1 ', ch6_start, ch7_start)  # 操作逻辑
s62 = find(r'^### 6\.2 ', ch6_start, ch7_start)      # 三层漏斗总览
s63 = find(r'^### 6\.3 ', ch6_start, ch7_start)      # 第1层DXCD
s631 = find(r'^#### 6\.3\.1 ', ch6_start, ch7_start)  # 四类区域
s6311 = find(r'^##### 6\.3\.1\.1 ', ch6_start, ch7_start)  # 全集划分
s64 = find(r'^### 6\.4 ', ch6_start, ch7_start)      # 第2层护型
s65 = find(r'^### 6\.5 ', ch6_start, ch7_start)      # 第3层介入时机
s66 = find(r'^### 6\.6 ', ch6_start, ch7_start)      # 定型规则
s661 = find(r'^#### 6\.6\.1 ', ch6_start, ch7_start)  # 流程图
s662 = find(r'^#### 6\.6\.2 ', ch6_start, ch7_start)  # 遍历验证
s67 = find(r'^### 6\.7 ', ch6_start, ch7_start)      # 期望收益
s68 = find(r'^### 6\.8 ', ch6_start, ch7_start)      # 持有条件
s681 = find(r'^#### 6\.8\.1 ', ch6_start, ch7_start)
s682 = find(r'^#### 6\.8\.2 ', ch6_start, ch7_start)
s69 = find(r'^### 6\.9 ', ch6_start, ch7_start)      # 少而精
s610 = find(r'^### 6\.10 ', ch6_start, ch7_start)    # 股性
s6101 = find(r'^#### 6\.10\.1 ', ch6_start, ch7_start)
s6102 = find(r'^#### 6\.10\.2 ', ch6_start, ch7_start)
s6103 = find(r'^#### 6\.10\.3 ', ch6_start, ch7_start)
s611 = find(r'^### 6\.11 ', ch6_start, ch7_start)    # 入管依据
s612 = find(r'^### 6\.12 ', ch6_start, ch7_start)    # 旧内容

print(f'6.1@{s61} 6.1.1@{s611} 6.2@{s62} 6.3@{s63} 6.3.1@{s631} 6.3.1.1@{s6311}')
print(f'6.4@{s64} 6.5@{s65} 6.6@{s66} 6.6.1@{s661} 6.6.2@{s662}')
print(f'6.7@{s67} 6.8@{s68} 6.8.1@{s681} 6.8.2@{s682} 6.9@{s69}')
print(f'6.10@{s610} 6.10.1@{s6101} 6.10.2@{s6102} 6.10.3@{s6103} 6.11@{s611} 6.12@{s612}')

# 提取各块
ch6_header = lines[ch6_start:s61]   # ## 六、 + 使用顺序说明
sec_61 = lines[s61:s62]             # 原6.1 指导思想 + 6.1.1
sec_62 = lines[s62:s63]             # 原6.2 三层漏斗总览
sec_63 = lines[s63:s64]             # 原6.3 第1层DXCD + 6.3.1四类区域
sec_64 = lines[s64:s65]             # 原6.4 第2层护型
sec_65 = lines[s65:s66]             # 原6.5 第3层介入时机
sec_66 = lines[s66:s67]             # 原6.6 定型规则 + 6.6.1 + 6.6.2
sec_67 = lines[s67:s68]             # 原6.7 期望收益
sec_68 = lines[s68:s69]             # 原6.8 持有条件
sec_69 = lines[s69:s610]            # 原6.9 少而精
sec_610 = lines[s610:s611]          # 原6.10 股性
sec_611 = lines[s611:s612]          # 原6.11 入管依据
sec_612 = lines[s612:ch7_start]     # 原6.12 旧内容

print(f'块大小: 6.1={len(sec_61)} 6.2={len(sec_62)} 6.3={len(sec_63)} 6.4={len(sec_64)} 6.5={len(sec_65)} 6.6={len(sec_66)}')
print(f'6.7={len(sec_67)} 6.8={len(sec_68)} 6.9={len(sec_69)} 6.10={len(sec_610)} 6.11={len(sec_611)} 6.12={len(sec_612)}')

import pickle
with open('____temp/_ch6_blocks2.pkl', 'wb') as f:
    pickle.dump({
        'ch6_header': ch6_header, 'sec_61': sec_61, 'sec_62': sec_62,
        'sec_63': sec_63, 'sec_64': sec_64, 'sec_65': sec_65, 'sec_66': sec_66,
        'sec_67': sec_67, 'sec_68': sec_68, 'sec_69': sec_69, 'sec_610': sec_610,
        'sec_611': sec_611, 'sec_612': sec_612,
        'ch6_start': ch6_start, 'ch7_start': ch7_start,
    }, f)
print('块已保存')