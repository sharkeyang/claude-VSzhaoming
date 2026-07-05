Attribute VB_Name = "ROS据管_DM3外簿引擎"
'########################################################################################
'########################################################################################
'##############################     通用外簿引擎     ####################################
'########################################################################################
'########################################################################################
'  通用外部工作簿访问引擎。藏库、花册等外部 xlsx 均通过此引擎读写。
'  簿名全径 = 完整路径（如 D:\zdata\昭明藏库D.xlsx），用 Dir 提取文件名定位已打开窗口。
'========================================================================================
'========================================================================================
'通用外簿引擎 — 定位已打开的外部工作簿
'========================================================================================
'========================================================================================
Function STBASE外簿引擎_定位(簿令 As Excel.Workbook, ByVal 簿名全径 As String) As Boolean
    Dim 簿名 As String
    簿名 = Dir(簿名全径)
    If UTL判断工簿打开(簿名) Then
        Set 簿令 = Workbooks(簿名)
        STBASE外簿引擎_定位 = True
        Exit Function
    End If
    ' 后台COM实例：GetObject尝试定位隐藏实例
    On Error Resume Next
    Dim 后台簿 As Object
    Set 后台簿 = GetObject(簿名全径)
    On Error GoTo 0
    If Not 后台簿 Is Nothing Then
        If Not 后台簿.Application Is Application Then
            Set 簿令 = 后台簿
            STBASE外簿引擎_定位 = True
            Exit Function
        End If
    End If
    STBASE外簿引擎_定位 = False
End Function
'========================================================================================
'通用外簿引擎 — 打开外部工作簿
'   是否后台=False → 当前Excel窗口可见打开
'   是否后台=True  → 独立隐藏COM实例，不干扰前台
'========================================================================================
'========================================================================================
Function STBASE外簿引擎_打开(簿令 As Excel.Workbook, ByVal 簿名全径 As String, Optional 是否后台 As Boolean = True) As Boolean
    STBASE外簿引擎_打开 = False
    If UTL判断文件存在(簿名全径) = False Then
        Debug.Print "[外簿打开] 文件不存在：" & 簿名全径
        Exit Function
    End If
    On Error Resume Next
    Dim openErrNum As Long
    Dim openErrDesc As String
    If 是否后台 = True Then
        Dim excelAPP As Excel.Application
        Set excelAPP = CreateObject("Excel.Application")
        excelAPP.Visible = False
        excelAPP.ScreenUpdating = False
        excelAPP.DisplayAlerts = False
        excelAPP.Interactive = False
        Set 簿令 = excelAPP.Workbooks.Open(簿名全径, ReadOnly:=False, IgnoreReadOnlyRecommended:=True)
        openErrNum = Err.Number
        openErrDesc = Err.Description
        Err.Clear
    Else
        Set 簿令 = Workbooks.Open(簿名全径, ReadOnly:=False, IgnoreReadOnlyRecommended:=True)
        openErrNum = Err.Number
        openErrDesc = Err.Description
        Err.Clear
    End If
    On Error GoTo 0
    If 簿令 Is Nothing Then
        Debug.Print "[外簿打开] 打开失败 Err=" & openErrNum & "：" & openErrDesc & " → " & 簿名全径
        Exit Function
    End If
    STBASE外簿引擎_打开 = True
End Function
'========================================================================================
'通用外簿引擎 — 定位→打开→返回工作表引用
'========================================================================================
'========================================================================================
Function STBASE外簿引擎_链接(WS目标 As Worksheet, ByVal 簿名全径 As String, ByVal 表名 As String) As Boolean
    STBASE外簿引擎_链接 = False
    Dim 簿令 As Excel.Workbook
    Dim 是否打开 As Boolean
    是否打开 = STBASE外簿引擎_定位(簿令, 簿名全径)
    If 是否打开 = False Then
        是否打开 = STBASE外簿引擎_打开(簿令, 簿名全径)
        If 是否打开 = False Then
            Debug.Print "[外簿链接] 定位+打开失败：" & 簿名全径 & " → " & 表名
            Exit Function
        End If
    End If
    If UTL判断工表存在(表名, 簿令) = False Then
        Debug.Print "[外簿链接] 表不存在：" & 簿名全径 & " → " & 表名
        Exit Function
    End If
    Set WS目标 = 簿令.Sheets(表名)
    STBASE外簿引擎_链接 = True
