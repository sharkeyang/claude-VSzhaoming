Attribute VB_Name = "IQQQ跨码_D据擎4跨码管理"
'Option Explicit
'========================================================================================
'跨码管理模块
'从神谕中剥离的仓位管理 + 日段统计 + 组合管理检查
'由神谕在循环内调用（仓位管理、日段统计），或由主控流程调用（组合管理检查）
'========================================================================================
'仅输出组合管理检查（A2），不跑其他表
'========================================================================================
Sub IQQQ展擎主前调_组合管理仅A2()
    Dim 谕组 As Variant
    Dim 计数全息 As Integer
    计数全息 = IQQQ跨码据擎_数程生成全息(谕组, 常花中股, 实结类型:="sSCC")
    If 计数全息 = 0 Then Exit Sub
    Dim MSG As String
    MSG = IQQQ展擎筛程至A2组合管理检查(谕组, 花列甲道, 常花中股, ThisWorkbook)
    MsgBox MSG, vbOKOnly, "组合管理检查"
    Erase 谕组
End Sub
'========================================================================================
'主入口：跨码管理（仓位管理 + 日段统计）
'########################################################################################
'########################################################################################
'##############################  仓位管理 单行  ##########################################
'########################################################################################
'########################################################################################
Public Function IQQQ跨码据擎_数程生成跨码管理1仓位管理( _
          ByRef 谕组 As Variant _
        , ByRef 组结算 As Variant _
        , ByVal X As Integer _
        , Optional ByVal 基列 As Integer = 花列甲道 _
        ) As Integer
'========================================================================================
    Dim 基位日类 As Integer
    基位日类 = 基列 - 1
    Dim 基位周类 As Integer
    基位周类 = 基列 - 1 + 花宽单道 * 1
    Dim CIDL As String
    CIDL = 组结算(X, 基位日类 + 位os代码)
    If UBCID是代码(CIDL) = False Then Exit Function
    '========================================================================================
    '获取仓数量（按位qt仓主选择福/彦）
    '========================================================================================
    Dim 值仓持数总 As Double, 值仓总额总 As Double
    Dim 值仓福数 As Double, 值仓福本 As Double
    Dim 值仓彦数 As Double, 值仓彦本 As Double
    值仓持数总 = 0: 值仓总额总 = 0
    值仓福数 = 0: 值仓福本 = 0
    值仓彦数 = 0: 值仓彦本 = 0
    '根据位qt仓主判断用哪个账户
    If 谕组(X, 位qt仓主) = 常仓名宝福 Then
        '福仓：只读福仓列
        If InStr(组结算(X, 位列花天仓宝福), ",") > 0 Then
            值仓福数 = Val(Left$(组结算(X, 位列花天仓宝福), InStr(组结算(X, 位列花天仓宝福), ",") - 1))
            值仓福本 = Val(Mid$(组结算(X, 位列花天仓宝福), InStr(组结算(X, 位列花天仓宝福), ",") + 1))
        End If
    ElseIf 谕组(X, 位qt仓主) = 常仓名宝彦 Then
        '彦仓：只读彦仓列
        If InStr(组结算(X, 位列花天仓宝彦), ",") > 0 Then
            值仓彦数 = Val(Left$(组结算(X, 位列花天仓宝彦), InStr(组结算(X, 位列花天仓宝彦), ",") - 1))
            值仓彦本 = Val(Mid$(组结算(X, 位列花天仓宝彦), InStr(组结算(X, 位列花天仓宝彦), ",") + 1))
        End If
    Else
        '位qt仓主为空，不做仓位计算
        Exit Function
    End If
    '合并（累加持仓数，加权平均成本）
    值仓持数总 = 值仓福数 + 值仓彦数
    值仓总额总 = 值仓福数 * 值仓福本 + 值仓彦数 * 值仓彦本
    Dim 值仓成本 As Double
    If 值仓持数总 > 0 Then
        谕组(X, 位谕of仓持数) = 值仓持数总
        值仓成本 = 值仓总额总 / 值仓持数总
    Else
        谕组(X, 位谕of仓持数) = 0
        值仓成本 = 0
    End If
    Dim 值仓持数 As Double
    值仓持数 = 谕组(X, 位谕of仓持数) / 100
    '================================================================================
    '对于持仓：只有【CID是代码】且【持仓数量>0】进行考虑
    '================================================================================
    If 值仓持数 > 0 Then
            '========================================================================
            '重新计算金额相关：市值、收益
            '========================================================================
            Dim 值今收 As Double, 值今高 As Double, 值今低 As Double, 值前收 As Double
            Dim 周类JC As Double
            值今收 = 组结算(X, 基位日类 + 位os结收)
            值今高 = 组结算(X, 基位日类 + 位os结高)
            值今低 = 组结算(X, 基位日类 + 位os结低)
            值前收 = 组结算(X, 基位日类 + 位os前收)
            周类JC = 组结算(X, 基位周类 + 位osJC)
            Dim 值仓持额 As Double
            Dim 值仓赚收 As Double, 值仓赚高 As Double, 值仓赚低 As Double
            Dim 值仓肉垫 As Double
            值仓持额 = 0
            值仓赚收 = 0
            值仓赚高 = 0
            值仓赚低 = 0
            If UBCID是中股票(CIDL) = True Or UBCID是中股基(CIDL) = True Then
                值仓持额 = Round(100 * 值仓持数 * 值今收 / 1000, 1)
                值仓赚收 = Round(100 * 值仓持数 * (值今收 - 值前收), 0)
                值仓赚高 = Round(100 * 值仓持数 * (值今高 - 值前收), 0)
                值仓赚低 = Round(100 * 值仓持数 * (值今低 - 值前收), 0)
                值仓肉垫 = Round(100 * 值仓持数 * (值今收 - 周类JC), 0)
            ElseIf UBCID是港股票(CIDL) = True Then
                值仓持额 = Round(常汇率港币 * 100 * 值仓持数 * 值今收 / 1000, 1)
                值仓赚收 = Round(常汇率港币 * 100 * 值仓持数 * (值今收 - 值前收), 0)
                值仓赚高 = Round(常汇率港币 * 100 * 值仓持数 * (值今高 - 值前收), 0)
                值仓赚低 = Round(常汇率港币 * 100 * 值仓持数 * (值今低 - 值前收), 0)
                值仓肉垫 = Round(常汇率港币 * 100 * 值仓持数 * (值今收 - 周类JC), 0)
            End If
            '计算仓赚
            谕组(X, 位谕of仓成本) = 值仓成本
            谕组(X, 位谕of仓持额) = 值仓持额
            谕组(X, 位谕of仓赚收) = 值仓赚收
            谕组(X, 位谕of仓赚高) = 值仓赚高
            谕组(X, 位谕of仓赚低) = 值仓赚低
            谕组(X, 位谕of仓赚损) = IIf(值仓赚高 > 0, 值仓赚收 - 值仓赚高, 0)
            谕组(X, 位谕of仓肉垫) = 值仓肉垫
            '========================================================================
            '计算盈亏比例
            '========================================================================
            Dim 值仓盈比 As Double
            If 值仓成本 > 0 Then
                值仓盈比 = Round(值今收 / 值仓成本 - 1, 2)
            Else
                值仓盈比 = 1
            End If
            谕组(X, 位谕of仓盈比) = Format(值仓盈比, "0%")
            '========================================================================
            '定义操盘类型与盯盘类型
            '========================================================================
                '【类别】停牌
                If 谕组(X, 位qt停牌) = "S" Then
                        谕组(X, 位谕of仓操类) = "操盘停牌"
                '【类别】ETF类
                ElseIf UBCID是中股基(CIDL) = True Then
                        谕组(X, 位谕of仓操类) = "操盘ETF类"
                        谕组(X, 位谕of仓限总) = IIf(谕组(X, 位谕of仓限倍) > 0, CInt(10000 / 100 / 值今收), 0)
                '--------------------------------------------------------------------
                '【类别】池金
                ElseIf 谕组(X, 位qt在池) = 常池名金 Then
                        谕组(X, 位谕of仓操类) = "操盘在池"
                        谕组(X, 位谕of仓限单) = (常值仓限底仓额 / 100 / 值今收)
                        谕组(X, 位谕of仓限总) = CInt(谕组(X, 位谕of仓限单) * 谕组(X, 位谕of仓限倍))
                '【类别】池银 池铜
                ElseIf 谕组(X, 位qt在池) = 常池名银 Or 谕组(X, 位qt在池) = 常池名铜 Then
                        谕组(X, 位谕of仓操类) = "操盘在池"
                        谕组(X, 位谕of仓限单) = (常值仓限底仓额 / 100 / 值今收)
                        谕组(X, 位谕of仓限总) = CInt(谕组(X, 位谕of仓限单) * 谕组(X, 位谕of仓限倍))
                '--------------------------------------------------------------------
                '【类别】操盘日类：快进快出
                Else
                        谕组(X, 位谕of仓操类) = "操盘快"
                        谕组(X, 位谕of仓限单) = (常值仓限底仓额 / 100 / 值今收)
                        谕组(X, 位谕of仓限总) = CInt(谕组(X, 位谕of仓限单) * 谕组(X, 位谕of仓限倍))
                End If
            '========================================================================
            '计算仓位比
            '========================================================================
            谕组(X, 位qt盯盘类别) = ""
            Dim 值仓位比 As Double
            If VBA.IsNumeric(谕组(X, 位谕of仓限总)) = True Then
                '--------------------------------------------------------------------
                If Left$(谕组(X, 位谕of周层界), 1) = "_" Then
                        谕组(X, 位qt盯盘类别) = "X旨"
                        谕组(X, 位谕of仓位比) = "仓限禁旨"
                ElseIf 谕组(X, 位谕of仓限总) = 0 Then
                        谕组(X, 位qt盯盘类别) = "O无"
                        谕组(X, 位谕of仓位比) = "仓限为0"
                Else
                        值仓位比 = Round(值仓持数 / 谕组(X, 位谕of仓限总), 1)
                        谕组(X, 位谕of仓位比) = IIf(值仓位比 > 1, 值仓位比 & "倍", 值仓位比)
                        If 谕组(X, 位谕of仓持额) * 1000 <= 常值仓限底仓额 Then
                            谕组(X, 位qt盯盘类别) = "H恒"
                        Else
                            谕组(X, 位qt盯盘类别) = "K狙"
                        End If
                End If
                '--------------------------------------------------------------------
                If InStr(谕组(X, 位谕of周层界), "_") > 0 Then
                        谕组(X, 位qt盯盘类别) = 谕组(X, 位qt盯盘类别) & "X周"
                ElseIf 谕组(X, 位谕of仓持额) * 1000 >= 常值仓限底仓额 * 2 Then
                        谕组(X, 位qt盯盘类别) = 谕组(X, 位qt盯盘类别) & "H重"
                ElseIf VBA.IsNumeric(值仓位比) And 值仓位比 > 1 Then
                        谕组(X, 位qt盯盘类别) = 谕组(X, 位qt盯盘类别) & "C超"
                End If
                If 谕组(X, 位谕of仓操类) = "操盘ETF类" Then
                        谕组(X, 位qt盯盘类别) = "ETF." & 谕组(X, 位qt盯盘类别)
                End If
                '--------------------------------------------------------------------
                        If Weekday(Date, vbMonday) <= 5 And (Time >= "09:29:00" And Time <= "15:00:00") Then
                            If 谕组(X, 位qt今高幅) >= 3 And 谕组(X, 位谕of日波上身) < 50 Then
                                谕组(X, 位qt盯盘类别) = 谕组(X, 位qt盯盘类别) & "_落"
                            End If
                        End If
            End If
            '========================================================================
            '周类操盘策略
            '========================================================================
                    谕组(X, 位谕of仓操作) = ""
                    If 谕组(X, 位谕of仓限总) = 0 Then
                            谕组(X, 位谕of仓操作) = "清" & 值仓持数 & "手"
                    Else
                            If 值仓位比 > 1 Then 谕组(X, 位谕of仓操作) = "削" & (值仓持数 - 谕组(X, 位谕of仓限总)) & "手"
                    End If
    End If
    IQQQ跨码据擎_数程生成跨码管理1仓位管理 = 1
