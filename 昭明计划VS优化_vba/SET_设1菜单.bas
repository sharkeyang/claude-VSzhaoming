Attribute VB_Name = "SET_设1菜单"
Option Explicit
'========================================================================================
'========================================================================================
'删除目录
'========================================================================================
'========================================================================================
Public Sub UGSOP_MENU_删除()
    '------------------------------------------------------------------------------------
'    Debug.Print ActiveWorkbook.Name
'    If Left$(ActiveWorkbook.Name, 3) = "QQQ" Then
'        Exit Sub
'    End If
    '------------------------------------------------------------------------------------
    On Error Resume Next
    Application.CommandBars("昭明菜栏").Delete
    Application.CommandBars("昭明单列").Delete
    Application.CommandBars("昭明操作").Delete
    On Error GoTo 0
    '------------------------------------------------------------------------------------
End Sub




'========================================================================================
'========================================================================================
'目录
'========================================================================================
'========================================================================================
Public Sub UGSOP_MENU_生成()
'========================================================================================
'菜单栏：删除
'========================================================================================
    Call UGSOP_MENU_删除
'========================================================================================
'菜单栏：昭明单列
'========================================================================================
    Dim 菜栏 As CommandBar
    Set 菜栏 = Application.CommandBars.Add(Name:="昭明单列", Position:=msoBarRight, Temporary:=True)
    菜栏.Visible = True
    '------------------------------------------------------------------------------------
    '---------------------------------------------
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花天sSCC_池今"
        .FaceId = 94 '340
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "仓池今"
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_归入调程ZW池今"
        .Caption = "今"
        .FaceId = 250
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_归出调程池今"
        .Caption = "今"
        .FaceId = 334
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "从今池删除"
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程cCCC_金银铜"
        .Caption = "索"
        .FaceId = 483 '42
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_归入调程ZZ池金"
        .Caption = "金"
        .FaceId = 250
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_归入调程ZY池银"
        .Caption = "银"
        .FaceId = 250
        .Style = msoButtonIconAndCaptionBelow
    End With
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "STBASE池管理_归入调程ZX池铜"
'        .Caption = "铜"
'        .FaceId = 250
'        .Style = msoButtonIconAndCaptionBelow
'    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_归入调程ZN池黑"
        .Caption = "黑"
        .FaceId = 250
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_归出调程池全"
        .Caption = "池"
        .FaceId = 334
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "从在池删除"
    End With
    '---------------------------------------------
    '从仓中删除
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_归出调程仓宝福"
        .Caption = "福"
        .FaceId = 334
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "从仓宝福删除"
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_归出调程仓宝彦"
        .Caption = "彦"
        .FaceId = 334
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "从仓宝彦删除"
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "UGSOP拣选引擎标记"
        .Caption = "标"
        .FaceId = 220 '340
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "标记选中"
    End With
    '---------------------------------------------
    '---------------------------------------------
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_表导入调程由选择文件池临时"
        .Caption = "临"
        .FaceId = 173 '340
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "对益盟池临时排序"
    End With
    '---------------------------------------------
'    '交割单
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "STCALL割册管理_瓜分交割单"
'        .Caption = "割"
'        .FaceId = 220 '340
'        .Style = msoButtonIconAndCaptionBelow
'        .TooltipText = "瓜分交割单（还未实现）"
'    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "UGSOP全局清理工表_昭明全部"
'        .Caption = "清"
        .FaceId = 108 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
    '---------------------------------------------
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展前调_月_默认"
        .Caption = "展月"
        .FaceId = 485
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展前调_周_默认"
        .Caption = "展周"
        .FaceId = 485
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展前调_日_默认"
        .Caption = "展日"
        .FaceId = 485
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
            With 菜栏.Controls.Add(Type:=msoControlButton)
                .OnAction = "UGSOP全局统一正程_更新"
                .Caption = "新"
                .FaceId = 37
                .Style = msoButtonIconAndCaptionBelow
                .TooltipText = "对任意页进行更新"
            End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排否sSSC"
        .Caption = "sSSC数"
        .FaceId = 136
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排周sSSC"
        .Caption = "sSSC周"
        .FaceId = 136
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排日sSSC"
        .Caption = "sSSC日"
        .FaceId = 136
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排仓sSSC"
        .Caption = "sSSC仓"
        .FaceId = 136
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
            With 菜栏.Controls.Add(Type:=msoControlButton)
                .OnAction = "UGSOP定时引擎开始"
                .Caption = "开"
                .FaceId = 33
                .Style = msoButtonIconAndCaptionBelow
            End With
            With 菜栏.Controls.Add(Type:=msoControlButton)
                .OnAction = "UGSOP定时引擎停止"
                .Caption = "停"
                .FaceId = 330
                .Style = msoButtonIconAndCaptionBelow
            End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排周sSCC"
        .Caption = "sSCC周"
        .FaceId = 133
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排日sSCC"
        .Caption = "sSCC日"
        .FaceId = 133
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排仓sSCC"
        .Caption = "sSCC仓"
        .FaceId = 136
        .Style = msoButtonIconAndCaptionBelow
    End With
'========================================================================================
'菜单栏：昭明操作
'========================================================================================
    Set 菜栏 = Application.CommandBars.Add(Name:="昭明操作", Position:=msoBarRight, Temporary:=True)
    菜栏.Visible = True
    '------------------------------------------------------------------------------------
    '排序
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "PSOP排序全表分块调程_按这列降序"
        .Caption = "降"
        .FaceId = 597 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "PSOP排序全表分块调程_按这列升序"
        .Caption = "升"
        .FaceId = 594 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按B周仓周护"
        .Caption = "周仓周护"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按B周仓周地"
        .Caption = "周仓周地"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按B周仓周层"
        .Caption = "周仓周层"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按B周仓日综"
        .Caption = "周仓日综"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按B周仓日层"
        .Caption = "周仓日层"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按B日仓日综"
        .Caption = "日仓日综"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按B日仓日层"
        .Caption = "日仓日层"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎瓜页前调决策按B日仓日层"
'        .Caption = "日仓日层"
'        .FaceId = 450 '340
'        .Style = msoButtonIconAndCaptionBelow
'    End With
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎瓜页前调决策按B日仓日层滤"
'        .Caption = "日仓日层滤"
'        .FaceId = 450 '340
'        .Style = msoButtonIconAndCaptionBelow
'    End With
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎瓜页前调决策按B日仓日机"
'        .Caption = "日仓日机"
'        .FaceId = 450 '340
'        .Style = msoButtonIconAndCaptionBelow
'    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按D混周层"
        .Caption = "混周层"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按D混日层"
        .Caption = "混日层"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按B混日综"
        .Caption = "混日综"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎瓜页前调决策按D混日机"
'        .Caption = "混日机"
'        .FaceId = 450 '340
'        .Style = msoButtonIconAndCaptionBelow
'    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按H活"
        .Caption = "活"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调决策按E池"
        .Caption = "池"
        .FaceId = 450 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "PSOP排序单块调程_按这列降序"
        .Caption = "降"
        .FaceId = 596 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "PSOP排序单块调程_按这列升序"
        .Caption = "升"
        .FaceId = 595 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
    '------------------------------------------------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = ""
        .FaceId = 911
        .Style = msoButtonIconAndCaptionBelow
    End With
    '------------------------------------------------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花天sSCC_仓宝合"
        .FaceId = 105 '340
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "仓宝合"
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布基程花天sSCC_仓宝周"
        .FaceId = 102 '340
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "仓宝周"
    End With

