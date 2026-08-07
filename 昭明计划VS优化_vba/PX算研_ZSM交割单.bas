Attribute VB_Name = "PX算研_ZSM交割单"
Option Explicit
Public Const 常册交割单 = "割单"
Public Const 常册割析 = "割析"
Public Const 位列割成交日期 = 1
Public Const 位列割成交时间 = 2
Public Const 位列割证券CIDL = 3
Public Const 位列割证券代码 = 4
Public Const 位列割证券名称 = 5
Public Const 位列割委托类别 = 6
Public Const 位列割成交价格 = 7
Public Const 位列割成交数量 = 8
Public Const 位列割成交金额 = 9
Public Const 位列割发生金额 = 10
Public Const 位列割佣金 = 11
Public Const 位列割印花税 = 12
Public Const 位列割过户费 = 13
Public Const 位列割其他费 = 14
Public Const 位列割成交编号 = 15
'------------------------------------------------------------------------------------
'交割单常量
'------------------------------------------------------------------------------------
Public Const 常割单后缀 = "割单"
Public Const 常割析后缀 = "割析"
Public Const 常割单列数 = 18
Public Const 常割单列状态 = 16
Public Const 常割单列配对类型 = 17
Public Const 常割单列账户 = 18
'------------------------------------------------------------------------------------
'模块级交割单数组（中间传递载体）
'  列1-15: 原始数据，列16: 状态，列17: 配对类型，列18: 账户
'------------------------------------------------------------------------------------
Public 割单数组() As Variant
Public 割单行数 As Long
'------------------------------------------------------------------------------------
Private Const 时段早盘 = "早盘9:30-10:00"
Private Const 时段上午中 = "上午中段10:00-11:00"
Private Const 时段午前收盘 = "午前收盘11:00-11:30"
Private Const 时段午盘 = "午盘13:00-14:00"
Private Const 时段尾盘前 = "尾盘前段14:00-14:29"
Private Const 时段尾盘后 = "尾盘后段14:30-15:00"
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
'导入信息：交割单
'========================================================================================
'========================================================================================
Sub STCALL割册管理_XLS交割单G2导入()
    Dim MSG As String
    ' 如果割单数组已有数据，跳过文件选择
    Dim ARRYM As Variant
    If 割单行数 > 0 Then
        ARRYM = 割单数组
        GoTo 开始处理
    End If
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
    '注：必须设为自动计算，否则 ="..." 公式不会被求值，显示为 0
    Application.Calculation = xlCalculationAutomatic
    Dim WB割 As Workbook
    Set WB割 = GetObject(FILEOPEN)
    WB割.Application.Calculate  ' 强制计算 ="..." 公式
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
开始处理:
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
    Dim 典集委类送股 As New Dictionary
    Dim 典集委类配号 As New Dictionary
    Dim 典集委类交易码票 As New Dictionary
    Dim 典集委类交易码基 As New Dictionary
    Dim 典集委类交易码他 As New Dictionary
    '------------------------------------------------------------------------------------
    '制作字典
    '------------------------------------------------------------------------------------
    Dim CIDV As Variant
    Dim CIDL As String
    Dim sdate As Variant
    Dim R As Integer
    Dim 值委托类别 As String
    Dim 表名 As String
    Dim X As Integer
    For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
        值委托类别 = ARRYM(R, 位列割委托类别)
        ' 去掉 ="" 包装（华宝交割单导出格式）
        值委托类别 = Replace(值委托类别, "=", "")
        值委托类别 = Replace(值委托类别, """", "")
        ' 跳过空行或无效行
        If 值委托类别 = "" Or 值委托类别 = "0" Then GoTo 下一行
        sdate = ARRYM(R, 位列割成交日期)
        ' 处理日期：可能为 8位数字串("20260105")、="20260105"格式、或Excel日期序列号
        If IsDate(sdate) Then
            ARRYM(R, 位列割成交日期) = CDate(sdate)
        ElseIf VarType(sdate) = vbString Then
            ' 去掉 ="" 包装
            sdate = Replace(sdate, "=", "")
            sdate = Replace(sdate, """", "")
            If Len(sdate) >= 8 Then
                ARRYM(R, 位列割成交日期) = DateSerial(CLng(Left$(sdate, 4)), CLng(Mid$(sdate, 5, 2)), CLng(Mid$(sdate, 7, 2)))
            End If
        End If
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
        ElseIf 值委托类别 = "送股" Then
            典集委类送股.Add Key:=R, Item:=R
        '-----------------------------------------------
        ElseIf 值委托类别 = "买入" Or 值委托类别 = "卖出" Then
            CIDV = ARRYM(R, 位列割证券代码)
            ' 去掉 ="" 包装
            If VarType(CIDV) = vbString Then
                CIDV = Replace(CIDV, "=", "")
                CIDV = Replace(CIDV, """", "")
            End If
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
下一行: Next R
    '------------------------------------------------------------------------------------
    '输出
    '------------------------------------------------------------------------------------
    Dim WB As Workbook
    Set WB = ThisWorkbook
    '--------------------------------------------------------------------------------
    '买卖相关
    '--------------------------------------------------------------------------------
    Dim 典集码类额 As New Dictionary
    Dim 典集码类数零近 As New Dictionary
    Dim 典集码类数零赚 As New Dictionary
    Dim 典集码类数零赔 As New Dictionary
    Dim 典集码类数正 As New Dictionary
    Dim 典集码类数负 As New Dictionary
    Dim 典集码类数未配对 As New Dictionary
    Dim 值累数 As Long
    Dim 值累额 As Double
    Dim 值成交日期 As Date
    Dim 值累额码类数正 As Double
    Dim 值累额码类数负 As Double
    Dim 值累额码类数零近月 As Double
    Dim 值累额码类数零远赚 As Double
    Dim 值累额码类数零远赔 As Double
    '--------------------------------------------------------------------------------
    For X = 1 To 典集委类交易码票.Count
        CIDL = 典集委类交易码票.Keys(X - 1)
        值累数 = 0
        值累额 = 0
        值成交日期 = Date - 200
        Dim 有未配对 As Boolean: 有未配对 = False
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                值累数 = 值累数 + ARRYM(R, 位列割成交数量)
                值累额 = 值累额 + ARRYM(R, 位列割发生金额)
                If 割单行数 > 0 Then
                    If ARRYM(R, 常割单列状态) = "未配对交易" Then
                        值累数 = 值累数 - ARRYM(R, 位列割成交数量)
                        值累额 = 值累额 - ARRYM(R, 位列割发生金额)
                        有未配对 = True
                    End If
                End If
                If ARRYM(R, 位列割成交日期) > 值成交日期 Then 值成交日期 = ARRYM(R, 位列割成交日期)
            End If
        Next R
        If 有未配对 Then 典集码类数未配对.Add Key:=CIDL, Item:=0
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
        '----------------------------------------------------------------------------
        Debug.Print X, CIDL, 值累数
        'If X > 55 Then Exit For
        '----------------------------------------------------------------------------
    Next X
    '--------------------------------------------------------------------------------
    '格式化
    '--------------------------------------------------------------------------------
    表名 = "割单" & 后台辅程_账户后缀(ARRYM, 2)
    Call IQQQ展擎出程至页割版(WB, 表名, 是否建表:=True, 章色:=常色十蓝, 章签:="【交易完全列表】")
    WB.Sheets(表名).Columns(位列割发生金额).HorizontalAlignment = xlRight
    WB.Sheets(表名).Columns(位列割成交数量).HorizontalAlignment = xlRight
    WB.Sheets(表名).Columns(位列割成交日期).NumberFormatLocal = 全设格式of日期
    WB.Sheets(表名).Columns(位列割成交日期).ColumnWidth = 14
    WB.Sheets(表名).Columns(位列割成交时间).ColumnWidth = 10
    WB.Sheets(表名).Columns(位列割证券名称).ColumnWidth = 12
    WB.Sheets(表名).Columns(位列割证券CIDL).ColumnWidth = 10
    WB.Sheets(表名).Columns(位列割证券CIDL).Font.Color = 常色五灰
    WB.Sheets(表名).Columns(位列割其他费).Hidden = True
    WB.Sheets(表名).Columns(位列割成交编号).Hidden = True
    WB.Sheets(表名).Columns(位列割发生金额).ColumnWidth = 10
    WB.Sheets(表名).Columns(位列割发生金额).NumberFormatLocal = 全设格式of零位
'    WB.Sheets(表名).Columns(位列割发生金额).Font.Bold = True
    WB.Sheets(表名).Columns(位列割成交金额).NumberFormatLocal = 全设格式of零位
    WB.Sheets(表名).Columns(位列割成交金额).Font.Color = 常色五灰
    WB.Sheets(表名).Columns(位列割佣金).Font.Color = 常色五灰
    WB.Sheets(表名).Columns(位列割印花税).Font.Color = 常色五灰
    WB.Sheets(表名).Columns(位列割过户费).Font.Color = 常色五灰
    WB.Sheets(表名).Columns(位列割其他费).Font.Color = 常色五灰
    WB.Sheets(表名).Columns(位列割成交价格).Font.Color = 常色二灰
    WB.Sheets(表名).Columns(位列割成交数量).ColumnWidth = 12
    WB.Sheets(表名).Columns(位列割成交数量).NumberFormatLocal = "[黑色]0_);[蓝色](0)"
    '--------------------------------------------------------------------------------
    Dim 典集委类交易个票 As New Dictionary
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(WB, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】累数正（未清仓）：" & 典集码类数正.Count)
    For X = 1 To 典集码类数正.Count
        CIDL = 典集码类数正.Keys(X - 1)
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色主靛, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(WB, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】累数〇（30日内）：" & 典集码类数零近.Count & " , " & CLng(值累额码类数零近月))
    For X = 1 To 典集码类数零近.Count
        CIDL = 典集码类数零近.Keys(X - 1)
       For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色蒂芙尼蓝, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(WB, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】累数〇（30日前.赚）：" & 典集码类数零赚.Count & " , " & CLng(值累额码类数零远赚))
    For X = 1 To 典集码类数零赚.Count
        CIDL = 典集码类数零赚.Keys(X - 1)
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色六青, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(WB, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】累数〇（30日前.赔）：" & 典集码类数零赔.Count & " , " & CLng(值累额码类数零远赔))
    For X = 1 To 典集码类数零赔.Count
        CIDL = 典集码类数零赔.Keys(X - 1)
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                典集委类交易个票.Add Key:=R, Item:=R
            End If
        Next R
        Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色四青, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
    Next X
    '--------------------------------------------------------------------------------
    Call IQQQ展擎出程至页割版(WB, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【交易】累数负（不完整）：" & 典集码类数未配对.Count)
    For X = 1 To 典集码类数未配对.Count
        CIDL = 典集码类数未配对.Keys(X - 1)
        For R = LBound(ARRYM, 1) + 1 To UBound(ARRYM, 1)
            If ARRYM(R, 位列割证券CIDL) = CIDL Then
                If 割单行数 = 0 Or ARRYM(R, 常割单列状态) = "未配对交易" Then
                    典集委类交易个票.Add Key:=R, Item:=R
                End If
            End If
        Next R
        If 典集委类交易个票.Count > 0 Then
            Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色五黄, 强列:=位列割证券代码, 强序:=xlAscending, 典码输出:=典集委类交易个票, 区签:=CIDL, 区释:="")
        End If
    Next X
    '--------------------------------------------------------------------------------
    Set 典集委类交易个票 = Nothing
    '--------------------------------------------------------------------------------
    '剔除类别 新股相关
    '--------------------------------------------------------------------------------
    '表名 = "IO割SS"
    '剔除类别
    Call IQQQ展擎出程至页割版(WB, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【剔除类别】")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色八蓝, 典码输出:=典集委类融券, 区签:="融券", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色八蓝, 典码输出:=典集委类融券购回, 区签:="融券购回", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色六蓝, 典码输出:=典集委类其他, 区签:="其他", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色六蓝, 典码输出:=典集委类红利, 区签:="红利", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色六蓝, 典码输出:=典集委类送股, 区签:="送股", 区释:="")
    'Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色十红, 典码输出:=典集委类组合费用, 区签:="组合费用", 区释:="")
    '新股相关
    Call IQQQ展擎出程至页割版(WB, 表名, 是否建表:=False, 章色:=常色四青, 章签:="【新股类别】")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色六青, 典码输出:=典集委类申购还款, 区签:="申购还款", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色六青, 典码输出:=典集委类申购扣款, 区签:="申购扣款", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色六青, 典码输出:=典集委类中签扣款, 区签:="中签扣款", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色六青, 典码输出:=典集委类中签通知, 区签:="中签通知", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色四青, 典码输出:=典集委类托管转入, 区签:="托管转入", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色四青, 典码输出:=典集委类托管转出, 区签:="托管转出", 区释:="")
    Call IQQQ展擎出程至页割版(WB, 表名, ARRYM, 基色底:=常色二青, 典码输出:=典集委类配号, 区签:="配号", 区释:="")
'========================================================================================
    UTL宏工具_END
    MSG = "导入华宝交割单" & vbCrLf
'    STCALL花册管理_重制花天P2正程导入益盟 = MSG
End Sub




'========================================================================================
'注意：【表名输出】（工表的名字）不能是数字类型
'========================================================================================
Function IQQQ展擎出程至页割版( _
          ByRef WB As Workbook _
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
    Dim X As Integer, Y As Integer
'========================================================================================
'准备工作
'========================================================================================
    '------------------------------------------------------------------------------------
    '建页
    '------------------------------------------------------------------------------------
    Dim WSTO As Worksheet
    If 是否建表 = True Or UTL判断工表存在(表名输出, WB) = False Then
        Call PBASE格程工具_表操工表新增(WSTO, 表名输出, WB:=WB, 基色底:=章色)
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
    Set WSTO = WB.Sheets(表名输出)
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
    For X = 1 To 典码输出.Count
        定位原序 = 典码输出.Items(X - 1)
        For Y = LBound(谕组, 2) To UBound(谕组, 2)
            ARRTO(X, Y) = 谕组(定位原序, Y)
        Next Y
    Next X
    典码输出.RemoveAll
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
    WSTO.Cells(行号标签, 位列割证券名称).HorizontalAlignment = xlRight
    WSTO.Cells(行号标签, 位列割委托类别).HorizontalAlignment = xlRight
    WSTO.Cells(行号标签, 位列割成交数量).Font.Color = 常色六灰
    WSTO.Cells(行号标签, 位列割成交数量).HorizontalAlignment = xlRight
    WSTO.Cells(行号标签, 位列割发生金额).HorizontalAlignment = xlRight
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
            .HorizontalAlignment = xlRight
        End With
        With .Cells(1, 1).Resize(计数输出, 1)
            .Interior.TintAndShade = 0.5
        End With
    End With
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



'========================================================================================
'交割单深度分析 — 5维度：⑥择时 → ⑦仓位 → ⑤成本 → ①盈亏 → ③T+0
'数据源：华宝证券交割单查询 XLS 文件
'========================================================================================
'========================================================================================
'常量
'========================================================================================
'------------------------------------------------------------------------------------'时段标签
'========================================================================================
'========================================================================================
'入口主调
'========================================================================================
'========================================================================================
Sub STCALL割册管理_XLS交割单G3解析()
    ' 如果割单数组已有数据，跳过文件选择
    Dim ARR原始 As Variant
    If 割单行数 > 0 Then
        ARR原始 = 割单数组
        GoTo 开始处理2
    End If
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
    Call PBASE格程工具_表操工表新增(WS割, 常册割析, 基色底:=常色十蓝)
'========================================================================================
    '读取 XLS 文件到数组（自动计算，确保 ="..." 公式被求值）
    Application.Calculation = xlCalculationAutomatic
    Dim WB割 As Workbook
    Set WB割 = GetObject(FILEOPEN)
    With WB割.ActiveSheet
        ARR原始 = .Range("A1").CurrentRegion
    End With
    WB割.Close False
    Set WB割 = Nothing
    '重命名Sheet加上账户后缀
    WS割.Name = 常册割析 & 后台辅程_账户后缀(ARR原始, 2)
开始处理2:
    If WS割 Is Nothing Then Call PBASE格程工具_表操工表新增(WS割, 常册割析 & 后台辅程_账户后缀(ARR原始, 2), 基色底:=常色十蓝)
    '过滤只保留买卖记录
    Dim 计数原始 As Long
    计数原始 = UBound(ARR原始, 1)
    Dim 计数交易 As Long
    计数交易 = 0
    Dim R As Long, j As Long
    For R = 2 To 计数原始
        Dim 类别 As String
        类别 = Replace(ARR原始(R, 6), "=", "")
        类别 = Replace(类别, """", "")
        If 类别 = "买入" Or 类别 = "卖出" Then 计数交易 = 计数交易 + 1
    Next
    If 计数交易 = 0 Then
        WS割.Cells(1, 1) = "无有效交易记录"
        UTL宏工具_END
        Exit Sub
    End If
    Dim ARR买卖 As Variant
    Dim 指针 As Long, vDate As Variant, sD As String
    ReDim ARR买卖(1 To 计数交易, 1 To 15)
    指针 = 0
    For R = 2 To 计数原始
        类别 = Replace(ARR原始(R, 6), "=", "")
        类别 = Replace(类别, """", "")
        If 类别 = "买入" Or 类别 = "卖出" Then
            指针 = 指针 + 1
            For j = 1 To 15: ARR买卖(指针, j) = ARR原始(R, j): Next
            ' 解析日期
                        vDate = ARR原始(R, 1)
            If IsDate(vDate) Then
                ARR买卖(指针, 1) = CDate(vDate)
            ElseIf VarType(vDate) = vbString Then
                                sD = Replace(vDate, "=", "")
                sD = Replace(sD, """", "")
                If Len(sD) >= 8 Then
                    ARR买卖(指针, 1) = DateSerial(CLng(Left$(sD, 4)), CLng(Mid$(sD, 5, 2)), CLng(Mid$(sD, 7, 2)))
                End If
            End If
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
    Dim ARR随手 As Variant
    Dim ARR月度 As Variant
    Dim ARR活跃 As Variant
    Dim ARR板块 As Variant

    后台辅程割析_P1择时分析 ARR买卖, ARR择时
    后台辅程割析_P2仓位分析 ARR买卖, ARR仓位
    后台辅程割析_P3成本分析 ARR买卖, ARR成本
    后台辅程割析_P4盈亏分析 ARR买卖, ARR盈亏
    后台辅程割析_P5T加0分析 ARR买卖, ARR_T0
    后台辅程割析_P6随手单分析 ARR买卖, ARR随手
    后台辅程割析_P7月度趋势 ARR买卖, ARR月度
    后台辅程割析_P8活跃股票 ARR买卖, ARR活跃
    后台辅程割析_P9板块偏好 ARR买卖, ARR板块
'========================================================================================
    '输出到表
    后台辅程割析_输出 WS割, ARR买卖, ARR择时, ARR仓位, ARR成本, ARR盈亏, ARR_T0, ARR随手, ARR月度, ARR活跃, ARR板块
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

'========================================================================================
'========================================================================================
'⑥ 择时分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_P1择时分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)

    '7个时段: 早盘 / 上午中 / 午前 / 午盘 / 尾盘前 / 尾盘后(收盘前半小时) / 其他
    Const 时段数 = 7
    Dim 时段列表 As Variant
    时段列表 = Array(时段早盘, 时段上午中, 时段午前收盘, 时段午盘, 时段尾盘前, 时段尾盘后, 时段其他)

    Dim 段计数(0 To 时段数 - 1) As Long
    Dim 段买笔(0 To 时段数 - 1) As Long
    Dim 段卖笔(0 To 时段数 - 1) As Long
    Dim 段买额(0 To 时段数 - 1) As Double
    Dim 段卖额(0 To 时段数 - 1) As Double

    '分钟级统计（最活跃分钟点）
    Dim 分钟典 As New Dictionary
    Dim 分钟买典 As New Dictionary
    Dim 分钟卖典 As New Dictionary
    Dim i As Long
    Dim idx As Long
    For i = 1 To 计数
        Dim s时间 As String
        s时间 = Trim(ARR(i, 位列割成交时间))
        Dim 小时 As Long, 分钟 As Long
        小时 = Val(Left(s时间, 2))
        分钟 = Val(Mid(s时间, 4, 2))
        Dim 时间分 As Long
        时间分 = 小时 * 60 + 分钟

        '累计分钟
        Dim 分钟键 As String
        分钟键 = Format(小时, "00") & ":" & Format(分钟, "00")
        If 分钟典.Exists(分钟键) Then
            分钟典(分钟键) = 分钟典(分钟键) + 1
        Else
            分钟典.Add 分钟键, 1
        End If
        Dim 类别 As String
        类别 = Trim(ARR(i, 位列割委托类别))
        If 类别 = "买入" Then
            If 分钟买典.Exists(分钟键) Then 分钟买典(分钟键) = 分钟买典(分钟键) + 1 Else 分钟买典.Add 分钟键, 1
        Else
            If 分钟卖典.Exists(分钟键) Then 分钟卖典(分钟键) = 分钟卖典(分钟键) + 1 Else 分钟卖典.Add 分钟键, 1
        End If

        '确定时段
        If 时间分 >= 570 And 时间分 < 600 Then        '9:30-10:00
            idx = 0
        ElseIf 时间分 >= 600 And 时间分 < 660 Then    '10:00-11:00
            idx = 1
        ElseIf 时间分 >= 660 And 时间分 < 690 Then    '11:00-11:30
            idx = 2
        ElseIf 时间分 >= 780 And 时间分 < 840 Then    '13:00-14:00
            idx = 3
        ElseIf 时间分 >= 840 And 时间分 < 870 Then    '14:00-14:29
            idx = 4
        ElseIf 时间分 >= 870 And 时间分 <= 900 Then   '14:30-15:00
            idx = 5
        Else
            idx = 6
        End If

        段计数(idx) = 段计数(idx) + 1
        Dim 金额 As Double
        金额 = Val(ARR(i, 位列割成交金额))

        If 类别 = "买入" Then
            段买笔(idx) = 段买笔(idx) + 1
            段买额(idx) = 段买额(idx) + 金额
        Else
            段卖笔(idx) = 段卖笔(idx) + 1
            段卖额(idx) = 段卖额(idx) + 金额
        End If
    Next

    '输出：时段表
    ReDim ARRTO(1 To 时段数 + 10, 1 To 12)
    ARRTO(1, 1) = "时段": ARRTO(1, 2) = "笔数": ARRTO(1, 3) = "占比"
    ARRTO(1, 4) = "买入笔数": ARRTO(1, 5) = "买入金额"
    ARRTO(1, 6) = "卖出笔数": ARRTO(1, 7) = "卖出金额"
    ARRTO(1, 8) = "买卖净额": ARRTO(1, 9) = "方向"

    For idx = 0 To 时段数 - 1
        Dim 行 As Long
        行 = idx + 2
        ARRTO(行, 1) = 时段列表(idx)
        ARRTO(行, 2) = 段计数(idx)
        ARRTO(行, 3) = Format(段计数(idx) / 计数, "0.000%")
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

    '输出：最活跃分钟点 TOP5
    Dim 分钟行 As Long
    分钟行 = 时段数 + 3
    ARRTO(分钟行, 1) = "最活跃分钟点 TOP5"
    ARRTO(分钟行 + 1, 1) = "分钟": ARRTO(分钟行 + 1, 2) = "笔数"
    ARRTO(分钟行 + 1, 3) = "占总比": ARRTO(分钟行 + 1, 4) = "买入": ARRTO(分钟行 + 1, 5) = "占买入"
    ARRTO(分钟行 + 1, 6) = "卖出": ARRTO(分钟行 + 1, 7) = "占卖出"
    '排序找TOP5
    Dim 分钟列表 As Variant
    分钟列表 = 分钟典.Keys
    Dim j As Long, k As Long
    For j = 0 To 分钟典.Count - 2
        For k = j + 1 To 分钟典.Count - 1
            If 分钟典(分钟列表(j)) < 分钟典(分钟列表(k)) Then
                Dim tmpK As String
                tmpK = 分钟列表(j)
                分钟列表(j) = 分钟列表(k)
                分钟列表(k) = tmpK
            End If
        Next
    Next
    Dim 总买笔 As Long, 总卖笔 As Long
    总买笔 = 0: 总卖笔 = 0
    For idx = 0 To 时段数 - 1
        总买笔 = 总买笔 + 段买笔(idx)
        总卖笔 = 总卖笔 + 段卖笔(idx)
    Next
    For j = 0 To Application.Min(分钟典.Count - 1, 4)
        分钟键 = 分钟列表(j)
        ARRTO(分钟行 + 2 + j, 1) = 分钟键
        ARRTO(分钟行 + 2 + j, 2) = 分钟典(分钟键)
        ARRTO(分钟行 + 2 + j, 3) = Format(分钟典(分钟键) / 计数, "0.000%")
        Dim 买笔 As Long, 卖笔 As Long
        If 分钟买典.Exists(分钟键) Then 买笔 = 分钟买典(分钟键) Else 买笔 = 0
        If 分钟卖典.Exists(分钟键) Then 卖笔 = 分钟卖典(分钟键) Else 卖笔 = 0
        ARRTO(分钟行 + 2 + j, 4) = 买笔
        ARRTO(分钟行 + 2 + j, 5) = IIf(总买笔 > 0, Format(买笔 / 总买笔, "0.000%"), "")
        ARRTO(分钟行 + 2 + j, 6) = 卖笔
        ARRTO(分钟行 + 2 + j, 7) = IIf(总卖笔 > 0, Format(卖笔 / 总卖笔, "0.000%"), "")
    Next
End Sub
'========================================================================================
'========================================================================================
'⑦ 仓位分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_P2仓位分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
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

    Dim i As Long, idx As Long
    For i = 1 To 计数
        Dim 金额 As Double
        金额 = Val(ARR(i, 位列割成交金额))
        For idx = 0 To 5
            If 金额 <= 位上限(idx) Then
                位计数(idx) = 位计数(idx) + 1
                位金额(idx) = 位金额(idx) + 金额
                Exit For
            End If
        Next
    Next

    '输出仓位分段：6行×5列
    ReDim ARRTO(1 To 26, 1 To 6)
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
        ARRTO(行, 1) = Mid(位标签(idx), 2)
        ARRTO(行, 2) = 位计数(idx)
        ARRTO(行, 3) = Format(位计数(idx) / 计数, "0.000%")
        ARRTO(行, 4) = 位金额(idx)
        If 总金额 > 0 Then ARRTO(行, 5) = Format(位金额(idx) / 总金额, "0.000%")
    Next

    ARRTO(7, 1) = "交易笔数合计": ARRTO(7, 2) = 计数
    ARRTO(8, 1) = "总成交金额": ARRTO(8, 4) = 总金额

    '--- 集中度分析 ---
    Dim 金额列表() As Double
    ReDim 金额列表(1 To 计数)
    For i = 1 To 计数
        金额列表(i) = Val(ARR(i, 位列割成交金额))
    Next
    Dim j As Long
    For i = 1 To 计数 - 1
        For j = i + 1 To 计数
            If 金额列表(i) < 金额列表(j) Then
                Dim tmp As Double
                tmp = 金额列表(i)
                金额列表(i) = 金额列表(j)
                金额列表(j) = tmp
            End If
        Next
    Next
    Dim 前1笔 As Long: 前1笔 = Int(计数 * 0.01 + 0.5)
    Dim 前5笔 As Long: 前5笔 = Int(计数 * 0.05 + 0.5)
    Dim 前20笔 As Long: 前20笔 = Int(计数 * 0.2 + 0.5)
    If 前1笔 < 1 Then 前1笔 = 1
    If 前5笔 < 1 Then 前5笔 = 1
    If 前20笔 < 1 Then 前20笔 = 1
    Dim 前1总额 As Double: 前1总额 = 0
    Dim 前5总额 As Double: 前5总额 = 0
    Dim 前20总额 As Double: 前20总额 = 0
    For i = 1 To 计数
        If i <= 前1笔 Then 前1总额 = 前1总额 + 金额列表(i)
        If i <= 前5笔 Then 前5总额 = 前5总额 + 金额列表(i)
        If i <= 前20笔 Then 前20总额 = 前20总额 + 金额列表(i)
    Next
    ARRTO(9, 1) = "集中度分析"
    ARRTO(10, 1) = "前1%交易": ARRTO(10, 2) = 前1笔 & "笔"
    ARRTO(10, 4) = "占总额": ARRTO(10, 5) = Format(前1总额 / 总金额, "0.000%")
    ARRTO(11, 1) = "前5%交易": ARRTO(11, 2) = 前5笔 & "笔"
    ARRTO(11, 4) = "占总额": ARRTO(11, 5) = Format(前5总额 / 总金额, "0.000%")
    ARRTO(12, 1) = "前20%交易": ARRTO(12, 2) = 前20笔 & "笔"
    ARRTO(12, 4) = "占总额": ARRTO(12, 5) = Format(前20总额 / 总金额, "0.000%")

    '--- 两账号对比 ---
    Dim 账1笔 As Long: 账1笔 = 0
    Dim 账2笔 As Long: 账2笔 = 0
    Dim 账1额 As Double: 账1额 = 0
    Dim 账2额 As Double: 账2额 = 0
    Dim 账1金额列表() As Double
    Dim 账2金额列表() As Double
    ReDim 账1金额列表(1 To 计数)
    ReDim 账2金额列表(1 To 计数)
    Dim 账1数 As Long: 账1数 = 0
    Dim 账2数 As Long: 账2数 = 0
    Dim 账名 As String
    For i = 1 To 计数
        账名 = STCALL割单工具_识别账户(Trim(ARR(i, 位列割证券CIDL)))
        金额 = Val(ARR(i, 位列割成交金额))
        If 账名 = 常仓名宝彦 Then
            账1笔 = 账1笔 + 1: 账1额 = 账1额 + 金额
            账1数 = 账1数 + 1: 账1金额列表(账1数) = 金额
        ElseIf 账名 = 常仓名宝福 Then
            账2笔 = 账2笔 + 1: 账2额 = 账2额 + 金额
            账2数 = 账2数 + 1: 账2金额列表(账2数) = 金额
        End If
    Next
    '排序找中位数
    For i = 1 To 账1数 - 1
        For j = i + 1 To 账1数
            If 账1金额列表(i) > 账1金额列表(j) Then
                tmp = 账1金额列表(i)
                账1金额列表(i) = 账1金额列表(j)
                账1金额列表(j) = tmp
            End If
        Next
    Next
    For i = 1 To 账2数 - 1
        For j = i + 1 To 账2数
            If 账2金额列表(i) > 账2金额列表(j) Then
                tmp = 账2金额列表(i)
                账2金额列表(i) = 账2金额列表(j)
                账2金额列表(j) = tmp
            End If
        Next
    Next
    ARRTO(13, 1) = "两账号对比"
    ARRTO(14, 1) = "账号": ARRTO(14, 2) = "笔数": ARRTO(14, 3) = "总金额"
    ARRTO(14, 4) = "均价": ARRTO(14, 5) = "中位数"
    ARRTO(15, 1) = 常仓名宝彦: ARRTO(15, 2) = 账1笔
    ARRTO(15, 3) = Round(账1额, 0)
    If 账1笔 > 0 Then ARRTO(15, 4) = Round(账1额 / 账1笔, 0) Else ARRTO(15, 4) = 0
    ARRTO(15, 5) = IIf(账1数 > 0, 账1金额列表(账1数 \ 2 + 1), 0)
    ARRTO(16, 1) = 常仓名宝福: ARRTO(16, 2) = 账2笔
    ARRTO(16, 3) = Round(账2额, 0)
    If 账2笔 > 0 Then ARRTO(16, 4) = Round(账2额 / 账2笔, 0) Else ARRTO(16, 4) = 0
    ARRTO(16, 5) = IIf(账2数 > 0, 账2金额列表(账2数 \ 2 + 1), 0)
End Sub
'========================================================================================
'========================================================================================
'⑤ 成本分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_P3成本分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)

    '收集佣金率
    Dim 佣金率集合() As Double
    ReDim 佣金率集合(1 To 计数)
    Dim 有效 As Long
    有效 = 0

    'ETF vs 个股统计
    Dim ETF佣金 As Double, ETF成交 As Double
    Dim 个股佣金 As Double, 个股成交 As Double
    Dim ETF笔数 As Long, 个股笔数 As Long
    ETF成交 = 0: ETF佣金 = 0: ETF笔数 = 0
    个股成交 = 0: 个股佣金 = 0: 个股笔数 = 0

    '分账号佣金率
    Dim 账1佣金 As Double, 账1成交 As Double, 账1笔 As Long
    Dim 账2佣金 As Double, 账2成交 As Double, 账2笔 As Long
    账1佣金 = 0: 账1成交 = 0: 账1笔 = 0
    账2佣金 = 0: 账2成交 = 0: 账2笔 = 0

    '卖出印花税
    Dim 卖印花税 As Double, 卖成交 As Double
    卖印花税 = 0: 卖成交 = 0

    Dim 总佣金 As Double, 总印花税 As Double, 总过户费 As Double, 总成交 As Double
    Dim 总其他费 As Double: 总其他费 = 0
    Dim i As Long
    For i = 1 To 计数
        Dim 佣金 As Double, 成交 As Double
        Dim 名称 As String, 类别 As String
        佣金 = Val(ARR(i, 位列割佣金))
        成交 = Val(ARR(i, 位列割成交金额))
        名称 = Trim(ARR(i, 位列割证券名称))
        类别 = Trim(ARR(i, 位列割委托类别))
        总佣金 = 总佣金 + 佣金
        总印花税 = 总印花税 + Val(ARR(i, 位列割印花税))
        总过户费 = 总过户费 + Val(ARR(i, 位列割过户费))
        总其他费 = 总其他费 + Val(ARR(i, 位列割其他费))
        总成交 = 总成交 + 成交
        'ETF判断
        If InStr(名称, "ETF") > 0 Or InStr(名称, "基金") > 0 Or InStr(名称, "LOF") > 0 Then
            ETF成交 = ETF成交 + 成交: ETF佣金 = ETF佣金 + 佣金: ETF笔数 = ETF笔数 + 1
        Else
            个股成交 = 个股成交 + 成交: 个股佣金 = 个股佣金 + 佣金: 个股笔数 = 个股笔数 + 1
        End If
        '分账号
        Dim 账名 As String
        账名 = STCALL割单工具_识别账户(Trim(ARR(i, 位列割证券CIDL)))
        If 账名 = 常仓名宝彦 Then
            账1佣金 = 账1佣金 + 佣金: 账1成交 = 账1成交 + 成交: 账1笔 = 账1笔 + 1
        ElseIf 账名 = 常仓名宝福 Then
            账2佣金 = 账2佣金 + 佣金: 账2成交 = 账2成交 + 成交: 账2笔 = 账2笔 + 1
        End If
        '卖出印花税
        If 类别 = "卖出" Then
            卖印花税 = 卖印花税 + Val(ARR(i, 位列割印花税))
            卖成交 = 卖成交 + 成交
        End If
        If 成交 > 0 And 佣金 > 0 Then
            有效 = 有效 + 1
            佣金率集合(有效) = 佣金 / 成交 * 10000
        End If
    Next

    ReDim ARRTO(1 To 24, 1 To 4)
    Dim 行号 As Long
    行号 = 1

    '--- 佣金率基本统计 ---
    ARRTO(行号, 1) = "指标": ARRTO(行号, 2) = "数值"
    行号 = 2
    ARRTO(行号, 1) = "有效样本数": ARRTO(行号, 2) = 有效

    If 有效 > 0 Then
        Dim 总和 As Double
        总和 = 0
        For i = 1 To 有效
            总和 = 总和 + 佣金率集合(i)
        Next
        行号 = 3: ARRTO(行号, 1) = "平均佣金率(万分)": ARRTO(行号, 2) = 总和 / 有效
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
        Dim p5 As Long, p95 As Long
        p5 = Int(有效 * 0.05 + 0.5): If p5 < 1 Then p5 = 1
        p95 = Int(有效 * 0.95 + 0.5): If p95 > 有效 Then p95 = 有效
        行号 = 7: ARRTO(行号, 1) = "P5(万分)": ARRTO(行号, 2) = 佣金率集合(p5)
        行号 = 8: ARRTO(行号, 1) = "P95(万分)": ARRTO(行号, 2) = 佣金率集合(p95)
    End If

    '--- 分账号佣金率 ---
    行号 = 10: ARRTO(行号, 1) = "分账号佣金率"
    行号 = 11: ARRTO(行号, 1) = "账号": ARRTO(行号, 2) = "笔数": ARRTO(行号, 3) = "佣金率(万分)"
    行号 = 12: ARRTO(行号, 1) = 常仓名宝彦: ARRTO(行号, 2) = 账1笔
    If 账1成交 > 0 Then ARRTO(行号, 3) = Round(账1佣金 / 账1成交 * 10000, 2) Else ARRTO(行号, 3) = 0
    行号 = 13: ARRTO(行号, 1) = 常仓名宝福: ARRTO(行号, 2) = 账2笔
    If 账2成交 > 0 Then ARRTO(行号, 3) = Round(账2佣金 / 账2成交 * 10000, 2) Else ARRTO(行号, 3) = 0

    '--- ETF vs 个股佣金对比 ---
    行号 = 15: ARRTO(行号, 1) = "类别": ARRTO(行号, 2) = "笔数": ARRTO(行号, 3) = "成交额": ARRTO(行号, 4) = "佣金率(万分)"
    行号 = 16: ARRTO(行号, 1) = "个股": ARRTO(行号, 2) = 个股笔数
    ARRTO(行号, 3) = 个股成交
    If 个股成交 > 0 Then ARRTO(行号, 4) = Round(个股佣金 / 个股成交 * 10000, 2) Else ARRTO(行号, 4) = 0
    行号 = 17: ARRTO(行号, 1) = "ETF/基金": ARRTO(行号, 2) = ETF笔数
    ARRTO(行号, 3) = ETF成交
    If ETF成交 > 0 Then ARRTO(行号, 4) = Round(ETF佣金 / ETF成交 * 10000, 2) Else ARRTO(行号, 4) = 0
    If ETF成交 > 0 And ETF佣金 > 0 Then
        行号 = 18: ARRTO(行号, 1) = "!ETF有佣金"
        ARRTO(行号, 2) = "ETF成交" & Round(ETF成交) & "元, 佣金" & Round(ETF佣金, 2) & "元"
    ElseIf ETF成交 > 0 And ETF佣金 = 0 Then
        行号 = 18: ARRTO(行号, 1) = "OKETF免佣金"
        ARRTO(行号, 2) = "ETF成交" & Round(ETF成交) & "元, 佣金0元"
    End If

    '--- 费用结构 ---
    Dim 总费用 As Double
    总费用 = 总佣金 + 总印花税 + 总过户费 + 总其他费
    行号 = 20: ARRTO(行号, 1) = "费用项目": ARRTO(行号, 2) = "金额": ARRTO(行号, 3) = "费率": ARRTO(行号, 4) = "每万元"
    行号 = 21: ARRTO(行号, 1) = "总成交金额": ARRTO(行号, 2) = 总成交
    行号 = 22: ARRTO(行号, 1) = "佣金": ARRTO(行号, 2) = Round(总佣金, 2)
    If 总成交 > 0 Then ARRTO(行号, 3) = Format(总佣金 / 总成交, "0.000%")
    ARRTO(行号, 4) = Round(总佣金 / 总成交 * 10000, 2)
    行号 = 23: ARRTO(行号, 1) = "印花税": ARRTO(行号, 2) = Round(总印花税, 2)
    If 总成交 > 0 Then ARRTO(行号, 3) = Format(总印花税 / 总成交, "0.000%")
    If 卖成交 > 0 Then ARRTO(行号, 4) = "卖出税率" & Round(卖印花税 / 卖成交 * 10000, 2) & "万分"
    行号 = 24: ARRTO(行号, 1) = "过户费": ARRTO(行号, 2) = Round(总过户费, 2)
    If 总成交 > 0 Then ARRTO(行号, 3) = Format(总过户费 / 总成交, "0.000%")
    '费用合计在输出段单独处理
End Sub
'========================================================================================
'========================================================================================
'① 盈亏分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_P4盈亏分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
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
    Dim 日期 As Date, 三个月前 As Date
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
        If 买额(idx) > 0 Then ARRTO(idx + 1, 4) = Format(净利润 / 买额(idx), "0.000%")
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
    If 总买额 > 0 Then ARRTO(去重数 + 2, 4) = Format(总利润 / 总买额, "0.000%")
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
Private Sub 后台辅程割析_P5T加0分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
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

    Dim i As Long, j As Long, idx As Long
    For i = 1 To 计数
        Dim s日期 As String, s代码 As String
        s日期 = Trim(ARR(i, 位列割成交日期))
        s代码 = Trim(ARR(i, 位列割证券代码))

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
        If 类别 = "买入" Then
            组买额(idx) = 组买额(idx) + 金额
            组买笔(idx) = 组买笔(idx) + 1
        Else
            组卖额(idx) = 组卖额(idx) + 金额
            组卖笔(idx) = 组卖笔(idx) + 1
        End If
    Next

    '筛选同时有买和卖的组(T+0)
    Dim T0数 As Long
    T0数 = 0
    For idx = 1 To 组数
        If 组买笔(idx) > 0 And 组卖笔(idx) > 0 Then T0数 = T0数 + 1
    Next
    '按实际T0数分配数组
    ReDim ARRTO(1 To T0数 + 3, 1 To 6)
    ARRTO(1, 1) = "日期": ARRTO(1, 2) = "证券代码"
    ARRTO(1, 3) = "证券名称": ARRTO(1, 4) = "买入金额"
    ARRTO(1, 5) = "卖出金额": ARRTO(1, 6) = "总笔数"

    Dim T0买总 As Double, T0卖总 As Double
    T0买总 = 0: T0卖总 = 0
    T0数 = 0
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
    If 计数 > 0 Then ARRTO(T0数 + 3, 2) = Format(T0数 / 计数, "0.000%")
End Sub
'========================================================================================
'========================================================================================
'⑧ 随手单分析
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_P6随手单分析(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    '随手单定义：14:30之前的买入
    Dim 计数 As Long
    计数 = UBound(ARR, 1)
    Dim 随手笔数 As Long: 随手笔数 = 0
    Dim 系统笔数 As Long: 系统笔数 = 0
    Dim 随手金额 As Double: 随手金额 = 0
    Dim 系统金额 As Double: 系统金额 = 0
    Dim 随手赚 As Long: 随手赚 = 0
    Dim 随手亏 As Long: 随手亏 = 0
    Dim 随手总盈亏 As Double: 随手总盈亏 = 0
    Dim 系统总盈亏 As Double: 系统总盈亏 = 0
    '逐笔跟踪
    Dim 随手明细(1 To 1000, 1 To 6) As Variant
    Dim 随手数 As Long: 随手数 = 0
    Dim i As Long, j As Long

    For i = 1 To 计数
        Dim s时间 As String
        s时间 = Trim(ARR(i, 位列割成交时间))
        Dim 小时 As Long, 分钟 As Long, 时间分 As Long
        小时 = Val(Left(s时间, 2))
        分钟 = Val(Mid(s时间, 4, 2))
        时间分 = 小时 * 60 + 分钟
        Dim 类别 As String
        类别 = Trim(ARR(i, 位列割委托类别))
        Dim 金额 As Double
        金额 = Val(ARR(i, 位列割成交金额))
        Dim 代码 As String
        代码 = Trim(ARR(i, 位列割证券代码))
        Dim 名称 As String
        名称 = Trim(ARR(i, 位列割证券名称))

        If 类别 = "买入" Then
            If 时间分 < 870 Then  '14:30 = 14*60+30 = 870
                '随手单
                随手笔数 = 随手笔数 + 1
                随手金额 = 随手金额 + 金额
                随手数 = 随手数 + 1
                随手明细(随手数, 1) = 代码
                随手明细(随手数, 2) = 名称
                随手明细(随手数, 3) = s时间
                随手明细(随手数, 4) = 金额
                '查找后续是否卖出，计算盈亏
                Dim 卖总额 As Double: 卖总额 = 0
                For j = i + 1 To 计数
                    If Trim(ARR(j, 位列割证券代码)) = 代码 And Trim(ARR(j, 位列割委托类别)) = "卖出" Then
                        卖总额 = 卖总额 + Val(ARR(j, 位列割成交金额))
                    End If
                Next
                Dim 盈亏 As Double
                盈亏 = 卖总额 - 金额
                随手明细(随手数, 5) = 盈亏
                If 盈亏 > 0 Then 随手赚 = 随手赚 + 1 Else 随手亏 = 随手亏 + 1
                随手总盈亏 = 随手总盈亏 + 盈亏
            Else
                '14:30后买入 = 系统单
                系统笔数 = 系统笔数 + 1
                系统金额 = 系统金额 + 金额
                '跟踪系统单盈亏
                Dim 卖总额2 As Double: 卖总额2 = 0
                For j = i + 1 To 计数
                    If Trim(ARR(j, 位列割证券代码)) = 代码 And Trim(ARR(j, 位列割委托类别)) = "卖出" Then
                        卖总额2 = 卖总额2 + Val(ARR(j, 位列割成交金额))
                    End If
                Next
                系统总盈亏 = 系统总盈亏 + (卖总额2 - 金额)
            End If
        End If
    Next

    '输出
    ReDim ARRTO(1 To 随手数 + 8, 1 To 6)
    ARRTO(1, 1) = "指标": ARRTO(1, 2) = "数值"
    ARRTO(2, 1) = "随手单笔数(14:30前买入)": ARRTO(2, 2) = 随手笔数
    ARRTO(3, 1) = "系统单笔数(14:30后买入)": ARRTO(3, 2) = 系统笔数
    ARRTO(4, 1) = "随手单金额": ARRTO(4, 2) = Round(随手金额, 0)
    ARRTO(5, 1) = "随手单胜率": ARRTO(5, 2) = IIf(随手笔数 > 0, Format(随手赚 / Application.Max(随手赚 + 随手亏, 1), "0.000%"), "N/A")
    ARRTO(6, 1) = "随手单总盈亏": ARRTO(6, 2) = Round(随手总盈亏, 0)
    ARRTO(7, 1) = "系统单总盈亏": ARRTO(7, 2) = Round(系统总盈亏, 0)
    ARRTO(8, 1) = "随手单vs系统单": ARRTO(8, 2) = IIf(随手笔数 > 0, "随手单" & IIf(随手总盈亏 >= 0, "赚钱", "亏钱") & " " & Round(随手总盈亏, 0) & "元, 系统单" & IIf(系统总盈亏 >= 0, "赚钱", "亏钱") & " " & Round(系统总盈亏, 0) & "元", "无随手单数据")
    '随手单明细（每笔盈亏）
    If 随手数 > 0 Then
        ARRTO(1, 4) = "代码": ARRTO(1, 5) = "名称": ARRTO(1, 6) = "盈亏"
        For i = 1 To 随手数
            ARRTO(i + 8, 1) = 随手明细(i, 1)
            ARRTO(i + 8, 2) = 随手明细(i, 2)
            ARRTO(i + 8, 3) = 随手明细(i, 3)
            ARRTO(i + 8, 4) = 随手明细(i, 4)
            ARRTO(i + 8, 5) = 随手明细(i, 5)
        Next
    End If
End Sub
'========================================================================================
'========================================================================================
'⑨ 月度趋势
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_P7月度趋势(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)
    Dim 月份 As New Dictionary
    Dim i As Long
    For i = 1 To 计数
        Dim vDate As Variant
        vDate = ARR(i, 位列割成交日期)
        Dim 月键 As String
        If IsDate(vDate) Then
            月键 = Format(CDate(vDate), "YYYY-MM")
        Else
            Dim sD As String
            sD = Trim(vDate)
            If Len(sD) >= 6 Then 月键 = Left(sD, 4) & "-" & Mid(sD, 5, 2)
        End If
        If 月键 <> "" Then
            If 月份.Exists(月键) Then
                月份(月键) = 月份(月键) + 1
            Else
                月份.Add 月键, 1
            End If
        End If
    Next
    '排序输出
    Dim 月列表 As Variant
    月列表 = 月份.Keys
    Dim j As Long, k As Long
    For j = 0 To 月份.Count - 2
        For k = j + 1 To 月份.Count - 1
            If 月列表(j) > 月列表(k) Then
                Dim tmpM As String
                tmpM = 月列表(j)
                月列表(j) = 月列表(k)
                月列表(k) = tmpM
            End If
        Next
    Next
    ReDim ARRTO(1 To 月份.Count + 2, 1 To 4)
    ARRTO(1, 1) = "月份": ARRTO(1, 2) = "笔数": ARRTO(1, 3) = "日均"
    For j = 0 To 月份.Count - 1
        月键 = 月列表(j)
        Dim 笔数 As Long
        笔数 = 月份(月键)
        ARRTO(j + 2, 1) = 月键
        ARRTO(j + 2, 2) = 笔数
        '粗略日均：按30天/月估算
        ARRTO(j + 2, 3) = Round(笔数 / 30, 1)
    Next
    ARRTO(月份.Count + 2, 1) = "合计"
    ARRTO(月份.Count + 2, 2) = 计数
End Sub
'========================================================================================
'========================================================================================
'⑩ 活跃股票TOP15
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_P8活跃股票(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)
    Dim 股典 As New Dictionary
    Dim i As Long
    For i = 1 To 计数
        Dim 代码 As String
        代码 = Trim(ARR(i, 位列割证券代码))
        If 代码 <> "" Then
            If 股典.Exists(代码) Then
                股典(代码) = 股典(代码) + 1
            Else
                股典.Add 代码, 1
            End If
        End If
    Next
    '排序找TOP15
    Dim 码列表 As Variant
    码列表 = 股典.Keys
    Dim j As Long, k As Long
    For j = 0 To 股典.Count - 2
        For k = j + 1 To 股典.Count - 1
            If 股典(码列表(j)) < 股典(码列表(k)) Then
                Dim tmpC As String
                tmpC = 码列表(j)
                码列表(j) = 码列表(k)
                码列表(k) = tmpC
            End If
        Next
    Next
    Dim 输出数 As Long
    输出数 = Application.Min(股典.Count, 15)
    ReDim ARRTO(1 To 输出数 + 2, 1 To 4)
    ARRTO(1, 1) = "代码": ARRTO(1, 2) = "名称": ARRTO(1, 3) = "次数"
    For j = 0 To 输出数 - 1
        代码 = 码列表(j)
        ARRTO(j + 2, 1) = 代码
        '查找名称
        Dim 名称 As String
        名称 = ""
        Dim i2 As Long
        For i2 = 1 To 计数
            If Trim(ARR(i2, 位列割证券代码)) = 代码 Then
                名称 = Trim(ARR(i2, 位列割证券名称))
                Exit For
            End If
        Next
        ARRTO(j + 2, 2) = 名称
        ARRTO(j + 2, 3) = 股典(代码)
    Next
    ARRTO(输出数 + 2, 1) = "涉及股票总数"
    ARRTO(输出数 + 2, 2) = 股典.Count
End Sub
'========================================================================================
'========================================================================================
'(11)板块偏好
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_P9板块偏好(ByRef ARR As Variant, ByRef ARRTO As Variant)
'========================================================================================
    Dim 计数 As Long
    计数 = UBound(ARR, 1)
    Dim 板典 As New Dictionary
    Dim 行典 As New Dictionary
    Dim i As Long
    For i = 1 To 计数
        Dim 代码 As String
        代码 = Trim(ARR(i, 位列割证券代码))
        Dim 板块 As String
        If Left(代码, 1) = "6" Then
            板块 = "主板沪"
        ElseIf Left(代码, 3) = "300" Then
            板块 = "创业板"
        ElseIf Left(代码, 3) = "688" Then
            板块 = "科创板"
        ElseIf Left(代码, 1) = "0" Or Left(代码, 1) = "2" Then
            板块 = "主板深"
        ElseIf Left(代码, 1) = "4" Or Left(代码, 1) = "8" Then
            板块 = "北交所"
        Else
            板块 = "其他"
        End If
        If 板典.Exists(板块) Then
            板典(板块) = 板典(板块) + 1
        Else
            板典.Add 板块, 1
        End If
        '行业（从名称判断）
        Dim 名称 As String
        名称 = Trim(ARR(i, 位列割证券名称))
        If InStr(名称, "ETF") > 0 Or InStr(名称, "基金") > 0 Then
            Dim 行业 As String
            行业 = "ETF"
            If 行典.Exists(行业) Then 行典(行业) = 行典(行业) + 1 Else 行典.Add 行业, 1
        End If
    Next
    '输出板块分布
    ReDim ARRTO(1 To 板典.Count + 行典.Count + 3, 1 To 4)
    ARRTO(1, 1) = "板块": ARRTO(1, 2) = "笔数": ARRTO(1, 3) = "占比"
    Dim 行号 As Long
    行号 = 2
    Dim 总笔 As Long
    总笔 = 0
    Dim 板列表 As Variant
    板列表 = 板典.Keys
    Dim j As Long
    For j = 0 To 板典.Count - 1
        ARRTO(行号, 1) = 板列表(j)
        ARRTO(行号, 2) = 板典(板列表(j))
        总笔 = 总笔 + 板典(板列表(j))
        ARRTO(行号, 3) = Format(板典(板列表(j)) / 计数, "0.000%")
        行号 = 行号 + 1
    Next
    ARRTO(行号, 1) = "行业": ARRTO(行号, 2) = "笔数": ARRTO(行号, 3) = "占比"
    行号 = 行号 + 1
    If 行典.Exists("ETF") Then
        ARRTO(行号, 1) = "ETF/基金"
        ARRTO(行号, 2) = 行典("ETF")
        ARRTO(行号, 3) = Format(行典("ETF") / 计数, "0.000%")
    End If
End Sub
'========================================================================================
'========================================================================================
Private Sub 后台辅程割析_输出(ByVal WS As Worksheet, _
    ByRef ARR原始 As Variant, _
    ByRef ARR择时 As Variant, _
    ByRef ARR仓位 As Variant, _
    ByRef ARR成本 As Variant, _
    ByRef ARR盈亏 As Variant, _
    ByRef ARR_T0 As Variant, _
    ByRef ARR随手 As Variant, _
    ByRef ARR月度 As Variant, _
    ByRef ARR活跃 As Variant, _
    ByRef ARR板块 As Variant)
'========================================================================================
    Dim 行号 As Long
    行号 = 1

    '标题（含账户识别）
    Dim 账户名 As String
    账户名 = STCALL割单工具_识别账户(Trim(ARR原始(1, 位列割证券CIDL)))
    WS.Cells(行号, 1) = "交割单深度分析报告"
    WS.Cells(行号, 1).Font.Bold = True
    WS.Cells(行号, 1).Font.Size = 14
    If 账户名 <> "" Then WS.Cells(行号, 2) = "账户: " & 账户名
    行号 = 行号 + 2

    '基础概况
    Dim 计数 As Long
    计数 = UBound(ARR原始, 1)
    Dim 股票数 As Long
    股票数 = UBound(ARR盈亏, 1) - 2

    WS.Cells(行号, 1) = "基础概况"
    WS.Cells(行号, 1).Font.Bold = True
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "总交易笔数": WS.Cells(行号, 2) = 计数
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "涉及股票数": WS.Cells(行号, 2) = 股票数
    行号 = 行号 + 1

    '⑥ 择时
    Call 后台辅程割析_输出段(WS, 行号, "⑥ 择时能力分析", ARR择时)
    行号 = 行号 + UBound(ARR择时, 1) + 2

    '⑦ 仓位
    Call 后台辅程割析_输出段(WS, 行号, "⑦ 仓位管理分析", ARR仓位)
    行号 = 行号 + UBound(ARR仓位, 1) + 2

    '⑤ 成本
    Call 后台辅程割析_输出段(WS, 行号, "⑤ 交易成本分析", ARR成本)
    行号 = 行号 + UBound(ARR成本, 1) + 2
    '费用合计
    Dim 平均佣 As Double, 总佣 As Double, 总印 As Double, 总过 As Double, 总成 As Double
    Dim iRow As Long
    For iRow = 2 To UBound(ARR成本, 1)
        If ARR成本(iRow, 1) = "佣金" Then 总佣 = Val(ARR成本(iRow, 2))
        If ARR成本(iRow, 1) = "印花税" Then 总印 = Val(ARR成本(iRow, 2))
        If ARR成本(iRow, 1) = "过户费" Then 总过 = Val(ARR成本(iRow, 2))
        If ARR成本(iRow, 1) = "总成交金额" Then 总成 = Val(ARR成本(iRow, 2))
    Next
    WS.Cells(行号, 1) = "费用合计": WS.Cells(行号, 1).Font.Bold = True
    WS.Cells(行号, 2) = Round(总佣 + 总印 + 总过, 2)
    If 总成 > 0 Then WS.Cells(行号, 3) = Format((总佣 + 总印 + 总过) / 总成, "0.000%")
    行号 = 行号 + 1

    '① 盈亏
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
    行号 = 行号 + 1

    'ETF vs 个股
    Dim ETF盈亏 As Double, 个股盈亏 As Double
    Dim ETF只数 As Long, 个股只数 As Long
    ETF盈亏 = 0: 个股盈亏 = 0: ETF只数 = 0: 个股只数 = 0
    For iRow = 2 To UBound(ARR盈亏, 1) - 2
        If InStr(ARR盈亏(iRow, 2), "ETF") > 0 Or InStr(ARR盈亏(iRow, 2), "基金") > 0 Then
            ETF盈亏 = ETF盈亏 + Val(ARR盈亏(iRow, 3))
            ETF只数 = ETF只数 + 1
        Else
            个股盈亏 = 个股盈亏 + Val(ARR盈亏(iRow, 3))
            个股只数 = 个股只数 + 1
        End If
    Next
    WS.Cells(行号, 1) = "ETF vs 个股": WS.Cells(行号, 1).Font.Bold = True
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "ETF投资": WS.Cells(行号, 2) = ETF只数 & "只"
    WS.Cells(行号, 3) = "净利润": WS.Cells(行号, 4) = Round(ETF盈亏, 2)
    行号 = 行号 + 1
    WS.Cells(行号, 1) = "个股投资": WS.Cells(行号, 2) = 个股只数 & "只"
    WS.Cells(行号, 3) = "净利润": WS.Cells(行号, 4) = Round(个股盈亏, 2)
    行号 = 行号 + 1

    '③ T+0
    Call 后台辅程割析_输出段(WS, 行号, "③ T+0识别分析", ARR_T0)
    行号 = 行号 + UBound(ARR_T0, 1) + 2

    '⑧ 随手单
    Call 后台辅程割析_输出段(WS, 行号, "⑧ 随手单分析(14:30前买入)", ARR随手)
    行号 = 行号 + UBound(ARR随手, 1) + 2

    '--- 综合结论 ---
    WS.Cells(行号, 1) = "综合结论"
    WS.Cells(行号, 1).Font.Bold = True
    WS.Cells(行号, 1).Font.Size = 14
    行号 = 行号 + 1
    '维度表头
    WS.Cells(行号, 1) = "维度": WS.Cells(行号, 2) = "特征"
    WS.Cells(行号, 1).Font.Bold = True: WS.Cells(行号, 2).Font.Bold = True
    行号 = 行号 + 1
    '① 择时风格
    Dim 尾盘笔 As Double, 总笔 As Double
    尾盘笔 = 0: 总笔 = 0
    For iRow = 2 To UBound(ARR择时, 1)
        If ARR择时(iRow, 1) = "尾盘后段14:30-15:00" Then 尾盘笔 = Val(ARR择时(iRow, 2))
        If ARR择时(iRow, 1) <> "" And VBA.IsNumeric(ARR择时(iRow, 2)) Then 总笔 = 总笔 + Val(ARR择时(iRow, 2))
    Next
    WS.Cells(行号, 1) = "择时风格"
    WS.Cells(行号, 2) = "尾盘密集操作型，偏下午交易，收盘前半小时" & 尾盘笔 & "笔(" & Format(尾盘笔 / 总笔, "0.0%") & ")"
    行号 = 行号 + 1
    '② 仓位风格
    Dim 小微占比 As String, 中位值 As Double
    小微占比 = "": 中位值 = 0
    For iRow = 2 To UBound(ARR仓位, 1)
        If ARR仓位(iRow, 1) = "小微<5千" Then 小微占比 = ARR仓位(iRow, 3)
        If ARR仓位(iRow, 1) = "小1-2万" Then 小微占比 = 小微占比 & "+" & ARR仓位(iRow, 3)
        If ARR仓位(iRow, 1) = "两账号对比" Then
            '中位数在下方两行
            If iRow + 2 <= UBound(ARR仓位, 1) Then 中位值 = Val(ARR仓位(iRow + 2, 5))
        End If
        If ARR仓位(iRow, 1) = 常仓名宝彦 Then 中位值 = Val(ARR仓位(iRow, 5))
        If 中位值 = 0 And ARR仓位(iRow, 1) = 常仓名宝福 Then 中位值 = Val(ARR仓位(iRow, 5))
    Next
    WS.Cells(行号, 1) = "仓位风格"
    WS.Cells(行号, 2) = "分散建仓，小单为主(<2万占" & 小微占比 & ")，中位数" & Round(中位值, 0) & "元"
    行号 = 行号 + 1
    '③ 交易成本
    平均佣 = 0: 总佣 = 0: 总印 = 0: 总过 = 0: 总成 = 0
    For iRow = 2 To UBound(ARR成本, 1)
        If ARR成本(iRow, 1) = "平均佣金率(万分)" Then 平均佣 = ARR成本(iRow, 2)
        If ARR成本(iRow, 1) = "佣金" Then 总佣 = Val(ARR成本(iRow, 2))
        If ARR成本(iRow, 1) = "印花税" Then 总印 = Val(ARR成本(iRow, 2))
        If ARR成本(iRow, 1) = "过户费" Then 总过 = Val(ARR成本(iRow, 2))
        If ARR成本(iRow, 1) = "总成交金额" Then 总成 = Val(ARR成本(iRow, 2))
    Next
    WS.Cells(行号, 1) = "交易成本"
    WS.Cells(行号, 2) = "佣金率中等偏低(" & Round(平均佣, 2) & "万分)，总成本" & Round(总佣 + 总印 + 总过, 0) & "元(" & Format((总佣 + 总印 + 总过) / 总成, "0.000%") & ")"
    行号 = 行号 + 1
    '④ 盈亏表现
    Dim 总利润 As Double
    总利润 = ARR盈亏(汇总行, 3)
    Dim 总收益率 As String
    总收益率 = ARR盈亏(汇总行, 4)
    Dim ETF收率 As String
    ETF收率 = ""
    Dim ETF买额 As Double
    ETF买额 = 0
    For iRow = 2 To UBound(ARR盈亏, 1) - 2
        If InStr(ARR盈亏(iRow, 2), "ETF") > 0 Or InStr(ARR盈亏(iRow, 2), "基金") > 0 Then
            ETF买额 = ETF买额 + Val(ARR盈亏(iRow, 7))
        End If
    Next
    If ETF买额 > 0 Then ETF收率 = "，ETF亏" & Format(ETF盈亏 / ETF买额, "0.00%")
    WS.Cells(行号, 1) = "盈亏表现"
    WS.Cells(行号, 2) = Round(总利润 / 10000, 1) & "万(" & 总收益率 & ")"
    If 个股只数 > 0 Then WS.Cells(行号, 2) = WS.Cells(行号, 2) & "，个股基本持平" & ETF收率
    行号 = 行号 + 1
    '⑤ 交易模式
    Dim T0比 As String
    T0比 = ""
    For iRow = 2 To UBound(ARR_T0, 1)
        If ARR_T0(iRow, 1) = "占全部交易" Then T0比 = ARR_T0(iRow, 2)
    Next
    WS.Cells(行号, 1) = "交易模式"
    WS.Cells(行号, 2) = "轻度做T(" & T0比 & ")，主要做T标的为ETF"
    行号 = 行号 + 1
    '⑥ 最大亏损源头 TOP3
    Dim 亏1 As String, 亏2 As String, 亏3 As String
    亏1 = "": 亏2 = "": 亏3 = ""
    Dim 亏计数 As Long: 亏计数 = 0
    For iRow = 2 To UBound(ARR盈亏, 1) - 2
        If Val(ARR盈亏(iRow, 3)) < 0 Then
            亏计数 = 亏计数 + 1
            Dim 亏文本 As String
            亏文本 = ARR盈亏(iRow, 2) & "(" & Round(Val(ARR盈亏(iRow, 3)) / 10000, 1) & "万)"
            If 亏计数 = 1 Then 亏1 = 亏文本
            If 亏计数 = 2 Then 亏2 = 亏文本
            If 亏计数 = 3 Then 亏3 = 亏文本: Exit For
        End If
    Next
    WS.Cells(行号, 1) = "最大亏损源头"
    WS.Cells(行号, 2) = 亏1 & "、" & 亏2 & "、" & 亏3
    行号 = 行号 + 2

    '⑨ 月度趋势
    Call 后台辅程割析_输出段(WS, 行号, "⑨ 月度交易量趋势", ARR月度)
    行号 = 行号 + UBound(ARR月度, 1) + 2

    '⑩ 活跃股票
    Call 后台辅程割析_输出段(WS, 行号, "⑩ 最活跃股票 TOP15", ARR活跃)
    行号 = 行号 + UBound(ARR活跃, 1) + 2

    '(11)板块偏好
    Call 后台辅程割析_输出段(WS, 行号, "(11)板块偏好分布", ARR板块)
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
'========================================================================================
' 持仓校准交割单 — 以当前持仓为基准，反向递推分离不完整交易
' 数据源：花册（当前持仓）+ 华宝交割单 XLS
' 算法：从最新交易倒推，持仓配不上的部分单独拎出
'========================================================================================
Public Sub STCALL割册管理_XLS交割单G1校准()
    Dim FILEOPEN As Variant
    FILEOPEN = Application.GetOpenFilename("华宝交割单信息,*.xls", , "选择交割单 XLS", , False)
    If FILEOPEN = False Then Exit Sub
    UTL宏工具_BEGIN
    ' ① 读取花册当前持仓
    Dim WS花 As Worksheet
    If STBASE外簿工具_花册链接(WS花, 常花中股) = False Then
        MsgBox "花册链接失败", vbCritical: Exit Sub
    End If
    Dim 末行 As Long
    末行 = WS花.Cells(65536, 1).End(xlUp).Row
    Dim 典集持仓 As Object
    Set 典集持仓 = CreateObject("Scripting.Dictionary")
    Dim R As Long
    For R = 2 To 末行
        Dim CIDL As String
        CIDL = Trim(WS花.Cells(R, 位列花天CIDL).Value)
        Dim 仓值 As String
        仓值 = Trim(WS花.Cells(R, 位列花天仓宝彦).Value)
        If CIDL <> "" And 仓值 <> "" Then
            Dim 逗号位 As Integer
            逗号位 = InStr(仓值, ",")
            If 逗号位 > 0 Then
                Dim 持仓量 As Double
                持仓量 = Val(Left$(仓值, 逗号位 - 1))
                If 持仓量 > 0 Then 典集持仓.Add Key:=CIDL, Item:=持仓量
            End If
        End If
    Next
    Set WS花 = Nothing
    ' ② 读取交割单
    Application.Calculation = xlCalculationAutomatic
    Dim WB割 As Workbook
    Set WB割 = GetObject(FILEOPEN)
    WB割.Application.Calculate
    Dim ARRYM As Variant
    With WB割.ActiveSheet
        ARRYM = .Range("A1").CurrentRegion
    End With
    WB割.Close False
    Set WB割 = Nothing
    ' ③ 构建输出表
    Dim WS出 As Worksheet
    Call PBASE格程工具_表操工表新增(WS出, "割校准" & 后台辅程_账户后缀(ARRYM, 2), 基色底:=常色十蓝)
    WS出.Cells(1, 1) = "证券代码"
    ReDim 割单数组(1 To 5000, 1 To 常割单列数)
    割单行数 = 0: WS出.Cells(1, 2) = "证券名称"
    WS出.Cells(1, 3) = "当前持仓": WS出.Cells(1, 4) = "日期"
    WS出.Cells(1, 5) = "委托类别": WS出.Cells(1, 6) = "成交数量"
    WS出.Cells(1, 7) = "成交金额": WS出.Cells(1, 8) = "状态"
    WS出.Rows(1).Font.Bold = True
    Dim 行号 As Long: 行号 = 2
    Dim 总完整 As Long: 总完整 = 0
    Dim 总不完整 As Long: 总不完整 = 0
    Dim 未配对行() As Long, 未配对计数 As Long, upi As Long, upr As Long
    ReDim 未配对行(1 To 5000)
    ' ④ 按股票分组处理
    Dim 总行 As Long: 总行 = UBound(ARRYM, 1)
    Dim 已处理 As Object
    Set 已处理 = CreateObject("Scripting.Dictionary")
    Dim i As Long, j As Long
    For i = 2 To 总行
        ' 清理委托类别
        Dim 类别 As String
        类别 = ARRYM(i, 6)
        If VarType(类别) = vbString Then
            类别 = Replace(类别, "=", "")
            类别 = Replace(类别, """", "")
        End If
        If 类别 <> "买入" And 类别 <> "卖出" Then
            ' 非交易类行，直接加入割单数组
            割单行数 = 割单行数 + 1
            Dim ac_other As Long
            For ac_other = 1 To 15: 割单数组(割单行数, ac_other) = ARRYM(i, ac_other): Next
            割单数组(割单行数, 6) = 类别
            割单数组(割单行数, 常割单列状态) = "其他"
            割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(i, 3))
            GoTo 跳过
        End If
        ' 清理股票代码
        Dim sCIDL As String, sCIDV As Variant
        sCIDV = ARRYM(i, 4)
        If VarType(sCIDV) = vbString Then
            sCIDV = Replace(sCIDV, "=", "")
            sCIDV = Replace(sCIDV, """", "")
        End If
        sCIDL = UBCID规制代码(sCIDV)
        If sCIDL = "" Then GoTo 跳过
        If 已处理.Exists(sCIDL) Then GoTo 跳过
        已处理.Add sCIDL, True
        ' 收集该股票所有交易
        Dim 交易行() As Long
        Dim 计数 As Long: 计数 = 0
        Dim 交易索引 As Long
        For j = 2 To 总行
            Dim jCIDL As String, jCIDV2 As Variant
            jCIDV2 = ARRYM(j, 4)
            If VarType(jCIDV2) = vbString Then
                jCIDV2 = Replace(jCIDV2, "=", "")
                jCIDV2 = Replace(jCIDV2, """", "")
            End If
            jCIDL = UBCID规制代码(jCIDV2)
            If jCIDL = sCIDL Then
                Dim j类别 As String
                j类别 = ARRYM(j, 6)
                If VarType(j类别) = vbString Then
                    j类别 = Replace(j类别, "=", "")
                    j类别 = Replace(j类别, """", "")
                End If
                If j类别 = "买入" Or j类别 = "卖出" Then
                    计数 = 计数 + 1
                    ReDim Preserve 交易行(1 To 计数)
                    交易行(计数) = j
                End If
            End If
        Next
        If 计数 = 0 Then GoTo 跳过
        ' 当前持仓
        If 典集持仓.Exists(sCIDL) Then 持仓量 = 典集持仓(sCIDL) Else 持仓量 = 0
        ' 计算净余和持仓量
        Dim 净余 As Double, qty As Double, 类别r As String, 标记 As String
        净余 = 0
        For 交易索引 = 1 To 计数
            R = 交易行(交易索引)
            qty = Val(ARRYM(R, 8))
            类别r = ARRYM(R, 6)
            If VarType(类别r) = vbString Then
                类别r = Replace(类别r, "=", "")
                类别r = Replace(类别r, """", "")
            End If
            If 类别r = "买入" Then 净余 = 净余 + qty Else 净余 = 净余 - qty
        Next
        Dim 老仓 As Double
        老仓 = 持仓量 - 净余
        ' 输出该股票结果
        Dim 名称 As String
        名称 = Trim(ARRYM(交易行(1), 5))
        WS出.Cells(行号, 1) = sCIDL
        WS出.Cells(行号, 2) = 名称
        WS出.Cells(行号, 3) = 持仓量
        WS出.Cells(行号, 4) = "---"
        WS出.Cells(行号, 5) = "---"
        WS出.Cells(行号, 6) = "---"
        WS出.Cells(行号, 7) = "---"
        WS出.Cells(行号, 8) = "汇总"
        WS出.Rows(行号).Font.Bold = True
        行号 = 行号 + 1
        总完整 = 总完整 + 1
        ' 从最旧到最新遍历，标记未配对交易
        Dim 待中和 As Double
        待中和 = 老仓
        For 交易索引 = 1 To 计数
            R = 交易行(交易索引)
            qty = Val(ARRYM(R, 8))
            类别r = ARRYM(R, 6)
            If VarType(类别r) = vbString Then
                类别r = Replace(类别r, "=", "")
                类别r = Replace(类别r, """", "")
            End If
            ' 决定标记
            If 待中和 > 0 And 类别r = "卖出" Then
                ' 卖出是在平老仓
                If qty <= 待中和 Then
                    标记 = "未配对交易"
                    待中和 = 待中和 - qty
                Else
                    ' 拆分卖出：待中和(未配对) + 剩余(配对)
                    ' 先输出未配对部分
                    WS出.Cells(行号, 3) = ""
                    WS出.Cells(行号, 4) = ARRYM(R, 1)
                    WS出.Cells(行号, 5) = 类别r
                    WS出.Cells(行号, 6) = 待中和
                    WS出.Cells(行号, 7) = Val(ARRYM(R, 9)) * 待中和 / qty
                    WS出.Cells(行号, 8) = "未配对交易"
                    WS出.Rows(行号).Interior.Color = 常色十红
                    割单行数 = 割单行数 + 1
                    Dim ac_s As Long
                    For ac_s = 1 To 15: 割单数组(割单行数, ac_s) = ARRYM(R, ac_s): Next
                    割单数组(割单行数, 6) = 类别r
                    割单数组(割单行数, 8) = 待中和
                    割单数组(割单行数, 9) = Val(ARRYM(R, 9)) * 待中和 / qty
                    割单数组(割单行数, 常割单列状态) = "未配对交易"
                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(R, 3))
                    未配对计数 = 未配对计数 + 1
                    未配对行(未配对计数) = 割单行数
                    总不完整 = 总不完整 + 1
                    行号 = 行号 + 1
                    ' 输出配对部分
                    WS出.Cells(行号, 3) = ""
                    WS出.Cells(行号, 4) = ARRYM(R, 1)
                    WS出.Cells(行号, 5) = 类别r
                    WS出.Cells(行号, 6) = qty - 待中和
                    WS出.Cells(行号, 7) = Val(ARRYM(R, 9)) * (qty - 待中和) / qty
                    WS出.Cells(行号, 8) = "配对交易"
                    割单行数 = 割单行数 + 1
                    For ac_s = 1 To 15: 割单数组(割单行数, ac_s) = ARRYM(R, ac_s): Next
                    割单数组(割单行数, 6) = 类别r
                    割单数组(割单行数, 8) = qty - 待中和
                    割单数组(割单行数, 9) = Val(ARRYM(R, 9)) * (qty - 待中和) / qty
                    割单数组(割单行数, 常割单列状态) = "配对交易"
                    割单数组(割单行数, 常割单列配对类型) = "历史买卖配对"
                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(R, 3))
                    行号 = 行号 + 1
                    待中和 = 0
                    GoTo 下一交易
                End If
            ElseIf 待中和 < 0 And 类别r = "买入" Then
                ' 买入是在填补缺口
                If qty <= -待中和 Then
                    标记 = "未配对交易"
                    待中和 = 待中和 + qty
                Else
                    ' 拆分买入
                    WS出.Cells(行号, 3) = ""
                    WS出.Cells(行号, 4) = ARRYM(R, 1)
                    WS出.Cells(行号, 5) = 类别r
                    WS出.Cells(行号, 6) = -待中和
                    WS出.Cells(行号, 7) = Val(ARRYM(R, 9)) * (-待中和) / qty
                    WS出.Cells(行号, 8) = "未配对交易"
                    WS出.Rows(行号).Interior.Color = 常色十红
                    割单行数 = 割单行数 + 1
                    Dim ac_b As Long
                    For ac_b = 1 To 15: 割单数组(割单行数, ac_b) = ARRYM(R, ac_b): Next
                    割单数组(割单行数, 6) = 类别r
                    割单数组(割单行数, 8) = -待中和
                    割单数组(割单行数, 9) = Val(ARRYM(R, 9)) * (-待中和) / qty
                    割单数组(割单行数, 常割单列状态) = "未配对交易"
                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(R, 3))
                    未配对计数 = 未配对计数 + 1
                    未配对行(未配对计数) = 割单行数
                    总不完整 = 总不完整 + 1
                    行号 = 行号 + 1
                    ' 输出配对部分
                    WS出.Cells(行号, 3) = ""
                    WS出.Cells(行号, 4) = ARRYM(R, 1)
                    WS出.Cells(行号, 5) = 类别r
                    WS出.Cells(行号, 6) = qty + 待中和
                    WS出.Cells(行号, 7) = Val(ARRYM(R, 9)) * (qty + 待中和) / qty
                    WS出.Cells(行号, 8) = "配对交易"
                    割单行数 = 割单行数 + 1
                    For ac_b = 1 To 15: 割单数组(割单行数, ac_b) = ARRYM(R, ac_b): Next
                    割单数组(割单行数, 6) = 类别r
                    割单数组(割单行数, 8) = qty + 待中和
                    割单数组(割单行数, 9) = Val(ARRYM(R, 9)) * (qty + 待中和) / qty
                    割单数组(割单行数, 常割单列状态) = "配对交易"
                    割单数组(割单行数, 常割单列配对类型) = "历史买卖配对"
                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(R, 3))
                    行号 = 行号 + 1
                    待中和 = 0
                    GoTo 下一交易
                End If
            Else
                标记 = "配对交易"
            End If
            ' 输出交易
            WS出.Cells(行号, 3) = ""
            WS出.Cells(行号, 4) = ARRYM(R, 1)
            WS出.Cells(行号, 5) = 类别r
            WS出.Cells(行号, 6) = qty
            WS出.Cells(行号, 7) = Val(ARRYM(R, 9))
            WS出.Cells(行号, 8) = 标记
            If 标记 = "未配对交易" Then
                WS出.Rows(行号).Interior.Color = 常色十红
                总不完整 = 总不完整 + 1
            End If
            割单行数 = 割单行数 + 1
            Dim ac As Long
            For ac = 1 To 15: 割单数组(割单行数, ac) = ARRYM(R, ac): Next
            割单数组(割单行数, 6) = 类别r
            割单数组(割单行数, 8) = qty
            割单数组(割单行数, 9) = Val(ARRYM(R, 9))
            割单数组(割单行数, 常割单列状态) = 标记
            If 标记 = "未配对交易" Then
                未配对计数 = 未配对计数 + 1
                未配对行(未配对计数) = 割单行数
            Else
                割单数组(割单行数, 常割单列配对类型) = "历史买卖配对"
            End If
            割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(R, 3))
            行号 = 行号 + 1
下一交易:
        Next
跳过:
    Next
    ' ⑤ 输出未配对交易（第二段）
    If 未配对计数 > 0 Then
        WS出.Cells(行号, 1) = "=== 未配对交易 ==="
        WS出.Rows(行号).Font.Bold = True
        WS出.Rows(行号).Font.Color = 常色十红
        行号 = 行号 + 1
        For upi = 1 To 未配对计数
            upr = 未配对行(upi)
            WS出.Cells(行号, 1) = 割单数组(upr, 4)
            WS出.Cells(行号, 2) = 割单数组(upr, 5)
            WS出.Cells(行号, 3) = ""
            WS出.Cells(行号, 4) = 割单数组(upr, 1)
            WS出.Cells(行号, 5) = 割单数组(upr, 6)
            WS出.Cells(行号, 6) = 割单数组(upr, 8)
            WS出.Cells(行号, 7) = 割单数组(upr, 9)
            WS出.Cells(行号, 8) = "未配对交易"
            WS出.Rows(行号).Interior.Color = 常色十红
            行号 = 行号 + 1
        Next
    End If
    ' ⑥ 格式化
    WS出.Columns("A:H").AutoFit
    WS出.Cells(2, 1).Activate
    Call PBASE格程工具_表冻结锁定(WS出, 基行:=1, 基列:=2)
    MsgBox "割校准完成" & vbCrLf & _
           "完整交易: " & 总完整 & " 只" & vbCrLf & _
           "不完整交易: " & 总不完整 & " 笔", vbInformation, "割校准"
    UTL宏工具_END
End Sub
'========================================================================================
' 割单工具_识别账户 — 根据股东代码返回账户名
'========================================================================================
Public Function STCALL割单工具_识别账户(ByVal 股东代码 As String) As String
    Select Case 股东代码
    Case 常股代宝彦_上证, 常股代宝彦_深证: STCALL割单工具_识别账户 = 常仓名宝彦
    Case 常股代宝福_上证, 常股代宝福_深证: STCALL割单工具_识别账户 = 常仓名宝福
    Case Else: STCALL割单工具_识别账户 = ""
    End Select
End Function
'========================================================================================
' 获取账户后缀（用于Sheet命名）
'========================================================================================
Private Function 后台辅程_账户后缀(ByRef ARR As Variant, Optional ByVal 行号 As Long = 1) As String
    Dim 账名 As String
    On Error Resume Next
    '先试第18列（常割单列账户，G1校准已写入账号）
    账名 = Trim(ARR(行号, 常割单列账户))
    If 账名 = "" Then
        '再试第3列（股东代码）
        账名 = STCALL割单工具_识别账户(Trim(ARR(行号, 位列割证券CIDL)))
    End If
    If 账名 = "" And 行号 < 10 Then
        Dim i As Long
        For i = 行号 + 1 To 10
            账名 = Trim(ARR(i, 常割单列账户))
            If 账名 = "" Then 账名 = STCALL割单工具_识别账户(Trim(ARR(i, 位列割证券CIDL)))
            If 账名 <> "" Then Exit For
        Next
    End If
    On Error GoTo 0
    If 账名 <> "" Then 后台辅程_账户后缀 = 账名 Else 后台辅程_账户后缀 = ""
End Function
'========================================================================================
' 割册管理_交割单总流程 — 三步串联
'========================================================================================
Public Sub STCALL割册管理_XLS交割单G0总流程()
    UTL宏工具_BEGIN
    Call STCALL割册管理_XLS交割单G1校准
    Call STCALL割册管理_XLS交割单G2导入
    Call STCALL割册管理_XLS交割单G3解析
    UTL宏工具_END
    MsgBox "交割单分析完成", vbInformation
End Sub
'========================================================================================
' 验证Name — 检查所有资金汇总 Name 是否存在并显示值
'========================================================================================
