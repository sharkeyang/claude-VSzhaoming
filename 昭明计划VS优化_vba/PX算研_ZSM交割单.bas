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
    Dim MSG As String
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
            典集委类申购还款.Add key:=R, Item:=R
        ElseIf 值委托类别 = "申购扣款" Then
            典集委类申购扣款.Add key:=R, Item:=R
        ElseIf 值委托类别 = "中签扣款" Then
            典集委类中签扣款.Add key:=R, Item:=R
        ElseIf 值委托类别 = "中签通知" Then
            典集委类中签通知.Add key:=R, Item:=R
        ElseIf 值委托类别 = "配号" Then
            典集委类配号.Add key:=R, Item:=R
        ElseIf 值委托类别 = "托管转入" Then
            典集委类托管转入.Add key:=R, Item:=R
        ElseIf 值委托类别 = "托管转出" Then
            典集委类托管转出.Add key:=R, Item:=R
        '-----------------------------------------------
        ElseIf 值委托类别 = "融券" Then
            典集委类融券.Add key:=R, Item:=R
        ElseIf 值委托类别 = "融券购回" Then
            典集委类融券购回.Add key:=R, Item:=R
        '-----------------------------------------------
        ElseIf 值委托类别 = "组合费用" Then
            典集委类组合费用.Add key:=R, Item:=R
        ElseIf 值委托类别 = "其他" Then
            典集委类其他.Add key:=R, Item:=R
        ElseIf 值委托类别 = "红利" Then
            典集委类红利.Add key:=R, Item:=R
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
                If 典集委类交易码票.Exists(CIDL) = False Then 典集委类交易码票.Add key:=CIDL, Item:=CIDL
            ElseIf UBCID是中股票(CIDL) = True Then
                If 典集委类交易码票.Exists(CIDL) = False Then 典集委类交易码票.Add key:=CIDL, Item:=CIDL
            Else
                典集委类交易码他.Add key:=R, Item:=R
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
                典集码类数正.Add key:=CIDL, Item:=值累数
                值累额码类数正 = 值累额码类数正 + 值累额
        ElseIf 值累数 < 0 Then
                典集码类数负.Add key:=CIDL, Item:=值累数
                值累额码类数负 = 值累额码类数负 + 值累额
        Else
            '过滤近30天交易
            If 值成交日期 >= Date - 30 Then
                典集码类数零近.Add key:=CIDL, Item:=值累数
                值累额码类数零近月 = 值累额码类数零近月 + 值累额
            ElseIf 值累额 >= 0 Then
                典集码类数零赚.Add key:=CIDL, Item:=值累数
                值累额码类数零远赚 = 值累额码类数零远赚 + 值累额
            Else
                典集码类数零赔.Add key:=CIDL, Item:=值累数
                值累额码类数零远赔 = 值累额码类数零远赔 + 值累额
            End If
        End If
        典集码类额.Add key:=CIDL, Item:=值累额
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
                典集委类交易个票.Add key:=R, Item:=R
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
                典集委类交易个票.Add key:=R, Item:=R
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
                典集委类交易个票.Add key:=R, Item:=R
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
                典集委类交易个票.Add key:=R, Item:=R
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
                典集委类交易个票.Add key:=R, Item:=R
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



Option Explicit
'========================================================================================
'交割单深度分析 — 5维度：⑥择时 → ⑦仓位 → ⑤成本 → ①盈亏 → ③T+0
'数据源：华宝证券交割单查询 TXT 文件（GBK编码、字段间3+空格分隔）
'========================================================================================
'========================================================================================
'常量
'========================================================================================
Public Const 常册割析 = "割析"
'------------------------------------------------------------------------------------
'列位常量（与 ZUTL_F1交割单 对齐）
Public Const 位列割成交日期 = 1
Public Const 位列割成交时间 = 2
Public Const 位列割证券CIDL = 3
Public Const 位列割证券代码 = 4
Public Const 位列割证券名称 = 5
Public Const 位列割委托类别 = 6
Public Const 位列割成交数量 = 8
Public Const 位列割成交金额 = 9
Public Const 位列割发生金额 = 10
Public Const 位列割佣金 = 11
Public Const 位列割印花税 = 12
Public Const 位列割过户费 = 13
Public Const 位列割其他费 = 14
'------------------------------------------------------------------------------------
'时段标签
Private Const 时段早盘 = "早盘9:30-10:00"
Private Const 时段上午中 = "上午中段10:00-11:30"
Private Const 时段午前收盘 = "午前收盘11:00-11:30"
Private Const 时段午盘 = "午盘13:00-14:00"
Private Const 时段尾盘 = "尾盘14:00-15:00"
Private Const 时段其他 = "其他时段"
'------------------------------------------------------------------------------------
'仓位分段标签（带数字前缀保序）
Private Const 位小微 = "1小微<5千"
Private Const 位小 = "2小1-2万"
Private Const 位中 = "3中2-5万"
Private Const 位中大 = "4中大5-10万"
Private Const 位大 = "5大10-20万"
Private Const 位超大 = "6超大>20万"
'========================================================================================
'========================================================================================
'入口主调
'========================================================================================
'========================================================================================
Sub STCALL割析_交单分析()
'========================================================================================
'选择文件
'========================================================================================
    Dim FILEOPEN As Variant
    FILEOPEN = Application.GetOpenFilename( _
        "华宝交割单信息,*.xls", , "选择华宝证券交割单 XLS", , False)
    If FILEOPEN = False Then Exit Sub