'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ乾坤分布调程花天sSCC_仓宝福"
'        .FaceId = 85 '340
'        .Style = msoButtonIconAndCaptionBelow
'        .TooltipText = "仓宝福"
'    End With
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ乾坤分布调程花天sSCC_仓宝彦"
'        .FaceId = 89 '340
'        .Style = msoButtonIconAndCaptionBelow
'        .TooltipText = "仓宝彦"
'    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市总程外簿降序_全部"
        .Caption = "统现市"
        .FaceId = 719 '772 '486
        .Style = msoButtonIconAndCaptionBelow
    End With
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_cCCC式频谱"
'        .Caption = "谱c"
'        .FaceId = 719 '772 '486
'        .Style = msoButtonIconAndCaptionBelow
'        .TooltipText = "cCCC式频谱"
'    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式频谱"
        .Caption = "谱s"
        .FaceId = 719 '772 '486
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "sSCC式频谱"
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程_全局全球"
        .FaceId = 86 '340
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "全局全球"
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程降序_市场美国"
        .FaceId = 100 '340
        .Caption = "S"
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "美国市场"
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程降序_市场香港"
        .FaceId = 87 '340
        .Caption = "K"
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "香港市场"
    End With
    '---------------------------------------------
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程SSC_典指必选"
        .FaceId = 88 '103 '340
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "典指必选"
    End With
    With 菜栏.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程SSC_典基必选"
        .FaceId = 84 '340
        .Style = msoButtonIconAndCaptionBelow
        .TooltipText = "典基必选"
    End With
    '---------------------------------------------
        '板块轮动
        With 菜栏.Controls.Add(Type:=msoControlButton)
            .OnAction = "历研统码调程__展日码核RL版"
            .Caption = "轮核RL"
            .FaceId = 422
            .Style = msoButtonIconAndCaptionBelow
            .TooltipText = "展日码核RL版"
        End With
        With 菜栏.Controls.Add(Type:=msoControlButton)
            .OnAction = "历研统码工具点灯"
            .Caption = "灯"
            .FaceId = 34 '103 '340
            .Style = msoButtonIconAndCaptionBelow
        End With
        With 菜栏.Controls.Add(Type:=msoControlButton)
            .OnAction = "历研统码调程__展日码总R版"
            .Caption = "轮总R"
            .FaceId = 422
            .Style = msoButtonIconAndCaptionBelow
            .TooltipText = "展日码总R版"
        End With
    '---------------------------------------------
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎频谱工具着色按日类涨幅"
'        .Caption = "谱涨"
'        .FaceId = 472 '417
'        .Style = msoButtonIconAndCaptionBelow
'    End With
'    With 菜栏.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎频谱工具着色按日基势局"
'        .Caption = "谱势"
'        .FaceId = 472 '340
'        .Style = msoButtonIconAndCaptionBelow
'    End With
    '---------------------------------------------
    '------------------------------------------------------------------------------------
    Set 菜栏 = Nothing
'========================================================================================
'设置菜单项
'========================================================================================
    Set 菜栏 = Application.CommandBars.Add(Name:="昭明菜栏", Position:=msoBarLeft, Temporary:=True)
    菜栏.Visible = True
    '------------------------------------------------------------------------------------
    '基础操作
    '------------------------------------------------------------------------------------
    Dim 菜项更新 As CommandBarPopup
    Set 菜项更新 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项更新
        .Caption = "更新"
    End With
    '------------------------------------------------------------------------------------
    '管理功能
    '------------------------------------------------------------------------------------
    Dim 菜项池 As CommandBarPopup
    Set 菜项池 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项池
        .Caption = "管理池"
    End With
    Dim 菜项结算 As CommandBarPopup
    Set 菜项结算 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项结算
        .Caption = "管理结算"
    End With
    '------------------------------------------------------------------------------------
    '锁定代码：研究规律
    '数据来源：tushare
    '------------------------------------------------------------------------------------
    Dim 菜项算比 As CommandBarPopup
    Set 菜项算比 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项算比
        .Caption = "研码算比"
    End With
    Dim 菜项算展 As CommandBarPopup
    Set 菜项算展 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项算展
        .Caption = "研码算展"
    End With
    '------------------------------------------------------------------------------------
    '锁定时点：筛选备选
    '数据来源：本簿信息
    '------------------------------------------------------------------------------------
    Dim 菜项决策 As CommandBarPopup
    Set 菜项决策 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项决策
        .Caption = "昭明决策"
    End With
    Dim 菜项频谱 As CommandBarPopup
    Set 菜项频谱 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项频谱
        .Caption = "昭明频谱"
    End With
    '------------------------------------------------------------------------------------
    '锁定时点：统计涨幅
    '数据来源：网络行情
    '------------------------------------------------------------------------------------
    Dim 菜项历研码 As CommandBarPopup
    Set 菜项历研码 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项历研码
        .Caption = "历研统码"
    End With
    Dim 菜项历研时 As CommandBarPopup
    Set 菜项历研时 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项历研时
        .Caption = "历研统时"
    End With
    '------------------------------------------------------------------------------------
    '锁定时点：外盘
    '------------------------------------------------------------------------------------
    Dim 菜项外盘 As CommandBarPopup
    Set 菜项外盘 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项外盘
        .Caption = "管理外盘"
    End With
    Dim 菜项现市 As CommandBarPopup
    Set 菜项现市 = 菜栏.Controls.Add(Type:=msoControlPopup, Temporary:=True)
    With 菜项现市
        .Caption = "统现市"
    End With
'========================================================================================
'菜项更新
'========================================================================================
    '------------------------------------------------------------------------------------
    '模块：更新行情
    '------------------------------------------------------------------------------------
    '更新单程
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "IQQQ展擎瓜页前调更新排否S___"
        .Caption = "S___"
        .FaceId = 133   '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排否sCCC"
        .Caption = "sCCC数"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排周sCCC"
        .Caption = "sCCC周"
        .FaceId = 136 '37
    End With
    '-----------------------------------
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .Enabled = False
        .Caption = "sSCC更新"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排否sSCC"
        .Caption = "sSCC数"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排日sSCC"
        .Caption = "sSCC日"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排周sSCC"
        .Caption = "sSCC周"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排仓sSCC"
        .Caption = "sSCC仓"
        .FaceId = 136 '37
    End With
    '-----------------------------------
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .Enabled = False
        .Caption = "sSSC更新"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排否sSSC"
        .Caption = "sSSC数"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排日sSSC"
        .Caption = "sSSC日"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排周sSSC"
        .Caption = "sSSC周"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排仓sSSC"
        .Caption = "sSSC仓"
        .FaceId = 136 '37
    End With
    '-----------------------------------
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .Enabled = False
        .Caption = "sSSS更新"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排否sSSS"
        .Caption = "sSSS数"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排日sSSS"
        .Caption = "sSSS日"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排周sSSS"
        .Caption = "sSSS周"
        .FaceId = 136 '37
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎瓜页前调更新排仓sSSS"
        .Caption = "sSSS仓"
        .FaceId = 136 '37
    End With
    '------------------------------------------------------------------------------------
    '模块：整理
    '------------------------------------------------------------------------------------
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "PSOP格整理调程_检查重复"
        .Caption = "检查重复"
        .FaceId = 251 '463 '447 '923 '308 '417
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "PSOP格整理调程_删除重复"
        .Caption = "删除重复"
        .FaceId = 251 '463 '447 '923 '308 '417
    End With
    
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "PSOP格整理调程_删除整行"
        .Caption = "删除行"
        .FaceId = 334
    End With
    
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .OnAction = "PSOP格整理调程_删除空行"
        .Caption = "删除空行"
        .FaceId = 334
    End With
