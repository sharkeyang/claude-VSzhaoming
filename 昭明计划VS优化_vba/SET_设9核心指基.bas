Attribute VB_Name = "SET_设9核心指基"
Option Explicit

'########################################################################################
'########################################################################################
'############################      IQQQ乾坤分布调程      #################################
'########################################################################################
'########################################################################################
Sub IQQQ乾坤分布调程SSC_典核心指基()
    Dim 指定表名  As String
    指定表名 = "Qx"
    Dim 典码称 As New Dictionary
    Call 后台族非票精分调程_WA_设置典核心行业(典码称)
    UTL宏工具_BEGIN
    Call IQQQ展擎出程至页(ThisWorkbook, 指定表名, 是否建表:=True, 章色:=常色主靛, 章签:="")
    Call IQQQ展擎筛程_出程更新通用(ThisWorkbook, 指定表名, 典码输出:=典码称, 实结类型:="sSCC", 基色底:=常色主靛)
    UTL宏工具_END
End Sub
Sub IQQQ乾坤分布调程SSC_典指必选()
    Dim 指定表名  As String
    指定表名 = "Qi"
    Dim 典码称 As New Dictionary
    Call 后台族非票精分调程_WA_制作典指必选(典码称)
    UTL宏工具_BEGIN
    Call IQQQ展擎出程至页(ThisWorkbook, 指定表名, 是否建表:=True, 章色:=常色主靛, 章签:="")
    Call IQQQ展擎筛程_出程更新通用(ThisWorkbook, 指定表名, 典码输出:=典码称, 实结类型:="sSCC", 基色底:=常色主靛)
    UTL宏工具_END
End Sub
Sub IQQQ乾坤分布调程SSC_典基必选()
    Dim 指定表名  As String
    指定表名 = "Qe"
    Dim 典码称 As New Dictionary
    Call 后台族非票精分调程_WA_制作典基必选(典码称)
    UTL宏工具_BEGIN
    Call IQQQ展擎出程至页(ThisWorkbook, 指定表名, 是否建表:=True, 章色:=常色主靛, 章签:="")
    Call IQQQ展擎筛程_出程更新通用(ThisWorkbook, 指定表名, 典码输出:=典码称, 实结类型:="sSCC", 基色底:=常色主靛)
    UTL宏工具_END
End Sub
'########################################################################################
'########################################################################################
'############################      IQQQ乾坤分布调程      #################################
'########################################################################################
'########################################################################################





'########################################################################################
'########################################################################################
'############################      非票精分调程设置      ################################
'########################################################################################
'########################################################################################
Function 后台族非票精分调程_WA_设置典核心宽基(典码称 As Dictionary)
    典码称.RemoveAll
'========================================================================================
'核心宽基指数
'========================================================================================
With 典码称
    '--------------------------------------------------------------
    '宽基
    '--------------------------------------------------------------
    .Add Key:="sh000001", Item:="上证指数"
'    .Add Key:="sz159601", Item:="A50ETF"
    .Add Key:="sh000016", Item:="上证50"
    .Add Key:="sz159919", Item:="沪深300ETF"
    .Add Key:="sz399905", Item:="中证500"
    .Add Key:="sh000852", Item:="中证1000"
    .Add Key:="sz159531", Item:="中证2000"
End With
'========================================================================================
End Function

Function 后台族非票精分调程_WA_设置典核心大盘(典码称 As Dictionary)
    典码称.RemoveAll
'========================================================================================
'核心宽基指数
'========================================================================================
With 典码称
    '--------------------------------------------------------------
    '宽基
    '--------------------------------------------------------------
    .Add Key:="sh000003", Item:="B股指数"    '比股票反应更早
    .Add Key:="sh510880", Item:="红利ETF"
'    .Add Key:="sh511090", Item:="国债30年ETF"
    .Add Key:="sh000139", Item:="上证转债"      '比股票反应更早
    .Add Key:="sh000001", Item:="上证指数"
    .Add Key:="sz159949", Item:="创业板50ETF"
    .Add Key:="sh588000", Item:="科创50ETF"
    .Add Key:="sz399678", Item:="深次新股"
    '--------------------------------------------------------------
    .Add Key:="sz159920", Item:="恒生ETF"
    .Add Key:="sh513330", Item:="恒生互联"
    .Add Key:="sh513050", Item:="中概互联"
    .Add Key:="sh513100", Item:="纳指ETF"
    '--------------------------------------------------------------
'    .Add Key:="sh510900", Item:="恒H股ETF"
'    .Add Key:="sh513310", Item:="中韩半导体ETF"
'    .Add Key:="sh000869", Item:="HK银行"
'    .Add Key:="sh513190", Item:="港股通金融ETF"
'    .Add Key:="sh513060", Item:="恒生医疗"
'    .Add Key:="sh513330", Item:="恒生互联"
''    .Add Key:="sh513680", Item:="恒生国企"
'    .Add Key:="sh513050", Item:="中概互联"
End With
'========================================================================================
End Function

Function 后台族非票精分调程_WA_设置典核心行业(典码称 As Dictionary)
    典码称.RemoveAll
'========================================================================================
'核心指数 - 板块轮动协同分组
'========================================================================================
With 典码称
'    '--------------------------------------------------------------
'    '宽基
'    '--------------------------------------------------------------
'    .Add Key:="sh000003", Item:="B股指数"    '比股票反应更早
'    .Add Key:="sh000001", Item:="上证指数"
'    .Add Key:="sh000139", Item:="上证转债"      '比股票反应更早
'    .Add Key:="sh511090", Item:="国债30年ETF"
''    .Add Key:="sz159601", Item:="A50ETF"
'    .Add Key:="sh000016", Item:="上证50"
'    .Add Key:="sh510300", Item:="沪深300ETF"
'    .Add Key:="sh510500", Item:="中证500ETF"
'    .Add Key:="sh000852", Item:="中证1000"
'    .Add Key:="sz159531", Item:="中证2000"
    '---------------------------------------
'    .Add Key:="sz159845", Item:="中证1000ETF"
'    .Add Key:="sz399276", Item:="创科技"
'    .Add Key:="sh588300", Item:="双创ETF"
'    .Add Key:="sz159949", Item:="创业板50ETF"
'    .Add Key:="sh588000", Item:="科创50ETF"
'    .Add Key:="sz399678", Item:="深次新股"
'    .Add Key:="sh510880", Item:="红利ETF"
'    .Add Key:="sh510270", Item:="国企ETF"
'    .Add Key:="sh510060", Item:="央企ETF"
'    .Add Key:="sh512960", Item:="央企结构调整ETF"
    '---------------------------------------
'    .Add Key:="sz399673", Item:="创业板50"
'    .Add Key:="sh000688", Item:="科创50"
'    .Add Key:="sh000016", Item:="上证50"
'    .Add Key:="sh000300", Item:="沪深300"
'    .Add Key:="sh000905", Item:="中证500"
'    .Add Key:="sh000852", Item:="中证1000"
'========================================================================================
'重点关注
'========================================================================================
    '--------------------------------------------------------------
    '制造乙：光伏·新能源·电池
    '--------------------------------------------------------------
    .Add Key:="sh516880", Item:="光伏50ETF"
    .Add Key:="sz399808", Item:="中证新能"
    .Add Key:="sz159755", Item:="电池ETF"
'    .Add Key:="sh516160", Item:="新能源ETF"
'    .Add Key:="sz399358", Item:="国证环保"
'    .Add Key:="sz159790", Item:="碳中和ETF"
    '--------------------------------------------------------------
    '制造甲：机床·机器人·高端装备·航空航天·军工
    '--------------------------------------------------------------
    .Add Key:="sz159663", Item:="机床ETF"
    .Add Key:="sz159770", Item:="机器人ETF"
'    .Add Key:="sh516800", Item:="智能制造ETF"
    .Add Key:="sh516320", Item:="高端装备ETF"
    .Add Key:="sh563380", Item:="航空航天ETF"
'    .Add Key:="sz399368", Item:="国证军工"
    .Add Key:="sh512660", Item:="军工ETF"
    '--------------------------------------------------------------
    '科技甲：人工智能·半导体·电子·通信
    '--------------------------------------------------------------
    .Add Key:="sh515980", Item:="人工智能AIETF"
    .Add Key:="sh512480", Item:="半导体ETF"
'    .Add Key:="sh512760", Item:="芯片ETF"
    .Add Key:="sh515320", Item:="电子50ETF"
'    .Add Key:="sz159997", Item:="电子ETF"
'    .Add Key:="sh562950", Item:="消费电子50ETF"
'    .Add Key:="sz159732", Item:="消费电子ETF"
'    .Add Key:="sz399360", Item:="新硬件"
'    .Add Key:="sz399389", Item:="国证通信"
    .Add Key:="sh515880", Item:="通信ETF"
'    .Add Key:="sh515050", Item:="5GETF"
    '--------------------------------------------------------------
    '科技乙：大数据·云计算·信息安全·软件·计算机
    '--------------------------------------------------------------
    .Add Key:="sh516000", Item:="数据ETF"
    .Add Key:="sh516510", Item:="云计算ETF"
    .Add Key:="sz159613", Item:="信息安全ETF"
    .Add Key:="sh515230", Item:="软件ETF"
    .Add Key:="sz159998", Item:="计算机ETF"
'    .Add Key:="sz399363", Item:="计算机"
'    .Add Key:="sh517200", Item:="互联网ETF"
'========================================================================================
'不明走势
'========================================================================================
    '--------------------------------------------------------------
    '消费三：影视·传媒·游戏
    '--------------------------------------------------------------
    .Add Key:="sh516620", Item:="影视ETF"
'    .Add Key:="sz399971", Item:="中证传媒"
    .Add Key:="sh512980", Item:="传媒ETF"
    .Add Key:="sz159869", Item:="游戏ETF"
    '--------------------------------------------------------------
    '金融甲：银行·金融
    '金融乙：证券·保险
    '--------------------------------------------------------------
