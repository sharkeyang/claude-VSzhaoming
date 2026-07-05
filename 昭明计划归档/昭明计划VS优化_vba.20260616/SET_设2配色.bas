Attribute VB_Name = "SET_设2配色"
'尝试使用OLE_COLOR作为常量类型或函数返回类型
'重新设置以下常色体系，保证每个色系有足够选择，并且命名规则适用，用RGB进行备注
'-----------------------------------------------
'-----------------------------------------------
'颜色
'-----------------------------------------------
Public Const 常色主靛 = 12611584            'RGB(   0, 112, 192)
Public Const 常色十靛 = 16750080            'RGB(   0, 150, 255)
Public Const 常色八靛 = 13137920            'RGB(   0, 120, 200)
Public Const 常色六靛 = 9853440             'RGB(   0,  90, 150)
Public Const 常色四靛 = 6568960             'RGB(   0,  60, 100)
Public Const 常色二靛 = 3284480             'RGB(   0,  30, 50)
'-----------
Public Const 常色十蓝 = 16711680            'RGB(   0,   0, 255)
Public Const 常色八蓝 = 13369344            'RGB(   0,   0, 204)
Public Const 常色六蓝 = 10027008            'RGB(   0,   0, 153)
Public Const 常色五蓝 = 8323072             'RGB(   0,   0, 127)
Public Const 常色四蓝 = 6684672             'RGB(   0,   0, 102)
Public Const 常色二蓝 = 3342336             'RGB(   0,   0, 51)
Public Const 常色灰蓝 = 16750230            'RGB( 150, 150, 255)
'-----------
Public Const 常色十紫 = 16711935            'RGB( 255,   0, 255)
Public Const 常色八紫 = 13369548            'RGB( 200,   0, 200)
Public Const 常色六紫 = 9830550             'RGB( 150,   0, 150)
Public Const 常色四紫 = 6684774             'RGB( 102,   0, 102)  主紫
Public Const 常色三紫 = 4653127             'RGB(  71,   0,  71)
Public Const 常色二紫 = 3342387             'RGB(  51,   0,  51)
Public Const 常色灰紫 = 13145800            'RGB( 200, 150, 200)
'-----------------------------------------------
Public Const 常色主绿 = 6723891             'RGB(  51, 153, 102)
Public Const 常色43绿 = 52377               'RGB( 153, 204,   0)
Public Const 常色浅绿 = 5299320             'RGB( 120, 220,  80)
Public Const 常色十绿 = 65280               'RGB(   0, 255,   0)
Public Const 常色八绿 = 52224               'RGB(   0, 204,   0)
Public Const 常色六绿 = 39168               'RGB(   0, 153,   0)
Public Const 常色四绿 = 26112               'RGB(   0, 102,   0)
Public Const 常色二绿 = 13056               'RGB(   0,  51,   0)
Public Const 常色一绿 = 6400                'RGB(   0,  25,   0)
Public Const 常色灰绿 = 9895830             'RGB( 150, 255, 150)
'-----------
Public Const 常色十青 = 16776960            'RGB(   0, 255, 255)
Public Const 常色八青 = 13421568            'RGB(   0, 204, 204)
Public Const 常色六青 = 9868800             'RGB(   0, 150, 150)
Public Const 常色五青 = 8421376             'RGB(   0, 128, 128)
Public Const 常色四青 = 6710784             'RGB(   0, 102, 102)
Public Const 常色三青 = 4934400             'RGB(   0,  75,  75)
Public Const 常色二青 = 3355392             'RGB(   0,  51,  51)
Public Const 常色一青 = 1710592             'RGB(   0,  26,  26)
'-----------
Public Const 常色十红 = 255                 'RGB( 255,   0,   0)
Public Const 常色八红 = 204                 'RGB( 204,   0,   0)
Public Const 常色六红 = 153                 'RGB( 153,   0,   0)
Public Const 常色五红 = 127                 'RGB( 127,   0,   0)
Public Const 常色四红 = 102                 'RGB( 102,   0,   0)
Public Const 常色三红 = 71                  'RGB( 71,   0,   0)
Public Const 常色二红 = 51                  'RGB( 51,   0,   0)
Public Const 常色灰红 = 9869055             'RGB( 255, 150, 150)
'-----------
Public Const 常色十橙 = 39423               'RGB( 255, 155,   0)
Public Const 常色八橙 = 31948               'RGB( 204, 124,   0)
Public Const 常色六橙 = 23961               'RGB( 153,  93,   0)
Public Const 常色五橙 = 19839               'RGB( 127,  77,   0)
Public Const 常色四橙 = 15974               'RGB( 102,  62,   0)
Public Const 常色二橙 = 7987                'RGB(  51,  31,   0)
'-----------
Public Const 常色主黄 = 65535               'RGB( 255, 255,   0)
Public Const 常色十黄 = 65535               'RGB( 255, 255,   0)
Public Const 常色八黄 = 52428               'RGB( 204, 204,   0)
Public Const 常色七黄 = 44461               'RGB( 173, 173,   0)
Public Const 常色六黄 = 38550               'RGB( 150, 150,   0)
Public Const 常色五黄 = 32896               'RGB( 128, 128,   0)
Public Const 常色四黄 = 26214               'RGB( 102, 102,   0)
Public Const 常色三黄 = 19789               'RGB(  77,  77,   0)
Public Const 常色二黄 = 13107               'RGB(  51,  51,   0)
Public Const 常色一黄 = 6682                'RGB(  26,  26,   0)
'-----------
Public Const 常色主白 = 16777215            'RGB( 255, 255, 255)
Public Const 常色九灰 = 15132390            'RGB( 230, 230, 230)
Public Const 常色八灰 = 13421772            'RGB( 204, 204, 204)
Public Const 常色七灰 = 11513775            'RGB( 175, 175, 175)
Public Const 常色六灰 = 9868950             'RGB( 150, 150, 150)
Public Const 常色五灰 = 8289918             'RGB( 126, 126, 126)
Public Const 常色四灰 = 6710886             'RGB( 102, 102, 102)
Public Const 常色三灰 = 4934475             'RGB(  75,  75,  75)
Public Const 常色二灰 = 3355443             'RGB(  51,  51,  51)
Public Const 常色一灰 = 1644825             'RGB(  25,  25,  25)
Public Const 常色主黑 = 855309              'RGB(   0,   0,   0)
'-----------------------------------------------
'配色
Public Const 常色勿动 = 常色主黑
Public Const 常色行情 = 常色十蓝
Public Const 常色指金 = 常色主靛
Public Const 常色研究 = 常色灰绿
'-----------------------------------------------