'========================================================================================
    UTL宏工具_BEGIN
'========================================================================================
    '创建输出表
    Dim WS割 As Worksheet
    Call PBASE格程工具_表操工表新增(WS割, 常册割析, 基色底:=常色马尔斯绿)
'========================================================================================
    '读取 XLS 文件到数组
    Dim WB割 As Workbook
    Set WB割 = GetObject(FILEOPEN)
    Dim ARR原始 As Variant
    With WB割.ActiveSheet
        ARR原始 = .Range("A1").CurrentRegion
    End With
    WB割.Close False
    Set WB割 = Nothing
    '过滤只保留买卖记录
    Dim 计数原始 As Long
    计数原始 = UBound(ARR原始, 1)
    Dim 计数交易 As Long
    计数交易 = 0
    Dim R As Long, j As Long
    For R = 2 To 计数原始
        If Trim(ARR原始(R, 6)) = "买入" Or Trim(ARR原始(R, 6)) = "卖出" Then 计数交易 = 计数交易 + 1
    Next
    If 计数交易 = 0 Then
        WS割.Cells(1, 1) = "无有效交易记录"
        UTL宏工具_END
        Exit Sub
    End If
    Dim ARR买卖 As Variant
    ReDim ARR买卖(1 To 计数交易, 1 To 15)
    Dim 指针 As Long
    指针 = 0
    For R = 2 To 计数原始
        If Trim(ARR原始(R, 6)) = "买入" Or Trim(ARR原始(R, 6)) = "卖出" Then
            指针 = 指针 + 1
            For j = 1 To 15: ARR买卖(指针, j) = ARR原始(R, j): Next
        End If
    Next
    Set ARR原始 = Nothing
'========================================================================================
    '生成分析结果
    Dim ARR择时 As Variant
    Dim ARR仓位 As Variant
    Dim ARR成本 As Variant
    Dim ARR盈亏 As Variant
    Dim ARR_T0 As Variant

    后台辅程割析_择时分析 ARR买卖, ARR择时
    后台辅程割析_仓位分析 ARR买卖, ARR仓位
    后台辅程割析_成本分析 ARR买卖, ARR成本
    后台辅程割析_盈亏分析 ARR买卖, ARR盈亏
    后台辅程割析_T加0分析 ARR买卖, ARR_T0
'========================================================================================
    '输出到表
    后台辅程割析_输出 WS割, ARR买卖, ARR择时, ARR仓位, ARR成本, ARR盈亏, ARR_T0
'========================================================================================
    '格式化
    后台辅程割析_格式化 WS割
'========================================================================================
    UTL宏工具_END
    WS割.Activate
    ActiveWindow.Zoom = 90
    MsgBox "交割单分析完成！" & vbCrLf & vbCrLf & _
           "总交易: " & 计数交易 & " 笔" & vbCrLf & _
           "股票数: " & UBound(ARR盈亏, 1) & " 只", vbInformation, 常册割析
End Sub
'========================================================================================
'========================================================================================
'读取文件
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_读数(ByVal sFILE As String, ByRef ARRTO As Variant)
'========================================================================================
    '二进制读入（TXT = GBK编码）
    Dim nFile As Integer
    nFile = FreeFile
    Open sFILE For Binary Access Read As #nFile
    Dim rawBytes() As Byte
    ReDim rawBytes(1 To LOF(nFile))
    Get #nFile, , rawBytes
    Close #nFile
'------------------------------------------------------------------------------------
    'GBK → Unicode
    Dim sAll As String
    sAll = StrConv(rawBytes, vbUnicode, &H804)
'------------------------------------------------------------------------------------
    '分行
    Dim lines As Variant
    lines = Split(sAll, vbCrLf)
    Dim 计数行 As Long
    计数行 = UBound(lines) - LBound(lines) + 1
'------------------------------------------------------------------------------------
    '先数有效行，分配数组
    Dim 计数有效 As Long
    Dim i As Long
    计数有效 = 0
    For i = 3 To 计数行 - 1    '跳过前3行（分隔线/空行/表头），最后一行可能空
        Dim sLINE As String
        sLINE = Trim(lines(i))
        If Len(sLINE) > 20 Then  '有实质内容
            计数有效 = 计数有效 + 1
        End If
    Next
