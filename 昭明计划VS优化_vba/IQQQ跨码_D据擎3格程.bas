Attribute VB_Name = "IQQQ跨码_D据擎3格程"
'池铜金类在池金银非持仓限额：设置金额上限为2500
Public Const 常值仓限底仓额 = 5000
'========================================================================================
'定义OS列：持仓列
'调整顺序：将操盘归为一类；将轨迹信息归为一类
'只把需要记录历史演变的放入HX，例如BTXX，对于可以直接计算的不再放入（BSXX）
'========================================================================================
Public Const 位os仓操作 = 1
Public Const 位os仓操横 = 2
Public Const 位os仓位比 = 3
Public Const 位os仓盈比 = 4
Public Const 位os仓额总 = 5
Public Const 位os仓数总 = 6
Public Const 位os仓成本 = 7
Public Const 位os仓赚收 = 8
Public Const 位os仓赚损 = 9
Public Const 位os仓列数 = 9
'========================================================================================








'########################################################################################
'########################################################################################
'##################################     更新引擎格程     ################################
'########################################################################################
'########################################################################################



'========================================================================================
'========================================================================================
'格式化：ZX
'========================================================================================
'========================================================================================
Function IQQQ跨码展擎_按列汇总( _
          ByRef WS As Worksheet _
        , Optional ByVal 基行 As Integer = 2 _
        , Optional ByVal 基色底 As Long = 常色指金 _
        ) As Integer
'========================================================================================
'格式化纵向：整列 & 标题行
'通过判断执行初始行号，保证每个页面只执行一次
'========================================================================================
If 基行 <= 4 Then
            '============================================================================
            '全局设置
            '============================================================================
            WS.Tab.Color = 基色底
            With WS.Cells
                .ClearFormats
                .Interior.ColorIndex = 56
                .Font.Name = "宋体"
                .Font.Size = 10
            End With
            '============================================================================
            '调整与冻结
            '注意：此步骤要放在其他过程前面
            '============================================================================
            WS.Rows.Hidden = False
            WS.Columns.Hidden = False
            Call PBASE格程工具_表冻结锁定(WS, 基列:=2)
            '============================================================================
            '格式化区域：神谕区域
            '============================================================================
            Call IQQQ跨码展擎_按列神谕区域(WS)
            '============================================================================
            '格式化区域：QT区域
            '包含【纵向格程】与【横向格程】，均只在对全页格式化时生效
            '============================================================================
            Call IQQQ跨码展擎_按列QT区域(WS, 基色底:=基色底)
            '============================================================================
End If
'========================================================================================
'返回
'========================================================================================
    IQQQ跨码展擎_按列汇总 = 列定位
'========================================================================================
End Function









'========================================================================================
'========================================================================================
'基程：QT格式化
'更新类别：整列 & 标题行
'========================================================================================
'========================================================================================
Function IQQQ跨码展擎_按列QT区域( _
          ByRef WS As Worksheet _
        , Optional ByVal 基行 As Integer = 2 _
        , Optional ByVal 基列 As Integer = 1 _
        , Optional ByVal 基色底 As Long = 常色行情 _
        , Optional ByVal 基色调 As Double = 0.8 _
        ) As Integer
'========================================================================================
'全局：字体
'========================================================================================
    With WS.Cells(1, 基列).Resize(1, 位qt主宽).EntireColumn
        .Font.Color = 常色主黑
        .Font.TintAndShade = 0.6
    End With
    WS.Columns(基列).Columns(位qt代称).Font.Color = 常色主黑
'========================================================================================
'边框
'========================================================================================
    With WS.Cells(1, 基列).Resize(1, 位qt主宽).EntireColumn
'        '内部边框
'        With .Borders(xlInsideVertical)
'            .LineStyle = xlContinuous
'            .Weight = xlThin
'            .Color = 基色底
'            .TintAndShade = 0.5
'        End With
'        '左右边框
'        With .Borders(xlEdgeLeft)
'            .LineStyle = xlContinuous
'            .Weight = xlMedium
'            .Color = 常色主黑
'        End With
'        With .Borders(xlEdgeRight)
'            .LineStyle = xlContinuous
'            .Weight = xlMedium
'            .Color = 常色主黑
'        End With
    End With
'========================================================================================
'标题行
'========================================================================================
    With WS.Cells(1, 基列)
        '--------------------------------------------------------------------------------
        With .Resize(1, 位qt主宽)
            .Interior.Color = 基色底
            .Interior.TintAndShade = -0.2
            .Font.Color = 常色主黑
            '.Font.Bold = True
            .HorizontalAlignment = xlRight
        End With
        '----------------------------------
        .Cells(1, 位qt代码) = "CID"
        .Cells(1, 位qt代称) = "NAM"
        .Cells(1, 位qt今涨幅) = "PR%"
        .Cells(1, 位qt今高幅) = "HR%"
        .Cells(1, 位qt今收) = "QC"
        .Cells(1, 位qt前收) = "LC"
        .Cells(1, 位qt今开) = "QO"
        .Cells(1, 位qt今高) = "QH"
        .Cells(1, 位qt今低) = "QL"
        .Cells(1, 位qt量比) = "10LB"
        .Cells(1, 位qt换手) = "HS%"
        .Cells(1, 位qt今量) = "今量"
        .Cells(1, 位qt今额) = "今额"
        .Cells(1, 位qt市值) = "市值"
        .Cells(1, 位qt停牌) = "停牌"
        .Cells(1, 位qt今时) = "今时"
        .Cells(1, 位qt今期) = "今日"
        .Cells(1, 位qt市板) = "市板"
        .Cells(1, 位qt行业) = "行浪"
        .Cells(1, 位qt行益) = "行益"
        .Cells(1, 位qt概念) = "概念"
        .Cells(1, 位qt今池) = "今池"
        .Cells(1, 位qt在池) = "在池"
        .Cells(1, 位qt仓主) = "仓主"
        .Cells(1, 位qt仓周) = "仓周"
        .Cells(1, 位qt盯盘类别) = "盯盘"
        '--------------------------------------------------------------------------------
    End With
'========================================================================================
'列：格式
'========================================================================================
    '------------------------------------------------------------------------------------
    With WS.Columns(基列)
        .Columns(位qt代码).NumberFormatLocal = 全设格式of代码
        .Columns(位qt今涨幅).NumberFormatLocal = 全设格式of一位
        .Columns(位qt今涨幅).HorizontalAlignment = xlRight
        .Columns(位qt今高幅).NumberFormatLocal = 全设格式of一位
        .Columns(位qt今高幅).HorizontalAlignment = xlRight
        .Columns(位qt今收).NumberFormatLocal = 全设格式of零位
        .Columns(位qt前收).NumberFormatLocal = 全设格式of价格
        .Columns(位qt今开).NumberFormatLocal = 全设格式of价格
        .Columns(位qt今高).NumberFormatLocal = 全设格式of价格
        .Columns(位qt今低).NumberFormatLocal = 全设格式of价格
        .Columns(位qt量比).NumberFormatLocal = 全设格式of零位
        .Columns(位qt换手).NumberFormatLocal = 全设格式of零位
        .Columns(位qt今时).NumberFormatLocal = "hh:mm"
        .Columns(位qt今期).NumberFormatLocal = 全设格式of日期
        .Columns(位qt行业).HorizontalAlignment = xlRight
        .Columns(位qt行益).HorizontalAlignment = xlRight
        .Columns(位qt概念).HorizontalAlignment = xlRight
        .Columns(位qt盯盘类别).HorizontalAlignment = xlRight
        With .Columns(位qt盯盘类别).Validation
            .Delete
            .Add Type:=xlValidateList, AlertStyle:=xlValidAlertWarning, Operator:=xlBetween _
                    , Formula1:="S已卖,Z长仓,Z停牌,I,D盯盘,A重仓,C回落"
        End With
    End With
    '------------------------------------------------------------------------------------
    With WS.Columns(基列)
        .Columns(位qt代码).ColumnWidth = 0.4
        .Columns(位qt代称).ColumnWidth = 9
        .Columns(位qt今涨幅).ColumnWidth = 5.5
        .Columns(位qt今高幅).ColumnWidth = 5
        .Columns(位qt前收).ColumnWidth = 5
        .Columns(位qt今收).ColumnWidth = 5
        .Columns(位qt今开).ColumnWidth = 5
        .Columns(位qt今高).ColumnWidth = 5
        .Columns(位qt今低).ColumnWidth = 5
        .Columns(位qt今量).ColumnWidth = 1
        .Columns(位qt今额).ColumnWidth = 1
        .Columns(位qt量比).ColumnWidth = 3
        .Columns(位qt换手).ColumnWidth = 3
        .Columns(位qt市值).ColumnWidth = 5
        .Columns(位qt行业).ColumnWidth = 9
        .Columns(位qt行益).ColumnWidth = 8
        .Columns(位qt概念).ColumnWidth = 8
        .Columns(位qt今时).ColumnWidth = 6
        .Columns(位qt今期).ColumnWidth = 9
        .Columns(位qt市板).ColumnWidth = 2
        .Columns(位qt今池).ColumnWidth = 2
        .Columns(位qt仓主).ColumnWidth = 2
        .Columns(位qt仓周).ColumnWidth = 2
        .Columns(位qt在池).ColumnWidth = 2
        .Columns(位qt盯盘类别).ColumnWidth = 7
    End With
'========================================================================================
'列：显示
'放入【按列格式化】
'========================================================================================
    WS.Cells(1, 基列).Resize(1, 位qt主宽).EntireColumn.Hidden = True
    With WS.Columns(基列)
        .Columns(位qt代码).Hidden = False
        .Columns(位qt代称).Hidden = False
        .Columns(位qt今涨幅).Hidden = False
        .Columns(位qt量比).Hidden = False
        .Columns(位qt换手).Hidden = False
        '.Columns(位qt行业).Hidden = False
        .Columns(位qt仓周).Hidden = False
        If WS.Name = 常池名金 Then
            .Columns(位qt今收).Hidden = False
            .Columns(位qt仓主).Hidden = False
        End If
    End With
