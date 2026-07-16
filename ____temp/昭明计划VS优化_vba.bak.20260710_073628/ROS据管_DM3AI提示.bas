Attribute VB_Name = "ROS据管_DM3AI提示"
'========================================================================================
' ROS据管_DM3AI提示 — 持仓AI操作提示引擎
' 功能：遍历花天表持仓股票，执行决策树生成AI操作提示
' 依赖：花天表已结算完成（神谕数据就绪）
' 入口：STBASEAI提示_执行持仓决策
'========================================================================================

'========================================================================================
' 主入口：遍历所有持仓，生成AI操作提示
'========================================================================================
Public Sub STBASEAI提示_执行持仓决策()
    Dim WS花册 As Worksheet
    Set WS花册 = ThisWorkbook.Sheets(常花中股)

    Dim 末行 As Long
    末行 = WS花册.Cells(WS花册.Rows.Count, 位列花天CIDL).End(xlUp).Row

    ' 写入表头
    WS花册.Cells(1, 位列花天AI提示) = "AI操作提示"
    WS花册.Cells(1, 位列花天AI提示).Font.Bold = True

    Dim 行号 As Long
    For 行号 = 2 To 末行
        '--- 跳过无仓位股票 ---
        Dim 仓合 As Variant
        仓合 = WS花册.Cells(行号, 位列花天仓宝合).Value
        If IsEmpty(仓合) Or IsNull(仓合) Then GoTo 清空提示
        If Not IsNumeric(仓合) Then GoTo 清空提示
        If 仓合 <= 0 Then GoTo 清空提示

        '--- 跳过停牌 ---
        Dim 停牌 As Variant
        停牌 = WS花册.Cells(行号, 位列花天停牌).Value
        If 停牌 = "S" Or 停牌 = "s" Then
            WS花册.Cells(行号, 位列花天AI提示) = "停牌"
            GoTo 下一行
        End If

        '--- 读取神谕数据 ---
        Dim 基日列 As Long
        基日列 = 花列甲道    '日类OS车道起始列

        Dim BTZE As Double, BTZC As Double, BTZD As Double, BTZB As Double, BTZA As Double
        Dim 日柱排 As String, 周柱排 As String, 冲高提示 As String
        Dim 日层联动 As String, 盯盘类别 As String, WXCD As String

        BTZE = WS花册.Cells(行号, 基日列 + 位谕of日类BTZE - 1)
        BTZC = WS花册.Cells(行号, 基日列 + 位谕of日类BTZC - 1)
        BTZD = WS花册.Cells(行号, 基日列 + 位谕of日类BTZD - 1)
        BTZB = WS花册.Cells(行号, 基日列 + 位谕of日类BTZB - 1)
        BTZA = WS花册.Cells(行号, 基日列 + 位谕of日类BTZA - 1)
        日柱排 = WS花册.Cells(行号, 基日列 + 位谕of日层柱排 - 1)
        日层联动 = WS花册.Cells(行号, 基日列 + 位谕of日层联动 - 1)
        WXCD = Left$(日层联动, 1)

        '周类数据
        周柱排 = WS花册.Cells(行号, 花列乙道 + 位谕of周层柱排 - 1)
        冲高提示 = WS花册.Cells(行号, 花列乙道 + 位谕of周层下柱冲高提示 - 1)

        '仓位类型（H恒=基仓/K狙=有浮仓）
        盯盘类别 = WS花册.Cells(行号, 位qt盯盘类别)

        '--- 决策树 ---
        Dim AI提示 As String

        If 盯盘类别 = "H恒" Or 仓合 <= 5000 Then
            '========================================
            ' 基仓决策
            '========================================
            If BTZE < 0 And BTZC < 0 Then
                AI提示 = "?? DJE下破，强制清仓！"
            ElseIf BTZE < 0 And BTZD < 0 Then
                AI提示 = "? DJD已破，关注DJE！"
            ElseIf BTZE < 0 Then
                AI提示 = "? DJC之上持有，待DJE修复"
            Else
                AI提示 = "? 基仓持有"
            End If

        ElseIf 盯盘类别 = "K狙" Or 仓合 > 5000 Then
            '========================================
            ' 浮仓决策
            '========================================
            Dim 可下日 As Boolean, 可下周 As Boolean
            可下日 = (Left$(日柱排, 1) = "升") And BTZA >= 0
            可下周 = (冲高提示 <> "") And (Left$(周柱排, 1) = "升")

            If 可下日 And BTZD >= 0 Then
                AI提示 = "? 浮仓：下日冲高  止盈+3%/止损破DJD"
            ElseIf 可下周 Then
                AI提示 = "? 浮仓：下周冲高  止盈下周达标/止损破DJB"
            ElseIf BTZE < 0 And BTZC < 0 Then
                AI提示 = "? 浮仓平仓+DJE已破，全部清仓！"
            Else
                AI提示 = "?? 浮仓：平仓回归基仓"
            End If
        Else
            AI提示 = ""
        End If

        WS花册.Cells(行号, 位列花天AI提示) = AI提示

        '--- 颜色格式 ---
        If AI提示 <> "" Then
            With WS花册.Cells(行号, 位列花天AI提示).Font
                If InStr(AI提示, "?") > 0 Or InStr(AI提示, "清仓") > 0 Then
                    .Color = RGB(255, 0, 0)        '红色-危险
                ElseIf InStr(AI提示, "?") > 0 Or InStr(AI提示, "??") > 0 Then
                    .Color = RGB(255, 128, 0)      '橙色-预警
                ElseIf InStr(AI提示, "?") > 0 Then
                    .Color = RGB(0, 128, 0)        '绿色-安全
                ElseIf InStr(AI提示, "?") > 0 Then
                    .Color = RGB(0, 0, 255)        '蓝色-观望
                End If
            End With
        End If

        GoTo 下一行

清空提示:
        WS花册.Cells(行号, 位列花天AI提示) = ""
下一行:
    Next 行号

    ' 自动调整列宽
    WS花册.Columns(位列花天AI提示).AutoFit
    If WS花册.Columns(位列花天AI提示).ColumnWidth < 20 Then
        WS花册.Columns(位列花天AI提示).ColumnWidth = 20
    End If

    Set WS花册 = Nothing
End Sub