'    .Add Key:="sh512880", Item:="证券ETF"
    .Add Key:="sh512070", Item:="证券保险ETF"
    .Add Key:="sz159931", Item:="金融ETF"
    .Add Key:="sh512800", Item:="银行ETF"
'========================================================================================
'旧经济
'========================================================================================
    '--------------------------------------------------------------
    '工业甲：绿色电力·煤炭·有色·油气
    '（钢铁·基建物理在此，逻辑归工业乙）
    '--------------------------------------------------------------
    .Add Key:="sh562960", Item:="绿色电力ETF"
    .Add Key:="sh515220", Item:="煤炭ETF"
'    .Add Key:="sz399438", Item:="绿色电力"
'    .Add Key:="sh561260", Item:="能源ETF"
    .Add Key:="sz399439", Item:="国证油气"
'    .Add Key:="sz159697", Item:="油气ETF"
    .Add Key:="sz399395", Item:="国证有色"
    .Add Key:="sh516780", Item:="稀土ETF"
'    .Add Key:="sz399440", Item:="国证钢铁"
    .Add Key:="sh515210", Item:="钢铁ETF"
'    .Add Key:="sz399359", Item:="国证基建"
    .Add Key:="sh516950", Item:="基建ETF"
    '--------------------------------------------------------------
    '消费二：创新药·医疗
    '--------------------------------------------------------------
'    .Add Key:="sz159647", Item:="中药ETF"
'    .Add Key:="sz159643", Item:="疫苗ETF"
    .Add Key:="sz159992", Item:="创新药ETF"
'    .Add Key:="sh512290", Item:="生物医药ETF"
'    .Add Key:="sz159929", Item:="医药ETF"
    .Add Key:="sh512170", Item:="医疗ETF"
'    .Add Key:="sh516610", Item:="医疗服务ETF"
'    .Add Key:="sz159883", Item:="医疗器械ETF"
    '--------------------------------------------------------------
    '消费一：酒·食品·旅游
    '--------------------------------------------------------------
    .Add Key:="sh512690", Item:="酒ETF"
    .Add Key:="sh515710", Item:="食品ETF"
'    .Add Key:="sz159736", Item:="饮食ETF"
'    .Add Key:="sh510150", Item:="消费ETF"
    .Add Key:="sz159766", Item:="旅游ETF"
    '--------------------------------------------------------------
    '工业乙：房地产·建材
    '--------------------------------------------------------------
'    .Add Key:="sz399983", Item:="地产等权"
'    .Add Key:="sh512200", Item:="房地产ETF"    '数据不准确
    .Add Key:="sz159768", Item:="房地产ETF"
    .Add Key:="sz159745", Item:="建材ETF"
    '--------------------------------------------------------------
    '消费四：畜牧·农业
    '--------------------------------------------------------------
    .Add Key:="sz159867", Item:="畜牧ETF"
'    .Add Key:="sz399435", Item:="国证农牧"
'    .Add Key:="sh562900", Item:="现代农业ETF"
    .Add Key:="sz159825", Item:="农业ETF"
'========================================================================================
'上升趋势
'========================================================================================
'========================================================================================
'反弹
'========================================================================================
'========================================================================================
'回落回落
'========================================================================================
'========================================================================================
'国外基金
'========================================================================================
    .Add Key:="sz159920", Item:="恒生ETF"
    .Add Key:="sh510900", Item:="恒H股ETF"
    .Add Key:="sh513100", Item:="纳指ETF"
    .Add Key:="sh513000", Item:="日经ETF"
    '.Add Key:="sh520830", Item:="沙特ETF"
    '--------------------------------------------------------------
    .Add Key:="sh513310", Item:="中韩半导体ETF"
'    .Add Key:="sh000869", Item:="HK银行"
    .Add Key:="sh513190", Item:="港股通金融ETF"
    .Add Key:="sh513060", Item:="恒生医疗"
    .Add Key:="sh520600", Item:="港股汽车"
    .Add Key:="sh513330", Item:="恒生互联"
    .Add Key:="sh513050", Item:="中概互联"
'    .Add Key:="sh513230", Item:="港股消费"
    .Add Key:="sh513360", Item:="教育ETF"
'    .Add Key:="sh513680", Item:="恒生国企"
End With
'========================================================================================
End Function








