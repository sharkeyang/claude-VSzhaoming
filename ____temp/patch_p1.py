#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
补丁脚本：将 IQQQ跨码_D据擎2神谕.bas 中的周冲策略/策分 改为 周冲策P3/分P3，
并新增周冲策P1/分P1（放在P3之前），以及相关函数。
"""
import re

with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas', 'r', encoding='utf-8') as f:
    content = f.read()

# ============================================================
# 1. 常量定义区域：插入P1常量，P3常量改名，后续偏移+2
# ============================================================
old_const = """Public Const 位谕始of族策 = 位谕终of族仓 + 1
'--- 周冲策略 ---
Public Const 位谕of周冲策略 = 位谕始of族策 + 0     '周冲策略: 匹配的策略名(如\"金升非\")
Public Const 位谕of周冲策分 = 位谕始of族策 + 1    '周冲策分: 冲高概率(P>=3%)
'--- 月基策周 三变量 ---
'月基策周：月基持仓的底层分类，按周层四域映射为7类
'  V1 月基分命 = 股性分（历史基因），衡量该股历史上沿长期均线操作是否容易赚钱
'  V2 月基分周 = 存续分（走势维持），仅对多长三分类评分，预示后续1~5周是否维持月基状态
Public Const 位谕of月基策周 = 位谕始of族策 + 2     '月基策周: 多长(积极)/多长(消极)/多长(不定)/多被(金)/多被(银)/多被(唏)/NA(空看)/NA(空长)
Public Const 位谕of月基分命 = 位谕始of族策 + 3     'V1 月基分命: 股性分(0~100)，从CSV查表，恶庄天然过滤
Public Const 位谕of月基分周 = 位谕始of族策 + 4     'V2 月基分周(5周): 当前周波型×柱排状态, 5周后是否仍在多长(续持率取整), 仅对多长评分
Public Const 位谕of月基带周 = 位谕始of族策 + 5     'V3 月基带周: (WXCD)▲/↘/↗/▽ WXCD→WXAB带动
Public Const 位谕of月基带日 = 位谕始of族策 + 6     'V4 月基带日: (DXAB)同上(DXCD)同上(DXEF) 日级别DXAB→DXCD→DXEF带动
'--- 日层段（后续尽量合并） ---
'--- 仓周/仓日分类（由神谕生成，跨码管理读取） ---
Public Const 位谕of仓周类 = 位谕始of族策 + 7    '由神谕生成（基于WXCD护型+周层护型，第2772行），跨码管理读取
Public Const 位谕of仓日类 = 位谕始of族策 + 8    '由神谕生成（基于日线层护级CD+层护段AB，第2785行），跨码管理读取
Public Const 位谕of日层段 = 位谕始of族策 + 9     '日层段: 仓位状态(NA/卖浮/持主/持被)，以ZE为准判定主动/被动/卖浮
Public Const 位谕of月基策日 = 位谕始of族策 + 10     '月基策日: 龙/唏/嘘/屁 + 强/弱 + 甲后缀
Public Const 位谕of月基日H2 = 位谕始of族策 + 11    '月基日H2: 评级(A/B/C/D)+下日DSHR>2分数2位，如\"A39\"，升序排序
'--- 日冲策略 ---
Public Const 位谕of日冲策分 = 位谕始of族策 + 12     '日冲策分: 下日高≥2%概率(0~100)，赛马全量数据
Public Const 位谕of日冲策略 = 位谕始of族策 + 13       '日冲策略: 三级策略名称(如\"等2A\")，周门过滤+等高线匹配
Public Const 位谕of日层机警 = 位谕始of族策 + 14     '原+16，后移
'-----------
Public Const 位谕of日层漏提示 = 位谕始of族策 + 15     '日层漏提示: 精密捡漏信号
Public Const 位谕of日层联动 = 位谕始of族策 + 16     '周日联动: 周看涨但日下跌捡漏, 输出周/日
Public Const 位谕of日层盈提示 = 位谕始of族策 + 17    '日层盈提示: 止盈信号
'-----------
Public Const 位谕of周层四域 = 位谕始of族策 + 18
Public Const 位谕of策传 = 位谕始of族策 + 19      '策传综合信息，供Python读取
Public Const 位谕of日层四域 = 位谕始of族策 + 20
Public Const 位谕终of族策 = 位谕of日层四域"""

new_const = """Public Const 位谕始of族策 = 位谕终of族仓 + 1
'--- 周冲策略 P1（新增，放在P3之前） ---
Public Const 位谕of周冲策P1 = 位谕始of族策 + 0     '周冲策P1: 完整条件(如\"等2_0橅_升排_{银_甲乙己}\")
Public Const 位谕of周冲分P1 = 位谕始of族策 + 1    '周冲分P1: 编码(如\"6B62\")，期望HR取整+P1梯度+P3取整
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

