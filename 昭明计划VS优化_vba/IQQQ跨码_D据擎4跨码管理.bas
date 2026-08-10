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
    
    '对于持仓：只有【CID是代码】且【持仓数量>0】进行考虑
    If 值仓持数 <= 0 Then Exit Function
    '================================================================================
    '衍生逻辑
    '================================================================================
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
            If InStr(谕组(X, 位谕of月基策日), "禁") > 0 Then
                    谕组(X, 位qt盯盘类别) = "X禁"
                    谕组(X, 位谕of仓位比) = "仓限禁旨"
            ElseIf 谕组(X, 位谕of仓限总) = 0 Then
                    谕组(X, 位qt盯盘类别) = "O无"
                    谕组(X, 位谕of仓位比) = "仓限为0"
            Else
                    值仓位比 = Round(值仓持数 / 谕组(X, 位谕of仓限总), 1)
                    谕组(X, 位谕of仓位比) = IIf(值仓位比 > 1, 值仓位比 & "倍", 值仓位比)
                    If 谕组(X, 位谕of仓持额) * 1000 <= 常值仓限底仓额 Then
                        谕组(X, 位qt盯盘类别) = "H基"
                    Else
                        谕组(X, 位qt盯盘类别) = "K冲"
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
    '================================================================================
    IQQQ跨码据擎_数程生成跨码管理1仓位管理 = 1
End Function
'##############################  日段统计 单行  ##########################################
'########################################################################################
'由神谕在循环内调用。从组结算统时区域复制日段仨/佰/十属性到谕组，





'========================================================================================
' IQQQ展擎筛程至A2组合管理检查 — 组合管理体检报告
' 由主控流程在神谕计算完成后调用，只读取不写入。
' 输出：Sheet 体检表（概览、行业分布、策略分布、风控检查、持仓明细）
' 读取谕组：位qt代码、位谕of仓持数、位谕of仓持额、位谕of仓位比、位谕of月基策周等
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
    Dim 策略典集额 As New Dictionary
    Dim 策日典集 As New Dictionary
    Dim 策日典集额 As New Dictionary
    Dim 总命分 As Double: 总命分 = 0
    Dim 总策分 As Double: 总策分 = 0
    Dim 命分票数 As Integer: 命分票数 = 0
    Dim 策分票数 As Integer: 策分票数 = 0
    Dim 月基策周 As Variant
    '--- 持仓明细 ---
    Dim 明细行 As Integer
    '--- 风控 ---
    Dim 超限名单 As String
    Dim 单票超限 As String
    '--- 仓位分布 ---
    Dim 仓低数 As Integer: 仓低数 = 0
    Dim 仓低额 As Double: 仓低额 = 0
    Dim 仓中数 As Integer: 仓中数 = 0
    Dim 仓中额 As Double: 仓中额 = 0
    Dim 仓满数 As Integer: 仓满数 = 0
    Dim 仓满额 As Double: 仓满额 = 0
    Dim 仓超数 As Integer: 仓超数 = 0
    Dim 仓超额 As Double: 仓超额 = 0
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
    '--- ETF/股票分类统计 ---
    Dim 票代称 As String
    Dim ETF数 As Integer: ETF数 = 0
    Dim ETF额 As Double: ETF额 = 0
    Dim 上证股数 As Integer: 上证股数 = 0
    Dim 上证股额 As Double: 上证股额 = 0
    Dim 科创股数 As Integer: 科创股数 = 0
    Dim 科创股额 As Double: 科创股额 = 0
    Dim 创业股数 As Integer: 创业股数 = 0
    Dim 创业股额 As Double: 创业股额 = 0
    Dim 深证股数 As Integer: 深证股数 = 0
    Dim 深证股额 As Double: 深证股额 = 0
    Dim 北交股数 As Integer: 北交股数 = 0
    Dim 北交股额 As Double: 北交股额 = 0
    '--- 行业持仓股票列表 ---
    Dim 行业股票典集 As New Dictionary  '行业→股票名称列表
    Dim 缺行业名单 As String: 缺行业名单 = ""  '无行业分类的股票名称列表
    '--- 双账户ETF/股票分类 ---
    Dim 福ETF数 As Integer, 彦ETF数 As Integer
    Dim 福ETF额 As Double, 彦ETF额 As Double
    Dim 福股数 As Integer, 彦股数 As Integer
    Dim 福股额 As Double, 彦股额 As Double
    Dim 福上证数 As Integer, 彦上证数 As Integer
    Dim 福上证额 As Double, 彦上证额 As Double
    Dim 福科创数 As Integer, 彦科创数 As Integer
    Dim 福科创额 As Double, 彦科创额 As Double
    Dim 福创业数 As Integer, 彦创业数 As Integer
    Dim 福创业额 As Double, 彦创业额 As Double
    Dim 福深证数 As Integer, 彦深证数 As Integer
    Dim 福深证额 As Double, 彦深证额 As Double
    Dim 福北交数 As Integer, 彦北交数 As Integer
    Dim 福北交额 As Double, 彦北交额 As Double
    Dim 福港股数 As Integer, 彦港股数 As Integer
    Dim 福港股额 As Double, 彦港股额 As Double
    Dim 港股数 As Integer, 港股额 As Double
    Dim 港计数 As Boolean
    '--- 策略分类统计 ---
    Dim 福月基数 As Integer, 福月基额 As Double
    Dim 彦月基数 As Integer, 彦月基额 As Double
    Dim 福周冲数 As Integer, 福周冲额 As Double
    Dim 彦周冲数 As Integer, 彦周冲额 As Double
    Dim 福日冲数 As Integer, 福日冲额 As Double
    Dim 彦日冲数 As Integer, 彦日冲额 As Double
    Dim 月基策周值 As String, 周冲策分 As Variant, 月基日H2值 As Variant