'    '------------------------------------------------------------------------------------
'    '排序：按 选定列
'    '------------------------------------------------------------------------------------
'    With 菜项更新.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
'        .Caption = "本列排序"
'        .Enabled = False
'    End With
'
'    With 菜项更新.Controls.Add(Type:=msoControlButton)
'        .OnAction = "PSOP排序单块调程_按这列降序"
'        .Caption = "本列 降"
'        .FaceId = 596
'    End With
'    With 菜项更新.Controls.Add(Type:=msoControlButton)
'        .OnAction = "PSOP排序单块调程_按这列升序"
'        .Caption = "本列 升"
'        .FaceId = 595
'    End With
    '------------------------------------------------------------------------------------
    '模块：清理
    '------------------------------------------------------------------------------------
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "UGSOP全局清理工簿_昭明全部"
        .Caption = "Close Workbook"
        .FaceId = 463
    End With
    With 菜项更新.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "UGSOP全局清理工表_昭明全部"
        .Caption = "Clean Worksheet"
        .FaceId = 108
    End With
'========================================================================================
'菜项池
'========================================================================================
    '------------------------------------------------------------------------------------
    '模块：导入持仓
    '------------------------------------------------------------------------------------
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "STCALL花册管理_重制花天P3调程导入仓宝福"
        .Caption = "导入仓宝福"
        .FaceId = 263  '481  '263 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STCALL花册管理_重制花天P3调程导入仓宝彦"
        .Caption = "导入仓宝彦"
        .FaceId = 263  '481  '263 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_表导入调程由选择文件池今"
        .Caption = "导入索引池 今 sSCC"
        .FaceId = 271  '22 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STCALL花册管理_重制花天P3调程导入仓宝福周池"
        .Caption = "导入仓宝福周池"
        .FaceId = 263  '481  '263 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STCALL花册管理_重制花天P3调程导入仓宝彦周池"
        .Caption = "导入仓宝彦周池"
        .FaceId = 263  '481  '263 '42
    End With
    '------------------------------------------------------------------------------------
    '模块：统一操作 池
    '------------------------------------------------------------------------------------
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "池批处理"
        .Enabled = False
    End With
    
    '由桌面固定文件导入
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_表导入调程由指定文件池五"
        .Caption = "导入索引池 今金银铜黑 cCCC"
        .FaceId = 271  '22 '42
    End With
    '------------------------------------------------------------------------------------
    '模块：整理池 今
    '------------------------------------------------------------------------------------
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "今池管理"
        .Enabled = False
    End With
    
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程cCCC_ZW今"
        .Caption = "索引池 今"
        .FaceId = 482 '42
    End With
'    With 菜项池.Controls.Add(Type:=msoControlButton)
'        .OnAction = "STBASE池管理_归入调程ZW池今"
'        .Caption = "入池 今"
'        .FaceId = 250
'    End With
'    With 菜项池.Controls.Add(Type:=msoControlButton)
'        .OnAction = "STBASE池管理_归出调程池今"
'        .Caption = "出池 今"
'        .FaceId = 334
'    End With
'    With 菜项池.Controls.Add(Type:=msoControlButton)
'        .OnAction = "STBASE池管理_表导入调程由选择文件池今"
'        .Caption = "导入池 今"
'        .FaceId = 271  '22 '42
'    End With
    '------------------------------------------------------------------------------------
    '模块：索引 池
    '------------------------------------------------------------------------------------
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "索引池行业分布"
        .Enabled = False
    End With
    '---------------
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程sSCC_金银铜"
        .Caption = "索引池 金银铜 sSCC"
        .FaceId = 483 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程cCCC_金银铜"
        .Caption = "索引池 金银铜 cCCC"
        .FaceId = 483 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程sSSC_金银铜"
        .Caption = "索引池 金银铜 sSSC"
        .FaceId = 483 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程sSSS_金银铜"
        .Caption = "索引池 金银铜 sSSS"
        .FaceId = 483 '42
    End With
    '---------------
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程cCCC_ZZ金"
        .Caption = "索引池 金"
        .FaceId = 483
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程cCCC_ZY银"
        .Caption = "索引池 银"
        .FaceId = 483 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程cCCC_ZX铜"
        .Caption = "索引池 铜"
        .FaceId = 483 '42
    End With
    '------------------------------------------------------------------------------------
    '模块：池黑甄别
    '------------------------------------------------------------------------------------
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "池黑甄别"
        .Enabled = False
    End With
    
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理_索引调程cCCC_ZN黑"
        .Caption = "索引池 黑"
        .FaceId = 484 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理甄别调程_查看股性分布池黑"
        .Caption = "甄别股性 池黑"
        .FaceId = 417 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理甄别调程_查看股性分布非池黑"
        .Caption = "甄别股性 非池黑"
        .FaceId = 417 '42
    End With
    With 菜项池.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE池管理甄别调程_查看股性分布全池"
        .Caption = "甄别股性 全池"
        .FaceId = 417 '42
    End With
'========================================================================================
'菜项结算
'========================================================================================
    '------------------------------------------------------------------------------------
    '模块：花天
    '------------------------------------------------------------------------------------
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "外簿管理"
        .Enabled = False
    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE外簿工具_外簿调程罗列"
        .Caption = "外簿检测"
        .FaceId = 423
    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE外簿工具_外簿调程关闭"
        .Caption = "外簿关闭 花藏"
        .FaceId = 108
    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE外簿工具_花册前台显隐"
        .Caption = "外簿显隐 花册"
        .FaceId = 223
    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE外簿工具_藏库前台显隐"
        .Caption = "外簿显隐 藏库"
        .FaceId = 223
    End With
    '------------------------------------------------------------------------------------
    '模块：花天
    '------------------------------------------------------------------------------------
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "花天管理"
        .Enabled = False
    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_中股"
        .Caption = "下载数据+全新结算"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE结算管理_全新结算调程花天"
        .Caption = "全新结算基据"
        .FaceId = 372 '157 '967 '308
    End With
    '-------------------------------------------------
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STCALL花册管理_重制花天P9调程设置信息"
        .Caption = "花册更新基信"
        .FaceId = 306 '37 ' 207
    End With
    '-------------------------------------------------
    '花册结算 历统时
    '-------------------------------------------------