content = content.replace(old_const, new_const)

# ============================================================
# 2. 神谕生成逻辑：P3写入改名，新增P1生成
# ============================================================
old_gen = """            '查概率表并写入
            If 周策略 <> "" And 周市板 <> "" Then
                谕组(X, 位谕of周冲策略) = 周策略
                谕组(X, 位谕of周冲策分) = IQQQ跨码工具_查周冲策分(周策略, 周市板)
            End If
            '============================================================================
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
'月基策周"""

new_gen = """            '查概率表并写入
            If 周策略 <> "" And 周市板 <> "" Then
                Dim 周P3分 As Double: 周P3分 = IQQQ跨码工具_查周冲策P3分(周策略, 周市板)
                谕组(X, 位谕of周冲策P3) = 周策略
                If 周P3分 > 0 And 周P3分 < 50.6 Then
                    谕组(X, 位谕of周冲分P3) = "_" & CStr(周P3分)
                Else
                    谕组(X, 位谕of周冲分P3) = 周P3分
                End If
                If 谕组(X, 位谕of周冲分P3) = 0 Or 谕组(X, 位谕of周冲分P3) = "_0" Then 谕组(X, 位谕of周冲分P3) = "_"
            End If
            '============================================================================
            'P1概率表（基于完整梯度框架：ZA分段+等类+地型+柱排+WXCD+WXAB）
            '============================================================================
            Dim 周P1策略 As String
            Dim 周等类 As String: 周等类 = ""
            Dim 周末符 As String: 周末符 = Right$(谕组(X, 位谕of周管中符串), 1)
            If 周ZA = 1 Then
                周等类 = "等1"
            ElseIf 周ZA > 0 Then
                If 周ZA >= 2 And InStr("AB", 周末符) > 0 Then
                    周等类 = "等3"
                ElseIf 周ZA >= 2 And InStr("CDEF", 周末符) > 0 Then
                    周等类 = "等2"
                End If
            ElseIf 周ZA = -1 Then
                周等类 = "等5"
            ElseIf 周ZA < 0 Then
                If 周ZA <= -2 And InStr("EF", 周末符) > 0 Then
                    周等类 = "等7"
                ElseIf 周ZA <= -2 And InStr("ABCD", 周末符) > 0 Then
                    周等类 = "等6"
                End If
            End If
            '============================================================================
            'P1策略名生成与查表
            '============================================================================
            周P1策略 = IQQQ跨码工具_生成P1编码(周ZA, 周等类, 组结算(X, 基位周类 + 位os层地型), 周柱排, 周局, 周护)
            If 周P1策略 <> "" Then
                Dim 周P1编码 As String: 周P1编码 = IQQQ跨码工具_查周冲策P1分(周P1策略)
                If 周P1编码 = "" Then
                    谕组(X, 位谕of周冲分P1) = "_"
                Else
                    '编码第二位=P1梯度，C/D/E/F=低于78.1%基线，分数加_前缀
                    If InStr("CDEF", Mid$(周P1编码, 2, 1)) > 0 Then
                        谕组(X, 位谕of周冲分P1) = "_" & 周P1编码
                    Else
                        谕组(X, 位谕of周冲分P1) = 周P1编码
                    End If
                    谕组(X, 位谕of周冲策P1) = 周P1策略
                End If
            End If
            '============================================================================
'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@
'月基策周"""

content = content.replace(old_gen, new_gen)

# ============================================================
# 3. 策传输出：P3改名，新增P1
# ============================================================
old_cb = """            程策传_冲高 = "周冲策略=" & 谕组(X, 位谕of周冲策略) & " 策分=" & 谕组(X, 位谕of周冲策分)"""
new_cb = """            程策传_冲高 = "周冲策P1=" & 谕组(X, 位谕of周冲策P1) & " 分P1=" & 谕组(X, 位谕of周冲分P1)
            程策传_冲高 = 程策传_冲高 & " 周冲策P3=" & 谕组(X, 位谕of周冲策P3) & " 分P3=" & 谕组(X, 位谕of周冲分P3)"""