'========================================================================================
'检验：QT区域
'========================================================================================
''    Dim 行号遍历 As Integer
''    For 行号遍历 = 基行 To PBASE格程工具_表参末行指定(ws, 基列)
''        With WS.Cells(行号遍历, 基列)
''            With .Resize(1, 位qt主宽)
''                .Interior.Color = 基色底
''            End With
''            '----------------------------------------------------------------------------
''            '针对指数行
''            If UBCID是中股指(.Value) = True Then
''                .Resize(1, 位qt主宽).Interior.TintAndShade = 0.5
''                .Cells(1, 位qt代称).Interior.TintAndShade = 0.3
''            ElseIf UBCID是中股基(.Value) = True Then
''                .Resize(1, 位qt主宽).Interior.TintAndShade = 0.6
''                .Cells(1, 位qt代称).Interior.TintAndShade = 0.4
''            ElseIf UBCID是中股票(.Value) = True Then
''                .Resize(1, 位qt主宽).Interior.TintAndShade = 0.8
''                .Cells(1, 位qt代称).Interior.TintAndShade = 0.4
''            '----------------------------------------------------------------------------
''            '针对空行
''            '----------------------------------------------------------------------------
''            Else
''                With .Resize(1, 位谕列终全部)
''                    .Borders(xlInsideVertical).LineStyle = xlNone
''                    .Interior.Color = 基色底
''                    .Interior.TintAndShade = 0
''                    .Font.Bold = True
''                    .Font.Color = 常色主黑
''                End With
''            End If
''            '----------------------------------------------------------------------------
''        End With
''    Next 行号遍历
'========================================================================================
'返回值
'========================================================================================
    IQQQ跨码展擎_按列QT区域 = 基列 + 位qt主宽
End Function








'========================================================================================
'========================================================================================
'操作：按行校验
'========================================================================================
'========================================================================================
Sub IQQQ跨码展擎_按行汇总调程()
    '------------------------------------------------------------------------------------
    Dim 当前表名  As String
    当前表名 = ActiveSheet.Name
    '------------------------------------------------------------------------------------
    '校验
    '------------------------------------------------------------------------------------
    If Left$(当前表名, 1) = 常簿缀选自 _
    Or Left$(当前表名, 1) = 常簿缀选临 _
    Or Left$(当前表名, 1) = 常簿缀市板 _
    Or Left$(当前表名, 1) = 常簿缀结算 _
    Or 当前表名 = "统算比" _
    Or 当前表名 = "统算展" _
    Then
    Else
        Exit Sub
    End If
    '------------------------------------------------------------------------------------
    Dim WSAS As Worksheet
    Set WSAS = ActiveSheet
    Call IQQQ跨码展擎_按行汇总(WSAS, 是否跨码:=True)
    Set WSAS = Nothing
    '------------------------------------------------------------------------------------
End Sub
'========================================================================================
'========================================================================================
'格式化横向：针对单元格进行格式化
'注意：利用参数【基行】可以针对基行之后的行进行格式化
'========================================================================================
'========================================================================================
Function IQQQ跨码展擎_按行汇总( _
          ByRef WS As Worksheet _
        , Optional ByVal 基列 As Integer = 1 _
        , Optional ByVal 基行 As Integer = 2 _
        , Optional ByVal 是否跨码 As Boolean = False _
        , Optional ByVal 是否算展 As Boolean = False _
        ) As Integer
    On Error Resume Next
'========================================================================================
'声明变量
'========================================================================================
    Dim CIDL As String
    Dim 设定scheme As Integer, 设定目列 As Integer
    '------------------------------------------------------------------------------------
    Dim 末行 As Integer
    末行 = PBASE格程工具_表参末行指定(WS, 基列)
'========================================================================================
'清理：comment
'========================================================================================
    WS.Cells(基行, 1).Resize(末行 - 基行 + 1, 1).EntireRow.ClearComments
'========================================================================================
'检验：神谕区域
'========================================================================================
    Dim 行号遍历 As Integer
    For 行号遍历 = 基行 To 末行
    CIDL = WS.Cells(行号遍历, 位qt代码).Value
    是否执行 = False
    If 是否跨码 = True Then
        If UBCID是代码(CIDL) = True Then
            是否执行 = True
        End If
    Else
            '针对算展
            是否执行 = 是否算展
    End If
    If 是否执行 = True Then
'########################################################################################
'跨码
'########################################################################################
If 是否跨码 = True Then
        '================================================================================
        With WS.Cells(行号遍历, 基列)
                '-------------------------------------------------------------------------
                '标注：池
                '-------------------------------------------------------------------------
                If .Cells(1, 位qt代码) Like "r_hk*" Then
                    .Interior.ColorIndex = 22
                ElseIf UBCID是中股票(.Cells(1, 位qt代码)) = True Then
                    If .Cells(1, 位qt在池) = 常池名黑 Then      '池黑
                        .Interior.ColorIndex = 3
                        .Cells(1, 位qt在池).Font.ColorIndex = 3
                    ElseIf .Cells(1, 位谕of仓持数) > 0 Then         '池持
                        .Interior.ColorIndex = 43
                    ElseIf .Cells(1, 位qt在池) = 常池名金 Then      '池金
                        .Interior.ColorIndex = 44
                    ElseIf .Cells(1, 位qt在池) = 常池名银 Then      '池银
                        .Interior.ColorIndex = 39
                    End If
                End If
                '-------------------------------------------------------------------------
        End With
        '================================================================================
End If
'########################################################################################
'月类
'########################################################################################
        '================================================================================
        '月类
        '================================================================================
        With WS.Cells(行号遍历, 基列)
'                '========================================================================
'                '底色：月波
'                '========================================================================
'                If Left$(.Cells(1, 位谕of月道层类).Value, 1) = "_" Then
'                                For Y = 位谕始of族月类 To 位谕终of族月类
'                                    With .Cells(1, Y)
'                                        值TintAndShade = .Interior.TintAndShade
'                                        .Interior.TintAndShade = 值TintAndShade - 0.2
'                                    End With
'                                Next
'                End If
                '========================================================================
                '检验：月类
                '========================================================================
                With .Cells(1, 位谕of月道尊比柱)
                        If .Value = "A" Then
                            .Interior.Color = 常色四靛
                        ElseIf Left$(.Value, 1) = "B" Then
                            .Interior.Color = 常色四绿
                        ElseIf Left$(.Value, 1) = "C" Then
                            .Interior.Color = 常色四橙
                        Else
                            .Interior.Color = 常色二红
                        End If
                End With
                '========================================================================
        End With
        '================================================================================
'########################################################################################
'周类
'########################################################################################
        '================================================================================
        '周波
        '================================================================================
        With WS.Cells(行号遍历, 基列)
                '########################################################################
                '========================================================================
                '底色：周波
                '========================================================================
                If Left$(.Cells(1, 位谕of周层类合).Value, 1) = "_" Then
                                For Y = 位谕始of族周波 To 位谕终of族周波
                                    With .Cells(1, Y)
                                        值TintAndShade = .Interior.TintAndShade
                                        .Interior.TintAndShade = 值TintAndShade - 0.5
                                    End With
                                Next
                End If
                '========================================================================
                '标注：周类波幅
                '========================================================================
                '                With .Cells(1, 位谕of周波均高幅十)
                '                        If .Value >= 15 Then
                '                            .Font.Color = 常色十红
                '                        ElseIf .Value >= 10 Then
                '                            .Font.Color = 常色六红
                '                        ElseIf .Value >= 5 Then
                '                            .Font.Color = 常色十黄
                '                        ElseIf .Value >= 3 Then
                '                        Else
                '                            .Font.Color = .Interior.Color
                '                        End If
                '                End With
                '------------------------------------------------------------------------
                With .Cells(1, 位谕of周波临涨幅)
                        .HorizontalAlignment = xlLeft
                        If .Value >= WS.Cells(行号遍历, 基列).Cells(1, 位谕of周波均涨幅五) Then .HorizontalAlignment = xlRight
                End With
                With .Cells(1, 位谕of周波临高幅)
                        .HorizontalAlignment = xlLeft
                        If .Value >= WS.Cells(行号遍历, 基列).Cells(1, 位谕of周波均高幅十) Then .HorizontalAlignment = xlRight
                End With
                With .Cells(1, 位谕of周波今涨幅)
                        .HorizontalAlignment = xlLeft
                        If .Value >= WS.Cells(行号遍历, 基列).Cells(1, 位谕of周波均涨幅五) Then .HorizontalAlignment = xlRight
                End With
                '------------------------------------------------------------------------
                With .Cells(1, 位谕of周波今高幅)
                        .HorizontalAlignment = xlLeft
                        If .Value >= 5 Then
                            .Font.Color = 常色十红
                            .Font.Bold = True
                            .HorizontalAlignment = xlRight
                        ElseIf .Value >= 2 Then
                            .Font.Color = 常色十红
                            .HorizontalAlignment = xlRight
                        ElseIf .Value >= 0 Then
                        Else
                            .Font.Color = 常色十绿
                        End If
                End With
                '========================================================================
        End With
        '================================================================================
        '周类
        '================================================================================
        With WS.Cells(行号遍历, 基列)
                '========================================================================
                '标注：周层
                '醍醐灌顶20240204：所有【周管族】【周暴族】仅针对【A5】管提供参考，其余可以忽略。
                '========================================================================