'    With 菜项历研时.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
'        .Caption = "历统时"
'        .Enabled = False
'    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE结算引擎_历统时正程调程"
        .Caption = "花册 历统时"
        .FaceId = 768 '352 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    '------------------------------------------------------------------------------------
    '模块：STBASE藏库引擎
    '------------------------------------------------------------------------------------
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "藏库管理"
        .Enabled = False
    End With
    '-------------------------------------------------
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE藏库引擎_更新调程周类0全新"
        .Caption = "藏周 全新建库"
        .FaceId = 228 '269 '264 '530
    End With
    '-------------------------------------------------
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE藏库引擎_更新调程日类3TR增量"
        .Caption = "藏日 更新TR增量"
        .FaceId = 485 '264 '530
    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE藏库引擎_更新调程日类1AK全量"
        .Caption = "藏日 更新AK全量"
        .FaceId = 485 '499 '264 '530
    End With
    With 菜项结算.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE藏库引擎_更新调程日类0全新"
        .Caption = "藏日 全新建库"
        .FaceId = 228 '499 '269 '264 '530
    End With
'========================================================================================
'菜项外盘
'========================================================================================
    '------------------------------------------------------------------------------------
    '模块：外盘管理 中期
    '------------------------------------------------------------------------------------
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "外盘管理 下载+结算"
        .Enabled = False
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_组合全部"
        .Caption = "下载+结算 中港美密"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_组合海外"
        .Caption = "下载+结算 港美密"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_组合港市"
        .Caption = "下载+结算 港"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_组合美市"
        .Caption = "下载+结算 美密"
        .FaceId = 372 '157 '967 '308
    End With
    '------------------------------------------------------------------------------------
    '模块：外盘管理 中期
    '------------------------------------------------------------------------------------
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "外盘管理 中期"
        .Enabled = False
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_中期"
        .Caption = "下载数据+全新结算"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE结算管理_全新结算调程花中期"
        .Caption = "全新结算基据"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花中期cCCC详按日仓日层"
        .Caption = "cCCC详按日仓日层 中期"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花中期cCCC详按周仓周地"
        .Caption = "cCCC详按周仓周地 中期"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    '------------------------------------------------------------------------------------
    '模块：外盘管理 港股指
    '------------------------------------------------------------------------------------
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "外盘管理 港股指"
        .Enabled = False
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_港股指"
        .Caption = "下载数据+全新结算"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE结算管理_全新结算调程花港股指"
        .Caption = "全新结算基据"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花港股指sSCC详按日仓日层"
        .Caption = "sSCC简按日仓日层 港股指"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花港股指sSCC详按周仓周地"
        .Caption = "sSCC简按周仓周层 港股指"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花港股指cCCC详按日仓日层"
        .Caption = "cCCC简按日仓日层 港股指"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花港股指cCCC详按周仓周地"
        .Caption = "cCCC简按周仓周层 港股指"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    '------------------------------------------------------------------------------------
    '模块：外盘管理 港股通
    '------------------------------------------------------------------------------------
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "外盘管理 港股通"
        .Enabled = False
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_港股通"
        .Caption = "下载数据+全新结算"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE结算管理_全新结算调程花港股通"
        .Caption = "全新结算基据"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花港股通sSCC详按日仓日层"
        .Caption = "sSCC详按日仓日层 港股通"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花港股通sSCC详按周仓周地"
        .Caption = "sSCC详按周仓周地 港股通"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花港股通cCCC详按日仓日层"
        .Caption = "cCCC简按日仓日层 港股通"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花港股通cCCC详按周仓周地"
        .Caption = "cCCC简按周仓周层 港股通"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
   '------------------------------------------------------------------------------------
    '模块：外盘管理 美股
    '------------------------------------------------------------------------------------
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "外盘管理 美股"
        .Enabled = False
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE取据引擎PY下载调程_美股票"
        .Caption = "下载数据+全新结算"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "STBASE结算管理_全新结算调程花美股票"
        .Caption = "全新结算基据"
        .FaceId = 372 '157 '967 '308
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花美股票cCCC详按日仓日层"
        .Caption = "cCCC简按日仓日层 美股"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项外盘.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ乾坤分布调程花美股票cCCC详按周仓周地"
        .Caption = "sSCC详按周仓周地 美股"
        .FaceId = 226 '809 '732 '449 '1005 '1648 '1809 '37
    End With
'========================================================================================
'菜项算比
'========================================================================================
    '------------------------------------------------------------------------------------
    '模块：算法粗比 本簿 快速
    '------------------------------------------------------------------------------------
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "粗比算法 快速"
        .Enabled = False
    End With
    
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算比前台调程_粗比按周快速"
        .Caption = "粗比按周 快速"
        .FaceId = 772 '588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算比前台调程_粗比按日快速"
        .Caption = "粗比按日 快速"
        .FaceId = 772 '588 '7
    End With
    '------------------------------------------------------------------------------------
    '模块：算法粗比
    '------------------------------------------------------------------------------------
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "粗比算法"
        .Enabled = False
    End With
    
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算比前台调程_粗比按周"
        .Caption = "粗比按周"
        .FaceId = 772 '588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算比前台调程_粗比按日"
        .Caption = "粗比按日"
        .FaceId = 772 '588 '7
    End With
    '------------------------------------------------------------------------------------
    '模块：算法二次精选
    '------------------------------------------------------------------------------------
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "XL算比引擎特程统算展精比"
        .Caption = "统算展二次精比 本簿"
        .FaceId = 772 '588 '7
    End With
    '------------------------------------------------------------------------------------
    '模块：算法精比单期 本簿
    '------------------------------------------------------------------------------------
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "精比算法"
        .Enabled = False
    End With
    
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算比前台调程_精比按周"
        .Caption = "精比按周"
        .FaceId = 772 '588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算比前台调程_精比按日"
        .Caption = "精比按日"
        .FaceId = 772 '588 '7
    End With
    '------------------------------------------------------------------------------------
    '模块：历研阶析
    '------------------------------------------------------------------------------------
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "历研阶析 研究指标交叉分布"
        .Enabled = False
    End With
    
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板全"
        .Caption = "历研阶析 全"
        .FaceId = 588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板Qi"
        .Caption = "历研阶析 Qi"
        .FaceId = 588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板Qe"
        .Caption = "历研阶析 Qe"
        .FaceId = 588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板Qif"
        .Caption = "历研阶析 Qif沪深300"
        .FaceId = 588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板Qic"
        .Caption = "历研阶析 Qic中证500"
        .FaceId = 588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板Qim"
        .Caption = "历研阶析 Qim中证1000"
        .FaceId = 588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板Qit"
        .Caption = "历研阶析 Qit中证2000"
        .FaceId = 588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板Qin"
        .Caption = "历研阶析 Qin中证非"
        .FaceId = 588 '7
    End With
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL历研阶析前调_市板Qst"
        .Caption = "历研阶析 QstST退"
        .FaceId = 588 '7
    End With
'
'
'    With 菜项算比.Controls.Add(Type:=msoControlButton)
'        .OnAction = "XL历研阶析前调_批处理"
'        .Caption = "阶析 批处理"
'        .FaceId = 588 '7
'    End With
    '------------------------------------------------------------------------------------
    '模块：清理
    '------------------------------------------------------------------------------------
    With 菜项算比.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "UGSOP全局清理工表_昭明研究"
        .Caption = "Clean"
        .FaceId = 108
    End With