Function 后台族非票精分调程_WA_制作典基必选(典码称 As Dictionary)
With 典码称
    .Add Key:="宽基A股", Item:="分类1"
    .Add Key:="sh510210", Item:="上证指数ETF"
    .Add Key:="sh510050", Item:="上证50ETF"
    .Add Key:="sh510300", Item:="沪深300ETF"
    .Add Key:="sh510500", Item:="中证500ETF"
    .Add Key:="sz159845", Item:="中证1000ETF"
    .Add Key:="sz159781", Item:="双创50ETF"
    .Add Key:="sz159949", Item:="创业板50ETF"
    .Add Key:="sh588000", Item:="科创50ETF"
    .Add Key:="缀特殊", Item:="分类2"
    .Add Key:="sz159920", Item:="恒生ETF"
    .Add Key:="sh510900", Item:="H股ETF"
    .Add Key:="sh513050", Item:="中概互联网ETF"
    .Add Key:="sh513330", Item:="恒生互联网ETF"
    .Add Key:="sh513060", Item:="恒生医疗ETF"
    .Add Key:="sz159726", Item:="恒生红利ETF"
    .Add Key:="sh511180", Item:="上证可转债ETF"
    .Add Key:="sh510880", Item:="红利ETF"
    .Add Key:="sh511990", Item:="华宝添益ETF"
    .Add Key:="sz159985", Item:="豆粕ETF"
    .Add Key:="sh518880", Item:="黄金ETF"
    .Add Key:="sh511880", Item:="银华日利ETF"
    .Add Key:="行业文娱", Item:="分类3"
    .Add Key:="sh513360", Item:="教育ETF"
    .Add Key:="sh516620", Item:="影视ETF"
    .Add Key:="sh512980", Item:="传媒ETF"
    .Add Key:="sz159766", Item:="旅游ETF"
    .Add Key:="sz159869", Item:="游戏ETF"
    .Add Key:="sh516770", Item:="游戏动漫ETF"
    .Add Key:="行业农业", Item:="分类4"
    .Add Key:="sh562900", Item:="现代农业ETF"
    .Add Key:="sz159867", Item:="畜牧ETF"
    .Add Key:="sh516670", Item:="畜牧养殖ETF"
    .Add Key:="sz159616", Item:="农牧ETF"
    .Add Key:="sh516810", Item:="农业50ETF"
    .Add Key:="sz159825", Item:="农业ETF"
    .Add Key:="sz159865", Item:="养殖ETF"
    .Add Key:="概念碳中和", Item:="分类5"
    .Add Key:="sh561190", Item:="双碳ETF"
    .Add Key:="sz159641", Item:="双碳ETF"
    .Add Key:="sh562990", Item:="碳中和100ETF"
    .Add Key:="sh516070", Item:="碳中和50ETF"
    .Add Key:="sz159790", Item:="碳中和ETF"
    .Add Key:="sh516880", Item:="光伏50ETF"
    .Add Key:="sh515790", Item:="光伏ETF"
    .Add Key:="sh516720", Item:="ESGETF"
    .Add Key:="sh516830", Item:="300ESGETF"
    .Add Key:="sz159611", Item:="电力ETF"
    .Add Key:="sz159625", Item:="绿色电力ETF"
    .Add Key:="sh515220", Item:="煤炭ETF"
    .Add Key:="sz159930", Item:="能源ETF"
    .Add Key:="sz159731", Item:="石化ETF"
    .Add Key:="sh510410", Item:="资源ETF"
    .Add Key:="行业材料", Item:="分类6"
    .Add Key:="sh516780", Item:="稀土ETF"
    .Add Key:="sh562800", Item:="稀有金属ETF"
    .Add Key:="sh512400", Item:="有色金属ETF"
    .Add Key:="sz159881", Item:="有色60ETF"
    .Add Key:="sz159980", Item:="有色ETF"
    .Add Key:="sh515210", Item:="钢铁ETF"
    .Add Key:="sz159761", Item:="新材料50ETF"
    .Add Key:="sh516360", Item:="新材料ETF"
    .Add Key:="sh516120", Item:="化工50ETF"
    .Add Key:="sz159870", Item:="化工ETF"
    .Add Key:="概念汽车", Item:="分类7"
    .Add Key:="sh516110", Item:="汽车ETF"
    .Add Key:="sh515700", Item:="新能车ETF"
    .Add Key:="sh516160", Item:="新能源ETF"
    .Add Key:="sh515030", Item:="新能源车ETF"
    .Add Key:="sh516580", Item:="新能源主题ETF"
    .Add Key:="sz159888", Item:="智能车ETF"
    .Add Key:="sh516380", Item:="智能电动车ETF"
    .Add Key:="sh516520", Item:="智能驾驶ETF"
    .Add Key:="sh515250", Item:="智能汽车ETF"
    .Add Key:="sz159840", Item:="锂电池ETF"
    .Add Key:="sz159757", Item:="电池30ETF"
    .Add Key:="sz159796", Item:="电池50ETF"
    .Add Key:="sz159755", Item:="电池ETF"
    .Add Key:="概念制造", Item:="分类8"
    .Add Key:="sh512670", Item:="国防ETF"
    .Add Key:="sh512660", Item:="军工ETF"
    .Add Key:="sh516800", Item:="智能制造ETF"
    .Add Key:="sh516320", Item:="高端装备ETF"
    .Add Key:="sh562360", Item:="机器人50ETF"
    .Add Key:="sz159770", Item:="机器人ETF"
    .Add Key:="sz159667", Item:="工业母机ETF"
    .Add Key:="sz159886", Item:="机械ETF"
    .Add Key:="行业科技", Item:="分类9"
    .Add Key:="sh515580", Item:="科技100ETF"
    .Add Key:="sh515750", Item:="科技50ETF"
    .Add Key:="sh515000", Item:="科技ETF"
    .Add Key:="sz159807", Item:="科技ETF"
    .Add Key:="sh512720", Item:="计算机ETF"
    .Add Key:="sz159998", Item:="计算机ETF"
    .Add Key:="sh515230", Item:="软件ETF"
    .Add Key:="sh512930", Item:="AIETF"
    .Add Key:="行业信息", Item:="分类10"
    .Add Key:="sh515880", Item:="通信ETF"
    .Add Key:="sh515050", Item:="5GETF"
    .Add Key:="sz159994", Item:="5GETF"
    .Add Key:="sh517050", Item:="互联网50ETF"
    .Add Key:="sh517200", Item:="互联网ETF"
    .Add Key:="sh516510", Item:="云计算ETF"
    .Add Key:="sz159613", Item:="信息安全ETF"
    .Add Key:="sz159939", Item:="信息技术ETF"
    .Add Key:="sh516000", Item:="大数据50ETF"
    .Add Key:="sh515400", Item:="大数据ETF"
    .Add Key:="sh515070", Item:="人工智能AIETF"
    .Add Key:="sz159819", Item:="人工智能ETF"
    .Add Key:="sz159851", Item:="金融科技ETF"
    .Add Key:="sh516330", Item:="物联网ETF"
    .Add Key:="行业芯片", Item:="分类11"
    .Add Key:="sh512480", Item:="半导体ETF"
    .Add Key:="sz159813", Item:="半导体ETF"
    .Add Key:="sh512760", Item:="芯片ETF"
    .Add Key:="sz159995", Item:="芯片ETF"
    .Add Key:="sh515320", Item:="电子50ETF"
    .Add Key:="sz159997", Item:="电子ETF"
    .Add Key:="sh562950", Item:="消费电子50ETF"
    .Add Key:="sz159732", Item:="消费电子ETF"
    .Add Key:="sz159786", Item:="VRETF"
    .Add Key:="行业金融地产", Item:="分类12"
    .Add Key:="sh512800", Item:="银行ETF"
    .Add Key:="sh512880", Item:="证券ETF"
    .Add Key:="sh512000", Item:="券商ETF"
    .Add Key:="sh512070", Item:="证券保险ETF"
    .Add Key:="sh510230", Item:="金融ETF"
    .Add Key:="sz159940", Item:="金融地产ETF"
    .Add Key:="sh512200", Item:="房地产ETF"
    .Add Key:="sh516970", Item:="基建50ETF"
    .Add Key:="sh516950", Item:="基建ETF"
    .Add Key:="sz159745", Item:="建材ETF"
    .Add Key:="行业医药", Item:="分类13"
    .Add Key:="sz159837", Item:="生物科技ETF"
    .Add Key:="sz159615", Item:="生物科技ETF港股"
    .Add Key:="sh512290", Item:="生物医药ETF"
    .Add Key:="sz159859", Item:="生物医药ETF"
    .Add Key:="sh515120", Item:="创新药ETF"
    .Add Key:="sz159992", Item:="创新药ETF"
    .Add Key:="sz159647", Item:="中药ETF"
    .Add Key:="sz159847", Item:="医疗50ETF"
    .Add Key:="sh512170", Item:="医疗ETF"
    .Add Key:="sz159877", Item:="医疗产业ETF"
    .Add Key:="sh516820", Item:="医疗创新ETF"
    .Add Key:="sh516610", Item:="医疗服务ETF"
    .Add Key:="sz159883", Item:="医疗器械ETF"
    .Add Key:="sh512120", Item:="医药50ETF"
    .Add Key:="sz159929", Item:="医药ETF"
    .Add Key:="sh512010", Item:="医药ETF"
    .Add Key:="sz159938", Item:="医药卫生ETF"
    .Add Key:="sz159760", Item:="公共卫生健康ETF"
    .Add Key:="概念必要消费", Item:="分类14"
    .Add Key:="sh515710", Item:="食品ETF"
    .Add Key:="sh512690", Item:="酒ETF"
    .Add Key:="sz159736", Item:="饮食ETF"
    .Add Key:="sh515170", Item:="食品饮料ETF"
    .Add Key:="sh512600", Item:="必选消费ETF"
    .Add Key:="概念可选消费", Item:="分类15"
    .Add Key:="sh515650", Item:="消费50ETF"
    .Add Key:="sh510150", Item:="消费ETF"
    .Add Key:="sz159928", Item:="消费ETF"
    .Add Key:="sz159996", Item:="家电ETF"
    .Add Key:="sh561130", Item:="国货ETF"
    .Add Key:="sh560800", Item:="数字经济ETF"
    .Add Key:="sh515920", Item:="智能消费ETF"
    .Add Key:="sh516910", Item:="物流ETF"
    .Add Key:="sh516560", Item:="养老ETF"
    .Add Key:="宽基双创", Item:="分类16"
    .Add Key:="sz159783", Item:="双创基金ETF"
    .Add Key:="sh588050", Item:="科创ETF"
    .Add Key:="sh588080", Item:="科创板50ETF"
    .Add Key:="sh588090", Item:="科创板ETF"
    .Add Key:="sh588360", Item:="科创创业ETF"
    .Add Key:="sh588260", Item:="科创信息ETF"
    .Add Key:="宽基港股", Item:="分类17"
    .Add Key:="sh513660", Item:="恒生ETF"
    .Add Key:="sh513690", Item:="恒生高股息ETF"
    .Add Key:="sz159850", Item:="恒生国企ETF"
    .Add Key:="sh513320", Item:="恒生新经济ETF"
    .Add Key:="sz159892", Item:="恒生医药ETF"
    .Add Key:="sh513600", Item:="恒生指数ETF"
    .Add Key:="sz159960", Item:="H股ETF港股通"
    .Add Key:="sh513280", Item:="港股生物科技ETF"
    .Add Key:="sh513070", Item:="港股消费50ETF"
    .Add Key:="sh513090", Item:="香港证券ETF"
    .Add Key:="sh517300", Item:="沪港深300ETF"
    .Add Key:="sh513550", Item:="港股通50ETF"
    .Add Key:="sh513990", Item:="港股通ETF"
    .Add Key:="sz159792", Item:="港股通互联网ETF"
    .Add Key:="sh513960", Item:="港股通消费ETF"
    .Add Key:="sz159776", Item:="港股通医药ETF"
    .Add Key:="境外中国科技", Item:="分类18"
    .Add Key:="sz159605", Item:="中概互联ETF"
    .Add Key:="sh513010", Item:="恒生科技30ETF"
    .Add Key:="sh513130", Item:="恒生科技ETF"
    .Add Key:="sh513180", Item:="恒生科技指数ETF"
    .Add Key:="sh513770", Item:="港股互联网ETF"
    .Add Key:="sh513980", Item:="港股科技50ETF"
    .Add Key:="sh513020", Item:="港股科技ETF"
    .Add Key:="sz159636", Item:="港股通科技30ETF"
    .Add Key:="sh513860", Item:="港股通科技ETF"
    .Add Key:="sh513210", Item:="恒易方达f"
    .Add Key:="sz159557", Item:="恒医疗指数f"
    .Add Key:="sz159303", Item:="恒医疗基金f"
    .Add Key:="sz159506", Item:="恒医疗f"
    .Add Key:="sh513170", Item:="恒央企f"
    .Add Key:="sh513970", Item:="恒消费f"
    .Add Key:="sz159699", Item:="恒消费f"
    .Add Key:="sz159742", Item:="恒科技指数f"
    .Add Key:="sh513380", Item:="恒科技龙头f"
    .Add Key:="sh513260", Item:="恒科技基金f"
    .Add Key:="sh513890", Item:="恒科技HKf"
    .Add Key:="sz159740", Item:="恒科技f"
    .Add Key:="sz159688", Item:="恒互联网f"
    .Add Key:="sz159545", Item:="恒红利低波f"
    .Add Key:="sh513950", Item:="恒红利f"
    .Add Key:="sh520520", Item:="恒港股消费f"
    .Add Key:="sz159318", Item:="恒港股通f"
    .Add Key:="sz159718", Item:="港股医药f"
    .Add Key:="sh513910", Item:="港股央企红利f"
    .Add Key:="sz159333", Item:="港股央企红利f"
    .Add Key:="sh520990", Item:="港股央企红利50f"
    .Add Key:="sh513230", Item:="港股消费f"
    .Add Key:="sz159735", Item:="港股消费f"
    .Add Key:="sh513200", Item:="港股通医药f"
    .Add Key:="sh520660", Item:="港股通央企红利南方f"
    .Add Key:="sh513920", Item:="港股通央企红利f"
    .Add Key:="sh513150", Item:="港股通科技50f"
    .Add Key:="sh513190", Item:="港股通金融f"
    .Add Key:="sh513040", Item:="港股通互联网f"
    .Add Key:="sh520890", Item:="港股通红利低波f"
    .Add Key:="sh513530", Item:="港股通红利f"
    .Add Key:="sz159570", Item:="港股通创新药f"
    .Add Key:="sz159711", Item:="港股通f"
    .Add Key:="sz159712", Item:="港股通50f"
    .Add Key:="sh513900", Item:="港股通100f"
    .Add Key:="sz159788", Item:="港股通100f"
    .Add Key:="sz159751", Item:="港股科技f"
    .Add Key:="sh513160", Item:="港股科技30f"
    .Add Key:="sh513140", Item:="港股金融f"
    .Add Key:="sz159568", Item:="港股互联网f"
    .Add Key:="sh513630", Item:="港股红利指数f"
    .Add Key:="sh513820", Item:="港股红利基金f"
    .Add Key:="sz159569", Item:="港股红利低波f"
    .Add Key:="sz159691", Item:="港股红利f"
    .Add Key:="sh513810", Item:="港股国企f"
    .Add Key:="sz159519", Item:="港股国企f"
    .Add Key:="sz159302", Item:="港股高股息f"
    .Add Key:="sh513750", Item:="港股非银f"
    .Add Key:="sh520700", Item:="港股创新药基金f"
    .Add Key:="sh513120", Item:="港股创新药f"
    .Add Key:="sz159567", Item:="港股创新药f"
    .Add Key:="sh513780", Item:="港股创新药50f"
    .Add Key:="境外指数", Item:="分类19"
    .Add Key:="sh513500", Item:="标普500ETF"
    .Add Key:="sz159941", Item:="纳指ETF"
    .Add Key:="sh513300", Item:="纳斯达克ETF"
    .Add Key:="sh513520", Item:="日经ETF"
    .Add Key:="sh513880", Item:="日经225ETF"
    .Add Key:="sh513030", Item:="德国ETF"
    .Add Key:="sh513080", Item:="法国CAC40ETF"
    .Add Key:="sz159601", Item:="A50ETF"
    .Add Key:="sh563000", Item:="中国A50ETF"
    .Add Key:="sz159696", Item:="纳指易方达f"
    .Add Key:="sh513290", Item:="纳指生物科技f"
    .Add Key:="sz159509", Item:="纳指科技f"
    .Add Key:="sh513870", Item:="纳指富国f"
    .Add Key:="sh513100", Item:="纳指f"
    .Add Key:="sh513390", Item:="纳指100f"
    .Add Key:="sz159660", Item:="纳指100f"
    .Add Key:="sz159501", Item:="纳斯达克指数f"
    .Add Key:="sz159632", Item:="纳斯达克f"
    .Add Key:="sz159513", Item:="纳斯达克100指数f"
    .Add Key:="sh513110", Item:="纳斯达克100f"
    .Add Key:="sz159659", Item:="纳斯达克100f"
    .Add Key:="sh513850", Item:="美国50f"
    .Add Key:="sz159577", Item:="美国50f"
    .Add Key:="sh513730", Item:="东南亚科技f"
    .Add Key:="sz159561", Item:="德国f"
    .Add Key:="sh513400", Item:="道琼斯f"
    .Add Key:="sh513350", Item:="标普油气f"
