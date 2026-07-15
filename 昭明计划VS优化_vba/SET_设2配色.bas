Attribute VB_Name = "SET_设2配色"
Option Explicit
'尝试使用OLE_COLOR作为常量类型或函数返回类型
'重新设置以下常色体系，保证每个色系有足够选择，并且命名规则适用，用RGB进行备注
'-----------------------------------------------
'========================================================================================
'艺术色系
Public Const 常色克莱因蓝 = 10956544        'RGB(   0,  47, 167)   — #002FA7
Public Const 常色蒂芙尼蓝 = 13621377        'RGB( 129, 216, 207)   — #81D8CF
Public Const 常色普鲁士蓝 = 5386496         'RGB(   0,  49,  82)   — #003152
Public Const 常色提香红 = 2316720           'RGB( 176,  89,  35)   — #B05923
Public Const 常色勃艮第红 = 2162832         'RGB( 144,   0,  33)   — #900021
Public Const 常色申布伦黄 = 7000827         'RGB( 251, 210, 106)   — #FBD26A
Public Const 常色凡戴克棕 = 2640783         'RGB( 143,  75,  40)   — #8F4B28
Public Const 常色马尔斯绿 = 8356865         'RGB(   1, 132, 127)   — #01847F
Public Const 常色只此青绿 = 13688896        'RGB(  64, 224, 208)   — #40E0D0
'========================================================================================
'特色系
'========================================================================================
'靛色系
Public Const 常色主靛 = 12611584            'RGB(   0, 112, 192)
Public Const 常色十靛 = 16750080            'RGB(   0, 150, 255)
Public Const 常色九靛 = 16745216            'RGB(   0, 131, 255)
Public Const 常色八靛 = 12611584            'RGB(   0, 112, 192) — 同主靛
Public Const 常色七靛 = 11166720            'RGB(   0, 100, 170)
Public Const 常色六靛 = 9853440             'RGB(   0,  90, 150)
Public Const 常色五靛 = 8409088             'RGB(   0,  80, 128)
Public Const 常色四靛 = 6568960             'RGB(   0,  60, 100)
Public Const 常色三靛 = 4926720             'RGB(   0,  45,  75)
Public Const 常色二靛 = 3284480             'RGB(   0,  30,  50)
Public Const 常色一靛 = 1642240             'RGB(   0,  15,  25)
Public Const 常色灰靛 = 16757910            'RGB( 150, 180, 255)
'-----------
'碧色系
Public Const 常色主碧 = 6723891             'RGB(  51, 153, 102) — 同八碧
Public Const 常色十碧 = 10066227            'RGB(  51, 153, 153)
Public Const 常色九碧 = 8427827             'RGB(  51, 153, 128)
Public Const 常色八碧 = 6723891             'RGB(  51, 153, 102)
Public Const 常色七碧 = 6717491             'RGB(  51, 128, 102)
Public Const 常色六碧 = 6710835             'RGB(  51, 102, 102)
Public Const 常色五碧 = 6710784             'RGB(   0, 102, 102)
Public Const 常色四碧 = 5065984             'RGB(   0,  77,  77)
Public Const 常色三碧 = 3355392             'RGB(   0,  51,  51)
Public Const 常色二碧 = 1710592             'RGB(   0,  26,  26)
Public Const 常色一碧 = 0                   'RGB(   0,   0,   0)
Public Const 常色灰碧 = 10079385            'RGB( 153, 204, 153)
'-----------
'43色系
Public Const 常色主43 = 52377               'RGB( 153, 204,   0) — 同八43
Public Const 常色十43 = 65484               'RGB( 204, 255,   0)
Public Const 常色九43 = 65458               'RGB( 178, 255,   0)
Public Const 常色八43 = 52377               'RGB( 153, 204,   0) — 同主43
Public Const 常色七43 = 45696               'RGB( 128, 178,   0)
Public Const 常色六43 = 39270               'RGB( 102, 153,   0)
Public Const 常色五43 = 32845               'RGB(  77, 128,   0)
Public Const 常色四43 = 26163               'RGB(  51, 102,   0)
Public Const 常色三43 = 19738               'RGB(  26,  77,   0)
Public Const 常色二43 = 13056               'RGB(   0,  51,   0)
Public Const 常色一43 = 6656                'RGB(   0,  26,   0)
Public Const 常色灰43 = 10092492            'RGB( 204, 255, 153)
'========================================================================================
'纯色系
'========================================================================================
'-----------
'赤色系
Public Const 常色主红 = 204                 'RGB( 204,   0,   0) — 同八红
Public Const 常色十红 = 255                 'RGB( 255,   0,   0)
Public Const 常色九红 = 230                 'RGB( 230,   0,   0)
Public Const 常色八红 = 204                 'RGB( 204,   0,   0)
Public Const 常色七红 = 179                 'RGB( 179,   0,   0)
Public Const 常色六红 = 153                 'RGB( 153,   0,   0)
Public Const 常色五红 = 127                 'RGB( 127,   0,   0)
Public Const 常色四红 = 102                 'RGB( 102,   0,   0)
Public Const 常色三红 = 77                   'RGB(  77,   0,   0)
Public Const 常色二红 = 51                  'RGB(  51,   0,   0)
Public Const 常色一红 = 26                  'RGB(  26,   0,   0)
Public Const 常色灰红 = 9869055             'RGB( 255, 150, 150)
'-----------
'橙色系
Public Const 常色主橙 = 31948               'RGB( 204, 124,   0) — 同八橙
Public Const 常色十橙 = 39935               'RGB( 255, 155,   0)
Public Const 常色九橙 = 36070               'RGB( 230, 140,   0)
Public Const 常色八橙 = 31948               'RGB( 204, 124,   0)
Public Const 常色七橙 = 27852               'RGB( 204, 108,   0)
Public Const 常色六橙 = 23961               'RGB( 153,  93,   0)
Public Const 常色五橙 = 19839               'RGB( 127,  77,   0)
Public Const 常色四橙 = 15974               'RGB( 102,  62,   0)
Public Const 常色三橙 = 11853               'RGB(  77,  46,   0)
Public Const 常色二橙 = 7987                'RGB(  51,  31,   0)
Public Const 常色一橙 = 3866                'RGB(  26,  15,   0)
Public Const 常色灰橙 = 8441087             'RGB( 255, 204, 128)
'-----------
'黄色系
Public Const 常色主黄 = 52428               'RGB( 204, 204,   0) — 同八黄
Public Const 常色十黄 = 65535               'RGB( 255, 255,   0)
Public Const 常色九黄 = 59135               'RGB( 255, 230,   0)
Public Const 常色八黄 = 52428               'RGB( 204, 204,   0)
Public Const 常色七黄 = 44461               'RGB( 173, 173,   0)
Public Const 常色六黄 = 38550               'RGB( 150, 150,   0)
Public Const 常色五黄 = 32896               'RGB( 128, 128,   0)
Public Const 常色四黄 = 26214               'RGB( 102, 102,   0)
Public Const 常色三黄 = 19789               'RGB(  77,  77,   0)
Public Const 常色二黄 = 13107               'RGB(  51,  51,   0)
Public Const 常色一黄 = 6682                'RGB(  26,  26,   0)
Public Const 常色灰黄 = 8441036             'RGB( 204, 204, 128)
'-----------
'绿色系
Public Const 常色主绿 = 52224               'RGB(   0, 204,   0) — 同八绿
Public Const 常色十绿 = 65280               'RGB(   0, 255,   0)
Public Const 常色九绿 = 58624               'RGB(   0, 229,   0)
Public Const 常色八绿 = 52224               'RGB(   0, 204,   0)
Public Const 常色七绿 = 45568               'RGB(   0, 178,   0)
Public Const 常色六绿 = 39168               'RGB(   0, 153,   0)
Public Const 常色五绿 = 32768               'RGB(   0, 128,   0)
Public Const 常色四绿 = 26112               'RGB(   0, 102,   0)
Public Const 常色三绿 = 19712               'RGB(   0,  77,   0)
Public Const 常色二绿 = 13056               'RGB(   0,  51,   0)
Public Const 常色一绿 = 6656                'RGB(   0,  26,   0)
Public Const 常色灰绿 = 9895830             'RGB( 150, 255, 150)
'-----------
'青色系
Public Const 常色主青 = 13421568            'RGB(   0, 204, 204) — 同八青
Public Const 常色十青 = 16776960            'RGB(   0, 255, 255)
Public Const 常色九青 = 15132160            'RGB(   0, 230, 230)
Public Const 常色八青 = 13421568            'RGB(   0, 204, 204)
Public Const 常色七青 = 11710976            'RGB(   0, 178, 178)
Public Const 常色六青 = 9868800             'RGB(   0, 150, 150)
Public Const 常色五青 = 8421376             'RGB(   0, 128, 128)
Public Const 常色四青 = 6710784             'RGB(   0, 102, 102)
Public Const 常色三青 = 4934400             'RGB(   0,  75,  75)
Public Const 常色二青 = 3355392             'RGB(   0,  51,  51)
Public Const 常色一青 = 1710592             'RGB(   0,  26,  26)
'-----------
'蓝色系
Public Const 常色主蓝 = 13369344            'RGB(   0,   0, 204) — 同八蓝
Public Const 常色十蓝 = 16711680            'RGB(   0,   0, 255)
Public Const 常色九蓝 = 15073280            'RGB(   0,   0, 230)
Public Const 常色八蓝 = 13369344            'RGB(   0,   0, 204)
Public Const 常色七蓝 = 11665408            'RGB(   0,   0, 178)
Public Const 常色六蓝 = 10027008            'RGB(   0,   0, 153)
Public Const 常色五蓝 = 8323072             'RGB(   0,   0, 127)
Public Const 常色四蓝 = 6684672             'RGB(   0,   0, 102)
Public Const 常色三蓝 = 5046272             'RGB(   0,   0,  77)
Public Const 常色二蓝 = 3342336             'RGB(   0,   0,  51)
Public Const 常色一蓝 = 1703936             'RGB(   0,   0,  26)
Public Const 常色灰蓝 = 16750230            'RGB( 150, 150, 255)
'-----------
'紫色系
Public Const 常色主紫 = 13107400            'RGB( 200,   0, 200) — 同八紫
Public Const 常色十紫 = 16711935            'RGB( 255,   0, 255)
Public Const 常色九紫 = 15073510            'RGB( 230,   0, 230)
Public Const 常色八紫 = 13107400            'RGB( 200,   0, 200)
Public Const 常色七紫 = 11665586            'RGB( 178,   0, 178)
Public Const 常色六紫 = 9830550             'RGB( 150,   0, 150)
Public Const 常色五紫 = 8388736             'RGB( 128,   0, 128)
Public Const 常色四紫 = 6684774             'RGB( 102,   0, 102)
Public Const 常色三紫 = 4653127             'RGB(  71,   0,  71)
Public Const 常色二紫 = 3342387             'RGB(  51,   0,  51)
Public Const 常色一紫 = 1703962             'RGB(  26,   0,  26)
Public Const 常色灰紫 = 13145800            'RGB( 200, 150, 200)
'-----------
'灰色系
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
Public Const 常色主黑 = 0                   'RGB(   0,   0,   0)
'========================================================================================
'配色
'========================================================================================
Public Const 常色勿动 = 常色主白
Public Const 常色行情 = 常色十蓝
Public Const 常色指金 = 常色主靛
Public Const 常色研究 = 常色灰绿
'========================================================================================