'                    '------------------------------------------------------------------------
'                    '针对三鳄：/__
'                    '------------------------------------------------------------------------
'                    If InStr(.Cells(1, 位谕of周层三鳄), "屎") > 0 Or InStr(.Cells(1, 位谕of周层三鳄), "尿") > 0 Then
'                                    For Y = 位谕始of族周层 To 位谕终of族周层
'                                        With .Cells(1, Y)
'                                            值TintAndShade = .Interior.TintAndShade
'                                            .Interior.Color = 常色一灰
'                                            .Interior.TintAndShade = 值TintAndShade
'                                        End With
'                                    Next
'                    ElseIf InStr(.Cells(1, 位谕of周层三鳄), "嘘") > 0 Then
'                                    For Y = 位谕始of族周层 To 位谕终of族周层
'                                        With .Cells(1, Y)
'                                            值TintAndShade = .Interior.TintAndShade
'                                            .Interior.Color = 常色二灰
'                                            .Interior.TintAndShade = 值TintAndShade
'                                        End With
'                                    Next
'                    '------------------------------------------------------------------------
'                    '设置WJC之上
'                    '------------------------------------------------------------------------
'                    ElseIf InStr(.Cells(1, 位谕of周层三鳄), "唏") > 0 Then
'                                    For Y = 位谕始of族周层 To 位谕终of族周层
'                                        With .Cells(1, Y)
'                                            值TintAndShade = .Interior.TintAndShade
'                                            .Interior.Color = 常色三蓝
'                                            .Interior.TintAndShade = 值TintAndShade
'                                        End With
'                                    Next
'                    ElseIf InStr(.Cells(1, 位谕of周层三鳄), "银") > 0 Then
'                                    For Y = 位谕始of族周层 To 位谕终of族周层
'                                        With .Cells(1, Y)
'                                            值TintAndShade = .Interior.TintAndShade
'                                            .Interior.Color = 常色四青
'                                            .Interior.TintAndShade = 值TintAndShade
'                                        End With
'                                    Next
'                    '------------------------------------------------------------------------
'                    '针对三鳄：/A7/A3/B1
'                    '------------------------------------------------------------------------
'                    Else
'                            '----------------------------------------------------------------
'                            '设置【周层】
'                            '注20251020：将（主）与（渡）同色调，而不单独对（主）中的（杂根）单独设色，说明要以WJB丘作为操盘的依据。
'                            '----------------------------------------------------------------
'                            If InStr(.Cells(1, 位谕of周层护型), "a甲") > 0 Then
'                                    For Y = 位谕始of族周层 To 位谕终of族周层
'                                        With .Cells(1, Y)
'                                            值TintAndShade = .Interior.TintAndShade
'                                            '值TintAndShade = 值TintAndShade - 0.2
'                                            .Interior.TintAndShade = 值TintAndShade
'                                        End With
'                                    Next
'                            ElseIf InStr(.Cells(1, 位谕of周层护型), "b乙") > 0 Then
'                                    For Y = 位谕始of族周层 To 位谕终of族周层
'                                        With .Cells(1, Y)
'                                            值TintAndShade = .Interior.TintAndShade
'                                            值TintAndShade = 值TintAndShade - 0.3
'                                            .Interior.TintAndShade = 值TintAndShade
'                                        End With
'                                    Next
'                            Else
'                                    For Y = 位谕始of族周层 To 位谕终of族周层
'                                        With .Cells(1, Y)
'                                            值TintAndShade = .Interior.TintAndShade
'                                            值TintAndShade = 值TintAndShade - 0.6
'                                            .Interior.TintAndShade = 值TintAndShade
'                                        End With
'                                    Next
'                            End If
'                            '----------------------------------------------------------------
'                    End If
                    '------------------------------------------------------------------------
                    '整体上色：STBASE结算工具_衍生色度按仓周类
                    '------------------------------------------------------------------------
                            For Y = 位谕始of族周层 To 位谕终of族周层
                                With .Cells(1, Y)
                                    值TintAndShade = .Interior.TintAndShade
                                    .Interior.Color = STBASE结算工具_衍生色度按仓周类(WS.Cells(行号遍历, 基列).Cells(1, 位谕of仓周类).Value)
                                    .Interior.TintAndShade = 值TintAndShade
                                End With
                            Next
                '========================================================================
                '标注：周管
                '========================================================================
                    '--------------------------------------------------------------------
                    '设置背景：周管系统
                    '--------------------------------------------------------------------
                    If .Cells(1, 位谕of周层类IS管) = "" Then
                                    For Y = 位谕始of族周管 To 位谕终of族周管
                                        With .Cells(1, Y)
                                            值TintAndShade = .Interior.TintAndShade
                                            .Interior.Color = 常色二灰
                                            .Interior.TintAndShade = 值TintAndShade
                                        End With
                                    Next
                    ElseIf Left$(.Cells(1, 位谕of周层类IS管), 1) = "_" Then
                                    For Y = 位谕始of族周管 To 位谕终of族周管
                                        With .Cells(1, Y)
                                            值TintAndShade = .Interior.TintAndShade
                                            .Interior.Color = 常色四灰
                                            .Interior.TintAndShade = 值TintAndShade
                                        End With
                                    Next
                    Else
                                    For Y = 位谕始of族周管 To 位谕终of族周管
                                        With .Cells(1, Y)
                                            值TintAndShade = .Interior.TintAndShade
                                            .Interior.TintAndShade = Application.Max(-0.9, 值TintAndShade - 0.2)
                                        End With
                                    Next
                    End If
                    '--------------------------------------------------------------------
                    '设置字色：周管系统
                    '对非管隐藏字体；对WJC线下管设置【常色四黄】字色
                    '--------------------------------------------------------------------
                    If .Cells(1, 位谕of周层类IS管).Value = "" Then
                            For Y = 位谕始of族周管 To 位谕终of族周管
                                With .Cells(1, Y)
                                    .Font.Color = .Interior.Color
                                End With
                            Next
                    ElseIf Left$(.Cells(1, 位谕of周层类IS管).Value, 1) = "_" Then
                            For Y = 位谕始of族周管 To 位谕终of族周管
                                With .Cells(1, Y)
                                    .Font.Color = 常色四黄
                                End With
                            Next
                    End If
                    '--------------------------------------------------------------------
                    '设置字色：周粒系统
                    '--------------------------------------------------------------------
                    If .Cells(1, 位谕of周层类IS粒) <> "" Then
                            With .Cells(1, 位谕of周层类IS粒)
                                If Left$(.Value, 1) = "_" Then
                                    .Font.Color = 常色四黄
                                End If
                            End With
                    End If
                '========================================================================
                '标注：周管系统
                '========================================================================
                If .Cells(1, 位谕of周层类IS管) <> "" Then
                        '-----------------------------------------------
                        '预警暴升：使用叭宽【哼JA】
                        '默认不需要考虑的情况，特殊情况在下面设置提醒颜色
                        '注意：只有在【Oa新】【Oa__】情况下才需要提醒回撤，其余情况看均线
                        If .Cells(1, 位谕of周管宽哼JA).Value >= 15 Then
                            With .Cells(1, 位谕of周管宽哼JA)
                                If .Value >= 20 Then
                                    .Font.Color = 常色八红
                                Else
                                    .Font.Color = 常色八黄
                                End If
                            End With
                            With .Cells(1, 位谕of周管撤哼JA)
                                '相对回撤
                                If .Value >= WS.Cells(行号遍历, 基列).Cells(1, 位谕of周管宽哼JA) Then
                                    .Font.Color = 常色八红
                                ElseIf .Value >= 0.5 * WS.Cells(行号遍历, 基列).Cells(1, 位谕of周管宽哼JA) Then .Font.Italic = True
                                    .Font.Color = 常色八黄
                                End If
                                '绝对回撤
                                If .Value >= 10 Then .Font.Italic = True
                            End With
                        End If
                        '-----------------------------------------------
                        '预警上符：仅在管内预警
                        With .Cells(1, 位谕of周管上符范)
                                If .Value >= 80 Then
                                    .Font.Color = 常色八红
                                ElseIf .Value >= 50 Then
                                    .Font.Color = 常色主黑
                                ElseIf .Value <= 3 Then
                                    .Font.Color = 常色八黄  '正在脱离哼
                                End If
                        End With
                        '-----------------------------------------------
                End If
                '========================================================================
                '标注：按值配色
                '========================================================================
                        '特殊操作：买阴下周冲高
                        With .Cells(1, 位谕of周层下柱冲高提示)
                                If InStr(.Value, "冲") > 0 Then
                                    .Font.Color = 常色主黑
                                ElseIf InStr(.Value, "待") > 0 Then
                                    .Font.Color = 常色主黑
                                ElseIf Len(.Value) <> 0 Then
                                    .Font.Color = 常色主黑
                                End If
                        End With
                        With .Cells(1, 位谕of周层猪操作)
                                If Left$(.Value, 1) = "冲" Then
                                    .Font.Color = 常色六黄
                                End If
                        End With
                '========================================================================
        End With
        '================================================================================