End Function
'##############################  日段统计 单行  ##########################################
'########################################################################################
'由神谕在循环内调用。从组结算统时区域复制日段仨/佰/十属性到谕组，





'========================================================================================
' IQQQ展擎筛程至A2组合管理检查 — 组合管理体检报告
' 由主控流程在神谕计算完成后调用，只读取不写入。
' 输出：Sheet 体检表（概览、行业分布、策略分布、风控检查、持仓明细）
' 读取谕组：位qt代码、位谕of仓持数、位谕of仓持额、位谕of仓位比、位谕of月基策略等
' 读取花册：福仓/彦仓持仓数据用于双账户分解
'========================================================================================
Public Function IQQQ展擎筛程至A2组合管理检查( _
          ByRef 谕组 As Variant _
        , ByVal 基列 As Integer _
        , ByVal 指定花册 As String _
        , ByRef WB As Workbook _
        ) As String
'========================================================================================
    Dim MSG As String
    Dim X As Integer
    Dim CIDL As String
    Dim 行号 As Integer
    Dim 末行 As Integer
    '--- 花册字典 ---
    Dim WS花册 As Worksheet
    Dim 典码位花册 As New Dictionary
    '--- 概览统计 ---
    Dim 持票数 As Integer: 持票数 = 0
    Dim 总持仓数 As Double: 总持仓数 = 0
    Dim 总持仓额 As Double: 总持仓额 = 0
    Dim 单票额 As Double
    '--- 双账户统计 ---
    Dim 福仓数 As Double, 彦仓数 As Double
    Dim 福仓字 As String, 彦仓字 As String
    Dim 福仓额 As Double: 福仓额 = 0
    Dim 彦仓额 As Double: 彦仓额 = 0
    Dim 福票数 As Integer: 福票数 = 0
    Dim 彦票数 As Integer: 彦票数 = 0
    '--- 行业统计 ---
    Dim 行业 As Variant
    Dim 行业额 As Double
    Dim 行业典集 As New Dictionary
    Dim 行业轮动典集 As New Dictionary
    Dim 轮动 As String
    '--- 策略统计 ---
    Dim 策略典集 As New Dictionary
    Dim 总命分 As Double: 总命分 = 0
    Dim 总策分 As Double: 总策分 = 0
    Dim 命分票数 As Integer: 命分票数 = 0
    Dim 策分票数 As Integer: 策分票数 = 0
    Dim 月基策略 As Variant
    '--- 持仓明细 ---
    Dim 明细行 As Integer
    '--- 风控 ---
    Dim 超限名单 As String
    Dim 单票超限 As String
    '--- 仓位分布 ---
    Dim 仓低数 As Integer: 仓低数 = 0
    Dim 仓中数 As Integer: 仓中数 = 0
    Dim 仓满数 As Integer: 仓满数 = 0
    Dim 仓超数 As Integer: 仓超数 = 0
    Dim 仓值 As Variant
    '--- 资金账户 ---
    Dim 福现金 As Double: 福现金 = 0
    Dim 彦现金 As Double: 彦现金 = 0
    Dim 福总资 As Double: 福总资 = 0
    Dim 彦总资 As Double: 彦总资 = 0
    '--- 策略违规 ---
    Dim 策略违规 As String
    Dim 命分 As Variant, 策分 As Variant
    Dim i As Integer
    '--- 集中度 ---
    Dim 前N仓额(1 To 10) As Double
    Dim 前N仓名(1 To 10) As String
    Dim 前N仓代(1 To 10) As String
    Dim 仓额排名 As Double, 仓名排名 As String
    Dim j As Integer
    Dim k As Integer
    '--- 仓周类上限 ---
    Dim 仓周类 As String
    Dim 仓周上限 As Double
    Dim 组合占比 As Double
    Dim 仓周违规 As String
    '--- 行业指数映射 ---
    Dim 行业指数映射 As Dictionary
    Dim 行业指数典集 As New Dictionary  '行业→Array(名称, CIDL, 类型)
    Dim 典指位 As New Dictionary  'CIDL→谕组行号
    Dim 指数信息 As Variant
    Dim 行号指 As Variant
