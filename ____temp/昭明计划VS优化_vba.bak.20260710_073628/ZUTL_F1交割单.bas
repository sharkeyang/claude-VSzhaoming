Attribute VB_Name = "ZUTL_F1交割单"
Option Explicit
Public Const 常册交割单 = "花割"
Public Const 位列割证券CIDL = 3
Public Const 位列割证券代码 = 4
Public Const 位列割证券名称 = 5
Public Const 位列割成交日期 = 1
Public Const 位列割成交时间 = 2
Public Const 位列割委托类别 = 6
Public Const 位列割成交数量 = 8
Public Const 位列割成交金额 = 9
Public Const 位列割发生金额 = 10
Public Const 位列割佣金 = 11
Public Const 位列割印花税 = 12
Public Const 位列割过户费 = 13
Public Const 位列割其他费 = 14
Public Const 位列割成交编号 = 15

'========================================================================================
'========================================================================================
'导入信息：交割单
'========================================================================================
'========================================================================================
Sub STCALL割册管理_瓜分交割单()
'========================================================================================
'验证文件存在
'========================================================================================
'    If UTL判断工表存在(常册交割单) = False Then
'        Debug.Print 常册交割单 & "不存在"
'        Exit Sub
'    End If
'========================================================================================
'益盟：导入文件
'========================================================================================
    Dim FILEOPEN
    FILEOPEN = Application.GetOpenFilename("华宝交割单信息,*.xls", , "华宝交割单信息xls", , False)
    If FILEOPEN = False Then
        Exit Sub
    End If
'========================================================================================
    UTL宏工具_BEGIN
'========================================================================================
'    Dim 位列割证券CIDL As Integer
'    Dim 位列割证券代码 As Integer
'    Dim 位列割证券名称 As Integer
'    Dim 位列割成交日期 As Integer
'    Dim 位列割成交时间 As Integer
'    Dim 位列割委托类别 As Integer
'    Dim 位列割成交数量 As Integer
    '------------------------------------------------------------------------------------
    '导入数组
    '------------------------------------------------------------------------------------
    Dim WB割 As Workbook
    Set WB割 = GetObject(FILEOPEN)
    Dim ARRYM As Variant
    With WB割.ActiveSheet
        ARRYM = .Range("A1").CurrentRegion
'        位列割证券代码 = .Rows(1).Find(what:="证券代码").Column
'        位列割证券名称 = .Rows(1).Find(what:="证券名称").Column
'        位列割成交日期 = .Rows(1).Find(what:="成交日期").Column
'        位列割成交时间 = .Rows(1).Find(what:="成交时间").Column
'        位列割委托类别 = .Rows(1).Find(what:="委托类别").Column
'        位列割证券CIDL = .Rows(1).Find(what:="股东代码").Column
'        位列割成交数量 = .Rows(1).Find(what:="成交数量").Column
    End With
    WB割.Close False
    Set WB割 = Nothing