'    .Add Key:="sz159518", Item:="标普油气f"
    .Add Key:="sz159529", Item:="标普消费f"
    .Add Key:="sz159502", Item:="标普生物科技f"
    .Add Key:="sh562060", Item:="标普红利f"
    .Add Key:="sz159655", Item:="标普f"
    .Add Key:="sh513650", Item:="标普500基金f"
    .Add Key:="sz159612", Item:="标普500f"
End With
End Function


Function 后台族非票精分调程_WA_制作典基可选(典码称 As Dictionary)
With 典码称
    .Add Key:="标志可选部分", Item:="分类20"
    .Add Key:="缀龙头", Item:="分类21"
    .Add Key:="sh510190", Item:="上证龙头ETF"
    .Add Key:="sh512580", Item:="碳中和龙头ETF"
    .Add Key:="sh512710", Item:="军工龙头ETF"
    .Add Key:="sh515280", Item:="银行龙头ETF"
    .Add Key:="sh515850", Item:="证券龙头ETF"
    .Add Key:="sh515950", Item:="医药龙头ETF"
    .Add Key:="sh516050", Item:="科技龙头ETF"
    .Add Key:="sh516130", Item:="消费龙头ETF"
    .Add Key:="sh516220", Item:="化工龙头ETF"
    .Add Key:="sh516640", Item:="芯片龙头ETF"
    .Add Key:="sh561100", Item:="消费电子龙头ETF"
    .Add Key:="sh588060", Item:="科创50ETF龙头"
    .Add Key:="sh588150", Item:="科创龙头ETF"
    .Add Key:="sh588330", Item:="双创龙头ETF"
    .Add Key:="sz159603", Item:="双创龙头ETF"
    .Add Key:="sz159609", Item:="光伏龙头ETF"
    .Add Key:="sz159640", Item:="碳中和龙头ETF"
    .Add Key:="sz159721", Item:="深创龙头ETF"
    .Add Key:="sz159723", Item:="科技龙头ETF"
    .Add Key:="sz159730", Item:="龙头家电ETF"
    .Add Key:="sz159752", Item:="新能源龙头ETF"
    .Add Key:="sz159767", Item:="电池龙头ETF"
    .Add Key:="sz159769", Item:="消费电子龙头ETF"
    .Add Key:="sz159801", Item:="芯片龙头ETF"
    .Add Key:="sz159856", Item:="互联网龙头ETF"
    .Add Key:="sz159876", Item:="有色龙头ETF"
    .Add Key:="sz159896", Item:="物联网龙头ETF"
    .Add Key:="sz159906", Item:="深成长龙头ETF"
    .Add Key:="sz159993", Item:="龙头券商ETF"
    .Add Key:="缀基金", Item:="分类22"
    .Add Key:="sh510090", Item:="ESGETF基金"
    .Add Key:="sh510330", Item:="300ETF基金"
    .Add Key:="sh510360", Item:="沪深300ETF基金"
    .Add Key:="sh510510", Item:="中证500ETF基金"
    .Add Key:="sh510680", Item:="上证50ETF基金"
    .Add Key:="sh510800", Item:="50ETF基金"
    .Add Key:="sh512500", Item:="500ETF基金"
    .Add Key:="sh512550", Item:="A50ETF基金"
    .Add Key:="sh512610", Item:="医药卫生ETF基金"
    .Add Key:="sh512640", Item:="金融地产ETF基金"
    .Add Key:="sh512680", Item:="军工ETF基金"
    .Add Key:="sh512700", Item:="银行ETF基金"
    .Add Key:="sh512900", Item:="证券ETF基金"
    .Add Key:="sh513580", Item:="恒生科技ETF基金"
    .Add Key:="sh515010", Item:="券商ETF基金"
    .Add Key:="sh515060", Item:="房地产ETF基金"
    .Add Key:="sh515300", Item:="红利低波ETF基金"
    .Add Key:="sh515860", Item:="科技ETF基金"
    .Add Key:="sh516150", Item:="稀土ETF基金"
    .Add Key:="sh516290", Item:="光伏ETF基金"
    .Add Key:="sh516480", Item:="新材料ETF基金"
    .Add Key:="sh516680", Item:="有色ETF基金"
    .Add Key:="sh516920", Item:="芯片ETF基金"
    .Add Key:="sh516930", Item:="生物科技ETF基金"
    .Add Key:="sh517030", Item:="沪港深300ETF基金"
    .Add Key:="sh517080", Item:="沪港深500ETF基金"
    .Add Key:="sh518660", Item:="黄金ETF基金"
    .Add Key:="sh560110", Item:="中证1000ETF基金"
    .Add Key:="sh560880", Item:="家电ETF基金"
    .Add Key:="sh561700", Item:="电力ETF基金"
    .Add Key:="sh561800", Item:="稀有金属ETF基金"
    .Add Key:="sh562300", Item:="碳中和ETF基金"
    .Add Key:="sh562880", Item:="电池ETF基金"
    .Add Key:="sh588180", Item:="科创50ETF基金"
    .Add Key:="sh588310", Item:="双创ETF基金"
    .Add Key:="sz159741", Item:="恒生科技ETF基金"
    .Add Key:="sz159763", Item:="新材料ETF基金"
    .Add Key:="sz159777", Item:="创科技ETF基金"
    .Add Key:="sz159779", Item:="消费电子ETF基金"
    .Add Key:="sz159782", Item:="双创50ETF基金"
    .Add Key:="sz159795", Item:="智能车ETF基金"
    .Add Key:="sz159797", Item:="医疗器械ETF基金"
    .Add Key:="sz159823", Item:="H股ETF基金"
    .Add Key:="sz159831", Item:="上海金ETF基金"
    .Add Key:="sz159838", Item:="医药ETF基金"
    .Add Key:="sz159848", Item:="证券ETF基金"
    .Add Key:="sz159863", Item:="光伏ETF基金"
    .Add Key:="sz159880", Item:="有色ETF基金"
    .Add Key:="sz159885", Item:="碳中和ETF基金"
    .Add Key:="sz159891", Item:="医疗ETF基金"
    .Add Key:="sz159945", Item:="能源ETF基金"
    .Add Key:="缀MSCI", Item:="分类23"
    .Add Key:="sh512160", Item:="MSCI中国A股ETF"
    .Add Key:="sh512180", Item:="MSCIA股ETF基金"
    .Add Key:="sh512280", Item:="景顺MSCIA股ETF"
    .Add Key:="sh512320", Item:="工银MSCI中国ETF"
    .Add Key:="sh512360", Item:="平安MSCI国际ETF"
    .Add Key:="sh512380", Item:="MSCI中国ETF"
    .Add Key:="sh512390", Item:="平安MSCI低波ETF"
    .Add Key:="sh512520", Item:="MSCIETF"
    .Add Key:="sh512920", Item:="MSCIETF新华"
    .Add Key:="sh512990", Item:="MSCIA股ETF"
    .Add Key:="sh515160", Item:="MSCI中国ETF招商"
    .Add Key:="sh515520", Item:="MSCI价值100ETF"
    .Add Key:="sh515770", Item:="上投摩根MSCIAETF"
    .Add Key:="sh515780", Item:="浦银MSCI中国ETF"
    .Add Key:="sh560050", Item:="MSCI中国A50ETF"
    .Add Key:="缀货币", Item:="分类24"
    .Add Key:="sh511360", Item:="短融ETF"
    .Add Key:="sh511850", Item:="财富宝ETF"
    .Add Key:="sh511660", Item:="货币ETF建信添益"
    .Add Key:="sz159001", Item:="货币ETF"
    .Add Key:="sh511900", Item:="富国货币ETF"
    .Add Key:="sh511810", Item:="理财金货币ETF"
    .Add Key:="sh511690", Item:="交易货币ETF"
    .Add Key:="sz159005", Item:="汇添富快钱ETF"
    .Add Key:="sh511700", Item:="场内货币ETF"
    .Add Key:="sh511600", Item:="货币ETF"
    .Add Key:="sh511620", Item:="货币基金ETF"
    .Add Key:="sh511770", Item:="金鹰增益货币ETF"
    .Add Key:="sh511830", Item:="华泰货币ETF"
    .Add Key:="sh511860", Item:="保证金货币ETF"
    .Add Key:="sh511910", Item:="融通货币ETF"
    .Add Key:="sh511920", Item:="广发货币ETF"
    .Add Key:="sh511930", Item:="中融日盈货币ETF"
    .Add Key:="sh511950", Item:="添利货币ETF"
    .Add Key:="sh511970", Item:="国寿货币ETF"
    .Add Key:="缀黄金", Item:="分类25"
    .Add Key:="sz159937", Item:="黄金ETF基金"
    .Add Key:="sh518800", Item:="黄金基金ETF"
    .Add Key:="sz159934", Item:="黄金ETF"
    .Add Key:="sh518850", Item:="黄金ETF9999"
    .Add Key:="sh518860", Item:="黄金ETFAU"
    .Add Key:="sz159812", Item:="黄金基金ETF"
    .Add Key:="缀债", Item:="分类26"
    .Add Key:="sh511010", Item:="国债ETF"
    .Add Key:="sh511020", Item:="活跃国债ETF"
    .Add Key:="sh511060", Item:="5年地方债ETF"
    .Add Key:="sh511220", Item:="城投债ETF"
    .Add Key:="sh511260", Item:="十年国债ETF"
    .Add Key:="sh511270", Item:="10年地方债ETF"
    .Add Key:="sh511380", Item:="可转债ETF"
    .Add Key:="sh511030", Item:="公司债ETF"
    .Add Key:="sz159816", Item:="0-4地债ETF"
    .Add Key:="sz159972", Item:="5年地债ETF"
    .Add Key:="sh511310", Item:="10年国债ETF"
    .Add Key:="缀基金公司", Item:="分类27"
    .Add Key:="sh510100", Item:="上证50ETF易方达"
    .Add Key:="sh510310", Item:="沪深300ETF易方达"
    .Add Key:="sh510580", Item:="中证500ETF易方达"
    .Add Key:="sh511800", Item:="易方达货币ETF"
    .Add Key:="sh512090", Item:="MSCIA股ETF易方达"
    .Add Key:="sh512560", Item:="军工ETF易方达"
    .Add Key:="sh512570", Item:="证券ETF易方达"
    .Add Key:="sh513000", Item:="日经225ETF易方达"
    .Add Key:="sh515180", Item:="红利ETF易方达"
    .Add Key:="sh516080", Item:="创新药ETF易方达"
    .Add Key:="sh516090", Item:="新能源ETF易方达"
    .Add Key:="sh516310", Item:="银行ETF易方达"
    .Add Key:="sz159715", Item:="稀土ETF易方达"
    .Add Key:="sz159787", Item:="建材ETF易方达"
    .Add Key:="sz159901", Item:="深证100ETF易方达"
    .Add Key:="sz159915", Item:="创业板ETF易方达"
    .Add Key:="sh515290", Item:="银行ETF天弘"
    .Add Key:="sh515330", Item:="300ETF天弘"
    .Add Key:="sz159820", Item:="中证500ETF天弘"
    .Add Key:="sz159977", Item:="创业板ETF天弘"
    .Add Key:="sz159639", Item:="碳中和ETF南方"
    .Add Key:="sz159925", Item:="沪深300ETF南方"
    .Add Key:="sz159948", Item:="创业板ETF南方"
    .Add Key:="sh510390", Item:="平安沪深300ETF"
    .Add Key:="sh510590", Item:="平安中证500ETF"
    .Add Key:="sh516180", Item:="光伏ETF平安"
    .Add Key:="sh516890", Item:="新材料ETF平安"
    .Add Key:="sz159793", Item:="线上消费ETF平安"
    .Add Key:="sz159832", Item:="平安金ETF"
    .Add Key:="sz159964", Item:="平安创业板ETF"
    .Add Key:="sz159922", Item:="中证500ETF嘉实"
    .Add Key:="sh512100", Item:="中证1000ETF"
    .Add Key:="sz159633", Item:="中证1000指数ETF"
    .Add Key:="sh560010", Item:="中证1000ETF指数"
    .Add Key:="sh515380", Item:="泰康沪深300ETF"
    .Add Key:="sh510350", Item:="工银沪深300ETF"
    .Add Key:="sh515660", Item:="国联安沪深300ETF"
    .Add Key:="sz159952", Item:="创业板ETF广发"
    .Add Key:="sh515680", Item:="嘉实央企创新ETF"
    .Add Key:="sh510380", Item:="国寿300ETF"
    .Add Key:="sz159908", Item:="创业板ETF博时"
    .Add Key:="sh560550", Item:="碳中和ETF环交所"
    .Add Key:="sz159961", Item:="深100ETF方正富邦"
    .Add Key:="sz159968", Item:="中证500ETF博时"
    .Add Key:="sh561550", Item:="500增强ETF"
    .Add Key:="sh561300", Item:="300增强ETF"
    .Add Key:="sh515020", Item:="银行ETF华夏"
    .Add Key:="sz159610", Item:="500ETF增强"
    .Add Key:="sz159629", Item:="1000ETF"
