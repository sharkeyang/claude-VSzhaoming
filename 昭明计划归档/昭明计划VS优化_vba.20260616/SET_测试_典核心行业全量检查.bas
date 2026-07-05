Attribute VB_Name = "SET_测试_典核心行业全量检查"

'========================================================================================
'测试：xlsm里典核心行业全部50个代码逐一检查UBCID是中股返回值
'========================================================================================
Public Sub 测试_sz159755()
    Dim 股票 As Boolean, 股指 As Boolean, 股基 As Boolean
    Dim K As String
    K = "sz159755"

    Debug.Print "=== 单测 sz159755 ==="
    Debug.Print "Len(K)=" & Len(K)
    Debug.Print "Mid(K,1,2)=" & Mid$(K, 1, 2)
    Debug.Print "Mid(K,3,1)=" & Mid$(K, 3, 1)
    Debug.Print "Mid(K,3,2)=" & Mid$(K, 3, 2)

    ' 第1次调用
    UBCID是三分类 K, 股票, 股指, 股基
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

Public Sub 测试_典核心行业全量检查()
    Dim 典 As New Dictionary
    Call 后台族非票精分调程_WA_设置典核心行业(典)

    Debug.Print "=== 典核心行业 全量检查 ==="
    Debug.Print "总代码数: " & 典.Count
    Debug.Print String(100, "=")

    Dim I As Integer
    Dim K As String
    Dim v As String
    Dim 是中股票 As Boolean, 是中股指 As Boolean, 是中股基 As Boolean
    Dim 中股快速 As Boolean, 中股函数 As Boolean
    Dim 被过滤 As Integer
    被过滤 = 0

    Debug.Print String(10, "-") & " 序号 " & String(10, "-") & " Key " & String(20, "-") & " Item " & String(15, "-") & " 中股票 " & String(8, "-") & " 中股指 " & String(8, "-") & " 中股基 " & String(8, "-") & " 快速 " & String(8, "-") & " 函数 " & String(8, "-") & " 分歧 " & String(5, "-")
    For I = 1 To 典.Count
        K = 典.Keys(I - 1)
        v = 典.Item(K)
        ' 第一次调用：模块级变量
        UBCID是三分类 K, 是中股票, 是中股指, 是中股基
        中股快速 = 是中股票 Or 是中股指 Or 是中股基
        ' 第二次调用：完全独立，验证结果一致性
        Dim 二股票 As Boolean, 二股指 As Boolean, 二股基 As Boolean
        Dim 有分歧 As Boolean
        UBCID是三分类 K, 二股票, 二股指, 二股基
        中股函数 = 二股票 Or 二股指 Or 二股基
        有分歧 = (中股快速 <> 中股函数)
        If 中股函数 = False Then 被过滤 = 被过滤 + 1
        Debug.Print "  " & I & "  |  " & K & "  |  " & v & " | " & 是中股票 & "  | " & 是中股指 & "  | " & 是中股基 & " | " & 中股快速 & "  | " & 中股函数 & "  | " & 有分歧
    Next I

    Debug.Print ""
    Debug.Print String(100, "=")
    Debug.Print "被过滤数: " & 被过滤 & ", 通过数: " & (典.Count - 被过滤)
End Sub