'========================================================================================
'建页
'========================================================================================
    Dim WSTO As Worksheet
    Dim 表名 As String
    表名 = 常簿缀选临 & "A2组合管理"
    Call PBASE格程工具_表操工表新增(WSTO, 表名, WB:=WB, 基色底:=常色六碧)
'========================================================================================
'花册链接
'========================================================================================
    If STBASE外簿工具_花册链接(WS花册, 指定花册) = False Then
        IQQQ展擎筛程至A2组合管理检查 = "【组合管理】花册链接失败" & vbCrLf
        Exit Function
    End If
    '--- 建立 CIDL → 行号 字典 ---
    For 行号 = 2 To WS花册.UsedRange.Rows.Count
        CIDL = Trim(WS花册.Cells(行号, 位列花天CIDL).Value)
        If CIDL <> "" Then
            If 典码位花册.Exists(CIDL) = False Then
                典码位花册.Add CIDL, 行号
            End If
        End If
    Next
'========================================================================================
'读取资金账户
'========================================================================================
    On Error Resume Next
    福现金 = Evaluate("ZF可用资金") / 1000
    彦现金 = Evaluate("ZJ可用资金") / 1000
    福总资 = Evaluate("ZF总资产") / 1000
    彦总资 = Evaluate("ZJ总资产") / 1000
    On Error GoTo 0
    '========================================================================================
    '行业指数映射字典 + CIDL→行号索引
    '========================================================================================
    Set 行业指数映射 = UTL族群引擎_行业指数映射()
    For X = LBound(谕组, 1) To UBound(谕组, 1)
        CIDL = 谕组(X, 位qt代码)
        If CIDL <> "" Then
            If 典指位.Exists(CIDL) = False Then 典指位.Add CIDL, X
        End If
    Next
'========================================================================================
'遍历谕组，统计持仓
'========================================================================================
    For X = LBound(谕组, 1) To UBound(谕组, 1)
            CIDL = 谕组(X, 位qt代码)
            '--- 从花册读取持仓数据 ---
            福仓数 = 0: 彦仓数 = 0
            If 典码位花册.Exists(CIDL) Then
                行号 = 典码位花册(CIDL)
                福仓字 = Trim(WS花册.Cells(行号, 位列花天仓宝福).Value)
                彦仓字 = Trim(WS花册.Cells(行号, 位列花天仓宝彦).Value)
                If InStr(福仓字, ",") > 0 Then 福仓数 = Val(Left$(福仓字, InStr(福仓字, ",") - 1))
                If InStr(彦仓字, ",") > 0 Then 彦仓数 = Val(Left$(彦仓字, InStr(彦仓字, ",") - 1))
            End If
            '--- 有持仓时才统计 ---
            If 福仓数 > 0 Or 彦仓数 > 0 Then
            Dim 值持仓数 As Double
            值持仓数 = 福仓数 + 彦仓数
            Dim 值今收 As Double
            值今收 = 谕组(X, 位qt今收)
            If Not VBA.IsNumeric(值今收) Then 值今收 = 0
            单票额 = Round(100 * 值持仓数 / 100 * 值今收 / 1000, 1)
            '--- 基础统计 ---
            持票数 = 持票数 + 1
            总持仓数 = 总持仓数 + 值持仓数
            总持仓额 = 总持仓额 + 单票额
            If 福仓数 > 0 Then
                福票数 = 福票数 + 1
                福仓额 = 福仓额 + 单票额 * 福仓数 / (福仓数 + 彦仓数)
            End If
            If 彦仓数 > 0 Then
                彦票数 = 彦票数 + 1
                彦仓额 = 彦仓额 + 单票额 * 彦仓数 / (福仓数 + 彦仓数)
            End If
            '--- 行业统计 ---
            行业 = 谕组(X, 位qt行益)
            If 行业 <> "" Then
                If 行业典集.Exists(行业) Then
                    行业额 = 行业典集(行业) + 单票额
                Else
                    行业额 = 单票额
                    '--- 首次遇到该行业，记录指数映射 ---
                    If 行业指数映射.Exists(行业) Then
                        行业指数典集(行业) = 行业指数映射(行业)
                    End If
                End If
                行业典集(行业) = 行业额
            End If
            '--- 板块轮动统计 ---
            轮动 = Left$(谕组(X, 位谕of仓周类), 1)
            If 轮动 <> "" Then
                If 行业轮动典集.Exists(行业) = False Then
                    行业轮动典集.Add 行业, 轮动
                Else
                    行业轮动典集(行业) = 行业轮动典集(行业) & 轮动
                End If
            End If
            '--- 策略统计 ---
            月基策略 = 谕组(X, 位谕of月基策略)
            If 月基策略 <> "" Then
                If 策略典集.Exists(月基策略) Then
                    策略典集(月基策略) = 策略典集(月基策略) + 1
                Else
                    策略典集(月基策略) = 1
                End If
            End If
            If VBA.IsNumeric(谕组(X, 位谕of月基命分)) Then
                总命分 = 总命分 + CDbl(谕组(X, 位谕of月基命分))
                命分票数 = 命分票数 + 1
            End If
            If VBA.IsNumeric(谕组(X, 位谕of月基策分)) Then
                总策分 = 总策分 + CDbl(谕组(X, 位谕of月基策分))
                策分票数 = 策分票数 + 1
            End If
            '--- 仓位分布 ---
            仓值 = 谕组(X, 位谕of仓位比)
            If VBA.IsNumeric(仓值) Then
                If 仓值 > 1 Then
                    仓超数 = 仓超数 + 1
                    单票超限 = 单票超限 & "[仓位]" & 谕组(X, 位qt代称) & "(" & 仓值 & "倍)" & vbCrLf
                ElseIf 仓值 >= 0.75 Then
                    仓满数 = 仓满数 + 1
                ElseIf 仓值 >= 0.25 Then
                    仓中数 = 仓中数 + 1
                Else
                    仓低数 = 仓低数 + 1
                End If
            End If
            '--- 前N重仓 ---
            For j = 1 To 10
                If 单票额 > 前N仓额(j) Then
                    '后移
                    For k = 10 To j + 1 Step -1
                        前N仓额(k) = 前N仓额(k - 1)
                        前N仓名(k) = 前N仓名(k - 1)
                        前N仓代(k) = 前N仓代(k - 1)
                    Next
                    前N仓额(j) = 单票额
                    前N仓名(j) = 谕组(X, 位qt代称)
                    前N仓代(j) = CIDL
                    Exit For
                End If
            Next
            '--- 仓周类上限 ---
            仓周类 = 谕组(X, 位谕of仓周类)
            组合占比 = 单票额 / IIf(总持仓额 > 0, 总持仓额, 1)
            If Left$(仓周类, 1) = "金" Or Left$(仓周类, 1) = "银" Then
                仓周上限 = 0.9
            ElseIf Left$(仓周类, 1) = "唏" Or Left$(仓周类, 1) = "嘘" Then
                仓周上限 = 0.5
            ElseIf Left$(仓周类, 1) = "屎" Or Left$(仓周类, 1) = "尿" Then
                仓周上限 = 0.2
            Else
                仓周上限 = 0.3
            End If
            If 组合占比 > 仓周上限 Then
                仓周违规 = 仓周违规 & "[仓限]" & 谕组(X, 位qt代称) & "=" & Format(组合占比, "0%") & ">" & Format(仓周上限, "0%") & "(" & 仓周类 & ")" & vbCrLf
            End If
            '--- 策略合规 ---
            月基策略 = 谕组(X, 位谕of月基策略)
            If Left$(月基策略, 2) = "NA" And 谕组(X, 位谕of仓持数) > 0 Then
                策略违规 = 策略违规 & "[策略]" & 谕组(X, 位qt代称) & "=" & 月基策略 & "但持仓" & vbCrLf
            End If
            命分 = 谕组(X, 位谕of月基命分)
            策分 = 谕组(X, 位谕of月基策分)
            If VBA.IsNumeric(命分) And VBA.IsNumeric(仓值) Then
                If 命分 < 50 And 仓值 > 0.5 Then
                    策略违规 = 策略违规 & "[低命分]" & 谕组(X, 位qt代称) & "=" & 命分 & "分但重仓" & 仓值 & vbCrLf
                End If
            End If
            If VBA.IsNumeric(策分) And VBA.IsNumeric(仓值) Then
                If 策分 < 60 And 仓值 > 0.5 Then
                    策略违规 = 策略违规 & "[低策分]" & 谕组(X, 位qt代称) & "=" & 策分 & "分但重仓" & 仓值 & vbCrLf
                End If
            End If
        End If
    Next X