End With
End Function


Function 后台族非票精分调程_WA_制作典指必选(典码称 As Dictionary)
With 典码称
    .Add Key:="宽基指数", Item:="分类1"
    .Add Key:="sh000001", Item:="上证指数"
    .Add Key:="sh000003", Item:="Ｂ股指数"
    .Add Key:="sh000159", Item:="沪股通"
    .Add Key:="sh000016", Item:="上证50"
    .Add Key:="sh000300", Item:="沪深300"
    .Add Key:="sh000905", Item:="中证500"
    .Add Key:="sh000852", Item:="中证1000"
    .Add Key:="sz399673", Item:="创业板50"
    .Add Key:="sh000688", Item:="科创50"
    .Add Key:="指数股指", Item:="分类2"
    .Add Key:="sz399914", Item:="300 金融"
    .Add Key:="sz399913", Item:="300 医药"
    .Add Key:="sh000849", Item:="300非银"
    .Add Key:="sz399657", Item:="300绩效"
    .Add Key:="sh000914", Item:="300金融"
    .Add Key:="sz399972", Item:="300深市"
    .Add Key:="sh000913", Item:="300医药"
    .Add Key:="sh000982", Item:="500等权"
    .Add Key:="sz399982", Item:="500等权"
    .Add Key:="sh000856", Item:="500工业"
    .Add Key:="sh000802", Item:="500沪市"
    .Add Key:="sz399802", Item:="500深市"
    .Add Key:="sh000858", Item:="500信息"
    .Add Key:="sh000857", Item:="500医药"
    .Add Key:="sh000854", Item:="500原料"
    .Add Key:="sz399382", Item:="1000材料"
    .Add Key:="sz399630", Item:="1000成长"
    .Add Key:="sz399367", Item:="1000地产"
    .Add Key:="sz399383", Item:="1000工业"
    .Add Key:="sz399390", Item:="1000公用"
    .Add Key:="sz399631", Item:="1000价值"
    .Add Key:="sz399387", Item:="1000金融"
    .Add Key:="sz399384", Item:="1000可选"
    .Add Key:="sz399381", Item:="1000能源"
    .Add Key:="sz399385", Item:="1000消费"
    .Add Key:="sz399388", Item:="1000信息"
    .Add Key:="sz399386", Item:="1000医药"
    .Add Key:="指数等权", Item:="分类3"
    .Add Key:="sh000070", Item:="能源等权"
    .Add Key:="sh000071", Item:="材料等权"
    .Add Key:="sh000072", Item:="工业等权"
    .Add Key:="sh000073", Item:="可选等权"
    .Add Key:="sh000074", Item:="消费等权"
    .Add Key:="sh000075", Item:="医药等权"
    .Add Key:="sh000076", Item:="金融等权"
    .Add Key:="sh000077", Item:="信息等权"
    .Add Key:="sh000078", Item:="电信等权"
    .Add Key:="sh000079", Item:="公用等权"
    .Add Key:="sz399983", Item:="地产等权"
    .Add Key:="sz399990", Item:="煤炭等权"
    .Add Key:="指数申万", Item:="分类4"
    .Add Key:="sz399231", Item:="农林指数"
    .Add Key:="sz399232", Item:="采矿指数"
    .Add Key:="sz399233", Item:="制造指数"
    .Add Key:="sz399234", Item:="水电指数"
    .Add Key:="sz399235", Item:="建筑指数"
    .Add Key:="sz399236", Item:="批零指数"
    .Add Key:="sz399237", Item:="运输指数"
    .Add Key:="sz399238", Item:="餐饮指数"
    .Add Key:="sz399239", Item:="IT指数"
    .Add Key:="sz399240", Item:="金融指数"
    .Add Key:="sz399241", Item:="地产指数"
    .Add Key:="sz399242", Item:="商务指数"
    .Add Key:="sz399243", Item:="科研指数"
    .Add Key:="sz399244", Item:="公共指数"
    .Add Key:="sz399248", Item:="文化指数"
    .Add Key:="sz399249", Item:="综企指数"
    .Add Key:="sz399398", Item:="绩效指数"
    .Add Key:="sz399901", Item:="小康指数"
    .Add Key:="sz399959", Item:="军工指数"
    .Add Key:="sz399354", Item:="分析师指数"
    .Add Key:="行业国证", Item:="分类5"
    .Add Key:="sz399420", Item:="国证保证"
    .Add Key:="sz399434", Item:="国证传媒"
    .Add Key:="sz399393", Item:="国证地产"
    .Add Key:="sz399320", Item:="国证服务"
    .Add Key:="sz399440", Item:="国证钢铁"
    .Add Key:="sz399419", Item:="国证高铁"
    .Add Key:="sz399418", Item:="国证国安"
    .Add Key:="sz399358", Item:="国证环保"
    .Add Key:="sz399359", Item:="国证基建"
    .Add Key:="sz399433", Item:="国证交运"
    .Add Key:="sz399368", Item:="国证军工"
    .Add Key:="sz399365", Item:="国证粮食"
    .Add Key:="sz399435", Item:="国证农牧"
    .Add Key:="sz399396", Item:="国证食品"
    .Add Key:="sz399389", Item:="国证通信"
    .Add Key:="sz399397", Item:="国证文化"
    .Add Key:="sz399353", Item:="国证物流"
    .Add Key:="sz399412", Item:="国证新能"
    .Add Key:="sz399392", Item:="国证新兴"
    .Add Key:="sz399394", Item:="国证医药"
    .Add Key:="sz399431", Item:="国证银行"
    .Add Key:="sz399439", Item:="国证油气"
    .Add Key:="sz399395", Item:="国证有色"
    .Add Key:="行业中证", Item:="分类6"
    .Add Key:="sz399997", Item:="中证白酒"
    .Add Key:="sz399971", Item:="中证传媒"
    .Add Key:="sz399813", Item:="中证国安"
    .Add Key:="sz399973", Item:="中证国防"
    .Add Key:="sh000827", Item:="中证环保"
    .Add Key:="sz399934", Item:="中证金融"
    .Add Key:="sz399987", Item:="中证酒"
    .Add Key:="sz399967", Item:="中证军工"
    .Add Key:="sz399998", Item:="中证煤炭"
    .Add Key:="sz399928", Item:="中证能源"
    .Add Key:="sz399804", Item:="中证体育"
    .Add Key:="sz399932", Item:="中证消费"
    .Add Key:="sz399808", Item:="中证新能"
    .Add Key:="sz399935", Item:="中证信息"
    .Add Key:="sz399989", Item:="中证医疗"
    .Add Key:="sz399933", Item:="中证医药"
    .Add Key:="sz399986", Item:="中证银行"
    .Add Key:="指数概念", Item:="分类7"
    .Add Key:="sz399417", Item:="新能源车"
    .Add Key:="sz399427", Item:="专利领先"
    .Add Key:="sz399429", Item:="新丝路"
    .Add Key:="sz399432", Item:="智能汽车"
    .Add Key:="sz399436", Item:="绿色煤炭"
    .Add Key:="sz399437", Item:="证券龙头"
    .Add Key:="sz399438", Item:="绿色电力"
    .Add Key:="sz399441", Item:="生物医药"
    .Add Key:="sz399693", Item:="安防产业"
    .Add Key:="sz399698", Item:="优势成长"
    .Add Key:="sz399699", Item:="金融科技"
    .Add Key:="sz399803", Item:="工业4.0"
    .Add Key:="sz399805", Item:="互联金融"
    .Add Key:="sz399806", Item:="环境治理"
    .Add Key:="sz399807", Item:="高铁产业"
    .Add Key:="sz399809", Item:="保险主题"
    .Add Key:="sz399812", Item:="养老产业"
    .Add Key:="sz399814", Item:="大农业"
    .Add Key:="sz399970", Item:="移动互联"
    .Add Key:="sz399974", Item:="国企改革"
    .Add Key:="sz399975", Item:="证券公司"
    .Add Key:="sz399991", Item:="一带一路"
    .Add Key:="sz399994", Item:="信息安全"
    .Add Key:="sz399995", Item:="基建工程"
    .Add Key:="sz399996", Item:="智能家居"
    .Add Key:="sz399360", Item:="新硬件"
    .Add Key:="sz399361", Item:="在线消费"
    .Add Key:="sz399363", Item:="云科技"
    .Add Key:="sz399366", Item:="能源金属"
    .Add Key:="sz399277", Item:="公共健康"
    .Add Key:="sz399292", Item:="民企发展"
    .Add Key:="sz399319", Item:="资源优势"
    .Add Key:="sz399391", Item:="投资时钟"
    .Add Key:="sh000097", Item:="高端装备"
    .Add Key:="sh000819", Item:="有色金属"
    .Add Key:="sh000102", Item:="沪投资品"
    .Add Key:="sh000103", Item:="沪消费品"
    .Add Key:="sh000114", Item:="持续产业"
    .Add Key:="sh000121", Item:="医药主题"
    .Add Key:="sh000122", Item:="农业主题"
    .Add Key:="系列50", Item:="分类8"
    .Add Key:="sz399284", Item:="AI 50"
    .Add Key:="sz399610", Item:="TMT50"
    .Add Key:="sz399282", Item:="大数据50"
    .Add Key:="sz399283", Item:="机器人50"
    .Add Key:="sz399286", Item:="区块链50"
    .Add Key:="sz399281", Item:="电子50"
    .Add Key:="sz399280", Item:="生物50"
    .Add Key:="sh000126", Item:="消费50"
    .Add Key:="sz399285", Item:="物联网50"
    .Add Key:="sz399279", Item:="云科技50"
    .Add Key:="sh000092", Item:="资源50"
    .Add Key:="sz399030", Item:="碳科技30"
    .Add Key:="sz399060", Item:="碳科技60"
    .Add Key:="sz399364", Item:="消费100"
    .Add Key:="sz399403", Item:="防御100"
    .Add Key:="sz399411", Item:="红利100"
    .Add Key:="sz399608", Item:="科技100"
    .Add Key:="sz399362", Item:="民企100"
    .Add Key:="sz399297", Item:="新浪100"
    .Add Key:="sz399278", Item:="长江100"
    .Add Key:="sz399402", Item:="周期100"
    .Add Key:="sh000851", Item:="百发100"
    .Add Key:="行业上证", Item:="分类9"
    .Add Key:="sh000033", Item:="上证材料"
    .Add Key:="sh000040", Item:="上证电信"
    .Add Key:="sh000034", Item:="上证工业"
    .Add Key:="sh000041", Item:="上证公用"
    .Add Key:="sh000158", Item:="上证环保"
    .Add Key:="sh000038", Item:="上证金融"
    .Add Key:="sh000035", Item:="上证可选"
    .Add Key:="sh000090", Item:="上证流通"
    .Add Key:="sh000049", Item:="上证民企"
    .Add Key:="sh000032", Item:="上证能源"
    .Add Key:="sh000066", Item:="上证商品"
    .Add Key:="sh000036", Item:="上证消费"
    .Add Key:="sh000067", Item:="上证新兴"
    .Add Key:="sh000039", Item:="上证信息"
    .Add Key:="sh000037", Item:="上证医药"
    .Add Key:="sh000134", Item:="上证银行"
    .Add Key:="sh000063", Item:="上证周期"
    .Add Key:="sh000068", Item:="上证资源"
    .Add Key:="行业深证", Item:="分类10"
    .Add Key:="sz399614", Item:="深证材料"
    .Add Key:="sz399637", Item:="深证地产"
    .Add Key:="sz399621", Item:="深证电信"
    .Add Key:="sz399615", Item:="深证工业"
    .Add Key:="sz399622", Item:="深证公用"
    .Add Key:="sz399638", Item:="深证环保"
    .Add Key:="sz399695", Item:="深证节能"
    .Add Key:="sz399619", Item:="深证金融"
    .Add Key:="sz399616", Item:="深证可选"
    .Add Key:="sz399613", Item:="深证能源"
    .Add Key:="sz399669", Item:="深证农业"
    .Add Key:="sz399654", Item:="深证文化"
    .Add Key:="sz399617", Item:="深证消费"
    .Add Key:="sz399641", Item:="深证新兴"
    .Add Key:="sz399620", Item:="深证信息"
    .Add Key:="sz399618", Item:="深证医药"
    .Add Key:="sz399636", Item:="深证装备"