'------------------------------------------------------------------------------------
    '分配结果数组
    ReDim ARRTO(1 To 计数有效, 1 To 15)
    Dim 行号 As Long
    行号 = 0
    Dim 字段 As Variant

    For i = 3 To 计数行 - 1
        sLINE = Trim(lines(i))
        If Len(sLINE) < 20 Then GoTo 下一行

        字段 = 后台辅程割析_分割字段(sLINE)
        If IsEmpty(字段) Then GoTo 下一行
        '只保留买卖记录，排除配号
        If 字段(6) <> "买入" And 字段(6) <> "卖出" Then GoTo 下一行

        行号 = 行号 + 1
        Dim j As Long
        For j = 1 To 15
            ARRTO(行号, j) = 字段(j)
        Next
下一行:
    Next
'------------------------------------------------------------------------------------
    '缩减数组
    If 行号 < 计数有效 Then
        If 行号 = 0 Then
            ReDim ARRTO(1, 1 To 15)
            ARRTO(1, 1) = ""
            Exit Sub
        End If
        Dim ARRTMP As Variant
        ARRTMP = ARRTO
        ReDim ARRTO(1 To 行号, 1 To 15)
        For i = 1 To 行号
            For j = 1 To 15
                ARRTO(i, j) = ARRTMP(i, j)
            Next
        Next
    End If
End Sub
'========================================================================================
'========================================================================================
'分割字段：扫描3+连续空格作为分隔符
'========================================================================================
'========================================================================================
Private Function 后台辅程割析_分割字段(ByVal sLINE As String) As Variant
'========================================================================================
    Dim result(1 To 15) As Variant
    Dim i As Long, nField As Long
    Dim inField As Boolean
    Dim fieldStart As Long
    Dim ch As String

    nField = 0
    inField = False

    For i = 1 To Len(sLINE)
        ch = Mid(sLINE, i, 1)
        If ch <> " " Then
            If Not inField Then
                inField = True
                fieldStart = i
            End If
        Else
            If inField Then
                '检查是否3+连续空格（字段分隔符）
                If i + 2 <= Len(sLINE) Then
                    If Mid(sLINE, i, 3) = "   " Then
                        nField = nField + 1
                        If nField <= 15 Then
                            result(nField) = Trim(Mid(sLINE, fieldStart, i - fieldStart))
                        End If
                        inField = False
                        '跳过所有后续空格
                        Do While i <= Len(sLINE) And Mid(sLINE, i, 1) = " "
                            i = i + 1
                        Loop
                        i = i - 1  'For循环会+1
                    End If
                End If
            End If
        End If
    Next

    '最后一个字段
    If inField Then
        nField = nField + 1
        If nField <= 15 Then
            result(nField) = Trim(Mid(sLINE, fieldStart))
        End If
    End If

    If nField >= 15 Then
        后台辅程割析_分割字段 = result
    Else
        后台辅程割析_分割字段 = Empty
    End If
End Function
'========================================================================================
'========================================================================================
'⑥ 择时分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_择时分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)

    '初始化各时段统计
    Dim 时段 As Variant
    Dim 时段列表 As Variant
    时段列表 = Array(时段早盘, 时段上午中, 时段午前收盘, 时段午盘, 时段尾盘, 时段其他)

    Dim 段计数(0 To 5) As Long
    Dim 段买笔(0 To 5) As Long
    Dim 段卖笔(0 To 5) As Long
    Dim 段买额(0 To 5) As Double
    Dim 段卖额(0 To 5) As Double

    Dim i As Long
    For i = 1 To 计数
        Dim s时间 As String
        s时间 = Trim(ARR(i, 位列割成交时间))
        Dim 小时 As Long
        小时 = Val(Left(s时间, 2))

        Dim idx As Long
        If 小时 = 9 Then
            idx = 0  '早盘
        ElseIf 小时 = 10 Then
            idx = 1  '上午中
        ElseIf 小时 = 11 Then
            idx = 2  '午前
        ElseIf 小时 = 13 Then
            idx = 3  '午盘
        ElseIf 小时 = 14 Or 小时 = 15 Then
            idx = 4  '尾盘（含15:00集合竞价）
        Else
            idx = 5  '其他
        End If

        段计数(idx) = 段计数(idx) + 1
        Dim 金额 As Double
        金额 = Val(ARR(i, 位列割成交金额))
        Dim 类别 As String
        类别 = Trim(ARR(i, 位列割委托类别))

        If 日期 > 最后日期(idx) Then 最后日期(idx) = 日期
        If 类别 = "买入" Then
            段买笔(idx) = 段买笔(idx) + 1
            段买额(idx) = 段买额(idx) + 金额
        Else
            段卖笔(idx) = 段卖笔(idx) + 1
            段卖额(idx) = 段卖额(idx) + 金额
        End If
    Next

    '输出数组：9列（时段/总笔数/占比/买笔/买额/卖笔/卖额/净额/方向）
    ReDim ARRTO(1 To 7, 1 To 9)
    ARRTO(1, 1) = "时段": ARRTO(1, 2) = "总笔数": ARRTO(1, 3) = "占比"
    ARRTO(1, 4) = "买入笔数": ARRTO(1, 5) = "买入金额"
    ARRTO(1, 6) = "卖出笔数": ARRTO(1, 7) = "卖出金额"
    ARRTO(1, 8) = "买卖净额": ARRTO(1, 9) = "方向"

    For idx = 0 To 5
        Dim 行 As Long
        行 = idx + 2
        ARRTO(行, 1) = 时段列表(idx)
        ARRTO(行, 2) = 段计数(idx)
        ARRTO(行, 3) = 段计数(idx) / 计数
        ARRTO(行, 4) = 段买笔(idx)
        ARRTO(行, 5) = 段买额(idx)
        ARRTO(行, 6) = 段卖笔(idx)
        ARRTO(行, 7) = 段卖额(idx)
        ARRTO(行, 8) = 段卖额(idx) - 段买额(idx)
        If 段买笔(idx) > 段卖笔(idx) Then
            ARRTO(行, 9) = "偏买入"
        ElseIf 段卖笔(idx) > 段买笔(idx) Then
            ARRTO(行, 9) = "偏卖出"
        Else
            ARRTO(行, 9) = "均衡"
        End If
    Next
