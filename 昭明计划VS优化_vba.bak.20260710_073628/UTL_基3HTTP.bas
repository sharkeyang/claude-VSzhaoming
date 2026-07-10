Attribute VB_Name = "UTL_基3HTTP"
Option Explicit
Public Const 常查询代码中股 = "sh000001"
Public Const 常查询代码港股 = "r_hk00384"
Public Const 常查询代码美股 = "s_usGOOG"
Public Const 常HTTP批大小 = 500   '腾讯/新浪批量查询每组代码数
'========================================================================================
'腾讯历史行情数组（从0开始）每行数据
Public Const 位序腾历下限 = 0
'-----------------------------
Public Const 位序腾历今日 = 0
Public Const 位序腾历今开 = 1
Public Const 位序腾历今收 = 2
Public Const 位序腾历今高 = 3
Public Const 位序腾历今低 = 4
Public Const 位序腾历今量 = 5
'-----------------------------
Public Const 位序腾历上限 = 5
'========================================================================================
'腾讯实时行情数组（从0开始）
Public Const 位序腾实市场 = 0
Public Const 位序腾实代称 = 1
Public Const 位序腾实代码 = 2
Public Const 位序腾实今收 = 3
Public Const 位序腾实前收 = 4
Public Const 位序腾实今开 = 5
Public Const 位序腾实交量 = 6
Public Const 位序腾实外盘 = 7
Public Const 位序腾实内盘 = 8
Public Const 位序腾实买一价 = 9
Public Const 位序腾实买一量 = 10
Public Const 位序腾实买二价 = 11
Public Const 位序腾实买二量 = 12
Public Const 位序腾实买三价 = 13
Public Const 位序腾实买三量 = 14
Public Const 位序腾实买四价 = 15
Public Const 位序腾实买四量 = 16
Public Const 位序腾实买五价 = 17
Public Const 位序腾实买五量 = 18
Public Const 位序腾实卖一价 = 19
Public Const 位序腾实卖一量 = 20
Public Const 位序腾实卖二价 = 21
Public Const 位序腾实卖二量 = 22
Public Const 位序腾实卖三价 = 23
Public Const 位序腾实卖三量 = 24
Public Const 位序腾实卖四价 = 25
Public Const 位序腾实卖四量 = 26
Public Const 位序腾实卖五价 = 27
Public Const 位序腾实卖五量 = 28
Public Const 位序腾实逐笔成交 = 29
Public Const 位序腾实时间 = 30
Public Const 位序腾实涨跌 = 31
Public Const 位序腾实今涨 = 32
Public Const 位序腾实今高 = 33
Public Const 位序腾实今低 = 34
Public Const 位序腾实价量额 = 35
Public Const 位序腾实成交量 = 36
Public Const 位序腾实交额 = 37
Public Const 位序腾实市盈静态 = 39
Public Const 位序腾实停牌 = 40
Public Const 位序腾实今高2 = 41
Public Const 位序腾实今低2 = 42
Public Const 位序腾实振幅 = 43
Public Const 位序腾实流市 = 44
Public Const 位序腾实总市 = 45
'-----------------------------
Public Const 位序腾实A换手 = 38
Public Const 位序腾实A市净 = 46
Public Const 位序腾实A涨停 = 47
Public Const 位序腾实A跌停 = 48
Public Const 位序腾实A量比 = 49
Public Const 位序腾实A盘差 = 50
Public Const 位序腾实A均价 = 51
Public Const 位序腾实A市盈动态 = 52
'-----------------------------
Public Const 位序腾实H名称英文 = 46
Public Const 位序腾实H股息率TTM = 47
Public Const 位序腾实H最高52周 = 48
Public Const 位序腾实H最低52周 = 49
Public Const 位序腾实H量比 = 50
Public Const 位序腾实H委比 = 51
Public Const 位序腾实H市盈TTM = 57
Public Const 位序腾实H市净 = 58
Public Const 位序腾实H换手 = 59
Public Const 位序腾实H每首股数 = 60
'========================================================================================





Private Sub 测试_UBHTTP通用_查程测试()
'     Debug.Print GetHttp("http://hq.sinajs.cn/list=sh000001")
'     Debug.Print UBHTTP通用_查程回全通用("http://quotes.money.163.com/trade/lsjysj_601318.html?year=2022&season=2")
'    Debug.Print UBHTTP通用_查程回全通用("http://quote.eastmoney.com/concept/sh603777.html?from=classic")
'     Debug.Print UBHTTP通用_查程回全通用("http://qt.gtimg.cn/q=sh688128")
     Debug.Print UBHTTP通用_查程回全通用("http://qt.gtimg.cn/q=sh000001")
     Debug.Print UBHTTP通用_查程回全通用("http://qt.gtimg.cn/q=sh688538")