'========================================================================================
'益盟：输出中间工作表
'========================================================================================
'    '------------------------------------------------------------------------------------
'    '建立工作簿
'    '------------------------------------------------------------------------------------
'    Dim WS割 As Worksheet
'    Call PBASE格程工具_表操工表新增(WS割, "IO割", WB:=ThisWorkbook, 基色底:=常色十红)
'    '------------------------------------------------------------------------------------
'    '输出数组
'    '------------------------------------------------------------------------------------
'    Call UTL数据转换_集ARR2WS(ARRYM, WS割, 始行:=1)
'    '------------------------------------------------------------------------------------
'    '格式化
'    '------------------------------------------------------------------------------------
'    WS割.Rows(1).Font.Bold = True
'    WS割.Columns(位列割证券代码).NumberFormatLocal = 全设格式of代码
'    WS割.Columns.AutoFit
'    '------------------------------------------------------------------------------------
'    '按照代码进行排序
'    '------------------------------------------------------------------------------------
'    WS割.Cells.Sort key1:=WS割.Cells(1, 位列割成交日期), order1:=xlAscending _
'                  , key2:=WS割.Cells(1, 位列割成交时间), order2:=xlAscending _
'                  , key3:=WS割.Cells(1, 位列割证券代码), order3:=xlAscending _
'                  , Header:=xlYes
'    '------------------------------------------------------------------------------------
'    WS割.Activate
'    ActiveWindow.Zoom = 80
'    Debug.Print WS割.Cells(65536, 位列割证券代码).End(xlUp).Row
'    Set WS割 = Nothing
'    '------------------------------------------------------------------------------------
'Stop
'Exit Sub
'========================================================================================
'割册：瓜分
'========================================================================================
    Dim 典集委类组合费用 As New Dictionary
    Dim 典集委类申购还款 As New Dictionary
    Dim 典集委类申购扣款 As New Dictionary
    Dim 典集委类中签通知 As New Dictionary
    Dim 典集委类中签扣款 As New Dictionary
    Dim 典集委类托管转入 As New Dictionary
    Dim 典集委类托管转出 As New Dictionary
    Dim 典集委类融券 As New Dictionary
    Dim 典集委类融券购回 As New Dictionary
    Dim 典集委类其他 As New Dictionary
    Dim 典集委类红利 As New Dictionary
    Dim 典集委类配号 As New Dictionary
    Dim 典集委类交易码票 As New Dictionary
    Dim 典集委类交易码基 As New Dictionary
    Dim 典集委类交易码他 As New Dictionary
    '------------------------------------------------------------------------------------
    '制作字典
    '------------------------------------------------------------------------------------
    Dim CIDV As Variant
    Dim CIDL As String
    Dim sdate As String
    Dim R As Integer
    Dim 值委托类别 As String
    Dim 表名 As String
    Dim X As Integer
    For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
        值委托类别 = ARRYM(R, 位列割委托类别)
        sdate = ARRYM(R, 位列割成交日期)
        ARRYM(R, 位列割成交日期) = DateSerial(Left$(sdate, 4), Mid$(sdate, 5, 2), Mid$(sdate, 7, 2))
        '-----------------------------------------------
        If 值委托类别 = "申购还款" Then
            典集委类申购还款.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "申购扣款" Then
            典集委类申购扣款.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "中签扣款" Then
            典集委类中签扣款.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "中签通知" Then
            典集委类中签通知.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "配号" Then
            典集委类配号.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "托管转入" Then
            典集委类托管转入.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "托管转出" Then
            典集委类托管转出.Add Key:=R, Item:=R
        '-----------------------------------------------
        ElseIf 值委托类别 = "融券" Then
            典集委类融券.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "融券购回" Then
            典集委类融券购回.Add Key:=R, Item:=R
        '-----------------------------------------------
        ElseIf 值委托类别 = "组合费用" Then
            典集委类组合费用.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "其他" Then
            典集委类其他.Add Key:=R, Item:=R
        ElseIf 值委托类别 = "红利" Then
            典集委类红利.Add Key:=R, Item:=R
        '-----------------------------------------------
        ElseIf 值委托类别 = "买入" Or 值委托类别 = "卖出" Then
            CIDV = ARRYM(R, 位列割证券代码)
            CIDL = UBCID规制代码(CIDV)
            ARRYM(R, 位列割证券CIDL) = CIDL
            If 值委托类别 = "买入" Then
                ARRYM(R, 位列割成交数量) = 1 * ARRYM(R, 位列割成交数量)
            ElseIf 值委托类别 = "卖出" Then
                ARRYM(R, 位列割成交数量) = -1 * ARRYM(R, 位列割成交数量)
            End If
            If UBCID是中股基(CIDL) = True Then
                If 典集委类交易码票.Exists(CIDL) = False Then 典集委类交易码票.Add Key:=CIDL, Item:=CIDL
            ElseIf UBCID是中股票(CIDL) = True Then
                If 典集委类交易码票.Exists(CIDL) = False Then 典集委类交易码票.Add Key:=CIDL, Item:=CIDL
            Else
                典集委类交易码他.Add Key:=R, Item:=R
            End If
        '-----------------------------------------------
        Else
            Stop
            '出现了未曾出现过的委托类别
        End If
    Next R
    '------------------------------------------------------------------------------------
    '输出
    '------------------------------------------------------------------------------------
    Dim wb As Workbook
    Set wb = ThisWorkbook
    '--------------------------------------------------------------------------------
    '买卖相关
    '--------------------------------------------------------------------------------
    Dim 典集码类额 As New Dictionary
    Dim 典集码类数零近 As New Dictionary
    Dim 典集码类数零赚 As New Dictionary
    Dim 典集码类数零赔 As New Dictionary
    Dim 典集码类数正 As New Dictionary
    Dim 典集码类数负 As New Dictionary
    Dim 值累数 As Long
    Dim 值累额 As Double
    Dim 值成交日期 As Date
    Dim 值累额码类数正 As Double
    Dim 值累额码类数负 As Double
    Dim 值累额码类数零近月 As Double
    Dim 值累额码类数零远赚 As Double
    Dim 值累额码类数零远赔 As Double
    For X = 1 To 典集委类交易码票.Count
        CIDL = 典集委类交易码票.Keys(X - 1)
        值累数 = 0
        值累额 = 0
        值成交日期 = Date - 200
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                值累数 = 值累数 + ARRYM(R, 位列割成交数量)
                值累额 = 值累额 + ARRYM(R, 位列割发生金额)
                If ARRYM(R, 位列割成交日期) > 值成交日期 Then 值成交日期 = ARRYM(R, 位列割成交日期)
            End If
        Next R
        If 值累数 > 0 Then
                典集码类数正.Add Key:=CIDL, Item:=值累数
                值累额码类数正 = 值累额码类数正 + 值累额
        ElseIf 值累数 < 0 Then
                典集码类数负.Add Key:=CIDL, Item:=值累数
                值累额码类数负 = 值累额码类数负 + 值累额
        Else
            '过滤近30天交易
            If 值成交日期 >= Date - 30 Then
                典集码类数零近.Add Key:=CIDL, Item:=值累数
                值累额码类数零近月 = 值累额码类数零近月 + 值累额
            ElseIf 值累额 >= 0 Then
                典集码类数零赚.Add Key:=CIDL, Item:=值累数
                值累额码类数零远赚 = 值累额码类数零远赚 + 值累额
            Else
                典集码类数零赔.Add Key:=CIDL, Item:=值累数
                值累额码类数零远赔 = 值累额码类数零远赔 + 值累额
            End If
        End If
        典集码类额.Add Key:=CIDL, Item:=值累额
        Debug.Print X, CIDL, 值累数