End With
End Function


Function 后台族非票精分调程_WA_制作典指可选(典码称 As Dictionary)
With 典码称
    .Add Key:="标志可选部分", Item:="分类11"
    .Add Key:="指数双创", Item:="分类12"
    .Add Key:="sz399012", Item:="创业300"
    .Add Key:="sz399635", Item:="创业板EW"
    .Add Key:="sz399667", Item:="创业板G"
    .Add Key:="sz399606", Item:="创业板R"
    .Add Key:="sz399668", Item:="创业板V"
    .Add Key:="sz399006", Item:="创业板指"
    .Add Key:="sz399102", Item:="创业板综"
    .Add Key:="sz399018", Item:="创业创新"
    .Add Key:="sz399293", Item:="创业大盘"
    .Add Key:="sz399692", Item:="创业低波"
    .Add Key:="sz399694", Item:="创业高贝"
    .Add Key:="sz399640", Item:="创业基础"
    .Add Key:="sz399295", Item:="创业蓝筹"
    .Add Key:="sz399643", Item:="创业新兴"
    .Add Key:="sz399691", Item:="创业专利"
    .Add Key:="sh000689", Item:="科创材料"
    .Add Key:="sh000687", Item:="科创高装"
    .Add Key:="sh000683", Item:="科创生物"
    .Add Key:="sh000682", Item:="科创信息"
    .Add Key:="sz399296", Item:="创成长"
    .Add Key:="sz399291", Item:="创精选88"
    .Add Key:="sz399276", Item:="创科技"
    .Add Key:="sz399351", Item:="创新示范"
    .Add Key:="sz399050", Item:="创新引擎"
    .Add Key:="sz399275", Item:="创医药"
    .Add Key:="sz399269", Item:="创质量"
    .Add Key:="sz399612", Item:="中创100"
    .Add Key:="sz399611", Item:="中创100R"
    .Add Key:="sz399624", Item:="中创400"
    .Add Key:="sz399625", Item:="中创500"
    .Add Key:="sz399660", Item:="中创EW"
    .Add Key:="sz399626", Item:="中创成长"
    .Add Key:="sz399665", Item:="中创低波"
    .Add Key:="sz399666", Item:="中创高贝"
    .Add Key:="sz399652", Item:="中创高新"
    .Add Key:="sz399627", Item:="中创价值"
    .Add Key:="指数深圳", Item:="分类13"
    .Add Key:="sz399632", Item:="深100EW"
    .Add Key:="sz399633", Item:="深300EW"
    .Add Key:="sz399674", Item:="深A医药"
    .Add Key:="sz399659", Item:="深成指EW"
    .Add Key:="sz399002", Item:="深成指R"
    .Add Key:="sz399088", Item:="深创100"
    .Add Key:="sz399678", Item:="深次新股"
    .Add Key:="sz399671", Item:="深防御50"
    .Add Key:="sz399672", Item:="深红利50"
    .Add Key:="sz399677", Item:="深互联EW"
    .Add Key:="sz399675", Item:="深互联网"
    .Add Key:="sz399352", Item:="深企综指"
    .Add Key:="sz399013", Item:="深市精选"
    .Add Key:="sz399646", Item:="深消费50"
    .Add Key:="sz399274", Item:="深新基建"
    .Add Key:="sz399647", Item:="深医药50"
    .Add Key:="sz399676", Item:="深医药EW"
    .Add Key:="sz399670", Item:="深周期50"
    .Add Key:="sz399290", Item:="深转交债"
    .Add Key:="sz399680", Item:="深成能源"
    .Add Key:="sz399681", Item:="深成材料"
    .Add Key:="sz399682", Item:="深成工业"
    .Add Key:="sz399683", Item:="深成可选"
    .Add Key:="sz399684", Item:="深成消费"
    .Add Key:="sz399685", Item:="深成医药"
    .Add Key:="sz399686", Item:="深成金融"
    .Add Key:="sz399687", Item:="深成信息"
    .Add Key:="sz399688", Item:="深成电信"
    .Add Key:="sz399689", Item:="深成公用"
    .Add Key:="sz399335", Item:="深证央企"
    .Add Key:="sz399337", Item:="深证民营"
    .Add Key:="sz399339", Item:="深证科技"
    .Add Key:="sz399341", Item:="深证责任"
    .Add Key:="sz399344", Item:="深证300R"
    .Add Key:="sz399346", Item:="深证成长"
    .Add Key:="sz399348", Item:="深证价值"
    .Add Key:="指数180", Item:="分类14"
    .Add Key:="sh000030", Item:="180R成长"
    .Add Key:="sh000031", Item:="180R价值"
    .Add Key:="sh000129", Item:="180波动"
    .Add Key:="sh000028", Item:="180成长"
    .Add Key:="sh000051", Item:="180等权"
    .Add Key:="sh000136", Item:="180低贝"
    .Add Key:="sh000123", Item:="180动态"
    .Add Key:="sh000093", Item:="180分层"
    .Add Key:="sh000135", Item:="180高贝"
    .Add Key:="sh000149", Item:="180红利"
    .Add Key:="sh000053", Item:="180基本"
    .Add Key:="sh000025", Item:="180基建"
    .Add Key:="sh000029", Item:="180价值"
    .Add Key:="sh000018", Item:="180金融"
    .Add Key:="sh000125", Item:="180稳定"
    .Add Key:="sh000027", Item:="180运输"
    .Add Key:="sh000021", Item:="180治理"
    .Add Key:="sh000026", Item:="180资源"
    .Add Key:="指数380", Item:="分类15"
    .Add Key:="sh000119", Item:="380R成长"
    .Add Key:="sh000120", Item:="380R价值"
    .Add Key:="sh000130", Item:="380波动"
    .Add Key:="sh000105", Item:="380材料"
    .Add Key:="sh000117", Item:="380成长"
    .Add Key:="sh000115", Item:="380等权"
    .Add Key:="sh000138", Item:="380低贝"
    .Add Key:="sh000112", Item:="380电信"
    .Add Key:="sh000141", Item:="380动态"
    .Add Key:="sh000137", Item:="380高贝"
    .Add Key:="sh000106", Item:="380工业"
    .Add Key:="sh000113", Item:="380公用"
    .Add Key:="sh000150", Item:="380红利"
    .Add Key:="sh000128", Item:="380基本"
    .Add Key:="sh000118", Item:="380价值"
    .Add Key:="sh000110", Item:="380金融"
    .Add Key:="sh000107", Item:="380可选"
    .Add Key:="sh000104", Item:="380能源"
    .Add Key:="sh000142", Item:="380稳定"
    .Add Key:="sh000108", Item:="380消费"
    .Add Key:="sh000111", Item:="380信息"
    .Add Key:="sh000109", Item:="380医药"
    .Add Key:="宽基指数市场", Item:="分类16"
    .Add Key:="sz399311", Item:="国证1000"
    .Add Key:="sz399303", Item:="国证2000"
    .Add Key:="sz399312", Item:="国证300"
    .Add Key:="sz399310", Item:="国证A50"
    .Add Key:="sh000903", Item:="中证100"
    .Add Key:="sz399903", Item:="中证100"
    .Add Key:="sh000906", Item:="中证800"
    .Add Key:="sh000132", Item:="上证100"
    .Add Key:="sh000133", Item:="上证150"
    .Add Key:="sh000010", Item:="上证180"
    .Add Key:="sh000009", Item:="上证380"
    .Add Key:="sh000098", Item:="上证F200"
    .Add Key:="sh000099", Item:="上证F300"
    .Add Key:="sh000100", Item:="上证F500"
    .Add Key:="sz399330", Item:="深证100"
    .Add Key:="sz399011", Item:="深证1000"
    .Add Key:="sz399004", Item:="深证100R"
    .Add Key:="sz399009", Item:="深证200"
    .Add Key:="sz399679", Item:="深证200R"
    .Add Key:="sz399007", Item:="深证300"
    .Add Key:="sz399010", Item:="深证700"
    .Add Key:="sz399107", Item:="深证Ａ指"
    .Add Key:="sz399108", Item:="深证Ｂ指"
    .Add Key:="sz399306", Item:="深证ETF"
    .Add Key:="sz399702", Item:="深证F120"
    .Add Key:="sz399703", Item:="深证F200"
    .Add Key:="sz399701", Item:="深证F60"
    .Add Key:="sz399648", Item:="深证GDP"
    .Add Key:="sz399317", Item:="国证Ａ指"
    .Add Key:="sz399318", Item:="国证Ｂ指"
    .Add Key:="sz399380", Item:="国证ETF"
    .Add Key:="sz399370", Item:="国证成长"
    .Add Key:="sz399428", Item:="国证定增"
    .Add Key:="sz399321", Item:="国证红利"
    .Add Key:="sz399379", Item:="国证基金"
    .Add Key:="sz399371", Item:="国证价值"
    .Add Key:="sz399369", Item:="国证责任"
    .Add Key:="sz399322", Item:="国证治理"
