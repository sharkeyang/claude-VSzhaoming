# -*- coding: utf-8 -*-
"""
批量更新 _产出物/_工具/ 下脚本的谕组日/周 CSV 列号（2026-10-04 元数据更新后）
====================================================
背景：谕组 CSV 重新导出后列数变化（日66→70、周53→62），元数据列号已更新。
     本脚本按映射关系批量替换脚本中的硬编码列号。

日类映射（旧→新）：
  顶型[43]→[42]  日等型[44]→[43]  仓日类[45]→[44]  BT连阳[42]→[41]
  DTZB[62]→[66]  DTZD[63]→[67]  DTAB[64]→[68]  DTCD[65]→[69]

周类映射（旧→新）：
  WXZA[14]→[13]  WXZB[15]→[14]  WXZC[16]→[15]  WXZD[17]→[16]  WXZE[18]→[17]  WXZF[19]→[18]
  WXAB[20]→[19]  WXAC[21]→[20]  WXBC[22]→[21]  WXAD[23]→[22]  WXBD[24]→[23]  WXCD[25]→[24]
  WXCE[26]→[25]  WXDE[27]→[26]  WXCF[28]→[27]  WXEF[29]→[28]
  底周[30]→[29]  哈周[31]→[30]  哼周[32]→[31]  顶周[33]→[32]  合底周[34]→[33]  合顶周[35]→[34]
  极折周[36]→[35]  顶态周[37]→[36]  顶型周[38]→[37]  顶触周[39]→[38]
  上符范周[40]→[39]  上符串周[41]→[40]  宽符串周[42]→[41]  宽哼JA周[43]→[42]  撤哼JA周[44]→[43]
  中符串周[45]→[44]  中符范周[46]→[45]  BT鼎周[47]→[46]  并符范周[48]→[47]  并符串周[49]→[48]
  层类周[50]→[49]  周龄[51]→[60]

用法：
  python ____temp/批量更新脚本列号.py
"""
import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')

工具目录 = '_产出物/_工具'

# 日类映射（旧→新）
日类映射 = {
    42: 41,   # BT连阳
    43: 42,   # 顶型
    44: 43,   # 日等型
    45: 44,   # 仓日类
    62: 66,   # DTZB
    63: 67,   # DTZD
    64: 68,   # DTAB
    65: 69,   # DTCD
}

# 周类映射（旧→新）
周类映射 = {
    14: 13, 15: 14, 16: 15, 17: 16, 18: 17, 19: 18,
    20: 19, 21: 20, 22: 21, 23: 22, 24: 23, 25: 24,
    26: 25, 27: 26, 28: 27, 29: 28,
    30: 29, 31: 30, 32: 31, 33: 32, 34: 33, 35: 34,
    36: 35, 37: 36, 38: 37, 39: 38,
    40: 39, 41: 40, 42: 41, 43: 42, 44: 43,
    45: 44, 46: 45, 47: 46, 48: 47, 49: 48,
    50: 49, 51: 60,
}

# 列号引用正则：row[N] / rows[idx][N] / rows[idx - 1][N] / to_f(row[N]) / float(row[N]) 等
# 匹配 [数字] 但排除 [0] 到 [13] 的日类基础列（这些不变）——实际按映射处理
列号引用 = re.compile(r'\[(\d+)\]')

def 判断类别(content):
    """根据 DATA_DIR 或注释判断脚本是日类还是周类"""
    if '谕组日' in content and '谕组周' not in content:
        return '日类'
    if '谕组周' in content and '谕组日' not in content:
        return '周类'
    # 两者都有或都没有，看 DATA_DIR
    if "DATA_DIR = '昭明算展/谕组日'" in content or "DATADIR = r'昭明算展/谕组日'" in content:
        return '日类'
    if "DATA_DIR = '昭明算展/谕组周'" in content or "DATADIR = r'昭明算展/谕组周'" in content:
        return '周类'
    return None

def 替换列号(content, 映射):
    """用占位符方式替换列号，避免冲突"""
    # 第一步：把旧列号替换为占位符
    for 旧 in 映射:
        content = content.replace(f'[{旧}]', f'[__占位{旧}__]')
    # 第二步：把占位符替换为新列号
    for 旧, 新 in 映射.items():
        content = content.replace(f'[__占位{旧}__]', f'[{新}]')
    return content

def 处理脚本(path):
    with open(path, encoding='utf-8') as f:
        content = f.read()
    类别 = 判断类别(content)
    if 类别 is None:
        return None, '无法判断类别'
    映射 = 日类映射 if 类别 == '日类' else 周类映射
    # 检查是否有需要替换的列号
    需要 = False
    for 旧 in 映射:
        if f'[{旧}]' in content:
            需要 = True
            break
    if not 需要:
        return 类别, '无需调整'
    new_content = 替换列号(content, 映射)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    return 类别, '已调整'

# 主流程
调整数 = 0
无需数 = 0
无法数 = 0
for fname in sorted(os.listdir(工具目录)):
    if not fname.endswith('.py'):
        continue
    path = os.path.join(工具目录, fname)
    类别, 结果 = 处理脚本(path)
    if 结果 == '已调整':
        print(f'  [调整] {fname} ({类别})')
        调整数 += 1
    elif 结果 == '无需调整':
        无需数 += 1
    else:
        print(f'  [跳过] {fname} ({结果})')
        无法数 += 1

print(f'\n完成：调整 {调整数} 个，无需调整 {无需数} 个，无法判断 {无法数} 个')
