'========================================================================================
' PX算研_ZPY接口 — Python接口模块
'========================================================================================
' 用途：所有Python调用、COM提取、测试验证的VBA入口统一放在此模块
' 调用方式：Python win32com → excel.Run("函数名")
' 设计原则：
'   1. 每个Public Sub独立完成一个数据提取/测试任务
'   2. 输出优先写入工作表（方便Python读取），也可写入立即窗口
'   3. 不依赖主菜单流程，可独立运行
'   4. 完成后MsgBox通知耗时
'========================================================================================
' 已有函数：
'   XL展探窄管蓄力()          — 窄管蓄力回测（200只×160参数组合）
'   ZPY_概率表_验证加载()           — 验证照明概率.txt加载正确性
'   ZPY_策略匹配_模拟(...)         — 模拟一只股票的周冲策略匹配
'   ZPY_概率表_调试加载()        — 逐行显示概率表加载过程
'========================================================================================
Attribute VB_Name = "PX算研_ZPY接口"
Option Explicit

'========================================================================================
' XL展探窄管蓄力 — 窄管蓄力回测
'========================================================================================
' 功能：日级别窄管条件（DS顶JA≤8 + 低波动 + 均线之上）的160参数组合验证
' 目的：找出"窄管中蓄力"的最佳参数（窗口/DS顶JA阈值/波动阈值/均线级别）
' 调用：Call XL展探窄管蓄力
' 输出：新建工作表"展探窄管蓄力"（窗口, DS顶JA阈值, 波动阈值%, 均线级别, 样本量, 阳柱数, 阳柱率%)
' 逻辑：
'   1. 遍历花册前200只股票
'   2. 每只：对每行数据（今日）检查160个参数组合是否满足窄管条件
'   3. 条件满足：记录下柱（明日）的阳柱/幅涨/幅高
'   4. 输出各组合的统计结果
' 参数网格：窗口[5,10,15,20] x DS顶JA[5,8,10,12,15] x 波动[0.5,1,1.5,2] x 均线[DJB,DJC] = 160组合
' 依赖：XL算展数程跨期, STBASE外簿工具_花册链接, PBASE格程工具_表操工表新增
'========================================================================================
Public Sub XL展探窄管蓄力()
    Dim TT As Single: TT = Timer

    '--------------------------------------------------------------------
    ' 参数定义
    '--------------------------------------------------------------------
    Dim 窗口集 As Variant:  窗口集 = Array(5, 10, 15, 20)
    Dim DS顶JA集 As Variant: DS顶JA集 = Array(5, 8, 10, 12, 15)
    Dim 波动集 As Variant:  波动集 = Array(0.5, 1, 1.5, 2)
    Dim 均线集 As Variant:  均线集 = Array("DJB", "DJC")

    Dim 总组合 As Integer
    总组合 = (UBound(窗口集) - LBound(窗口集) + 1) * _
            (UBound(DS顶JA集) - LBound(DS顶JA集) + 1) * _
            (UBound(波动集) - LBound(波动集) + 1) * _
            (UBound(均线集) - LBound(均线集) + 1)
    ' = 4 x 5 x 4 x 2 = 160

    Dim 计数组() As Long, 阳柱数() As Long, 幅涨和() As Double, 幅高和() As Double
    ReDim 计数组(0 To 总组合 - 1), 阳柱数(0 To 总组合 - 1)
    ReDim 幅涨和(0 To 总组合 - 1), 幅高和(0 To 总组合 - 1)

    ' 参数描述表
    Dim 参表() As String: ReDim 参表(0 To 总组合 - 1)
    Dim idx As Integer, wi As Integer, di As Integer, vi As Integer, mi As Integer
    For wi = LBound(窗口集) To UBound(窗口集)
        For di = LBound(DS顶JA集) To UBound(DS顶JA集)
            For vi = LBound(波动集) To UBound(波动集)
                For mi = LBound(均线集) To UBound(均线集)
                    参表(idx) = 窗口集(wi) & "," & DS顶JA集(di) & "," & 波动集(vi) & "," & 均线集(mi)
                    idx = idx + 1
                Next
            Next
        Next
    Next

    ' 取前200只
    Dim WS花天 As Worksheet
    If STBASE外簿工具_花册链接(WS花天, 常花中股) = False Then MsgBox "花册链接失败": Exit Sub
    Dim 末行 As Long: 末行 = WS花天.Cells(65536, 1).End(xlUp).Row
    Dim 股数 As Long: 股数 = 末行 - 1
    If 股数 > 200 Then 股数 = 200
    Dim 股列表() As String: ReDim 股列表(1 To 股数)
    Dim i As Long
    For i = 1 To 股数: 股列表(i) = WS花天.Cells(i + 1, 1).Value: Next

    Dim ARRLLL As Variant, 谕组 As Variant, 计数 As Integer, X As Integer
    For i = 1 To 股数
        If Len(股列表(i)) < 4 Then GoTo 下一股
        计数 = XL算展数程跨期(ARRLLL, 股列表(i), , , 谕组, , "")
        If 计数 < 1 Then GoTo 下一股
        Call 展探窄管蓄力_行遍历(谕组, ARRLLL, 0, 计数组, 阳柱数, 幅涨和, 幅高和, 窗口集, DS顶JA集, 波动集, 均线集)
