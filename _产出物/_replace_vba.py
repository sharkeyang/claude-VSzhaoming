# 替换函数
with open('d:/@VSwork/VS昭明计划VBA优化/昭明计划VS优化_vba/PX算研_RAP算展1引擎.bas', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到XL算展数程跨期函数
start = content.find('Function XL算展数程跨期(')
end = content.find('End Function', start)
end = content.find('End Function', end + 13) + 12  # 第二个End Function

old = content[start:end]

new = """Function XL算展数程跨期( _
          ARRLLL As Variant _
        , 指定代码 As String _
        , Optional ByVal 指定结期上限 As Variant _
        , Optional ByVal 典腾实 As Variant _
        , Optional ByRef 谕组 As Variant _
        , Optional 被研算法 As String = "" _
        , Optional 被研期类 As String = "" _
        ) As Integer
'========================================================================================
'三步组合：生成历史 -> 生成神谕 -> 算法灌入
'========================================================================================
    Dim 计数 As Integer
    计数 = XL算展数程跨期_生成历史(ARRLLL, 指定代码, 指定结期上限, 典腾实)
    If 计数 < 1 Then Exit Function
    '------------------------------------------------------------------------------------
    '生成神谕
    '------------------------------------------------------------------------------------
    If Not IsMissing(谕组) Then
        ReDim 谕组(LBound(ARRLLL, 1) To UBound(ARRLLL, 1), 1 To 位qt主宽) As Variant
        Call IQQQ跨码据擎_数程生成跨时神谕(谕组, ARRLLL, 基列:=1, 是否跨码:=False)
    End If
    '------------------------------------------------------------------------------------
    '算法灌入
    '------------------------------------------------------------------------------------
    If Len(被研算法) > 0 Then Call XL算灌引擎跨期(ARRLLL, 规则算法:=被研算法)
    '------------------------------------------------------------------------------------
    '展示
    '------------------------------------------------------------------------------------
'    Dim WSLX As Worksheet
'    Call PBASE格程工具_表操工表新增(WSLX, "KLLL")
'    Call UTL数据转换_集ARR2WS(ARRLLL, WSLX, 2, 1)
'    Call IQQQ跨码展擎_按列OS区域(WSLX, 1)
'    Call IQQQ跨码展擎_按列OS区域(WSLX, 1 + 花宽单道)
'    Call IQQQ跨码展擎_按列OS区域(WSLX, 1 + 花宽单道 * 2)
'Stop
'========================================================================================
'返回
'========================================================================================
    XL算展数程跨期 = 计数
End Function

'========================================================================================
'========================================================================================
'功能：生成历史数据（CSV取据 -> 结算 -> 合并ARRLLL）
'========================================================================================
'========================================================================================
Function XL算展数程跨期_生成历史( _
          ARRLLL As Variant _
        , 指定代码 As String _
        , Optional ByVal 指定结期上限 As Variant _
        , Optional ByVal 典腾实 As Variant _
        ) As Integer
'========================================================================================
'参数设置
'========================================================================================
    Dim 指定结日 As Date
    If IsMissing(指定结期上限) Then
        指定结日 = Date
    Else
        指定结日 = CDate(指定结期上限)
        If 指定结日 > Date Then 指定结日 = Date
    End If
    Dim ARROSD As Variant
    Dim ARROSW As Variant
    Dim ARROSM As Variant
'========================================================================================
'导入外部数据：日类
'========================================================================================
    Dim ARRCSVD As Variant
    Dim 计数日类 As Integer
    计数日类 = STBASE取据引擎_工具取据由外库(ARRCSVD, 指定代码, 指定结期上限:=指定结日)
    If 计数日类 < 1 Then Exit Function
    If Not IsMissing(典腾实) Then
        If Not IsEmpty(典腾实) Then
            If 典腾实.Exists(指定代码) Then
                Dim ARRTR As Variant
                ARRTR = 典腾实(指定代码)
                If ARRTR(1, 位列TS结期) > ARRCSVD(计数日类, 位列TS结期) Then
                    Dim tmpCSVD As Variant
                    ReDim tmpCSVD(1 To 计数日类 + 1, 1 To 位列TS上限单期)
                    Dim rr As Integer, cc As Integer
                    For rr = 1 To 计数日类
                        For cc = 1 To 位列TS上限单期
                            tmpCSVD(rr, cc) = ARRCSVD(rr, cc)
                        Next
                    Next
                    tmpCSVD(计数日类 + 1, 位列TS结龄) = 计数日类 + 1
                    tmpCSVD(计数日类 + 1, 位列TS结期) = ARRTR(1, 位列TS结期)
                    tmpCSVD(计数日类 + 1, 位列TS结收) = ARRTR(1, 位列TS结收)
                    tmpCSVD(计数日类 + 1, 位列TS结开) = ARRTR(1, 位列TS结开)
                    tmpCSVD(计数日类 + 1, 位列TS结高) = ARRTR(1, 位列TS结高)
                    tmpCSVD(计数日类 + 1, 位列TS结低) = ARRTR(1, 位列TS结低)
                    ARRCSVD = tmpCSVD
                    计数日类 = 计数日类 + 1
                End If
            End If
        End If
    End If
'========================================================================================
'结算数据
'========================================================================================
    Dim 是否去重 As Boolean
    是否去重 = False
    Dim ARRDATAD As Variant
    计数日类 = STBASE取据引擎_工具结算数据转换(ARRCSVD, ARRDATAD, 常期类为日, 是否去重:=是否去重)
    Call STBASE结算引擎_全点基组数程(ARROSD, ARRDATAD, 指定代码, 常期类为日)
    Dim ARRDATAW As Variant
    计数日类 = STBASE取据引擎_工具结算数据转换(ARRCSVD, ARRDATAW, 常期类为周, 是否去重:=是否去重)
    Call STBASE结算引擎_全点基组数程(ARROSW, ARRDATAW, 指定代码, 常期类为周)
    Dim ARRDATAM As Variant
    计数日类 = STBASE取据引擎_工具结算数据转换(ARRCSVD, ARRDATAM, 常期类为月, 是否去重:=是否去重)
    Call STBASE结算引擎_全点基组数程(ARROSM, ARRDATAM, 指定代码, 常期类为月)
'========================================================================================
'合并
'========================================================================================
    ARRLLL = ARROSD
    Call STBASE罗盘数程_OS按日墨汁数程基程(ARRLLL, ARROSW)
    Call STBASE罗盘数程_OS按日墨汁数程基程(ARRLLL, ARROSM)
    Erase ARROSD
    Erase ARROSW
    Erase ARROSM
'========================================================================================
'返回
'========================================================================================
    Erase ARRCSVD
    Erase ARRDATAD
    Erase ARRDATAW
    Erase ARRDATAM
    XL算展数程跨期_生成历史 = 计数日类
End Function
"""

content = content.replace(old, new)

with open('d:/@VSwork/VS昭明计划VBA优化/昭明计划VS优化_vba/PX算研_RAP算展1引擎.bas', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK')