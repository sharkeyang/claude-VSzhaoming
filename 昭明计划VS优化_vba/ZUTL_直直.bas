Attribute VB_Name = "ZUTL_直直"
'Option Explicit
'待完成任务
'========================================================================================
'STUDY:实时模拟月与周行情变化情况，用五因素做判断，总结持仓规律
'========================================================================================
'添加指标：M12与M26交叉后的天数
'待研究：月线站上JB之后，每次周线站上JB之上之后的赚钱概率
'========================================================================================
'========================================================================================
'http://etfdb.com/etfdb-categories/
'美股：按照基金持仓编制列表
'========================================================================================
'========================================================================================
'长期任务：
'李默佛尔操盘术，用VBA实现
'对于CSV文件，从尾部开始读入，反向计算指标，画均线
'========================================================================================
'========================================================================================
'========================================================================================
'保命准则：
'(1)大盘CBX在均线以下，严格控制仓位，绝不可超过半仓。
'(2)股指序列呈现反向结构时，不进行买卖。
'(3)不可恋战，不可存在侥幸心理，不可以想：已经跌成这样了，还能跌多少。
'(4)严格按照操盘指南进行操作。
'========================================================================================
'========================================================================================
'========================================================================================


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
Public Sub UTL宏工具_显示工作簿()
    '强制显示当前工作簿窗口
    On Error Resume Next
    Application.Visible = True
    ThisWorkbook.Windows(1).Visible = True
    ThisWorkbook.Windows(1).WindowState = xlNormal
    ThisWorkbook.Activate
    On Error GoTo 0
End Sub
Sub 后台辅程操作_激活前台()
        Application.ScreenUpdating = True
        Application.DisplayAlerts = True
        Application.Calculation = xlCalculationAutomatic
        Application.Interactive = True
        Application.EnableEvents = True
'    Application.StandardFont = "宋体"
'    Application.StandardFontSize = 11
    'B = CStr(WorksheetFunction.RoundUp(a, 0))
    'Debug.Print B
End Sub

'解决弹框《Excel提示不同的单元格格式太多》
Sub 后台辅程清理单元格样式()
    Dim s As Style
    On Error Resume Next
    For Each s In ThisWorkbook.Styles
    If Not s.BuiltIn Then s.Delete
    Next
    MsgBox "所有讨厌的自定义格式都删除啦！"
End Sub



Sub 后台辅程清理WB()
    Call UGSOP全局清理工表_昭明全部
End Sub



Private Sub 后台质程操作_选区2列表()
    Dim 码市 As String
    码市 = "HK" '"SS"
    Dim 每行代码个数 As Integer
    每行代码个数 = 10
    '------------------------------------------------------------------------------------
    Dim 码格式 As String
    If 码市 = "SS" Then
        码格式 = 全设格式of代码
    ElseIf 码市 = "HK" Then
        码格式 = "00000"
    End If
    '------------------------------------------------------------------------------------
    Dim 缩进字符串 As String
    缩进字符串 = String(8, " ")
    '------------------------------------------------------------------------------------
    Dim CL As Range
    Dim CIDV As Variant
    Dim CIDS As String
    Dim CIDL As String
    Dim 类代码列表 As String
    Dim 类代码个数 As Integer
    '------------------------------------------------------------------------------------
    类代码个数 = 0
    类代码列表 = ""
    For Each CL In Selection
        CIDV = CL.Value
        If Len(CIDV) > 0 Then
            If VBA.IsNumeric(CIDV) = True Then
                If Len(CIDV) > 0 Then
                    CIDS = Format$(CIDV, 码格式)
                End If
                If 码市 = "SS" Then
                    If CIDS Like "60####" Then
                        CIDL = "sh" & CIDS
                    ElseIf CIDS Like "00####" Or CIDS Like "30####" Then
                        CIDL = "sz" & CIDS
                    ElseIf CIDS Like 常通配全码代码 Then
                        CIDL = CIDS
                    End If
                ElseIf 码市 = "HK" Then
                    CIDL = "hk" & CIDS
                End If
           Else
                CIDL = CIDV
            End If
            
            '----------------------------------------------------------------------------
            类代码列表 = 类代码列表 & "," & Chr(34) & CIDL & Chr(34)
            类代码个数 = 类代码个数 + 1
            
            If 类代码个数 Mod 每行代码个数 = 0 Then
                类代码列表 = 类代码列表 & " _" & vbCrLf & 缩进字符串
            End If
            '----------------------------------------------------------------------------
        End If
    Next
    类代码列表 = 缩进字符串 & "__" & Mid$(类代码列表, 2)
    '------------------------------------------------------------------------------------
    Debug.Print 类代码列表 & ")" & vbCrLf
