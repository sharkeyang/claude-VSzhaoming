Attribute VB_Name = "ZUTL_验日冲22态"
'========================================================================================
' ZUTL_验日冲22态 — 验证日冲22态赋值是否正确的测试工具
' 用法：在Excel中运行 测试_日冲22态
' 输出：立即窗口打印前几只股票的日冲22态
'========================================================================================
Option Explicit

'========================================================================================
' 测试_日冲22态 — 验证位谕of日冲22态是否正确赋值
'========================================================================================
Public Sub 测试_日冲22态()
    Dim TT As Single: TT = Timer
    Dim 谕组 As Variant
    Dim 计数 As Long
    Dim X As Long
    Dim 状态 As String
    Dim 分布 As Object
    Set 分布 = CreateObject("Scripting.Dictionary")
    Dim 总行 As Long
    Dim 打印行 As Long

    ' 生成全息（用常花中股，只取前5只）
    Debug.Print "===== 日冲22态验证 ====="
    Debug.Print ""

    计数 = IQQQ跨码据擎_数程生成全息(谕组, 常花中股, 实结类型:="sSCC")
    If 计数 = 0 Then
        Debug.Print "生成失败"
        Exit Sub
    End If

    总行 = UBound(谕组, 1) - LBound(谕组, 1) + 1
    Debug.Print "总行数: " & 总行

    ' 打印前30行的日冲22态
    If 总行 > 30 Then 打印行 = 30 Else 打印行 = 总行
    For X = LBound(谕组, 1) To LBound(谕组, 1) + 打印行 - 1
        状态 = 谕组(X, 位谕of日冲22态)
        If 状态 = "" Then 状态 = "(空)"
        If 分布.Exists(状态) Then
            分布(状态) = 分布(状态) + 1
        Else
            分布.Add 状态, 1
        End If
        Debug.Print "  X=" & X & " 22态=" & 状态
    Next X

    ' 打印分布
    Debug.Print ""
    Debug.Print "===== 分布汇总 ====="
    Dim 键 As Variant
    For Each 键 In 分布.Keys
        Debug.Print 键 & ": " & 分布(键)
    Next 键

    Debug.Print "===== 耗时: " & CLng(Timer - TT) & "秒 ====="
End Sub