'========================================================================================
'输出：标题
'========================================================================================
    末行 = 1
    With WSTO.Cells(末行, 1)
        .Value = "组合管理体检报告"
        .Font.Size = 18
        .Font.Bold = True
        .Font.Color = 常色主黑
        .Interior.Color = 常色六碧
    End With
    WSTO.Cells(末行, 2).Value = "生成时间: " & Now()
    WSTO.Cells(末行, 2).Font.Size = 10
    WSTO.Rows(末行).RowHeight = 30
'========================================================================================
'输出：一、持仓概览
'========================================================================================
    末行 = 3
    WSTO.Cells(末行, 1).Value = "一、持仓概览"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 4
    WSTO.Cells(末行, 1).Value = "指标"
    WSTO.Cells(末行, 2).Value = "宝福"
    WSTO.Cells(末行, 3).Value = "宝彦"
    WSTO.Cells(末行, 4).Value = "合计"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 5
    WSTO.Cells(末行, 1).Value = "持票数"
    WSTO.Cells(末行, 2).Value = 福票数
    WSTO.Cells(末行, 3).Value = 彦票数
    WSTO.Cells(末行, 4).Value = 持票数
    末行 = 6
    WSTO.Cells(末行, 1).Value = "持仓市值(千元)"
    WSTO.Cells(末行, 2).Value = Round(福仓额, 1)
    WSTO.Cells(末行, 3).Value = Round(彦仓额, 1)
    WSTO.Cells(末行, 4).Value = Round(总持仓额, 1)
    末行 = 7
    WSTO.Cells(末行, 1).Value = "现金余额(千元)"
    WSTO.Cells(末行, 2).Value = Round(福现金, 1)
    WSTO.Cells(末行, 3).Value = Round(彦现金, 1)
    WSTO.Cells(末行, 4).Value = Round(福现金 + 彦现金, 1)
    末行 = 8
    WSTO.Cells(末行, 1).Value = "总资产(千元)"
    WSTO.Cells(末行, 2).Value = Round(福总资, 1)
    WSTO.Cells(末行, 3).Value = Round(彦总资, 1)
    WSTO.Cells(末行, 4).Value = Round(福总资 + 彦总资, 1)
    末行 = 9
    WSTO.Cells(末行, 1).Value = "满仓率"
    If 福总资 > 0 Then WSTO.Cells(末行, 2).Value = Format(福仓额 / 福总资, "0%")
    If 彦总资 > 0 Then WSTO.Cells(末行, 3).Value = Format(彦仓额 / 彦总资, "0%")
    If 福总资 + 彦总资 > 0 Then WSTO.Cells(末行, 4).Value = Format(总持仓额 / (福总资 + 彦总资), "0%")
    末行 = 10
    WSTO.Cells(末行, 1).Value = "仓位目标"
    If 福总资 > 0 Then WSTO.Cells(末行, 2).Value = Format(福仓额 / 福总资, "0%") & "(目标30%)"
    If 福总资 > 0 Then WSTO.Cells(末行, 2).Font.Color = IIf(Abs(福仓额 / 福总资 - 0.3) > 0.15, 常色主黄, 常色主黑)
    If 彦总资 > 0 Then WSTO.Cells(末行, 3).Value = Format(彦仓额 / 彦总资, "0%") & "(目标60%)"
    If 彦总资 > 0 Then WSTO.Cells(末行, 3).Font.Color = IIf(Abs(彦仓额 / 彦总资 - 0.6) > 0.2, 常色主黄, 常色主黑)
    If 福总资 + 彦总资 > 0 Then WSTO.Cells(末行, 4).Value = Format(总持仓额 / (福总资 + 彦总资), "0%")
    '--- 概览数字格式，全部右对齐 ---
    For X = 5 To 10
        With WSTO.Rows(X)
            .HorizontalAlignment = xlRight
            If X <= 8 Then .NumberFormatLocal = "#,##0"
        End With
    Next