End Function
'========================================================================================
'通用外簿引擎 — 读整表到数组
'========================================================================================
'========================================================================================
Function STBASE外簿引擎_获取组(ARR As Variant, ByVal 簿名全径 As String, ByVal 表名 As String, ByVal 维横 As Integer, ByVal 维纵 As Integer) As Integer
    Dim WS As Worksheet
    If STBASE外簿引擎_链接(WS, 簿名全径, 表名) = False Then Exit Function
    ARR = WS.Cells(1, 1).Resize(维纵, 维横)
    STBASE外簿引擎_获取组 = 维纵 - 位行TT头部
End Function
'========================================================================================
'通用外簿引擎 — 保存
'========================================================================================
'========================================================================================
Sub STBASE外簿引擎_保存(ByVal 簿名全径 As String)
    Dim 簿名 As String
    簿名 = Dir(簿名全径)
    If UTL判断工簿打开(簿名) Then
        Dim bAlerts As Boolean
        bAlerts = Application.DisplayAlerts
        Application.DisplayAlerts = False
        Workbooks(簿名).Save
        Application.DisplayAlerts = bAlerts
    End If
End Sub
'========================================================================================
'通用外簿引擎 — 关闭
'========================================================================================
'========================================================================================
Function STBASE外簿引擎_关闭(ByVal 簿名全径 As String, Optional 簿令 As Excel.Workbook, Optional 是否保存修改 As Boolean = False) As Boolean
    Dim 簿名 As String
    簿名 = Dir(簿名全径)
    If UTL判断工簿打开(簿名) Then
        Workbooks(簿名).Close savechanges:=是否保存修改
    ElseIf Not 簿令 Is Nothing Then
        Dim excelAPP As Excel.Application
        Set excelAPP = 簿令.Application
        簿令.Close savechanges:=是否保存修改
        Set 簿令 = Nothing
        excelAPP.ScreenUpdating = True
        excelAPP.DisplayAlerts = True
        excelAPP.Interactive = True
        excelAPP.Quit
        Set excelAPP = Nothing
    End If
    STBASE外簿引擎_关闭 = True
End Function
'########################################################################################
'########################################################################################
'##############################     通用外簿引擎     ####################################
'########################################################################################
'########################################################################################


'########################################################################################
'########################################################################################
'##################################     藏库封装     ####################################
'########################################################################################
'########################################################################################
Function STBASE外簿工具_藏库获取组库(ARR藏库 As Variant, Optional 指定期类 As String = 常期类为日) As Integer
    Dim WS藏库 As Worksheet
    If STBASE外簿工具_藏库链接(WS藏库, 指定期类) = False Then Exit Function
    Dim 维横 As Integer
    维横 = PBASE格程工具_表参末列指定(WS藏库, 位行TT交日)
    Dim 维纵 As Integer
    维纵 = PBASE格程工具_表参末行指定(WS藏库, 位列TT代码)
    STBASE外簿工具_藏库获取组库 = STBASE外簿引擎_获取组(ARR藏库, 常外簿藏库, 指定期类, 维横, 维纵)
End Function
Function STBASE外簿工具_藏库链接(WS藏库 As Worksheet, Optional 指定期类 As String = 常期类为日) As Boolean
    STBASE外簿工具_藏库链接 = STBASE外簿引擎_链接(WS藏库, 常外簿藏库, 指定期类)
End Function
Function STBASE外簿工具_藏库打开(藏库令 As Excel.Workbook, Optional 指定期类 As String = 常期类为日, Optional 是否后台 As Boolean = False) As Boolean
    STBASE外簿工具_藏库打开 = STBASE外簿引擎_打开(藏库令, 常外簿藏库, 是否后台)