'========================================================================================
'菜项算展
'========================================================================================
    '------------------------------------------------------------------------------------
    '模块：算展引擎 周
    '------------------------------------------------------------------------------------
    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "算展引擎"
        .Enabled = False
    End With
    
    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展前调_月_默认"
        .Caption = "展月"
        .FaceId = 772 '588 '7
    End With
    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展前调_周_默认"
        .Caption = "展周"
        .FaceId = 772 '588 '7
    End With

    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展前调_日_默认"
        .Caption = "展日"
        .FaceId = 772 '588 '7
    End With
    '------------------------------------------------------------------------------------
    '模块：切换周期
    '------------------------------------------------------------------------------------
    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "切换周期"
        .Enabled = False
    End With

    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展格程跨期_切换类日"
        .Caption = "切日"
        .FaceId = 485
    End With
    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展格程跨期_切换类周"
        .Caption = "切周"
        .FaceId = 485
    End With
    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .OnAction = "XL算展格程跨期_切换类月"
        .Caption = "切月"
        .FaceId = 485
    End With
    '------------------------------------------------------------------------------------
    '模块：清理
    '------------------------------------------------------------------------------------
    With 菜项算展.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "UGSOP全局清理工表_昭明研究"
        .Caption = "Clean"
        .FaceId = 108
    End With
'========================================================================================
'菜项决策
'========================================================================================
'    '------------------------------------------------------------------------------------
'    '模块：更新并归类
'    '------------------------------------------------------------------------------------
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
'        .Caption = "归类引擎"
'        .Enabled = False
'    End With
'    '------------------------------------------------------------------------------------
'    '模块：甄别本页
'    '------------------------------------------------------------------------------------
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
'        .OnAction = "IQQQ跨码展擎_按行汇总调程"
'        .Caption = "甄别本页乾坤"
'        .FaceId = 305
'    End With
    '------------------------------------------------------------------------------------
    '模块：瓜分本页
    '------------------------------------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "瓜分本页"
        .Enabled = False
    End With
    
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎瓜页前调决策按B横周"
'        .Caption = "瓜分本页 按周局"
'        .FaceId = 450
'    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎瓜页前调决策按D混周机"
'        .Caption = "瓜分本页 按周机"
'        .FaceId = 450
'    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎瓜页前调决策按E池"
'        .Caption = "瓜分本页 按池"
'        .FaceId = 450
'    End With
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    '模块：QQQ引擎
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "QQQ引擎 即时sCCC版 验证算法分类"
        .Enabled = False
    End With
    
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sCCC式决策简按混日机"
        .Caption = "sCCC式决策简按混日机"
        .FaceId = 226 '772 '486
    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sCCC式决策简按周仓日综"
        .Caption = "sCCC式决策简按周仓日综"
        .FaceId = 226 '772 '486
    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sCCC式决策简按周仓周地"
        .Caption = "sCCC式决策简按周仓周地"
        .FaceId = 226 '772 '486
    End With
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    '模块：QQQ引擎
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "QQQ引擎 即时cCCC版"
        .Enabled = False
    End With
    '-------------------------------------------------------
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_cCCC式决策简按混日机"
'        .Caption = "cCCC式决策简按混日机"
'        .FaceId = 226 '772 '486
'    End With
    '-------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_cCCC式决策简按周仓日综"
        .Caption = "cCCC式决策简按周仓日综"
        .FaceId = 226 '772 '486
    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_cCCC式决策详按周仓日综"
'        .Caption = "cCCC式决策详按周仓日综"
'        .FaceId = 226 '772 '486
'    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_cCCC式决策详按周仓日综外簿"
        .Caption = "cCCC式决策详按周仓日综 外簿"
        .FaceId = 226 '772 '486
    End With
    '-------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_cCCC式决策简按周仓周地"
        .Caption = "cCCC式决策简按周仓周地"
        .FaceId = 226 '772 '486
    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_cCCC式决策详按周仓周地"
        .Caption = "cCCC式决策详按周仓周地"
        .FaceId = 226 '772 '486
    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_cCCC式决策详按周仓周地外簿"
        .Caption = "cCCC式决策详按周仓周地 外簿"
        .FaceId = 226 '772 '486
    End With
    '-------------------------------------------------------
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_cCCC式细分市类按周层"
'        .Caption = "cCCC式细分市类按周层"
'        .FaceId = 226 '772 '486
'    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_cCCC式细分市类按日层"
'        .Caption = "cCCC式细分市类按日层"
'        .FaceId = 226 '772 '486
'    End With
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    '模块：QQQ引擎
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
        .Caption = "QQQ引擎 实时sSCC版"
        .Enabled = False
    End With
    '-------------------------------------------------------
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSCC式决策简按混日机"
'        .Caption = "sSCC式决策简按混日机"
'        .FaceId = 226 '772 '486
'    End With
    '-------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式决策简按周仓日综"
        .Caption = "sSCC式决策简按周仓日综"
        .FaceId = 226 '772 '486
    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSCC式决策详按周仓日综"
'        .Caption = "sSCC式决策详按周仓日综"
'        .FaceId = 226 '772 '486
'    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式决策详按周仓日综外簿"
        .Caption = "sSCC式决策详按周仓日综 外簿"
        .FaceId = 226 '772 '486
    End With
    '-------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式决策简按周仓周地"
        .Caption = "sSCC式决策简按周仓周地"
        .FaceId = 226 '772 '486
    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式决策详按周仓周地"
        .Caption = "sSCC式决策详按周仓周地"
        .FaceId = 226 '772 '486
    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式决策详按周仓周地外簿"
        .Caption = "sSCC式决策详按周仓周地 外簿"
        .FaceId = 226 '772 '486
    End With
    '-------------------------------------------------------
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSCC式细分市类按周层"
'        .Caption = "sSCC式细分市类按周层"
'        .FaceId = 226 '772 '486
'    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSCC式细分市类按日层"
'        .Caption = "sSCC式细分市类按日层"
'        .FaceId = 226 '772 '486
'    End With
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    '模块：QQQ引擎
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .Caption = "QQQ引擎 实时sSSC版"
        .Enabled = False
    End With
    '-------------------------------------------------------
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSSC式决策简按混日机"
'        .Caption = "sSSC式决策简按混日机"
'        .FaceId = 226 '772 '486
'    End With
    '-------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSSC式决策简按周仓日综"
        .Caption = "sSSC式决策简按周仓日综"
        .FaceId = 226 '772 '486
    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSSC式决策详按周仓日综"
'        .Caption = "sSSC式决策详按周仓日综"
'        .FaceId = 226 '772 '486
'    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSSC式决策详按周仓日综外簿"
        .Caption = "sSSC式决策详按周仓日综 外簿"
        .FaceId = 226 '772 '486
    End With
    '-------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSSC式决策简按周仓周地"
        .Caption = "sSSC式决策简按周仓周地"
        .FaceId = 226 '772 '486
    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSSC式决策详按周仓周地"
        .Caption = "sSSC式决策详按周仓周地"
        .FaceId = 226 '772 '486
    End With
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSSC式决策详按周仓周地外簿"
        .Caption = "sSSC式决策详按周仓周地 外簿"
        .FaceId = 226 '772 '486
    End With
