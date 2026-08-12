# -*- coding: utf-8 -*-
import re

with open(r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'r', encoding='utf-8') as f:
    text = f.read()

# The 大盘仓位限制 section was deleted. Restore it from git HEAD.
# The current file jumps from 概览数字格式 directly to 二、行业分布.
# We need to insert the 大盘仓位限制 section between them.

# First, find the insertion point: after the 概览/持仓构成数字格式 end
insert_marker = "For X = 5 To 16\n        WSTO.Rows(X).HorizontalAlignment = xlRight\n        WSTO.Cells(X, 1).HorizontalAlignment = xlLeft\n    Next"
insert_pos = text.find(insert_marker)
if insert_pos < 0:
    print("ERROR: insert marker not found")
    exit(1)

# Find the end of the formatting block (Next)
# The Next is the last line of the insert_marker
# We insert after the next line
end_of_block = text.find('\n', insert_pos)
end_of_block = text.find('\n', end_of_block + 1)
end_of_block = text.find('\n', end_of_block + 1)
end_of_block = text.find('\n', end_of_block + 1)
end_of_block = text.find('\n', end_of_block + 1)

# The section to insert follows after 'Next'
# Find the next line after 'Next'
next_line = text.find('\n', end_of_block + 1)

# The 大盘仓位限制 section from git HEAD, adjusted for current layout
# Current layout: 满仓率 at 行16, 大盘仓位限制 at 行17, 福账户 at 行18, etc.
section = """
'========================================================================================
'输出：大盘仓位限制
'========================================================================================
    Dim 大盘行 As Integer
    Dim 指正分 As Integer, 指负分 As Integer
    Dim 指CIDL As Variant, 指月基 As String, 促动 As String
    指正分 = 0: 指负分 = 0
    '--- 评分：3个宽基指数月基带日促动方向 ---
    For Each 指CIDL In Array("sh000001", "sz399006", "sh000688")
        If 典指位.Exists(指CIDL) Then
            指月基 = 谕组(典指位(指CIDL), 位谕of月基带日)
            If Len(指月基) >= 4 Then
                促动 = Mid$(指月基, 4, 1)
                If 促动 = "\u25b2" Or 促动 = "\u2197" Then 指正分 = 指正分 + 1
                If 促动 = "\u2198" Or 促动 = "\u25bd" Then 指负分 = 指负分 + 1
            End If
        End If
    Next
    Dim 大盘判断 As String, 总上限 As Double
    Dim 总分 As Integer: 总分 = 指正分 - 指负分
    '--- 日冲策分评分（补充维度） ---
    Dim 冲高分 As Integer: 冲高分 = 0
    Dim 冲低分 As Integer: 冲低分 = 0
    Dim 冲分1 As String, 冲分2 As String, 冲分3 As String
    Dim 指冲 As Variant
    冲分1 = "": 冲分2 = "": 冲分3 = ""
    指序号 = 0
    For Each 指CIDL In Array("sh000001", "sz399006", "sh000688")
        指序号 = 指序号 + 1
        If 典指位.Exists(指CIDL) Then
            指冲 = 谕组(典指位(指CIDL), 位谕of日冲策分)
            If VBA.IsNumeric(指冲) Then
                If 指序号 = 1 Then 冲分1 = CStr(指冲)
                If 指序号 = 2 Then 冲分2 = CStr(指冲)
                If 指序号 = 3 Then 冲分3 = CStr(指冲)
                If 指冲 >= 50 Then 冲高分 = 冲高分 + 1 Else 冲低分 = 冲低分 + 1
            End If
        End If
    Next
    Dim 总分2 As Integer: 总分2 = 总分 + (冲高分 - 冲低分)
    Select Case 总分2
        Case Is >= 4: 大盘判断 = "强好": 总上限 = 1
        Case 2, 3: 大盘判断 = "向好": 总上限 = 0.85
        Case 0, 1: 大盘判断 = "偏多": 总上限 = 0.66
        Case -1: 大盘判断 = "中性": 总上限 = 0.5
        Case -2, -3: 大盘判断 = "偏空": 总上限 = 0.33
        Case Is <= -4: 大盘判断 = "向差": 总上限 = 0.33
    End Select
    '--- 输出计算步骤到Immediate和Sheet ---
    Debug.Print "【大盘评分】上证=" & 促动1 & "(" & 冲分1 & ") 创业板=" & 促动2 & "(" & 冲分2 & ") 科创=" & 促动3 & "(" & 冲分3 & ")"
    Debug.Print "【大盘评分】促动分=" & 总分 & " 日冲分=" & (冲高分 - 冲低分) & " 总分=" & 总分2 & " => " & 大盘判断 & " 上限=" & Format(总上限, "0%")
    Dim 大盘评分明细 As String
    大盘评分明细 = "促动" & 促动1 & "/" & 促动2 & "/" & 促动3 & " 日冲" & 冲分1 & "/" & 冲分2 & "/" & 冲分3
    大盘评分明细 = 大盘评分明细 & " => 总分" & 总分2 & " " & 大盘判断 & " 上限" & Format(总上限, "0%")
    WSTO.Cells(17, 8).Value = 大盘评分明细
    WSTO.Cells(17, 8).Font.Size = 9
    WSTO.Cells(17, 8).Font.Color = 常色三灰
    WSTO.Range(WSTO.Cells(17, 8), WSTO.Cells(17, 14)).Merge
    '--- 更新概览行17：大盘仓位限制 ---
    WSTO.Cells(17, 1).Value = "大盘仓位限制"
    WSTO.Cells(17, 3).Value = Format(总上限, "0%")
    WSTO.Cells(17, 5).Value = Format(总上限, "0%")
    WSTO.Cells(17, 7).Value = Format(总上限, "0%")
    WSTO.Rows(17).HorizontalAlignment = xlRight
    大盘行 = 18
    '福账户
    Dim 福上限 As Double: 福上限 = 福总资 * 总上限
    Dim 福月基目标 As Double: 福月基目标 = 福上限 * 0.2
    Dim 福周冲目标 As Double: 福周冲目标 = 福上限 * 0.4
    Dim 福日冲目标 As Double: 福日冲目标 = 福上限 * 0.4
    Dim 福月基比 As Double: 福月基比 = IIf(福上限 > 0, 福月基额 / 福上限, 0)
    Dim 福周冲比 As Double: 福周冲比 = IIf(福上限 > 0, 福周冲额 / 福上限, 0)
    Dim 福日冲比 As Double: 福日冲比 = IIf(福上限 > 0, 福日冲额 / 福上限, 0)
    Dim 福非策额 As Double: 福非策额 = 福仓额 - 福月基额 - 福周冲额 - 福日冲额
    Dim 福非策比 As Double: 福非策比 = IIf(福上限 > 0, 福非策额 / 福上限, 0)
    大盘行 = 18
    WSTO.Cells(大盘行, 1).Value = "福账户限额"
    WSTO.Cells(大盘行, 2).Value = Format(总上限, "0%")
    WSTO.Cells(大盘行, 3).Value = Round(福上限, 1) & "(" & IIf(福仓额 <= 福上限, "达标", "超额") & ")"
    WSTO.Cells(大盘行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(大盘行, 7).Value = IIf(福仓额 <= 福上限, "达标", "超额")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(福仓额 <= 福上限, 常色主黑, 常色主红)
    大盘行 = 19
    WSTO.Cells(大盘行, 1).Value = "  \u251c\u2500月基(>=20%)"
    WSTO.Cells(大盘行, 2).Value = Format(总上限 * 0.2, "0%")
    WSTO.Cells(大盘行, 3).Value = Round(福月基额, 1) & "(" & IIf(福月基额 >= 福月基目标, "达标", "缺额") & ")"
    WSTO.Cells(大盘行, 7).Value = IIf(福月基额 >= 福月基目标, "达标", "缺额")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(福月基额 >= 福月基目标, 常色主黑, 常色主蓝)
    大盘行 = 20
    WSTO.Cells(大盘行, 1).Value = "  \u251c\u2500周冲(<=40%)"
    WSTO.Cells(大盘行, 2).Value = Format(总上限 * 0.4, "0%")
    WSTO.Cells(大盘行, 3).Value = Round(福周冲额, 1) & "(" & IIf(福周冲额 <= 福周冲目标, "达标", "超额") & ")"
    WSTO.Cells(大盘行, 7).Value = IIf(福周冲额 <= 福周冲目标, "达标", "超额")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(福周冲额 <= 福周冲目标, 常色主黑, 常色主红)
    大盘行 = 21
    WSTO.Cells(大盘行, 1).Value = "  \u251c\u2500日冲(<=40%)"
    WSTO.Cells(大盘行, 2).Value = Format(总上限 * 0.4, "0%")
    WSTO.Cells(大盘行, 3).Value = Round(福日冲额, 1) & "(" & IIf(福日冲额 <= 福日冲目标, "达标", "超额") & ")"
    WSTO.Cells(大盘行, 7).Value = IIf(福日冲额 <= 福日冲目标, "达标", "超额")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(福日冲额 <= 福日冲目标, 常色主黑, 常色主红)
    大盘行 = 22
    WSTO.Cells(大盘行, 1).Value = "  \u2514\u2500非策略(=0%)"
    WSTO.Cells(大盘行, 3).Value = Round(福非策额, 1) & "(" & IIf(福非策额 > 0, "超额", "无目标") & ")"
    WSTO.Cells(大盘行, 7).Value = IIf(福非策额 > 0, "超额", "无目标")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(福非策额 > 0, 常色主红, 常色主黑)
    Dim 彦上限 As Double: 彦上限 = 彦总资 * 总上限
    Dim 彦月基目标 As Double: 彦月基目标 = 彦上限 * 0.5
    Dim 彦周冲目标 As Double: 彦周冲目标 = 彦上限 * 0.5
    Dim 彦日冲目标 As Double: 彦日冲目标 = 彦上限 * 0.2
    Dim 彦月基比 As Double: 彦月基比 = IIf(彦上限 > 0, 彦月基额 / 彦上限, 0)
    Dim 彦周冲比 As Double: 彦周冲比 = IIf(彦上限 > 0, 彦周冲额 / 彦上限, 0)
    Dim 彦日冲比 As Double: 彦日冲比 = IIf(彦上限 > 0, 彦日冲额 / 彦上限, 0)
    Dim 彦非策额 As Double: 彦非策额 = 彦仓额 - 彦月基额 - 彦周冲额 - 彦日冲额
    Dim 彦非策比 As Double: 彦非策比 = IIf(彦上限 > 0, 彦非策额 / 彦上限, 0)
    大盘行 = 23
    WSTO.Cells(大盘行, 1).Value = "彦账户限额"
    WSTO.Cells(大盘行, 4).Value = Format(总上限, "0%")
    WSTO.Cells(大盘行, 5).Value = Round(彦上限, 1) & "(" & IIf(彦仓额 <= 彦上限, "达标", "超额") & ")"
    WSTO.Cells(大盘行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(大盘行, 7).Value = IIf(彦仓额 <= 彦上限, "达标", "超额")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(彦仓额 <= 彦上限, 常色主黑, 常色主红)
    大盘行 = 24
    WSTO.Cells(大盘行, 1).Value = "  \u251c\u2500月基(>=50%)"
    WSTO.Cells(大盘行, 4).Value = Format(总上限 * 0.5, "0%")
    WSTO.Cells(大盘行, 5).Value = Round(彦月基额, 1) & "(" & IIf(彦月基额 >= 彦月基目标, "达标", "缺额") & ")"
    WSTO.Cells(大盘行, 7).Value = IIf(彦月基额 >= 彦月基目标, "达标", "缺额")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(彦月基额 >= 彦月基目标, 常色主黑, 常色主蓝)
    大盘行 = 25
    WSTO.Cells(大盘行, 1).Value = "  \u251c\u2500周冲(<=50%)"
    WSTO.Cells(大盘行, 4).Value = Format(总上限 * 0.5, "0%")
    WSTO.Cells(大盘行, 5).Value = Round(彦周冲额, 1) & "(" & IIf(彦周冲额 <= 彦周冲目标, "达标", "超额") & ")"
    WSTO.Cells(大盘行, 7).Value = IIf(彦周冲额 <= 彦周冲目标, "达标", "超额")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(彦周冲额 <= 彦周冲目标, 常色主黑, 常色主红)
    大盘行 = 26
    WSTO.Cells(大盘行, 1).Value = "  \u251c\u2500日冲(<=20%)"
    WSTO.Cells(大盘行, 5).Value = Round(彦日冲额, 1) & "(" & IIf(彦日冲额 <= 彦日冲目标, "达标", "超额") & ")"
    WSTO.Cells(大盘行, 7).Value = IIf(彦日冲额 <= 彦日冲目标, "达标", "超额")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(彦日冲额 <= 彦日冲目标, 常色主黑, 常色主红)
    大盘行 = 27
    WSTO.Cells(大盘行, 1).Value = "  \u2514\u2500非策略(=0%)"
    WSTO.Cells(大盘行, 5).Value = Round(彦非策额, 1) & "(" & IIf(彦非策额 > 0, "超额", "无目标") & ")"
    WSTO.Cells(大盘行, 7).Value = IIf(彦非策额 > 0, "超额", "无目标")
    WSTO.Cells(大盘行, 7).Font.Color = IIf(彦非策额 > 0, 常色主红, 常色主黑)
    '--- 右对齐 ---
    With WSTO
        For X = 18 To 29
            .Rows(X).HorizontalAlignment = xlRight
            .Cells(X, 1).HorizontalAlignment = xlLeft
        Next
    End With
"""

# Insert after the 概览 formatting block
text = text[:next_line] + section + text[next_line:]

with open(r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'w', encoding='utf-8') as f:
    f.write(text)

print('OK - section restored')