End Function
Function STBASE外簿工具_藏库定位(藏库令 As Excel.Workbook, Optional 指定期类 As String = 常期类为日) As Boolean
    STBASE外簿工具_藏库定位 = STBASE外簿引擎_定位(藏库令, 常外簿藏库)
End Function
Function STBASE外簿工具_藏库保存(Optional 指定期类 As String = 常期类为日)
    STBASE外簿引擎_保存 常外簿藏库
End Function
Function STBASE外簿工具_藏库关闭(Optional 藏库令 As Excel.Workbook, Optional 指定期类 As String = 常期类为日, Optional 是否保存修改 As Boolean = False) As Boolean
    STBASE外簿工具_藏库关闭 = STBASE外簿引擎_关闭(常外簿藏库, 藏库令, 是否保存修改)
End Function
Function STBASE外簿工具_藏库簿名(Optional 指定期类 As String = 常期类为日) As String
    STBASE外簿工具_藏库簿名 = 常外簿藏库
End Function
'########################################################################################
'########################################################################################
'##################################     藏库封装     ####################################
'########################################################################################
'########################################################################################
'Private Sub 测试_STBASE外簿工具_藏库链接()
'    Dim WS藏库 As Worksheet
'    If STBASE外簿工具_藏库链接(WS藏库, 常期类为周) = True Then
'        Debug.Print WS藏库.Name
'    End If
'End Sub
'########################################################################################
'########################################################################################
'##################################     花册封装     ####################################
'########################################################################################
'########################################################################################
Function STBASE外簿工具_花册获取组库(ARR花册 As Variant, Optional 指定花册 As String = 常花中期) As Integer
    Dim WS花册 As Worksheet
    If STBASE外簿工具_花册链接(WS花册, 指定花册) = False Then Exit Function
    Dim 维横 As Integer
    维横 = PBASE格程工具_表参末列指定(WS花册, 1)
    Dim 维纵 As Integer
    维纵 = PBASE格程工具_表参末行指定(WS花册, 位列花天CIDL)
    ARR花册 = WS花册.Cells(1, 1).Resize(维纵, 维横)
    STBASE外簿工具_花册获取组库 = 维纵 - 1
End Function
Function STBASE外簿工具_花册链接(WS花册 As Worksheet, Optional 指定花册 As String = 常花中期) As Boolean
    STBASE外簿工具_花册链接 = STBASE外簿引擎_链接(WS花册, 常外簿花册, 指定花册)
End Function
Function STBASE外簿工具_花册打开(花册令 As Excel.Workbook, Optional 指定花册 As String = 常花中期, Optional 是否后台 As Boolean = True) As Boolean
    If UTL判断文件存在(常外簿花册) = False Then STBASE外簿工具_花册初始化
    STBASE外簿工具_花册打开 = STBASE外簿引擎_打开(花册令, 常外簿花册, 是否后台)
End Function
Function STBASE外簿工具_花册定位(花册令 As Excel.Workbook, Optional 指定花册 As String = 常花中期) As Boolean
    STBASE外簿工具_花册定位 = STBASE外簿引擎_定位(花册令, 常外簿花册)
End Function
Function STBASE外簿工具_花册保存(Optional 指定花册 As String = 常花中期)
    STBASE外簿引擎_保存 常外簿花册