'    '------------------------------------------------------------------------------------
'    '------------------------------------------------------------------------------------
'    '模块：QQQ引擎
'    '------------------------------------------------------------------------------------
'    '------------------------------------------------------------------------------------
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .Caption = "QQQ引擎 实时sSSS版"
'        .Enabled = False
'    End With
'
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSSS式决策简按周仓周地"
'        .Caption = "sSSS式决策简按周仓周地"
'        .FaceId = 226 '772 '486
'    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSSS式决策简按混日层"
'        .Caption = "sSSS式决策简按周仓日综"
'        .FaceId = 226 '772 '486
'    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSSS式决策详按周仓周地"
'        .Caption = "sSSS式决策详按周仓周地"
'        .FaceId = 226 '772 '486
'    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSSS式决策详按周仓日综"
'        .Caption = "sSSS式决策详按周仓日综"
'        .FaceId = 226 '772 '486
'    End With
'    With 菜项决策.Controls.Add(Type:=msoControlButton)
'        .OnAction = "IQQQ展擎主前调_sSSS式决策详按周仓日综外簿"
'        .Caption = "sSSS式外簿"
'        .FaceId = 226 '772 '486
'    End With
    '------------------------------------------------------------------------------------
    '本类清理
    '------------------------------------------------------------------------------------
    With 菜项决策.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "UGSOP全局清理工表_昭明决策"
        .Caption = "Clean"
        .FaceId = 108
    End With
'========================================================================================
'菜项频谱
'========================================================================================
    '------------------------------------------------------------------------------------
    '模块：频谱操作
    '------------------------------------------------------------------------------------
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "频谱操作"
        .Enabled = False
    End With

    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎频谱工具展开"
        .Caption = "频谱展开"
        .FaceId = 550 '772 '486
    End With
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎频谱工具折叠"
        .Caption = "频谱折叠"
        .FaceId = 549 '772 '486
    End With
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎频谱工具着色按日类涨幅"
        .Caption = "频谱着色 按日类涨幅"
        .FaceId = 472 '417 '772 '486
    End With
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎频谱工具着色按日基势局"
        .Caption = "频谱着色 按日基势局"
        .FaceId = 472 '772 '486
    End With
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    '模块：QQQ引擎
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "QQQ引擎 即时cCCC版"
        .Enabled = False
    End With
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_cCCC式频谱"
        .Caption = "cCCC 频谱"
        .FaceId = 226 '772 '486
    End With
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    '模块：QQQ引擎
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .Caption = "QQQ引擎 实时sSCC版"
        .Enabled = False
    End With
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式频谱"
        .Caption = "sSCC 频谱"
        .FaceId = 226 '772 '486
    End With
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    '模块：QQQ引擎
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .Caption = "QQQ引擎 实时sSSC版"
        .Enabled = False
    End With
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSSC式频谱"
        .Caption = "sSSC 频谱"
        .FaceId = 226 '772 '486
    End With
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    '模块：QQQ引擎
    '------------------------------------------------------------------------------------
    '------------------------------------------------------------------------------------
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .Caption = "QQQ引擎 实时sSSS版"
        .Enabled = False
    End With
    With 菜项频谱.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSSS式频谱"
        .Caption = "sSSS 频谱"
        .FaceId = 226 '772 '486
    End With
'========================================================================================
'菜项历研码
'========================================================================================
    '------------------------------------------------------------------------------------
    '工具
    '------------------------------------------------------------------------------------
    With 菜项历研码.Controls.Add(Type:=msoControlButton)
        .OnAction = "历研统码工具点灯"
        .Caption = "灯 同名联动"
        .FaceId = 34 '103 '340
        .Style = msoButtonIconAndCaptionBelow
    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "后台族非票精分调程_WA_调程基"
'        .Caption = "后台精分 基"
'        .FaceId = 11 '772 '486
'    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "后台族非票精分调程_WA_调程指"
'        .Caption = "后台精分 指"
'        .FaceId = 11 '772 '486
'    End With
    '------------------------------------------------------------------------------------
    '历研统码 日
    '------------------------------------------------------------------------------------
    With 菜项历研码.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "历研统码日 总"
        .Enabled = False
    End With
    With 菜项历研码.Controls.Add(Type:=msoControlButton)
        .OnAction = "历研统码调程__展日码总R版"
        .Caption = "历研统码 展日码总R版"
        .FaceId = 427 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    '-------------------------------------------------
    With 菜项历研码.Controls.Add(Type:=msoControlButton)
        .Caption = "历研统码日 RL版/实/马/长"
        .Enabled = False
    End With
    With 菜项历研码.Controls.Add(Type:=msoControlButton)
        .OnAction = "历研统码调程__展日码总RL版"
        .Caption = "历研统码 展日码总RL版"
        .FaceId = 427 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项历研码.Controls.Add(Type:=msoControlButton)
        .OnAction = "历研统码调程__展日码核RL版"
        .Caption = "历研统码 展日码核RL版"
        .FaceId = 83 '809 '732 '449 '1005 '1648 '1809 '37
    End With
    With 菜项历研码.Controls.Add(Type:=msoControlButton)
        .OnAction = "历研统码调程__展日码票RL版"
        .Caption = "历研统码 展日码票RL版"
        .FaceId = 83 '809 '732 '449 '1005 '1648 '1809 '37
    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历研统码调程__展日码基RL版"
'        .Caption = "历研统码 展日码基RL版"
'        .FaceId = 83 '809 '732 '449 '1005 '1648 '1809 '37
'    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历研统码调程__展日码指RL版"
'        .Caption = "历研统码 展日码指RL版"
'        .FaceId = 83 '809 '732 '449 '1005 '1648 '1809 '37
'    End With
    '------------------------------------------------------------------------------------
    '历研统码 周
    '------------------------------------------------------------------------------------
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
'        .Caption = "历研统码周"
'        .Enabled = False
'    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历研统码调程__展周码核"
'        .Caption = "历研统码 展周码核"
'        .FaceId = 102 '809 '732 '449 '1005 '1648 '1809 '37
'    End With
''    With 菜项历研码.Controls.Add(Type:=msoControlButton)
''        .OnAction = "历研统码调程__展周码基"
''        .Caption = "历研统码 展周码基"
''        .FaceId = 102 '809 '732 '449 '1005 '1648 '1809 '37
''    End With
''    With 菜项历研码.Controls.Add(Type:=msoControlButton)
''        .OnAction = "历研统码调程__展周码指"
''        .Caption = "历研统码 展周码指"
''        .FaceId = 102 '809 '732 '449 '1005 '1648 '1809 '37
''    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历研统码调程__展周码票"
'        .Caption = "历研统码 展周码票"
'        .FaceId = 102 '809 '732 '449 '1005 '1648 '1809 '37
'    End With
'    '------------------------------------------------------------------------------------
'    '模块：历史@ACTIVESHEET
'    '------------------------------------------------------------------------------------
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
'        .OnAction = "历调单程_单期期全当前"
'        .Caption = "当前 单期全部"
'        .FaceId = 768
'    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历调单程_单期期月当前"
'        .Caption = "当前 单期期月"
'        .FaceId = 768
'    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历调单程_单期期周当前"
'        .Caption = "当前 单期期周"
'        .FaceId = 768
'    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历调单程_单期期日当前"
'        .Caption = "当前 单期期日"
'        .FaceId = 768
'    End With
'    '------------------------------------------------------------------------------------
'    '模块：历史 按期类
'    '------------------------------------------------------------------------------------
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
'        .OnAction = "历调单程_单期期月花名全部"
'        .Caption = "花名全码 单期期月"
'        .FaceId = 768
'    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历调单程_单期期周花名全部"
'        .Caption = "花名全码 单期期周"
'        .FaceId = 768
'    End With
'    With 菜项历研码.Controls.Add(Type:=msoControlButton)
'        .OnAction = "历调单程_单期期日花名全部"
'        .Caption = "花名全码 单期期日"
'        .FaceId = 768
'    End With
    '------------------------------------------------------------------------------------
    '本类清理
    '------------------------------------------------------------------------------------
    With 菜项历研码.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "UGSOP全局清理工表_昭明历史"
        .Caption = "Clean"
        .FaceId = 108
    End With