'========================================================================================
'输出：二、行业分布
'========================================================================================
    末行 = 12
    WSTO.Cells(末行, 1).Value = "二、行业分布"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 13
    WSTO.Cells(末行, 1).Value = "行业"
    WSTO.Cells(末行, 2).Value = "持仓额(千元)"
    WSTO.Cells(末行, 3).Value = "占比"
    WSTO.Cells(末行, 4).Value = "状态"
    WSTO.Cells(末行, 5).Value = "参考标的"
    WSTO.Cells(末行, 6).Value = "CIDL"
    WSTO.Cells(末行, 7).Value = "类型"
    WSTO.Cells(末行, 8).Value = "走势"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 14
    For Each 行业 In 行业典集.Keys
        行业额 = 行业典集(行业)
        WSTO.Cells(末行, 1).Value = 行业
        WSTO.Cells(末行, 2).Value = Round(行业额, 1)
        WSTO.Cells(末行, 2).NumberFormatLocal = "#,##0.0"
        WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 3).Value = Format(行业额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
        WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
        '--- 状态：行业上限30% ---
        If 行业额 / IIf(总持仓额 > 0, 总持仓额, 1) > 0.3 Then
            WSTO.Cells(末行, 4).Value = "X超限"
            WSTO.Cells(末行, 4).Font.Color = 常色主红
            超限名单 = 超限名单 & "[行业]" & 行业 & "(" & Format(行业额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%") & ">30%)" & vbCrLf
        Else
            WSTO.Cells(末行, 4).Value = "OK"
            WSTO.Cells(末行, 4).Font.Color = 常色主绿
        End If
        '--- 参考标的 + 走势 ---
        If 行业指数典集.Exists(行业) Then
            指数信息 = 行业指数典集(行业)
            WSTO.Cells(末行, 5).Value = 指数信息(0)  '名称
            WSTO.Cells(末行, 6).Value = 指数信息(1)  'CIDL
            WSTO.Cells(末行, 7).Value = 指数信息(2)  '类型
            '--- 走势：从谕组读取该标的的月基带周 ---
            If 典指位.Exists(指数信息(1)) Then
                行号指 = 典指位(指数信息(1))
                WSTO.Cells(末行, 8).Value = 谕组(行号指, 位谕of月基带周)
            End If
        Else
            WSTO.Cells(末行, 5).Value = "—"
        End If
        末行 = 末行 + 1
    Next
'========================================================================================
'输出：二B、板块轮动状态
'========================================================================================
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "二B、板块轮动状态"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "行业"
    WSTO.Cells(末行, 2).Value = "主升票数"
    WSTO.Cells(末行, 3).Value = "弱势票数"
    WSTO.Cells(末行, 4).Value = "状态"
    WSTO.Cells(末行, 5).Value = "建议仓位"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 末行 + 1
    Dim 轮动行业 As Variant
    Dim 轮动行 As Integer
    轮动行 = 末行
    For Each 轮动行业 In 行业轮动典集.Keys
        Dim 轮动串 As String
        轮动串 = 行业轮动典集(轮动行业)
        Dim 主升数 As Long: 主升数 = 0
        Dim 弱势数 As Long: 弱势数 = 0
        Dim c As Long
        For c = 1 To Len(轮动串)
            Dim ch As String
            ch = Mid$(轮动串, c, 1)
            If ch = "金" Or ch = "银" Then 主升数 = 主升数 + 1
            If ch = "屎" Or ch = "尿" Then 弱势数 = 弱势数 + 1
        Next
        WSTO.Cells(轮动行, 1).Value = 轮动行业
        WSTO.Cells(轮动行, 2).Value = 主升数
        WSTO.Cells(轮动行, 3).Value = 弱势数
        '状态判定
        Dim 轮动状态 As String
        Dim 建议仓位 As String
        If 主升数 > 弱势数 And 主升数 >= 2 Then
            轮动状态 = "主升"
            建议仓位 = "40-50%"
            WSTO.Cells(轮动行, 4).Font.Color = 常色主绿
        ElseIf 主升数 > 0 And 主升数 >= 弱势数 Then
            轮动状态 = "轮动候选"
            建议仓位 = "20-30%"
            WSTO.Cells(轮动行, 4).Font.Color = 常色主黄
        ElseIf 主升数 = 0 And 弱势数 = 0 Then
            轮动状态 = "震荡"
            建议仓位 = "10-20%"
        Else
            轮动状态 = "回避"
            建议仓位 = "0-5%"
            WSTO.Cells(轮动行, 4).Font.Color = 常色主红
        End If
        WSTO.Cells(轮动行, 4).Value = 轮动状态
        WSTO.Cells(轮动行, 5).Value = 建议仓位
        轮动行 = 轮动行 + 1
    Next
    末行 = 轮动行 + 1
'========================================================================================
'输出：三、策略分布
'========================================================================================
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "三、策略分布"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "月基策略"
    WSTO.Cells(末行, 2).Value = "票数"
    WSTO.Cells(末行, 3).Value = "占比"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 末行 + 1
    For Each 月基策略 In 策略典集.Keys
        WSTO.Cells(末行, 1).Value = 月基策略
        WSTO.Cells(末行, 2).Value = 策略典集(月基策略)
        WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 3).Value = Format(策略典集(月基策略) / IIf(持票数 > 0, 持票数, 1), "0%")
        WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
        末行 = 末行 + 1
    Next
    '--- 平均评分 ---
    If 命分票数 > 0 Then
        WSTO.Cells(末行, 1).Value = "平均命分"
        WSTO.Cells(末行, 2).Value = Round(总命分 / 命分票数, 1)
        末行 = 末行 + 1
    End If
    If 策分票数 > 0 Then
        WSTO.Cells(末行, 1).Value = "平均策分"
        WSTO.Cells(末行, 2).Value = Round(总策分 / 策分票数, 1)
        末行 = 末行 + 1
    End If
'========================================================================================
'输出：四、仓位分布
'========================================================================================
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "四、仓位分布"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "仓位"
    WSTO.Cells(末行, 2).Value = "票数"
    WSTO.Cells(末行, 3).Value = "占比"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "低仓(<25%)"
    WSTO.Cells(末行, 2).Value = 仓低数
    WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 3).Value = Format(仓低数 / IIf(持票数 > 0, 持票数, 1), "0%")
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "中仓(25%~75%)"
    WSTO.Cells(末行, 2).Value = 仓中数
    WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 3).Value = Format(仓中数 / IIf(持票数 > 0, 持票数, 1), "0%")
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "满仓(75%~100%)"
    WSTO.Cells(末行, 2).Value = 仓满数
    WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 3).Value = Format(仓满数 / IIf(持票数 > 0, 持票数, 1), "0%")
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "超限(>100%)"
    WSTO.Cells(末行, 1).Font.Color = IIf(仓超数 > 0, 常色主红, 常色主黑)
    WSTO.Cells(末行, 2).Value = 仓超数
    WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 3).Value = Format(仓超数 / IIf(持票数 > 0, 持票数, 1), "0%")