'########################################################################################
'日类
'########################################################################################
        '================================================================================
        '格式类：日类
        '醍醐灌顶20240215：完全以DJE为界划分阴阳。【非日类[哼JC管]】对于WJE之上WJC之下隐藏信息。
        '醍醐灌顶20240911：根据【周日联动】进行信息显示，放弃原有根据【BTZE】进行信息显示
        '================================================================================
        With WS.Cells(行号遍历, 基列)
                '========================================================================
                '注20260305：应用（WXCD+WJB止损），按照周波型进行着色。
                '颜色分配：破（二红）初（六紫）再（四紫）主龙猪0无（十靛）主龙猪栏栅杂（六靛）主龙猪蛀（43绿）震WXZA劫（四绿）
                '========================================================================
                    If InStr(.Cells(1, 位谕of日层联动), "屎") > 0 Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色一灰
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    ElseIf InStr(.Cells(1, 位谕of日层联动), "尿") > 0 Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色二灰
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    ElseIf Left$(.Cells(1, 位谕of日层联动), 1) = "嘘" Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色二橙
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    ElseIf Left$(.Cells(1, 位谕of日层联动), 1) = "唏" Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色六蓝
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    '--------------------------------------------------------------------
                    '可持有，但存在瑕疵。铜，因为WXCD还未正交，必有震荡。银，处于WJB之下。
                    '--------------------------------------------------------------------
                    ElseIf Left$(.Cells(1, 位谕of日层联动), 1) = "银" Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色四青
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    '--------------------------------------------------------------------
                    '单列：过渡期
                    '注20260303：因存续时间较短，且已经区分地型，不再对（再）区分是否为龙。
                    '--------------------------------------------------------------------
                    '以下为经历WJB劫后始终未触顶
                    '注20260303：因存续时间较短，且已经区分地型，不再对（再）区分是否为龙。'包含：震负芽（/W3h/W3u）头负芽（/W2I/W2i）头正芽
                    ElseIf InStr(.Cells(1, 位谕of周层波型), "破") > 0 _
                        Or InStr(.Cells(1, 位谕of周层波型), "震负") > 0 Or InStr(.Cells(1, 位谕of周层波型), "头") > 0 _
                        Or InStr(.Cells(1, 位谕of周层波型), "再B") > 0 _
                        Or InStr(.Cells(1, 位谕of周层波型), "再C") > 0 _
                        Or InStr(.Cells(1, 位谕of周层波型), "再") > 0 Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色四紫
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    ElseIf InStr(.Cells(1, 位谕of周层波型), "初") > 0 _
                        Or InStr(.Cells(1, 位谕of周层波型), "储") > 0 Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色主碧
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    '--------------------------------------------------------------------
                    '以下均为：主
                    '--------------------------------------------------------------------
                    '应对WXZA劫
                    '--------------------------------------------------------------------
                    ElseIf InStr(.Cells(1, 位谕of周层波型), "龙管根") > 0 _
                        Or InStr(.Cells(1, 位谕of周层波型), "震正芽") > 0 Or InStr(.Cells(1, 位谕of周层波型), "震正根") > 0 _
                        Or InStr(.Cells(1, 位谕of周层波型), "4蛀") > 0 Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色六黄
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    '--------------------------------------------------------------------
                    '单列：WJA之上管内
                    '--------------------------------------------------------------------
                    ElseIf InStr(.Cells(1, 位谕of周层波型), "震正〇") > 0 _
                        Or InStr(.Cells(1, 位谕of周层波型), "龙管") > 0 Then
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色四靛
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    '--------------------------------------------------------------------
                    '单列：龙猪。地型（前四柱是否存在异常柱/跌连/跌吞）
                    '--------------------------------------------------------------------
                    Else
                                For Y = 位谕始of族日层 To 位谕终of族日管
                                    值TintAndShade = .Cells(1, Y).Interior.TintAndShade
                                    .Cells(1, Y).Interior.Color = 常色十靛
                                    .Cells(1, Y).Interior.TintAndShade = 值TintAndShade
                                Next
                    End If
                '========================================================================
                '检验：日层系
                '========================================================================
                '------------------------------------------------------------------------
                '日层系 多层级均线偏离
                '------------------------------------------------------------------------
                If .Cells(1, 位谕of日类BTZE) < 0 Then
                        '------------------------------------------------------------
                        '预警暴升：使用叭宽【哼JA】
                        '默认不需要考虑的情况，特殊情况在下面设置提醒颜色
                        '注意：只有在【Oa新】【Oa__】情况下才需要提醒回撤，其余情况看均线
                        '------------------------------------------------------------
                        If .Cells(1, 位谕of日层宽哼JC).Value >= 15 Then
                            With .Cells(1, 位谕of日层宽哼JC)
                                If .Value >= 20 Then
                                    .Font.Color = 常色八红
                                End If
                            End With
                            With .Cells(1, 位谕of日层撤哼JC)
                                '相对回撤
                                If .Value >= WS.Cells(行号遍历, 基列).Cells(1, 位谕of日层宽哼JC) Then
                                    .Font.Color = 常色八红
                                ElseIf .Value >= 0.5 * WS.Cells(行号遍历, 基列).Cells(1, 位谕of日层宽哼JC) Then .Font.Italic = True
                                    .Font.Color = 常色八黄
                                End If
                                '绝对回撤
                                If .Value >= 10 Then .Font.Italic = True
                            End With
                        ElseIf .Cells(1, 位谕of日层宽哼JC).Value <= 5 Then
                            With .Cells(1, 位谕of日层宽哼JC)
                                    .Font.Color = .Interior.Color
                                    .Font.TintAndShade = -0.1
                            End With
                            With .Cells(1, 位谕of日层撤哼JC)
                                    .Font.Color = .Interior.Color
                                    .Font.TintAndShade = -0.1
                            End With
                        End If
                        '------------------------------------------------------------
                        '偏离
                        '------------------------------------------------------------
                        With .Cells(1, 位谕of日层脸哼JA)
                                .Font.Color = .Interior.Color
                                If .Value >= 10 Then
                                    .Font.Color = 常色八红
                                ElseIf .Value >= 8 Then
                                    .Font.TintAndShade = 0.5
                                ElseIf .Value <= 3 Then
                                Else
                                    .Font.TintAndShade = -0.2
                                End If
                        End With
                        With .Cells(1, 位谕of日层BSHA)
                                .Font.Color = .Interior.Color
                                If .Value >= 10 Then
                                    .Font.Color = 常色八红
                                ElseIf .Value >= 8 Then
                                    .Font.TintAndShade = 0.5
                                ElseIf .Value <= 3 Then
                                Else
                                    .Font.TintAndShade = -0.2
                                End If
                        End With
                        '------------------------------------------------------------
                End If
                With .Cells(1, 位谕of日层BT连阳)
                        If Len(.Value) = 0 Then
                        ElseIf .Value >= 3 Then
                            .Font.Color = 常色八红
                        End If
                End With
                '-------------------------------------------------------------------------
                '日层系 买提示指标
                '-------------------------------------------------------------------------
                        With .Cells(1, 位谕of日层联动)
                                If Left$(.Value, 1) = "N" Then
                                    .Font.Color = 常色一红
                                ElseIf InStr(.Value, "持") > 0 Then
                                    .Font.Color = .Interior.Color
                                    .Font.TintAndShade = -0.3
                                End If
                        End With
                        '------------------------------------------------------------
                        With .Cells(1, 位谕of日层盈提示)
                                If InStr(.Value, "连") > 0 Then
                                    .Font.Bold = True
                                End If
                                If InStr(.Value, "高") > 0 Or InStr(.Value, "偏") > 0 Then
                                    .Font.Color = 常色三红
                                ElseIf InStr(.Value, "宽") > 0 Then
                                    .Font.Color = 常色三青
                                End If
                        End With
                '========================================================================
                '检验：日波系
                '检验：标注日类卖出建议
                '根据日类最高以及回撤幅度进行判断
                '========================================================================
                '日波高幅
                With .Cells(1, 位谕of日波BSHR)
                        If .Value >= 3 Then
                            .HorizontalAlignment = xlLeft
                            If .Value >= 5 Then
                                .Font.Bold = True
                            End If
                        Else
                            .HorizontalAlignment = xlRight
                            If .Value <= 1 Then
                                .Font.Color = .Interior.Color
                                .Font.TintAndShade = -0.2
                            End If
                        End If
                End With
                '------------------------------------------------------------------------
                '标注：日波上身
                '------------------------------------------------------------------------
                With .Cells(1, 位谕of日波上身)
                        If WS.Cells(行号遍历, 基列).Cells(1, 位谕of日波BSHR).Value < 1.5 Then
                                .Interior.Color = 常色二灰
                        Else
                            If .Value < 0 Then
                                .Interior.Color = 常色四蓝
                            ElseIf .Value < 25 Then
                                .Interior.Color = 常色四红
                            ElseIf .Value < 50 Then
                                .Interior.Color = 常色六红
                            ElseIf .Value < 75 Then
                                .Interior.Color = 常色四绿
                            Else
                                .Interior.Color = 常色六绿
                            End If
                        End If
                        .Font.Color = .Interior.Color
                End With
                '------------------------------------------------------------------------
'                With .Cells(1, 位谕of日段十停数高)
'                        If .Value = 0 Then .Font.Color = .Interior.Color
'                End With
                With .Cells(1, 位谕of日段仨停数高)
                        If .Value = 0 Then
                            .Font.Color = .Interior.Color
                        ElseIf .Value >= 2 Then
                            .Font.Color = 常色六黄
                        End If
                End With
'                With .Cells(1, 位谕of日段佰停数高)
'                        If .Value = 0 Then .Font.Color = .Interior.Color
'                End With
                '------------------------------------------------------------------------
'                With .Cells(1, 位谕of日段十均幅高)
'                        If .Value < 1.5 Then .Font.Color = .Interior.Color
'                End With
'                With .Cells(1, 位谕of日段仨均幅高)
'                        If .Value < 1.5 Then .Font.Color = .Interior.Color
'                End With
'                With .Cells(1, 位谕of日段佰均幅高)
'                        If .Value < 1.5 Then .Font.Color = .Interior.Color
'                End With
                '========================================================================
        End With
        '================================================================================
'########################################################################################
'配对操作：不同周期同类指标
'########################################################################################
        With WS.Cells(行号遍历, 基列)
'                '========================================================================
'                '波型
'                '========================================================================
'                        With .Cells(1, 位谕of周层波型)
'                                If .Value = "" Then
'                                ElseIf InStr(.Value, "破") > 0 Then
'                                    .Font.Color = 常色四红
'                                End If
'                        End With
'                '========================================================================
'                '层界
'                '========================================================================
'                        With .Cells(1, 位谕of周层界)
'                                If InStr(.Value, "破") > 0 Then
'                                    .Font.Color = 常色四红
'                                ElseIf Left$(.Value, 1) = "_" Then
'                                    .Font.Color = .Interior.Color
'                                    .Font.TintAndShade = 0.2
'                                ElseIf InStr(.Value, "储") > 0 Then
'                                    .Font.Color = 常色四青
'                                ElseIf InStr(.Value, "再") > 0 Then
'                                    .Font.Color = 常色四紫
'                                End If
'                        End With
'                        With .Cells(1, 位谕of日层界)
'                                If InStr(.Value, "破") > 0 Then
'                                    .Font.Color = 常色三红
'                                ElseIf Left$(.Value, 1) = "_" Then
'                                    .Font.Color = .Interior.Color
'                                    .Font.TintAndShade = -0.2
'                                ElseIf InStr(.Value, "储") > 0 Then
'                                    .Font.Color = 常色一绿
'                                ElseIf InStr(.Value, "再") > 0 Then
'                                    .Font.Color = 常色三紫
'                                End If
'                        End With
                '========================================================================
                '护型
                '========================================================================
                        With .Cells(1, 位谕of周层护型)
                                If .Value = "" Then
                                ElseIf InStr(.Value, "丁") > 0 Or InStr(.Value, "戊") > 0 Then
                                    .Font.Color = 常色二红
                                ElseIf InStr(.Value, "丙") > 0 Then
                                    .Font.Color = 常色三红
                                End If
                        End With
                        With .Cells(1, 位谕of日层护型)
                                If .Value = "" Then
                                ElseIf InStr(.Value, "丁") > 0 Or InStr(.Value, "戊") > 0 Then
                                    .Font.Color = 常色二红
                                ElseIf InStr(.Value, "丙") > 0 Then
                                    .Font.Color = 常色三红
                                End If
                        End With
                '========================================================================
                '柱排
                '========================================================================
'                        With .Cells(1, 位谕of周层柱排)
'                                If Left$(WS.Cells(行号遍历, 基列).cells(1, 位谕of周层界), 1) = "_" Then
'                                    .Font.Color = .Interior.Color
'                                    .Font.TintAndShade = -0.1
'                                End If
'                        End With
                '========================================================================
                '柱型
                '========================================================================
                        With .Cells(1, 位谕of周层柱型)
                                If InStr(.Value, "N") > 0 Then
                                    .Font.Color = .Interior.Color
                                    .Font.TintAndShade = 0
                                ElseIf InStr(.Value, "梯") > 0 Then
                                    .Font.Color = 常色一灰
                                ElseIf InStr(.Value, "栏") > 0 Then
                                    .Font.Color = 常色八黄
                                ElseIf InStr(.Value, "栅") > 0 Then
                                    .Font.Color = 常色六黄
                                ElseIf InStr(.Value, "杂") > 0 Then
                                    .Font.Color = 常色四黄
                                ElseIf InStr(.Value, "枝") > 0 Then
                                    .Font.Color = 常色四橙
                                ElseIf InStr(.Value, "根") > 0 Then
                                    .Font.Color = 常色六蓝
                                ElseIf Len(.Value) <> 0 Then
                                    .Font.Color = .Interior.Color
                                    .Font.TintAndShade = -0.1
                                End If
                        End With
                        With .Cells(1, 位谕of日层柱型)
                                If InStr(.Value, "N") > 0 Then
                                    .Font.Color = .Interior.Color
                                    .Font.TintAndShade = 0
                                ElseIf InStr(.Value, "梯") > 0 Then
                                    .Font.Color = 常色一灰
                                ElseIf InStr(.Value, "栏") > 0 Then
                                    .Font.Color = 常色八黄
                                ElseIf InStr(.Value, "栅") > 0 Then
                                    .Font.Color = 常色六黄
                                ElseIf InStr(.Value, "杂") > 0 Then
                                    .Font.Color = 常色四黄
                                ElseIf InStr(.Value, "枝") > 0 Then
                                    .Font.Color = 常色四橙
                                ElseIf InStr(.Value, "根") > 0 Then
                                    .Font.Color = 常色六蓝
                                ElseIf Len(.Value) <> 0 Then
                                    .Font.Color = .Interior.Color
                                    .Font.TintAndShade = -0.1
                                End If
                        End With
                '========================================================================
        End With
        '================================================================================