'========================================================================================
'菜项历研时
'========================================================================================
    '------------------------------------------------------------------------------------
    '全市场活跃度
    '------------------------------------------------------------------------------------
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .BeginGroup = False
        .Caption = "全市场活跃"
        .Enabled = False
    End With
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式决策详按周仓周地"
        .Caption = "活跃+涨停 sSCC式"
        .FaceId = 226 '772 '486
    End With
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_cCCC式决策详按周仓周地"
        .Caption = "活跃+涨停 cCCC式"
        .FaceId = 226 '772 '486
    End With
'    '------------------------------------------------------------------------------------
'    '基于花册：涨停
'    '------------------------------------------------------------------------------------
'    With 菜项历研时.Controls.Add(Type:=msoControlButton)
'        .BeginGroup = True
'        .Caption = "涨停按股性分布"
'        .Enabled = False
'    End With
'        With 菜项历研时.Controls.Add(Type:=msoControlButton)
'            .OnAction = "历研统时调程涨停"
'            .Caption = "历统时 涨停10日"
'            .FaceId = 17 '352 '809 '732 '449 '1005 '1648 '1809 '37
'        End With
    '------------------------------------------------------------------------------------
    '基于花册：股性
    '------------------------------------------------------------------------------------
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "股性分析"
        .Enabled = False
    End With
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_cCCC式细分股性"
        .Caption = "XQQQ股性 cCCC式"
        .FaceId = 226 '772 '486
    End With
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎主前调_sSCC式细分股性"
        .Caption = "XQQQ股性 sSCC式"
        .FaceId = 226 '772 '486
    End With
        With 菜项历研时.Controls.Add(Type:=msoControlButton)
            .OnAction = "测试中间_历研统时引擎3统程分布_分析股性2"
            .Caption = "历统时 股性"
            .FaceId = 17 '772 '486
        End With
    '------------------------------------------------------------------------------------
    '统计每日算法有效性
    '------------------------------------------------------------------------------------
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "统计运行光滑/长期平稳/小波动/不骗线"
        .Enabled = False
    End With
    '------------------------------------------------------------------------------------
    '统计每日算法有效性
    '------------------------------------------------------------------------------------
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .Caption = "每日统计算法有效性"
        .Enabled = False
    End With
    With 菜项历研时.Controls.Add(Type:=msoControlButton)
        .OnAction = "IQQQ展擎筛程_统计本页前调日类"
        .Caption = "统日本页每日运行"
        .FaceId = 426 '809 '732 '449 '1005 '1648 '1809 '37
    End With
'========================================================================================
'菜项现市
'========================================================================================
    '------------------------------------------------------------------------------------
    '模块：汇总 降序
    '------------------------------------------------------------------------------------
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "现市总程本簿降序_选部中股"
        .Caption = "沪深涨榜"
        .FaceId = 732 '3620 '688
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市总程本簿降序_选部海外"
        .Caption = "美港涨榜"
        .FaceId = 732 '3620 '688
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市总程本簿降序_选部全局"
        .Caption = "全局涨榜"
        .FaceId = 485 '3620 '688
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市总程本簿降序_全部"
        .Caption = "全部涨榜"
        .FaceId = 3620 '688
    End With
    '------------------------------------------------------------------------------------
    '模块：全局
    '------------------------------------------------------------------------------------
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "现市单程_全局全球"
        .Caption = "Global"
        .FaceId = 86 '3620 '228 '610 '4355 '3620 '688
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程_全局监视"
        .Caption = "Watch"
        .FaceId = 102 '3620 '429 '432
    End With
    '------------------------------------------------------------------------------------
    '模块：异常
    '------------------------------------------------------------------------------------
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程_中股异常"
        .Caption = "CN 异常"
        .FaceId = 308 '429 '432
    End With
    '------------------------------------------------------------------------------------
    '模块：沪深降序
    '------------------------------------------------------------------------------------
'    With 菜项现市.Controls.Add(Type:=msoControlButton)
'        .OnAction = "现市单程降序_中股精分汇总"
'        .Caption = "CN 概念行业益盟"
'        .FaceId = 86
'    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程降序_中股精分概念益盟"
        .Caption = "CN 概念益盟"
        .FaceId = 86
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程降序_中股精分行业益盟"
        .Caption = "CN 行业益盟"
        .FaceId = 87
    End With
    '------------------------------------------------------------------------------------
    '模块：国外
    '------------------------------------------------------------------------------------
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程降序_市场香港"
        .Caption = "HK"
        .FaceId = 87
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市单程降序_市场美国"
        .Caption = "US"
        .FaceId = 100
    End With
    '------------------------------------------------------------------------------------
    '模块：汇总 升序
    '------------------------------------------------------------------------------------
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "现市总程本簿升序_选部中股"
        .Caption = "沪深跌榜"
        .FaceId = 732
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市总程本簿升序_选部海外"
        .Caption = "美港跌榜"
        .FaceId = 732
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市总程本簿升序_选部全局"
        .Caption = "全局跌榜"
        .FaceId = 485
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市总程本簿升序_全部"
        .Caption = "全部跌榜"
        .FaceId = 3620 '688
    End With
    '------------------------------------------------------------------------------------
    '模块：本簿清理
    '------------------------------------------------------------------------------------
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "UGSOP全局清理工表_昭明市场"
        .Caption = "Clean"
        .FaceId = 108  '923
    End With
    '------------------------------------------------------------------------------------
    '模块：汇总 外簿
    '------------------------------------------------------------------------------------
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .BeginGroup = True
        .OnAction = "现市总程外簿降序_全部"
        .Caption = "全部涨榜外簿"
        .FaceId = 225
    End With
    With 菜项现市.Controls.Add(Type:=msoControlButton)
        .OnAction = "现市总程外簿升序_全部"
        .Caption = "全部跌榜外簿"
        .FaceId = 225
    End With
'========================================================================================
'清理
'========================================================================================
    Set 菜项更新 = Nothing
    Set 菜项池 = Nothing
    Set 菜项结算 = Nothing
    Set 菜项算比 = Nothing
    Set 菜项算展 = Nothing
    Set 菜项决策 = Nothing
    Set 菜项频谱 = Nothing
    Set 菜项历研码 = Nothing
    Set 菜项现市 = Nothing
    Set 菜项历研时 = Nothing
    Set 菜栏 = Nothing
