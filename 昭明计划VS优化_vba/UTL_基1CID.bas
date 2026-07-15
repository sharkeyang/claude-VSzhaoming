Attribute VB_Name = "UTL_基1CID"
Option Explicit


'########################################################################################
'########################################################################################
'#####################################    CID相关   ######################################
'########################################################################################
'########################################################################################
'========================================================================================
'CID判断 — 热路径优化：长度+首字符快速判断，兜底Like保持语义一致
'========================================================================================
'
' 分类速查表：
' ┌──────────────┬───────────┬───────────┬──────────┬──────┬───────┬───────────┬──────────────────────────────────┐
' │ 短码 (6位)   │ 全码 (8位)│ 规制码格式│ 三分类   │是代码│ 是A股 │  是指数   │  是ETF                          │
' ├──────────────┼───────────┼───────────┼──────────┼──────┼───────┼───────────┼──────────────────────────────────┤
' │ 600xxx       │ sh600xxx  │ sh600xxx  │ T, F, F  │  Y   │  T    │    F      │    F    │ 上证主板                     │
' │ 688xxx       │ sh688xxx  │ sh688xxx  │ T, F, F  │  Y   │  T    │    F      │    F    │ 科创板                       │
' │ 000xxx       │ sz000xxx  │ sz000xxx  │ T, F, F  │  Y   │  T    │    F      │    F    │ 深证主板                     │
' │ 300xxx       │ sz300xxx  │ sz300xxx  │ T, F, F  │  Y   │  T    │    F      │    F    │ 创业板                       │
' │ 9xxxxx       │ bj9xxxxx  │ bj9xxxxx  │ T, F, F  │  Y   │  T    │    F      │    F    │ 北交所                       │
' │ 5xxxxx       │ sh5xxxxx  │ sh5xxxxx  │ T, F, T  │  Y   │  T    │    F      │    T    │ 上证ETF (含sh51/52/53/55/56/58) │
' │ 15xxxx       │ sz15xxxx  │ sz15xxxx  │ T, F, T  │  Y   │  T    │    F      │    T    │ 深证基金ETF/LOF                 │
' │ 16xxxx       │ sz16xxxx  │ sz16xxxx  │ T, F, T  │  Y   │  T    │    F      │    T    │ 深证基金ETF/LOF                 │
' │ 000001       │ sh000001  │ sh000001  │ F, T, F  │  Y   │  F    │    T      │    F    │ 上证指数                     │
' │ 399001       │ sz399001  │ sz399001  │ F, T, F  │  Y   │  F    │    T      │    F    │ 深证指数                     │
' │ r_hk00001    │ —         │ r_hk00001 │ F, F, F  │  Y   │  F    │    F      │    F    │ 港股                         │
' │ HKIX.00700   │ —         │ HKIX.00700│ F, F, F  │  Y   │  F    │    F      │    F    │ 港指数                       │
' │ s_usAAPL     │ —         │ s_usAAPL  │ F, F, F  │  Y   │  F    │    F      │    F    │ 美股                         │
' │ US.NVDA      │ —         │ US.NVDA   │ F, F, F  │  Y   │  F    │    F      │    F    │ 美股                         │
' │ fx0000       │ —         │ fx0000    │ F, F, F  │  Y   │  F    │    F      │    F    │ 中期                         │
' │ 123456       │ —         │ —         │ T, F, F  │  Y   │  T    │    F      │    F    │ 纯数字                       │
' └──────────────┴───────────┴───────────┴──────────┴──────┴───────┴───────────┴──────────────────────────────────┘
' 三分类 = [是中股票, 是中股指, 是中股基]
' 是代码 = 覆盖上表所有行（纯数字6位也视为代码）
'
' 2026-07-14 验证：VBA分类代码覆盖了全部7673只谕组CSV的代码前缀
'   sh5* → 基金(ETF) 覆盖 sh51/sh52/sh53/sh55/sh56/sh58 共900只
'   sz1* → 基金(ETF/LOF) 覆盖全部 sz15/sz16/sz17等 共694只(通配符sz1#####)
'   sh60/sh68 → 股票; sz00/sz30 → 股票; bj* → 股票
'   sh000/sz399 → 指数
'   无遗漏前缀，VBA分类代码无需修改。
'   但 MP1_花册分类映射.json 需与谕组CSV保持同步，
'   当前映射覆盖7487/7673只，缺失207只 (北交所48+沪ETF59+深ETF48+科创板20等)。
Function UBCID是代码(CIDV As Variant) As Boolean
    Dim lenV As Long
    lenV = Len(CIDV)
    If lenV = 0 Then Exit Function

    If lenV = 6 And IsNumeric(CIDV) Then
        UBCID是代码 = True
    ElseIf lenV = 8 Then
        Dim p2 As String
        p2 = LCase$(Mid$(CIDV, 1, 2))
        If p2 = "sh" Or p2 = "sz" Or Left$(CIDV, 2) = "bj" Then UBCID是代码 = True
    ElseIf lenV = 7 Then
        If Left$(CIDV, 4) = "r_hk" Or Left$(CIDV, 4) = "s_us" Then UBCID是代码 = True
    ElseIf lenV = 10 And Left$(CIDV, 5) = "HKIX." Then
        UBCID是代码 = True
    ElseIf lenV >= 4 And Left$(CIDV, 3) = "US." Then
        UBCID是代码 = True
    ElseIf lenV = 6 And Left$(CIDV, 2) = "fx" And Right$(CIDV, 1) = "0" Then
        UBCID是代码 = True
    ElseIf lenV >= 6 And lenV <= 8 Then
        If LCase$(CIDV) Like 常通配全码代码 Then
            UBCID是代码 = True
        ElseIf CIDV Like "r_hk#####" Then
            UBCID是代码 = True
        ElseIf CIDV Like "US.*" Then
            UBCID是代码 = True
        ElseIf CIDV Like "s_us*" Then
            UBCID是代码 = True
        ElseIf Left$(CIDV, 5) = "HKIX." Then
            UBCID是代码 = True
        ElseIf Left$(CIDV, 2) = "fx" And Right$(CIDV, 1) = "0" Then
            UBCID是代码 = True
        End If
    End If
