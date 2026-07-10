Attribute VB_Name = "ROS据管_DM3外簿引擎1"
Option Explicit
'########################################################################################
'########################################################################################
'##############################     通用外簿引擎     ####################################
'########################################################################################
'########################################################################################
'########################################################################################
'########################################################################################
'##############################     通用外簿引擎     ####################################
'########################################################################################
'########################################################################################
'  通用外部工作簿访问引擎。藏库、花册等外部 xlsx 均通过此引擎读写。
'  单例策略：所有路径统一先定位→再打开，确保同一文件只存在一个实例（前台或后台）。
'
'  逻辑链：
'    1. 定位(簿名全径) → 前台Workbooks查同名 → 后台GetObject查隐藏实例 → 返回Workbook
'    2. 打开(簿名全径) → 先调定位 → 命中则直接复用，返回True
'                      → 未命中则按是否后台参数决定在前台还是新COM实例中打开
'    3. 链接(簿名全径, 表名) → 先调定位 → 命中则直接用
'                           → 未命中则调打开 → 再定位失败则报错
'
'  关键规则：
'    - 定位优先：无论前台/后台打开，定位已存在实例都直接复用
'    - 不强制迁移：已打开的实例保持原状，不从一个实例迁到另一个
'    - 单线程安全：VBA单线程模型，无并发竞态
'========================================================================================
'========================================================================================
'通用外簿引擎 — 定位已打开的外部工作簿（前台+后台）
'  步骤1：Dir(全径) 提取文件名 → UTL判断工簿打开 → Workbooks(文件名) 获取前台引用
'  步骤2：GetObject(全径) 尝试定位隐藏COM实例 → 获取后台引用
'  返回：簿令=找到的Workbook，定位成功返回True
'========================================================================================
Function STBASE外簿引擎_定位(簿令 As Excel.Workbook, ByVal 簿名全径 As String) As Boolean
    Dim 簿名 As String
    簿名 = Dir(簿名全径)
    ' 前台：当前Excel实例
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
        Set 簿令 = 后台簿
        STBASE外簿引擎_定位 = True
        Exit Function
    End If
    STBASE外簿引擎_定位 = False
End Function
'========================================================================================
'通用外簿引擎 — 定位→打开→返回工作表引用
'  流程：定位(簿) → 失败则打开(簿) → 失败则报错
'        → 定位工表存在 → 失败则报错
'        → 返回Worksheet引用
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
'通用外簿引擎 — 打开外部工作簿
'  策略：先定位，已打开则复用；未打开才执行打开操作
'  参数：是否后台=True → 新COM实例打开；=False → 当前实例打开
'========================================================================================
Function STBASE外簿引擎_打开(簿令 As Excel.Workbook, ByVal 簿名全径 As String, Optional 是否后台 As Boolean = False) As Boolean
    STBASE外簿引擎_打开 = False
    If UTL判断文件存在(簿名全径) = False Then
        Debug.Print "[外簿打开] 文件不存在：" & 簿名全径
        Exit Function
    End If
    ' 先定位，避免重复打开
    If STBASE外簿引擎_定位(簿令, 簿名全径) Then
        STBASE外簿引擎_打开 = True
        Exit Function
    End If
    ' 定位失败才执行打开
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
'外簿统一关闭 — 遍历所有外簿路径，无论前台后台都保存关闭
' 路径A：前台Workbooks中存在 → Close + DisplayAlerts恢复
' 路径B：提供了Workbook引用 → 判断是否后台，仅后台Quit
' 路径C：无引用 + 前台未开 → GetObject找隐藏实例，关+Quit
'========================================================================================
Function STBASE外簿引擎_关闭(ByVal 簿名全径 As String, Optional 簿令 As Excel.Workbook, Optional 是否保存修改 As Boolean = False) As Boolean
    Dim 簿名 As String
    簿名 = Dir(簿名全径)
    ' 路径A：前台Workbooks中存在
    If UTL判断工簿打开(簿名) Then
        Dim bAlerts As Boolean
        bAlerts = Application.DisplayAlerts
        Application.DisplayAlerts = False
        Workbooks(簿名).Close savechanges:=是否保存修改
        Application.DisplayAlerts = bAlerts
        STBASE外簿引擎_关闭 = True
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
        STBASE外簿引擎_关闭 = True
        Exit Function
    End If
    ' 路径C：GetObject找隐藏实例
    On Error Resume Next
    Dim 后台簿 As Object
    Set 后台簿 = GetObject(簿名全径)
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
            STBASE外簿引擎_关闭 = True
        End If
    End If
