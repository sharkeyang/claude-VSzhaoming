Attribute VB_Name = "UTL_基1CID"


'########################################################################################
'########################################################################################
'#####################################    CID相关   ######################################
'########################################################################################
'########################################################################################
'========================================================================================
'CID判断 — 热路径优化：长度+首字符快速判断，兜底Like保持语义一致
'
' 判断规则（按优先级）：
'  1) 6位纯数字 → 算代码（三分类：中股票）
'  2) 8位且前缀 sh/sz/bj → A股全码（三分类：中股票/中股指/中股基 依短码首段区分）
'  3) 7位且前缀 r_hk/s_us → 港股/美股
'  4) 10位且前缀 HKIX. → 港股指数
'  5) >=4位且前缀 US. → 美股
'  6) 6位且 fx#####0 → 期货
'  7) 6-8位兜底 Like 通配符 → 覆盖未列出的 A股/港股/美股格式
' 三分类 = [是中股票, 是中股指, 是中股基]
' 是代码 = 以上所有规则取并集
Function UBCID是代码(CIDV As Variant) As Boolean
    Dim lenV As Long
    lenV = Len(CIDV)
    If lenV = 0 Then Exit Function

    ' 6位纯数字 → 任意6位数字都算代码
    If lenV = 6 And IsNumeric(CIDV) Then
        UBCID是代码 = True
    ' 8位 → sh/sz/bj前缀的全码
    ElseIf lenV = 8 Then
        Dim p2 As String
        p2 = LCase$(Mid$(CIDV, 1, 2))
        If p2 = "sh" Or p2 = "sz" Or Left$(CIDV, 2) = "bj" Then UBCID是代码 = True
    ' 7位 → r_hk##### / s_us#####
    ElseIf lenV = 7 Then
        If Left$(CIDV, 4) = "r_hk" Or Left$(CIDV, 4) = "s_us" Then UBCID是代码 = True
    ' 10位 → HKIX.#####
    ElseIf lenV = 10 And Left$(CIDV, 5) = "HKIX." Then
        UBCID是代码 = True
    ' >=4位 → US.*
    ElseIf lenV >= 4 And Left$(CIDV, 3) = "US." Then
        UBCID是代码 = True
    ' 6位 → fx#####0
    ElseIf lenV = 6 And Left$(CIDV, 2) = "fx" And Right$(CIDV, 1) = "0" Then
        UBCID是代码 = True
    ' 6-8位兜底 → Like通配符匹配
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
                    c3 = Asc(Mid$(CIDV, 3, 1))
                    ' sh60/sh68 → 股票; sh000 → 指数; sh5 → 基金
                    If c3 = &H36 Or c3 = &H38 Then
                        是中股票 = True
                    ElseIf Mid$(CIDV, 3, 3) = "000" Then
                        是中股指 = True
                    ElseIf Mid$(CIDV, 3, 1) = "5" Then
                        是中股基 = True
                    End If

                Case "sz"
                    c3 = Asc(Mid$(CIDV, 3, 1))
                    ' sz00/sz30 → 股票; sz399 → 指数; sz15 → 基金
                    If c3 = &H30 Or c3 = &H33 Then
                        是中股票 = True
                    ElseIf Mid$(CIDV, 3, 3) = "399" Then
                        是中股指 = True
                    ElseIf Mid$(CIDV, 3, 2) = "15" Then
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
'判断市板
'========================================================================================
Function UBCID设置市板(CIDL As String, 市日 As Date) As String
    Dim 市板 As String
    If UBCID是中股指(CIDL) = True Then
        市板 = 常市板指
    ElseIf UBCID是中股基(CIDL) = True Then
        市板 = 常市板基
    ElseIf CIDL Like 常通配全码北交股 Then
        市板 = 常市板票Qb
    ElseIf CIDL Like 常通配全码上科股 Then
        市板 = 常市板票Q8
    ElseIf UBCID是中股票(CIDL) Then
        If 市日 >= 常设市日隔离 Then
            市板 = 常市板票Qo
        ElseIf CIDL Like 常通配全码深创股 Then
            市板 = 常市板票Q3
        ElseIf CIDL Like 常通配全码深主股 Then
            市板 = 常市板票Q0
        ElseIf CIDL Like 常通配全码上主股 Then
            市板 = 常市板票Q6
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