End Sub
'========================================================================================
'========================================================================================
'⑦ 仓位分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_仓位分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)

    '仓位分段
    Dim 位标签 As Variant
    位标签 = Array(位小微, 位小, 位中, 位中大, 位大, 位超大)
    Dim 位上限 As Variant
    位上限 = Array(5000, 20000, 50000, 100000, 200000, 999999999#)
    Dim 位计数(0 To 5) As Long
    Dim 位金额(0 To 5) As Double

    Dim i As Long
    For i = 1 To 计数
        Dim 金额 As Double
        金额 = Val(ARR(i, 位列割成交金额))
        Dim idx As Long
        For idx = 0 To 5
            If 金额 <= 位上限(idx) Then
                位计数(idx) = 位计数(idx) + 1
                位金额(idx) = 位金额(idx) + 金额
                Exit For
            End If
        Next
    Next

    '输出仓位分段：6行×5列
    ReDim ARRTO(1 To 8, 1 To 5)
    ARRTO(1, 1) = "仓位段": ARRTO(1, 2) = "笔数": ARRTO(1, 3) = "笔数占比"
    ARRTO(1, 4) = "累计金额": ARRTO(1, 5) = "金额占比"

    Dim 总金额 As Double
    总金额 = 0
    For idx = 0 To 5
        总金额 = 总金额 + 位金额(idx)
    Next

    For idx = 0 To 5
        Dim 行 As Long
        行 = idx + 2
        ARRTO(行, 1) = Mid(位标签(idx), 2)  '去掉排序前缀数字
        ARRTO(行, 2) = 位计数(idx)
        ARRTO(行, 3) = 位计数(idx) / 计数
        ARRTO(行, 4) = 位金额(idx)
        If 总金额 > 0 Then ARRTO(行, 5) = 位金额(idx) / 总金额
    Next

    '第8行：排序确认
    ARRTO(7, 1) = "交易笔数合计": ARRTO(7, 2) = 计数
    ARRTO(8, 1) = "总成交金额": ARRTO(8, 4) = 总金额
End Sub
'========================================================================================
'========================================================================================
'⑤ 成本分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_成本分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)

    '收集佣金率
    Dim 佣金率集合() As Double
    ReDim 佣金率集合(1 To 计数)
    Dim 有效 As Long
    有效 = 0

    Dim 总佣金 As Double, 总印花税 As Double, 总过户费 As Double, 总成交 As Double
    Dim i As Long
    For i = 1 To 计数
        Dim 佣金 As Double, 成交 As Double
        佣金 = Val(ARR(i, 位列割佣金))
        成交 = Val(ARR(i, 位列割成交金额))
        总佣金 = 总佣金 + 佣金
        总印花税 = 总印花税 + Val(ARR(i, 位列割印花税))
        总过户费 = 总过户费 + Val(ARR(i, 位列割过户费))
        总成交 = 总成交 + 成交
        If 成交 > 0 And 佣金 > 0 Then
            有效 = 有效 + 1
            佣金率集合(有效) = 佣金 / 成交 * 10000  '万分比
        End If
    Next

    ReDim ARRTO(1 To 12, 1 To 4)
    Dim 行号 As Long
    行号 = 1

    '--- 佣金率基本统计 ---
    ARRTO(行号, 1) = "指标": ARRTO(行号, 2) = "数值"
    行号 = 2
    ARRTO(行号, 1) = "有效样本数": ARRTO(行号, 2) = 有效

    If 有效 > 0 Then
        '均值
        Dim 总和 As Double
        总和 = 0
        For i = 1 To 有效
            总和 = 总和 + 佣金率集合(i)
        Next
        行号 = 3: ARRTO(行号, 1) = "平均佣金率(万分)": ARRTO(行号, 2) = 总和 / 有效

        '中位
        Dim j As Long, k As Long
        For i = 1 To 有效 - 1
            For j = i + 1 To 有效
                If 佣金率集合(i) > 佣金率集合(j) Then
                    Dim tmp As Double
                    tmp = 佣金率集合(i)
                    佣金率集合(i) = 佣金率集合(j)
                    佣金率集合(j) = tmp
                End If
            Next
        Next
        行号 = 4: ARRTO(行号, 1) = "中位佣金率(万分)": ARRTO(行号, 2) = 佣金率集合(有效 \ 2 + 1)
        行号 = 5: ARRTO(行号, 1) = "最低佣金率(万分)": ARRTO(行号, 2) = 佣金率集合(1)
        行号 = 6: ARRTO(行号, 1) = "最高佣金率(万分)": ARRTO(行号, 2) = 佣金率集合(有效)

        'P5/P95
        Dim p5 As Long, p95 As Long
        p5 = Int(有效 * 0.05 + 0.5): If p5 < 1 Then p5 = 1
        p95 = Int(有效 * 0.95 + 0.5): If p95 > 有效 Then p95 = 有效
        行号 = 7: ARRTO(行号, 1) = "P5(万分)": ARRTO(行号, 2) = 佣金率集合(p5)
        行号 = 8: ARRTO(行号, 1) = "P95(万分)": ARRTO(行号, 2) = 佣金率集合(p95)
    End If

    '--- 费用结构 ---
    行号 = 10: ARRTO(行号, 1) = "费用项目": ARRTO(行号, 2) = "金额": ARRTO(行号, 3) = "费率"
    行号 = 11: ARRTO(行号, 1) = "总成交金额": ARRTO(行号, 2) = 总成交
    行号 = 12: ARRTO(行号, 1) = "佣金总计": ARRTO(行号, 2) = 总佣金
    If 总成交 > 0 Then ARRTO(行号, 3) = 总佣金 / 总成交 * 100
End Sub
'========================================================================================
'========================================================================================
'① 盈亏分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_盈亏分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)

    '按股票分组
    '最多492只股票，用数组+字典模拟
    Dim 代码列表(1 To 600) As String
    Dim 名称列表(1 To 600) As String
    Dim 买额(1 To 600) As Double
    Dim 卖额(1 To 600) As Double
    Dim 买佣(1 To 600) As Double, 卖佣(1 To 600) As Double
    Dim 买印(1 To 600) As Double, 卖印(1 To 600) As Double
    Dim 买过(1 To 600) As Double, 卖过(1 To 600) As Double
    Dim 买数(1 To 600) As Double, 卖数(1 To 600) As Double
    Dim 笔数(1 To 600) As Long
    Dim 最后日期(1 To 600) As Date

    Dim 三个月前 As Date
    三个月前 = Date - 90
    Dim 去重数 As Long
    去重数 = 0

    Dim i As Long, j As Long
    For i = 1 To 计数
        Dim s代码 As String
        s代码 = Trim(ARR(i, 位列割证券代码))
        '查找
        Dim idx As Long
        idx = 0
        For j = 1 To 去重数
            If 代码列表(j) = s代码 Then
                idx = j
                Exit For
            End If
        Next
        If idx = 0 Then
            去重数 = 去重数 + 1
            idx = 去重数
            代码列表(idx) = s代码
            名称列表(idx) = Trim(ARR(i, 位列割证券名称))
        End If

        笔数(idx) = 笔数(idx) + 1
        Dim 类别 As String
        类别 = Trim(ARR(i, 位列割委托类别))
        Dim 金额 As Double
        金额 = Val(ARR(i, 位列割成交金额))
        Dim 佣金 As Double
        佣金 = Val(ARR(i, 位列割佣金))
        Dim 印花 As Double
        印花 = Val(ARR(i, 位列割印花税))
        Dim 过户 As Double
        过户 = Val(ARR(i, 位列割过户费))
        Dim 数量 As Double
        数量 = Val(ARR(i, 位列割成交数量))
        Dim 日期 As Date
        日期 = ARR(i, 位列割成交日期)

        If 日期 > 最后日期(idx) Then 最后日期(idx) = 日期
        If 类别 = "买入" Then
            买额(idx) = 买额(idx) + 金额
            买佣(idx) = 买佣(idx) + 佣金
            买印(idx) = 买印(idx) + 印花
            买过(idx) = 买过(idx) + 过户
            买数(idx) = 买数(idx) + 数量
        Else
            卖额(idx) = 卖额(idx) + 金额
            卖佣(idx) = 卖佣(idx) + 佣金
            卖印(idx) = 卖印(idx) + 印花
            卖过(idx) = 卖过(idx) + 过户
            卖数(idx) = 卖数(idx) + 数量
        End If
    Next

    '计算结果
    ReDim ARRTO(1 To 去重数 + 3, 1 To 8)
    ARRTO(1, 1) = "证券代码": ARRTO(1, 2) = "证券名称"
    ARRTO(1, 3) = "净利润": ARRTO(1, 4) = "收益率"
    ARRTO(1, 5) = "交易笔数": ARRTO(1, 6) = "持仓状态"
    ARRTO(1, 7) = "成本价": ARRTO(1, 8) = "浮动盈亏"

    For idx = 1 To 去重数
        Dim 净利润 As Double
        净利润 = 卖额(idx) - 买额(idx) - 买佣(idx) - 卖佣(idx) - 买印(idx) - 卖印(idx) - 买过(idx) - 卖过(idx)
        Dim 剩余 As Double
        剩余 = 买数(idx) - 卖数(idx)

        ARRTO(idx + 1, 1) = 代码列表(idx)
        ARRTO(idx + 1, 2) = 名称列表(idx)
        ARRTO(idx + 1, 3) = 净利润
        If 买额(idx) > 0 Then ARRTO(idx + 1, 4) = 净利润 / 买额(idx) * 100
        ARRTO(idx + 1, 5) = 笔数(idx)
        If 剩余 > 0 Then
            ARRTO(idx + 1, 6) = "持仓中"
            If 买数(idx) > 0 Then ARRTO(idx + 1, 7) = (买额(idx) + 买佣(idx) + 买印(idx) + 买过(idx)) / 买数(idx)
            ARRTO(idx + 1, 8) = "需查行情"
        ElseIf 卖额(idx) > 0 And 买额(idx) > 0 Then
            ARRTO(idx + 1, 6) = "已清仓"
        ElseIf 最后日期(idx) < 三个月前 Then
            ARRTO(idx + 1, 6) = "不完整(三个月前)"
        Else
            ARRTO(idx + 1, 6) = "数据不完整"
        End If
    Next

    '汇总行
    Dim 总利润 As Double, 总买额 As Double, 胜数 As Long
    总利润 = 0: 总买额 = 0: 胜数 = 0
    For idx = 1 To 去重数
        净利润 = 卖额(idx) - 买额(idx) - 买佣(idx) - 卖佣(idx) - 买印(idx) - 卖印(idx) - 买过(idx) - 卖过(idx)
        总利润 = 总利润 + 净利润
        总买额 = 总买额 + 买额(idx)
        If 净利润 > 0 Then 胜数 = 胜数 + 1
    Next
    ARRTO(去重数 + 2, 1) = "汇总"
    ARRTO(去重数 + 2, 3) = 总利润
    If 总买额 > 0 Then ARRTO(去重数 + 2, 4) = 总利润 / 总买额 * 100
    ARRTO(去重数 + 2, 5) = 去重数

    ARRTO(去重数 + 3, 1) = "胜率"
    ARRTO(去重数 + 3, 3) = 胜数
    ARRTO(去重数 + 3, 4) = 去重数 - 胜数
    If 去重数 > 0 Then ARRTO(去重数 + 3, 5) = 胜数 / 去重数 * 100
End Sub
'========================================================================================
'========================================================================================
'③ T+0分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_T加0分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)

    '按(日期+代码)分组
    Dim 组日期(1 To 2000) As String
    Dim 组代码(1 To 2000) As String
    Dim 组名称(1 To 2000) As String
    Dim 组买额(1 To 2000) As Double
    Dim 组卖额(1 To 2000) As Double
    Dim 组买笔(1 To 2000) As Long
    Dim 组卖笔(1 To 2000) As Long
    Dim 组数 As Long
    组数 = 0

    Dim i As Long, j As Long
    For i = 1 To 计数
        Dim s日期 As String, s代码 As String
        s日期 = Trim(ARR(i, 位列割成交日期))
        s代码 = Trim(ARR(i, 位列割证券代码))

        Dim idx As Long
        idx = 0
        For j = 1 To 组数
            If 组日期(j) = s日期 And 组代码(j) = s代码 Then
                idx = j
                Exit For
            End If
        Next
        If idx = 0 Then
            组数 = 组数 + 1
            idx = 组数
            组日期(idx) = s日期
            组代码(idx) = s代码
            组名称(idx) = Trim(ARR(i, 位列割证券名称))
        End If

        Dim 类别 As String
        类别 = Trim(ARR(i, 位列割委托类别))
        Dim 金额 As Double
        金额 = Val(ARR(i, 位列割成交金额))
        If 日期 > 最后日期(idx) Then 最后日期(idx) = 日期
        If 类别 = "买入" Then
            组买额(idx) = 组买额(idx) + 金额
            组买笔(idx) = 组买笔(idx) + 1
        Else
            组卖额(idx) = 组卖额(idx) + 金额
            组卖笔(idx) = 组卖笔(idx) + 1
        End If
    Next

    '筛选同时有买和卖的组(T+0)
    ReDim ARRTO(1 To 组数 + 3, 1 To 6)
    ARRTO(1, 1) = "日期": ARRTO(1, 2) = "证券代码"
    ARRTO(1, 3) = "证券名称": ARRTO(1, 4) = "买入金额"
    ARRTO(1, 5) = "卖出金额": ARRTO(1, 6) = "总笔数"

    Dim T0数 As Long
    T0数 = 0
    Dim T0买总 As Double, T0卖总 As Double
    T0买总 = 0: T0卖总 = 0

    For idx = 1 To 组数
        If 组买笔(idx) > 0 And 组卖笔(idx) > 0 Then
            T0数 = T0数 + 1
            ARRTO(T0数 + 1, 1) = 组日期(idx)
            ARRTO(T0数 + 1, 2) = 组代码(idx)
            ARRTO(T0数 + 1, 3) = 组名称(idx)
            ARRTO(T0数 + 1, 4) = 组买额(idx)
            ARRTO(T0数 + 1, 5) = 组卖额(idx)
            ARRTO(T0数 + 1, 6) = 组买笔(idx) + 组卖笔(idx)
            T0买总 = T0买总 + 组买额(idx)
            T0卖总 = T0卖总 + 组卖额(idx)
        End If
    Next

    '汇总
    ARRTO(T0数 + 2, 1) = "T+0汇总"
    ARRTO(T0数 + 2, 2) = T0数 & " 条"
    ARRTO(T0数 + 2, 4) = T0买总
    ARRTO(T0数 + 2, 5) = T0卖总

    ARRTO(T0数 + 3, 1) = "占全部交易"
    If 计数 > 0 Then ARRTO(T0数 + 3, 2) = Format(T0数 / 计数 * 100, "0.0") & "%"
End Sub
'========================================================================================
'========================================================================================
'输出到表
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_输出(ByVal WS As Worksheet, _
    ByRef ARR原始 As Variant, _
    ByRef ARR择时 As Variant, _
    ByRef ARR仓位 As Variant, _
    ByRef ARR成本 As Variant, _
    ByRef ARR盈亏 As Variant, _
    ByRef ARR_T0 As Variant)
'========================================================================================
    Dim 行号 As Long
    行号 = 1

    '标题
    WS.Cells(行号, 1) = "交割单深度分析报告"
    WS.Cells(行号, 1).Font.Bold = True
    WS.Cells(行号, 1).Font.Size = 14
    行号 = 行号 + 2

    '基础概况
    Dim 计数 As Long
    计数 = UBound(ARR原始, 1)
    Dim 股票数 As Long
    股票数 = UBound(ARR盈亏, 1) - 2  '减去汇总行

    WS.Cells(行号, 1) = "基础概况"
    WS.Cells(行号, 1).Font.Bold = True
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "总交易笔数": WS.Cells(行号, 2) = 计数
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "涉及股票数": WS.Cells(行号, 2) = 股票数
    行号 = 行号 + 2

    '⑥ 择时
    Call 后台辅程割析_输出段(WS, 行号, "⑥ 择时能力分析", ARR择时)
    行号 = 行号 + UBound(ARR择时, 1) + 4

    '⑦ 仓位
    Call 后台辅程割析_输出段(WS, 行号, "⑦ 仓位管理分析", ARR仓位)
    行号 = 行号 + UBound(ARR仓位, 1) + 4

    '⑤ 成本
    Call 后台辅程割析_输出段(WS, 行号, "⑤ 交易成本分析", ARR成本)
    行号 = 行号 + UBound(ARR成本, 1) + 4

    '① 盈亏（只输出TOP15+亏损TOP15+汇总）
    WS.Cells(行号, 1) = "① 盈亏分析"
    WS.Cells(行号, 1).Font.Bold = True
    行号 = 行号 + 1

    '盈利TOP15
    WS.Cells(行号, 1) = "盈利 TOP 15"
    WS.Cells(行号, 1).Font.Bold = True
    行号 = 行号 + 1
    Call 后台辅程割析_输出表头(WS, 行号, ARR盈亏)
    行号 = 行号 + 1
    Call 后台辅程割析_输出排序(WS, 行号, ARR盈亏, 3, False, 15)
    行号 = 行号 + 17

    '亏损TOP15
    WS.Cells(行号, 1) = "亏损 TOP 15"
    WS.Cells(行号, 1).Font.Bold = True
    行号 = 行号 + 1
    Call 后台辅程割析_输出表头(WS, 行号, ARR盈亏)
    行号 = 行号 + 1
    Call 后台辅程割析_输出排序(WS, 行号, ARR盈亏, 3, True, 15)
    行号 = 行号 + 17

    '盈亏汇总
    Dim 汇总行 As Long
    汇总行 = UBound(ARR盈亏, 1) - 1
    WS.Cells(行号, 1) = "汇总": WS.Cells(行号, 1).Font.Bold = True
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "总净利润": WS.Cells(行号, 2) = ARR盈亏(汇总行, 3)
    WS.Cells(行号, 2).NumberFormatLocal = "#,##0.00"
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "总收益率(%)": WS.Cells(行号, 2) = ARR盈亏(汇总行, 4)
    WS.Cells(行号, 2).NumberFormatLocal = "0.00"
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "盈利股票数": WS.Cells(行号, 2) = ARR盈亏(UBound(ARR盈亏, 1), 3)
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "亏损股票数": WS.Cells(行号, 2) = ARR盈亏(UBound(ARR盈亏, 1), 4)
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "胜率(%)": WS.Cells(行号, 2) = ARR盈亏(UBound(ARR盈亏, 1), 5)
    WS.Cells(行号, 2).NumberFormatLocal = "0.0"
    行号 = 行号 + 3

    '③ T+0
    Call 后台辅程割析_输出段(WS, 行号, "③ T+0识别分析", ARR_T0)
End Sub
'========================================================================================
'========================================================================================
'输出辅助
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_输出段(ByVal WS As Worksheet, ByVal 行号 As Long, _
    ByVal 标题 As String, ByRef ARR As Variant)
    WS.Cells(行号, 1) = 标题
    WS.Cells(行号, 1).Font.Bold = True
    行号 = 行号 + 1
    Call 后台辅程割析_输出表头(WS, 行号, ARR)
    行号 = 行号 + 1
    Dim i As Long, j As Long
    For i = 2 To UBound(ARR, 1)
        For j = 1 To UBound(ARR, 2)
            WS.Cells(行号, j) = ARR(i, j)
        Next
        行号 = 行号 + 1
    Next
End Sub

Private Sub 后台辅程割析_输出表头(ByVal WS As Worksheet, ByVal 行号 As Long, ByRef ARR As Variant)
    Dim j As Long
    For j = 1 To UBound(ARR, 2)
        WS.Cells(行号, j) = ARR(1, j)
        WS.Cells(行号, j).Font.Bold = True
    Next
End Sub

Private Sub 后台辅程割析_输出排序(ByVal WS As Worksheet, ByVal 行号 As Long, _
    ByRef ARR As Variant, ByVal 排序列 As Long, ByVal 升序 As Boolean, ByVal 取前N As Long)
    Dim 总行 As Long
    总行 = UBound(ARR, 1)
    Dim 数据行 As Long
    数据行 = 总行 - 2  '排除汇总行

    '复制行索引
    Dim 索引() As Long
    ReDim 索引(1 To 数据行)
    Dim i As Long
    For i = 1 To 数据行
        索引(i) = i + 1
    Next

    '冒泡排序
    Dim j As Long, tmp As Long
    For i = 1 To 数据行 - 1
        For j = i + 1 To 数据行
            Dim 交换 As Boolean
            If 升序 Then
                交换 = Val(ARR(索引(i), 排序列)) > Val(ARR(索引(j), 排序列))
            Else
                交换 = Val(ARR(索引(i), 排序列)) < Val(ARR(索引(j), 排序列))
            End If
            If 交换 Then
                tmp = 索引(i): 索引(i) = 索引(j): 索引(j) = tmp
            End If
        Next
    Next

    '输出前N
    Dim 输出数 As Long
    输出数 = 数据行
    If 取前N > 0 And 取前N < 输出数 Then 输出数 = 取前N

    Dim 列数 As Long
    列数 = UBound(ARR, 2)
    For i = 1 To 输出数
        For j = 1 To 列数
            WS.Cells(行号, j) = ARR(索引(i), j)
        Next
        行号 = 行号 + 1
    Next
End Sub
'========================================================================================
'========================================================================================
'格式化
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_格式化(ByVal WS As Worksheet)
'========================================================================================
    WS.Columns("A:Z").Font.Name = "宋体"
    WS.Columns("A:Z").Font.Size = 10
    WS.Columns("A").ColumnWidth = 16
    WS.Columns("B").ColumnWidth = 14
    WS.Columns("C").ColumnWidth = 12
    WS.Columns("D").ColumnWidth = 14
    WS.Columns("E").ColumnWidth = 12
    WS.Columns("F").ColumnWidth = 12
    WS.Columns("A:A").NumberFormatLocal = "@"  '文本格式
    WS.Rows("1:1").RowHeight = 25
    WS.Activate
    ActiveWindow.Zoom = 90
End Sub