Private Sub 后台辅程颜色转换_RGB2OLE_测试2()
    Dim c As Long
    c = 后台辅程颜色转换_RGB2OLE(51, 153, 102)
    Debug.Print c
    With Columns("b").Interior
        .Color = c
    End With
    ThisWorkbook.Activate
End Sub


Private Sub 后台辅程颜色转换_RGB2OLE_测试()
    Debug.Print "========== 艺术色系 =========="
    Debug.Print "常色克莱因蓝  RGB(0,47,167)     = " & RGB(0, 47, 167)
    Debug.Print "常色蒂芙尼蓝  RGB(129,216,207)  = " & RGB(129, 216, 207)
    Debug.Print "常色普鲁士蓝  RGB(0,49,82)      = " & RGB(0, 49, 82)
    Debug.Print "常色提香红    RGB(176,89,35)    = " & RGB(176, 89, 35)
    Debug.Print "常色勃艮第红  RGB(144,0,33)     = " & RGB(144, 0, 33)
    Debug.Print "常色申布伦黄  RGB(251,210,106)  = " & RGB(251, 210, 106)
    Debug.Print "常色凡戴克棕  RGB(143,75,40)    = " & RGB(143, 75, 40)
    Debug.Print "常色马尔斯绿  RGB(1,132,127)    = " & RGB(1, 132, 127)
    Debug.Print "常色只此青绿  RGB(64,224,208)   = " & RGB(64, 224, 208)
    Debug.Print ""
    Debug.Print "========== 靛色系 =========="
    Debug.Print "常色主靛/八靛 RGB(0,112,192)    = " & RGB(0, 112, 192)
    Debug.Print "常色十靛      RGB(0,150,255)    = " & RGB(0, 150, 255)
    Debug.Print "常色九靛      RGB(0,131,255)    = " & RGB(0, 131, 255)
    Debug.Print "常色七靛      RGB(0,100,170)    = " & RGB(0, 100, 170)
    Debug.Print "常色六靛      RGB(0,90,150)     = " & RGB(0, 90, 150)
    Debug.Print "常色五靛      RGB(0,80,128)     = " & RGB(0, 80, 128)
    Debug.Print "常色四靛      RGB(0,60,100)     = " & RGB(0, 60, 100)
    Debug.Print "常色三靛      RGB(0,45,75)      = " & RGB(0, 45, 75)
    Debug.Print "常色二靛      RGB(0,30,50)      = " & RGB(0, 30, 50)
    Debug.Print "常色一靛      RGB(0,15,25)      = " & RGB(0, 15, 25)
    Debug.Print "常色灰靛      RGB(150,180,255)  = " & RGB(150, 180, 255)
    Debug.Print ""
    Debug.Print "========== 碧色系 =========="
    Debug.Print "常色主碧/八碧 RGB(51,153,102)   = " & RGB(51, 153, 102)
    Debug.Print "常色主碧      RGB(51,153,153)   = " & RGB(51, 153, 153)
    Debug.Print "常色九碧      RGB(51,153,128)   = " & RGB(51, 153, 128)
    Debug.Print "常色七碧      RGB(51,128,102)   = " & RGB(51, 128, 102)
    Debug.Print "常色六碧      RGB(51,102,102)   = " & RGB(51, 102, 102)
    Debug.Print "常色五碧      RGB(0,102,102)    = " & RGB(0, 102, 102)
    Debug.Print "常色四碧      RGB(0,77,77)      = " & RGB(0, 77, 77)
    Debug.Print "常色三碧      RGB(0,51,51)      = " & RGB(0, 51, 51)
    Debug.Print "常色二碧      RGB(0,26,26)      = " & RGB(0, 26, 26)
    Debug.Print "常色一碧      RGB(0,0,0)        = " & RGB(0, 0, 0)
    Debug.Print "常色灰碧      RGB(153,204,153)  = " & RGB(153, 204, 153)
    Debug.Print ""
    Debug.Print "========== 43色系 =========="
    Debug.Print "常色主43/八43 RGB(153,204,0)    = " & RGB(153, 204, 0)
    Debug.Print "常色十43      RGB(204,255,0)    = " & RGB(204, 255, 0)
    Debug.Print "常色九43      RGB(178,255,0)    = " & RGB(178, 255, 0)
    Debug.Print "常色七43      RGB(128,178,0)    = " & RGB(128, 178, 0)
    Debug.Print "常色六43      RGB(102,153,0)    = " & RGB(102, 153, 0)
    Debug.Print "常色五43      RGB(77,128,0)     = " & RGB(77, 128, 0)
    Debug.Print "常色四43      RGB(51,102,0)     = " & RGB(51, 102, 0)
    Debug.Print "常色三43      RGB(26,77,0)      = " & RGB(26, 77, 0)
    Debug.Print "常色二43      RGB(0,51,0)       = " & RGB(0, 51, 0)
    Debug.Print "常色一43      RGB(0,26,0)       = " & RGB(0, 26, 0)
    Debug.Print "常色灰43      RGB(204,255,153)  = " & RGB(204, 255, 153)
    Debug.Print ""
    Debug.Print "========== 赤色系 =========="
    Debug.Print "常色主红/八红 RGB(204,0,0)      = " & RGB(204, 0, 0)
    Debug.Print "常色十红      RGB(255,0,0)      = " & RGB(255, 0, 0)
    Debug.Print "常色九红      RGB(230,0,0)      = " & RGB(230, 0, 0)
    Debug.Print "常色七红      RGB(179,0,0)      = " & RGB(179, 0, 0)
    Debug.Print "常色六红      RGB(153,0,0)      = " & RGB(153, 0, 0)
    Debug.Print "常色五红      RGB(127,0,0)      = " & RGB(127, 0, 0)
    Debug.Print "常色四红      RGB(102,0,0)      = " & RGB(102, 0, 0)
    Debug.Print "常色三红      RGB(77,0,0)       = " & RGB(77, 0, 0)
    Debug.Print "常色二红      RGB(51,0,0)       = " & RGB(51, 0, 0)
    Debug.Print "常色一红      RGB(26,0,0)       = " & RGB(26, 0, 0)
    Debug.Print "常色灰红      RGB(255,150,150)  = " & RGB(255, 150, 150)
    Debug.Print ""
    Debug.Print "========== 橙色系 =========="
    Debug.Print "常色主橙/八橙 RGB(204,124,0)    = " & RGB(204, 124, 0)
    Debug.Print "常色十橙      RGB(255,155,0)    = " & RGB(255, 155, 0)
    Debug.Print "常色九橙      RGB(230,140,0)    = " & RGB(230, 140, 0)
    Debug.Print "常色七橙      RGB(204,108,0)    = " & RGB(204, 108, 0)
    Debug.Print "常色六橙      RGB(153,93,0)     = " & RGB(153, 93, 0)
    Debug.Print "常色五橙      RGB(127,77,0)     = " & RGB(127, 77, 0)
    Debug.Print "常色四橙      RGB(102,62,0)     = " & RGB(102, 62, 0)
    Debug.Print "常色三橙      RGB(77,46,0)      = " & RGB(77, 46, 0)
    Debug.Print "常色二橙      RGB(51,31,0)      = " & RGB(51, 31, 0)
    Debug.Print "常色一橙      RGB(26,15,0)      = " & RGB(26, 15, 0)
    Debug.Print "常色灰橙      RGB(255,204,128)  = " & RGB(255, 204, 128)
    Debug.Print ""
    Debug.Print "========== 黄色系 =========="
    Debug.Print "常色主黄/八黄 RGB(204,204,0)    = " & RGB(204, 204, 0)
    Debug.Print "常色十黄      RGB(255,255,0)    = " & RGB(255, 255, 0)
    Debug.Print "常色九黄      RGB(255,230,0)    = " & RGB(255, 230, 0)
    Debug.Print "常色七黄      RGB(173,173,0)    = " & RGB(173, 173, 0)
    Debug.Print "常色六黄      RGB(150,150,0)    = " & RGB(150, 150, 0)
    Debug.Print "常色五黄      RGB(128,128,0)    = " & RGB(128, 128, 0)
    Debug.Print "常色四黄      RGB(102,102,0)    = " & RGB(102, 102, 0)
    Debug.Print "常色三黄      RGB(77,77,0)      = " & RGB(77, 77, 0)
    Debug.Print "常色二黄      RGB(51,51,0)      = " & RGB(51, 51, 0)
    Debug.Print "常色一黄      RGB(26,26,0)      = " & RGB(26, 26, 0)
    Debug.Print "常色灰黄      RGB(204,204,128)  = " & RGB(204, 204, 128)
    Debug.Print ""
    Debug.Print "========== 绿色系 =========="
    Debug.Print "常色主绿/八绿 RGB(0,204,0)      = " & RGB(0, 204, 0)
    Debug.Print "常色十绿      RGB(0,255,0)      = " & RGB(0, 255, 0)
    Debug.Print "常色九绿      RGB(0,229,0)      = " & RGB(0, 229, 0)
    Debug.Print "常色七绿      RGB(0,178,0)      = " & RGB(0, 178, 0)
    Debug.Print "常色六绿      RGB(0,153,0)      = " & RGB(0, 153, 0)
    Debug.Print "常色五绿      RGB(0,128,0)      = " & RGB(0, 128, 0)
    Debug.Print "常色四绿      RGB(0,102,0)      = " & RGB(0, 102, 0)
    Debug.Print "常色三绿      RGB(0,77,0)       = " & RGB(0, 77, 0)
    Debug.Print "常色二绿      RGB(0,51,0)       = " & RGB(0, 51, 0)
    Debug.Print "常色一绿      RGB(0,26,0)       = " & RGB(0, 26, 0)
    Debug.Print "常色灰绿      RGB(150,255,150)  = " & RGB(150, 255, 150)
    Debug.Print ""
    Debug.Print "========== 青色系 =========="
    Debug.Print "常色主青/八青 RGB(0,204,204)    = " & RGB(0, 204, 204)
    Debug.Print "常色十青      RGB(0,255,255)    = " & RGB(0, 255, 255)
    Debug.Print "常色九青      RGB(0,230,230)    = " & RGB(0, 230, 230)
    Debug.Print "常色七青      RGB(0,178,178)    = " & RGB(0, 178, 178)
    Debug.Print "常色六青      RGB(0,150,150)    = " & RGB(0, 150, 150)
    Debug.Print "常色五青      RGB(0,128,128)    = " & RGB(0, 128, 128)
    Debug.Print "常色四青      RGB(0,102,102)    = " & RGB(0, 102, 102)
    Debug.Print "常色三青      RGB(0,75,75)      = " & RGB(0, 75, 75)
    Debug.Print "常色二青      RGB(0,51,51)      = " & RGB(0, 51, 51)
    Debug.Print "常色一青      RGB(0,26,26)      = " & RGB(0, 26, 26)
    Debug.Print ""
    Debug.Print "========== 蓝色系 =========="
    Debug.Print "常色主蓝/八蓝 RGB(0,0,204)      = " & RGB(0, 0, 204)
    Debug.Print "常色十蓝      RGB(0,0,255)      = " & RGB(0, 0, 255)
    Debug.Print "常色九蓝      RGB(0,0,230)      = " & RGB(0, 0, 230)
    Debug.Print "常色七蓝      RGB(0,0,178)      = " & RGB(0, 0, 178)
    Debug.Print "常色六蓝      RGB(0,0,153)      = " & RGB(0, 0, 153)
    Debug.Print "常色五蓝      RGB(0,0,127)      = " & RGB(0, 0, 127)
    Debug.Print "常色四蓝      RGB(0,0,102)      = " & RGB(0, 0, 102)
    Debug.Print "常色三蓝      RGB(0,0,77)       = " & RGB(0, 0, 77)
    Debug.Print "常色二蓝      RGB(0,0,51)       = " & RGB(0, 0, 51)
    Debug.Print "常色一蓝      RGB(0,0,26)       = " & RGB(0, 0, 26)
    Debug.Print "常色灰蓝      RGB(150,150,255)  = " & RGB(150, 150, 255)
    Debug.Print ""
    Debug.Print "========== 紫色系 =========="
    Debug.Print "常色主紫/八紫 RGB(200,0,200)    = " & RGB(200, 0, 200)
    Debug.Print "常色十紫      RGB(255,0,255)    = " & RGB(255, 0, 255)
    Debug.Print "常色九紫      RGB(230,0,230)    = " & RGB(230, 0, 230)
    Debug.Print "常色七紫      RGB(178,0,178)    = " & RGB(178, 0, 178)
    Debug.Print "常色六紫      RGB(150,0,150)    = " & RGB(150, 0, 150)
    Debug.Print "常色五紫      RGB(128,0,128)    = " & RGB(128, 0, 128)
    Debug.Print "常色四紫      RGB(102,0,102)    = " & RGB(102, 0, 102)
    Debug.Print "常色三紫      RGB(71,0,71)      = " & RGB(71, 0, 71)
    Debug.Print "常色二紫      RGB(51,0,51)      = " & RGB(51, 0, 51)
    Debug.Print "常色一紫      RGB(26,0,26)      = " & RGB(26, 0, 26)
    Debug.Print "常色灰紫      RGB(200,150,200)  = " & RGB(200, 150, 200)
    Debug.Print ""
    Debug.Print "========== 灰色系 =========="
    Debug.Print "常色主白      RGB(255,255,255)  = " & RGB(255, 255, 255)
    Debug.Print "常色主灰/八灰 RGB(204,204,204)  = " & RGB(204, 204, 204)
    Debug.Print "常色十灰      RGB(255,255,255)  = " & RGB(255, 255, 255)
    Debug.Print "常色九灰      RGB(230,230,230)  = " & RGB(230, 230, 230)
    Debug.Print "常色七灰      RGB(175,175,175)  = " & RGB(175, 175, 175)
    Debug.Print "常色六灰      RGB(150,150,150)  = " & RGB(150, 150, 150)
    Debug.Print "常色五灰      RGB(126,126,126)  = " & RGB(126, 126, 126)
    Debug.Print "常色四灰      RGB(102,102,102)  = " & RGB(102, 102, 102)
    Debug.Print "常色三灰      RGB(75,75,75)     = " & RGB(75, 75, 75)
    Debug.Print "常色二灰      RGB(51,51,51)     = " & RGB(51, 51, 51)
    Debug.Print "常色一灰      RGB(25,25,25)     = " & RGB(25, 25, 25)
    Debug.Print "常色主黑      RGB(0,0,0)        = " & RGB(0, 0, 0)
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
    Dim i%
    Dim 色度 As Long
    For i = 1 To 60
        With Cells(i, 2)
            .Value = i
            .Comment.Delete
            .AddComment
            .Comment.Visible = False
            .Comment.Shape.Width = 180
            .Comment.Shape.Height = 70
            .Comment.Shape.Fill.Solid
            .Comment.Shape.Fill.ForeColor.SchemeColor = i
        End With
        Cells(i, 3).Interior.ColorIndex = i
        Cells(i, 3) = i
        色度 = Cells(i, 3).Interior.Color
        Cells(i, 4) = 色度
        Cells(i, 5) = 后台辅程颜色转换_OLE2RGB(色度)
    Next
    '------------------------------------------------------------------------------------
    On Error GoTo 0
End Sub



Private Sub 后台辅程颜色测试()
    Dim 色度 As Long
    色度 = 常色八绿
    Call 后台辅程颜色转换_OLE2RGB(常色八绿)
    ActiveSheet.Cells.Interior.Color = 色度
End Sub
Private Function 后台辅程颜色转换_OLE2RGB(Color As Variant) As String
    Dim R%, G%, B%
    Dim MSG As String
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
    R = WorksheetFunction.Hex2Dec(Left$(CHEX, 2))
    G = WorksheetFunction.Hex2Dec(Mid$(CHEX, 3, 2))
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