'========================================================================================
'建页
'========================================================================================
    Dim WSTO As Worksheet
    Dim 表名 As String
    表名 = 常簿缀选临 & "Z仓管"
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
    福现金 = 跨码管理_取名称值("ZF可用资金") / 1000
    彦现金 = 跨码管理_取名称值("ZJ可用资金") / 1000
    福总资 = 跨码管理_取名称值("ZF总资产") / 1000
    彦总资 = 跨码管理_取名称值("ZJ总资产") / 1000
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
            '--- ETF/股票分类（双账户） ---
            票代称 = 谕组(X, 位qt代称)
            Dim 福票额 As Double, 彦票额 As Double
            福票额 = 单票额 * 福仓数 / IIf(值持仓数 > 0, 值持仓数, 1)
            彦票额 = 单票额 * 彦仓数 / IIf(值持仓数 > 0, 值持仓数, 1)
            If CIDL Like "sh5#####" Or CIDL Like "sz1#####" Then
                ETF数 = ETF数 + 1: ETF额 = ETF额 + 单票额
                If 福仓数 > 0 Then 福ETF数 = 福ETF数 + 1: 福ETF额 = 福ETF额 + 福票额
                If 彦仓数 > 0 Then 彦ETF数 = 彦ETF数 + 1: 彦ETF额 = 彦ETF额 + 彦票额
            ElseIf CIDL Like "sh60####" Then
                上证股数 = 上证股数 + 1: 上证股额 = 上证股额 + 单票额
                If 福仓数 > 0 Then 福上证数 = 福上证数 + 1: 福上证额 = 福上证额 + 福票额
                If 彦仓数 > 0 Then 彦上证数 = 彦上证数 + 1: 彦上证额 = 彦上证额 + 彦票额
            ElseIf CIDL Like "sz00####" Then
                深证股数 = 深证股数 + 1: 深证股额 = 深证股额 + 单票额
                If 福仓数 > 0 Then 福深证数 = 福深证数 + 1: 福深证额 = 福深证额 + 福票额
                If 彦仓数 > 0 Then 彦深证数 = 彦深证数 + 1: 彦深证额 = 彦深证额 + 彦票额
            ElseIf CIDL Like "sz30####" Then
                创业股数 = 创业股数 + 1: 创业股额 = 创业股额 + 单票额
                If 福仓数 > 0 Then 福创业数 = 福创业数 + 1: 福创业额 = 福创业额 + 福票额
                If 彦仓数 > 0 Then 彦创业数 = 彦创业数 + 1: 彦创业额 = 彦创业额 + 彦票额
            ElseIf CIDL Like "sh68####" Then
                科创股数 = 科创股数 + 1: 科创股额 = 科创股额 + 单票额
                If 福仓数 > 0 Then 福科创数 = 福科创数 + 1: 福科创额 = 福科创额 + 福票额
                If 彦仓数 > 0 Then 彦科创数 = 彦科创数 + 1: 彦科创额 = 彦科创额 + 彦票额
            ElseIf CIDL Like "bj[9]#####" Then
                北交股数 = 北交股数 + 1: 北交股额 = 北交股额 + 单票额
                If 福仓数 > 0 Then 福北交数 = 福北交数 + 1: 福北交额 = 福北交额 + 福票额
                If 彦仓数 > 0 Then 彦北交数 = 彦北交数 + 1: 彦北交额 = 彦北交额 + 彦票额
            ElseIf Left$(CIDL, 4) = "r_hk" Then
                港股数 = 港股数 + 1: 港股额 = 港股额 + 单票额
                If 福仓数 > 0 Then 福港股数 = 福港股数 + 1: 福港股额 = 福港股额 + 福票额
                If 彦仓数 > 0 Then 彦港股数 = 彦港股数 + 1: 彦港股额 = 彦港股额 + 彦票额
            Else
                '其他（美股、B股等）归入港股合计
                港股数 = 港股数 + 1: 港股额 = 港股额 + 单票额
                If 福仓数 > 0 Then 福港股数 = 福港股数 + 1: 福港股额 = 福港股额 + 福票额
                If 彦仓数 > 0 Then 彦港股数 = 彦港股数 + 1: 彦港股额 = 彦港股额 + 彦票额
            End If
            '--- 双账户股票合计 ---
            If CIDL Like "sh5#####" Or CIDL Like "sz1#####" Then
                'ETF已在上面统计
            Else
                If 福仓数 > 0 Then 福股数 = 福股数 + 1: 福股额 = 福股额 + 福票额
                If 彦仓数 > 0 Then 彦股数 = 彦股数 + 1: 彦股额 = 彦股额 + 彦票额
            End If
            If 福仓数 > 0 Then
                福票数 = 福票数 + 1
                福仓额 = 福仓额 + 单票额 * 福仓数 / (福仓数 + 彦仓数)
            End If
            If 彦仓数 > 0 Then
                彦票数 = 彦票数 + 1
                彦仓额 = 彦仓额 + 单票额 * 彦仓数 / (福仓数 + 彦仓数)
            End If
            '--- 策略分类统计 ---
            月基策周值 = 谕组(X, 位谕of月基策周)
            If 月基策周值 <> "" And Left$(月基策周值, 2) <> "NA" Then
                If 福仓数 > 0 Then 福月基数 = 福月基数 + 1: 福月基额 = 福月基额 + 福票额
                If 彦仓数 > 0 Then 彦月基数 = 彦月基数 + 1: 彦月基额 = 彦月基额 + 彦票额
            Else
                '非月基 → 周冲/日冲
                周冲策分 = 谕组(X, 位谕of周冲策分)
                If VBA.IsNumeric(周冲策分) And 周冲策分 >= 50 Then
                    If 福仓数 > 0 Then 福周冲数 = 福周冲数 + 1: 福周冲额 = 福周冲额 + 福票额
                    If 彦仓数 > 0 Then 彦周冲数 = 彦周冲数 + 1: 彦周冲额 = 彦周冲额 + 彦票额
                Else
                    '非周冲 → 检查月基分日
                    日冲策分 = 谕组(X, 位谕of日冲策分)
                    If VBA.IsNumeric(日冲策分) And 日冲策分 >= 50 Then
                        If 福仓数 > 0 Then 福日冲数 = 福日冲数 + 1: 福日冲额 = 福日冲额 + 福票额
                        If 彦仓数 > 0 Then 彦日冲数 = 彦日冲数 + 1: 彦日冲额 = 彦日冲额 + 彦票额
                    End If
                    '月基分日<50 → 非策略，不计入任何策略分类
                End If
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
                '--- 记录该行业的持仓股票名称 ---
                If 行业股票典集.Exists(行业) Then
                    行业股票典集(行业) = 行业股票典集(行业) & "、" & 票代称
                Else
                    行业股票典集(行业) = 票代称
                End If
            Else
                缺行业名单 = 缺行业名单 & "、" & 票代称
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
            月基策周 = 谕组(X, 位谕of月基策周)
            If 月基策周 <> "" Then
                If 策略典集.Exists(月基策周) Then
                    策略典集(月基策周) = 策略典集(月基策周) + 1
                    策略典集额(月基策周) = 策略典集额(月基策周) + 单票额
                Else
                    策略典集(月基策周) = 1
                    策略典集额(月基策周) = 单票额
                End If
            Else
                '空月基策周归入非策略
                If 策略典集.Exists("非策略") Then
                    策略典集("非策略") = 策略典集("非策略") + 1
                    策略典集额("非策略") = 策略典集额("非策略") + 单票额
                Else
                    策略典集("非策略") = 1
                    策略典集额("非策略") = 单票额
                End If
            End If
            '--- 月基策日统计 ---
            Dim 月基策日值 As String
            月基策日值 = Left$(谕组(X, 位谕of月基策日), 1)
            If 月基策日值 >= "A" And 月基策日值 <= "H" Then
                If 策日典集.Exists(月基策日值) Then
                    策日典集(月基策日值) = 策日典集(月基策日值) + 1
                    策日典集额(月基策日值) = 策日典集额(月基策日值) + 单票额
                Else
                    策日典集(月基策日值) = 1
                    策日典集额(月基策日值) = 单票额
                End If
            End If
            If VBA.IsNumeric(谕组(X, 位谕of月基分命)) Then
                总命分 = 总命分 + CDbl(谕组(X, 位谕of月基分命))
                命分票数 = 命分票数 + 1
            End If
            If VBA.IsNumeric(谕组(X, 位谕of月基分周)) Then
                总策分 = 总策分 + CDbl(谕组(X, 位谕of月基分周))
                策分票数 = 策分票数 + 1
            End If
            '--- 仓位分布 ---
            仓值 = 谕组(X, 位谕of仓位比)
            If VBA.IsNumeric(仓值) Then
                If 仓值 > 1 Then
                    仓超数 = 仓超数 + 1
                    仓超额 = 仓超额 + 单票额
                    单票超限 = 单票超限 & "[仓位]" & 谕组(X, 位qt代称) & "(" & 仓值 & "倍)" & vbCrLf
                ElseIf 仓值 >= 0.75 Then
                    仓满数 = 仓满数 + 1
                    仓满额 = 仓满额 + 单票额
                ElseIf 仓值 >= 0.25 Then
                    仓中数 = 仓中数 + 1
                    仓中额 = 仓中额 + 单票额
                Else
                    仓低数 = 仓低数 + 1
                    仓低额 = 仓低额 + 单票额
                End If
            Else
                '非数值仓位比（如"仓限禁旨""仓限为0""2倍"）归入低仓
                仓低数 = 仓低数 + 1
                仓低额 = 仓低额 + 单票额
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
            '--- 仓限倍超限 ---
            If InStr(谕组(X, 位谕of仓位比), "倍") > 0 Then
                仓周违规 = 仓周违规 & "[仓限]" & 谕组(X, 位qt代称) & "=" & 谕组(X, 位谕of仓位比) & "(超限)" & vbCrLf
            End If
            '--- 策略合规 ---
            If InStr(谕组(X, 位谕of月基策日), "禁") > 0 And 谕组(X, 位谕of仓持数) > 0 Then
                策略违规 = 策略违规 & "[策略]" & 谕组(X, 位qt代称) & "=" & 谕组(X, 位谕of月基策日) & "但持仓" & vbCrLf
            End If
            命分 = 谕组(X, 位谕of月基分命)
            策分 = 谕组(X, 位谕of月基分周)
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
    End With
    WSTO.Rows(末行).RowHeight = 30
    WSTO.Range(WSTO.Cells(1, 1), WSTO.Cells(1, 14)).Merge
    '--- 标题行(行1)下边框 ---
    With WSTO.Range(WSTO.Cells(1, 1), WSTO.Cells(1, 14)).Borders(xlEdgeBottom)
        .LineStyle = xlContinuous
        .Weight = xlMedium
        .ColorIndex = 0
    End With
    末行 = 2
    WSTO.Cells(末行, 1).Value = "生成时间: " & Now()
    WSTO.Cells(末行, 1).Font.Size = 10
    WSTO.Cells(末行, 1).Font.Color = 常色三灰
    WSTO.Rows(末行).RowHeight = 10