Sub xxx()
    Debug.Print 后台辅程颜色转换_RGB2OLE(230, 230, 230)
    Debug.Print 后台辅程颜色转换_RGB2OLE(175, 175, 175)
    Debug.Print 后台辅程颜色转换_RGB2OLE(126, 126, 126)
    Debug.Print 后台辅程颜色转换_RGB2OLE(0, 75, 75)
    Debug.Print 后台辅程颜色转换_RGB2OLE(0, 51, 0)
    Debug.Print 后台辅程颜色转换_RGB2OLE(0, 90, 150)
End Sub



'Public Const 常色十靛 = 16750848            'RGB(   0, 153, 255)
'Public Const 常色八靛 = 16750848            'RGB(   0, 204, 255)


Private Sub 后台辅程颜色转换_RGB2OLE_测试()
    Dim c As Long
    c = 后台辅程颜色转换_RGB2OLE(0, 26, 26)
    Debug.Print c
    With Columns("b").Interior
        .Color = c
    End With
    ThisWorkbook.Activate
End Sub





Private Sub 后台辅程颜色_查看colorindex()
    On Error Resume Next
    '------------------------------------------------------------------------------------
    Columns.Hidden = False
    Columns(3).Clear
    Columns(3).ColumnWidth = 20
    Columns(4).Clear
    Columns(4).ColumnWidth = 20
    Columns(5).Clear
    Columns(5).ColumnWidth = 20
    'Cells.Clear
    Dim I%
    For I = 1 To 60
        With Cells(I, 2)
            .Value = I
            .Comment.Delete
            .AddComment
            .Comment.Visible = False
            .Comment.Shape.Width = 180
            .Comment.Shape.Height = 70
            .Comment.Shape.Fill.Solid
            .Comment.Shape.Fill.ForeColor.SchemeColor = I
        End With
        Cells(I, 3).Interior.ColorIndex = I
        Cells(I, 3) = I
        色度 = Cells(I, 3).Interior.Color
        Cells(I, 4) = 色度
        Cells(I, 5) = 后台辅程颜色转换_OLE2RGB(色度)
    Next
    '------------------------------------------------------------------------------------
    On Error GoTo 0
End Sub




Private Sub 后台辅程颜色测试()
    色度 = 常色八绿
    Call 后台辅程颜色转换_OLE2RGB(常色八绿)
    ActiveSheet.Cells.Interior.Color = 色度
End Sub
Private Function 后台辅程颜色转换_OLE2RGB(Color As Variant) As String
    Dim R%, G%, B%
    R = Color Mod 256
    G = Color \ 256 Mod 256
    B = Color \ 256 \ 256 Mod 256
    'Debug.Print "R : " & CStr(R) & " G : " & CStr(G) & " B : " & CStr(B)
    MSG = "RGB( " & CStr(R) & ", " & CStr(G) & ", " & CStr(B) & ")"
    Debug.Print MSG
    后台辅程颜色转换_OLE2RGB = MSG
End Function
Private Function 后台辅程颜色转换_RGB2OLE(Optional 色红 As Integer = 0, Optional 色绿 As Integer = 0, Optional 色蓝 As Integer = 0) As Long
    Dim c As OLE_COLOR
    后台辅程颜色转换_RGB2OLE = RGB(色红, 色绿, 色蓝)
    '------------------------------------------------------------------------------------
'    Debug.Print C
'    With Columns("b").Interior
'        .Color = C
'    End With
'    ThisWorkbook.Activate
End Function
Private Sub 后台辅程颜色转换_HEX_OLE()
    Dim CHEX As String
    CHEX = "03a9f4"
    '------------------------------------------------------------------------------------
    Dim R%, G%, B%
    R = WorksheetFunction.Hex2Dec(Left(CHEX, 2))
    G = WorksheetFunction.Hex2Dec(Mid(CHEX, 3, 2))
    B = WorksheetFunction.Hex2Dec(Right(CHEX, 2))
    
    Dim COLE As OLE_COLOR
    COLE = RGB(R, G, B)
    
    Debug.Print COLE
    With Cells.Interior
        .Color = COLE
       ' Debug.Print .Color
    End With
    ActiveWindow.Activate
End Sub