'     Debug.Print UBHTTP通用_查程回全通用("http://qt.gtimg.cn/q=r_hk00700")
End Sub

Private Sub 测试_UBHTTP腾实_对比批量vs逐只()
    Dim 测试码 As Variant, 码 As Variant, i As Long, J As Long
    Dim aRESP As Variant, nRESP As Integer
    Dim 查回典 As Dictionary, 段组 As Variant
    Dim 代码串 As String, 差异数 As Long

    ' 测试代码：覆盖A股沪、A股深、港股、美股
    测试码 = Array("sh000001", "sh600703", "sz002129", "sh601988", "r_hk00700")

    '====================================================================
    ' 第一轮：逐只查询
    '====================================================================
    Debug.Print "========== 逐只查询 =========="
    Dim 逐只结果 As New Dictionary
    For Each 码 In 测试码
        nRESP = UBHTTP腾实_查回组(aRESP, 码)
        If nRESP > 0 Then
            逐只结果(码) = aRESP
            Debug.Print 码, "OK, 字段数=" & nRESP, "前3字段: " & aRESP(0) & " | " & aRESP(1) & " | " & aRESP(2)
        Else
            逐只结果.Add 码, Empty
            Debug.Print 码, "FAIL"
        End If
    Next

    '====================================================================
    ' 第二轮：批量查询
    '====================================================================
    Debug.Print vbCrLf & "========== 批量查询 =========="
    代码串 = Join(测试码, ",")
    Debug.Print "URL码串: " & 代码串

    Set 查回典 = UBHTTP腾实_查回典批量(代码串)
    Debug.Print "返回条目数: " & 查回典.Count

    For Each 码 In 测试码
        If 查回典.Exists(码) Then
            段组 = 查回典(码)
            Debug.Print 码, "OK, 字段数=" & (UBound(段组) + 1), "前3字段: " & 段组(0) & " | " & 段组(1) & " | " & 段组(2)
        Else
            Debug.Print 码, "NOT FOUND in batch result"
        End If
    Next

    '====================================================================
    ' 第三轮：逐字段对比
    '====================================================================
    Debug.Print vbCrLf & "========== 字段对比 =========="
    差异数 = 0
    For Each 码 In 测试码
        If 逐只结果.Exists(码) And 查回典.Exists(码) Then
            If Not IsEmpty(逐只结果(码)) Then
                aRESP = 逐只结果(码)
                段组 = 查回典(码)
                Dim 差异字段 As String: 差异字段 = ""
                For i = 0 To Application.Max(UBound(aRESP), UBound(段组))
                    Dim v1 As String, v2 As String
                    v1 = "": v2 = ""
                    If i <= UBound(aRESP) Then v1 = aRESP(i)
                    If i <= UBound(段组) Then v2 = 段组(i)
                    If v1 <> v2 Then
                        差异字段 = 差异字段 & " [" & i & "]旧=" & v1 & " 新=" & v2
                    End If
                Next
                If Len(差异字段) > 0 Then
                    差异数 = 差异数 + 1
                    Debug.Print "? " & 码 & 差异字段
                Else
                    Debug.Print "? " & 码 & " 完全一致"
                End If
            End If
        End If
    Next

    Debug.Print vbCrLf & "总差异: " & 差异数
    If 差异数 = 0 Then Debug.Print ">>> 批量查询与逐只查询结果完全一致 <<<"
End Sub

Private Sub 测试_UBHTTP腾实_压测批量百码()
    Dim 代码串 As String, 码数组 As Variant, i As Long
    Dim 查回典 As Dictionary

    Dim WS花天 As Worksheet
    If STBASE外簿工具_花册链接(WS花天, 常花中股) = False Then
        Debug.Print "无法链接花天"
        Exit Sub
    End If

    Dim 末行 As Long
    末行 = WS花天.[a65536].End(xlUp).Row
    If 末行 > 101 Then 末行 = 101
    If 末行 < 2 Then
        Debug.Print "花天无数据"
        Exit Sub
    End If

    ReDim 码数组(1 To 末行 - 1) As String
    For i = 2 To 末行
        码数组(i - 1) = WS花天.Cells(i, 1).Value
    Next

    代码串 = Join(码数组, ",")
    Debug.Print "========== 批量压测 =========="
    Debug.Print "代码数: " & (末行 - 1)
    Debug.Print "URL长度: " & Len("http://qt.gtimg.cn/q=" & 代码串)

    Dim TT As Double
    TT = Timer
    Set 查回典 = UBHTTP腾实_查回典批量(代码串)
    Dim 耗时 As Double
    耗时 = Timer - TT

    Debug.Print "返回条目: " & 查回典.Count
    Debug.Print "耗时(秒): " & Format(耗时, "0.00")
    Debug.Print "命中率: " & Format(查回典.Count / (末行 - 1), "0.0%")

    Debug.Print vbCrLf & "--- 前5条抽样 ---"
    Dim 码 As Variant, 段组 As Variant
    i = 0
    For Each 码 In 码数组
        If 查回典.Exists(码) Then
            i = i + 1
            段组 = 查回典(码)
            Debug.Print 码, 段组(1), 段组(3)
            If i >= 50 Then Exit For
        End If
    Next