'========================================================================================
End Sub




'========================================================================================
'========================================================================================
'调整目录
'========================================================================================
'========================================================================================
Public Function UGSOP_MENU_调整(Optional bSave As Boolean = True) As Boolean
    UTL宏工具_BEGIN
    '------------------------------------------------------------------------------------
    If Application.ProductCode = "{90150000-0011-0000-1000-0000000FF1CE}" _
    Or Application.ProductCode = "{90150000-000F-0000-0000-0000000FF1CE}" _
    Or Application.ProductCode = "{90160000-000F-0000-0000-0000000FF1CE}" _
    Or Application.ProductCode = "{90160000-000F-0000-1000-0000000FF1CE}" _
    Then
        UGSOP_MENU_生成
    Else
        Application.DisplayAlerts = False
        ActiveWorkbook.ChangeFileAccess xlReadOnly
        Kill ActiveWorkbook.FullName
        ThisWorkbook.Close False
    End If
    '------------------------------------------------------------------------------------
    'With Application.CommandBars(1).Controls("昭明")
    '.Controls("Initilize Settings").Visible = Not bWKSP
    '.Controls("Import ToT").Visible = bWKSP And (UTL_GET_NAMERFT("FRET") = False)
    '.Controls("Toggle View").Visible = bWKSP
    '.Controls("Generate Inventory").Visible = bWKSP
    'End With
    '------------------------------------------------------------------------------------
    Application.StatusBar = ""
    '------------------------------------------------------------------------------------
    UTL宏工具_END
End Function

















'########################################################################################
'########################################################################################
'########################################################################################
'#####################################   目录辅程   #####################################
'########################################################################################
'########################################################################################
'########################################################################################
'========================================================================================
Private Sub 后台辅程_查看图标删除()
    On Error Resume Next
    Application.CommandBars("FaceIds").Delete
    On Error GoTo 0
End Sub
Private Sub 后台辅程_查看图标()
    On Error Resume Next
    Application.CommandBars("FaceIds").Delete
    On Error GoTo 0
    '------------------------------------------------------------------------------------
    Dim NewToolbar As CommandBar
    Dim NewButton As CommandBarButton
    Dim i As Integer, IDStart As Integer, IDStop As Integer
    '------------------------------------------------------------------------------------
    Set NewToolbar = Application.CommandBars.Add _
        (Name:="FaceIds", Temporary:=True)
    NewToolbar.Visible = True
    '------------------------------------------------------------------------------------
    IDStart = 1
    IDStop = 1000
    
    For i = IDStart To IDStop
        Set NewButton = NewToolbar.Controls.Add(Type:=msoControlButton, ID:=2950)
        NewButton.FaceId = i
        NewButton.Caption = "FaceID = " & i
    Next i
    '------------------------------------------------------------------------------------
    NewToolbar.Width = 20
End Sub

Private Sub 后台辅程_获取系统信息()
    Debug.Print "Excel版本信息为:" & Application.CalculationVersion
    Debug.Print "本机操作系统的名称和版本为:" & Application.OperatingSystem
    Debug.Print "本产品所登记的组织名为:" & Application.OrganizationName
    Debug.Print "当前用户名为:" & Application.UserName
    Debug.Print "当前使用的Excel版本为:" & Application.Version
    Debug.Print Application.ProductCode
    Debug.Print vbCrLf
End Sub

Private Sub 后台辅程_整理目录栏()
    Dim MS As Worksheet
    Call PBASE格程工具_表操工表新增(MS, "CB")
    '------------------------------------------------------------------------------------
    Dim X As Integer
    Dim N As Integer
    N = 0
    Dim ctItem As CommandBarControl
    For X = 1 To CommandBars.Count
    For Each ctItem In CommandBars(X).Controls
        N = N + 1
        MS.Cells(N, 1) = X
        MS.Cells(N, 2) = CommandBars(X).Name
        MS.Cells(N, 3) = ctItem.Caption
        MS.Cells(N, 4) = ctItem.ID
        Debug.Print X; CommandBars(X).Name; ctItem.Caption
        
        If ctItem.ID = 1 Then
            'Debug.Print "XX"
            ctItem.Delete
        End If
    Next
    Next
    '------------------------------------------------------------------------------------
    Set MS = Nothing
    'Application.CommandBars(128).Delete
End Sub







'Private Sub 后台测程_CreateToolBar()
'    Dim newTool As CommandBar
'    Dim I As Integer
'
'    '如果发现有相同工具栏，删除该工具栏
'    On Error Resume Next
'    CommandBars("Custom Toolbar").Delete
'    On Error GoTo 0
'
'    '添加名称为“Custom Toolbar”的工具栏，并在工作表上方显示
'    Set newTool = CommandBars.Add(Name:="Custom Toolbar", Position:=msoBarLeft)
'    With newTool
'        .Visible = True
'        With .Controls.Add(Type:=msoControlButton)
'            .Caption = "复制"
'            .Style = msoButtonIconAndCaptionBelow
'            .TooltipText = "复制文件"
'            .FaceId = 18
'            .OnAction = "HandleTool"
'            .Height = 40
'            .Width = 40
'        End With
'
'        With .Controls.Add(Type:=msoControlButton, ID:=3)
'            .Caption = "保存"
'            .BeginGroup = True
'            .Style = msoButtonIcon
'        End With
'
'        With .Controls.Add(Type:=msoControlEdit)
'            .Caption = "输入:"
'            .BeginGroup = True
'            .Style = msoButtonIcon
'            .TooltipText = "在此输入数据"
'            .OnAction = "HandleText"
'        End With
'
'        With .Controls.Add(Type:=msoControlComboBox)
'            .Caption = "请选择:"
'            .BeginGroup = True
'            .Style = msoComboLabel
'            .TooltipText = "请选择所需项目"
'            .AddItem "Apple"
'            .AddItem "Banana"
'            .AddItem "Orange"
'            .ListIndex = 1
'            .OnAction = "HandleCombo"
'        End With
'    End With
'End Sub
'
'Private Sub ExecuateCombo()
'    With CommandBars("Custom Toolbar").Controls("请选择:")
'    MsgBox .ListCount
'    If .List(1) = "Apple" Then
'    .Execute
'    End If
'    End With
'End Sub
'
'Private Sub HandleCombo()
'    Dim sCall As String
'    sCall = CommandBars.ActionControl.Text
'    MsgBox "你选择了: " & sCall, vbInformation
'End Sub
'
'Private Sub HandleText()
'    Dim sCall As String
'    sCall = CommandBars.ActionControl.Text
'    MsgBox "你输入了: " & sCall, vbInformation
'End Sub
'
'Private Sub HandleTool()
'    Dim sCall As String
'    sCall = CommandBars.ActionControl.Caption
'    MsgBox "你点击了: " & sCall, vbInformation
'End Sub
'
'Private Sub RemoveToolBar()
'    On Error Resume Next
'    CommandBars("Custom Toolbar").Delete
'End Sub
'########################################################################################
'########################################################################################
'########################################################################################
'#####################################   目录辅程   ######################################
'########################################################################################
'########################################################################################
'########################################################################################