下一股:
        If i Mod 50 = 0 Then Debug.Print "展探窄管蓄力: 已处理 " & i & "/" & 股数 & "只, 耗时" & CLng(Timer - TT) & "秒": DoEvents
    Next

    ' 输出
    Dim WS As Worksheet
    Call PBASE格程工具_表操工表新增(WS, "展探窄管蓄力")
    With WS
        .Cells(1, 1) = "窗口": .Cells(1, 2) = "DS顶JA阈值": .Cells(1, 3) = "波动阈值(%)"
        .Cells(1, 4) = "均线级别": .Cells(1, 5) = "样本量": .Cells(1, 6) = "阳柱数"
        .Cells(1, 7) = "阳柱率(%)": .Cells(1, 8) = "均幅涨(%)": .Cells(1, 9) = "均幅高(%)"
        .Range("A1:I1").Font.Bold = True
        For idx = 0 To 总组合 - 1
            Dim parts As Variant: parts = Split(参表(idx), ",")
            .Cells(idx + 2, 1) = CInt(parts(0)): .Cells(idx + 2, 2) = CDbl(parts(1))
            .Cells(idx + 2, 3) = CDbl(parts(2)): .Cells(idx + 2, 4) = parts(3)
            .Cells(idx + 2, 5) = 计数组(idx): .Cells(idx + 2, 6) = 阳柱数(idx)
            If 计数组(idx) > 0 Then
                .Cells(idx + 2, 7) = Round(阳柱数(idx) / 计数组(idx) * 100, 1)
                .Cells(idx + 2, 8) = Round(幅涨和(idx) / 计数组(idx) * 100, 2)
                .Cells(idx + 2, 9) = Round(幅高和(idx) / 计数组(idx) * 100, 2)
            End If
        Next
        .Columns("A:I").AutoFit
    End With
    MsgBox "完成！" & 股数 & "只，" & 总组合 & "组合，耗时 " & CLng(Timer - TT) & " 秒", vbInformation
End Sub

'========================================================================================
' ZPY_概率表_验证加载 — 验证概率表加载正确性
'========================================================================================
' 功能：用5组已知的(策略,市板)→期望值 验证查概率表()函数返回正确
' 目的：排查D:\zdata\照明概率.txt的格式问题或查概率表()函数bug
' 调用：Call ZPY_概率表_验证加载
' 输出：Debug.Print逐项显示，MsgBox汇总结果
' 逻辑：
'   1. 硬编码5组测试数据（全量基准|Qd=28.6, 金最优|Qe=100.0 等）
'   2. 逐项调用查概率表()对比期望值
'   3. 全部通过=绿色MsgBox，任一失败=红色MsgBox+显示偏差
' 常见失败原因：概率表文件不存在/格式错误/新策略未加入概率表
'========================================================================================
Public Sub ZPY_概率表_验证加载()
    Dim 测试项 As Variant
    测试项 = Array( _
        Array("全量基准", "Qd", 28.6), _
        Array("金+多长", "Qif", 65.0), _
        Array("金+多长+升排+非孕", "Qimit", 91.4), _
        Array("银+盈提示有", "Qin", 86.4), _
        Array("金最优(全部)", "Qe", 100.0))

    Dim i As Integer, 策略 As String, 市板 As String, 期望 As Double, 实际 As Double
    Dim 全部正确 As Boolean: 全部正确 = True
    Debug.Print "===== 查概率表 测试 ====="
    For i = LBound(测试项) To UBound(测试项)
        策略 = 测试项(i)(0): 市板 = 测试项(i)(1): 期望 = 测试项(i)(2)
        实际 = 查概率表(策略, 市板)
        If 实际 = 期望 Then
            Debug.Print "✅ " & 策略 & " | " & 市板 & " = " & 实际
        Else
            Debug.Print "❌ " & 策略 & " | " & 市板 & " = " & 实际 & " (期望 " & 期望 & ")"
            全部正确 = False
        End If
    Next
    If 全部正确 Then
        MsgBox "查概率表 测试通过 ✅", vbInformation
    Else
        MsgBox "查概率表 测试失败 ❌", vbExclamation
    End If