End With
End Function
'########################################################################################
'########################################################################################
'############################      非票精分调程设置      ################################
'########################################################################################
'########################################################################################





    





'########################################################################################
'########################################################################################
'################################   后台族非票精分调程   ################################
'########################################################################################
'########################################################################################
Sub 后台族非票精分调程_WA_调程基()
    Call 后台族非票精分调程_WA_主程(是否整基:=True)
End Sub
Sub 后台族非票精分调程_WA_调程指()
    Call 后台族非票精分调程_WA_主程(是否整基:=False)
End Sub



Private Function 后台族非票精分调程_WA_主程(Optional 是否整基 As Boolean = True)
    Dim 表名输出 As String
    表名输出 = "Z组历统时" & IIf(是否整基, "基", "指")
'========================================================================================
'制作字典
'========================================================================================
    '------------------------------------------------------------------------------------
    '制作字典
    '------------------------------------------------------------------------------------
    Dim 典码花册指 As New Dictionary
    Call STCALL花册工具_提取典码花天按市池(典码花册指, 包含市指:=True, 包含市基:=False, 包含市票:=False)
    Dim 典码花册基 As New Dictionary
    Call STCALL花册工具_提取典码花天按市池(典码花册基, 包含市指:=False, 包含市基:=True, 包含市票:=False)
    '------------------------------------------------------------------------------------
    '制作：数组
    '------------------------------------------------------------------------------------
    Dim 组历统时 As Variant
    If UTL判断工表存在(表名输出) = False Then
            If 是否整基 = True Then
                Call 历研统时引擎2数程(组历统时, 典码花册基, 常期类为日)
            Else
                Call 历研统时引擎2数程(组历统时, 典码花册指, 常期类为日)
            End If
            Dim WSTO As Worksheet
            Call PBASE格程工具_表操工表新增(WSTO, 表名输出, 基色底:=常色主碧)
            Call 历研统时引擎5格程按列(WSTO, 1)
            Call UTL数据转换_集ARR2WS(组历统时, WSTO, 2, 1)
            Call PBASE格程工具_表冻结锁定(WSTO, 1, 2)
            WSTO.Columns.AutoFit
            Set WSTO = Nothing
    Else
            '读取临时表替代
            Call UTL数据转换_集WS2ARR(组历统时, ThisWorkbook.Sheets(表名输出), 2, 1)
    End If
    Set 典码花册基 = Nothing
    Set 典码花册指 = Nothing