End Sub





'########################################################################################
'########################################################################################
'#####################################    HTTP基础  ######################################
'########################################################################################
'########################################################################################
'========================================================================================
'========================================================================================
'质程：查询URL并初加工
'========================================================================================
'========================================================================================
Function UBHTTP通用_查程回引(sURL As String, Optional 试错阈值 As Long = 1999) As String
    '------------------------------------------------------------------------------------
    Dim sResponseText As String
    sResponseText = UBHTTP通用_查程回全通用(sURL)
    '------------------------------------------------------------------------------------
    Dim iStt As Integer
    Dim iEnd As Integer
    iStt = InStr(sResponseText, """")
    iEnd = InStrRev(sResponseText, """")
        
    If iEnd > iStt Then
        UBHTTP通用_查程回引 = Mid$(sResponseText, iStt + 1, iEnd - iStt - 1)
    Else
        UBHTTP通用_查程回引 = sResponseText
    End If
    '------------------------------------------------------------------------------------
End Function
'========================================================================================
'质程：查询URL
'注意：区分是否为新浪接口
'========================================================================================
Function UBHTTP通用_查程回全通用(sURL As String, Optional 试错阈值 As Integer = 1999) As String
    Dim sResponseText As String
    If InStr(sURL, "sina") <> 0 Then
        sResponseText = UBHTTP通用_查程回全新浪(sURL)
    Else
        sResponseText = UBHTTP通用_查程回全腾讯(sURL, 试错阈值)
    End If
    UBHTTP通用_查程回全通用 = sResponseText
End Function
'========================================================================================
'查询接口：新浪
'========================================================================================
Private Function UBHTTP通用_查程回全新浪(sURL As String) As String
    Dim sResponseText As String
    With CreateObject("WinHttp.WinHttpRequest.5.1")
        .Open "GET", sURL, False
        .setRequestHeader "Referer", "http://vip.stock.finance.sina.com.cn/"
        .send
        sResponseText = .responseText
    End With
    UBHTTP通用_查程回全新浪 = sResponseText
End Function
'========================================================================================
'查询接口：腾讯
'========================================================================================
Private Function UBHTTP通用_查程回全腾讯(sURL As String, Optional 试错阈值 As Integer = 1999) As String
    Dim sResponseText As String
    Dim XMLHTTP As New MSXML2.ServerXMLHTTP60

    XMLHTTP.setTimeouts 3000, 5000, 5000, 10000
    XMLHTTP.Open "GET", sURL, False  ' 同步模式，避免 readyState 卡在 1

    On Error Resume Next
    XMLHTTP.send
    On Error GoTo 0

    If XMLHTTP.Status = 200 Then
        On Error Resume Next
        sResponseText = XMLHTTP.responseText
        On Error GoTo 0
        UBHTTP通用_查程回全腾讯 = sResponseText
    Else
        Debug.Print sURL, "Status="; XMLHTTP.Status; "readyState="; XMLHTTP.readyState
    End If

    Set XMLHTTP = Nothing
End Function
'########################################################################################
'########################################################################################
'#####################################    HTTP基础  ######################################
'########################################################################################
'########################################################################################




'########################################################################################
'########################################################################################
'#####################################    是否断网     ###################################
'########################################################################################
'########################################################################################
'========================================================================================
'查询行情：腾讯实时 是否断网
'========================================================================================
Function UBHTTP腾实_查是否断网(Optional CIDL As String = 常查询代码中股) As Boolean
    Dim sURL As String
    sURL = "http://qt.gtimg.cn/q=" & CIDL
    UBHTTP腾实_查是否断网 = (Len(UBHTTP通用_查程回全腾讯(sURL, 试错阈值:=50)) < 10)
End Function
'========================================================================================
'查询行情：腾讯历史 是否断网
'========================================================================================
Function UBHTTP腾历_查是否断网(Optional CIDL As String = 常查询代码中股) As Boolean
    Dim sRESP As String
    sRESP = UBHTTP腾历_查回引(CIDL)
    UBHTTP腾历_查是否断网 = (Len(sRESP) < 2)
End Function
'########################################################################################
'########################################################################################
'#####################################    是否断网     ###################################
'########################################################################################
'########################################################################################




'Function GetHttp(Url)
'    Dim xmlobject
'    On Error Resume Next
'    Set xmlobject = CreateObject("WinHttp.WinHttpRequest.5.1")
'    xmlobject.Open "GET", Url, False
'    xmlobject.setRequestHeader "Referer", "http://vip.stock.finance.sina.com.cn/"
'    xmlobject.send
'    GetHttp = xmlobject.responseBody
'    GetHttp = BytesToBstr(GetHttp, "GB2312")
'    Set objXML = Nothing
'    On Error GoTo 0
'End Function




Private Sub 测试_UBHTTP_RESPONSETEXT()
    Dim sURL As String
    Dim sSEP As String
    sURL = "http://finance.sina.com.cn/realstock/company/hotstock_daily_a.js"
    sSEP = ","
    sURL = "http://qt.gtimg.cn/q=sh000001"
    'Debug.Print UBHTTP通用_查程回引(sURL)

'    Debug.Print UBHTTP腾实_查回引("sh000005")
    Dim aRESP As Variant
    Debug.Print UBHTTP腾实_查回组(aRESP, "sh000005")
'    Debug.Print STBASE取据引擎查时戳由腾实("sh000005")
'    Debug.Print UBHTTP腾实_查是否断网
'    For I = LBound(aRESP) To UBound(aRESP)
'        Debug.Print I, aRESP(I)
'    Next
   ' Debug.Print UBHTTP通用_查程回全("https://api.coinmarketcap.com/v2/ticker/")
End Sub



Private Sub 测试_对比批量vs逐只_at花天全码()
    Const 测试码数上限 As Integer = 5000

    Dim WS花天 As Worksheet
    If STBASE外簿工具_花册链接(WS花天, 常花中股) = False Then
        Debug.Print "无法链接花天": Exit Sub
    End If

    Dim 末行 As Long, i As Long, 码 As String
    末行 = WS花天.[a65536].End(xlUp).Row

    Dim 码列表() As String, 码数 As Long: 码数 = 0
    ReDim 码列表(1 To 末行)
    For i = 2 To 末行
        码 = WS花天.Cells(i, 1).Value
        If 码 Like "sh*" Or 码 Like "sz*" Then
            码数 = 码数 + 1
            码列表(码数) = 码
            If 码数 >= 测试码数上限 Then Exit For
        End If
    Next
    If 码数 = 0 Then Debug.Print "无代码": Exit Sub
    ReDim Preserve 码列表(1 To 码数)

    Debug.Print "========== 批量vs逐只 全对比 =========="
    Debug.Print "测试代码数: " & 码数

    Dim 组宽 As Integer: 组宽 = 位qt主宽
    Dim 组批 As Variant, 组单 As Variant
    ReDim 组批(1 To 码数, 1 To 组宽) As Variant
    For i = 1 To 码数
        组批(i, 位qt代码) = 码列表(i)
    Next
    组单 = 组批

    Debug.Print vbCrLf & "--- 批量模式 ---"
    Dim TT批 As Double, 结果批 As Integer
    TT批 = Timer
    结果批 = IQQQ跨码据擎_数程查询行情(组批, 使用批量:=True)
    Debug.Print "耗时(秒): " & Format(Timer - TT批, "0.00")
    Debug.Print "未停牌数: " & 结果批

    Debug.Print vbCrLf & "--- 逐只模式 ---"
    Dim TT单 As Double, 结果单 As Integer
    TT单 = Timer
    结果单 = IQQQ跨码据擎_数程查询行情(组单, 使用批量:=False)
    Debug.Print "耗时(秒): " & Format(Timer - TT单, "0.00")
    Debug.Print "未停牌数: " & 结果单

    Debug.Print vbCrLf & "--- 字段对比 ---"
    Dim 差异 As Long, 行 As Long, 列 As Long
    Dim v批 As String, v单 As String
    差异 = 0
    For 行 = 1 To 码数
        For 列 = 1 To 组宽
            v批 = "": v单 = ""
            If Not IsEmpty(组批(行, 列)) Then v批 = CStr(组批(行, 列))
            If Not IsEmpty(组单(行, 列)) Then v单 = CStr(组单(行, 列))
            If v批 <> v单 Then
                差异 = 差异 + 1
                If 差异 <= 10 Then
                    Debug.Print "x " & 码列表(行) & " 列" & 列 & ": 批=" & v批 & " 单=" & v单
                End If
            End If
        Next
    Next

    Debug.Print vbCrLf & "总差异字段数: " & 差异
    Debug.Print "倍速: " & Format((Timer - TT单) / IIf(Timer - TT批 > 0, Timer - TT批, 0.01), "0.0") & "x"
    If 差异 = 0 Then Debug.Print ">>> 结果完全一致 <<<"
End Sub





'########################################################################################
'########################################################################################
'#####################################      HTTP腾实    ##################################
'########################################################################################
'########################################################################################
'========================================================================================
'查询行情：腾讯实时 回文引号内容
'========================================================================================
Function UBHTTP腾实_查回引(CIDL As String) As String
    Dim sURL As String
    Dim sRESP As String
    '------------------------------------------------------------------------------------
    sURL = "http://qt.gtimg.cn/q=" & CIDL
    sRESP = UBHTTP通用_查程回引(sURL)
    '------------------------------------------------------------------------------------
    UBHTTP腾实_查回引 = sRESP
End Function
'========================================================================================
'查询行情：腾讯实时 回文引号内容 转换为数组
'========================================================================================
Function UBHTTP腾实_查回组(aRESP As Variant, ByVal CIDL As String) As Integer
    '------------------------------------------------------------------------------------
    Dim sRESP As String
    sRESP = UBHTTP腾实_查回引(CIDL)
    '------------------------------------------------------------------------------------
    Dim sSEP As String
    sSEP = "~"
    If Len(sRESP) > 2 Then
        aRESP = Split(sRESP, sSEP)
        UBHTTP腾实_查回组 = UBound(aRESP) - LBound(aRESP) + 1
    Else
        UBHTTP腾实_查回组 = 0
    End If
    '------------------------------------------------------------------------------------
End Function
'========================================================================================
'查询行情：腾讯实时 批量（一次HTTP查多只股票）
'参数 每批大小 = 每次URL最多带多少只（默认100）
'参数 重试次数 = 每批无结果时重试几次（默认3）
'返回 Dictionary：Key=代码(如"sh000001"), Value=Split数组(按~分隔)
'========================================================================================
Function UBHTTP腾实_查回典批量(代码串 As String _
                             , Optional 每批大小 As Integer = 常HTTP批大小 _
                             , Optional 重试次数 As Integer = 3 _
                             ) As Dictionary
    Set UBHTTP腾实_查回典批量 = New Dictionary
    If Len(代码串) = 0 Then Exit Function
    '------------------------------------------------------------------------------------
    '拆分代码串为数组 → 按每批大小切片
    '------------------------------------------------------------------------------------
    Dim 全码组 As Variant
    Dim 批起 As Long, 批止 As Long
    Dim s子代码串 As String, sURL As String, sRESP As String
    Dim 重试序号 As Integer
    Dim 行组 As Variant, 行文 As String, i As Long
    Dim 码 As String, 段组 As Variant, 引组 As Variant

    全码组 = Split(代码串, ",")

    For 批起 = LBound(全码组) To UBound(全码组) Step 每批大小
        批止 = 批起 + 每批大小 - 1
        If 批止 > UBound(全码组) Then 批止 = UBound(全码组)
        s子代码串 = Join(UTL数据转换_切片子组(全码组, 批起, 批止), ",")

        ' 重试循环
        For 重试序号 = 1 To 重试次数
            sURL = "http://qt.gtimg.cn/q=" & s子代码串
            sRESP = UBHTTP通用_查程回全通用(sURL)
            If Len(sRESP) >= 10 Then Exit For
        Next

        If Len(sRESP) < 10 Then GoTo 跳过本批

        ' 解析本批结果
        行组 = Split(sRESP, Chr(10))
        For i = LBound(行组) To UBound(行组)
            行文 = Trim(行组(i))
            If Len(行文) > 10 Then
                码 = Split(行文, "=")(0)
                If Left$(码, 2) = "v_" Then 码 = Mid$(码, 3)
                引组 = Split(行文, """")
                If UBound(引组) >= 1 Then
                    段组 = Split(引组(1), "~")
                    If UBound(段组) >= 0 Then
                        If Not UBHTTP腾实_查回典批量.Exists(码) Then
                            UBHTTP腾实_查回典批量.Add 码, 段组
                        End If
                    End If
                End If
            End If
        Next
跳过本批:
    Next 批起
End Function

' 切片辅助：从数组中取一段
Private Function UTL数据转换_切片子组(原组 As Variant, 起 As Long, 止 As Long) As Variant
    Dim 结果() As String, J As Long, K As Long
    ReDim 结果(0 To 止 - 起)
    For J = 起 To 止
        结果(K) = 原组(J)
        K = K + 1
    Next
    UTL数据转换_切片子组 = 结果
End Function
'========================================================================================
'查询行情：新浪实时 批量（一次HTTP查多只股票，适用 hk/gb_/CFF_RE_/int_/hf_/fx_ 等非沪深代码）
'返回 Dictionary：Key=代码, Value=Split数组（按逗号分隔，与查基程单码ZZ查询的aRESP格式一致）
'========================================================================================
Function UBHTTP新浪_查回典批量(代码串 As String _
                             , Optional 每批大小 As Integer = 常HTTP批大小 _
                             , Optional 重试次数 As Integer = 3 _
                             ) As Dictionary
    Set UBHTTP新浪_查回典批量 = New Dictionary
    If Len(代码串) = 0 Then Exit Function

    Dim 全码组 As Variant, 批起 As Long, 批止 As Long
    Dim s子代码串 As String, sURL As String, sRESP As String
    Dim 重试序号 As Integer, 行组 As Variant, 行文 As String, i As Long
    Dim 码 As String, 等位 As Long, 引组 As Variant, 段组 As Variant

    全码组 = Split(代码串, ",")

'    Debug.Print "[新浪批量] 代码串=" & 代码串

    For 批起 = LBound(全码组) To UBound(全码组) Step 每批大小
        批止 = 批起 + 每批大小 - 1
        If 批止 > UBound(全码组) Then 批止 = UBound(全码组)
        s子代码串 = Join(UTL数据转换_切片子组(全码组, 批起, 批止), ",")

        For 重试序号 = 1 To 重试次数
            sURL = "http://hq.sinajs.cn/list=" & s子代码串
            sRESP = UBHTTP通用_查程回全通用(sURL)
            If Len(sRESP) >= 10 Then Exit For
        Next

'        Debug.Print "[新浪批量] URL=" & sURL & " 响应长度=" & Len(sRESP) & " 行数=" & (UBound(Split(sRESP, Chr(10))) + 1)

        If Len(sRESP) < 10 Then GoTo 跳过本批

        行组 = Split(sRESP, Chr(10))
        For i = LBound(行组) To UBound(行组)
            行文 = Trim(Replace(行组(i), vbCr, ""))
            If Len(行文) > 10 Then
                等位 = InStr(行文, "=")
                If 等位 > 0 Then
                    码 = Left$(行文, 等位 - 1)
                    码 = Replace(码, "var hq_str_", "")
                    码 = Trim(Replace(码, vbCr, ""))
                End If
                引组 = Split(行文, """")
                If UBound(引组) >= 1 Then
                    段组 = Split(引组(1), ",")
                    If UBound(段组) >= 0 Then
                        If Not UBHTTP新浪_查回典批量.Exists(码) Then
                            UBHTTP新浪_查回典批量.Add 码, 段组
                        End If
                    End If
                End If
            End If
        Next
跳过本批:
    Next 批起
'    Debug.Print "[新浪批量] 结果: " & UBHTTP新浪_查回典批量.Count & " 条"
End Function
'########################################################################################
'########################################################################################
'#####################################      HTTP腾实    ##################################
'########################################################################################
'########################################################################################



'########################################################################################
'########################################################################################
'#####################################      HTTP腾历    ##################################
'########################################################################################
'########################################################################################
'========================================================================================
'查询行情：腾讯历史 回文引号内容
'========================================================================================
Function UBHTTP腾历_查回引(CIDL As String, Optional 期类 As String = 常期类为日) As String
    '------------------------------------------------------------------------------------
    '设置：URL
    '------------------------------------------------------------------------------------
    Dim sURL前缀 As String
    Select Case 期类
    Case 常期类为日
        'sURL前缀 = "http://data.gtimg.cn/flashdata/hushen/daily/19/"
        sURL前缀 = "http://data.gtimg.cn/flashdata/hushen/latest/daily/"
    Case 常期类为周
        'sURL前缀 = "http://data.gtimg.cn/flashdata/hushen/weekly/"
        sURL前缀 = "http://data.gtimg.cn/flashdata/hushen/latest/weekly/"
    Case 常期类为月
        'sURL前缀 = "http://data.gtimg.cn/flashdata/hushen/monthly/"
        sURL前缀 = "http://data.gtimg.cn/flashdata/hushen/latest/monthly/"
    End Select
    '------------------------------------------------------------------------------------
    '问题：为什么网页能够查到的数据，但是vba查不到
    '------------------------------------------------------------------------------------
    Dim sURL As String
    Dim sRESP As String
    sURL = sURL前缀 & CIDL & ".js"
    sRESP = UBHTTP通用_查程回引(sURL)
    '------------------------------------------------------------------------------------
    UBHTTP腾历_查回引 = sRESP
End Function
'========================================================================================
'查询行情：腾讯历史 回文引号内容 转换为数组
'========================================================================================
Function UBHTTP腾历_查回组行(aRESP As Variant, CIDL As String, 期类 As String) As Integer
    '------------------------------------------------------------------------------------
    Dim sRESP As String
    sRESP = UBHTTP腾历_查回引(CIDL, 期类)
    '------------------------------------------------------------------------------------
    Dim sSEP As String
    sSEP = "\n\"
    If InStr(sRESP, sSEP) > 0 Then
        sRESP = Replace(sRESP, Chr(10), "")         '去除换行符
        aRESP = Split(sRESP, sSEP)
        UBHTTP腾历_查回组行 = UBound(aRESP) - LBound(aRESP) + 1
    Else
        UBHTTP腾历_查回组行 = 0
    End If
    '------------------------------------------------------------------------------------
End Function
'########################################################################################
'########################################################################################
'#####################################      HTTP腾历    ##################################
'########################################################################################
'########################################################################################







'########################################################################################
'########################################################################################
'#####################################    HTTP辅程  ######################################
'########################################################################################
'########################################################################################
Private Function 后台质程_获取原始行情(码集 As Collection, aQUO As Variant)
'========================================================================================
'重置数组
'========================================================================================
    ReDim aQUO(码集.Count, 53) As Variant
'========================================================================================
'处理标题
'========================================================================================
    aQUO(0, 位序腾实市场) = "市场"
    aQUO(0, 位序腾实代称) = "名称"
    aQUO(0, 位序腾实代码) = "代码"
    aQUO(0, 位序腾实今收) = "今收"
    aQUO(0, 位序腾实前收) = "前收"
    aQUO(0, 位序腾实今开) = "今开"
    aQUO(0, 位序腾实交量) = "交量"
    aQUO(0, 位序腾实外盘) = "外盘"
    aQUO(0, 位序腾实内盘) = "内盘"
    aQUO(0, 位序腾实买一价) = "买一价"
    aQUO(0, 位序腾实买一量) = "买一量"
    aQUO(0, 位序腾实买二价) = "买二价"
    aQUO(0, 位序腾实买二量) = "买二量"
    aQUO(0, 位序腾实买三价) = "买三价"
    aQUO(0, 位序腾实买三量) = "买三量"
    aQUO(0, 位序腾实买四价) = "买四价"
    aQUO(0, 位序腾实买四量) = "买四量"
    aQUO(0, 位序腾实买五价) = "买五价"
    aQUO(0, 位序腾实买五量) = "买五量"
    aQUO(0, 位序腾实卖一价) = "卖一价"
    aQUO(0, 位序腾实卖一量) = "卖一量"
    aQUO(0, 位序腾实卖二价) = "卖二价"
    aQUO(0, 位序腾实卖二量) = "卖二量"
    aQUO(0, 位序腾实卖三价) = "卖三价"
    aQUO(0, 位序腾实卖三量) = "卖三量"
    aQUO(0, 位序腾实卖四价) = "卖四价"
    aQUO(0, 位序腾实卖四量) = "卖四量"
    aQUO(0, 位序腾实卖五价) = "卖五价"
    aQUO(0, 位序腾实卖五量) = "卖五量"
    aQUO(0, 位序腾实逐笔成交) = "最近逐笔成交"
    aQUO(0, 位序腾实时间) = "时间"
    aQUO(0, 位序腾实涨跌) = "涨跌"
    aQUO(0, 位序腾实今涨) = "涨幅"
    aQUO(0, 位序腾实今高) = "最高"
    aQUO(0, 位序腾实今低) = "最低"
    aQUO(0, 位序腾实价量额) = "价量额"
    aQUO(0, 位序腾实成交量) = "成交量"
    aQUO(0, 位序腾实交额) = "成交额"
    aQUO(0, 位序腾实A换手) = "换手"
    aQUO(0, 位序腾实市盈静态) = "市盈"
    aQUO(0, 位序腾实停牌) = "停牌"
    aQUO(0, 位序腾实今高2) = "最高"
    aQUO(0, 位序腾实今低2) = "最低"
    aQUO(0, 位序腾实振幅) = "振幅"
    aQUO(0, 位序腾实流市) = "流通市值"
    aQUO(0, 位序腾实总市) = "总市值"
    aQUO(0, 位序腾实A市净) = "市净"
    aQUO(0, 位序腾实A涨停) = "涨停"
    aQUO(0, 位序腾实A跌停) = "跌停"
    aQUO(0, 位序腾实A量比) = "量比"
    aQUO(0, 位序腾实A盘差) = "盘差"
    aQUO(0, 位序腾实A均价) = "均价"
    aQUO(0, 位序腾实A市盈动态) = "动态市盈"
'========================================================================================
'查询信息
'========================================================================================
    Dim nRESP As Integer
    Dim aRESP As Variant
    Dim X As Integer
    Dim CIDL As String
    Dim Y As Long
    For X = 1 To 码集.Count
        '--------------------------------------------------------------------------------
        '查询信息
        '--------------------------------------------------------------------------------
        CIDL = 码集(X)
        nRESP = UBHTTP腾实_查回组(aRESP, CIDL)
        Debug.Print "QUO >> "; X
        '--------------------------------------------------------------------------------
        '处理信息
        '--------------------------------------------------------------------------------
        If nRESP > 0 Then
            For Y = LBound(aRESP) To UBound(aRESP)
                aQUO(X, Y) = aRESP(Y)
            Next Y
            Erase aRESP
        End If
    Next X
'========================================================================================
'检查专用
'========================================================================================
    'For X = LBound(aQUO, 1) To UBound(aQUO, 1)
    '    For Y = LBound(aQUO, 2) To UBound(aQUO, 2)
    '        Cells(X + 1, Y + 1) = aQUO(X, Y)
    '    Next Y
    'Next X
'========================================================================================
End Function
'########################################################################################
'########################################################################################
'#####################################    HTTP辅程  ######################################
'########################################################################################
'########################################################################################







'########################################################################################
'########################################################################################
'#####################################    HTTP搜码  ######################################
'########################################################################################
'########################################################################################
Private Sub 后台正程_搜索沪码()
    Call 后台质程_搜索代码("sh", 0, 1000)
    Call 后台质程_搜索代码("sz", 399000, 399999)
    Call 后台质程_搜索代码("hk", 0, 99999)
End Sub


'=====================================================================================
'=====================================================================================
'搜索代码基本模块
'=====================================================================================
'=====================================================================================
Private Sub 后台质程_搜索代码(市场 As String, 代码起始 As Long, 代码结束 As Long)
    Dim TT As Double
    TT = Timer
    UTL宏工具_BEGIN
'-------------------------------------------------------------------------------------
    Dim sWS As String
    Select Case 市场
    Case "sh"
        sWS = "码沪"
    Case "sz"
        sWS = "码深"
    Case "hk"
        sWS = "码港"
    End Select
    
    Dim 参数代码格式 As String
    Select Case 市场
    Case "sh", "sz"
        参数代码格式 = 全设格式of代码
    Case "hk"
        参数代码格式 = "00000"
    End Select
    '---------------------------------------------------------------------------------
    Dim MS As Worksheet
    Call PBASE格程工具_表操工表新增(MS, sWS, wb:=ThisWorkbook, 基色底:=常色主黄)
    Dim nZROW As Integer
    nZROW = MS.[a65536].End(xlUp).Row
'=====================================================================================
'查询信息
'=====================================================================================
    Dim sURL As String
    Dim sSEP As String
    Dim sRESP As String
    Dim aRESP As Variant
    Dim aQUO() As Variant
    '---------------------------------------------------------------------------------
    Dim ROWID As Long
    Dim 代码 As String
    Dim Y As Long
    ROWID = 1
    Dim X As Long
    '---------------------------------------------------------------------------------
    On Error Resume Next
    For X = 代码起始 To 代码结束
        代码 = LCase(市场) & Format$(X, 参数代码格式)
        '-----------------------------------------------------------------------------
        '腾讯
        '-----------------------------------------------------------------------------
'        sURL = "http://qt.gtimg.cn/q=sh" & 代码
'        sSEP = "~"
        '-----------------------------------------------------------------------------
        '新浪
        '-----------------------------------------------------------------------------
        sURL = "http://hq.sinajs.cn/list=" & 代码
        sSEP = ","
        '-----------------------------------------------------------------------------
        '查询信息
        '-----------------------------------------------------------------------------
        sRESP = UBHTTP通用_查程回引(sURL)
        '-----------------------------------------------------------------------------
        '处理信息
        '-----------------------------------------------------------------------------
        If Len(sRESP) > 2 Then
            aRESP = Split(sRESP, sSEP)
            '-------------------------------------------------------------------------
            '提取信息
            '-------------------------------------------------------------------------
            ROWID = ROWID + 1
            MS.Cells(ROWID, 1) = 代码
            
            For Y = LBound(aRESP) To UBound(aRESP)
                MS.Cells(ROWID, Y + 2) = aRESP(Y)
            Next Y
            '-------------------------------------------------------------------------
        End If
        If X Mod 3000 = 0 Then ThisWorkbook.Save
    Next X
    On Error GoTo 0
    MS.Columns.AutoFit
'=====================================================================================
'=====================================================================================
POINT_WRONGWBK:
    ThisWorkbook.Save
    UTL宏工具_END
    Debug.Print "耗时：" & CInt(Timer - TT)
End Sub
'########################################################################################
'########################################################################################
'#####################################    HTTP搜码  ######################################
'########################################################################################
'########################################################################################






