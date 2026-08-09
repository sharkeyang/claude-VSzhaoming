Attribute VB_Name = "AUTL_热加载"
'========================================================================================
' AUTL_热加载 — 在线加载 .bas 文件，无需关闭工作簿
'========================================================================================
' 功能：从昭明计划VS优化_vba/ 目录读取所有 .bas 文件，直接注入当前 VBA 工程
' 安全：不会删除自己所在的模块（AUTL_热加载）
' 依赖：_产出物/_工具/热加载_转GBK.py（将 UTF-8 .bas 转为 GBK 编码）
'
' 使用方法：
'   1. 修改 .bas 文件（用文本编辑器）
'   2. 点击菜单「更新」→「热加载VBA」或按 Alt+F8 → 选择「AUTL_热加载」→ 运行
'   3. 弹窗显示「热加载完成」即生效，花册/藏库全部在线不受影响
'
' 注意事项：
'   1. 本模块自身不会被热加载重载，需 vba2EXCEL 正式导入一次
'   2. 热加载前建议先备份（vba2EXCEL 会自动备份）
'   3. 语法错误的 .bas 会跳过，不影响已导入的模块
'   4. 依赖 Python 环境（_产出物/_工具/热加载_转GBK.py）
'========================================================================================
Public Sub AUTL_热加载()
    On Error Resume Next
    Dim testComp As Object
    Set testComp = Application.VBE.ActiveVBProject.VBComponents
    If Err.Number <> 0 Then
        Err.Clear
        On Error GoTo 0
        MsgBox "热加载失败：当前处于中断模式" & vbCrLf & _
               "请按 F5 继续运行后重试，或按 Ctrl+Break 后点击" & vbCrLf & _
               "「重置」按钮再试", vbExclamation, "热加载VBA"
        Exit Sub
    End If
    On Error GoTo 0
    Call 热加载_执行("D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\", True)
    '------------------------------------------------------------------------------------
    UTL宏工具_强制重置状态
End Sub


Public Sub UTL宏工具_强制重置状态()
    UTL宏工具_DEPTH = 0
    Application.ScreenUpdating = True
    Application.DisplayAlerts = True
    Application.Calculation = xlCalculationAutomatic
    Application.Interactive = True
    Application.EnableEvents = True
    Debug.Print "已重置：ScreenUpdating/DisplayAlerts/Interactive/EnableEvents → True" & vbCrLf & _
           "Calculation → Automatic" & vbCrLf & _
           "Depth → 0", vbInformation, "状态重置完成"
End Sub

'========================================================================================
' 热加载_执行 — 核心导入函数
' 调用 Python 脚本将 UTF-8 .bas 转为 GBK 临时目录，再用 Import 注入
'========================================================================================
Private Sub 热加载_执行(ByVal 目录 As String, Optional 是否弹窗 As Boolean = True)
    Dim 自名 As String, 脚本路径 As String, 临时GBK目录 As String, cmd As String, 模块名 As String, 首行 As String
    Dim FSO As Object, vbproj As Object, comp As Object, file As Object
    Dim shell As Object, 流 As Object
    Dim 删除类() As String, 删除数 As Long, i As Long, 引号1 As Long, 引号2 As Long
    Dim 删除计数 As Long, 导入计数 As Long

    自名 = "AUTL_热加载"
    脚本路径 = "D:\@VSwork\VS昭明计划VBA优化\_产出物\_工具\热加载_转GBK.py"

    Set FSO = CreateObject("Scripting.FileSystemObject")
    If FSO.FolderExists(目录) = False Then
        If 是否弹窗 Then MsgBox "目录不存在：" & 目录, vbCritical
        Exit Sub
    End If
    If FSO.FileExists(脚本路径) = False Then
        If 是否弹窗 Then MsgBox "Python脚本不存在：" & 脚本路径, vbCritical
        Exit Sub
    End If

    ' ① 调用 Python 脚本，将 UTF-8 .bas 转为 GBK 临时目录
    Set shell = CreateObject("WScript.Shell")
    cmd = "C:\ProgramData\anaconda3\python.exe """ & 脚本路径 & """"
    shell.Run cmd, 0, True

    ' ② 临时目录固定为 %TEMP%\vba_hot_reload\
    临时GBK目录 = Environ("TEMP") & "\vba_hot_reload"
    If FSO.FolderExists(临时GBK目录) = False Then
        If 是否弹窗 Then MsgBox "Python 脚本执行失败，无法创建临时目录", vbCritical
        Exit Sub
    End If

    ' ③ 收集要删除的模块
    Set vbproj = Application.VBE.ActiveVBProject
    删除数 = 0
    For Each comp In vbproj.VBComponents
        If comp.Type = 1 Then
            If comp.Name <> 自名 Then
                ReDim Preserve 删除类(删除数)
                删除类(删除数) = comp.Name
                删除数 = 删除数 + 1
            End If
        End If
    Next

    ' ④ 删除
    For i = 0 To 删除数 - 1
        On Error Resume Next
        vbproj.VBComponents.Remove vbproj.VBComponents(删除类(i))
        If Err.Number = 0 Then 删除计数 = 删除计数 + 1
        On Error GoTo 0
    Next

    ' ⑤ 从 GBK 临时目录导入（先删同名模块，避免二义性）
    Dim 文件计数 As Long: 文件计数 = 0
    Dim 跳过计数 As Long: 跳过计数 = 0
    For Each file In FSO.GetFolder(临时GBK目录).Files
        If LCase(FSO.GetExtensionName(file.Name)) = "bas" And file.Name <> "AUTL_热加载.bas" Then
            文件计数 = 文件计数 + 1
            ' 用 Open 语句读取第一行提取模块名（比ADODB.Stream更稳定）
            Dim 文件号 As Integer
            文件号 = FreeFile
            On Error Resume Next
            Open file.Path For Input As #文件号
            Line Input #文件号, 首行
            Close #文件号
            If Err.Number <> 0 Then
                Debug.Print "  [跳过] " & file.Name & " - 空文件或读失败"
                跳过计数 = 跳过计数 + 1
                Err.Clear: On Error GoTo 0: GoTo 跳过文件
            End If
            On Error GoTo 0
            引号1 = InStr(首行, """")
            If 引号1 > 0 Then
                引号2 = InStr(引号1 + 1, 首行, """")
                If 引号2 > 0 Then
                    模块名 = Mid$(首行, 引号1 + 1, 引号2 - 引号1 - 1)
                    ' 如果模块已存在，先删除
                    On Error Resume Next
                    vbproj.VBComponents.Remove vbproj.VBComponents(模块名)
                    Err.Clear
                    On Error GoTo 0
                End If
            End If
            ' 导入
            On Error Resume Next
            vbproj.VBComponents.Import file.Path
            If Err.Number = 0 Then
                导入计数 = 导入计数 + 1
                Debug.Print "  [OK] " & file.Name
            Else
                Debug.Print "  [!!] " & file.Name & " - " & Err.Description
                Err.Clear
            End If
            On Error GoTo 0
        End If
跳过文件:
    Next
    Debug.Print "【热加载统计】临时目录共 " & 文件计数 & " 个 .bas 文件，跳过 " & 跳过计数 & " 个，导入 " & 导入计数 & " 个"
    Set 流 = Nothing

    ' ⑥ 清理临时目录
    On Error Resume Next
    FSO.DeleteFolder 临时GBK目录, True
    On Error GoTo 0

    If 是否弹窗 Then
        MsgBox "热加载完成" & vbCrLf & _
               "删除 " & 删除计数 & " 个旧模块" & vbCrLf & _
               "导入 " & 导入计数 & " 个新模块" & vbCrLf & _
               "（跳过 " & 自名 & " 自身）", _
               vbInformation, "热加载VBA"
    End If
End Sub