'        If X > 55 Then Exit For
    Next X
    '--------------------------------------------------------------------------------
    表名 = "IO割BS"
    Call IQQQ展擎出程至页割版(wb, 表名, 是否建表:=True, 章色:=常色四青, 章签:="【交易】")
    Dim 典集委类交易个票 As New Dictionary
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(wb, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】类数〇（近30日）：" & 典集码类数零近.Count & " , " & 值累额码类数零近月)
    For X = 1 To 典集码类数零近.Count
        CIDL = 典集码类数零近.Keys(X - 1)
       For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色主靛, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(wb, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】类数〇（远赚）：" & 典集码类数零赚.Count & " , " & 值累额码类数零远赚)
    For X = 1 To 典集码类数零赚.Count
        CIDL = 典集码类数零赚.Keys(X - 1)
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色主靛, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(wb, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】类数〇（远赔）：" & 典集码类数零赔.Count & " , " & 值累额码类数零远赔)
    For X = 1 To 典集码类数零赔.Count
        CIDL = 典集码类数零赔.Keys(X - 1)
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色主靛, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(wb, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】类数正（未清仓）：" & 典集码类数正.Count)
    For X = 1 To 典集码类数正.Count
        CIDL = 典集码类数正.Keys(X - 1)
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色主靛, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(wb, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】类数负（不完整）：" & 典集码类数负.Count)
    For X = 1 To 典集码类数负.Count
        CIDL = 典集码类数负.Keys(X - 1)
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色主靛, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Set 典集委类交易个票 = Nothing
    '--------------------------------------------------------------------------------
    '剔除类别 新股相关
    '--------------------------------------------------------------------------------
    '表名 = "IO割SS"
    '剔除类别
    Call IQQQ展擎出程至页割版(wb, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【剔除类别】")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色八蓝, 典码输出:=典集委类融券, 区签:="融券", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色八蓝, 典码输出:=典集委类融券购回, 区签:="融券购回", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色六蓝, 典码输出:=典集委类其他, 区签:="其他", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色六蓝, 典码输出:=典集委类红利, 区签:="红利", 区释:="")
    'Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色十红, 典码输出:=典集委类组合费用, 区签:="组合费用", 区释:="")
    '新股相关
    Call IQQQ展擎出程至页割版(wb, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【新股类别】")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色六青, 典码输出:=典集委类申购还款, 区签:="申购还款", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色六青, 典码输出:=典集委类申购扣款, 区签:="申购扣款", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色六青, 典码输出:=典集委类中签扣款, 区签:="中签扣款", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色六青, 典码输出:=典集委类中签通知, 区签:="中签通知", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色四青, 典码输出:=典集委类托管转入, 区签:="托管转入", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色四青, 典码输出:=典集委类托管转出, 区签:="托管转出", 区释:="")
    Call IQQQ展擎出程至页割版(wb, 表名, ARRYM, 基色底:=常色二青, 典码输出:=典集委类配号, 区签:="配号", 区释:="")
'========================================================================================
    UTL宏工具_END
    MSG = "导入华宝交割单" & vbCrLf
'    STCALL花册管理_重制花天P2正程导入益盟 = MSG
End Sub




'========================================================================================
'注意：【表名输出】（工表的名字）不能是数字类型
'========================================================================================
Function IQQQ展擎出程至页割版( _
          ByRef wb As Workbook _
        , ByVal 表名输出 As String _
        , Optional ByRef 谕组 As Variant _
        , Optional ByRef 典码输出 As Dictionary _
        , Optional ByVal 区签 As String = "" _
        , Optional ByVal 区释 As String = "" _
        , Optional ByVal 基色底 As Long = 常色主碧 _
        , Optional ByVal 神谕归类 As Integer = 0 _
        , Optional ByVal 强列 As Integer = 0 _
        , Optional ByVal 强序 As XlSortOrder = xlDescending _
        , Optional ByVal 节签 As String = "" _
        , Optional ByVal 节色 As Long = 常色主白 _
        , Optional ByVal 章签 As String = "" _
        , Optional ByVal 章色 As Long = 常色主碧 _
        , Optional ByVal 是否建表 As Boolean = False _
        , Optional ByVal 计列输出 As Integer = 15 _
        ) As String
'========================================================================================
'设置
'========================================================================================
    Dim 割列标签类别 As Integer
    割列标签类别 = 1
    Dim 割列标签注释 As Integer
    割列标签注释 = 2
    Dim 割列标签计数 As Integer
    割列标签计数 = 3
'========================================================================================
'准备工作
'========================================================================================
    '------------------------------------------------------------------------------------
    '建页
    '------------------------------------------------------------------------------------
    Dim WSTO As Worksheet
    If 是否建表 = True Or UTL判断工表存在(表名输出, wb) = False Then
        Call PBASE格程工具_表操工表新增(WSTO, 表名输出, wb:=wb, 基色底:=章色)
'        Call IQQQ跨码展擎_按列汇总(WSTO, 基色底:=章色)
            '============================================================================
            '全局设置
            '============================================================================
            WSTO.Tab.Color = 常色主黑
            With WSTO.Cells
                .ClearFormats
                .Interior.ColorIndex = 56
                .Font.Name = "宋体"
                .Font.Size = 10
            End With
            '============================================================================
            '调整与冻结
            '注意：此步骤要放在其他过程前面
            '============================================================================
            WSTO.Rows.Hidden = False
            WSTO.Columns.Hidden = False
            Call PBASE格程工具_表冻结锁定(WSTO, 基列:=2)
            '============================================================================
    End If
    Set WSTO = wb.Sheets(表名输出)
    Dim 末行 As Integer
    末行 = PBASE格程工具_表参末行指定(WSTO, 1)
    '------------------------------------------------------------------------------------
    '标记：章签
    '------------------------------------------------------------------------------------
    If Len(章签) > 0 Then
        With WSTO.Rows(末行 + 1)
            With .Cells(1, 1).Resize(1, 计列输出)
                .RowHeight = 50
                .Font.Size = 20
                .Font.Color = 常色主黑
                .Interior.Color = 常色主白
                .VerticalAlignment = xlCenter
                .HorizontalAlignment = xlLeft
                .Font.Bold = True
                .Borders(xlInsideVertical).LineStyle = xlNone
                .Borders(xlEdgeTop).Color = 常色四灰
                .Borders(xlEdgeTop).Weight = xlThin
            End With
            .Cells(1, 割列标签类别).Value = ">"
            .Cells(1, 割列标签注释).Value = ">" & 章签
            .Cells(1, 割列标签注释).Font.Color = 章色
        End With
        末行 = 末行 + 1
    End If
    '------------------------------------------------------------------------------------
    '标记：节签
    '------------------------------------------------------------------------------------
    If Len(节签) > 0 Then
        With WSTO.Rows(末行 + 1)
            With .Cells(1, 1).Resize(1, 计列输出)
                .RowHeight = 40
                .Font.Size = 20
                .Interior.Color = 常色主黑
                .VerticalAlignment = xlCenter
                .HorizontalAlignment = xlLeft
                .Font.Bold = True
                .Borders(xlInsideVertical).LineStyle = xlNone
                .Borders(xlEdgeTop).Color = 常色四灰
                .Borders(xlEdgeTop).Weight = xlThin
            End With
            .Cells(1, 割列标签类别).Value = ">"
            .Cells(1, 割列标签注释).Value = ">" & 节签
            .Cells(1, 割列标签注释).Font.Color = 节色
        End With
        末行 = 末行 + 1
    End If
'========================================================================================
'验证
'========================================================================================
    If VBA.IsMissing(谕组) = True Then Exit Function
    If VBA.IsEmpty(谕组) = True Then Exit Function
    '------------------------------------------------------------------------------------
    If 典码输出 Is Nothing Then
        Exit Function
    ElseIf 典码输出.Count = 0 Then
        Exit Function
    End If
    Dim 计数输出 As Integer
    计数输出 = 典码输出.Count
'========================================================================================
'输出：标签
'========================================================================================
    '------------------------------------------------------------------------------------
    Dim 行号标签 As Integer
    行号标签 = 末行 + 1
    Dim 行号数始 As Integer
    行号数始 = 末行 + 2
    '------------------------------------------------------------------------------------
    '标签
    '------------------------------------------------------------------------------------
    With WSTO.Rows(行号标签)
        With .Cells(1, 1).Resize(1, 计列输出)
            .RowHeight = 20
            .Font.Size = 12
            .Font.Color = 常色六灰
            .Interior.Color = 常色主黑
            .Interior.TintAndShade = 0.2
            .Borders(xlInsideVertical).LineStyle = xlNone
'            .Borders(xlEdgeTop).Color = 常色四灰
'            .Borders(xlEdgeTop).Weight = xlThin
            .VerticalAlignment = xlCenter
            .HorizontalAlignment = xlLeft
            .Font.Bold = True
            .Font.Italic = True
        End With
        .Cells(1, 割列标签类别) = ">" & 区签
        .Cells(1, 割列标签类别).Font.Color = 基色底
'        .Cells(1, 割列标签计数) = 计数输出 & "只"
'        .Cells(1, 割列标签计数).HorizontalAlignment = xlRight
        .Cells(1, 割列标签注释) = 区释
    End With
'========================================================================================
'输出：数据
'========================================================================================
    ReDim ARRTO(1 To 计数输出, LBound(谕组, 2) To UBound(谕组, 2)) As Variant
    '------------------------------------------------------------------------------------
    '准备数据
    '------------------------------------------------------------------------------------
    Dim 定位原序 As Integer
    Dim Y As Integer
    For X = 1 To 典码输出.Count
        定位原序 = 典码输出.Items(X - 1)
        For Y = LBound(谕组, 2) To UBound(谕组, 2)
            ARRTO(X, Y) = 谕组(定位原序, Y)
        Next Y
    Next X
    典码输出.RemoveAll
    Set 典码输出 = Nothing
    '------------------------------------------------------------------------------------
    '统计
    '------------------------------------------------------------------------------------
    For X = LBound(ARRTO, 1) To UBound(ARRTO, 1)
        WSTO.Cells(行号标签, 位列割发生金额) = WSTO.Cells(行号标签, 位列割发生金额) + ARRTO(X, 位列割发生金额)
        WSTO.Cells(行号标签, 位列割成交数量) = WSTO.Cells(行号标签, 位列割成交数量) + ARRTO(X, 位列割成交数量)
        WSTO.Cells(行号标签, 位列割证券名称) = ARRTO(X, 位列割证券名称)
        WSTO.Cells(行号标签, 位列割委托类别) = 计数输出 & "次"
    Next
    With WSTO.Cells(行号标签, 位列割发生金额)
        .Font.Color = IIf(.Value > 0, 常色十红, 常色十绿)
    End With
    '------------------------------------------------------------------------------------
    '输出
    '------------------------------------------------------------------------------------
    Dim 区域数据 As Range
    Set 区域数据 = WSTO.Rows(行号数始).Resize(计数输出, 计列输出)
    区域数据 = ARRTO
    Erase ARRTO
    'Call UTL数据转换_集ARR2WS(ARRTO, WSTO, 行号数始)
'========================================================================================
'格式化
'========================================================================================
    '------------------------------------------------------------------------------------
    '格式化：数据
    '------------------------------------------------------------------------------------
    With WSTO.Cells(行号数始, 1)
        With .Resize(计数输出, 计列输出)
            .Interior.Color = 基色底
            .Interior.TintAndShade = 0.8
        End With
        With .Cells(1, 1).Resize(计数输出, 1)
            .Interior.TintAndShade = 0.5
        End With
    End With
    WSTO.Columns(位列割发生金额).HorizontalAlignment = xlRight
    WSTO.Columns(位列割成交数量).HorizontalAlignment = xlRight
    WSTO.Columns(位列割成交编号).Hidden = True
    WSTO.Columns(位列割成交日期).NumberFormatLocal = 全设格式of日期
    WSTO.Columns(位列割成交日期).ColumnWidth = 10
    '------------------------------------------------------------------------------------
    '排序
    '------------------------------------------------------------------------------------
    With 区域数据
'            .Sort key1:=.Cells(1, 位谕of周基乾局), order1:=xlAscending, _
'                  key2:=.Cells(1, 位谕of周德横类), order2:=xlAscending, _
'                  Header:=xlNo
'
        If 强列 <> 0 Then
            .Sort key1:=.Cells(1, 强列), order1:=强序, Header:=xlNo
        End If
    End With
    Set 区域数据 = Nothing
'    '------------------------------------------------------------------------------------
'    '格式化：归类
'    '------------------------------------------------------------------------------------
'    If 神谕归类 <> 0 Then
'        Select Case 神谕归类
'        Case 位谕of周基乾局
'        Case 位谕of日基乾局
'        Case 位谕of日基坤局
'        End Select
'    End If
'    '------------------------------------------------------------------------------------
'    '格式化：按行校验
'    '------------------------------------------------------------------------------------
'    Call IQQQ跨码展擎_按行汇总(WSTO, 基行:=行号数始, 是否跨码:=True)
'========================================================================================
'返回
'========================================================================================
    Set WSTO = Nothing
    Dim MSG As String
    MSG = ">" & 表名输出 & " " & 区签 & "：" & 计数输出 & vbCrLf
    '标准返回格式：以>开始，以换行结束
    IQQQ展擎出程至页割版 = MSG
'========================================================================================
End Function