'========================================================================================
'制作：典
'========================================================================================
    '------------------------------------------------------------------------------------
    '制作基础列表：
    '必选部分：具有代表性的宽基/行业/概念，要求一定的市值与成交量，两市同名情况保留较大情况。
    '可选部分：不具有代表性意义，包括系列后缀/龙头/黄金ETF/货币ETF/基金公司ETF
    '重复部分：与以上重名，但实力较弱情况。
    '放弃部分：市值或成交量过小。
    '------------------------------------------------------------------------------------
    Dim 典码称 As New Dictionary
    Dim X As Long, Y As Long, 代称 As String, CIDL As String
    Dim 目行 As Long, 末行 As Long
    If 是否整基 = True Then
        Call 后台族非票精分调程_WA_制作典基必选(典码称)
        Call 后台族非票精分调程_WA_制作典基可选(典码称)
    Else
        Call 后台族非票精分调程_WA_制作典指必选(典码称)
        Call 后台族非票精分调程_WA_制作典指可选(典码称)
    End If
    Dim 行标志放弃部分 As Integer
    行标志放弃部分 = 1 + 典码称.Count
    '------------------------------------------------------------------------------------
    '寻找与必选部分同名的被替代列表
    '------------------------------------------------------------------------------------
    典码称.Add Key:="标志重复部分", Item:="分类98"
    Dim 典称称 As New Dictionary
    For X = 1 To 典码称.Count
        代称 = 典码称.Items(X - 1)
        If 典称称.Exists(代称) = False Then 典称称.Add Key:=代称, Item:=代称
    Next
    For X = LBound(组历统时, 1) To UBound(组历统时, 1)  '按码
        CIDL = 组历统时(X, 位统时列CIDL)
        代称 = 组历统时(X, 位统时列代称)
        If 典称称.Exists(代称) = True Then
            If 典码称.Exists(CIDL) = False Then 典码称.Add Key:=CIDL, Item:=代称
        End If
    Next
    典码称.Add Key:="标志放弃部分", Item:="分类99"
    Set 典称称 = Nothing
'========================================================================================
'输出：典码
'========================================================================================
    Dim WS整理 As Worksheet
    Call PBASE格程工具_表操工表新增(WS整理, "整理", 基色底:=常色主碧)
    Call PBASE格程工具_表冻结锁定(WS整理, 1, 2, 缩放:=80)
    WS整理.Cells.Font.Size = 10
    WS整理.Cells(1, 1) = "代码"
    WS整理.Cells(1, 2) = "代称"
    With WS整理.Rows(1)
        .Font.Bold = True
        .Font.Color = 常色主白
        .Interior.Color = 常色四靛
    End With
    Set WS整理 = ThisWorkbook.Sheets("整理")
    '格式化：按列
    Call 历研统时引擎5格程按列(WS整理, 1)
    '====================================================================================
    '输出
    '====================================================================================
    Dim 典码行 As New Dictionary
    For X = 1 To 典码称.Count
        目行 = X + 1
        CIDL = 典码称.Keys(X - 1)
        WS整理.Cells(目行, 位统时列CIDL) = CIDL
        WS整理.Cells(目行, 位统时列代称) = 典码称.Items(X - 1)
        If 典码行.Exists(CIDL) = False Then 典码行.Add Key:=CIDL, Item:=目行
    Next
    Set 典码称 = Nothing
'========================================================================================
'匹配信息
'========================================================================================
    Dim 计数新增 As Integer
    计数新增 = 0
    末行 = PBASE格程工具_表参末行指定(WS整理, 1)
    '====================================================================================
    '首行
    '====================================================================================
'    For Y = LBound(组历统时, 2) To UBound(组历统时, 2)
'        WS整理.Cells(1, Y) = 组历统时(LBound(组历统时, 1), Y)
'    Next
'    Stop
    '====================================================================================
    For X = LBound(组历统时, 1) To UBound(组历统时, 1)  '按码
        CIDL = 组历统时(X, 1)
        If UBCID是代码(CIDL) = True Then
            If 典码行.Exists(CIDL) Then
                目行 = 典码行(CIDL)
                For Y = LBound(组历统时, 2) To UBound(组历统时, 2)
                    WS整理.Cells(目行, Y) = 组历统时(X, Y)
                Next
            Else
                计数新增 = 计数新增 + 1
                目行 = 末行 + 计数新增
                For Y = LBound(组历统时, 2) To UBound(组历统时, 2)
                    WS整理.Cells(目行, Y) = 组历统时(X, Y)
                Next
            End If
        End If
    Next
    Set 典码行 = Nothing
    '====================================================================================
    '格式化
    '====================================================================================
    Dim 计数分类 As Integer
    计数分类 = 0
    For X = 2 To PBASE格程工具_表参末行指定(WS整理)
        CIDL = WS整理.Cells(X, 位统时列CIDL)
        If UBCID是中股指(CIDL) = True Or UBCID是中股基(CIDL) = True Then
            WS整理.Cells(X, 位统时列总终 + 1) = IIf(Left$(CIDL, 2) = "sh", "沪", "深")
            
            If WS整理.Cells(X, 位统时列市值) >= 5 Then
                WS整理.Cells(X, 位统时列市值).Interior.ColorIndex = 36
            End If
        Else
            计数分类 = 计数分类 + 1
            WS整理.Cells(X, 位统时列代称) = "分类" & 计数分类
            With WS整理.Rows(X)
                .Font.Bold = True
                If InStr(CIDL, "宽基") > 0 Then
                    .Interior.Color = 常色主靛
                ElseIf InStr(CIDL, "行业") > 0 Then
                    .Interior.Color = 常色十青
                ElseIf InStr(CIDL, "概念") > 0 Then
                    .Interior.Color = 常色四黄
                ElseIf InStr(CIDL, "境外") > 0 Then
                    .Interior.Color = 常色六紫
                Else
                    .Interior.Color = 常色六灰
                End If
            End With
        End If
        'If X <= 行标志放弃部分 Then
        If X <= PBASE格程工具_表参末行指定(WS整理) Then
            代称 = WS整理.Cells(X, 位统时列代称)
            WS整理.Cells(X, 位统时列总终 + 2) = "典码称.Add Key:=""" & CIDL & """, Item:=""" & 代称 & """"
        End If
    Next
'========================================================================================
'格式化
'========================================================================================
    WS整理.Columns.AutoFit
    With WS整理
        .Columns(位统时列十高小比).NumberFormatLocal = 全设格式of百分
        .Columns(位统时列仨高小比).NumberFormatLocal = 全设格式of百分
        .Columns(位统时列佰高小比).NumberFormatLocal = 全设格式of百分
        .Columns(位统时列十重心正比).NumberFormatLocal = 全设格式of百分
        .Columns(位统时列仨重心正比).NumberFormatLocal = 全设格式of百分
        .Columns(位统时列佰重心正比).NumberFormatLocal = 全设格式of百分
        .Columns(位统时列交额).NumberFormatLocal = 全设格式of零位
        .Columns(位统时列市值).NumberFormatLocal = 全设格式of零位
    End With
    With WS整理
        .Columns(位统时列十停数涨).Hidden = True
        .Columns(位统时列十停数高).Hidden = True
        .Columns(位统时列十停数跌).Hidden = True
        .Columns(位统时列十停数低).Hidden = True
        .Columns(位统时列仨停数涨).Hidden = True
        .Columns(位统时列仨停数高).Hidden = True
        .Columns(位统时列仨停数跌).Hidden = True
        .Columns(位统时列仨停数低).Hidden = True
        .Columns(位统时列佰停数涨).Hidden = True
        .Columns(位统时列佰停数高).Hidden = True
        .Columns(位统时列佰停数跌).Hidden = True
        .Columns(位统时列佰停数低).Hidden = True
'        .Cells(1, 位统时列波始).Resize(1, 位统时列停牌 - 位统时列波始 + 1).EntireColumn.Hidden = True
    End With
    Set WS整理 = Nothing
'========================================================================================
End Function



Sub 后台族非票精分调程_WA_测程中间操作()
    Dim 期类 As String
    期类 = 常期类为日
    Dim 表名 As String
    表名 = "Z指"
'========================================================================================
'导入现有
'========================================================================================
    If UTL判断工表存在(表名) = False Then Exit Sub
    Dim WS整理 As Worksheet
    Set WS整理 = ThisWorkbook.Sheets(表名)
    '====================================================================================
    Dim CIDL As String
    Dim 代称 As String
    Dim 计数分类 As Integer
    Dim 典基码称 As New Dictionary
    '====================================================================================
    Dim X As Integer
    For X = 2 To PBASE格程工具_表参末行指定(WS整理)
        CIDL = WS整理.Cells(X, 1)
        代称 = WS整理.Cells(X, 2)
        If Len(CIDL) = 0 Then
        ElseIf UBCID是代码(CIDL) = False Then
            计数分类 = 计数分类 + 1
            If 典基码称.Exists(CIDL) = False Then
                典基码称.Add Key:=CIDL, Item:="分类" & 计数分类
            End If
            '标志以下弃
'            If CIDL = "标志放弃部分" Then Exit For
        ElseIf UBCID是中股指(CIDL) Or UBCID是中股基(CIDL) = True Then
            If 典基码称.Exists(CIDL) = False Then
                典基码称.Add Key:=CIDL, Item:=代称
            End If
        End If
    Next
    Set WS整理 = Nothing
'========================================================================================
'导入现有
'========================================================================================
    Dim WSTO As Worksheet
    Call PBASE格程工具_表操工表新增(WSTO, "XX", 基色底:=常色主碧)
    WSTO.Cells.Font.Size = 10
    WSTO.Cells(1, 1) = "代码"
    WSTO.Cells(1, 2) = "代称"
    With WSTO.Rows(1)
        .Font.Bold = True
        .Font.Color = 常色主白
        .Interior.Color = 常色四靛
    End With
    '====================================================================================
    For X = 1 To 典基码称.Count
        WSTO.Cells(X + 1, 位统时列CIDL) = 典基码称.Keys(X - 1)
        WSTO.Cells(X + 1, 位统时列代称) = 典基码称.Items(X - 1)
    Next
    '====================================================================================
    WSTO.Columns.AutoFit
End Sub
'########################################################################################
'########################################################################################
'################################   后台族非票精分调程   #################################
'########################################################################################
'########################################################################################


