#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
统一命名规则：
  常量: 位谕of周策略P1 / 位谕of周策分P1 / 位谕of周策略P3 / 位谕of周策分P3
        位谕of月策略周 / 位谕of月策分命 / 位谕of月策分周 / 位谕of月策带周 / 位谕of月策带日
        位谕of月策略日 / 位谕of月策分日P2
        位谕of日策略P2 / 位谕of日策分P2
  显示名: 周策略P1 / 周策分P1 / 周策略P3 / 周策分P3
          月策略周 / 月策分命 / 月策分周 / 月策带周 / 月策带日
          月策略日 / 月策分日P2
          日策略P2 / 日策分P2
  文件名: vba周策分P1表.txt / vba周策分P3表.txt
  函数名: IQQQ跨码工具_查周策分P1 / IQQQ跨码工具_查周策分P3
  变量名: 周策略P1 / 周策分P1 / 周策略P3 / 周策分P3
"""

import os, glob

# ============================================================
# 1. 神谕.bas
# ============================================================
with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas', 'r', encoding='utf-8') as f:
    content = f.read()

# 常量定义
old_const = """Public Const 位谕始of族策 = 位谕终of族仓 + 1
'--- 周冲策略 P1（新增，放在P3之前） ---
Public Const 位谕of周冲策P1 = 位谕始of族策 + 0     '周冲策P1: 完整条件(如\"等2_0橅_升排_{银_甲乙己}\")
Public Const 位谕of周冲分P1 = 位谕始of族策 + 1    '周冲分P1: 编码(如\"6B84\")，期望HR取整+P1梯度+P1取整
'--- 周冲策略 P3（原周冲策略/策分改名） ---
Public Const 位谕of周冲策P3 = 位谕始of族策 + 2     '周冲策P3: 匹配的策略名(如\"金升非\")
Public Const 位谕of周冲分P3 = 位谕始of族策 + 3    '周冲分P3: 冲高概率(P>=3%)
'--- 月基策周 三变量 ---
'月基策周：月基持仓的底层分类，按周层四域映射为7类
'  V1 月基分命 = 股性分（历史基因），衡量该股历史上沿长期均线操作是否容易赚钱
'  V2 月基分周 = 存续分（走势维持），仅对多长三分类评分，预示后续1~5周是否维持月基状态
Public Const 位谕of月基策周 = 位谕始of族策 + 4     '月基策周: 多长(积极)/多长(消极)/多长(不定)/多被(金)/多被(银)/多被(唏)/NA(空看)/NA(空长)
Public Const 位谕of月基分命 = 位谕始of族策 + 5     'V1 月基分命: 股性分(0~100)，从CSV查表，恶庄天然过滤
Public Const 位谕of月基分周 = 位谕始of族策 + 6     'V2 月基分周(5周): 当前周波型×柱排状态, 5周后是否仍在多长(续持率取整), 仅对多长评分
Public Const 位谕of月基带周 = 位谕始of族策 + 7     'V3 月基带周: (WXCD)▲/↘/↗/▽ WXCD→WXAB带动
Public Const 位谕of月基带日 = 位谕始of族策 + 8     'V4 月基带日: (DXAB)同上(DXCD)同上(DXEF) 日级别DXAB→DXCD→DXEF带动
'--- 日层段（后续尽量合并） ---
'--- 仓周/仓日分类（由神谕生成，跨码管理读取） ---
Public Const 位谕of仓周类 = 位谕始of族策 + 9    '由神谕生成（基于WXCD护型+周层护型，第2772行），跨码管理读取
Public Const 位谕of仓日类 = 位谕始of族策 + 10    '由神谕生成（基于日线层护级CD+层护段AB，第2785行），跨码管理读取
Public Const 位谕of日层段 = 位谕始of族策 + 11     '日层段: 仓位状态(NA/卖浮/持主/持被)，以ZE为准判定主动/被动/卖浮
Public Const 位谕of月基策日 = 位谕始of族策 + 12     '月基策日: 龙/唏/嘘/屁 + 强/弱 + 甲后缀
Public Const 位谕of月基日H2 = 位谕始of族策 + 13    '月基日H2: 评级(A/B/C/D)+下日DSHR>2分数2位，如\"A39\"，升序排序
'--- 日冲策略 ---
Public Const 位谕of日冲策分 = 位谕始of族策 + 14     '日冲策分: 下日高≥2%概率(0~100)，赛马全量数据
Public Const 位谕of日冲策略 = 位谕始of族策 + 15       '日冲策略: 三级策略名称(如\"等2A\")，周门过滤+等高线匹配
Public Const 位谕of日层机警 = 位谕始of族策 + 16     '原+16，后移
'-----------
Public Const 位谕of日层漏提示 = 位谕始of族策 + 17     '日层漏提示: 精密捡漏信号
Public Const 位谕of日层联动 = 位谕始of族策 + 18     '周日联动: 周看涨但日下跌捡漏, 输出周/日
Public Const 位谕of日层盈提示 = 位谕始of族策 + 19    '日层盈提示: 止盈信号
'-----------
Public Const 位谕of周层四域 = 位谕始of族策 + 20
Public Const 位谕of策传 = 位谕始of族策 + 21      '策传综合信息，供Python读取
Public Const 位谕of日层四域 = 位谕始of族策 + 22
Public Const 位谕终of族策 = 位谕of日层四域"""

new_const = """Public Const 位谕始of族策 = 位谕终of族仓 + 1
'--- 周策略 P1 ---
Public Const 位谕of周策略P1 = 位谕始of族策 + 0     '周策略P1: 完整条件(如\"等2_0橅_升排_{银_甲乙己}\")
Public Const 位谕of周策分P1 = 位谕始of族策 + 1    '周策分P1: 编码(如\"6B84\")，期望HR取整+P1梯度+P1取整
'--- 周策略 P3 ---
Public Const 位谕of周策略P3 = 位谕始of族策 + 2     '周策略P3: 匹配的策略名(如\"金升非\")
Public Const 位谕of周策分P3 = 位谕始of族策 + 3    '周策分P3: 冲高概率(P>=3%)
'--- 月基策周 三变量 ---
Public Const 位谕of月策略周 = 位谕始of族策 + 4     '月策略周: 多长(积极)/多长(消极)/多长(不定)/多被(金)/多被(银)/多被(唏)/NA(空看)/NA(空长)
Public Const 位谕of月策分命 = 位谕始of族策 + 5     '月策分命: 股性分(0~100)，从CSV查表，恶庄天然过滤
Public Const 位谕of月策分周 = 位谕始of族策 + 6     '月策分周(5周): 当前周波型×柱排状态, 5周后是否仍在多长(续持率取整), 仅对多长评分
Public Const 位谕of月策带周 = 位谕始of族策 + 7     '月策带周: (WXCD)▲/↘/↗/▽ WXCD→WXAB带动
Public Const 位谕of月策带日 = 位谕始of族策 + 8     '月策带日: (DXAB)同上(DXCD)同上(DXEF) 日级别DXAB→DXCD→DXEF带动
'--- 仓周/仓日分类 ---
Public Const 位谕of仓周类 = 位谕始of族策 + 9
Public Const 位谕of仓日类 = 位谕始of族策 + 10
Public Const 位谕of日层段 = 位谕始of族策 + 11
'--- 月策略日 ---
Public Const 位谕of月策略日 = 位谕始of族策 + 12     '月策略日: 龙/唏/嘘/屁 + 强/弱 + 甲后缀
Public Const 位谕of月策分日P2 = 位谕始of族策 + 13   '月策分日P2: 评级(A/B/C/D)+下日DSHR>2分数2位，如\"A39\"
'--- 日策略 P2 ---
Public Const 位谕of日策分P2 = 位谕始of族策 + 14     '日策分P2: 下日高≥2%概率(0~100)
Public Const 位谕of日策略P2 = 位谕始of族策 + 15     '日策略P2: 三级策略名称(如\"等2A\")
Public Const 位谕of日层机警 = 位谕始of族策 + 16
'-----------
Public Const 位谕of日层漏提示 = 位谕始of族策 + 17
Public Const 位谕of日层联动 = 位谕始of族策 + 18
Public Const 位谕of日层盈提示 = 位谕始of族策 + 19
'-----------
Public Const 位谕of周层四域 = 位谕始of族策 + 20
Public Const 位谕of策传 = 位谕始of族策 + 21
Public Const 位谕of日层四域 = 位谕始of族策 + 22
Public Const 位谕终of族策 = 位谕of日层四域"""

content = content.replace(old_const, new_const)

# 旧名→新名映射（常量名）
rename_map = {
    '位谕of周冲策P1': '位谕of周策略P1',
    '位谕of周冲分P1': '位谕of周策分P1',
    '位谕of周冲策P3': '位谕of周策略P3',
    '位谕of周冲分P3': '位谕of周策分P3',
    '位谕of月基策周': '位谕of月策略周',
    '位谕of月基分命': '位谕of月策分命',
    '位谕of月基分周': '位谕of月策分周',
    '位谕of月基带周': '位谕of月策带周',
    '位谕of月基带日': '位谕of月策带日',
    '位谕of月基策日': '位谕of月策略日',
    '位谕of月基日H2': '位谕of月策分日P2',
    '位谕of日冲策分': '位谕of日策分P2',
    '位谕of日冲策略': '位谕of日策略P2',
}

for old, new in rename_map.items():
    content = content.replace(old, new)

# 显示名映射
display_map = {
    '"周冲策P1"': '"周策略P1"',
    '"周冲分P1"': '"周策分P1"',
    '"周冲策P3"': '"周策略P3"',
    '"周冲分P3"': '"周策分P3"',
    '"月基策周"': '"月策略周"',
    '"月基分命"': '"月策分命"',
    '"月基分周"': '"月策分周"',
    '"月基带周"': '"月策带周"',
    '"月基带日"': '"月策带日"',
    '"月基策日"': '"月策略日"',
    '"月基日H2"': '"月策分日P2"',
    '"日冲策分"': '"日策分P2"',
    '"日冲策略"': '"日策略P2"',
}

for old, new in display_map.items():
    content = content.replace(old, new)

# 函数名
content = content.replace('IQQQ跨码工具_查周冲策P3分', 'IQQQ跨码工具_查周策分P3')
content = content.replace('IQQQ跨码工具_查周冲策P1分', 'IQQQ跨码工具_查周策分P1')

# 文件路径
content = content.replace('vba周冲策P1分表.txt', 'vba周策分P1表.txt')
content = content.replace('vba周冲策分表.txt', 'vba周策分P3表.txt')

# 策传输出
content = content.replace('"周冲策P1="', '"周策略P1="')
content = content.replace('" 分P1="', '" 策分P1="')
content = content.replace('" 周冲策P3="', '" 周策略P3="')
content = content.replace('" 分P3="', '" 策分P3="')

# 变量名（局部变量）
content = content.replace('Dim 周P1策略 As String', 'Dim 周策略P1 As String')
content = content.replace('周P1策略 = IQQQ跨码工具', '周策略P1 = IQQQ跨码工具')
content = content.replace('If 周P1策略 <> "" Then', 'If 周策略P1 <> "" Then')
content = content.replace('Dim 周P1编码 As String: 周P1编码 = IQQQ跨码工具_查周策分P1(周P1策略)', 'Dim 周策分P1 As String: 周策分P1 = IQQQ跨码工具_查周策分P1(周策略P1)')
content = content.replace('If 周P1编码 = "" Then', 'If 周策分P1 = "" Then')
content = content.replace('Dim 周P1取整 As Integer: 周P1取整 = Val(Mid$(周P1编码, 3, 2))', 'Dim 周P1取整 As Integer: 周P1取整 = Val(Mid$(周策分P1, 3, 2))')
content = content.replace('If 周P1取整 > 0 And 周P1取整 < 78 Then\n                        谕组(X, 位谕of周策分P1) = "_" & 周P1编码\n                    Else\n                        谕组(X, 位谕of周策分P1) = 周P1编码\n                    End If\n                    谕组(X, 位谕of周策略P1) = 周P1策略',
                         'If 周P1取整 > 0 And 周P1取整 < 78 Then\n                        谕组(X, 位谕of周策分P1) = "_" & 周策分P1\n                    Else\n                        谕组(X, 位谕of周策分P1) = 周策分P1\n                    End If\n                    谕组(X, 位谕of周策略P1) = 周策略P1')

# P3变量
content = content.replace('Dim 周P3分 As Double: 周P3分 = IQQQ跨码工具_查周策分P3', 'Dim 周策分P3 As Double: 周策分P3 = IQQQ跨码工具_查周策分P3')
content = content.replace('If 周P3分 > 0 And 周P3分 < 50.6 Then\n                    谕组(X, 位谕of周策分P3) = "_" & CStr(周P3分)\n                Else\n                    谕组(X, 位谕of周策分P3) = 周P3分\n                End If\n                If 谕组(X, 位谕of周策分P3) = 0 Or 谕组(X, 位谕of周策分P3) = "_0" Then 谕组(X, 位谕of周策分P3) = "_"',
                         'If 周策分P3 > 0 And 周策分P3 < 50.6 Then\n                    谕组(X, 位谕of周策分P3) = "_" & CStr(周策分P3)\n                Else\n                    谕组(X, 位谕of周策分P3) = 周策分P3\n                End If\n                If 谕组(X, 位谕of周策分P3) = 0 Or 谕组(X, 位谕of周策分P3) = "_0" Then 谕组(X, 位谕of周策分P3) = "_"')

with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas', 'w', encoding='utf-8') as f:
    f.write(content)
print('神谕.bas 更新完成')

# ============================================================
# 2. 跨码管理.bas
# ============================================================
with open('昭明计划VS优化_vba/IQQQ跨码_D据擎4跨码管理.bas', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in rename_map.items():
    content = content.replace(old, new)

with open('昭明计划VS优化_vba/IQQQ跨码_D据擎4跨码管理.bas', 'w', encoding='utf-8') as f:
    f.write(content)
print('跨码管理.bas 更新完成')

# ============================================================
# 3. 筛选.bas
# ============================================================
with open('昭明计划VS优化_vba/IQQQ跨码_P展擎1筛选.bas', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in rename_map.items():
    content = content.replace(old, new)

with open('昭明计划VS优化_vba/IQQQ跨码_P展擎1筛选.bas', 'w', encoding='utf-8') as f:
    f.write(content)
print('筛选.bas 更新完成')

# ============================================================
# 4. 格程.bas
# ============================================================
with open('昭明计划VS优化_vba/IQQQ跨码_D据擎3格程.bas', 'r', encoding='utf-8') as f:
    content = f.read()

for old, new in rename_map.items():
    content = content.replace(old, new)

# 显示名
for old, new in display_map.items():
    content = content.replace(old, new)

with open('昭明计划VS优化_vba/IQQQ跨码_D据擎3格程.bas', 'w', encoding='utf-8') as f:
    f.write(content)
print('格程.bas 更新完成')

# ============================================================
# 5. 重命名外部文件
# ============================================================
file_renames = [
    ('_产出物/_工具/vba周冲策P1分表.txt', '_产出物/_工具/vba周策分P1表.txt'),
    ('_产出物/_工具/vba周冲策分表.txt', '_产出物/_工具/vba周策分P3表.txt'),
]

for old_path, new_path in file_renames:
    if os.path.exists(old_path):
        os.rename(old_path, new_path)
        print(f'{os.path.basename(old_path)} → {os.path.basename(new_path)}')
    else:
        print(f'{old_path} 不存在，跳过')

# ============================================================
# 6. 验证
# ============================================================
print()
print('=== 验证 ===')
for fname in ['昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas',
              '昭明计划VS优化_vba/IQQQ跨码_D据擎4跨码管理.bas',
              '昭明计划VS优化_vba/IQQQ跨码_P展擎1筛选.bas',
              '昭明计划VS优化_vba/IQQQ跨码_D据擎3格程.bas']:
    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()
    # 检查旧名残留
    old_names = ['位谕of周冲策P1', '位谕of周冲分P1', '位谕of周冲策P3', '位谕of周冲分P3',
                 '位谕of月基策周', '位谕of月基分命', '位谕of月基分周', '位谕of月基带周', '位谕of月基带日',
                 '位谕of月基策日', '位谕of月基日H2',
                 '位谕of日冲策分', '位谕of日冲策略']
    has_old = False
    for old in old_names:
        if old in content:
            print(f'  ❌ {os.path.basename(fname)}: 残留 {old}')
            has_old = True
    if not has_old:
        print(f'  ✅ {os.path.basename(fname)}: 全部更新')