'########################################################################################
'仓日类
'########################################################################################
        '================================================================================
        '格式类：仓系
        '================================================================================
        With WS.Cells(行号遍历, 基列)
                '------------------------------------------------------------------------
'                '标记：操盘类别
'                With .Cells(1, 位谕of仓日类)
'                    .Interior.Color = STBASE结算工具_衍生色度按仓日类(.Value)
'                    .Font.Color = .Interior.Color
'                    .Font.TintAndShade = -0.1
'                End With
                '------------------------------------------------------------------------
                '标记：仓赚损
                With .Cells(1, 位谕of仓赚损)
                    .Font.ColorIndex = IIf(.Value <= -99, 1, 15)
                End With
                '标记：低于最基础金额，将字体设置为灰色
                With .Cells(1, 位谕of仓持额)
                    If .Value > 3 Then .Font.ColorIndex = 1
                End With
                '标记：盈亏比
                With .Cells(1, 位谕of仓盈比)
                    If .Value < -0.1 Then .Interior.Color = 常色主黄
                End With
                '标记：仓位比
                With .Cells(1, 位谕of仓位比)
                    If VBA.IsNumeric(.Value) = False Then .Font.Color = 常色十靛
                End With
                If .Cells(1, 位谕of仓操类) = "操盘在池" Then
                With .Cells(1, 位谕of仓位比)
                    If .Value < 0.3 Then .Interior.Color = 常色主黄
                    '判断仓位是否过小：防止踏空
                End With
                End If
                '------------------------------------------------------------------------
        End With
'        '================================================================================
'        '设置：comment
'        '================================================================================
'        If 是否跨码 = True Then
'        With WS.Cells(行号遍历, 基列)
'                '-------------------------------------------------------------------------
'                If Left$(.Cells(1, 位谕of周层护型), 1) = "×" Then
'                        设定目列 = 位谕of周德竖态
'                        设定scheme = 37     '深红
'                '----------------------------------------------------
'                ElseIf Left$(.Cells(1, 位谕of周层护型), 1) = "魑" Then
'                        设定目列 = 位谕of周德竖态
'                        设定scheme = 34     '黄色
'                '----------------------------------------------------
'                ElseIf Left$(.Cells(1, 位谕of周层护型), 1) = "魅" Then
'                        设定目列 = 位谕of周道月势
'                        设定scheme = 44     '淡绿色
'                '----------------------------------------------------
'                Else
'                        设定目列 = 位谕of周基乾局
'                        设定scheme = 30
'                End If
'                '-------------------------------------------------------------------------
'                If Len(.Cells(1, 位谕of周道乾坤)) > 0 Then
'                With .Cells(1, 设定目列)
'                        '.Comment.Delete
'                        .AddComment
'                        .Comment.Visible = False
'                        .Comment.Shape.Width = 370
'                        .Comment.Shape.Height = 200
'                        .Comment.Shape.TextFrame.Characters.Font.Size = 10
'                        .Comment.Shape.TextFrame.Characters.Font.Name = "宋体"
'                        .Comment.Shape.Fill.Solid
'                        .Comment.text text:=WS.Cells(行号遍历, 基列).cells(1, 位谕of周道乾坤).Value
'                        .Comment.Shape.Fill.ForeColor.SchemeColor = 设定scheme
'                End With
'                End If
'                '-------------------------------------------------------------------------
'        End With
'        End If
'        '================================================================================
'        '格式类：买卖建议comment
'        '================================================================================
'        If 是否跨码 = True Then
'        With WS.Cells(行号遍历,基列)
'                值挂策 = ""
'                '-------------------------------------------------------------------------
'                If Len(.Cells(1, 位谕of仓操作)) > 0 Then
'                        值挂策 = 值挂策 & .Cells(1, 位谕of仓操作)
'                Else
'                        值挂策 = 值挂策 & "无需操作"
'                End If
'                '-------------------------------------------
'                值挂策 = 值挂策 & Chr(10) & String(20, "-")
'                值挂策 = 值挂策 & Chr(10) & "日挂卖价：" & Round(.Cells(1, 位qt今收) * (1 + .Cells(1, 位谕of日段十均幅高) / 100), 2)
'                值挂策 = 值挂策 & Chr(10) & "均日高幅%：" & Round(.Cells(1, 位谕of日段十均幅高) * 1#, 1)
'                值挂策 = 值挂策 & Chr(10) & "本日高幅%：" & Round(.Cells(1, 位谕of日波BSHR) * 1#, 1)
'                值挂策 = 值挂策 & Chr(10) & "> 涨9%：" & Round(.Cells(1, 位qt今收) * 1.09, 2)
'                值挂策 = 值挂策 & Chr(10) & "> 涨5%：" & Round(.Cells(1, 位qt今收) * 1.05, 2)
'                值挂策 = 值挂策 & Chr(10) & "> 涨3%：" & Round(.Cells(1, 位qt今收) * 1.03, 2)
'                值挂策 = 值挂策 & Chr(10) & "> 涨2%：" & Round(.Cells(1, 位qt今收) * 1.02, 2)
'                值挂策 = 值挂策 & Chr(10) & "> 涨0%：" & Round(.Cells(1, 位qt今收) * 1#, 2)
'                值挂策 = 值挂策 & Chr(10) & "均日涨幅%：" & Round(.Cells(1, 位谕of日段十均幅涨) * 1#, 1)
'                值挂策 = 值挂策 & Chr(10) & "本日涨幅%：" & Round(.Cells(1, 位谕of日波BSPR) * 1#, 1) & IIf(.Cells(1, 位谕of日波BSPR) >= .Cells(1, 位谕of日段十均幅涨), " 超", "")
'                '-------------------------------------------
'                值挂策 = 值挂策 & Chr(10) & String(20, "-")
'                值挂策 = 值挂策 & Chr(10) & "周挂卖价：" & Round(.Cells(1, 位谕of周波今收) * (1 + .Cells(1, 位谕of周波均高幅十) / 100), 2)
'                值挂策 = 值挂策 & Chr(10) & "均周高幅%：" & Round(.Cells(1, 位谕of周波均高幅十) * 1#, 1)
'                值挂策 = 值挂策 & Chr(10) & "上周高幅%：" & Round(.Cells(1, 位谕of周波今高幅) * 1#, 1)
'                值挂策 = 值挂策 & Chr(10) & "本周高幅%：" & Round(.Cells(1, 位谕of周波临高幅) * 1#, 1) & IIf(.Cells(1, 位谕of周波临高幅) >= .Cells(1, 位谕of周波均高幅十), " 超", "")
'                值挂策 = 值挂策 & Chr(10) & "> 涨9%：" & Round(.Cells(1, 位谕of周波今收) * 1.09, 2)
'                值挂策 = 值挂策 & Chr(10) & "> 涨5%：" & Round(.Cells(1, 位谕of周波今收) * 1.05, 2)
'                值挂策 = 值挂策 & Chr(10) & "> 涨3%：" & Round(.Cells(1, 位谕of周波今收) * 1.03, 2)
'                值挂策 = 值挂策 & Chr(10) & "> 涨2%：" & Round(.Cells(1, 位谕of周波今收) * 1.02, 2)
'                值挂策 = 值挂策 & Chr(10) & "> 涨0%：" & Round(.Cells(1, 位谕of周波今收) * 1#, 2)
'                值挂策 = 值挂策 & Chr(10) & "均周涨幅%：" & Round(.Cells(1, 位谕of周波均涨幅五) * 1#, 1)
'                值挂策 = 值挂策 & Chr(10) & "本周涨幅%：" & Round(.Cells(1, 位谕of周波临涨幅) * 1#, 1) & IIf(.Cells(1, 位谕of周波临涨幅) >= .Cells(1, 位谕of周波均涨幅五), " 超", "")
'                '-------------------------------------------
'                值挂策 = 值挂策 & Chr(10) & String(20, "-")
'                值挂策 = 值挂策 & Chr(10) & .Cells(1, 位qt代称)
'                值挂策 = 值挂策 & Chr(10) & "仓单位：" & .Cells(1, 位谕of仓限单)
'                值挂策 = 值挂策 & Chr(10) & "仓限倍：" & .Cells(1, 位谕of仓限倍)
'                值挂策 = 值挂策 & Chr(10) & "仓限手：" & .Cells(1, 位谕of仓限总)
'                值挂策 = 值挂策 & Chr(10) & "仓数总：" & .Cells(1, 位谕of仓持数)
'                值挂策 = 值挂策 & Chr(10) & "仓位比：" & Format(.Cells(1, 位谕of仓位比), "0%")
'                值挂策 = 值挂策 & Chr(10) & "仓额总：" & .Cells(1, 位谕of仓持额) & " 千"
'                '-------------------------------------------------------------------------
'                If .Cells(1, 位谕of仓持数) > 0 Then
'                With .Cells(1, 位谕of仓操作)
'                    .AddComment
'                    .Comment.Visible = False
'                    .Comment.Shape.Width = 100
'                    .Comment.Shape.Height = 360
'                    .Comment.text text:=值挂策
'                End With
'                End If
'                '-------------------------------------------------------------------------
'        End With
'        End If
        '================================================================================
    End If
    Next