End Sub

'========================================================================================
' ZPY_策略匹配_模拟 — 模拟一只股票的周冲策略匹配
'========================================================================================
' 功能：给定周线条件参数，模拟神谕的周冲策略匹配逻辑，输出匹配结果
' 目的：验证策略匹配逻辑是否正确（特别用于新增/修改匹配条件后）
' 调用：Call ZPY_策略匹配_模拟("金","乙",7,"升.尾连QQ.Q3","高","Aa龙猪.初")
' 参数（均为可选，有默认值）：
'   WXCD — 大局（默认"金"）
'   WXAB — 护型（默认"甲"，可选甲/乙/己/丙/丁/戊）
'   ZA — ZA周数（默认7）
'   柱排 — 周类柱排字符串（默认"升.尾连QQ.Q3"）
'   盈提 — 盈提示（默认"高"，可选空/高/宽/丘）
'   波型 — 波型字符串（默认"Aa龙猪.初"）
' 输出：Debug.Print显示 输入参数→匹配策略→查概率表结果
' 逻辑：完整复制神谕.bas中的策略匹配If-ElseIf树
'========================================================================================
Public Sub ZPY_策略匹配_模拟(Optional WXCD As String = "金", _
                           Optional WXAB As String = "甲", _
                           Optional ZA As Double = 7, _
                           Optional 柱排 As String = "升.尾连QQ.Q3", _
                           Optional 盈提 As String = "高", _
                           Optional 波型 As String = "Aa龙猪.初")
    Dim 周局 As String: 周局 = WXCD
    Dim 周护 As String: 周护 = WXAB
    Dim 周ZA As Double: 周ZA = ZA
    Dim 周柱排 As String: 周柱排 = 柱排
    Dim 周盈提 As String: 周盈提 = 盈提
    Dim 周波型 As String: 周波型 = 波型
    Dim 周策略 As String: 周策略 = ""

    ' 复制神谕中的匹配逻辑
    If InStr(周局, "金") > 0 And InStr(周护, "甲") + InStr(周护, "乙") + InStr(周护, "己") > 0 Then
        If Left$(周柱排, 1) = "升" And InStr(周柱排, "尾反孕") = 0 Then
            If InStr(周盈提, "高") > 0 Then
                If InStr(周波型, "龙猪") > 0 Or InStr(周波型, "龙管") > 0 Then
                    周策略 = "金最优(全部)"
                Else: 周策略 = "金+多长+升排+非孕+盈高"
                End If
            Else: 周策略 = "金+多长+升排+非孕"
            End If
        ElseIf Left$(周柱排, 1) = "升" Then: 周策略 = "金+多长+升排"
        Else: 周策略 = "金+多长"
        End If
    ElseIf InStr(周局, "银") > 0 Then
        If InStr(周盈提, "高") > 0 Or InStr(周盈提, "宽") > 0 Then: 周策略 = "银+盈提示有"
        ElseIf InStr(周护, "己") > 0 Then: 周策略 = "银+WXAB=己"
        ElseIf Left$(周柱排, 1) = "升" Then: 周策略 = "银+柱排=升"
        ElseIf InStr(周波型, "龙猪") > 0 Then: 周策略 = "银+龙猪"
        ElseIf 周ZA > 5 And 周ZA <= 10 Then: 周策略 = "银+ZA5~10"
        End If
    End If

    Debug.Print "===== 匹配策略 测试 ====="
    Debug.Print "输入: WXCD=" & 周局 & " WXAB=" & 周护 & " ZA=" & 周ZA
    Debug.Print "     柱排=" & 周柱排 & " 盈提=" & 周盈提 & " 波型=" & 周波型
    If 周策略 <> "" Then
        Debug.Print "匹配: " & 周策略
        Debug.Print "概率(Qd): " & 查概率表(周策略, "Qd")
    Else: Debug.Print "匹配: 无"
    End If
