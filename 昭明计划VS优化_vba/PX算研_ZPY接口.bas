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
'   XL展探窄管蓄力()          — 窄管蓄力回测（200只×160参数组合）
'   ZPY_概率表_验证加载()           — 验证照明概率.txt加载正确性
'   ZPY_策略匹配_模拟(...)         — 模拟一只股票的周冲策略匹配
'   ZPY_概率表_调试加载()        — 逐行显示概率表加载过程
'   ZPY_批量算展()               — 批量生成算展Excel用于验证（读取stocks.txt）
'========================================================================================
Option Explicit

'======================================================================================== (2026-07-17)
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

'======================================================================================== (2026-07-17 迁自神谕)
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
        Array("金多", "Qif", 65#), _
        Array("金升非", "Qimit", 91.4), _
        Array("银盈", "Qin", 86.4), _
        Array("金升非盈龙", "Qe", 100#))

    Dim i As Integer, 策略 As String, 市板 As String, 期望 As Double, 实际 As Double
    Dim 全部正确 As Boolean: 全部正确 = True
    Debug.Print "===== 查概率表 测试 ====="
    For i = LBound(测试项) To UBound(测试项)
        策略 = 测试项(i)(0): 市板 = 测试项(i)(1): 期望 = 测试项(i)(2)
        实际 = IQQQ跨码工具_查周冲策分(策略, 市板)
        If 实际 = 期望 Then
            Debug.Print "? " & 策略 & " | " & 市板 & " = " & 实际
        Else
            Debug.Print "? " & 策略 & " | " & 市板 & " = " & 实际 & " (期望 " & 期望 & ")"
            全部正确 = False
        End If
    Next
    If 全部正确 Then
        MsgBox "查概率表 测试通过 ?", vbInformation
    Else
        MsgBox "查概率表 测试失败 ?", vbExclamation
    End If
End Sub

'======================================================================================== (2026-07-17 迁自神谕)
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
                    周策略 = "金升非盈龙"
                Else
                    周策略 = "金升非盈"
                End If
            Else
                周策略 = "金升非"
            End If
        ElseIf Left$(周柱排, 1) = "升" Then
            周策略 = "金升"
        Else
            周策略 = "金多"
        End If
    ElseIf InStr(周局, "银") > 0 Then
        If InStr(周盈提, "高") > 0 Or InStr(周盈提, "宽") > 0 Then
            周策略 = "银盈"
        ElseIf InStr(周护, "己") > 0 Then
            周策略 = "银己"
        ElseIf Left$(周柱排, 1) = "升" Then
            周策略 = "银升"
        ElseIf InStr(周波型, "龙猪") > 0 Then
            周策略 = "银龙"
        ElseIf 周ZA > 5 And 周ZA <= 10 Then
            周策略 = "银ZA"
        End If
    End If

    Debug.Print "===== 匹配策略 测试 ====="
    Debug.Print "输入: WXCD=" & 周局 & " WXAB=" & 周护 & " ZA=" & 周ZA
    Debug.Print "     柱排=" & 周柱排 & " 盈提=" & 周盈提 & " 波型=" & 周波型
    If 周策略 <> "" Then
        Debug.Print "匹配: " & 周策略
        Debug.Print "概率(Qd): " & IQQQ跨码工具_查周冲策分(周策略, "Qd")
    Else: Debug.Print "匹配: 无"
    End If
End Sub

'======================================================================================== (2026-07-17 迁自神谕)
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
'   4. 关闭文件→调用IQQQ跨码工具_查周冲策分("全量基准","Qd")验证
' 典型排查场景：概率表新增策略后/文件损坏/路径变更
'========================================================================================
Public Sub ZPY_概率表_调试加载()
    Dim 文件号 As Integer, 行内容 As String, 行数 As Integer
    Dim 字段 As Variant, 头字段 As Variant
    文件号 = FreeFile
    On Error GoTo 文件错误
    Open "D:\zdata\照明概率.txt" For Input As #文件号
    Debug.Print "? 文件打开成功"
    Line Input #文件号, 行内容: 头字段 = Split(行内容, vbTab)
    Debug.Print "? 表头(" & UBound(头字段) + 1 & "列): " & 行内容
    行数 = 0
    Do While Not EOF(文件号)
        Line Input #文件号, 行内容: 行数 = 行数 + 1
        字段 = Split(行内容, vbTab)
        If 行数 <= 3 Then Debug.Print "  行" & 行数 & ": " & 字段(0) & "|" & 字段(1)
    Loop
    Close #文件号: Debug.Print "? 共 " & 行数 & " 行数据"
    Debug.Print "? IQQQ跨码工具_查周冲策分(""全量基准"",""Qd"") = " & IQQQ跨码工具_查周冲策分("全量基准", "Qd")
    Exit Sub
文件错误:
    Debug.Print "? " & Err.Description & " 路径: D:\zdata\照明概率.txt"
End Sub

'======================================================================================== (2026-07-18)
' ZPY_批量算展 — 批量生成算展Excel用于验证
'========================================================================================
' 读取 D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0724\stocks.txt
' 每市板100只，已有则跳过，无则生成，确保每市板100只
' 调用：Alt+F8 → ZPY_批量算展 → 运行
' 进度：Excel状态栏查看
'========================================================================================
Public Sub ZPY_批量算展()
    Dim 输出目录 As String
    输出目录 = ThisWorkbook.Path & "\昭明算展\算展0724\"

    Dim FSO As Object
    Set FSO = CreateObject("Scripting.FileSystemObject")
    If Not FSO.FolderExists(输出目录) Then FSO.CreateFolder 输出目录

    ' 读取stocks.txt到字典
    Dim 路径 As String: 路径 = 输出目录 & "stocks.txt"
    If Not FSO.FileExists(路径) Then MsgBox "找不到: " & 路径, vbCritical: Exit Sub

    Dim 全部股票 As Object: Set 全部股票 = CreateObject("Scripting.Dictionary")
    Dim 文件号 As Integer, 行内容 As String, 字段 As Variant
    Dim 代码 As String, 名称 As String, 市板 As Variant, key As Variant

    文件号 = FreeFile
    Open 路径 For Input As #文件号
    Do While Not EOF(文件号)
        Line Input #文件号, 行内容: 行内容 = Trim(行内容)
        If Len(行内容) = 0 Then GoTo 下一行
        If Left$(行内容, 1) = "#" Or Left$(行内容, 1) = "[" Then GoTo 下一行
        字段 = Split(行内容, ",")
        If UBound(字段) < 1 Then GoTo 下一行
        代码 = Trim(字段(1))
        If UBound(字段) >= 2 Then 名称 = Trim(字段(2))
        市板 = Trim(字段(0))
        全部股票(代码) = 市板 & "|" & 名称
下一行:
    Loop
    Close #文件号
    Debug.Print "读取股票: " & 全部股票.Count & "只"

    ' 统计各市板已有的xlsx
    Dim 市板集 As Object: Set 市板集 = CreateObject("Scripting.Dictionary")
    Dim 各市板已有 As Object: Set 各市板已有 = CreateObject("Scripting.Dictionary")
    Dim 各市板待生成 As Object: Set 各市板待生成 = CreateObject("Scripting.Dictionary")
    Dim 各市板列表 As Object: Set 各市板列表 = CreateObject("Scripting.Dictionary")

    ' 遍历全部股票，按市板分组
    For Each key In 全部股票.Keys
        市板 = Split(全部股票(key), "|")(0)
        If Not 各市板列表.Exists(市板) Then Set 各市板列表(市板) = CreateObject("Scripting.Dictionary")
        各市板列表(市板)(key) = 全部股票(key)
    Next

    ' 统计各市板已有文件
    Dim 已有文件 As Object: Set 已有文件 = CreateObject("Scripting.Dictionary")
    Dim f As Object
    For Each f In FSO.GetFolder(输出目录).Files
        If LCase(FSO.GetExtensionName(f.Name)) = "xlsx" Then
            Dim 文件码 As String: 文件码 = Replace(f.Name, "算展.", "")
            文件码 = Replace(文件码, ".xlsx", "")
            已有文件(文件码) = True
        End If
    Next

    ' 输出各市板状态
    Dim 总生成 As Long: 总生成 = 0
    Dim 总跳过 As Long: 总跳过 = 0
    Dim 总失败 As Long: 总失败 = 0

    For Each 市板 In 各市板列表.Keys
        Dim 已有数 As Long: 已有数 = 0
        Dim 待生 As Object: Set 待生 = CreateObject("Scripting.Dictionary")
        For Each key In 各市板列表(市板).Keys
            If 已有文件.Exists(key) Then
                已有数 = 已有数 + 1
            Else
                待生(key) = 全部股票(key)
            End If
        Next

        ' 需要生成的数量 = 100 - 已有数
        Dim 需生成 As Long: 需生成 = 100 - 已有数
        If 需生成 < 0 Then 需生成 = 0

        ' 输出该市板状态
        Application.StatusBar = "市板 " & 市板 & " : 已有" & 已有数 & "只, 需生成" & 需生成 & "只"

        ' 生成缺失的
        Dim 计数 As Long: 计数 = 0
        For Each key In 待生.Keys
            If 计数 >= 需生成 Then Exit For
            代码 = key
            名称 = Split(待生(key), "|")(1)
            Application.StatusBar = "正在生成 [" & 市板 & "] " & 代码 & " " & 名称 & " (" & (计数 + 1) & "/" & 需生成 & ")"

            On Error Resume Next
            Call XL算展取单股(代码)
            Dim 源路径 As String: 源路径 = ThisWorkbook.Path & "\昭明算展\算展." & 代码 & ".xlsx"
            If Err.Number = 0 And FSO.FileExists(源路径) Then
                ' 生成成功，移动文件到输出目录
                Dim 目标路径 As String: 目标路径 = 输出目录 & "算展." & 代码 & ".xlsx"
                If FSO.FileExists(目标路径) Then FSO.DeleteFile 目标路径
                On Error Resume Next: FSO.MoveFile 源路径, 目标路径: On Error GoTo 0
                总生成 = 总生成 + 1: 计数 = 计数 + 1
            Else
                If Err.Number <> 0 Then Err.Clear
                总失败 = 总失败 + 1
            End If
            On Error GoTo 0
        Next
        总跳过 = 总跳过 + (已有数 + 待生.Count - 需生成)
    Next

    Application.StatusBar = False
    Application.StatusBar = "批量算展完成! 生成:" & 总生成 & " 跳过:" & 总跳过 & " 失败:" & 总失败
    Debug.Print "批量算展完成! 生成:" & 总生成 & " 跳过:" & 总跳过 & " 失败:" & 总失败
End Sub

'========================================================================================
' 私有辅助函数 — 供XL展探窄管蓄力调用
'========================================================================================

'======================================================================================== (2026-07-17)
' 展探窄管蓄力_行遍历 — 单只股票的行遍历 + 160参数组合检查
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

'======================================================================================== (2026-07-17)
' 展探窗取_BSHA最大值 — 从循环缓冲区取最近win个BSHA的最大值
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
Private Function 展探窗取_BSHA最大值(Buf() As Double, 指针 As Integer, 最大窗口 As Integer, win As Integer) As Double
    Dim 最大值 As Double: 最大值 = -9999
    Dim i As Integer, 物理索引 As Integer
    For i = 0 To win - 1
        物理索引 = 指针 - 1 - i
        If 物理索引 < 1 Then 物理索引 = 物理索引 + 最大窗口
        If Buf(物理索引) > 最大值 Then 最大值 = Buf(物理索引)
    Next: 展探窗取_BSHA最大值 = 最大值
End Function

'======================================================================================== (2026-07-17)
' 展探窗取_标准差 — 从循环缓冲区取最近win个幅涨的标准差
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

'========================================================================================
'日冲查概率 — 查216分支概率表，返回→ZE+ZC+ZA和DSHA>1
'入口：DXEF(金/银/嘘/唏/屎/尿), DXCD(上/中/下/忐/忠/忑), DXAB(上/中/下/忐/忠/忑)
'返回：pZA=→ZE+ZC+ZA概率, pDSHA1=下日DSHA>1概率, 小样本标记
'数据：6战场×6DXCD×6DXAB=216分支，内嵌VBA数组
'========================================================================================
Public Function IQQQ跨码工具_查日冲概率(ByVal sDXEF As String, ByVal sDXCD As String, ByVal sDXAB As String, _
    ByRef pZA As Double, ByRef pDSHA1 As Double, ByRef 小样本标记 As String) As Boolean

    Dim iEF As Long, iCD As Long, iAB As Long
    Dim rowData As Variant

    '映射DXEF
    Select Case sDXEF
        Case "金": iEF = 0
        Case "银": iEF = 1
        Case "嘘": iEF = 2
        Case "唏": iEF = 3
        Case "屎": iEF = 4
        Case "尿": iEF = 5
        Case Else: IQQQ跨码工具_查日冲概率 = False: Exit Function
    End Select
    '映射DXCD
    Select Case sDXCD
        Case "上": iCD = 0
        Case "中": iCD = 1
        Case "下": iCD = 2
        Case "忐": iCD = 3
        Case "忠": iCD = 4
        Case "忑": iCD = 5
        Case Else: IQQQ跨码工具_查日冲概率 = False: Exit Function
    End Select
    '映射DXAB
    Select Case sDXAB
        Case "上": iAB = 0
        Case "中": iAB = 1
        Case "下": iAB = 2
        Case "忐": iAB = 3
        Case "忠": iAB = 4
        Case "忑": iAB = 5
        Case Else: IQQQ跨码工具_查日冲概率 = False: Exit Function
    End Select

    '216分支概率数据（6战场×6DXCD×6DXAB）
    '格式：Array(N, →ZE>0, →ZE+ZC, →ZE+ZC+ZA, DSHA>1, 小样本标记)
    rowData = 日冲取数据(iEF, iCD, iAB)
    If IsEmpty(rowData) Then IQQQ跨码工具_查日冲概率 = False: Exit Function

    pZA = rowData(3)       '→ZE>0+ZC>0+ZA>0
    pDSHA1 = rowData(4)    '下日DSHA>1
    ' 小样本分级：按N值动态判断（不依赖硬编码标记）
    Dim 样本N As Long: 样本N = CLng(rowData(0))
    If 样本N < 1000 Then
        小样本标记 = ".微"
    ElseIf 样本N < 10000 Then
        小样本标记 = ".小"
    Else
        小样本标记 = ""
    End If
    IQQQ跨码工具_查日冲概率 = (样本N > 0)
End Function

'========================================================================================
'日冲取数据 — 返回指定战场的6×6概率数组
'========================================================================================
' ===== 日冲概率数据初始化（216分支）=====
Private Function 日冲取数据(iEF As Long, iCD As Long, iAB As Long) As Variant
    Static ARRDATA(0 To 5, 0 To 5, 0 To 5) As Variant
    Static 已初始化 As Boolean
    If Not 已初始化 Then
        已初始化 = True
        ARRDATA(0, 0, 0) = Array(2835950, 99.8, 98#, 82.4, 86.8, 0)
        ARRDATA(0, 0, 1) = Array(592158, 99.3, 92.9, 29.8, 43.4, 0)
        ARRDATA(0, 0, 2) = Array(413672, 98.1, 73.4, 15.9, 26.8, 0)
        ARRDATA(0, 0, 3) = Array(174052, 99.5, 85.9, 81.1, 90.1, 0)
        ARRDATA(0, 0, 4) = Array(52107, 99.3, 76.3, 65#, 78.5, 0)
        ARRDATA(0, 0, 5) = Array(183943, 99#, 66.9, 28.6, 44.1, 0)
        ARRDATA(0, 1, 0) = Array(9430, 99.1, 38.7, 38.7, 67.6, 0)
        ARRDATA(0, 1, 1) = Array(3983, 98.2, 32.3, 29.1, 41.5, 0)
        ARRDATA(0, 1, 2) = Array(77256, 94.2, 20.9, 9.7, 16.7, 0)
        ARRDATA(0, 1, 3) = Array(47647, 99.4, 44.9, 44.9, 87.5, 0)
        ARRDATA(0, 1, 4) = Array(103331, 99.1, 30#, 30#, 79.4, 0)
        ARRDATA(0, 1, 5) = Array(662167, 98.2, 14.6, 10.8, 29.2, 0)
        ARRDATA(0, 2, 0) = Array(4021, 97#, 29.9, 29.9, 69.1, 0)
        ARRDATA(0, 2, 1) = Array(1420, 94.3, 24.1, 23.6, 44#, 0)
        ARRDATA(0, 2, 2) = Array(21334, 71.5, 12.4, 9#, 18.1, 0)
        ARRDATA(0, 2, 3) = Array(23839, 96.9, 25.7, 25.7, 87.8, 0)
        ARRDATA(0, 2, 4) = Array(96829, 89.4, 8.6, 8.6, 80.1, 0)
        ARRDATA(0, 2, 5) = Array(890297, 60.5, 2#, 2#, 22.9, 0)
        ARRDATA(0, 3, 0) = Array(265004, 97.4, 95.1, 85.1, 88.3, 0)
        ARRDATA(0, 3, 1) = Array(30720, 82.3, 75.9, 30.8, 41#, 0)
        ARRDATA(0, 3, 2) = Array(6655, 60.8, 50.5, 18.8, 29.4, 0)
        ARRDATA(0, 3, 3) = Array(5228, 94.3, 84.9, 84.3, 93.2, 0)
        ARRDATA(0, 3, 4) = Array(161, 72#, 60.2, 57.1, 78.9, 0)
        ARRDATA(0, 3, 5) = Array(398, 65.3, 56#, 41.2, 54.8, 0)
        ARRDATA(0, 4, 0) = Array(29874, 88.6, 71.6, 68.7, 80#, 0)
        ARRDATA(0, 4, 1) = Array(8960, 69.1, 52.2, 30.3, 39.2, 0)
        ARRDATA(0, 4, 2) = Array(5662, 48.5, 35.6, 17.4, 26.8, 0)
        ARRDATA(0, 4, 3) = Array(4655, 90.3, 74.3, 74.3, 91.3, 0)
        ARRDATA(0, 4, 4) = Array(229, 78.2, 60.7, 57.6, 70.3, 0)
        ARRDATA(0, 4, 5) = Array(500, 58.6, 44.8, 36.8, 54.4, 0)
        ARRDATA(0, 5, 0) = Array(19116, 86.3, 35#, 35#, 73.5, 0)
        ARRDATA(0, 5, 1) = Array(6978, 72.1, 25.1, 23.3, 41.5, 0)
        ARRDATA(0, 5, 2) = Array(29877, 46.6, 14.4, 10.9, 22.7, 0)
        ARRDATA(0, 5, 3) = Array(31143, 87.6, 31.3, 31.3, 87.2, 0)
        ARRDATA(0, 5, 4) = Array(34339, 65.5, 10.3, 10.3, 76.1, 0)
        ARRDATA(0, 5, 5) = Array(197633, 23.3, 3.2, 3.1, 25.7, 0)
        ARRDATA(1, 0, 0) = Array(801170, 99.8, 98.8, 80.9, 87.2, 0)
        ARRDATA(1, 0, 1) = Array(198140, 99.1, 95.1, 28.8, 41.8, 0)
        ARRDATA(1, 0, 2) = Array(127383, 96.9, 76.3, 15.4, 25.4, 0)
        ARRDATA(1, 0, 3) = Array(31448, 99.3, 87.1, 80.3, 89.5, 0)
        ARRDATA(1, 0, 4) = Array(12052, 99#, 76.5, 63.6, 77.9, 0)
        ARRDATA(1, 0, 5) = Array(52636, 98.4, 68.4, 28.2, 42.1, 0)
        ARRDATA(1, 1, 0) = Array(620, 95.3, 35.3, 35.3, 60.6, 0)
        ARRDATA(1, 1, 1) = Array(360, 94.7, 28.6, 26.9, 35.8, 0)
        ARRDATA(1, 1, 2) = Array(15033, 85.8, 20.2, 7.8, 13.5, 0)
        ARRDATA(1, 1, 3) = Array(3767, 98.2, 47.4, 47.4, 86.5, 0)
        ARRDATA(1, 1, 4) = Array(13448, 98#, 33.3, 33.3, 77.1, 0)
        ARRDATA(1, 1, 5) = Array(133564, 94.3, 16#, 10.8, 25.9, 0)
        ARRDATA(1, 2, 0) = Array(192, 93.2, 28.6, 28.6, 66.1, 0)
        ARRDATA(1, 2, 1) = Array(87, 65.9, 15.5, 15.4, 35.5, 1)
        ARRDATA(1, 2, 2) = Array(2778, 42.3, 10.9, 7.8, 13.8, 0)
        ARRDATA(1, 2, 3) = Array(973, 92.8, 30.4, 30.4, 87.7, 0)
        ARRDATA(1, 2, 4) = Array(5478, 80.6, 9.7, 9.7, 77.7, 0)
        ARRDATA(1, 2, 5) = Array(98639, 43.7, 2.1, 2#, 17.7, 0)
        ARRDATA(1, 3, 0) = Array(31181, 96.3, 95.4, 86#, 86.8, 0)
        ARRDATA(1, 3, 1) = Array(3526, 75.3, 72.7, 28.4, 34.8, 0)
        ARRDATA(1, 3, 2) = Array(808, 45.5, 40.7, 15#, 22.6, 0)
        ARRDATA(1, 3, 3) = Array(312, 85.6, 80.8, 80.4, 83.3, 0)
        ARRDATA(1, 3, 4) = Array(13, 90.2, 88.3, 76.6, 77.1, 1)
        ARRDATA(1, 3, 5) = Array(35, 80#, 78.4, 67.1, 69.7, 1)
        ARRDATA(1, 4, 0) = Array(536, 77.8, 61.9, 60.1, 68.7, 0)
        ARRDATA(1, 4, 1) = Array(351, 53.6, 41#, 25.4, 32.5, 0)
        ARRDATA(1, 4, 2) = Array(375, 37.1, 28.8, 14.1, 19.5, 0)
        ARRDATA(1, 4, 3) = Array(96, 71#, 59.6, 55.2, 61.4, 1)
        ARRDATA(1, 4, 4) = Array(12, 60#, 48.1, 40.4, 48.5, 1)
        ARRDATA(1, 4, 5) = Array(32, 56.2, 45.3, 38.1, 45#, 1)
        ARRDATA(1, 5, 0) = Array(348, 85.1, 40.5, 40.5, 66.4, 0)
        ARRDATA(1, 5, 1) = Array(195, 69.7, 30.3, 27.2, 41#, 0)
        ARRDATA(1, 5, 2) = Array(1664, 28.8, 13.8, 10.2, 16.5, 0)
        ARRDATA(1, 5, 3) = Array(429, 81.6, 39.6, 39.6, 85.1, 0)
        ARRDATA(1, 5, 4) = Array(416, 56.7, 18.5, 18.5, 64.9, 0)
        ARRDATA(1, 5, 5) = Array(5110, 11.9, 3.9, 3.7, 19.6, 0)
        ARRDATA(2, 0, 0) = Array(13720, 92.7, 89.9, 83.9, 86.9, 0)
        ARRDATA(2, 0, 1) = Array(1133, 54.1, 50.9, 29.8, 38.2, 0)
        ARRDATA(2, 0, 2) = Array(1225, 29.1, 27.2, 17.6, 28.8, 0)
        ARRDATA(2, 0, 3) = Array(3702, 83.4, 74.7, 74.1, 88.9, 0)
        ARRDATA(2, 0, 4) = Array(500, 49.2, 46.4, 45#, 68.2, 0)
        ARRDATA(2, 0, 5) = Array(628, 34.2, 32.2, 27.1, 45.9, 0)
        ARRDATA(2, 1, 0) = Array(99, 64.2, 36.8, 36.1, 52.7, 1)
        ARRDATA(2, 1, 1) = Array(36, 54.2, 30.4, 29.3, 45.5, 1)
        ARRDATA(2, 1, 2) = Array(383, 32.9, 16.2, 11#, 15.1, 0)
        ARRDATA(2, 1, 3) = Array(819, 83.5, 49.3, 49.3, 86.7, 0)
        ARRDATA(2, 1, 4) = Array(650, 55.5, 35.7, 35.7, 70.8, 0)
        ARRDATA(2, 1, 5) = Array(1339, 36.2, 21.8, 19.8, 32.4, 0)
        ARRDATA(2, 2, 0) = Array(116, 77.6, 31#, 31#, 71.6, 0)
        ARRDATA(2, 2, 1) = Array(32, 21.7, 4.6, 4.5, 28.5, 1)
        ARRDATA(2, 2, 2) = Array(909, 23.1, 11.4, 7.9, 15.5, 0)
        ARRDATA(2, 2, 3) = Array(2569, 79.3, 27.3, 27.3, 90.6, 0)
        ARRDATA(2, 2, 4) = Array(12286, 41#, 7.6, 7.6, 82.2, 0)
        ARRDATA(2, 2, 5) = Array(84198, 6.2, 1.5, 1.5, 23.8, 0)
        ARRDATA(2, 3, 0) = Array(140418, 77.5, 77.1, 74.2, 90.2, 0)
        ARRDATA(2, 3, 1) = Array(10521, 31.2, 31.1, 21.6, 42.9, 0)
        ARRDATA(2, 3, 2) = Array(2138, 17.4, 17.3, 12.7, 31.3, 0)
        ARRDATA(2, 3, 3) = Array(3840, 77#, 73.9, 73.8, 94.7, 0)
        ARRDATA(2, 3, 4) = Array(138, 32.6, 32.6, 32.6, 65.2, 0)
        ARRDATA(2, 3, 5) = Array(257, 23.7, 23.3, 22.6, 58.8, 0)
        ARRDATA(2, 4, 0) = Array(106168, 35.4, 34.1, 33.9, 85.5, 0)
        ARRDATA(2, 4, 1) = Array(16759, 13.5, 13.2, 11.1, 40.7, 0)
        ARRDATA(2, 4, 2) = Array(6777, 8.6, 8.5, 7#, 30.5, 0)
        ARRDATA(2, 4, 3) = Array(10625, 49.7, 46.7, 46.7, 93.4, 0)
        ARRDATA(2, 4, 4) = Array(422, 25.1, 24.4, 24.4, 71.6, 0)
        ARRDATA(2, 4, 5) = Array(940, 12.8, 12.4, 11.8, 52.9, 0)
        ARRDATA(2, 5, 0) = Array(45657, 21.7, 14.4, 14.4, 76.9, 0)
        ARRDATA(2, 5, 1) = Array(10794, 10#, 7.4, 7.3, 41.8, 0)
        ARRDATA(2, 5, 2) = Array(34421, 5.7, 4.3, 3.9, 24.4, 0)
        ARRDATA(2, 5, 3) = Array(88045, 26.2, 13.7, 13.7, 89.1, 0)
        ARRDATA(2, 5, 4) = Array(137524, 9.2, 3#, 3#, 78.6, 0)
        ARRDATA(2, 5, 5) = Array(569447, 1.8, 0.8, 0.8, 28#, 0)
        ARRDATA(3, 0, 0) = Array(543133, 98.3, 97.2, 80.8, 85.9, 0)
        ARRDATA(3, 0, 1) = Array(126984, 90.5, 87.5, 30#, 40#, 0)
        ARRDATA(3, 0, 2) = Array(86920, 75.4, 62.8, 16.4, 24.5, 0)
        ARRDATA(3, 0, 3) = Array(30643, 95.3, 84.9, 79.6, 87.8, 0)
        ARRDATA(3, 0, 4) = Array(10147, 91#, 72.7, 63.4, 74.6, 0)
        ARRDATA(3, 0, 5) = Array(34261, 81.2, 61.1, 30.3, 40.8, 0)
        ARRDATA(3, 1, 0) = Array(986, 88.7, 36.3, 36.3, 53.7, 0)
        ARRDATA(3, 1, 1) = Array(398, 79.1, 30.2, 28.6, 33.7, 0)
        ARRDATA(3, 1, 2) = Array(13529, 54.6, 19.2, 9.4, 14.4, 0)
        ARRDATA(3, 1, 3) = Array(5058, 92.2, 47.6, 47.6, 84.3, 0)
        ARRDATA(3, 1, 4) = Array(14220, 86.9, 33.5, 33.5, 73#, 0)
        ARRDATA(3, 1, 5) = Array(97883, 68.9, 18.1, 13.3, 26.9, 0)
        ARRDATA(3, 2, 0) = Array(392, 73.7, 29.3, 29.3, 53.6, 0)
        ARRDATA(3, 2, 1) = Array(201, 68.7, 26.4, 25.9, 33.8, 0)
        ARRDATA(3, 2, 2) = Array(4700, 25.6, 10#, 7.6, 14#, 0)
        ARRDATA(3, 2, 3) = Array(1980, 81#, 27.2, 27.2, 83.3, 0)
        ARRDATA(3, 2, 4) = Array(10298, 63#, 11.9, 11.9, 75.1, 0)
        ARRDATA(3, 2, 5) = Array(142731, 21#, 2.5, 2.4, 18.3, 0)
        ARRDATA(3, 3, 0) = Array(78516, 92.9, 92.4, 84.1, 87.2, 0)
        ARRDATA(3, 3, 1) = Array(10276, 59.3, 58.6, 27.5, 36.1, 0)
        ARRDATA(3, 3, 2) = Array(2504, 24.9, 23.9, 11.9, 21#, 0)
        ARRDATA(3, 3, 3) = Array(861, 80.6, 77#, 76.7, 85.9, 0)
        ARRDATA(3, 3, 4) = Array(35, 75.6, 74.5, 64.9, 70.9, 1)
        ARRDATA(3, 3, 5) = Array(105, 39#, 38.1, 28.6, 37.1, 0)
        ARRDATA(3, 4, 0) = Array(1948, 67.8, 59.7, 57#, 69#, 0)
        ARRDATA(3, 4, 1) = Array(919, 40.7, 36.1, 25.6, 34.4, 0)
        ARRDATA(3, 4, 2) = Array(1225, 18.4, 16.7, 11.5, 19.8, 0)
        ARRDATA(3, 4, 3) = Array(370, 70.5, 63.8, 63.5, 80.8, 0)
        ARRDATA(3, 4, 4) = Array(40, 46.5, 42#, 38.7, 53.7, 1)
        ARRDATA(3, 4, 5) = Array(150, 26.7, 26#, 24#, 39.3, 0)
        ARRDATA(3, 5, 0) = Array(982, 66#, 33.6, 33.6, 60.4, 0)
        ARRDATA(3, 5, 1) = Array(505, 46.7, 24.8, 23.6, 34.3, 0)
        ARRDATA(3, 5, 2) = Array(4115, 15.7, 10.3, 8.4, 16.3, 0)
        ARRDATA(3, 5, 3) = Array(1302, 69.4, 36.3, 36.3, 82.4, 0)
        ARRDATA(3, 5, 4) = Array(1264, 44.4, 18.5, 18.5, 67.8, 0)
        ARRDATA(3, 5, 5) = Array(14491, 7.8, 3.7, 3.6, 18.4, 0)
        ARRDATA(4, 0, 0) = Array(225124, 73.3, 73#, 68.5, 85#, 0)
        ARRDATA(4, 0, 1) = Array(39506, 30#, 29.9, 19.9, 39#, 0)
        ARRDATA(4, 0, 2) = Array(34735, 12.8, 12.6, 8.9, 25#, 0)
        ARRDATA(4, 0, 3) = Array(26309, 51.7, 49.9, 49.5, 87.1, 0)
        ARRDATA(4, 0, 4) = Array(6165, 28.1, 26.8, 26.1, 70.5, 0)
        ARRDATA(4, 0, 5) = Array(14429, 15#, 14.7, 13.2, 41.5, 0)
        ARRDATA(4, 1, 0) = Array(696, 57.9, 23.6, 23.6, 34.1, 0)
        ARRDATA(4, 1, 1) = Array(266, 32.3, 16.2, 16.2, 26.3, 0)
        ARRDATA(4, 1, 2) = Array(5839, 11.2, 8.6, 6.6, 15.4, 0)
        ARRDATA(4, 1, 3) = Array(4368, 48.9, 35.4, 35.4, 81.5, 0)
        ARRDATA(4, 1, 4) = Array(8189, 31.4, 21.7, 21.7, 70.7, 0)
        ARRDATA(4, 1, 5) = Array(29475, 11.6, 9.3, 8.6, 29.8, 0)
        ARRDATA(4, 2, 0) = Array(567, 33.5, 18.2, 18.2, 48#, 0)
        ARRDATA(4, 2, 1) = Array(234, 24.4, 17.9, 17.5, 32.1, 0)
        ARRDATA(4, 2, 2) = Array(6911, 6.9, 5.3, 4.4, 12.6, 0)
        ARRDATA(4, 2, 3) = Array(6053, 38.1, 20.9, 20.9, 82.9, 0)
        ARRDATA(4, 2, 4) = Array(30181, 15.8, 7#, 7#, 73.1, 0)
        ARRDATA(4, 2, 5) = Array(262425, 2.6, 1.4, 1.4, 20.3, 0)
        ARRDATA(4, 3, 0) = Array(840612, 33.7, 33.6, 33#, 88.1, 0)
        ARRDATA(4, 3, 1) = Array(91467, 8.9, 8.9, 7.1, 38.8, 0)
        ARRDATA(4, 3, 2) = Array(23043, 3.8, 3.8, 3.4, 27#, 0)
        ARRDATA(4, 3, 3) = Array(17842, 26.7, 26.5, 26.5, 91.7, 0)
        ARRDATA(4, 3, 4) = Array(1052, 6.3, 6.3, 6.2, 72#, 0)
        ARRDATA(4, 3, 5) = Array(2642, 3.1, 3.1, 3.1, 49.4, 0)
        ARRDATA(4, 4, 0) = Array(761773, 1.9, 1.9, 1.9, 84.1, 0)
        ARRDATA(4, 4, 1) = Array(122721, 1#, 1#, 1#, 38.6, 0)
        ARRDATA(4, 4, 2) = Array(58732, 0.9, 0.9, 0.9, 26.7, 0)
        ARRDATA(4, 4, 3) = Array(64561, 5.4, 5.3, 5.3, 91.6, 0)
        ARRDATA(4, 4, 4) = Array(3729, 1.7, 1.7, 1.7, 71.1, 0)
        ARRDATA(4, 4, 5) = Array(8504, 1.4, 1.3, 1.3, 47.1, 0)
        ARRDATA(4, 5, 0) = Array(260251, 1.1, 0.8, 0.8, 75.2, 0)
        ARRDATA(4, 5, 1) = Array(62595, 0.8, 0.6, 0.6, 40.3, 0)
        ARRDATA(4, 5, 2) = Array(201933, 0.6, 0.6, 0.5, 22.2, 0)
        ARRDATA(4, 5, 3) = Array(421283, 1.7, 1.3, 1.3, 87.1, 0)
        ARRDATA(4, 5, 4) = Array(654977, 0.6, 0.4, 0.4, 74.8, 0)
        ARRDATA(4, 5, 5) = Array(2997237, 0.2, 0.1, 0.1, 24#, 0)
        ARRDATA(5, 0, 0) = Array(5816, 86.7, 84.7, 79.7, 81.4, 0)
        ARRDATA(5, 0, 1) = Array(523, 45.9, 43.6, 28.3, 39.4, 0)
        ARRDATA(5, 0, 2) = Array(557, 24.6, 20.8, 13.3, 25.5, 0)
        ARRDATA(5, 0, 3) = Array(1474, 71.8, 66.8, 66.5, 83.7, 0)
        ARRDATA(5, 0, 4) = Array(225, 44.9, 39.1, 37.8, 64.4, 0)
        ARRDATA(5, 0, 5) = Array(272, 23.2, 22.4, 19.5, 47.4, 0)
        ARRDATA(5, 1, 0) = Array(61, 51.8, 27.3, 26.7, 33.2, 1)
        ARRDATA(5, 1, 1) = Array(9, 47.2, 24.7, 23.8, 40.8, 1)
        ARRDATA(5, 1, 2) = Array(211, 34.6, 16.1, 11.8, 12.8, 0)
        ARRDATA(5, 1, 3) = Array(292, 66.1, 44.2, 44.2, 78.8, 0)
        ARRDATA(5, 1, 4) = Array(270, 50.4, 30.7, 30.7, 55.2, 0)
        ARRDATA(5, 1, 5) = Array(478, 29.1, 16.3, 15.5, 32.8, 0)
        ARRDATA(5, 2, 0) = Array(63, 26#, 14.3, 14.3, 30.1, 1)
        ARRDATA(5, 2, 1) = Array(20, 9.4, 4.5, 4.4, 22.5, 1)
        ARRDATA(5, 2, 2) = Array(643, 19.4, 13.2, 10.3, 14.6, 0)
        ARRDATA(5, 2, 3) = Array(755, 57.4, 27.3, 27.3, 83.8, 0)
        ARRDATA(5, 2, 4) = Array(3368, 23.4, 8.8, 8.8, 75#, 0)
        ARRDATA(5, 2, 5) = Array(29453, 3.8, 1.8, 1.8, 20.3, 0)
        ARRDATA(5, 3, 0) = Array(95762, 49.9, 49.8, 49.1, 91.1, 0)
        ARRDATA(5, 3, 1) = Array(5585, 13.8, 13.8, 11.2, 43.4, 0)
        ARRDATA(5, 3, 2) = Array(1075, 7.1, 7.1, 6#, 31.4, 0)
        ARRDATA(5, 3, 3) = Array(2316, 56.9, 56.2, 56.1, 92.2, 0)
        ARRDATA(5, 3, 4) = Array(66, 37.1, 37.1, 36.6, 83.1, 1)
        ARRDATA(5, 3, 5) = Array(149, 10.1, 10.1, 9.4, 56.4, 0)
        ARRDATA(5, 4, 0) = Array(161508, 5.4, 5.3, 5.3, 88#, 0)
        ARRDATA(5, 4, 1) = Array(17852, 1.7, 1.7, 1.7, 42.6, 0)
        ARRDATA(5, 4, 2) = Array(5734, 1.6, 1.6, 1.5, 30.8, 0)
        ARRDATA(5, 4, 3) = Array(11770, 14.9, 14.7, 14.7, 93.3, 0)
        ARRDATA(5, 4, 4) = Array(385, 4.4, 4.4, 4.4, 75.6, 0)
        ARRDATA(5, 4, 5) = Array(686, 4.1, 4.1, 3.8, 51.5, 0)
        ARRDATA(5, 5, 0) = Array(76788, 1.6, 1.3, 1.3, 79.7, 0)
        ARRDATA(5, 5, 1) = Array(14768, 0.8, 0.7, 0.7, 43.8, 0)
        ARRDATA(5, 5, 2) = Array(37734, 0.9, 0.8, 0.8, 25.1, 0)
        ARRDATA(5, 5, 3) = Array(136083, 2.9, 2.2, 2.2, 89.7, 0)
        ARRDATA(5, 5, 4) = Array(234528, 0.8, 0.5, 0.5, 79.6, 0)
        ARRDATA(5, 5, 5) = Array(921600, 0.2, 0.1, 0.1, 27.5, 0)
    End If
    日冲取数据 = ARRDATA(iEF, iCD, iAB)
End Function

'========================================================================================
'查日冲H2分 — 从CSV查表获取下日DSHR>2（按市板）
'文件路径：_产出物\_工具\vba日冲策分表_市板.csv
'格式: DXEF,DXCD,DXAB,市板,样本,→ZE>0,...,下日DSHR>2,均HR,中位HR
'兼容市板：Qim/Qit → Qimit
'========================================================================================
Public Function IQQQ跨码工具_查日冲H2分(ByVal sDXEF As String, ByVal sDXCD As String, ByVal sDXAB As String, ByVal s市板 As String) As Double
    Static 概率典 As Object
    Static 已加载 As Boolean
    Dim 文件号 As Integer, 行内容 As String, 字段 As Variant
    Dim 键 As String, 市板查 As String

    If Not 已加载 Then
        Set 概率典 = CreateObject("Scripting.Dictionary")
        文件号 = FreeFile
        Open ThisWorkbook.Path & "\_产出物\_工具\vba日冲策分表_市板.csv" For Input As #文件号
            Line Input #文件号, 行内容  ' 跳过表头
            Do While Not EOF(文件号)
                Line Input #文件号, 行内容
                字段 = Split(行内容, ",")
                If UBound(字段) >= 12 Then
                    键 = 字段(0) & "|" & 字段(1) & "|" & 字段(2) & "|" & 字段(3)
                    概率典(键) = CDbl(字段(10))  ' 下日DSHR>2（第10列）
                End If
            Loop
        Close #文件号
        已加载 = True
    End If

    ' 兼容市板：Qim/Qit → Qimit
    市板查 = s市板
    If 市板查 = "Qim" Or 市板查 = "Qit" Then 市板查 = "Qimit"

    键 = sDXEF & "|" & sDXCD & "|" & sDXAB & "|" & 市板查
    If 概率典.Exists(键) Then
        IQQQ跨码工具_查日冲H2分 = 概率典(键)
    Else
        ' 市板查不到则回退全量
        键 = sDXEF & "|" & sDXCD & "|" & sDXAB & "|全量"
        If 概率典.Exists(键) Then IQQQ跨码工具_查日冲H2分 = 概率典(键) Else IQQQ跨码工具_查日冲H2分 = 0
    End If
End Function