'========================================================================================
'迷你图专区
'========================================================================================
'    Dim 是否迷你图 As Boolean
'    If WS.Name = 常仓名宝福 Or WS.Name = 常仓名宝彦 Then
'        是否迷你图 = True
'    Else
'        是否迷你图 = False
'    End If
''----------------------------------------------------------------------------------------
'If 是否迷你图 = True Then
'    WS.Columns(位谕of周波涨幅迷).Hidden = False
'    '------------------------------------------------------------------------------------
'    '遍历绘制
'    '------------------------------------------------------------------------------------
'    For 行号遍历 = 基行 To 末行
'    CIDL = WS.Cells(行号遍历,基列).cells(1,  位qt代码).Value
'    If UBCID是代码(CIDL) = True Then
'        '================================================================================
'        '迷你图
'        '================================================================================
'        With WS.Cells(行号遍历, 基列)
'                '----------------------------------------------------------------
'                '迷你图
'                '----------------------------------------------------------------
'                With WS.Cells(行号遍历,基列).cells(1,  位谕of周波涨幅迷)
'                        With .SparklineGroups
'                            .Add Type:=xlSparkColumn, SourceData:=WS.Cells(行号遍历,基列).cells(1,  位谕of周波涨幅4).Resize(1, 5).Address
'                            .Item(1).SeriesColor.Color = 常色六红
'                            .Item(1).Points.Negative.Visible = True
'                            .Item(1).Points.Negative.Color.Color = 常色四绿
'                            .Item(1).DisplayHidden = True
''                            .Item(1).Axes.Vertical.MaxScaleType = xlSparkScaleCustom
''                            .Item(1).Axes.Vertical.CustomMaxScaleValue = 10
''                            .Item(1).Axes.Vertical.MinScaleType = xlSparkScaleCustom
''                            .Item(1).Axes.Vertical.CustomMinScaleValue = -10
'                        End With
'                End With
'                '----------------------------------------------------------------
'        End With
'    End If
'    Next
'End If
'========================================================================================
'返回
'========================================================================================
    On Error GoTo 0
    IQQQ跨码展擎_按行汇总 = 末行
End Function



'----------------------------------------------------------------------------------------
'----------------------------------------------------------------------------------------
'废弃代码区
'----------------------------------------------------------------------------------------
'----------------------------------------------------------------------------------------
'                '========================================================================
'                '标注：周类叠幅
'                '========================================================================
'                '预警暴升：使用层差五
'                With .Cells(1, 位谕of周波今叠幅)
'                        '设置底色：根据极折
'                        If Right(WS.Cells(行号遍历,基列).cells(1,  位谕of周龟顶触), 1) = "高" Then
'                             .Interior.Color = 常色主靛
'                        ElseIf Right(WS.Cells(行号遍历,基列).cells(1,  位谕of周龟顶触), 1) = "撤" Then
'                             .Interior.Color = 常色六橙
'                        ElseIf Right(WS.Cells(行号遍历, 基列).cells(1, 位谕of周龟顶触), 1) = "弹" Then
'                             .Interior.Color = 常色四灰
'                        ElseIf Right(WS.Cells(行号遍历, 基列).cells(1, 位谕of周龟顶触), 1) = "低" Then
'                             .Interior.Color = 常色二灰
'                        End If
'                        '设置字体
'                        If .Value >= 30 Then
'                                .HorizontalAlignment = xlRight
'                                If .Value >= 50 Then
'                                    .Font.Bold = True
'                                End If
'                        Else
'                                .HorizontalAlignment = xlLeft
'                                If .Value <= 15 Then
'                                    .Font.Color = .Interior.Color
'                                    .Font.TintAndShade = -0.1
'                                End If
'                        End If
'                End With
'                '------------------------------------------------------------------------
'                If .Cells(1, 位谕of周龟BT哈) < .Cells(1, 位谕of周龟BT哼) Then
'                    If .Cells(1, 位谕of周波今叠幅) < .Cells(1, 位谕of周波均叠幅五) Then
'                        .Cells(1, 位谕of周波均叠幅五).Interior.Color = 常色十红
'                    End If
'                End If
                '========================================================================
                '标注：日波叠幅
                '========================================================================
'                '预警暴升：使用层差五
'                With .Cells(1, 位谕of日波叠幅)
'                        '设置底色：根据极折
'                        If Right(WS.Cells(行号遍历,基列).cells(1,  位谕of日龟顶触), 1) = "高" Then
'                             .Interior.Color = 常色主靛
'                        ElseIf Right(WS.Cells(行号遍历, 基列).cells(1, 位谕of日龟顶触), 1) = "撤" Then
'                             .Interior.Color = 常色六橙
'                        ElseIf Right(WS.Cells(行号遍历,基列).cells(1,  位谕of日龟顶触), 1) = "弹" Then
'                             .Interior.Color = 常色四灰
'                        ElseIf Right(WS.Cells(行号遍历, 基列).cells(1, 位谕of日龟顶触), 1) = "低" Then
'                             .Interior.Color = 常色二灰
'                        End If
'                        '设置字体
'                        If .Value >= 20 Then
'                                .HorizontalAlignment = xlRight
'                                If .Value >= 40 Then
'                                    .Font.Bold = True
'                                End If
'                        Else
'                                .HorizontalAlignment = xlLeft
'                                If .Value < 10 Then
'                                    .Font.Color = .Interior.Color
'                                    .Font.TintAndShade = -0.1
'                                ElseIf .Value < 15 Then
'                                    .Font.Color = .Interior.Color
'                                    .Font.TintAndShade = -0.4
'                                End If
'                        End If
'                End With
'                '========================================================================
'----------------------------------------------------------------------------------------
'----------------------------------------------------------------------------------------
'废弃代码区
'----------------------------------------------------------------------------------------
'----------------------------------------------------------------------------------------




'放入【按行操作】
Function IQQQ跨码展擎_校验持仓区域( _
      ByRef WS As Worksheet _
    , Optional ByVal 基行 As Integer = 1 _
    , Optional ByVal 基列 As Integer = 1 _
    ) As String
'========================================================================================
'声明变量
'========================================================================================
        If WS Is Nothing Then Exit Function
        '--------------------------------------------------------------------------------
        Dim CIDL As String
        Dim 值代称 As String
        '--------------------------------------------------------------------------------
        Dim MSG汇总 As String
        Dim MSG清仓 As String
        Dim MSG剔除 As String
        '--------------------------------------------------------------------------------
        Dim 典值池数 As New Dictionary
        With 典值池数
            .Add Key:="池全", Item:=0
            .Add Key:="池金", Item:=0
            .Add Key:="池白", Item:=0
            .Add Key:="池基", Item:=0
            .Add Key:="池外", Item:=0
        End With
        Dim 典值池额 As New Dictionary
        With 典值池额
            .Add Key:="池全", Item:=0
            .Add Key:="池金", Item:=0
            .Add Key:="池白", Item:=0
            .Add Key:="池基", Item:=0
            .Add Key:="池外", Item:=0
        End With
        Dim 典值池赚收 As New Dictionary
        With 典值池赚收
            .Add Key:="池全", Item:=0
            .Add Key:="池金", Item:=0
            .Add Key:="池白", Item:=0
            .Add Key:="池基", Item:=0
            .Add Key:="池外", Item:=0
        End With
        Dim 典值池赚高 As New Dictionary
        With 典值池赚高
            .Add Key:="池全", Item:=0
            .Add Key:="池金", Item:=0
            .Add Key:="池白", Item:=0
            .Add Key:="池基", Item:=0
            .Add Key:="池外", Item:=0
        End With
        Dim 典值池赚低 As New Dictionary
        With 典值池赚低
            .Add Key:="池全", Item:=0
            .Add Key:="池金", Item:=0
            .Add Key:="池白", Item:=0
            .Add Key:="池基", Item:=0
            .Add Key:="池外", Item:=0
        End With
'========================================================================================
'确定范围
'========================================================================================
        Dim 始行  As Integer
        始行 = 2
        Dim 末行 As Integer
        末行 = PBASE格程工具_表参定位特征行号(WS, 特征值:="核心指数")
        Dim 总行 As Integer
        总行 = 末行 - 始行 + 1
        If 总行 < 1 Then Exit Function
'========================================================================================
'校验
'========================================================================================
    值仓失垫计数 = 0
    Dim 行号遍历 As Integer
    For 行号遍历 = 始行 To 末行
        '================================================================================
        '甄别代码
        '================================================================================
        CIDL = WS.Cells(行号遍历, 位qt代码)
        If UBCID是代码(CIDL) = True Then
                '========================================================================
                '统计整体持仓情况
                '========================================================================
                值仓持额 = WS.Cells(行号遍历, 位谕of仓持额)
                值仓赚收 = WS.Cells(行号遍历, 位谕of仓赚收)
                值仓赚高 = WS.Cells(行号遍历, 位谕of仓赚高)
                值仓赚低 = WS.Cells(行号遍历, 位谕of仓赚低)
                '-----------------------------------------------------------------
                值仓持票汇总 = 值仓持票汇总 + 1
                值仓持额汇总 = 值仓持额汇总 + 值仓持额
                '========================================================================
                '待完成：            '根据对应大盘指数进行各自板块 大势的判断
                '========================================================================
                典值池数("池全") = 典值池数("池全") + 1
                典值池额("池全") = 典值池额("池全") + 值仓持额
                典值池赚收("池全") = 典值池赚收("池全") + 值仓赚收
                典值池赚高("池全") = 典值池赚高("池全") + 值仓赚高
                典值池赚低("池全") = 典值池赚低("池全") + 值仓赚低
                '-----------------------------------------------------------------
                If InStr(WS.Cells(行号遍历, 位qt盯盘类别), "O") > 0 Then
                    典值池数("池无") = 典值池数("池无") + 1
                    典值池额("池无") = 典值池额("池无") + 值仓持额
                    典值池赚收("池无") = 典值池赚收("池无") + 值仓赚收
                    典值池赚高("池无") = 典值池赚高("池无") + 值仓赚高
                    典值池赚低("池无") = 典值池赚低("池无") + 值仓赚低
                ElseIf InStr(WS.Cells(行号遍历, 位qt盯盘类别), "ETF") > 0 Then
                    典值池数("池基") = 典值池数("池基") + 1
                    典值池额("池基") = 典值池额("池基") + 值仓持额
                    典值池赚收("池基") = 典值池赚收("池基") + 值仓赚收
                    典值池赚高("池基") = 典值池赚高("池基") + 值仓赚高
                    典值池赚低("池基") = 典值池赚低("池基") + 值仓赚低
                Else
                    典值池数("池长") = 典值池数("池长") + 1
                    典值池额("池长") = 典值池额("池长") + 值仓持额
                    典值池赚收("池长") = 典值池赚收("池长") + 值仓赚收
                    典值池赚高("池长") = 典值池赚高("池长") + 值仓赚高
                    典值池赚低("池长") = 典值池赚低("池长") + 值仓赚低
                End If
                '========================================================================
                值仓肉垫 = WS.Cells(行号遍历, 位谕of仓肉垫)
                If 值仓肉垫 >= 0 Then
                    值仓肉垫汇总 = 值仓肉垫汇总 + 值仓肉垫
                Else
                    值仓失垫计数 = 值仓失垫计数 + 1
                End If
                '========================================================================
        End If
    Next
    '====================================================================================
    '汇总提示信息
    '====================================================================================
    If 值仓持额汇总 > 0 Then
            '-----------------------------------------------------------------
            MSG汇总 = MSG汇总 & "持仓分析：" & vbCrLf
            '-----------------------------------------------------------------
            MSG汇总 = MSG汇总 & vbCrLf
            MSG汇总 = MSG汇总 & "  总票：" & 典值池数("池全") & " / " & 典值池额("池全") & " (" & Format(典值池额("池全") / 值仓持额汇总, "0%") & ")" & vbCrLf
            MSG汇总 = MSG汇总 & "> 池长：" & 典值池数("池长") & " / " & 典值池额("池长") & " (" & Format(典值池额("池长") / 值仓持额汇总, "0%") & ")" & vbCrLf
            MSG汇总 = MSG汇总 & "> 池无：" & 典值池数("池无") & " / " & 典值池额("池无") & " (" & Format(典值池额("池无") / 值仓持额汇总, "0%") & ")" & vbCrLf
            MSG汇总 = MSG汇总 & "> 池基：" & 典值池数("池基") & " / " & 典值池额("池基") & " (" & Format(典值池额("池基") / 值仓持额汇总, "0%") & ")" & vbCrLf
            '-----------------------------------------------------------------
            MSG汇总 = MSG汇总 & vbCrLf
            MSG汇总 = MSG汇总 & "  总票：" & 典值池赚收("池全") & "   ( " & 典值池赚低("池全") & " , " & 典值池赚高("池全") & " ) " & vbCrLf
            MSG汇总 = MSG汇总 & "> 池长：" & 典值池赚收("池长") & "   ( " & 典值池赚低("池长") & " , " & 典值池赚高("池长") & " ) " & vbCrLf
            MSG汇总 = MSG汇总 & "> 池无：" & 典值池赚收("池无") & "   ( " & 典值池赚低("池无") & " , " & 典值池赚高("池无") & " ) " & vbCrLf
            MSG汇总 = MSG汇总 & "> 池基：" & 典值池赚收("池基") & "   ( " & 典值池赚低("池基") & " , " & 典值池赚高("池基") & " ) " & vbCrLf
            '-----------------------------------------------------------------
            MSG汇总 = MSG汇总 & vbCrLf
            MSG汇总 = MSG汇总 & ">  肉垫：" & 典值池额("池全") - Round(值仓肉垫汇总 / 1000, 1) & "   ( " & 值仓肉垫汇总 & " , " & 值仓失垫计数 & " 失垫) " & vbCrLf
            '-----------------------------------------------------------------
            MSG汇总 = MSG汇总 & ">  只可顺守，不可逆取，不要怕输，不要怕盈" & vbCrLf
            '-----------------------------------------------------------------
    End If
