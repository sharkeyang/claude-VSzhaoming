'========================================================================================
'测试宏：日冲策略 vs 日周联动 对比分析
'用法：在已有神谕数据的簿中运行
'========================================================================================
Public Sub 测试_日冲策略vs日周联动()
    Dim 谕组 As Variant
    ' 获取当前表的神谕数据
    Dim WS As Worksheet
    Set WS = ActiveSheet
    Dim 基行 As Long, 基列 As Long
    基行 = 1: 基列 = 1
    ' 从当前表读取谕组（简化版，实际需根据具体情况调整）

    ' 统计各组合的对应关系
    Dim 统计 As New Dictionary
    Dim X As Long
    For X = LBound(谕组, 1) To UBound(谕组, 1)
        Dim 日冲 As String: 日冲 = 谕组(X, 位谕of日冲策略)
        Dim 日联 As String: 日联 = 谕组(X, 位谕of日层联动)
        If 日冲 <> "" And 日联 <> "" Then
            Dim 周向 As String: 周向 = Left$(日联, 1)
            Dim Key As String: Key = 日冲 & "|" & 周向
            统计(Key) = 统计(Key) + 1
        End If
    Next

    ' 输出结果
    Dim MSG As String
    MSG = "日冲策略 vs 日周联动(周向) 对比:" & vbCrLf & vbCrLf
    MSG = MSG & "日冲等级" & vbTab & "周向=升" & vbTab & "周向=待" & vbTab & "周向=降" & vbCrLf
    Dim 等级 As Variant
    For Each 等级 In Array("A", "B", "C", "D", "E", "F", "G", "H")
        Dim 升 As Long: 升 = 统计(等级 & "|升")
        Dim 待 As Long: 待 = 统计(等级 & "|待")
        Dim 降 As Long: 降 = 统计(等级 & "|降")
        Dim 总 As Long: 总 = 升 + 待 + 降
        If 总 > 0 Then
            MSG = MSG & 等级 & "级" & vbTab & 升 & "(" & Format(升/总*100, "0") & "%)" & vbTab & 待 & "(" & Format(待/总*100, "0") & "%)" & vbTab & 降 & "(" & Format(降/总*100, "0") & "%)" & vbCrLf
        End If
    Next
    MsgBox MSG, vbOKOnly, "日冲策略 vs 日周联动"
End Sub