'========================================================================================
'输出：五、集中度
'========================================================================================
    末行 = 末行 + 2
    WSTO.Cells(末行, 1).Value = "五、集中度"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "排名"
    WSTO.Cells(末行, 2).Value = "代码"
    WSTO.Cells(末行, 3).Value = "名称"
    WSTO.Cells(末行, 4).Value = "持仓额(千元)"
    WSTO.Cells(末行, 5).Value = "占比"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    For j = 1 To 10
        If 前N仓额(j) > 0 Then
            末行 = 末行 + 1
            WSTO.Cells(末行, 1).Value = "第" & j & "名"
            WSTO.Cells(末行, 2).Value = 前N仓代(j)
            WSTO.Cells(末行, 3).Value = 前N仓名(j)
            WSTO.Cells(末行, 4).Value = 前N仓额(j)
            WSTO.Cells(末行, 4).NumberFormatLocal = "#,##0.0"
            WSTO.Cells(末行, 5).Value = Format(前N仓额(j) / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
        End If
    Next
    '--- 前3/5/10集中度 ---
    Dim 前3额 As Double: 前3额 = 0
    Dim 前5额 As Double: 前5额 = 0
    Dim 前10额 As Double: 前10额 = 0
    For j = 1 To 10
        If 前N仓额(j) > 0 Then
            If j <= 3 Then 前3额 = 前3额 + 前N仓额(j)
            If j <= 5 Then 前5额 = 前5额 + 前N仓额(j)
            前10额 = 前10额 + 前N仓额(j)
        End If
    Next
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "前3集中度"
    WSTO.Cells(末行, 2).Value = Format(前3额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
    WSTO.Cells(末行, 2).Font.Color = IIf(前3额 / IIf(总持仓额 > 0, 总持仓额, 1) > 0.5, 常色主黄, 常色主黑)
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "前5集中度"
    WSTO.Cells(末行, 2).Value = Format(前5额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
    WSTO.Cells(末行, 2).Font.Color = IIf(前5额 / IIf(总持仓额 > 0, 总持仓额, 1) > 0.7, 常色主黄, 常色主黑)
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "前10集中度"
    WSTO.Cells(末行, 2).Value = Format(前10额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
'========================================================================================
'输出：六、风控检查
'========================================================================================
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "六、风控检查"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    '--- 行业集中度 ---
    If Len(超限名单) > 0 Then
        WSTO.Cells(末行, 1).Value = "X行业超限"
        WSTO.Cells(末行, 1).Font.Color = 常色主红
        Dim 超限行 As Variant
        超限行 = Split(超限名单, vbCrLf)
        For i = 0 To UBound(超限行)
            If 超限行(i) <> "" Then
                WSTO.Cells(末行 + 1 + i, 2).Value = 超限行(i)
            End If
        Next
        末行 = 末行 + UBound(超限行) + 1
    Else
        WSTO.Cells(末行, 1).Value = "OK行业集中度"
        WSTO.Cells(末行, 1).Font.Color = 常色主绿
        WSTO.Cells(末行, 2).Value = "所有行业均未超限(上限30%)"
        末行 = 末行 + 1
    End If
    '--- 单票超限 ---
    If Len(单票超限) > 0 Then
        WSTO.Cells(末行, 1).Value = "X单票超限"
        WSTO.Cells(末行, 1).Font.Color = 常色主红
        Dim 单票行 As Variant
        单票行 = Split(单票超限, vbCrLf)
        For i = 0 To UBound(单票行)
            If 单票行(i) <> "" Then
                WSTO.Cells(末行 + 1 + i, 2).Value = 单票行(i)
            End If
        Next
        末行 = 末行 + UBound(单票行) + 1
    Else
        WSTO.Cells(末行, 1).Value = "OK单票仓位"
        WSTO.Cells(末行, 1).Font.Color = 常色主绿
        WSTO.Cells(末行, 2).Value = "所有股票均未超限"
        末行 = 末行 + 1
    End If
    '--- 持票数 ---
    WSTO.Cells(末行, 1).Value = "持票数"
    WSTO.Cells(末行, 2).Value = 持票数 & "只"
    末行 = 末行 + 1
    '--- 总仓位 ---
    If 总持仓额 > 0 Then
        WSTO.Cells(末行, 1).Value = "总持仓"
        WSTO.Cells(末行, 2).Value = Round(总持仓额, 1) & "千元"
        末行 = 末行 + 1
    End If
    '--- 策略合规 ---
    If Len(策略违规) > 0 Then
        WSTO.Cells(末行, 1).Value = "X策略违规"
        WSTO.Cells(末行, 1).Font.Color = 常色主红
        Dim 违规行 As Variant
        违规行 = Split(策略违规, vbCrLf)
        For i = 0 To UBound(违规行)
            If 违规行(i) <> "" Then
                WSTO.Cells(末行 + 1 + i, 2).Value = 违规行(i)
            End If
        Next
        末行 = 末行 + UBound(违规行) + 1
    Else
        WSTO.Cells(末行, 1).Value = "OK策略合规"
        WSTO.Cells(末行, 1).Font.Color = 常色主绿
        WSTO.Cells(末行, 2).Value = "所有持仓符合月基策略"
        末行 = 末行 + 1
    End If
    '--- 仓周类上限 ---
    If Len(仓周违规) > 0 Then
        WSTO.Cells(末行, 1).Value = "X仓周类超限"
        WSTO.Cells(末行, 1).Font.Color = 常色主红
        Dim 仓周行 As Variant
        仓周行 = Split(仓周违规, vbCrLf)
        For i = 0 To UBound(仓周行)
            If 仓周行(i) <> "" Then
                WSTO.Cells(末行 + 1 + i, 2).Value = 仓周行(i)
            End If
        Next
        末行 = 末行 + UBound(仓周行) + 1
    Else
        WSTO.Cells(末行, 1).Value = "OK仓周类上限"
        WSTO.Cells(末行, 1).Font.Color = 常色主绿
        WSTO.Cells(末行, 2).Value = "所有股票符合仓周类上限(金银90%/唏嘘50%/屎尿20%)"
        末行 = 末行 + 1
    End If
'========================================================================================
'输出：六、福仓持仓明细
'========================================================================================
    末行 = 末行 + 2
    WSTO.Cells(末行, 1).Value = "七、福仓持仓明细"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "代码"
    WSTO.Cells(末行, 2).Value = "名称"
    WSTO.Cells(末行, 3).Value = "行业"
    WSTO.Cells(末行, 4).Value = "持股数"
    WSTO.Cells(末行, 5).Value = "持额"
    WSTO.Cells(末行, 6).Value = "仓位比"
    WSTO.Cells(末行, 7).Value = "月基策略"
    WSTO.Cells(末行, 8).Value = "命分"
    WSTO.Cells(末行, 9).Value = "策分"
    WSTO.Cells(末行, 10).Value = "操作"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    明细行 = 末行 + 1
    For X = LBound(谕组, 1) To UBound(谕组, 1)
            CIDL = 谕组(X, 位qt代码)
            福仓数 = 0
            If 典码位花册.Exists(CIDL) Then
                行号 = 典码位花册(CIDL)
                福仓字 = Trim(WS花册.Cells(行号, 位列花天仓宝福).Value)
                If InStr(福仓字, ",") > 0 Then 福仓数 = Val(Left$(福仓字, InStr(福仓字, ",") - 1))
        End If
            If 福仓数 > 0 Then
                WSTO.Cells(明细行, 1).Value = CIDL
                WSTO.Cells(明细行, 2).Value = 谕组(X, 位qt代称)
                WSTO.Cells(明细行, 3).Value = 谕组(X, 位qt行益)
                WSTO.Cells(明细行, 4).Value = 福仓数
                WSTO.Cells(明细行, 4).NumberFormatLocal = "#,##0"
                WSTO.Cells(明细行, 5).Value = Round(100 * 福仓数 / 100 * IIf(VBA.IsNumeric(谕组(X, 位qt今收)), 谕组(X, 位qt今收), 0) / 1000, 1)
                WSTO.Cells(明细行, 5).NumberFormatLocal = "#,##0.0"
                WSTO.Cells(明细行, 6).Value = 谕组(X, 位谕of仓位比)
                WSTO.Cells(明细行, 7).Value = 谕组(X, 位谕of月基策略)
                If VBA.IsNumeric(谕组(X, 位谕of月基命分)) Then WSTO.Cells(明细行, 8).Value = 谕组(X, 位谕of月基命分)
                If VBA.IsNumeric(谕组(X, 位谕of月基策分)) Then WSTO.Cells(明细行, 9).Value = 谕组(X, 位谕of月基策分)
                WSTO.Cells(明细行, 10).Value = 谕组(X, 位谕of仓操作)
                明细行 = 明细行 + 1
            End If
    Next
'========================================================================================
'输出：七、彦仓持仓明细
'========================================================================================
    末行 = 明细行 + 1
    WSTO.Cells(末行, 1).Value = "八、彦仓持仓明细"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "代码"
    WSTO.Cells(末行, 2).Value = "名称"
    WSTO.Cells(末行, 3).Value = "行业"
    WSTO.Cells(末行, 4).Value = "持股数"
    WSTO.Cells(末行, 5).Value = "持额"
    WSTO.Cells(末行, 6).Value = "仓位比"
    WSTO.Cells(末行, 7).Value = "月基策略"
    WSTO.Cells(末行, 8).Value = "命分"
    WSTO.Cells(末行, 9).Value = "策分"
    WSTO.Cells(末行, 10).Value = "操作"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    明细行 = 末行 + 1
    For X = LBound(谕组, 1) To UBound(谕组, 1)
            CIDL = 谕组(X, 位qt代码)
            彦仓数 = 0
            If 典码位花册.Exists(CIDL) Then
                行号 = 典码位花册(CIDL)
                彦仓字 = Trim(WS花册.Cells(行号, 位列花天仓宝彦).Value)
                If InStr(彦仓字, ",") > 0 Then 彦仓数 = Val(Left$(彦仓字, InStr(彦仓字, ",") - 1))
        End If
            If 彦仓数 > 0 Then
                WSTO.Cells(明细行, 1).Value = CIDL
                WSTO.Cells(明细行, 2).Value = 谕组(X, 位qt代称)
                WSTO.Cells(明细行, 3).Value = 谕组(X, 位qt行益)
                WSTO.Cells(明细行, 4).Value = 彦仓数
                WSTO.Cells(明细行, 4).NumberFormatLocal = "#,##0"
                WSTO.Cells(明细行, 5).Value = Round(100 * 彦仓数 / 100 * IIf(VBA.IsNumeric(谕组(X, 位qt今收)), 谕组(X, 位qt今收), 0) / 1000, 1)
                WSTO.Cells(明细行, 5).NumberFormatLocal = "#,##0.0"
                WSTO.Cells(明细行, 6).Value = 谕组(X, 位谕of仓位比)
                WSTO.Cells(明细行, 7).Value = 谕组(X, 位谕of月基策略)
                If VBA.IsNumeric(谕组(X, 位谕of月基命分)) Then WSTO.Cells(明细行, 8).Value = 谕组(X, 位谕of月基命分)
                If VBA.IsNumeric(谕组(X, 位谕of月基策分)) Then WSTO.Cells(明细行, 9).Value = 谕组(X, 位谕of月基策分)
                WSTO.Cells(明细行, 10).Value = 谕组(X, 位谕of仓操作)
                明细行 = 明细行 + 1
            End If
    Next
'========================================================================================
'列宽调整
'========================================================================================
    WSTO.Columns("A").ColumnWidth = 16
    WSTO.Columns("B").ColumnWidth = 10
    WSTO.Columns("C").ColumnWidth = 10
    WSTO.Columns("D").ColumnWidth = 12
    WSTO.Columns("E").ColumnWidth = 12
    WSTO.Columns("F").ColumnWidth = 12
    WSTO.Columns("G").ColumnWidth = 10
    WSTO.Columns("H").ColumnWidth = 10
    WSTO.Columns("I").ColumnWidth = 6
    WSTO.Columns("J").ColumnWidth = 6
    WSTO.Columns("K").ColumnWidth = 10
'========================================================================================
'输出：组合调整建议
'========================================================================================
    末行 = 明细行 + 2
    WSTO.Cells(末行, 1).Value = "组合调整建议（最小修改方案）"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "维度"
    WSTO.Cells(末行, 2).Value = "当前状态"
    WSTO.Cells(末行, 3).Value = "建议调整"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 末行 + 1
    Dim 建议数 As Integer: 建议数 = 0
    '--- 行业集中度建议 ---
    For Each 行业 In 行业典集.Keys
        行业额 = 行业典集(行业)
        If 行业额 / IIf(总持仓额 > 0, 总持仓额, 1) > 0.3 Then
            建议数 = 建议数 + 1
            WSTO.Cells(末行, 1).Value = "行业集中度"
            WSTO.Cells(末行, 2).Value = 行业 & "超限(" & Format(行业额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%") & ">30%)"
            WSTO.Cells(末行, 3).Value = "减仓" & 行业 & Round(行业额 - 总持仓额 * 0.3, 1) & "千元至30%"
            WSTO.Cells(末行, 3).Font.Color = 常色主黄
            末行 = 末行 + 1
        End If
    Next
    '--- 单票超限建议 ---
    If Len(单票超限) > 0 Then
        单票行 = Split(单票超限, vbCrLf)
        For i = 0 To UBound(单票行)
            If 单票行(i) <> "" Then
                建议数 = 建议数 + 1
                WSTO.Cells(末行, 1).Value = "单票超限"
                WSTO.Cells(末行, 2).Value = 单票行(i)
                WSTO.Cells(末行, 3).Value = "减仓至仓位比≤1"
                WSTO.Cells(末行, 3).Font.Color = 常色主黄
                末行 = 末行 + 1
            End If
        Next
    End If
    '--- 仓周类上限建议 ---
    If Len(仓周违规) > 0 Then
        仓周行 = Split(仓周违规, vbCrLf)
        For i = 0 To UBound(仓周行)
            If 仓周行(i) <> "" Then
                建议数 = 建议数 + 1
                WSTO.Cells(末行, 1).Value = "仓周类上限"
                WSTO.Cells(末行, 2).Value = 仓周行(i)
                WSTO.Cells(末行, 3).Value = "减仓至组合占比≤上限"
                WSTO.Cells(末行, 3).Font.Color = 常色主黄
                末行 = 末行 + 1
            End If
        Next
    End If
    '--- 账户目标偏离建议 ---
    If 福总资 > 0 Then
        Dim 福满 As Double: 福满 = 福仓额 / 福总资
        If Abs(福满 - 0.3) > 0.15 Then
            建议数 = 建议数 + 1
            WSTO.Cells(末行, 1).Value = "宝福仓位目标"
            WSTO.Cells(末行, 2).Value = "当前" & Format(福满, "0%") & "(目标30%)"
            If 福满 > 0.45 Then
                WSTO.Cells(末行, 3).Value = "减仓至30%，释放" & Round((福满 - 0.3) * 福总资, 1) & "千元"
            ElseIf 福满 < 0.15 Then
                WSTO.Cells(末行, 3).Value = "可加仓至30%，增加" & Round((0.3 - 福满) * 福总资, 1) & "千元"
            End If
            WSTO.Cells(末行, 3).Font.Color = 常色主黄
            末行 = 末行 + 1
        End If
    End If
    If 彦总资 > 0 Then
        Dim 彦满 As Double: 彦满 = 彦仓额 / 彦总资
        If Abs(彦满 - 0.6) > 0.2 Then
            建议数 = 建议数 + 1
            WSTO.Cells(末行, 1).Value = "宝彦仓位目标"
            WSTO.Cells(末行, 2).Value = "当前" & Format(彦满, "0%") & "(目标60%)"
            If 彦满 > 0.8 Then
                WSTO.Cells(末行, 3).Value = "减仓至60%，释放" & Round((彦满 - 0.6) * 彦总资, 1) & "千元"
            ElseIf 彦满 < 0.4 Then
                WSTO.Cells(末行, 3).Value = "可加仓至60%，增加" & Round((0.6 - 彦满) * 彦总资, 1) & "千元"
            End If
            WSTO.Cells(末行, 3).Font.Color = 常色主黄
            末行 = 末行 + 1
        End If
    End If
    '--- 板块不足建议 ---
    If 行业典集.Count < 3 Then
        建议数 = 建议数 + 1
        WSTO.Cells(末行, 1).Value = "板块分散度"
        WSTO.Cells(末行, 2).Value = "仅" & 行业典集.Count & "个板块，不足3个"
        WSTO.Cells(末行, 3).Value = "建议新增1-2个板块分散风险"
        WSTO.Cells(末行, 3).Font.Color = 常色主黄
        末行 = 末行 + 1
    End If
    '--- 无建议 ---
    If 建议数 = 0 Then
        WSTO.Cells(末行, 1).Value = "OK组合合规"
        WSTO.Cells(末行, 1).Font.Color = 常色主绿
        WSTO.Cells(末行, 2).Value = "当前持仓符合所有规则，无需调整"
    End If
'========================================================================================
'返回
'========================================================================================
    MSG = MSG & "【组合管理】体检报告已生成→" & 表名 & vbCrLf
    MSG = MSG & "  持票=" & 持票数 & " | 总持仓额=" & Round(总持仓额, 1) & "千元 | 总持股数=" & 总持仓数 & "股" & vbCrLf
    IQQQ展擎筛程至A2组合管理检查 = MSG
'========================================================================================
End Function
'########################################################################################
'########################################################################################
'##############################  行业指数映射表  ########################################
'########################################################################################
'########################################################################################
'益盟细分行业 → 参考指数/ETF 映射字典
'Key=益盟细分行业名称, Item=数组(参考名称, CIDL, 类型)
'仅包含成分股高度重叠(≥70%)的精准匹配，不精确的不计入
'编制日期：2026-08-02  详见MP2_研究投资组合管理.md 第六章
'########################################################################################
Public Function UTL族群引擎_行业指数映射() As Dictionary
    Dim 典 As New Dictionary
    '========================================================================================
    '金融族
    '========================================================================================
    典.Add key:="银行", Item:=Array("中证银行", "sz399986", "指数")
    典.Add key:="证券期货", Item:=Array("证券公司", "sz399975", "指数")
    典.Add key:="保险", Item:=Array("保险主题", "sz399809", "指数")
    典.Add key:="多元金融", Item:=Array("中证金融", "sz399934", "指数")
    '========================================================================================
    '电子制造族
    '========================================================================================
    典.Add key:="半导体", Item:=Array("半导体ETF", "sh512480", "ETF")
    典.Add key:="消费电子", Item:=Array("消费电子ETF", "sz159732", "ETF")
    典.Add key:="电源设备", Item:=Array("中证新能", "sz399808", "指数")
    典.Add key:="IT设备", Item:=Array("国证通信", "sz399389", "指数")
    '========================================================================================
    '文化族
    '========================================================================================
    典.Add key:="文化传媒", Item:=Array("国证文化", "sz399397", "指数")
    典.Add key:="影视动漫", Item:=Array("中证传媒", "sz399971", "指数")
    典.Add key:="游戏", Item:=Array("中证传媒", "sz399971", "指数")
    典.Add key:="教育", Item:=Array("教育ETF", "sh513360", "ETF")
    典.Add key:="景点", Item:=Array("旅游ETF", "sz159766", "ETF")
    典.Add key:="旅游综合", Item:=Array("旅游ETF", "sz159766", "ETF")
    典.Add key:="其他休闲服务", Item:=Array("旅游ETF", "sz159766", "ETF")
    '========================================================================================
    '互联网族
    '========================================================================================
    典.Add key:="软件开发", Item:=Array("中证信息", "sz399935", "指数")
    典.Add key:="软件服务", Item:=Array("中证信息", "sz399935", "指数")
    典.Add key:="通信设备", Item:=Array("国证通信", "sz399389", "指数")
    典.Add key:="通信服务", Item:=Array("国证通信", "sz399389", "指数")
    典.Add key:="营销传播", Item:=Array("中证传媒", "sz399971", "指数")
    典.Add key:="互联网传媒", Item:=Array("中证传媒", "sz399971", "指数")
    '========================================================================================
    '周期族
    '========================================================================================
    典.Add key:="有色金属", Item:=Array("国证有色", "sz399395", "指数")
    典.Add key:="钢铁", Item:=Array("国证钢铁", "sz399440", "指数")
    典.Add key:="煤炭开采", Item:=Array("中证煤炭", "sz399998", "指数")
    典.Add key:="电力", Item:=Array("绿色电力", "sz399438", "指数")
    典.Add key:="环境保护", Item:=Array("中证环保", "sh000827", "指数")
    典.Add key:="石油石化", Item:=Array("国证油气", "sz399439", "指数")
    典.Add key:="黄金", Item:=Array("国证有色", "sz399395", "指数")
    '========================================================================================
    '电气制造族
    '========================================================================================
    典.Add key:="航天国防", Item:=Array("中证军工", "sz399967", "指数")
    典.Add key:="光伏设备", Item:=Array("中证新能", "sz399808", "指数")
    典.Add key:="风电设备", Item:=Array("中证新能", "sz399808", "指数")
    典.Add key:="自动化设备", Item:=Array("机器人50", "sz399283", "指数")
    '========================================================================================
    '机械制造族
    '========================================================================================
    典.Add key:="机床设备", Item:=Array("工业4.0", "sz399803", "指数")
    '========================================================================================
    '汽车族
    '========================================================================================
    典.Add key:="汽车制造", Item:=Array("新能源车", "sz399417", "指数")
    典.Add key:="汽车零部件", Item:=Array("新能源车", "sz399417", "指数")
    典.Add key:="电池", Item:=Array("中证新能", "sz399808", "指数")
    '========================================================================================
    '运输族
    '========================================================================================
    典.Add key:="仓储物流", Item:=Array("国证物流", "sz399353", "指数")
    典.Add key:="航空运输", Item:=Array("国证交运", "sz399433", "指数")
    典.Add key:="机场", Item:=Array("国证交运", "sz399433", "指数")
    典.Add key:="铁路运输", Item:=Array("国证交运", "sz399433", "指数")
    典.Add key:="高速公路", Item:=Array("国证交运", "sz399433", "指数")
    典.Add key:="水上运输", Item:=Array("国证交运", "sz399433", "指数")
    典.Add key:="港口", Item:=Array("国证交运", "sz399433", "指数")
    '========================================================================================
    '基建族
    '========================================================================================
    典.Add key:="工程建筑", Item:=Array("基建工程", "sz399995", "指数")
    典.Add key:="建材", Item:=Array("国证基建", "sz399359", "指数")
    典.Add key:="装修装饰", Item:=Array("基建工程", "sz399995", "指数")
    典.Add key:="房地产", Item:=Array("国证地产", "sz399393", "指数")
    典.Add key:="水泥", Item:=Array("国证基建", "sz399359", "指数")
    '========================================================================================
    '农业族
    '========================================================================================
    典.Add key:="农药", Item:=Array("国证农牧", "sz399435", "指数")
    典.Add key:="农林", Item:=Array("国证农牧", "sz399435", "指数")
    典.Add key:="农业服务", Item:=Array("国证农牧", "sz399435", "指数")
    典.Add key:="牧渔", Item:=Array("国证农牧", "sz399435", "指数")
    典.Add key:="饲料加工", Item:=Array("国证粮食", "sz399365", "指数")
    典.Add key:="动物保健", Item:=Array("国证农牧", "sz399435", "指数")
    '========================================================================================
    '化工族
    '========================================================================================
    典.Add key:="化学制品", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add key:="化学原料", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add key:="化肥", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add key:="化纤", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add key:="橡胶", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add key:="塑料", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add key:="新材料", Item:=Array("新材料ETF", "sh516360", "ETF")
    '========================================================================================
    '医药族
    '========================================================================================
    典.Add key:="医疗美容", Item:=Array("中证医药", "sz399933", "指数")
    典.Add key:="医药制造", Item:=Array("中证医药", "sz399933", "指数")
    典.Add key:="中药", Item:=Array("中证医药", "sz399933", "指数")
    典.Add key:="生物制品", Item:=Array("生物医药", "sz399441", "指数")
    典.Add key:="医疗服务", Item:=Array("中证医疗", "sz399989", "指数")
    典.Add key:="医药流通", Item:=Array("中证医药", "sz399933", "指数")
    典.Add key:="医疗器械", Item:=Array("中证医疗", "sz399989", "指数")
    '========================================================================================
    '消费族
    '========================================================================================
    典.Add key:="酿酒", Item:=Array("中证白酒", "sz399997", "指数")
    典.Add key:="饮料制造", Item:=Array("中证酒", "sz399987", "指数")
    典.Add key:="食品加工", Item:=Array("国证食品", "sz399396", "指数")
    典.Add key:="酒店餐饮", Item:=Array("国证服务", "sz399320", "指数")
    典.Add key:="服装", Item:=Array("中证消费", "sz399932", "指数")
    典.Add key:="家电", Item:=Array("中证消费", "sz399932", "指数")
    典.Add key:="家具制造", Item:=Array("中证消费", "sz399932", "指数")
    '========================================================================================
    '公共族
    '========================================================================================
    典.Add key:="公用事业", Item:=Array("绿色电力", "sz399438", "指数")
    '========================================================================================
    Set UTL族群引擎_行业指数映射 = 典
End Function