'========================================================================================
'返回
'========================================================================================
    IQQQ跨码展擎_校验持仓区域 = MSG汇总
End Function








''========================================================================================
''========================================================================================
''子程：OS格式化
''========================================================================================
''========================================================================================
'Function PCALL更新引擎格程OS子程( _
'          WS As Worksheet _
'        , Optional 基列 As Integer = 花列甲道 _
'        , Optional 基色底 As Long = 常色指金 _
'        ) As Integer
''========================================================================================
''清理格式化
''========================================================================================
'    With WS.Cells(1, 基列).Resize(1, 花宽单道 * 3).EntireColumn
'        .ClearFormats
'        .Interior.ColorIndex = 56
'        .Font.Size = 10
'    End With
''========================================================================================
''基础格式化
''========================================================================================
'    Dim 列定位 As Integer
'    列定位 = 基列
'    列定位 = IQQQ跨码展擎_按列OS区域(WS, 列定位, 基色底:=基色底, 基色调:=0.7)
'    列定位 = IQQQ跨码展擎_按列OS区域(WS, 列定位, 基色底:=基色底, 基色调:=0.6)
'    列定位 = IQQQ跨码展擎_按列OS区域(WS, 列定位, 基色底:=基色底, 基色调:=0.3)
''========================================================================================
''特殊格式化：行格式
''========================================================================================
'    Dim 行号遍历 As Integer
'    For 行号遍历 = 2 To PBASE格程工具_表参末行指定(ws, 基列)
'        '--------------------------------------------------------------------------------
'        '针对空行
'        '--------------------------------------------------------------------------------
'        If UBCID是代码(WS.Cells(行号遍历, 位qt代码).Value) = False Then
'            '分割：将颜色设置为蓝色
'            With WS.Cells(行号遍历, 基列).Resize(1, 花宽单道 * 3)
'                .Interior.Color = 基色底
'                .Interior.TintAndShade = 0
'            End With
'        End If
'        '--------------------------------------------------------------------------------
'    Next 行号遍历
''========================================================================================
''显示
''========================================================================================
'    WS.Cells(1, 基列).Resize(1, 花宽单道 * 3).EntireColumn.Hidden = True
''========================================================================================
''返回
''========================================================================================
'    PCALL更新引擎格程OS子程 = 列定位
''========================================================================================
'End Function


'========================================================================================
'========================================================================================
'基程：OS部分
'========================================================================================
'========================================================================================
Function IQQQ跨码展擎_按列OS区域( _
          ByRef WS As Worksheet _
        , ByVal 基列 As Integer _
        , Optional ByVal 标行 As Integer = 1 _
        , Optional ByVal 基色底 As Long = 常色指金 _
        , Optional ByVal 基色调 As Double = 0.5 _
        ) As Integer
'========================================================================================
'全局
'========================================================================================
    '------------------------------------------------------------------------------------
    '全部字体
    '------------------------------------------------------------------------------------
    With WS.Cells(标行, 基列).Resize(1, 花宽单道).EntireColumn
        .Font.Size = 10
        .Font.Color = 常色主黑
        .Font.TintAndShade = 0.3
    End With
    '------------------------------------------------------------------------------------
    '全部底纹
    '------------------------------------------------------------------------------------
    Dim 末行 As Integer
    末行 = PBASE格程工具_表参末行指定(WS, 位os代码)
    
    With WS.Cells(标行, 基列).Resize(末行, 花宽单道)
        .Interior.Color = 基色底
        .Interior.TintAndShade = 基色调
    End With
'========================================================================================
'标题内容
'========================================================================================
    With WS.Cells(标行, 基列).Resize(1, 花宽单道)
        .VerticalAlignment = xlTop
        .HorizontalAlignment = xlRight
        .Interior.Color = 基色底
        .Interior.TintAndShade = -0.1
        .Font.Color = 常色主黑
        .Font.Bold = True
    End With
    '------------------------------------------------------------------------------------
    With WS.Cells(标行, 基列)
        '-----------------------------------------
        .Cells(1, 位os代码) = "CIDL"
        .Cells(1, 位os基代称) = "代称"
        .Cells(1, 位os期类) = "I"
         '----------------------------------------
        .Cells(1, 位os基累龄) = "累龄"
        .Cells(1, 位os基市期) = "市日"
        .Cells(1, 位os停牌) = "停牌"
         '----------------------------------------
        .Cells(1, 位os前期) = "前日"
        .Cells(1, 位os前收) = "前收"
        .Cells(1, 位os前开) = "前开"
        .Cells(1, 位os前高) = "前高"
        .Cells(1, 位os前低) = "前低"
        '------
        .Cells(1, 位os结期) = "结日"
        .Cells(1, 位os结收) = "结收"
        .Cells(1, 位os结开) = "结开"
        .Cells(1, 位os结高) = "结高"
        .Cells(1, 位os结低) = "结低"
        '------
        .Cells(1, 位os临期) = "临日"
        .Cells(1, 位os临收) = "临收"
        .Cells(1, 位os临开) = "临开"
        .Cells(1, 位os临高) = "临高"
        .Cells(1, 位os临低) = "临低"
        '----------------------------------------
        .Cells(1, 位os结幅PR0) = "结涨幅"
        .Cells(1, 位os结幅PR1) = "PR1"
        .Cells(1, 位os结幅PR2) = "PR2"
        .Cells(1, 位os结幅PR3) = "PR3"
        .Cells(1, 位os结幅PR4) = "PR4"
        .Cells(1, 位os结幅PR5) = "PR5"
        .Cells(1, 位os结幅PR6) = "PR6"
        .Cells(1, 位os结幅PR7) = "PR7"
        .Cells(1, 位os结幅PR8) = "PR8"
        .Cells(1, 位os结幅PR9) = "PR9"
        '------
        .Cells(1, 位os结幅HR0) = "结高幅"
        .Cells(1, 位os结幅HR1) = "HR1"
        .Cells(1, 位os结幅HR2) = "HR2"
        .Cells(1, 位os结幅HR3) = "HR3"
        .Cells(1, 位os结幅HR4) = "HR4"
        .Cells(1, 位os结幅HR5) = "HR5"
        .Cells(1, 位os结幅HR6) = "HR6"
        .Cells(1, 位os结幅HR7) = "HR7"
        .Cells(1, 位os结幅HR8) = "HR8"
        .Cells(1, 位os结幅HR9) = "HR9"
        '----------------------------------------
        .Cells(1, 位osJZ) = "JZ"
        .Cells(1, 位osJA) = "JA"
        .Cells(1, 位osJB) = "JB"
        .Cells(1, 位osJC) = "JC"
        .Cells(1, 位osJD) = "JD"
        .Cells(1, 位osJE) = "JE"
        .Cells(1, 位osJF) = "JF"
        .Cells(1, 位osJG) = "JG"
        '------
        .Cells(1, 位osBTPR0) = "TPP"
        '------
        .Cells(1, 位osBTZA) = "TZA"
        .Cells(1, 位osBTZB) = "TZB"
        .Cells(1, 位osBTZC) = "TZC"
        .Cells(1, 位osBTZD) = "TZD"
        .Cells(1, 位osBTZE) = "TZE"
        .Cells(1, 位osBTZF) = "TZF"
        .Cells(1, 位osBTZG) = "TZG"
        '------
        .Cells(1, 位osBTAB) = "TAB"
        .Cells(1, 位osBTAC) = "TAC"
        .Cells(1, 位osBTBC) = "TBC"
        .Cells(1, 位osBTAD) = "TAD"
        .Cells(1, 位osBTBD) = "TBD"
        .Cells(1, 位osBTCD) = "TCD"
        .Cells(1, 位osBTAE) = "TAE"
        .Cells(1, 位osBTCE) = "TCE"
        .Cells(1, 位osBTDE) = "TDE"
        .Cells(1, 位osBTAF) = "TAF"
        .Cells(1, 位osBTCF) = "TCF"
        .Cells(1, 位osBTDF) = "TDF"
        .Cells(1, 位osBTEF) = "TEF"
        .Cells(1, 位osBTAG) = "TZD"
        .Cells(1, 位osBTCG) = "TBD"
        .Cells(1, 位osBTEG) = "TZE"
        .Cells(1, 位osBTFG) = "TBE"
        '----------------------------------------
        .Cells(1, 位os算法名) = "算法"
        .Cells(1, 位os算今仓) = "今仓"
        .Cells(1, 位os算今手) = "今手"
        .Cells(1, 位os算今赚) = "今赚"
        .Cells(1, 位os算累赚) = "累赚"
        .Cells(1, 位os算累持) = "累持"
        '----------------------------------------
        .Cells(1, 位os局势周基) = "周基势局"
        .Cells(1, 位os局势日基) = "日基势局"
        .Cells(1, 位os局ZEFG) = "值局ZEFG"
        .Cells(1, 位os局ZCDE) = "值局ZCDE"
        .Cells(1, 位os局ZABC) = "值局ZABC"
        '----------------------------------------
        .Cells(1, 位os具锚ZD) = "锚ZD"
        .Cells(1, 位os具锚ZC) = "锚ZC"
        .Cells(1, 位os具BT鼎) = "T鼎"
        '----------------------------------------
        .Cells(1, 位os奏数DE叉DC) = "数DE叉DC"
        .Cells(1, 位os奏数DE叉CB) = "数DE叉CB"
        .Cells(1, 位os奏数DE叉EZ) = "数DE叉EZ"
        .Cells(1, 位os奏数DE叉DZ) = "数DE叉DZ"
        '----------------------------------------
        .Cells(1, 位os奏数BC叉BA) = "数BC叉BA"
        '----------------------------------------
        .Cells(1, 位os龟前顶) = "前顶"
        .Cells(1, 位os龟结顶) = "结顶"
        .Cells(1, 位os龟临顶) = "临顶"
        .Cells(1, 位os龟BT顶) = "BT顶"
        .Cells(1, 位os龟前底) = "前底"
        .Cells(1, 位os龟结底) = "结底"
        .Cells(1, 位os龟临底) = "临底"
        .Cells(1, 位os龟BT底) = "BT底"
        .Cells(1, 位os龟前哼) = "前哼"
        .Cells(1, 位os龟结哼) = "结哼"
        .Cells(1, 位os龟临哼) = "临哼"
        .Cells(1, 位os龟BT哼) = "BT哼"
        .Cells(1, 位os龟前哈) = "前哈"
        .Cells(1, 位os龟结哈) = "结哈"
        .Cells(1, 位os龟临哈) = "临哈"
        .Cells(1, 位os龟BT哈) = "BT哈"
        '----------------------------------------
        .Cells(1, 位os具并符串) = "并符"
        .Cells(1, 位os具中符串) = "中符"
        .Cells(1, 位os具上符串) = "上符"
        .Cells(1, 位os具宽符串) = "宽符"
        '----------------------------------------
    End With