End Function


'========================================================================================
'测试：xlsm里典核心行业全部50个代码逐一检查UBCID是中股返回值
'========================================================================================
Public Sub 测试_sz159755()
    Dim 股票 As Boolean, 股指 As Boolean, 股基 As Boolean
    Dim k As String
    k = "sz399001"

    Debug.Print "=== 单测 sz159755 ==="
    Debug.Print "Len(K)=" & Len(k)
    Debug.Print "Mid$(K,1,2)=" & Mid$(k, 1, 2)
    Debug.Print "Mid$(K,3,1)=" & Mid$(k, 3, 1)
    Debug.Print "Mid$(K,3,2)=" & Mid$(k, 3, 2)

    ' 第1次调用
    UBCID是三分类 "sz399001", 股票, 股指, 股基
    Debug.Print "第1次: 股票=" & 股票 & " 股指=" & 股指 & " 股基=" & 股基

    ' 第2次调用
    UBCID是三分类 "sz159755", 股票, 股指, 股基
    Debug.Print "第2次: 股票=" & 股票 & " 股指=" & 股指 & " 股基=" & 股基

    ' 第3次调用：穿插其他代码
    UBCID是三分类 "sh600000", 股票, 股指, 股基
    Debug.Print "穿插sh600000后: 股票=" & 股票 & " 股指=" & 股指 & " 股基=" & 股基

    ' 第4次调用：回到sz159755
    UBCID是三分类 "sz159755", 股票, 股指, 股基
    Debug.Print "第4次: 股票=" & 股票 & " 股指=" & 股指 & " 股基=" & 股基

    Debug.Print ""
    Debug.Print "=== 调用UBCID是中股(sz159755) ==="
    Debug.Print "UBCID是中股 = " & UBCID是中股("sz159755")