End Function
'========================================================================================
'外簿统一关闭 — 遍历所有外簿路径，无论前台后台都保存关闭
' 路径A：前台Workbooks中存在 → Close + DisplayAlerts恢复
' 路径B：提供了Workbook引用 → 判断是否后台，仅后台Quit
' 路径C：无引用 + 前台未开 → GetObject找隐藏实例，关+Quit
'========================================================================================
Function STBASE外簿引擎_关闭全径(ByVal 全路径 As String, Optional 簿令 As Excel.Workbook, Optional 是否保存修改 As Boolean = False) As Boolean
    Dim 簿名 As String
    簿名 = Dir(全路径)
    ' 路径A：前台Workbooks中存在
    If UTL判断工簿打开(簿名) Then
        Dim bAlerts As Boolean
        bAlerts = Application.DisplayAlerts
        Application.DisplayAlerts = False
        Workbooks(簿名).Close savechanges:=是否保存修改
        Application.DisplayAlerts = bAlerts
        STBASE外簿引擎_关闭全径 = True
        Exit Function
    End If
    ' 路径B：有引用 → 判断是否后台
    If Not 簿令 Is Nothing Then
        Dim excelAPP As Excel.Application
        Set excelAPP = 簿令.Application
        簿令.Close savechanges:=是否保存修改
        Set 簿令 = Nothing
        If Not excelAPP Is Application Then
            excelAPP.ScreenUpdating = True
            excelAPP.DisplayAlerts = True
            excelAPP.Interactive = True
            excelAPP.Quit
        End If
        Set excelAPP = Nothing
        STBASE外簿引擎_关闭全径 = True
        Exit Function
    End If
    ' 路径C：GetObject找隐藏实例
    On Error Resume Next
    Dim 后台簿 As Object
    Set 后台簿 = GetObject(全路径)
    On Error GoTo 0
    If Not 后台簿 Is Nothing Then
        If Not 后台簿.Application Is Application Then
            Dim 后台APP As Object
            Set 后台APP = 后台簿.Application
            后台簿.Close savechanges:=是否保存修改
            Set 后台簿 = Nothing
            后台APP.ScreenUpdating = True
            后台APP.DisplayAlerts = True
            后台APP.Interactive = True
            后台APP.Quit
            Set 后台APP = Nothing
            STBASE外簿引擎_关闭全径 = True
        End If
    End If
End Function

'========================================================================================
'统一外簿关闭 — 关闭昭明花册 + 昭明藏库D
'========================================================================================
Sub STBASE外簿工具_外簿关闭调程()
    On Error Resume Next
    Call STBASE外簿引擎_关闭全径(常外簿花册, , True)
    Call STBASE外簿引擎_关闭全径(常外簿藏库, , True)
    On Error GoTo 0
End Sub

'========================================================================================
'旧接口兼容 — 按周期关闭单个花册表
'========================================================================================
Function STBASE外簿工具_花册关闭(Optional 花册令 As Excel.Workbook, Optional 指定花册 As String = 常花中期, Optional 是否保存修改 As Boolean = False) As Boolean
    Dim 全路径 As String
    全路径 = 常外簿花册
    On Error Resume Next
    Call STBASE外簿引擎_关闭全径(全路径, 花册令, 是否保存修改)
    On Error GoTo 0
    STBASE外簿工具_花册关闭 = True
End Function
Function STBASE外簿工具_花册簿名(Optional 指定花册 As String = 常花中期) As String
    STBASE外簿工具_花册簿名 = 常外簿花册
End Function
'========================================================================================
'花册外簿初始化 — 若外簿文件不存在则创建，含全部花册sheet
'========================================================================================
Sub STBASE外簿工具_花册初始化()
    If UTL判断文件存在(常外簿花册) Then Exit Sub
    Dim bAlerts As Boolean
    bAlerts = Application.DisplayAlerts
    Application.DisplayAlerts = False
    Dim 花册簿 As Excel.Workbook
    Set 花册簿 = Workbooks.Add
    花册簿.Sheets.Add after:=花册簿.Sheets(花册簿.Sheets.Count), Count:=5
    Dim I As Integer
    For I = 花册簿.Sheets.Count - 4 To 花册簿.Sheets.Count
        花册簿.Sheets(I).Name = Choose(I - 花册簿.Sheets.Count + 5, 常花中股, 常花美股, 常花中期, 常花港股指, 常花港股通)
    Next
    花册簿.Sheets(1).Delete
    花册簿.SaveAs Filename:=常外簿花册, FileFormat:=xlOpenXMLWorkbook
    花册簿.Close False
    Application.DisplayAlerts = bAlerts
End Sub
'########################################################################################
'########################################################################################
'##################################     花册封装     ####################################
'########################################################################################
'########################################################################################