'========================================================================================
'边框
'========================================================================================
    With WS.Columns(基列)
        With .Borders(xlEdgeLeft)
            .LineStyle = xlContinuous
            .Color = 常色主黑
            .Weight = xlMedium
        End With
        With .Columns(花宽单道).Borders(xlEdgeRight)
            .LineStyle = xlContinuous
            .Color = 常色主黑
            .Weight = xlMedium
        End With
    End With
'========================================================================================
'列格式
'========================================================================================
'    With WS.Columns(基列)
'        .Columns(位os基市期).NumberFormatLocal = 全设格式of日期
'        .Columns(位os结期).NumberFormatLocal = 全设格式of日期
'        .Columns(位os结幅PR0).NumberFormatLocal = 全设格式of一位
'        .Columns(位os前收).NumberFormatLocal = 全设格式of价格
'        .Columns(位os结收).NumberFormatLocal = 全设格式of价格
'        .Columns(位osJZ).NumberFormatLocal = 全设格式of价格
'        .Columns(位osJA).NumberFormatLocal = 全设格式of价格
'        .Columns(位osJB).NumberFormatLocal = 全设格式of价格
'        .Columns(位osJC).NumberFormatLocal = 全设格式of价格
'        .Columns(位osJD).NumberFormatLocal = 全设格式of价格
'        .Columns(位osJE).NumberFormatLocal = 全设格式of价格
'        .Columns(位osJF).NumberFormatLocal = 全设格式of价格
'        .Columns(位os算今手).NumberFormatLocal = 全设格式of零位
'    End With
    '---------------------------------------------------------------------------------
    With WS.Cells(标行, 基列).Resize(1, 花宽单道).EntireColumn
        .Columns.NumberFormatLocal = "0_);[蓝色](0)"
        .Columns(位os基市期).NumberFormatLocal = 全设格式of日期
        .Columns(位os前期).NumberFormatLocal = 全设格式of日期
        .Columns(位os结期).NumberFormatLocal = 全设格式of日期
        .Columns(位os临期).NumberFormatLocal = 全设格式of日期
        '其他列
        .ColumnWidth = 4
    End With
    With WS.Columns(基列)
        .Columns(位os代码).ColumnWidth = 9
        .Columns(位os基代称).ColumnWidth = 8
        .Columns(位os基市期).ColumnWidth = 9
        .Columns(位os基累龄).ColumnWidth = 6
        .Columns(位os期类).ColumnWidth = 2
        .Columns(位os停牌).ColumnWidth = 2
        '-------------------------------------
        .Columns(位os结幅PR0).ColumnWidth = 6
        
        .Columns(位os前收).ColumnWidth = 7
        .Columns(位os前开).ColumnWidth = 7
        .Columns(位os前高).ColumnWidth = 7
        .Columns(位os前低).ColumnWidth = 7
        .Columns(位os前期).ColumnWidth = 9
        .Columns(位os结收).ColumnWidth = 7
        .Columns(位os结开).ColumnWidth = 7
        .Columns(位os结高).ColumnWidth = 7
        .Columns(位os结低).ColumnWidth = 7
        .Columns(位os结期).ColumnWidth = 9
        .Columns(位os临收).ColumnWidth = 7
        .Columns(位os临开).ColumnWidth = 7
        .Columns(位os临高).ColumnWidth = 7
        .Columns(位os临低).ColumnWidth = 7
        .Columns(位os临期).ColumnWidth = 9
        '-------------------------------------
        .Columns(位osJZ).ColumnWidth = 8
        .Columns(位osJA).ColumnWidth = 8
        .Columns(位osJB).ColumnWidth = 8
        .Columns(位osJC).ColumnWidth = 8
        .Columns(位osJD).ColumnWidth = 8
        .Columns(位osJE).ColumnWidth = 8
        .Columns(位osJF).ColumnWidth = 8
        '-------------------------------------
        .Columns(位os算法名).ColumnWidth = 8
        .Columns(位os算累持).ColumnWidth = 4
        .Columns(位os算累赚).ColumnWidth = 6
        .Columns(位os算今赚).ColumnWidth = 6
        .Columns(位os算今手).ColumnWidth = 6
        .Columns(位os算今仓).ColumnWidth = 4
        '-------------------------------------
        .Columns(位os局势周基).ColumnWidth = 2
        .Columns(位os局势日基).ColumnWidth = 2
        .Columns(位os局ZEFG).ColumnWidth = 2
        .Columns(位os局ZCDE).ColumnWidth = 2
        .Columns(位os局ZABC).ColumnWidth = 2
        '-------------------------------------
        .Columns(位os具锚ZD).ColumnWidth = 5
        .Columns(位os具锚ZC).ColumnWidth = 5
        '-------------------------------------
    End With
    '---------------------------------------------------------------------------------
    WS.Cells(标行, 基列).Resize(1, 花宽单道).EntireColumn.Columns.Hidden = True
    With WS.Columns(基列)
        '-------------------------------------
        .Columns(位os代码).Hidden = False
        .Columns(位os期类).Hidden = False
        .Columns(位os基累龄).Hidden = False
        .Columns(位os停牌).Hidden = False
        '-------------------------------------
        .Columns(位os结期).Hidden = False
        .Columns(位os结幅PR0).Hidden = False
        .Columns(位os结收).Hidden = False
'        .Columns(位os结开).Hidden = False
        .Columns(位os结高).Hidden = False
'        .Columns(位os结低).Hidden = False
'        .Columns(位os临期).Hidden = False
'        .Columns(位os临收).Hidden = False
'        .Columns(位os临开).Hidden = False
'        .Columns(位os临高).Hidden = False
'        .Columns(位os临低).Hidden = False
        '-------------------------------------
'        .Columns(位os局势周基).Hidden = False
'        .Columns(位os局势日基).Hidden = False
        .Columns(位os局ZEFG).Hidden = False
        .Columns(位os局ZCDE).Hidden = False
        .Columns(位os局ZABC).Hidden = False
        '-------------------------------------
    End With
'========================================================================================
'清理
'========================================================================================
    'WS.Columns(基列).Columns(位os结量).ClearContents
'========================================================================================
'返回
'========================================================================================
    IQQQ跨码展擎_按列OS区域 = 基列 + 花宽单道
End Function
'########################################################################################
'########################################################################################
'##################################     更新引擎格程     ################################
'########################################################################################
'########################################################################################







'########################################################################################
'##################################      表格冻结      ##################################
'########################################################################################
'========================================================================================
'========================================================================================
'格式化：冻结
'========================================================================================
'========================================================================================
Function PBASE格程工具_表冻结取消(WS As Worksheet) As Boolean
    '------------------------------------------------------------------------------------
    WS.Activate
    With ActiveWindow
        .WindowState = xlMaximized
        .FreezePanes = False
        .Split = False
        .SplitRow = 0
        .SplitColumn = 0
    End With
    PBASE格程工具_表冻结取消 = True
    '------------------------------------------------------------------------------------
End Function
Function PBASE格程工具_表冻结锁定(WS As Worksheet, Optional 基行 As Integer = 1, Optional 基列 As Integer = 0, Optional 缩放 As Integer = 80) As Boolean
    '------------------------------------------------------------------------------------
    PBASE格程工具_表冻结取消 WS
    WS.Cells(1, 1).Select
    '------------------------------------------------------------------------------------
    With ActiveWindow
        .LargeScroll toleft:=2
        .SplitRow = 基行
        .SplitColumn = 基列
        .Split = True
        .FreezePanes = True
    End With
    '------------------------------------------------------------------------------------
    ActiveWindow.Zoom = 缩放
    PBASE格程工具_表冻结锁定 = True
    '------------------------------------------------------------------------------------
End Function
'Sub PBASE格程工具_表冻结锁定测试()
'    Dim WS As Worksheet
'    Set WS = ThisWorkbook.ActiveSheet
'    Call PBASE格程工具_表冻结锁定(WS, 55, 0)
'End Sub
'########################################################################################
'##################################      表格冻结      ##################################
'########################################################################################