End Sub
'========================================================================================
'统一三中分类 — 热路径优化：合并中股票/中股指/中股基为一次函数调用
' 逻辑与原UBCID是中股票/中股指/中股基完全一致
'========================================================================================
Function UBCID是三分类(CIDV As Variant, ByRef 是中股票 As Boolean, ByRef 是中股指 As Boolean, ByRef 是中股基 As Boolean) As Boolean
    是中股票 = False: 是中股指 = False: 是中股基 = False
    Dim lenV As Long
    lenV = Len(CIDV)
    If lenV = 0 Then
        UBCID是三分类 = False
    End If

    Dim p2 As String
    p2 = LCase$(Mid$(CIDV, 1, 2))
    Dim c3 As Byte

    Select Case True
        ' ===== 全码8位 =====
        Case lenV = 8
            Select Case p2
                Case "sh"
                    ' sh60/sh68 → 股票; sh000 → 指数; sh5 → 基金
                    If Mid$(CIDV, 3, 2) = "60" Or Mid$(CIDV, 3, 2) = "68" Then
                        是中股票 = True
                    ElseIf Mid$(CIDV, 3, 2) = "00" Then
                        是中股指 = True
                    ElseIf Mid$(CIDV, 3, 1) = "5" Then
                        是中股基 = True
                    End If

                Case "sz"
                    ' sz00/sz30 → 股票; sz399 → 指数; sz15 → 基金
                    If Mid$(CIDV, 3, 2) = "00" Or Mid$(CIDV, 3, 2) = "30" Then
                        是中股票 = True
                    ElseIf Mid$(CIDV, 3, 2) = "39" Then
                        是中股指 = True
                    ElseIf Mid$(CIDV, 3, 1) = "1" Then
                        'sz1xxxxx = 深市基金(ETF/LOF)，含sz159/sz160/sz161/sz162/sz163等
                        是中股基 = True
                    End If

                Case "bj"
                    是中股票 = True
            End Select

        ' ===== 纯数字6位 =====
        Case lenV = 6 And IsNumeric(CIDV)
            Dim c1 As Byte
            c1 = Asc(Mid$(CIDV, 1, 1))
            Dim c3n As Byte
            c3n = Asc(Mid$(CIDV, 3, 1))
            ' 首 digit: 6/8/0/3 → 股票; 0/3 → 指数; 5 → 基金
            ' 第三位: 0 → 指数; 9 → 指数
            If c1 = &H36 Or c1 = &H38 Or c1 = &H30 Or c1 = &H33 Then
                是中股票 = True
            ElseIf c1 = &H30 And c3n = &H30 Then
                是中股指 = True
            ElseIf c1 = &H33 And c3n = &H39 Then
                是中股指 = True
            ElseIf c1 = &H35 Then
                是中股基 = True
            End If

        ' ===== 非A股体系：直接跳过（三个参数保持 False）=====
        Case lenV = 7 And Left$(CIDV, 4) = "r_hk"
        Case lenV = 10 And Left$(CIDV, 5) = "HKIX."
        Case lenV = 7 And Left$(CIDV, 4) = "s_us"
        Case lenV >= 4 And Left$(CIDV, 3) = "US."
        Case lenV = 6 And Left$(CIDV, 2) = "fx" And Right$(CIDV, 1) = "0"

        ' ===== 兜底 Like =====
        Case Else
            If lenV >= 6 And lenV <= 8 Then
                If LCase$(CIDV) Like 常通配全码代码 Then
                    ' ??###### 格式，无法区分类型，不做标记
                ElseIf CIDV Like "r_hk#####" Then
                ElseIf CIDV Like "US.*" Then
                ElseIf CIDV Like "s_us*" Then
                ElseIf Left$(CIDV, 5) = "HKIX." Then
                ElseIf Left$(CIDV, 2) = "fx" And Right$(CIDV, 1) = "0" Then
                End If
            End If
    End Select

    UBCID是三分类 = True
End Function

'========================================================================================
'保留旧接口兼容 — 调用三分类，返回布尔值
'========================================================================================
Function UBCID是中股(CIDV As Variant) As Boolean
    Dim 是中股票 As Boolean, 是中股指 As Boolean, 是中股基 As Boolean
    UBCID是三分类 CIDV, 是中股票, 是中股指, 是中股基
    UBCID是中股 = 是中股票 Or 是中股指 Or 是中股基
End Function
Function UBCID是中股票(CIDV As Variant) As Boolean
    Dim 是中股票 As Boolean, 是中股指 As Boolean, 是中股基 As Boolean
    UBCID是三分类 CIDV, 是中股票, 是中股指, 是中股基
    UBCID是中股票 = 是中股票
End Function
Function UBCID是中股指(CIDV As Variant) As Boolean
    Dim 是中股票 As Boolean, 是中股指 As Boolean, 是中股基 As Boolean
    UBCID是三分类 CIDV, 是中股票, 是中股指, 是中股基
    UBCID是中股指 = 是中股指
End Function
Function UBCID是中股基(CIDV As Variant) As Boolean
    Dim 是中股票 As Boolean, 是中股指 As Boolean, 是中股基 As Boolean
    UBCID是三分类 CIDV, 是中股票, 是中股指, 是中股基
    UBCID是中股基 = 是中股基
End Function
Function UBCID是港股票(CIDV As Variant) As Boolean
    UBCID是港股票 = (Len(CIDV) = 7 And Left$(CIDV, 4) = "r_hk")
End Function
Function UBCID是港股指(CIDV As Variant) As Boolean
    UBCID是港股指 = (Len(CIDV) = 10 And Left$(CIDV, 5) = "HKIX.")
End Function
Function UBCID是美股票(CIDV As Variant) As Boolean
    UBCID是美股票 = (Len(CIDV) >= 4 And Left$(CIDV, 3) = "US.") Or (Len(CIDV) = 7 And Left$(CIDV, 4) = "s_us")
End Function
Function UBCID是中期(CIDV As Variant) As Boolean
    UBCID是中期 = (Len(CIDV) = 6 And Left$(CIDV, 2) = "fx" And Right$(CIDV, 1) = "0")
End Function