End Sub





Function 后台质程操作_左合并(WSL As Worksheet, WSR As Worksheet, 主列L, 主列R, 目标列号L, 原始列号R)
'    Dim WSL As Worksheet
'    Dim WSR As Worksheet
'    Set WSL = ThisWorkbook.Sheets("IOTS")
'    Set WSR = ThisWorkbook.Sheets("概念")
    '------------------------------------------------------------------------------------
'    Dim 主列L
'    Dim 主列R
'    主列L = "A"
'    主列R = "D"
    '------------------------------------------------------------------------------------
'    Dim 目标列号L
'    Dim 原始列号R
'    目标列号L = "X"
'    原始列号R = "I"
    '------------------------------------------------------------------------------------
    Dim L As Integer
    Dim R As Integer
    
    For L = 2 To WSL.Cells(65536, 主列L).End(xlUp).Row
        Debug.Print WSL.Name; L
        For R = 2 To WSR.Cells(65536, 主列R).End(xlUp).Row
            If WSL.Cells(L, 主列L) = CLng(WSR.Cells(R, 主列R)) Then
                WSL.Cells(L, 目标列号L) = WSR.Cells(R, 原始列号R)
            End If
        Next R
    Next L
    
    'WSL.Columns(目标列号L).AutoFit
    '------------------------------------------------------------------------------------
End Function




'========================================================================================
' 计算A列-B列的差值
'========================================================================================
Private Sub 后台质程操作_列差A_B()
    Dim WSA As Worksheet
    Set WSA = ThisWorkbook.Sheets("HD")
    Dim WSB As Worksheet
    If STBASE外簿工具_花册链接(WSB, 常花中股) = False Then Exit Sub
    Dim 列A
    Dim 列B
    列A = "A"
    列B = "A"
    '------------------------------------------------------------------------------------
    Dim 已有 As Boolean
    Dim 差串 As String
    Dim M As Integer, X As Integer
    '------------------------------------------------------------------------------------
    For M = 1 To WSA.Cells(65536, 列A).End(xlUp).Row
        已有 = False
        For X = 1 To WSB.Cells(65536, 列B).End(xlUp).Row
            If WSA.Cells(M, 列A) = WSB.Cells(X, 列B) Then
                'WSA.Cells(M, 列A).Interior.ColorIndex = 33
                已有 = True
            End If
        Next
        
        If 已有 = False And WSA.Cells(M, 列A) <> "" Then
            差串 = 差串 & "," & WSA.Cells(M, 列A)
        End If
    Next
    差串 = WSA.Name & "[" & 列A & "]-" & WSB.Name & "[" & 列B & "]:" & vbCrLf & Mid$(差串, 2) & vbCrLf
    Debug.Print 差串
