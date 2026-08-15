Attribute VB_Name = "PX算研_ZPY接口"
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
'   XL算研_展探窄管蓄力()        — 窄管蓄力回测（200只×160参数组合）
'========================================================================================
Option Explicit

'======================================================================================== (2026-07-17)
' XL算研_展探窄管蓄力 — 窄管蓄力回测
'========================================================================================
Public Sub XL算研_展探窄管蓄力()
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
        Call XL算研_展探窄管蓄力_行遍历(谕组, ARRLLL, 0, 计数组, 阳柱数, 幅涨和, 幅高和, 窗口集, DS顶JA集, 波动集, 均线集)
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

'======================================================================================== (2026-07-18)
' 私有辅助函数 — 供XL展探窄管蓄力调用
'========================================================================================

'======================================================================================== (2026-07-17)
' XL算研_展探窄管蓄力_行遍历 — 单只股票的行遍历 + 160参数组合检查
'========================================================================================
' 功能：对一只股票的ALL日行情逐行检查所有160个参数组合是否满足窄管条件
' 参数：
'   谕组 — 日级别指标数组（含BSHA/BSPB/BSPC等）
'   ARRLLL — 原始行情数组（含临幅PR/临幅HR）
'   基位日类 — 日类数据在ARRLLL中的起始偏移量（通常=0）
'   计数组/阳柱数/幅涨和/幅高和 — 累加器，跨股票累积
'   窗口集/DS顶JA集/波动集/均线集 — 参数网格定义
' 逻辑：
'   1. 维护循环缓冲区（BSHA缓冲/幅涨缓冲），避免每次重算
'   2. 对每行，预计算所有窗口大小的BSHA最大值+波动率
'   3. 遍历160参数组合，逐层过滤：
'      ① 窄管(BSHA最大 ≤ DS顶JA阈值)
'      ② 低波动(标准差 × 100 < 波动阈值)
'      ③ 均线之上(BSPB>0或BSPC>0)
'   4. 条件全部满足→记录下柱数据到累加器
' 性能优化：按窗口预计算BSHA/波动，避免内层循环重复计算
'========================================================================================
Private Sub XL算研_展探窄管蓄力_行遍历(ByRef 谕组 As Variant, ByRef ARRLLL As Variant, _
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
            窗口谱BSHA(wi) = XL算研_展探窗取_BSHA最大值(BSHA缓冲, 指针, 最大窗口, win)
            窗口谱波动(wi) = XL算研_展探窗取_标准差(幅涨缓冲, 指针, 最大窗口, win)
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

'======================================================================================== (2026-07-17)
' XL算研_展探窗取_BSHA最大值 — 从循环缓冲区取最近win个BSHA的最大值
'========================================================================================
' 功能：在滑动窗口缓冲区中查找最近N天BSHA（日级别偏离DA百分比）的最大值
' 参数：
'   Buf() — 循环缓冲区[1..maxWin]
'   指针 — 下一个写入位置（指向最旧数据之后）
'   最大窗口 — 缓冲区物理大小
'   win — 本次查询窗口大小（≤最大窗口）
' 返回：最近win天内的BSHA最大值
' 逻辑：从(指针-1)倒推win个元素，处理环形索引环绕
'========================================================================================
Private Function XL算研_展探窗取_BSHA最大值(Buf() As Double, 指针 As Integer, 最大窗口 As Integer, win As Integer) As Double
    Dim 最大值 As Double: 最大值 = -9999
    Dim i As Integer, 物理索引 As Integer
    For i = 0 To win - 1
        物理索引 = 指针 - 1 - i
        If 物理索引 < 1 Then 物理索引 = 物理索引 + 最大窗口
        If Buf(物理索引) > 最大值 Then 最大值 = Buf(物理索引)
    Next: XL算研_展探窗取_BSHA最大值 = 最大值
End Function

'======================================================================================== (2026-07-17)
' XL算研_展探窗取_标准差 — 从循环缓冲区取最近win个幅涨的标准差
'========================================================================================
' 功能：计算最近N天日涨跌幅的标准差，衡量波动率
' 参数：
'   Buf() — 循环缓冲区[1..maxWin]
'   指针 — 下一个写入位置
'   最大窗口 — 缓冲区物理大小
'   win — 本次窗口大小（≥2，否则返回0）
' 返回：最近win天的日涨跌幅标准差
' 逻辑：收集值→均值→样本方差→开方
' 注意：win<2无法计算，返回0
'========================================================================================
Private Function XL算研_展探窗取_标准差(Buf() As Double, 指针 As Integer, 最大窗口 As Integer, win As Integer) As Double
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
    方差 = 方差 / (win - 1): XL算研_展探窗取_标准差 = Sqr(方差)
End Function

'======================================================================================== (2026-08-02)
' XL算研_测试日冲数据 — 检查神谕日冲计算
'========================================================================================
Public Sub XL算研_测试日冲数据()
    Dim 谕组 As Variant
    Dim 计数 As Long
    计数 = IQQQ跨码据擎_数程生成全息(谕组, 常花中股, 实结类型:="sSCC")
    If 计数 = 0 Then MsgBox "全息失败": Exit Sub
    Dim X As Long
    Dim 分布(0 To 100) As Long, 评级分布(0 To 3) As Long, 总 As Long: 总 = 0
    For X = LBound(谕组, 1) To UBound(谕组, 1)
        Dim CIDL As String: CIDL = 谕组(X, 位qt代码)
        If CIDL = "" Then GoTo 跳过
        If Not (Left$(CIDL, 2) = "sh" Or Left$(CIDL, 2) = "sz") Then GoTo 跳过
        Dim h2 As Variant: h2 = 谕组(X, 位谕of月策分日P2)
        If VarType(h2) = vbString And Len(h2) >= 3 Then
            Dim 评级 As String: 评级 = Left$(h2, 1)
            Dim 分数 As Integer: 分数 = Val(Mid$(h2, 2))
            If 分数 >= 0 And 分数 <= 100 Then 分布(分数) = 分布(分数) + 1
            Select Case 评级
                Case "A": 评级分布(0) = 评级分布(0) + 1
                Case "B": 评级分布(1) = 评级分布(1) + 1
                Case "C": 评级分布(2) = 评级分布(2) + 1
                Case "D": 评级分布(3) = 评级分布(3) + 1
            End Select
            总 = 总 + 1
        End If
跳过:
    Next
    Debug.Print "=== 月策分日P2分布 ==="
    Debug.Print "总样本: " & 总 & " 评级: A=" & 评级分布(0) & " B=" & 评级分布(1) & " C=" & 评级分布(2) & " D=" & 评级分布(3)
    Dim i As Integer
    For i = 0 To 100
        If 分布(i) > 0 Then Debug.Print "  " & Format(i, "00") & "=" & 分布(i);
    Next
    Debug.Print ""
    Erase 谕组
    MsgBox "测试完成，按 Ctrl+G 看结果", vbInformation
End Sub

'======================================================================================== (2026-08-02)
' XL算研_展探大盘个股联动 — 提取数据到CSV
'========================================================================================
Public Sub XL算研_展探大盘个股联动()
    Dim 谕组 As Variant, 计数 As Long
    Dim TT As Single: TT = Timer
    Dim CSV路径 As String: CSV路径 = "D:\@VSwork\VS昭明计划VBA优化\____temp\大盘个股联动.csv"
    计数 = IQQQ跨码据擎_数程生成全息(谕组, 常花中股, 实结类型:="sSCC")
    If 计数 = 0 Then MsgBox "全息失败": Exit Sub
    Dim 文件号 As Integer: 文件号 = FreeFile
    Open CSV路径 For Output As #文件号
    Print #文件号, "CIDL,代称,日策分P2,仓周类,月策带周,月策带日,月策略周,行业益盟,是宽基指数"
    Dim X As Long, R As Long: R = 0
    For X = LBound(谕组, 1) To UBound(谕组, 1)
        Dim CIDL2 As String: CIDL2 = 谕组(X, 位qt代码)
        If CIDL2 = "" Then GoTo 跳过2
        If Not (Left$(CIDL2, 2) = "sh" Or Left$(CIDL2, 2) = "sz") Then GoTo 跳过2
        Dim 行文本 As String
        行文本 = CIDL2 & "," & 谕组(X, 位qt代称)
        行文本 = 行文本 & "," & IIf(VBA.IsNumeric(谕组(X, 位谕of日策分P2)), CStr(谕组(X, 位谕of日策分P2)), "")
        行文本 = 行文本 & "," & 谕组(X, 位谕of仓周类) & "," & 谕组(X, 位谕of月策带周)
        行文本 = 行文本 & "," & 谕组(X, 位谕of月策带日) & "," & 谕组(X, 位谕of月策略周)
        行文本 = 行文本 & "," & 谕组(X, 位qt行益)
        行文本 = 行文本 & "," & IIf(CIDL2 = "sh000001" Or CIDL2 = "sz399006" Or CIDL2 = "sh000688", "是", "")
        Print #文件号, 行文本
        R = R + 1
跳过2:
    Next
    Close #文件号
    Erase 谕组
    MsgBox "数据已生成: " & R & " 行 -> " & CSV路径, vbInformation
End Sub

'========================================================================================
'========================================================================================
' 测试_月策略日vs日周联动 — 对比月策略日(A-H)与日周联动(周向)的对应关系
' 输出：各等级在 升/待/降 三种周向中的分布比例
' 预期：A/B/C级(日级别好)→周向=升比例高，D/H级(日级别差)→周向=降比例高
'========================================================================================
Public Sub 测试_月策略日vs日周联动()
    Dim TT As Single: TT = Timer
    Dim 谕组 As Variant
    Dim 计数 As Long
    Dim X As Long

    Debug.Print "===== 月策略日 vs 日周联动(周向) 对比 ====="
    计数 = IQQQ跨码据擎_数程生成全息(谕组, 常花中股, 实结类型:="sSCC")
    If 计数 = 0 Then Debug.Print "生成失败": Exit Sub

    ' 统计各组合
    Dim 统计 As Object
    Set 统计 = CreateObject("Scripting.Dictionary")
    Dim 总行 As Long
    For X = LBound(谕组, 1) To UBound(谕组, 1)
        Dim 月策略日 As String: 月策略日 = 谕组(X, 位谕of月策略日)
        Dim 日联 As String: 日联 = 谕组(X, 位谕of日层联动)
        If 月策略日 <> "" And 日联 <> "" Then
            Dim 周向 As String: 周向 = Left$(日联, 1)
            If InStr("升降待", 周向) > 0 Then
                Dim Key As String: Key = 月策略日 & "|" & 周向
                统计(Key) = 统计(Key) + 1
                总行 = 总行 + 1
            End If
        End If
    Next

    ' 输出结果
    Debug.Print ""
    Debug.Print "总样本: " & 总行
    Debug.Print ""
    Debug.Print "等级" & vbTab & "升" & vbTab & "待" & vbTab & "降"
    Debug.Print "----" & vbTab & "--" & vbTab & "--" & vbTab & "--"
    Dim 等级 As Variant
    For Each 等级 In Array("A", "B", "C", "D", "E", "F", "G", "H")
        Dim 升 As Long: 升 = 统计(等级 & "|升")
        Dim 待 As Long: 待 = 统计(等级 & "|待")
        Dim 降 As Long: 降 = 统计(等级 & "|降")
        Dim 总 As Long: 总 = 升 + 待 + 降
        If 总 > 0 Then
            Debug.Print 等级 & "级" & vbTab & 升 & "(" & Format$(升 / 总 * 100, "0") & "%)" & vbTab & 待 & "(" & Format$(待 / 总 * 100, "0") & "%)" & vbTab & 降 & "(" & Format$(降 / 总 * 100, "0") & "%)"
        End If
    Next
    Debug.Print ""
    Debug.Print "===== 耗时: " & CLng(Timer - TT) & "秒 ====="
End Sub