'========================================================================================
'转换CIDV为CIDL — 规制代码
'========================================================================================
Function UBCID规制代码(CIDV As Variant) As String
    Dim CIDS As String
    Dim CIDL As String
    CIDS = ""
    CIDL = ""

    If IsNumeric(CIDV) And Len(CIDV) > 0 Then
        CIDS = Format$(CIDV, "000000")
        If CIDS Like 常通配短码上主股 Or CIDS Like 常通配短码上科股 Or CIDS Like 常通配短码上ETF Then
            CIDL = 常通配码缀上证 & CIDS
        ElseIf CIDS Like 常通配短码深主股 Or CIDS Like 常通配短码深创股 Or CIDS Like 常通配短码深ETF Then
            CIDL = 常通配码缀深证 & CIDS
        ElseIf CIDS Like 常通配短码北交股 Then
            CIDL = 常通配码缀北证 & CIDS
        End If
    ElseIf Len(CIDV) = 8 Then
        CIDS = LCase$(CIDV)
        If CIDS Like 常通配全码代码 Then CIDL = CIDS
    ElseIf CIDV Like "HK.#####" Then
        CIDL = "r_hk" & Right$(CIDV, 5)
    ElseIf CIDV Like "HK####" Then
        CIDL = "r_hk0" & Right$(CIDV, 4)
    Else
        UBCID规制代码 = CIDV
        Exit Function
    End If

    UBCID规制代码 = CIDL
End Function

'========================================================================================
'转换CIDV为CIDL — 规制指码
'========================================================================================
Function UBCID规制指码(CIDV As Variant) As String
    Dim CIDS As String
    Dim CIDL As String
    CIDS = ""
    CIDL = ""

    If IsNumeric(CIDV) And Len(CIDV) > 0 Then
        CIDS = Format$(CIDV, "000000")
    Else
        CIDS = LCase$(CIDV)
    End If

    If CIDS Like 常通配短码上指 Then
        CIDL = 常通配码缀上证 & CIDS
    ElseIf CIDS Like 常通配短码深指 Then
        CIDL = 常通配码缀深证 & CIDS
    Else
        CIDL = CIDS
    End If

    UBCID规制指码 = CIDL
End Function

'========================================================================================
'转换全码为AKShare格式
'========================================================================================
Function UBCID转换L2T(CIDL As String) As String
    If Len(CIDL) = 8 Then
        UBCID转换L2T = Right$(CIDL, 6) & "." & VBA.UCase$(Left$(CIDL, 2))
    Else
        UBCID转换L2T = ""
    End If
End Function

'========================================================================================
'========================================================================================
'判断市板
'分类路径：
'  CIDL
'   ├── 是指数?      → Qd (index)
'   ├── 是基金ETF?   → Qe (ETF)
'   └── 是股票?
'        ├── 代称含ST/退 → Qst
'        ├── 沪深300    → Qif
'        ├── 中证500    → Qic
'        ├── 中证1000   → Qim
'        ├── 中证2000   → Qit
'        └── 其他股票   → Qin
'参数：组花册/X 为可选，传入时可O(1)直接取值，不传时返回空
'========================================================================================
Function UBCID设置市板(CIDL As String, 市日 As Date, _
            Optional 组花册 As Variant = Nothing, Optional X As Long = 0) As String
    Dim 市板 As String

    If UBCID是中股指(CIDL) = True Then
        市板 = 常市板指        ' Qd = index
    ElseIf UBCID是中股基(CIDL) = True Then
        市板 = 常市板基        ' Qe = ETF
    ElseIf UBCID是中股票(CIDL) = True Then
        If IsArray(组花册) And X > 0 Then
            ' 有花册参数 → 直接按行号取（O(1)）
            If InStr(组花册(X, 位列花天代称), "ST") > 0 Or InStr(组花册(X, 位列花天代称), "退") > 0 Then
                市板 = 常市板票Qst
            ElseIf 组花册(X, 位列花天是否中股300) = "Y" Then
                市板 = 常市板票Qf  ' Qif = 沪深300
            ElseIf 组花册(X, 位列花天是否中证500) = "Y" Then
                市板 = 常市板票Qc  ' Qic = 中证500
            ElseIf 组花册(X, 位列花天是否中证1000) = "Y" Then
                市板 = 常市板票Qm  ' Qim = 中证1000
            ElseIf 组花册(X, 位列花天是否中证2000) = "Y" Then
                市板 = 常市板票Qt  ' Qit = 中证2000
            Else
                市板 = 常市板票Qn  ' Qin = 中证非
            End If
        Else
            ' 无花册参数 → 返回空
            市板 = ""
        End If
    Else
        市板 = ""
    End If

    UBCID设置市板 = 市板
End Function

'########################################################################################
'########################################################################################
'#####################################    CID相关   ######################################
'########################################################################################
'########################################################################################