End Function
'========================================================================================
'通用外簿引擎 — 切换前台窗口显示/隐藏
'========================================================================================
Sub STBASE外簿引擎_前台显隐(ByVal 簿名全径 As String)
    Dim wb As Workbook
    Dim 簿名 As String
    簿名 = Dir(簿名全径)
    If UTL判断工簿打开(簿名) Then
        For Each wb In Workbooks
            If wb.Name = 簿名 Then
                wb.Windows(1).Visible = Not wb.Windows(1).Visible
                Exit For
            End If
        Next wb
    End If
End Sub
'========================================================================================
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
Function STBASE外簿工具_藏库链接(WS藏库 As Worksheet, Optional 指定期类 As String = 常期类为日) As Boolean
    STBASE外簿工具_藏库链接 = STBASE外簿引擎_链接(WS藏库, 常外簿藏库, 指定期类)
End Function
Function STBASE外簿工具_藏库打开(藏库令 As Excel.Workbook, Optional 指定期类 As String = 常期类为日, Optional 是否后台 As Boolean = False) As Boolean
    STBASE外簿工具_藏库打开 = STBASE外簿引擎_打开(藏库令, 常外簿藏库, 是否后台)
End Function
Function STBASE外簿工具_藏库定位(藏库令 As Excel.Workbook, Optional 指定期类 As String = 常期类为日) As Boolean
    STBASE外簿工具_藏库定位 = STBASE外簿引擎_定位(藏库令, 常外簿藏库)
End Function
Sub STBASE外簿工具_藏库前台显隐()
    STBASE外簿引擎_前台显隐 常外簿藏库
End Sub
'========================================================================================
'========================================================================================
Function STBASE外簿工具_藏库获取组库(ARR藏库 As Variant, Optional 指定期类 As String = 常期类为日) As Integer
    Dim WS藏库 As Worksheet
    If STBASE外簿工具_藏库链接(WS藏库, 指定期类) = False Then Exit Function
    Dim 维横 As Integer
    维横 = PBASE格程工具_表参末列指定(WS藏库, 位行TT交日)
    Dim 维纵 As Integer
    维纵 = PBASE格程工具_表参末行指定(WS藏库, 位列TT代码)
    ARR藏库 = WS藏库.Cells(1, 1).Resize(维纵, 维横)
    STBASE外簿工具_藏库获取组库 = 维纵 - 位行TT头部
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
Sub STBASE外簿工具_花册前台显隐()
    STBASE外簿引擎_前台显隐 常外簿花册
End Sub
'========================================================================================
'旧接口兼容 — 按周期关闭单个花册表
'========================================================================================
Function STBASE外簿工具_花册关闭(Optional 花册令 As Excel.Workbook, Optional 指定花册 As String = 常花中期, Optional 是否保存修改 As Boolean = False) As Boolean
    Dim 全路径 As String
    全路径 = 常外簿花册
    On Error Resume Next
    Call STBASE外簿引擎_关闭(全路径, 花册令, 是否保存修改)
    On Error GoTo 0
    STBASE外簿工具_花册关闭 = True
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
    Dim i As Integer
    For i = 花册簿.Sheets.Count - 4 To 花册簿.Sheets.Count
        花册簿.Sheets(i).Name = Choose(i - 花册簿.Sheets.Count + 5, 常花中股, 常花美股, 常花中期, 常花港股指, 常花港股通)
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