End Sub
Private Sub 后台质程操作_去重A_B()
    Dim WSA As Worksheet
    Set WSA = ThisWorkbook.Sheets("热门")
    Dim WSB As Worksheet
    Set WSB = ThisWorkbook.Sheets("中概")
    Dim 列A
    Dim 列B
    列A = "B"
    列B = "B"
    '------------------------------------------------------------------------------------
    Dim 已有 As Boolean
    Dim 差串 As String
    '------------------------------------------------------------------------------------
    For M = WSA.Cells(65536, 列A).End(xlUp).Row To 1 Step -1
        已有 = False
        For X = 1 To WSB.Cells(65536, 列B).End(xlUp).Row
            If WSA.Cells(M, 列A) = WSB.Cells(X, 列B) Then
                WSA.Cells(M, 列A).Interior.ColorIndex = 33
                WSA.Rows(M).Delete
                已有 = True
            End If
        Next
        
        If 已有 = False And WSA.Cells(M, 列A) <> "" Then
            差串 = 差串 & "," & WSA.Cells(M, 列A)
        End If
    Next
    差串 = WSA.Name & "[" & 列A & "]-" & WSB.Name & "[" & 列B & "]:" & vbCrLf & Mid$(差串, 2) & vbCrLf
    Debug.Print 差串
End Sub
Private Sub 后台质程操作_比较数据()
    Dim WX As Worksheet
    If STBASE外簿工具_花册链接(WX, 常花中股) = False Then Exit Sub
    Dim WY As Worksheet
    Set WY = ThisWorkbook.Sheets("HD1")
    '------------------------------------------------------------------------------------
    Dim NROW As Integer
    NROW = WX.UsedRange.SpecialCells(xlCellTypeLastCell).Row
    Dim NCOL As Integer
    NCOL = WX.UsedRange.SpecialCells(xlCellTypeLastCell).Column

    Debug.Print NROW; NCOL
    '------------------------------------------------------------------------------------
    For M = 1 To NROW
    For N = 1 To NCOL
        If WX.Cells(M, N) <> WY.Cells(M, N) Then
            Debug.Print M; N; WX.Cells(M, N); WY.Cells(M, N)
        End If
    Next N
    Next M
    '------------------------------------------------------------------------------------
End Sub





Private Sub 后台质程操作_获取文件夹内容(ByVal nPath As String, ByRef iCount As Long)
    Dim IFileSys As Object
    Dim iFolder As Object
    Dim iFile As Object
    Dim gfile As Object
'    Dim iFile As Files, gFile As File
'    Dim iFolder As Folder, sFolder As Folders, nFolder As Folder
    Set IFileSys = CreateObject("Scripting.FileSystemObject")
    Set iFolder = IFileSys.GetFolder(nPath)
    Set iFile = iFolder.Files
    '------------------------------------------------------------------------------------
    For Each gfile In iFile
        
       ' .Hyperlinks.Add anchor:=.Cells(iCount, 1), Address:=gFile.path, TextToDisplay:=gFile.Name
        Debug.Print iCount; gfile.Path, gfile.Name
        iCount = iCount + 1
    Next
End Sub
Private Sub 后台质程操作_导入()
    Dim wb As Workbook
    Dim ARR
    
    Set wb = GetObject(Application.GetOpenFilename("csv文件,*.csv", , "请选择", , False))
    ARR = wb.ActiveSheet.Range("A1").CurrentRegion
    wb.Close False
    
    Range("A1").Resize(UBound(ARR), UBound(ARR, 2)) = ARR
End Sub



'为单元格添加三角形
Sub CoverCommentIndicator()
    'Update 20141110
    Dim pWs As Worksheet
    Dim pComment As Comment
    Dim pRng As Range
    Dim pShape As Shape
    Set pWs = Application.ActiveSheet
    Dim wShp As Double, hShp As Double
    wShp = 6
    hShp = 4
    For Each pComment In pWs.Comments
      Set pRng = pComment.Parent
      Set pShape = pWs.Shapes.AddShape(msoShapeRightTriangle, pRng.Offset(0, 1).Left - wShp, pRng.Top, wShp, hShp)
      With pShape
        .Flip msoFlipVertical
        .Flip msoFlipHorizontal
        .Fill.ForeColor.SchemeColor = 12
        .Fill.Visible = msoTrue
        .Fill.Solid
        .Line.Visible = msoFalse
      End With
    Next
End Sub