content = content.replace(old_cb, new_cb)

# ============================================================
# 4. 表头：新增P1，P3改名
# ============================================================
old_header = """        .Cells(1, 位谕of策传) = "策传"
        .Cells(1, 位谕of周冲策略) = "周冲策略"
        .Cells(1, 位谕of周冲策分) = "周冲策分"
        .Cells(1, 位谕of月基策周) = "月基策周\""""
new_header = """        .Cells(1, 位谕of策传) = "策传"
        .Cells(1, 位谕of周冲策P1) = "周冲策P1"
        .Cells(1, 位谕of周冲分P1) = "周冲分P1"
        .Cells(1, 位谕of周冲策P3) = "周冲策P3"
        .Cells(1, 位谕of周冲分P3) = "周冲分P3"
        .Cells(1, 位谕of月基策周) = "月基策周\""""
content = content.replace(old_header, new_header)

# ============================================================
# 5. 列着色：P3改名，新增P1
# ============================================================
old_color = """        .Columns(位谕of月基策日).Interior.Color = 常色四43
        .Columns(位谕of月基日H2).Interior.Color = 常色五43
        .Columns(位谕of周冲策略).Interior.Color = 常色四靛
        .Columns(位谕of周冲策分).Interior.Color = 常色五靛
        .Columns(位谕of日冲策略).Interior.Color = 常色四绿
        .Columns(位谕of日冲策分).Interior.Color = 常色六绿"""
new_color = """        .Columns(位谕of月基策日).Interior.Color = 常色四43
        .Columns(位谕of月基日H2).Interior.Color = 常色五43
        .Columns(位谕of周冲策P1).Interior.Color = 常色四靛
        .Columns(位谕of周冲分P1).Interior.Color = 常色五靛
        .Columns(位谕of周冲策P3).Interior.Color = 常色四靛
        .Columns(位谕of周冲分P3).Interior.Color = 常色五靛
        .Columns(位谕of日冲策略).Interior.Color = 常色四绿
        .Columns(位谕of日冲策分).Interior.Color = 常色六绿"""
content = content.replace(old_color, new_color)

# ============================================================
# 6. 列宽+左对齐：P3改名，新增P1
# ============================================================
old_width = """        .Columns(位谕of周冲策略).HorizontalAlignment = xlLeft
        .Columns(位谕of周冲策略).ColumnWidth = 6
        .Columns(位谕of周冲策分).ColumnWidth = 4"""
new_width = """        .Columns(位谕of周冲策P1).ColumnWidth = 6
        .Columns(位谕of周冲策P1).HorizontalAlignment = xlLeft
        .Columns(位谕of周冲分P1).ColumnWidth = 4
        .Columns(位谕of周冲策P3).ColumnWidth = 6
        .Columns(位谕of周冲策P3).HorizontalAlignment = xlLeft
        .Columns(位谕of周冲分P3).ColumnWidth = 4"""
content = content.replace(old_width, new_width)

# ============================================================
# 7. 在 IQQQ跨码工具_查周冲策分 函数之后，插入P1编码生成函数和P1查表函数
# ============================================================
# 先改名查周冲策分 → 查周冲策P3分
content = content.replace('IQQQ跨码工具_查周冲策分', 'IQQQ跨码工具_查周冲策P3分')

# 在P3查表函数之后插入P1相关函数
old_func_end = """If 概率典.Exists(键) Then IQQQ跨码工具_查周冲策P3分 = 概率典(键) Else IQQQ跨码工具_查周冲策P3分 = 0
End Function
'========================================================================================

'========================================================================================
'获取单码市板 — 从花册单行查询，不加载整个数组"""