End Sub

'========================================================================================
' ZPY_概率表_调试加载 — 逐行显示概率表加载过程
'========================================================================================
' 功能：打开D:\zdata\照明概率.txt，逐行读取并打印到立即窗口，最后验证查概率表()可正常查询
' 目的：排查概率表文件是否存在/编码是否正确/行列格式是否对齐
' 调用：Call ZPY_概率表_调试加载
' 输出：Debug.Print显示（文件路径/表头/前3行数据/总行数/末行查询结果）
' 逻辑：
'   1. 尝试打开文件（On Error捕获路径错误）
'   2. 读取表头→显示列数
'   3. 逐行读取→显示前3行内容
'   4. 关闭文件→调用查概率表("全量基准","Qd")验证
' 典型排查场景：概率表新增策略后/文件损坏/路径变更
'========================================================================================
Public Sub ZPY_概率表_调试加载()
    Dim 文件号 As Integer, 行内容 As String, 行数 As Integer
    Dim 字段 As Variant, 头字段 As Variant
    文件号 = FreeFile
    On Error GoTo 文件错误
    Open "D:\zdata\照明概率.txt" For Input As #文件号
    Debug.Print "✅ 文件打开成功"
    Line Input #文件号, 行内容: 头字段 = Split(行内容, vbTab)
    Debug.Print "✅ 表头(" & UBound(头字段) + 1 & "列): " & 行内容
    行数 = 0
    Do While Not EOF(文件号)
        Line Input #文件号, 行内容: 行数 = 行数 + 1
        字段 = Split(行内容, vbTab)
        If 行数 <= 3 Then Debug.Print "  行" & 行数 & ": " & 字段(0) & "|" & 字段(1)
    Loop
    Close #文件号: Debug.Print "✅ 共 " & 行数 & " 行数据"
    Debug.Print "✅ 查概率表(""全量基准"",""Qd"") = " & 查概率表("全量基准", "Qd")
    Exit Sub
文件错误:
    Debug.Print "❌ " & Err.Description & " 路径: D:\zdata\照明概率.txt"
End Sub

