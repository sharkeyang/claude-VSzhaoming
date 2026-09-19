# -*- coding: utf-8 -*-
"""第六章精简重组：拼接新顺序 + 更新标题编号"""
import re, sys, io, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

SRC = '_主文档/MC3.3.5_甲乙己日等型交叉分析报告.md'
with open(SRC, encoding='utf-8') as f:
    lines = f.readlines()

with open('____temp/_ch6_blocks2.pkl', 'rb') as f:
    B = pickle.load(f)

ch6_start = B['ch6_start']
ch7_start = B['ch7_start']

ch6_header = B['ch6_header']
sec_61 = B['sec_61']      # 原6.1 指导思想 + 6.1.1
sec_62 = B['sec_62']      # 原6.2 三层漏斗总览
sec_63 = B['sec_63']      # 原6.3 第1层DXCD + 6.3.1
sec_64 = B['sec_64']      # 原6.4 第2层护型
sec_65 = B['sec_65']      # 原6.5 第3层介入时机
sec_66 = B['sec_66']      # 原6.6 定型规则 + 6.6.1 + 6.6.2
sec_67 = B['sec_67']      # 原6.7 期望收益
sec_68 = B['sec_68']      # 原6.8 持有条件
sec_69 = B['sec_69']      # 原6.9 少而精
sec_610 = B['sec_610']    # 原6.10 股性
sec_611 = B['sec_611']    # 原6.11 入管依据
sec_612 = B['sec_612']    # 原6.12 旧内容

# ============ 标题编号更新函数 ============
def renum_title(line):
    """更新标题行编号。返回新标题行。"""
    m = re.match(r'^(#{2,5}) (6\.\d+(?:\.\d+)?)(.*)$', line)
    if not m:
        return line
    hashes, num, rest = m.group(1), m.group(2), m.group(3)
    # 映射：旧编号 → (新编号, 新标题级别)
    mapping = {
        '6.1':   ('6.1.1', '####'),   # 指导思想 → 6.1.1
        '6.1.1': ('6.1.2', '#####'),  # 操作逻辑 → 6.1.2
        '6.2':   ('6.1',   '###'),    # 三层漏斗总览 → 6.1
        '6.3':   ('6.2',   '###'),    # 第1层 → 6.2
        '6.3.1': ('6.2.1', '####'),   # 四类区域 → 6.2.1
        '6.3.1.1': ('6.2.1.1', '#####'),  # 全集划分 → 6.2.1.1
        '6.4':   ('6.3',   '###'),    # 第2层 → 6.3
        '6.5':   ('6.4',   '###'),    # 第3层 → 6.4
        '6.6':   ('6.5',   '###'),    # 定型规则 → 6.5
        '6.6.1': ('6.5.1', '####'),   # 流程图 → 6.5.1
        '6.6.2': ('6.5.2', '####'),   # 遍历验证 → 6.5.2
        '6.7':   ('6.12.5', '####'),  # 期望收益 → 6.12.5
        '6.8':   ('6.12.6', '####'),  # 持有条件 → 6.12.6
        '6.8.1': ('6.12.6.1', '#####'),
        '6.8.2': ('6.12.6.2', '#####'),
        '6.9':   ('6.12.7', '####'),  # 少而精 → 6.12.7
        '6.10':  ('6.12.8', '####'),  # 股性 → 6.12.8
        '6.10.1': ('6.12.8.1', '#####'),
        '6.10.2': ('6.12.8.2', '#####'),
        '6.10.3': ('6.12.8.3', '#####'),
        '6.11':  ('6.4.2', '####'),   # 入管依据 → 6.4.2（归入第3层）
        '6.12':  ('6.12',  '###'),    # 旧内容 → 6.12
        '6.12.1': ('6.12.1', '####'),
        '6.12.2': ('6.12.2', '####'),
        '6.12.2.1': ('6.12.2.1', '#####'),
        '6.12.2.2': ('6.12.2.2', '#####'),
        '6.12.3': ('6.12.3', '####'),
        '6.12.4': ('6.12.4', '####'),
    }
    if num in mapping:
        new_num, new_hashes = mapping[num]
        return f'{new_hashes} {new_num}{rest}'
    return line

def renum_block(block):
    return [renum_title(l) for l in block]

# ============ 拼接新顺序 ============
new_ch6 = []
new_ch6 += ch6_header
new_ch6 += renum_block(sec_62)   # 6.1 三层漏斗总览
new_ch6 += renum_block(sec_61)   # 6.1.1 指导思想 + 6.1.2 操作逻辑
new_ch6 += renum_block(sec_63)   # 6.2 第1层
new_ch6 += renum_block(sec_64)   # 6.3 第2层
new_ch6 += renum_block(sec_65)   # 6.4 第3层介入时机
new_ch6 += renum_block(sec_611)  # 6.4.2 入管依据（归入第3层）
new_ch6 += renum_block(sec_66)   # 6.5 定型规则
new_ch6 += renum_block(sec_612)  # 6.12 旧内容
new_ch6 += renum_block(sec_67)   # 6.12.5 期望收益
new_ch6 += renum_block(sec_68)   # 6.12.6 持有条件
new_ch6 += renum_block(sec_69)   # 6.12.7 少而精
new_ch6 += renum_block(sec_610)  # 6.12.8 股性

# 替换原第六章
new_lines = lines[:ch6_start] + new_ch6 + lines[ch7_start:]

with open(SRC, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print('✅ 第六章结构重排完成')