'========================================================================================
'统一外簿关闭 — 关闭昭明花册 + 昭明藏库D
'========================================================================================
Sub STBASE外簿工具_外簿调程关闭()
    On Error Resume Next
    Call STBASE外簿引擎_关闭(常外簿花册, , True)
    Call STBASE外簿引擎_关闭(常外簿藏库, , True)
    On Error GoTo 0
End Sub


'########################################################################################
'########################################################################################
'##################################   外簿调程罗列   ####################################
'########################################################################################
'########################################################################################
' 用途：列出所有已打开的Workbook，标注前台/后台实例
' 用法：运行 UTL外簿实例检测_列出全部
'========================================================================================
Sub STBASE外簿工具_外簿调程罗列()
    Dim MSG As String
    MSG = "已打开工作簿清单" & vbCrLf
    MSG = MSG & "──────────────────────" & vbCrLf
    ' ---- 前台实例 ----
    MSG = MSG & "[前台]" & vbCrLf
    Dim wb As Workbook
    Dim idx As Integer
    idx = 0
    For Each wb In Workbooks
        idx = idx + 1
        Dim vis As String
        If wb.Windows(1).Visible Then
            vis = "  [可见]"
        Else
            vis = "  [隐藏]"
        End If
        MSG = MSG & "  " & idx & ". " & wb.Name & vis & vbCrLf
        MSG = MSG & "     " & wb.FullName & vbCrLf
    Next wb
    If idx = 0 Then MSG = MSG & "  (无)" & vbCrLf
    MSG = MSG & vbCrLf & "  共 " & idx & " 个" & vbCrLf
    MSG = MSG & "──────────────────────" & vbCrLf

    ' ---- 后台实例 ----
    MSG = MSG & "[后台]" & vbCrLf
    Dim 后台计数 As Integer
    后台计数 = 0

    Dim 探测路径 As Variant
    探测路径 = Array(常外簿花册, 常外簿藏库)

    Dim 已检全径 As Object
    Set 已检全径 = CreateObject("Scripting.Dictionary")
    For Each wb In Workbooks
        已检全径.Add wb.FullName, True
    Next wb

    On Error Resume Next
    Dim i As Integer
    For i = 0 To UBound(探测路径)
        Dim 全径 As String
        全径 = Evaluate(探测路径(i))
        If 全径 <> "" And Not 已检全径.Exists(全径) Then
            已检全径.Add 全径, True
            Call STBASE外簿工具_外簿子程检测后台(全径, MSG, 后台计数, idx)
        End If
    Next i
    On Error GoTo 0

    If 后台计数 = 0 Then MSG = MSG & "  (无)" & vbCrLf
    MSG = MSG & vbCrLf & "  共 " & 后台计数 & " 个" & vbCrLf
    MSG = MSG & "──────────────────────" & vbCrLf
    ' ---- 汇总 ----
    MSG = MSG & "合计: 前台 " & idx & " + 后台 " & 后台计数 & " = " & idx + 后台计数

    Debug.Print MSG
    MsgBox MSG, vbOKOnly, "外簿实例检测"
End Sub

'========================================================================================
'内部：探测指定文件是否在后台COM实例中打开
'========================================================================================
Private Sub STBASE外簿工具_外簿子程检测后台(簿全径 As String, ByRef MSG As String, ByRef 计数 As Integer, ByRef idx As Integer)
    On Error Resume Next
    Dim 后台簿 As Object
    Set 后台簿 = GetObject(簿全径)
    On Error GoTo 0

    If Not 后台簿 Is Nothing Then
        计数 = 计数 + 1
        idx = idx + 1
        Dim 簿名 As String
        簿名 = Dir(簿全径)
        MSG = MSG & "  " & idx & ". " & 簿名 & "  [后台]" & vbCrLf
        MSG = MSG & "     " & 簿全径 & vbCrLf

        ' 释放后台引用
        Set 后台簿 = Nothing
    End If
End Sub
'========================================================================================
'########################################################################################
'########################################################################################
'##################################   外簿调程罗列   ####################################
'########################################################################################
'########################################################################################