new_funcs = """If 概率典.Exists(键) Then IQQQ跨码工具_查周冲策P3分 = 概率典(键) Else IQQQ跨码工具_查周冲策P3分 = 0
End Function
'========================================================================================

'========================================================================================
'生成P1编码 — 基于完整梯度框架（ZA分段+等类+地型+柱排+WXCD+WXAB）
'编码格式：期望HR取整 + P1梯度(A-F) + P3取整，如"6B62"
'========================================================================================
Public Function IQQQ跨码工具_生成P1编码(ByVal ZA周 As Double, ByVal 等类 As String, _
    ByVal 地型 As String, ByVal 柱排 As String, ByVal WXCD As String, ByVal WXAB护 As String) As String

    Dim ZA段 As String, 柱排向 As String, WXCD名 As String, WXAB名 As String

    'ZA分段
    If ZA周 >= 4 Then
        ZA段 = "ZA≥4"
    ElseIf ZA周 >= 0 Then
        ZA段 = "ZA≥0~<4"
    ElseIf ZA周 >= -3 Then
        ZA段 = "ZA≥-3~<0"
    Else
        ZA段 = "ZA<-3"
    End If

    '柱排方向
    If Left$(柱排, 1) = "升" Then
        柱排向 = "升排"
    ElseIf Left$(柱排, 1) = "跌" Then
        柱排向 = "跌排"
    Else
        柱排向 = "人排"
    End If

    'WXCD
    If InStr(WXCD, "金") > 0 Then
        WXCD名 = "金"
    ElseIf InStr(WXCD, "银") > 0 Then
        WXCD名 = "银"
    ElseIf InStr(WXCD, "唏") > 0 Then
        WXCD名 = "唏"
    ElseIf InStr(WXCD, "嘘") > 0 Then
        WXCD名 = "嘘"
    ElseIf InStr(WXCD, "尿") > 0 Then
        WXCD名 = "尿"
    ElseIf InStr(WXCD, "屎") > 0 Then
        WXCD名 = "屎"
    Else
        WXCD名 = "未知"
    End If

    'WXAB
    If InStr(WXAB护, "甲") > 0 Or InStr(WXAB护, "乙") > 0 Or InStr(WXAB护, "己") > 0 Then
        WXAB名 = "甲乙己"
    Else
        WXAB名 = "丙丁戊"
    End If

    '地型简化
    Dim 地型名 As String
    If ZA段 = "ZA≥0~<4" Then
        地型名 = "4上WJA"
    ElseIf ZA段 = "ZA≥-3~<0" Then
        地型名 = "5跌破"
    Else
        地型名 = 地型
    End If

    '生成完整策略名（用于查表），格式：等2_0橅_升排_{银_甲乙己}
    IQQQ跨码工具_生成P1编码 = 等类 & "_" & 地型名 & "_" & 柱排向 & "_{" & WXCD名 & "_" & WXAB名 & "}"
End Function
'========================================================================================

'========================================================================================
'查周冲策P1分 — 从vba周冲策P1分表.txt读取P1编码
'返回：编码字符串（如"6B62"），查不到返回""
'========================================================================================
Public Function IQQQ跨码工具_查周冲策P1分(ByVal 策略名 As String) As String
    Static 概率典P1 As Dictionary
    Static 已加载P1 As Boolean
    Dim 文件号 As Integer, 行内容 As String
    Dim 字段 As Variant

    If Not 已加载P1 Then
        Set 概率典P1 = New Dictionary
        文件号 = FreeFile
        Open ThisWorkbook.Path & "\_产出物\_工具\vba周冲策P1分表.txt" For Input As #文件号
            Line Input #文件号, 行内容  '跳过表头
            Do While Not EOF(文件号)
                Line Input #文件号, 行内容
                字段 = Split(行内容, vbTab)
                If UBound(字段) >= 1 Then
                    概率典P1(字段(0)) = 字段(1)  '长名称→编码
                End If
            Loop
        Close #文件号
        已加载P1 = True
    End If

    If 概率典P1.Exists(策略名) Then IQQQ跨码工具_查周冲策P1分 = 概率典P1(策略名) Else IQQQ跨码工具_查周冲策P1分 = ""
End Function
'========================================================================================

'========================================================================================
'获取单码市板 — 从花册单行查询，不加载整个数组"""

content = content.replace(old_func_end, new_funcs)

# ============================================================
# 写入文件
# ============================================================
with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas', 'w', encoding='utf-8') as f:
    f.write(content)

print('补丁应用完成')
print('位谕of周冲策P1出现次数:', content.count('位谕of周冲策P1'))
print('位谕of周冲分P1出现次数:', content.count('位谕of周冲分P1'))
print('位谕of周冲策P3出现次数:', content.count('位谕of周冲策P3'))
print('位谕of周冲分P3出现次数:', content.count('位谕of周冲分P3'))
print('IQQQ跨码工具_生成P1编码出现次数:', content.count('IQQQ跨码工具_生成P1编码'))
print('IQQQ跨码工具_查周冲策P1分出现次数:', content.count('IQQQ跨码工具_查周冲策P1分'))
print('IQQQ跨码工具_查周冲策P3分出现次数:', content.count('IQQQ跨码工具_查周冲策P3分'))