'========================================================================================
'输出：一、持仓概览
'========================================================================================
    末行 = 3
    WSTO.Cells(末行, 1).Value = "一、持仓概览"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    WSTO.Cells(末行, 1).HorizontalAlignment = xlRight
    末行 = 4
    WSTO.Cells(末行, 1).Value = "指标"
    WSTO.Cells(末行, 2).Value = "宝福(数)"
    WSTO.Cells(末行, 3).Value = "宝福(额)"
    WSTO.Cells(末行, 4).Value = "彦仓(数)"
    WSTO.Cells(末行, 5).Value = "彦仓(额)"
    WSTO.Cells(末行, 6).Value = "合计(数)"
    WSTO.Cells(末行, 7).Value = "合计(额)"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    '--- 概览表头(行4)灰底 ---
    With WSTO.Range(WSTO.Cells(4, 1), WSTO.Cells(4, 7)).Interior
        .Color = 常色八灰
    End With
    '--- 各节标题行(行3)下边框 ---
    With WSTO.Range(WSTO.Cells(3, 1), WSTO.Cells(3, 7)).Borders(xlEdgeBottom)
        .LineStyle = xlContinuous
        .Weight = xlMedium
        .Color = 常色五靛
    End With
    Dim 概览始 As Integer: 概览始 = 末行 + 1
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "总资产(千元)"
    WSTO.Cells(末行, 3).Value = Round(福总资, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 5).Value = Round(彦总资, 1)
    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 7).Value = Round(福总资 + 彦总资, 1)
    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    WSTO.Rows(末行).Font.Bold = True
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "现金余额(千元)"
    WSTO.Cells(末行, 3).Value = Round(福现金, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 5).Value = Round(彦现金, 1)
    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 7).Value = Round(福现金 + 彦现金, 1)
    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    WSTO.Rows(末行).Font.Bold = True
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "持仓"
    WSTO.Cells(末行, 2).Value = 福票数
    WSTO.Cells(末行, 3).Value = Round(福仓额, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦票数
    WSTO.Cells(末行, 5).Value = Round(彦仓额, 1)
    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 持票数
    WSTO.Cells(末行, 7).Value = Round(总持仓额, 1)
    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    WSTO.Rows(末行).Font.Bold = True
    '--- 持仓构成（直接展开在持仓之下） ---
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  ├─ETF"
    WSTO.Cells(末行, 2).Value = 福ETF数: WSTO.Cells(末行, 3).Value = Round(福ETF额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦ETF数: WSTO.Cells(末行, 5).Value = Round(彦ETF额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = ETF数: WSTO.Cells(末行, 7).Value = Round(ETF额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  └─股票"
    WSTO.Cells(末行, 2).Value = 福股数: WSTO.Cells(末行, 3).Value = Round(福股额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦股数: WSTO.Cells(末行, 5).Value = Round(彦股额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 持票数 - ETF数: WSTO.Cells(末行, 7).Value = Round(总持仓额 - ETF额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    '交易所细分
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "   ├─上证"
    WSTO.Cells(末行, 2).Value = 福上证数: WSTO.Cells(末行, 3).Value = Round(福上证额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦上证数: WSTO.Cells(末行, 5).Value = Round(彦上证额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 上证股数: WSTO.Cells(末行, 7).Value = Round(上证股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "   ├─科创"
    WSTO.Cells(末行, 2).Value = 福科创数: WSTO.Cells(末行, 3).Value = Round(福科创额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦科创数: WSTO.Cells(末行, 5).Value = Round(彦科创额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 科创股数: WSTO.Cells(末行, 7).Value = Round(科创股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "   ├─深证"
    WSTO.Cells(末行, 2).Value = 福深证数: WSTO.Cells(末行, 3).Value = Round(福深证额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦深证数: WSTO.Cells(末行, 5).Value = Round(彦深证额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 深证股数: WSTO.Cells(末行, 7).Value = Round(深证股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "   ├─创业"
    WSTO.Cells(末行, 2).Value = 福创业数: WSTO.Cells(末行, 3).Value = Round(福创业额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦创业数: WSTO.Cells(末行, 5).Value = Round(彦创业额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 创业股数: WSTO.Cells(末行, 7).Value = Round(创业股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "   ├─北交"
    WSTO.Cells(末行, 2).Value = 福北交数: WSTO.Cells(末行, 3).Value = Round(福北交额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦北交数: WSTO.Cells(末行, 5).Value = Round(彦北交额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 北交股数: WSTO.Cells(末行, 7).Value = Round(北交股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "   └─港股"
    WSTO.Cells(末行, 2).Value = 福港股数: WSTO.Cells(末行, 3).Value = Round(福港股额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦港股数: WSTO.Cells(末行, 5).Value = Round(彦港股额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 港股数: WSTO.Cells(末行, 7).Value = Round(港股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    '--- 现金/资产/仓位 ---
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "满仓率"
    If 福总资 > 0 Then WSTO.Cells(末行, 3).Value = Format(福仓额 / 福总资, "0%")
    If 彦总资 > 0 Then WSTO.Cells(末行, 5).Value = Format(彦仓额 / 彦总资, "0%")
    If 福总资 + 彦总资 > 0 Then WSTO.Cells(末行, 7).Value = Format(总持仓额 / (福总资 + 彦总资), "0%")

    '--- 持仓构成数据行(6-13)浅灰间隔 ---
    For X = 8 To 15
        With WSTO.Range(WSTO.Cells(X, 1), WSTO.Cells(X, 7))
            .Interior.Color = RGB(245, 245, 245)
            .Font.Color = 常色五灰
        End With
    Next
    '--- 概览/持仓构成数字格式 ---
    For X = 5 To 16
        WSTO.Rows(X).HorizontalAlignment = xlRight
        WSTO.Cells(X, 1).HorizontalAlignment = xlLeft
    Next
'========================================================================================
'输出：大盘仓位限制
'========================================================================================
    Dim 指正分 As Integer, 指负分 As Integer
    Dim 指CIDL As Variant, 指月基 As String, 促动 As String
    指正分 = 0: 指负分 = 0
    '--- 评分：3个宽基指数月基带日促动方向 ---
    For Each 指CIDL In Array("sh000001", "sz399006", "sh000688")
        If 典指位.Exists(指CIDL) Then
            指月基 = 谕组(典指位(指CIDL), 位谕of月基带日)
            If Len(指月基) >= 4 Then
                促动 = Mid$(指月基, 4, 1)
                If 促动 = "▲" Or 促动 = "↗" Then 指正分 = 指正分 + 1
                If 促动 = "↘" Or 促动 = "▽" Then 指负分 = 指负分 + 1
            End If
        End If
    Next
    Dim 大盘判断 As String, 总上限 As Double
    Dim 总分 As Integer: 总分 = 指正分 - 指负分
    '--- 月基分日评分（补充维度） ---
    Dim 冲高分 As Integer: 冲高分 = 0
    Dim 冲低分 As Integer: 冲低分 = 0
    Dim 冲分1 As String, 冲分2 As String, 冲分3 As String
    Dim 指冲 As Variant
    冲分1 = "": 冲分2 = "": 冲分3 = ""
    指序号 = 0
    For Each 指CIDL In Array("sh000001", "sz399006", "sh000688")
        指序号 = 指序号 + 1
        If 典指位.Exists(指CIDL) Then
            指冲 = 谕组(典指位(指CIDL), 位谕of日冲策分)
            If VBA.IsNumeric(指冲) Then
                If 指序号 = 1 Then 冲分1 = CStr(指冲)
                If 指序号 = 2 Then 冲分2 = CStr(指冲)
                If 指序号 = 3 Then 冲分3 = CStr(指冲)
                If 指冲 >= 50 Then 冲高分 = 冲高分 + 1 Else 冲低分 = 冲低分 + 1
            End If
        End If
    Next
    Dim 总分2 As Integer: 总分2 = 总分 + (冲高分 - 冲低分)
    Select Case 总分2
        Case Is >= 4: 大盘判断 = "强好": 总上限 = 1
        Case 2, 3: 大盘判断 = "向好": 总上限 = 0.85
        Case 0, 1: 大盘判断 = "偏多": 总上限 = 0.66
        Case -1: 大盘判断 = "中性": 总上限 = 0.5
        Case -2, -3: 大盘判断 = "偏空": 总上限 = 0.33
        Case Is <= -4: 大盘判断 = "向差": 总上限 = 0.33
    End Select
    '--- 输出计算步骤到Immediate和Sheet ---
    Debug.Print "【大盘评分】上证=" & 促动1 & "(" & 冲分1 & ") 创业板=" & 促动2 & "(" & 冲分2 & ") 科创=" & 促动3 & "(" & 冲分3 & ")"
    Debug.Print "【大盘评分】促动分=" & 总分 & " 日冲分=" & (冲高分 - 冲低分) & " 总分=" & 总分2 & " => " & 大盘判断 & " 上限=" & Format(总上限, "0%")
    Dim 大盘评分明细 As String
    大盘评分明细 = "促动" & 促动1 & "/" & 促动2 & "/" & 促动3 & " 日冲" & 冲分1 & "/" & 冲分2 & "/" & 冲分3
    大盘评分明细 = 大盘评分明细 & " => 总分" & 总分2 & " " & 大盘判断 & " 上限" & Format(总上限, "0%")
    Dim 仓位始 As Integer: 仓位始 = 末行 + 1
    末行 = 末行 + 1
    WSTO.Cells(末行, 8).Value = 大盘评分明细
    WSTO.Cells(末行, 8).Font.Size = 9
    WSTO.Cells(末行, 8).Font.Color = 常色三灰
    WSTO.Range(WSTO.Cells(末行, 8), WSTO.Cells(末行, 14)).Merge
    '--- 更新概览行18：大盘仓位限制 ---
    WSTO.Cells(末行, 1).Value = "大盘仓位限制"
    WSTO.Cells(末行, 3).Value = Format(总上限, "0%")
    WSTO.Cells(末行, 5).Value = Format(总上限, "0%")
    WSTO.Cells(末行, 7).Value = Format(总上限, "0%")
    '福账户
    Dim 福上限 As Double: 福上限 = 福总资 * 总上限
    Dim 福月基目标 As Double: 福月基目标 = 福上限 * 0.2
    Dim 福周冲目标 As Double: 福周冲目标 = 福上限 * 0.4
    Dim 福日冲目标 As Double: 福日冲目标 = 福上限 * 0.4
    Dim 福月基比 As Double
    If 福上限 > 0 Then 福月基比 = 福月基额 / 福上限 Else 福月基比 = 0
    Dim 福周冲比 As Double
    If 福上限 > 0 Then 福周冲比 = 福周冲额 / 福上限 Else 福周冲比 = 0
    Dim 福日冲比 As Double
    If 福上限 > 0 Then 福日冲比 = 福日冲额 / 福上限 Else 福日冲比 = 0
    Dim 福非策额 As Double: 福非策额 = 福仓额 - 福月基额 - 福周冲额 - 福日冲额
    Dim 福非策比 As Double
    If 福上限 > 0 Then 福非策比 = 福非策额 / 福上限 Else 福非策比 = 0
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "福账户限额"
    WSTO.Cells(末行, 2).Value = "≤" & Format(总上限, "0%") & "," & Round(福上限, 1)
    WSTO.Cells(末行, 3).Value = Round(福仓额, 1) & "(" & IIf(福仓额 <= 福上限, "达标", "超额") & ")"
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 7).Value = IIf(福仓额 <= 福上限, "达标", "超额")
    WSTO.Cells(末行, 7).Font.Color = IIf(福仓额 <= 福上限, 常色主黑, 常色主红)
    WSTO.Rows(末行).Font.Bold = True
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  ├─月基(≥20%)"
    WSTO.Cells(末行, 2).Value = "≥" & Format(总上限 * 0.2, "0%") & "," & Round(福月基目标, 1)
    WSTO.Cells(末行, 3).Value = Round(福月基额, 1) & "(" & IIf(福月基额 >= 福月基目标, "达标", "缺额") & ")"
    WSTO.Cells(末行, 7).Value = IIf(福月基额 >= 福月基目标, "达标", "缺额")
    WSTO.Cells(末行, 7).Font.Color = IIf(福月基额 >= 福月基目标, 常色主黑, 常色主蓝)
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  ├─周冲(≤40%)"
    WSTO.Cells(末行, 2).Value = "≤" & Format(总上限 * 0.4, "0%") & "," & Round(福周冲目标, 1)
    WSTO.Cells(末行, 3).Value = Round(福周冲额, 1) & "(" & IIf(福周冲额 <= 福周冲目标, "达标", "超额") & ")"
    WSTO.Cells(末行, 7).Value = IIf(福周冲额 <= 福周冲目标, "达标", "超额")
    WSTO.Cells(末行, 7).Font.Color = IIf(福周冲额 <= 福周冲目标, 常色主黑, 常色主红)
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  ├─日冲(≤40%)"
    WSTO.Cells(末行, 2).Value = "≤" & Format(总上限 * 0.4, "0%") & "," & Round(福日冲目标, 1)
    WSTO.Cells(末行, 3).Value = Round(福日冲额, 1) & "(" & IIf(福日冲额 <= 福日冲目标, "达标", "超额") & ")"
    WSTO.Cells(末行, 7).Value = IIf(福日冲额 <= 福日冲目标, "达标", "超额")
    WSTO.Cells(末行, 7).Font.Color = IIf(福日冲额 <= 福日冲目标, 常色主黑, 常色主红)
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  └─非策略(=0%)"
    WSTO.Cells(末行, 2).Value = "'=0%,0"
    WSTO.Cells(末行, 3).Value = Round(福非策额, 1) & "(" & IIf(福非策额 > 0, "超额", "无目标") & ")"
    WSTO.Cells(末行, 7).Value = IIf(福非策额 > 0, "超额", "无目标")
    WSTO.Cells(末行, 7).Font.Color = IIf(福非策额 > 0, 常色主红, 常色主黑)
    Dim 彦上限 As Double: 彦上限 = 彦总资 * 总上限
    Dim 彦月基目标 As Double: 彦月基目标 = 彦上限 * 0.5
    Dim 彦周冲目标 As Double: 彦周冲目标 = 彦上限 * 0.5
    Dim 彦日冲目标 As Double: 彦日冲目标 = 彦上限 * 0.2
    Dim 彦月基比 As Double
    If 彦上限 > 0 Then 彦月基比 = 彦月基额 / 彦上限 Else 彦月基比 = 0
    Dim 彦周冲比 As Double
    If 彦上限 > 0 Then 彦周冲比 = 彦周冲额 / 彦上限 Else 彦周冲比 = 0
    Dim 彦日冲比 As Double
    If 彦上限 > 0 Then 彦日冲比 = 彦日冲额 / 彦上限 Else 彦日冲比 = 0
    Dim 彦非策额 As Double: 彦非策额 = 彦仓额 - 彦月基额 - 彦周冲额 - 彦日冲额
    Dim 彦非策比 As Double
    If 彦上限 > 0 Then 彦非策比 = 彦非策额 / 彦上限 Else 彦非策比 = 0
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "彦账户限额"
    WSTO.Cells(末行, 4).Value = "≤" & Format(总上限, "0%") & "," & Round(彦上限, 1)
    WSTO.Cells(末行, 5).Value = Round(彦仓额, 1) & "(" & IIf(彦仓额 <= 彦上限, "达标", "超额") & ")"
    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 7).Value = IIf(彦仓额 <= 彦上限, "达标", "超额")
    WSTO.Cells(末行, 7).Font.Color = IIf(彦仓额 <= 彦上限, 常色主黑, 常色主红)
    WSTO.Rows(末行).Font.Bold = True
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  ├─月基(≥50%)"
    WSTO.Cells(末行, 4).Value = "≥" & Format(总上限 * 0.5, "0%") & "," & Round(彦月基目标, 1)
    WSTO.Cells(末行, 5).Value = Round(彦月基额, 1) & "(" & IIf(彦月基额 >= 彦月基目标, "达标", "缺额") & ")"
    WSTO.Cells(末行, 7).Value = IIf(彦月基额 >= 彦月基目标, "达标", "缺额")
    WSTO.Cells(末行, 7).Font.Color = IIf(彦月基额 >= 彦月基目标, 常色主黑, 常色主蓝)
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  ├─周冲(≤50%)"
    WSTO.Cells(末行, 4).Value = "≤" & Format(总上限 * 0.5, "0%") & "," & Round(彦周冲目标, 1)
    WSTO.Cells(末行, 5).Value = Round(彦周冲额, 1) & "(" & IIf(彦周冲额 <= 彦周冲目标, "达标", "超额") & ")"
    WSTO.Cells(末行, 7).Value = IIf(彦周冲额 <= 彦周冲目标, "达标", "超额")
    WSTO.Cells(末行, 7).Font.Color = IIf(彦周冲额 <= 彦周冲目标, 常色主黑, 常色主红)
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  ├─日冲(≤20%)"
    WSTO.Cells(末行, 4).Value = "≤" & Format(总上限 * 0.2, "0%") & "," & Round(彦日冲目标, 1)
    WSTO.Cells(末行, 5).Value = Round(彦日冲额, 1) & "(" & IIf(彦日冲额 <= 彦日冲目标, "达标", "超额") & ")"
    WSTO.Cells(末行, 7).Value = IIf(彦日冲额 <= 彦日冲目标, "达标", "超额")
    WSTO.Cells(末行, 7).Font.Color = IIf(彦日冲额 <= 彦日冲目标, 常色主黑, 常色主红)
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "  └─非策略(=0%)"
    WSTO.Cells(末行, 4).Value = "'=0%,0"
    WSTO.Cells(末行, 5).Value = Round(彦非策额, 1) & "(" & IIf(彦非策额 > 0, "超额", "无目标") & ")"
    WSTO.Cells(末行, 7).Value = IIf(彦非策额 > 0, "超额", "无目标")
    WSTO.Cells(末行, 7).Font.Color = IIf(彦非策额 > 0, 常色主红, 常色主黑)
    '--- 右对齐 ---
    With WSTO
        For X = 仓位始 To 末行
            .Rows(X).HorizontalAlignment = xlRight
            .Cells(X, 1).HorizontalAlignment = xlLeft
        Next
    End With
'========================================================================================
'输出：二、行业分布
'========================================================================================
    Dim 行业始 As Integer: 行业始 = 末行 + 2
    末行 = 行业始
    WSTO.Cells(末行, 1).Value = "二、行业分布"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    WSTO.Cells(末行, 1).HorizontalAlignment = xlRight
    '--- 各节标题行(行32)下边框 ---
    With WSTO.Range(WSTO.Cells(末行, 1), WSTO.Cells(末行, 18)).Borders(xlEdgeBottom)
        .LineStyle = xlContinuous
        .Weight = xlMedium
        .Color = 常色五靛
    End With
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "行业"
    WSTO.Cells(末行, 2).Value = "持额(千元)"
    WSTO.Cells(末行, 3).Value = "持额占比"
    WSTO.Cells(末行, 4).Value = "行业限额"
    WSTO.Cells(末行, 5).Value = "对标指数"
    WSTO.Cells(末行, 6).Value = "对标CIDL"
    WSTO.Cells(末行, 7).Value = "月基策周"
    WSTO.Cells(末行, 8).Value = "月基分命"
    WSTO.Cells(末行, 9).Value = "月基分周"
    WSTO.Cells(末行, 10).Value = "仓操作"
    WSTO.Cells(末行, 15).Value = "主升数"
    WSTO.Cells(末行, 16).Value = "弱势数"
    WSTO.Cells(末行, 17).Value = "轮动状态"
    WSTO.Cells(末行, 18).Value = "建议仓位"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    '--- 行业分布表头灰底 ---
    With WSTO.Range(WSTO.Cells(末行, 1), WSTO.Cells(末行, 18)).Interior
        .Color = 常色八灰
    End With
    末行 = 末行 + 1
    For Each 行业 In 行业典集.Keys
        行业额 = 行业典集(行业)
        WSTO.Cells(末行, 1).Value = 行业
        WSTO.Cells(末行, 2).Value = Round(行业额, 1)
        WSTO.Cells(末行, 2).NumberFormatLocal = "#,##0.0"
        WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 3).Value = Format(行业额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
        WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
        '--- 行业限额 ---
        If 行业额 / IIf(总持仓额 > 0, 总持仓额, 1) > 0.3 Then
            WSTO.Cells(末行, 4).Value = "X超限"
            WSTO.Cells(末行, 4).Font.Color = 常色主红
            超限名单 = 超限名单 & "[行业]" & 行业 & "(" & Format(行业额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%") & ">30%)" & vbCrLf
        Else
            WSTO.Cells(末行, 4).Value = "未超"
            WSTO.Cells(末行, 4).Font.Color = 常色主绿
        End If
        '--- 对标指数 + 月基数据 ---
        If 行业指数典集.Exists(行业) Then
            指数信息 = 行业指数典集(行业)
            WSTO.Cells(末行, 5).Value = 指数信息(0)  '对标指数名称
            WSTO.Cells(末行, 6).Value = 指数信息(1)  '对标CIDL
            '--- 从谕组读取该标的的月基数据 ---
            If 典指位.Exists(指数信息(1)) Then
                行号指 = 典指位(指数信息(1))
                WSTO.Cells(末行, 7).Value = 谕组(行号指, 位谕of月基策周)
                WSTO.Cells(末行, 8).Value = 谕组(行号指, 位谕of月基带周)
                WSTO.Cells(末行, 9).Value = 谕组(行号指, 位谕of月基带日)
            End If
        Else
            WSTO.Cells(末行, 5).Value = "—"
        End If
        '--- 持仓股票列表 ---
        If 行业股票典集.Exists(行业) Then
            WSTO.Cells(末行, 10).Value = 行业股票典集(行业)
            WSTO.Range(WSTO.Cells(末行, 10), WSTO.Cells(末行, 14)).Merge
        End If
        '--- 轮动状态 ---
        If 行业轮动典集.Exists(行业) Then
            Dim 轮动串 As String: 轮动串 = 行业轮动典集(行业)
            Dim 主升数 As Long: 主升数 = 0
            Dim 弱势数 As Long: 弱势数 = 0
            Dim c As Long
            For c = 1 To Len(轮动串)
                Dim ch As String: ch = Mid$(轮动串, c, 1)
                If ch = "金" Or ch = "银" Then 主升数 = 主升数 + 1
                If ch = "屎" Or ch = "尿" Then 弱势数 = 弱势数 + 1
            Next
            WSTO.Cells(末行, 15).Value = 主升数
            WSTO.Cells(末行, 16).Value = 弱势数
            If 主升数 > 弱势数 And 主升数 >= 2 Then
                WSTO.Cells(末行, 17).Value = "主升"
                WSTO.Cells(末行, 18).Value = "40-50%"
            ElseIf 主升数 > 0 And 主升数 >= 弱势数 Then
                WSTO.Cells(末行, 17).Value = "轮动候选"
                WSTO.Cells(末行, 18).Value = "20-30%"
            ElseIf 主升数 = 0 And 弱势数 = 0 Then
                WSTO.Cells(末行, 17).Value = "震荡"
                WSTO.Cells(末行, 18).Value = "10-20%"
            Else
                WSTO.Cells(末行, 17).Value = "回避"
                WSTO.Cells(末行, 18).Value = "0-5%"
            End If
        End If
        末行 = 末行 + 1
    Next
    '--- 行业分布数据行浅灰间隔 ---
    Dim 末行整 As Integer
    末行整 = WSTO.UsedRange.Rows.Count
    For X = 行业始 To 末行整
        If X Mod 2 = 0 Then
            With WSTO.Range(WSTO.Cells(X, 1), WSTO.Cells(X, 14)).Interior
                .Color = RGB(242, 248, 255)
            End With
        End If
    Next
    '--- 行业合计核验，差额补"其他" ---
    Dim 行业合计 As Double: 行业合计 = 0
    For Each 行业 In 行业典集.Keys: 行业合计 = 行业合计 + 行业典集(行业): Next
    If 缺行业名单 <> "" Then
        WSTO.Cells(末行, 1).Value = "其他(未分类)"
        WSTO.Cells(末行, 2).Value = Round(总持仓额 - 行业合计, 1)
        WSTO.Cells(末行, 2).NumberFormatLocal = "#,##0.0"
        WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 3).Value = Format((总持仓额 - 行业合计) / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
        WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 4).Value = "未超"
        WSTO.Cells(末行, 5).Value = "—"
        WSTO.Cells(末行, 10).Value = Mid$(缺行业名单, 2)  '去掉开头的"、"
        WSTO.Range(WSTO.Cells(末行, 10), WSTO.Cells(末行, 14)).Merge
        WSTO.Cells(末行, 1).Font.Color = 常色三灰
        末行 = 末行 + 1
    End If
    WSTO.Rows(行业始).RowHeight = 20  '行业表头行高
'========================================================================================
'输出：三、策略分布
'========================================================================================
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "三、策略分布"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "月基策周"
    WSTO.Cells(末行, 2).Value = "票数"
    WSTO.Cells(末行, 3).Value = "票额"
    WSTO.Cells(末行, 4).Value = "票额占比"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 末行 + 1
    Dim 策表 As Variant: 策表 = Array("多长(积极)", "多长(消极)", "多长(不定)", "多被(金)", "多被(银)", "多被(唏)", "NA(空看)", "NA(空长)")
    Dim 策 As Variant, 策数 As Integer, 策额 As Double
    For Each 策 In 策表
        If 策略典集.Exists(策) Then
            策数 = 策略典集(策): 策额 = 策略典集额(策)
        Else
            策数 = 0: 策额 = 0
        End If
        WSTO.Cells(末行, 1).Value = 策
        WSTO.Cells(末行, 2).Value = 策数
        WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 3).Value = Round(策额, 1)
        WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
        WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 4).Value = Format(策额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
        WSTO.Cells(末行, 4).HorizontalAlignment = xlRight
        末行 = 末行 + 1
    Next
    '--- 平均评分 ---
    '--- 月基策日分布 ---
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "月基策日"
    WSTO.Cells(末行, 2).Value = "票数"
    WSTO.Cells(末行, 3).Value = "票额"
    WSTO.Cells(末行, 4).Value = "票额占比"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 末行 + 1
    Dim 策日A As Variant, 策日 As Variant, 策日数 As Integer, 策日额 As Double
    Dim 策日表 As Variant: 策日表 = Array(_
        Array("A", "A主"), Array("B", "B被"), Array("C", "C被"), Array("D", "D被"), _
        Array("E", "E主"), Array("F", "F被"), Array("G", "G傻"), Array("H", "H禁"))
    For Each 策日A In 策日表
        策日 = 策日A(0)
        If 策日典集.Exists(策日) Then
            策日数 = 策日典集(策日): 策日额 = 策日典集额(策日)
        Else
            策日数 = 0: 策日额 = 0
        End If
        WSTO.Cells(末行, 1).Value = 策日A(1)
        WSTO.Cells(末行, 2).Value = 策日数
        WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 3).Value = Round(策日额, 1)
        WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
        WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
        WSTO.Cells(末行, 4).Value = Format(策日额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
        WSTO.Cells(末行, 4).HorizontalAlignment = xlRight
        末行 = 末行 + 1
    Next
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
    WSTO.Cells(末行, 3).Value = "票额"
    WSTO.Cells(末行, 4).Value = "票额占比"
    With WSTO.Rows(末行).Font: .Bold = True: End With
    With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "低仓(<25%)"
    WSTO.Cells(末行, 2).Value = 仓低数
    WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 3).Value = Round(仓低额, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 4).Value = Format(仓低额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
    WSTO.Cells(末行, 4).HorizontalAlignment = xlRight
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "中仓(25%~75%)"
    WSTO.Cells(末行, 2).Value = 仓中数
    WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 3).Value = Round(仓中额, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 4).Value = Format(仓中额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
    WSTO.Cells(末行, 4).HorizontalAlignment = xlRight
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "满仓(75%~100%)"
    WSTO.Cells(末行, 2).Value = 仓满数
    WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 3).Value = Round(仓满额, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 4).Value = Format(仓满额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
    WSTO.Cells(末行, 4).HorizontalAlignment = xlRight
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "超限(>100%)"
    WSTO.Cells(末行, 1).Font.Color = IIf(仓超数 > 0, 常色主红, 常色主黑)
    WSTO.Cells(末行, 2).Value = 仓超数
    WSTO.Cells(末行, 2).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 3).Value = Round(仓超额, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 3).HorizontalAlignment = xlRight
    WSTO.Cells(末行, 4).Value = Format(仓超额 / IIf(总持仓额 > 0, 总持仓额, 1), "0%")
    WSTO.Cells(末行, 4).HorizontalAlignment = xlRight
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
    末行 = 末行 + 2
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
        末行 = 末行 + 1
        WSTO.Cells(末行, 1).Value = "类别"
        WSTO.Cells(末行, 2).Value = "名称"
        WSTO.Cells(末行, 3).Value = "具体原因"
        With WSTO.Rows(末行).Font: .Bold = True: End With
        With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
        For i = 0 To UBound(违规行)
            If 违规行(i) <> "" Then
                Dim 类 As String, 名 As String, 因 As String
                Dim 等号 As Integer
                类 = Left$(违规行(i), InStr(违规行(i), "]"))
                名 = Mid$(违规行(i), InStr(违规行(i), "]") + 1, InStr(违规行(i), "=") - InStr(违规行(i), "]") - 1)
                等号 = InStr(违规行(i), "=")
                If 等号 > 0 Then 因 = Mid$(违规行(i), 等号 + 1) Else 因 = ""
                WSTO.Cells(末行 + 1 + i, 1).Value = 类
                WSTO.Cells(末行 + 1 + i, 2).Value = 名
                WSTO.Cells(末行 + 1 + i, 3).Value = 因
            End If
        Next
        末行 = 末行 + UBound(违规行) + 1
    Else
        WSTO.Cells(末行, 1).Value = "OK策略合规"
        WSTO.Cells(末行, 1).Font.Color = 常色主绿
        WSTO.Cells(末行, 2).Value = "所有持仓符合月基策日"
        末行 = 末行 + 1
    End If
    '--- 仓周类上限 ---
    If Len(仓周违规) > 0 Then
        WSTO.Cells(末行, 1).Value = "X仓周类超限"
        WSTO.Cells(末行, 1).Font.Color = 常色主红
        Dim 仓周行 As Variant
        仓周行 = Split(仓周违规, vbCrLf)
        末行 = 末行 + 1
        WSTO.Cells(末行, 1).Value = "类别"
        WSTO.Cells(末行, 2).Value = "名称"
        WSTO.Cells(末行, 3).Value = "具体原因"
        With WSTO.Rows(末行).Font: .Bold = True: End With
        With WSTO.Rows(末行).Interior: .Color = 常色九灰: End With
        For i = 0 To UBound(仓周行)
            If 仓周行(i) <> "" Then
                Dim 仓类 As String, 仓名 As String, 仓因 As String
                Dim 仓等号 As Integer
                仓类 = Left$(仓周行(i), InStr(仓周行(i), "]"))
                仓名 = Mid$(仓周行(i), InStr(仓周行(i), "]") + 1, InStr(仓周行(i), "=") - InStr(仓周行(i), "]") - 1)
                仓等号 = InStr(仓周行(i), "=")
                If 仓等号 > 0 Then 仓因 = Mid$(仓周行(i), 仓等号 + 1) Else 仓因 = ""
                WSTO.Cells(末行 + 1 + i, 1).Value = 仓类
                WSTO.Cells(末行 + 1 + i, 2).Value = 仓名
                WSTO.Cells(末行 + 1 + i, 3).Value = 仓因
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
'输出：七、持仓明细（福仓）
'========================================================================================
    末行 = 末行 + 2
    WSTO.Cells(末行, 1).Value = "七、持仓明细"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Size = 14
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "福仓持仓明细"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Color = 常色主靛
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "代码"
    WSTO.Cells(末行, 2).Value = "名称"
    WSTO.Cells(末行, 3).Value = "行业"
    WSTO.Cells(末行, 4).Value = "持股数"
    WSTO.Cells(末行, 5).Value = "持额"
    WSTO.Cells(末行, 6).Value = "仓位比"
    WSTO.Cells(末行, 7).Value = "月基策周"
    WSTO.Cells(末行, 8).Value = "月基分命"
    WSTO.Cells(末行, 9).Value = "月基分周"
    WSTO.Cells(末行, 10).Value = "仓操作"
    WSTO.Cells(末行, 11).Value = "月基带周"
    WSTO.Cells(末行, 12).Value = "月基带日"
    WSTO.Cells(末行, 13).Value = "月基策日"
    WSTO.Cells(末行, 14).Value = "仓周类"
    WSTO.Cells(末行, 15).Value = "仓日类"
    WSTO.Cells(末行, 16).Value = "周冲策略"
    WSTO.Cells(末行, 17).Value = "周冲策分"
    WSTO.Cells(末行, 18).Value = "月基分日"
    WSTO.Cells(末行, 19).Value = "月基日H2"
    WSTO.Cells(末行, 20).Value = "策略分类"
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
                WSTO.Cells(明细行, 7).Value = 谕组(X, 位谕of月基策周)
                If VBA.IsNumeric(谕组(X, 位谕of月基分命)) Then WSTO.Cells(明细行, 8).Value = 谕组(X, 位谕of月基分命)
                If VBA.IsNumeric(谕组(X, 位谕of月基分周)) Then WSTO.Cells(明细行, 9).Value = 谕组(X, 位谕of月基分周)
                WSTO.Cells(明细行, 10).Value = 谕组(X, 位谕of仓操作)
                '策略数据
                WSTO.Cells(明细行, 11).Value = 谕组(X, 位谕of月基带周)
                WSTO.Cells(明细行, 12).Value = 谕组(X, 位谕of月基带日)
                WSTO.Cells(明细行, 13).Value = 谕组(X, 位谕of月基策日)
                WSTO.Cells(明细行, 14).Value = 谕组(X, 位谕of仓周类)
                WSTO.Cells(明细行, 15).Value = 谕组(X, 位谕of仓日类)
                WSTO.Cells(明细行, 16).Value = 谕组(X, 位谕of周冲策略)
                If VBA.IsNumeric(谕组(X, 位谕of周冲策分)) Then WSTO.Cells(明细行, 17).Value = 谕组(X, 位谕of周冲策分)
                If VBA.IsNumeric(谕组(X, 位谕of日冲策分)) Then WSTO.Cells(明细行, 18).Value = 谕组(X, 位谕of日冲策分)
                WSTO.Cells(明细行, 19).Value = 谕组(X, 位谕of月基日H2)
                '策略分类
                If 谕组(X, 位谕of月基策周) <> "" And Left$(谕组(X, 位谕of月基策周), 2) <> "NA" Then
                    WSTO.Cells(明细行, 20).Value = "月基"
                ElseIf VBA.IsNumeric(谕组(X, 位谕of周冲策分)) And 谕组(X, 位谕of周冲策分) >= 50 Then
                    WSTO.Cells(明细行, 20).Value = "周冲"
                ElseIf VBA.IsNumeric(谕组(X, 位谕of日冲策分)) And 谕组(X, 位谕of日冲策分) >= 50 Then
                    WSTO.Cells(明细行, 20).Value = "日冲"
                Else
                    WSTO.Cells(明细行, 20).Value = "非策略"
                End If
                明细行 = 明细行 + 1
            End If
    Next
'========================================================================================
'输出：七、持仓明细（彦仓）
'========================================================================================
    末行 = 明细行 + 1
    WSTO.Cells(末行, 1).Value = "彦仓持仓明细"
    WSTO.Cells(末行, 1).Font.Bold = True
    WSTO.Cells(末行, 1).Font.Color = 常色主靛
    末行 = 末行 + 1
    WSTO.Cells(末行, 1).Value = "代码"
    WSTO.Cells(末行, 2).Value = "名称"
    WSTO.Cells(末行, 3).Value = "行业"
    WSTO.Cells(末行, 4).Value = "持股数"
    WSTO.Cells(末行, 5).Value = "持额"
    WSTO.Cells(末行, 6).Value = "仓位比"
    WSTO.Cells(末行, 7).Value = "月基策周"
    WSTO.Cells(末行, 8).Value = "月基分命"
    WSTO.Cells(末行, 9).Value = "月基分周"
    WSTO.Cells(末行, 10).Value = "仓操作"
    WSTO.Cells(末行, 11).Value = "月基带周"
    WSTO.Cells(末行, 12).Value = "月基带日"
    WSTO.Cells(末行, 13).Value = "月基策日"
    WSTO.Cells(末行, 14).Value = "仓周类"
    WSTO.Cells(末行, 15).Value = "仓日类"
    WSTO.Cells(末行, 16).Value = "周冲策略"
    WSTO.Cells(末行, 17).Value = "周冲策分"
    WSTO.Cells(末行, 18).Value = "月基分日"
    WSTO.Cells(末行, 19).Value = "月基日H2"
    WSTO.Cells(末行, 20).Value = "策略分类"
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
                WSTO.Cells(明细行, 7).Value = 谕组(X, 位谕of月基策周)
                If VBA.IsNumeric(谕组(X, 位谕of月基分命)) Then WSTO.Cells(明细行, 8).Value = 谕组(X, 位谕of月基分命)
                If VBA.IsNumeric(谕组(X, 位谕of月基分周)) Then WSTO.Cells(明细行, 9).Value = 谕组(X, 位谕of月基分周)
                WSTO.Cells(明细行, 10).Value = 谕组(X, 位谕of仓操作)
                '策略数据
                WSTO.Cells(明细行, 11).Value = 谕组(X, 位谕of月基带周)
                WSTO.Cells(明细行, 12).Value = 谕组(X, 位谕of月基带日)
                WSTO.Cells(明细行, 13).Value = 谕组(X, 位谕of月基策日)
                WSTO.Cells(明细行, 14).Value = 谕组(X, 位谕of仓周类)
                WSTO.Cells(明细行, 15).Value = 谕组(X, 位谕of仓日类)
                WSTO.Cells(明细行, 16).Value = 谕组(X, 位谕of周冲策略)
                If VBA.IsNumeric(谕组(X, 位谕of周冲策分)) Then WSTO.Cells(明细行, 17).Value = 谕组(X, 位谕of周冲策分)
                If VBA.IsNumeric(谕组(X, 位谕of日冲策分)) Then WSTO.Cells(明细行, 18).Value = 谕组(X, 位谕of日冲策分)
                WSTO.Cells(明细行, 19).Value = 谕组(X, 位谕of月基日H2)
                '策略分类
                If 谕组(X, 位谕of月基策周) <> "" And Left$(谕组(X, 位谕of月基策周), 2) <> "NA" Then
                    WSTO.Cells(明细行, 20).Value = "月基"
                ElseIf VBA.IsNumeric(谕组(X, 位谕of周冲策分)) And 谕组(X, 位谕of周冲策分) >= 50 Then
                    WSTO.Cells(明细行, 20).Value = "周冲"
                ElseIf VBA.IsNumeric(谕组(X, 位谕of日冲策分)) And 谕组(X, 位谕of日冲策分) >= 50 Then
                    WSTO.Cells(明细行, 20).Value = "日冲"
                Else
                    WSTO.Cells(明细行, 20).Value = "非策略"
                End If
                明细行 = 明细行 + 1
            End If
    Next
'========================================================================================
'输出：八、组合调整建议
'========================================================================================
    末行 = 明细行 + 2
    WSTO.Cells(末行, 1).Value = "八、组合调整建议（最小修改方案）"
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
                WSTO.Cells(末行, 3).Value = "减仓至仓位比<=1"
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
                WSTO.Cells(末行, 3).Value = "减仓至组合占比<=上限"
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
    '全局格式化：边框 + 底色
    '========================================================================================
    末行整 = WSTO.UsedRange.Rows.Count
    Dim 末列整 As Integer
    末列整 = 20  '最大列数
    '--- 全表细边框 ---
    With WSTO.Range(WSTO.Cells(3, 1), WSTO.Cells(末行整, 末列整)).Borders
        .LineStyle = xlContinuous
        .Weight = xlThin
        .ColorIndex = 15  '灰
    End With
'========================================================================================
'列宽调整
'========================================================================================
    WSTO.Columns("A:Z").ColumnWidth = 12
    WSTO.Columns("A").ColumnWidth = 18
    WSTO.Columns("I").ColumnWidth = 15
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
'仅包含成分股高度重叠(>=70%)的精准匹配，不精确的不计入
'编制日期：2026-08-02  详见MP2_研究投资组合管理.md 第六章
'########################################################################################
Public Function UTL族群引擎_行业指数映射() As Dictionary
    Dim 典 As New Dictionary
    '========================================================================================
    '金融族
    '========================================================================================
    典.Add Key:="银行", Item:=Array("中证银行", "sz399986", "指数")
    典.Add Key:="证券期货", Item:=Array("证券公司", "sz399975", "指数")
    典.Add Key:="保险", Item:=Array("保险主题", "sz399809", "指数")
    典.Add Key:="多元金融", Item:=Array("中证金融", "sz399934", "指数")
    '========================================================================================
    '电子制造族
    '========================================================================================
    典.Add Key:="半导体", Item:=Array("半导体ETF", "sh512480", "ETF")
    典.Add Key:="消费电子", Item:=Array("消费电子ETF", "sz159732", "ETF")
    典.Add Key:="电子元件", Item:=Array("电子ETF", "sz159997", "ETF")
    典.Add Key:="电源设备", Item:=Array("中证新能", "sz399808", "指数")
    典.Add Key:="IT设备", Item:=Array("国证通信", "sz399389", "指数")
    '========================================================================================
    '文化族
    '========================================================================================
    典.Add Key:="文化传媒", Item:=Array("国证文化", "sz399397", "指数")
    典.Add Key:="影视动漫", Item:=Array("中证传媒", "sz399971", "指数")
    典.Add Key:="游戏", Item:=Array("中证传媒", "sz399971", "指数")
    典.Add Key:="教育", Item:=Array("教育ETF", "sh513360", "ETF")
    典.Add Key:="景点", Item:=Array("旅游ETF", "sz159766", "ETF")
    典.Add Key:="旅游综合", Item:=Array("旅游ETF", "sz159766", "ETF")
    典.Add Key:="其他休闲服务", Item:=Array("旅游ETF", "sz159766", "ETF")
    '========================================================================================
    '互联网族
    '========================================================================================
    典.Add Key:="软件开发", Item:=Array("中证信息", "sz399935", "指数")
    典.Add Key:="软件服务", Item:=Array("中证信息", "sz399935", "指数")
    典.Add Key:="通信设备", Item:=Array("国证通信", "sz399389", "指数")
    典.Add Key:="通信服务", Item:=Array("国证通信", "sz399389", "指数")
    典.Add Key:="营销传播", Item:=Array("中证传媒", "sz399971", "指数")
    典.Add Key:="互联网传媒", Item:=Array("中证传媒", "sz399971", "指数")
    '========================================================================================
    '周期族
    '========================================================================================
    典.Add Key:="有色金属", Item:=Array("国证有色", "sz399395", "指数")
    典.Add Key:="钢铁", Item:=Array("国证钢铁", "sz399440", "指数")
    典.Add Key:="煤炭开采", Item:=Array("中证煤炭", "sz399998", "指数")
    典.Add Key:="电力", Item:=Array("绿色电力", "sz399438", "指数")
    典.Add Key:="环境保护", Item:=Array("中证环保", "sh000827", "指数")
    典.Add Key:="石油石化", Item:=Array("国证油气", "sz399439", "指数")
    典.Add Key:="黄金", Item:=Array("国证有色", "sz399395", "指数")
    '========================================================================================
    '电气制造族
    '========================================================================================
    典.Add Key:="航天国防", Item:=Array("中证军工", "sz399967", "指数")
    典.Add Key:="光伏设备", Item:=Array("中证新能", "sz399808", "指数")
    典.Add Key:="风电设备", Item:=Array("中证新能", "sz399808", "指数")
    典.Add Key:="自动化设备", Item:=Array("机器人50", "sz399283", "指数")
    '========================================================================================
    '机械制造族
    '========================================================================================
    典.Add Key:="机床设备", Item:=Array("工业4.0", "sz399803", "指数")
    '========================================================================================
    '汽车族
    '========================================================================================
    典.Add Key:="汽车制造", Item:=Array("新能源车", "sz399417", "指数")
    典.Add Key:="汽车零部件", Item:=Array("新能源车", "sz399417", "指数")
    典.Add Key:="电池", Item:=Array("中证新能", "sz399808", "指数")
    '========================================================================================
    '运输族
    '========================================================================================
    典.Add Key:="仓储物流", Item:=Array("国证物流", "sz399353", "指数")
    典.Add Key:="航空运输", Item:=Array("国证交运", "sz399433", "指数")
    典.Add Key:="机场", Item:=Array("国证交运", "sz399433", "指数")
    典.Add Key:="铁路运输", Item:=Array("国证交运", "sz399433", "指数")
    典.Add Key:="高速公路", Item:=Array("国证交运", "sz399433", "指数")
    典.Add Key:="水上运输", Item:=Array("国证交运", "sz399433", "指数")
    典.Add Key:="港口", Item:=Array("国证交运", "sz399433", "指数")
    '========================================================================================
    '基建族
    '========================================================================================
    典.Add Key:="工程建筑", Item:=Array("基建工程", "sz399995", "指数")
    典.Add Key:="建材", Item:=Array("国证基建", "sz399359", "指数")
    典.Add Key:="装修装饰", Item:=Array("基建工程", "sz399995", "指数")
    典.Add Key:="房地产", Item:=Array("国证地产", "sz399393", "指数")
    典.Add Key:="水泥", Item:=Array("国证基建", "sz399359", "指数")
    '========================================================================================
    '农业族
    '========================================================================================
    典.Add Key:="农药", Item:=Array("国证农牧", "sz399435", "指数")
    典.Add Key:="农林", Item:=Array("国证农牧", "sz399435", "指数")
    典.Add Key:="农业服务", Item:=Array("国证农牧", "sz399435", "指数")
    典.Add Key:="牧渔", Item:=Array("国证农牧", "sz399435", "指数")
    典.Add Key:="饲料加工", Item:=Array("国证粮食", "sz399365", "指数")
    典.Add Key:="动物保健", Item:=Array("国证农牧", "sz399435", "指数")
    '========================================================================================
    '化工族
    '========================================================================================
    典.Add Key:="化学制品", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add Key:="化学原料", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add Key:="化肥", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add Key:="化纤", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add Key:="橡胶", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add Key:="塑料", Item:=Array("化工ETF", "sz159870", "ETF")
    典.Add Key:="新材料", Item:=Array("新材料ETF", "sh516360", "ETF")
    '========================================================================================
    '医药族
    '========================================================================================
    典.Add Key:="医疗美容", Item:=Array("中证医药", "sz399933", "指数")
    典.Add Key:="医药制造", Item:=Array("中证医药", "sz399933", "指数")
    典.Add Key:="中药", Item:=Array("中证医药", "sz399933", "指数")
    典.Add Key:="生物制品", Item:=Array("生物医药", "sz399441", "指数")
    典.Add Key:="医疗服务", Item:=Array("中证医疗", "sz399989", "指数")
    典.Add Key:="医药流通", Item:=Array("中证医药", "sz399933", "指数")
    典.Add Key:="医疗器械", Item:=Array("中证医疗", "sz399989", "指数")
    '========================================================================================
    '消费族
    '========================================================================================
    典.Add Key:="酿酒", Item:=Array("中证白酒", "sz399997", "指数")
    典.Add Key:="饮料制造", Item:=Array("中证酒", "sz399987", "指数")
    典.Add Key:="食品加工", Item:=Array("国证食品", "sz399396", "指数")
    典.Add Key:="酒店餐饮", Item:=Array("国证服务", "sz399320", "指数")
    典.Add Key:="服装", Item:=Array("中证消费", "sz399932", "指数")
    典.Add Key:="家电", Item:=Array("中证消费", "sz399932", "指数")
    典.Add Key:="家具制造", Item:=Array("中证消费", "sz399932", "指数")
    '========================================================================================
    '公共族
    '========================================================================================
    典.Add Key:="公用事业", Item:=Array("绿色电力", "sz399438", "指数")
    '========================================================================================
    Set UTL族群引擎_行业指数映射 = 典
End Function

'========================================================================================
'========================================================================================
' 跨码管理_取名称值 — 按名称读取常量值（与设置代码对应）
'========================================================================================
' 设置方式：ThisWorkbook.Names.Add Name:=名称, RefersTo:="=" & 数值
' 读取方式：CDbl(Mid(ThisWorkbook.Names(名称).RefersTo, 2))
' 不依赖活动工作簿，不遍历，不调用 Evaluate
'========================================================================================
Private Function 跨码管理_取名称值(ByVal 名称 As String) As Double
    On Error Resume Next
    跨码管理_取名称值 = CDbl(Mid(ThisWorkbook.Names(名称).RefersTo, 2))
End Function