'========================================================================================
' 私有辅助函数
'========================================================================================
Private Sub 展探窄管蓄力_行遍历(ByRef 谕组 As Variant, ByRef ARRLLL As Variant, _
    ByVal 基位日类 As Integer, ByRef 计数组() As Long, ByRef 阳柱数() As Long, _
    ByRef 幅涨和() As Double, ByRef 幅高和() As Double, _
    ByRef 窗口集 As Variant, ByRef DS顶JA集 As Variant, _
    ByRef 波动集 As Variant, ByRef 均线集 As Variant)
    Dim 总行 As Integer: 总行 = UBound(谕组, 1) - LBound(谕组, 1) + 1
    Dim 最大窗口 As Integer: 最大窗口 = 窗口集(UBound(窗口集))
    Dim BSHA缓冲() As Double, 幅涨缓冲() As Double
    ReDim BSHA缓冲(1 To 最大窗口), 幅涨缓冲(1 To 最大窗口)
    Dim X As Integer, 指针 As Integer: 指针 = 1
    For X = LBound(谕组, 1) To UBound(谕组, 1) - 1
        Dim BSHA As Variant: BSHA = 谕组(X, 位谕of日层BSHA)
        Dim 幅涨 As Variant: 幅涨 = ARRLLL(X, 基位日类 + 位os临幅PR)
        Dim 下柱幅涨 As Variant: 下柱幅涨 = ARRLLL(X + 1, 基位日类 + 位os临幅PR)
        Dim 下柱幅高 As Variant: 下柱幅高 = ARRLLL(X + 1, 基位日类 + 位os临幅HR)
        Dim BSPB As Variant: BSPB = 谕组(X, 位谕of日波BSPB)
        Dim BSPC As Variant: BSPC = 谕组(X, 位谕of日波BSPC)
        If VBA.IsEmpty(BSHA) Or VBA.IsEmpty(幅涨) Then GoTo 下一行
        If VBA.IsEmpty(下柱幅涨) Or VBA.IsEmpty(下柱幅高) Then GoTo 下一行
        BSHA缓冲(指针) = CDbl(BSHA): 幅涨缓冲(指针) = CDbl(幅涨)
        指针 = 指针 + 1: If 指针 > 最大窗口 Then 指针 = 1
        If X < LBound(谕组, 1) + 最大窗口 - 1 Then GoTo 下一行
        Dim 窗口谱BSHA() As Double, 窗口谱波动() As Double
        ReDim 窗口谱BSHA(LBound(窗口集) To UBound(窗口集))
        ReDim 窗口谱波动(LBound(窗口集) To UBound(窗口集))
        Dim wi As Integer
        For wi = LBound(窗口集) To UBound(窗口集)
            Dim win As Integer: win = 窗口集(wi)
            窗口谱BSHA(wi) = 展探窗取_BSHA最大值(BSHA缓冲, 指针, 最大窗口, win)
            窗口谱波动(wi) = 展探窗取_标准差(幅涨缓冲, 指针, 最大窗口, win)
        Next
        Dim idx As Integer: idx = 0
        For wi = LBound(窗口集) To UBound(窗口集)
            Dim 当前BSHA最大 As Double: 当前BSHA最大 = 窗口谱BSHA(wi)
            Dim 当前波动 As Double: 当前波动 = 窗口谱波动(wi)
            For di = LBound(DS顶JA集) To UBound(DS顶JA集)
                If 当前BSHA最大 > DS顶JA集(di) Then
                    idx = idx + (UBound(波动集) - LBound(波动集) + 1) * (UBound(均线集) - LBound(均线集) + 1)
                    GoTo 跳过此DS
                End If
                For vi = LBound(波动集) To UBound(波动集)
                    If 当前波动 * 100 >= 波动集(vi) Then
                        idx = idx + (UBound(均线集) - LBound(均线集) + 1)
                        GoTo 跳过此波动
                    End If
                    For mi = LBound(均线集) To UBound(均线集)
                        Select Case 均线集(mi)
                            Case "DJB": If CDbl(BSPB) <= 0 Then GoTo 跳过此组合
                            Case "DJC": If CDbl(BSPC) <= 0 Then GoTo 跳过此组合
                        End Select
                        计数组(idx) = 计数组(idx) + 1
                        If CDbl(下柱幅涨) > 0 Then 阳柱数(idx) = 阳柱数(idx) + 1
                        幅涨和(idx) = 幅涨和(idx) + CDbl(下柱幅涨)
                        幅高和(idx) = 幅高和(idx) + CDbl(下柱幅高)
跳过此组合:          idx = idx + 1
                    Next mi
跳过此波动:        Next vi
跳过此DS:        Next di
        Next wi
下一行: Next X
End Sub

Private Function 展探窗取_BSHA最大值(Buf() As Double, 指针 As Integer, 最大窗口 As Integer, win As Integer) As Double
    Dim 最大值 As Double: 最大值 = -9999
    Dim i As Integer, 物理索引 As Integer
    For i = 0 To win - 1
        物理索引 = 指针 - 1 - i
        If 物理索引 < 1 Then 物理索引 = 物理索引 + 最大窗口
        If Buf(物理索引) > 最大值 Then 最大值 = Buf(物理索引)
    Next: 展探窗取_BSHA最大值 = 最大值
End Function

Private Function 展探窗取_标准差(Buf() As Double, 指针 As Integer, 最大窗口 As Integer, win As Integer) As Double
    If win < 2 Then Exit Function
    Dim 临时() As Double: ReDim 临时(0 To win - 1)
    Dim i As Integer, 物理索引 As Integer
    For i = 0 To win - 1
        物理索引 = 指针 - 1 - i
        If 物理索引 < 1 Then 物理索引 = 物理索引 + 最大窗口
        临时(i) = Buf(物理索引)
    Next
    Dim 均值 As Double: 均值 = 0
    For i = 0 To win - 1: 均值 = 均值 + 临时(i): Next: 均值 = 均值 / win
    Dim 方差 As Double: 方差 = 0
    For i = 0 To win - 1: 方差 = 方差 + (临时(i) - 均值) ^ 2: Next
    方差 = 方差 / (win - 1): 展探窗取_标准差 = Sqr(方差)
End Function