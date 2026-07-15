Attribute VB_Name = "SET_设0常量1"
Option Explicit
Option Compare Text
'========================================================================================
'========================================================================================
'设定
'========================================================================================
'========================================================================================
Public Const 常汇率港币 = 0.9      '20241001
'-----------------------------------------------
Public Const 常设市日隔离 = "2019/1/1"
'-----------------------------------------------
'定义各种变量的FORMAT
Public Const 全设格式of代码 = "000000"
Public Const 全设格式of零位 = "0"
Public Const 全设格式of一位 = "0.0"
Public Const 全设格式of二位 = "0.00"
Public Const 全设格式of三位 = "0.000"
Public Const 全设格式of价格 = "0.0"
Public Const 全设格式of百分 = "0%"
Public Const 全设格式of日期 = "YYYYMMDD"
Public Const 全设格式of时间 = "YYYYMMDD HHMMSS"
'========================================================================================
'========================================================================================
'常值：仓位
'========================================================================================
'========================================================================================
Public Const 常仓限冲 = 10
Public Const 常仓限常 = 5
Public Const 常仓限试 = 3
Public Const 常仓限警 = 1
Public Const 常仓限禁 = 0
'========================================================================================
'========================================================================================
'常值：分类
'========================================================================================
'========================================================================================
Public Const 常花结期 = "结期"
Public Const 常花中股 = "花天"
Public Const 常花美股 = "花美"
Public Const 常花中期 = "花期"
Public Const 常花港股指 = "花港指"
Public Const 常花港股通 = "花港通"
'-----------------------------------------------
'定义基础数据目录
Public Const 全设基夹根 = "D:\zdata"
Public Const 全设基夹中股 = "D:\zdata\data中股"
Public Const 全设基夹港股 = "D:\zdata\data港股"
Public Const 全设基夹美股 = "D:\zdata\data美股"
Public Const 全设基夹中期 = "D:\zdata\data中期"
'-----------------------------------------------
'定义外部工作簿路径
Public Const 常外簿藏库 = "D:\zdata\昭明藏库D.xlsx"
Public Const 常外簿花册 = "D:\zdata\昭明花册.xlsx"
'-----------------------------------------------
'定义结算周期的类别
Public Const 常期类为日 = "D"
Public Const 常期类为周 = "W"
Public Const 常期类为月 = "M"
Public Const 常期类为乾 = "X"
Public Const 常期类为巽 = "Y"
'-----------------------------------------------
Public Const 常簿缀选自 = "Z"
Public Const 常簿缀选临 = "."
Public Const 常簿缀结算 = "H"
Public Const 常簿缀频谱 = "P"
Public Const 常簿缀市板 = "Q"
Public Const 常簿缀研究 = "L"
Public Const 常簿缀历统 = "R"
'-----------------------------------------------
Public Const 常仓名宝合 = "Z"
Public Const 常仓名宝周 = ".ZW"      '池周
Public Const 常仓名宝福 = ".ZF"
Public Const 常仓名宝彦 = ".ZJ"
'-----------
Public Const 常池名今 = "Z0"      '池今
Public Const 常池名金 = "Z1"      '池金：下周冲高
Public Const 常池名银 = "Z2"      '池银：长期甲
Public Const 常池名铜 = "Z3"      '池铜：长期乙
Public Const 常池名黑 = "Zn"      '黑名单
'-----------------------------------------------
'定义各种市场类别的通配符
Public Const 常市板指 = "Qd"
Public Const 常市板基 = "Qe"
'中证成分分类（替代旧Qs分类）
Public Const 常市板票Qst = "Qst"  'ST/退市
Public Const 常市板票Qif = "Qif"  '沪深300
Public Const 常市板票Qic = "Qic"  '中证500
Public Const 常市板票Qim = "Qim"  '中证1000
Public Const 常市板票Qit = "Qit"  '中证2000
Public Const 常市板票Qin = "Qin"  '中证非（非成分股）
'-----------------------------------------------
'定义各种代码的通配符
Public Const 常通配码缀上证 = "sh"
Public Const 常通配码缀深证 = "sz"
Public Const 常通配码缀北证 = "bj"
'-----------
Public Const 常通配短码代码 = "######"
Public Const 常通配全码代码 = "??######"    '"s?######"
'-----------
Public Const 常通配短码上指 = "000###"
Public Const 常通配短码深指 = "399###"
Public Const 常通配全码上指 = "sh000###"
Public Const 常通配全码深指 = "sz399###"
'-----------
Public Const 常通配短码上主股 = "60####"
Public Const 常通配短码上科股 = "68####"
Public Const 常通配短码深主股 = "00####"
Public Const 常通配短码深创股 = "30####"
Public Const 常通配短码北交股 = "[9]#####"
Public Const 常通配全码上主股 = "sh60####"
Public Const 常通配全码上科股 = "sh68####"
Public Const 常通配全码深主股 = "sz00####"
Public Const 常通配全码深创股 = "sz30####"
Public Const 常通配全码北交股 = "bj[9]#####"
'-----------
Public Const 常通配短码上ETF = "5#####"
Public Const 常通配短码深ETF = "1#####"    '1xxxxx = 深市基金，通配符覆盖15/16/17等
Public Const 常通配全码上ETF = "sh5#####"
Public Const 常通配全码深ETF = "sz1#####"   'sz1xxxxx = 深市基金(ETF/LOF)，使用通配符1位覆盖sz15/sz16/sz17等
'========================================================================================
'========================================================================================
'定义OS列
'调整顺序：将操盘归为一类；将轨迹信息归为一类
'只把需要记录历史演变的放入HX，例如BTXX，对于可以直接计算的不再放入（BSXX）
'包含信息：
'(1)基本信息：期类、累龄等；
'(2)柱线信息：两日完整K线信息（收开高低）；
'(3)柱组信息：五至十日统计信息，五收符、连续涨跌、或10日收盘与最高；
'(4)均线信息，均线相交信息；
'(5)阶部信息：均线衍生信息，阶、六象、八部、护线；
'(6)统计信息：历史各种统计；
'(7)算法信息：用于回测。
'========================================================================================
'分路：OSqp
'----------------------------------------------------------------------------------------
'(1)基本信息
'----------------------------------------------
Public Const 位os代码 = 1
Public Const 位os期类 = 2
Public Const 位os口期 = 3
Public Const 位os停牌 = 4
'----------------------------------------------
'(2)波动信息
'----------------------------------------------
Public Const 位os始柱波类 = 5
'------------------------
'结价：已正式结算的价。相当于上期的价格，即昨天或上周五
Public Const 位os结期 = 位os始柱波类 + 0
Public Const 位os结收 = 位os始柱波类 + 1
Public Const 位os结开 = 位os始柱波类 + 2
Public Const 位os结高 = 位os始柱波类 + 3
Public Const 位os结低 = 位os始柱波类 + 4
Public Const 位os结交量 = 位os始柱波类 + 5
Public Const 位os结换手 = 位os始柱波类 + 6
Public Const 位os结量比 = 位os始柱波类 + 7
'-----
'前价：已正式结算的价。相当于上上期的价格，即前天或上上周五
Public Const 位os前期 = 位os始柱波类 + 8
Public Const 位os前收 = 位os始柱波类 + 9
Public Const 位os前开 = 位os始柱波类 + 10
Public Const 位os前高 = 位os始柱波类 + 11
Public Const 位os前低 = 位os始柱波类 + 12
Public Const 位os前交量 = 位os始柱波类 + 13
Public Const 位os前换手 = 位os始柱波类 + 14
Public Const 位os前量比 = 位os始柱波类 + 15
'-----------------------------------------------------------------
'临价信息：临时结算的价。相当于本期的价格，即今天或本周进行到现在（但还未到正式结算时间点）
'对于日类os，临价在盘中结算前与正式结算前利用实时信息进行更新。
'对于周类os，临价在每日结算时利用当时正式结算的日类信息进行更新，在盘中结算中用实时信息更新。
'出现临时价格的地方：
'(1)结算前，将即将用于日类与周类结算的价格写入临价，其中实时结算最为复杂
'(2)继点结算中，用“结价”更新“前价”，用“临价”更新“结价”
'(3)继点结算引擎中清零
'(4)每日结算时，在（日类结算后）（周类结算前），把日类正式结算价格填写到周类临时价格
'(5)在神谕中，对临时价格进行利用
'-----------------------------------------------------------------
Public Const 位os临期 = 位os始柱波类 + 16
Public Const 位os临收 = 位os始柱波类 + 17
Public Const 位os临开 = 位os始柱波类 + 18
Public Const 位os临高 = 位os始柱波类 + 19
Public Const 位os临低 = 位os始柱波类 + 20
Public Const 位os临交量 = 位os始柱波类 + 21
Public Const 位os临换手 = 位os始柱波类 + 22
Public Const 位os临量比 = 位os始柱波类 + 23
Public Const 位os临幅PR = 位os始柱波类 + 24
Public Const 位os临幅HR = 位os始柱波类 + 25
Public Const 位os临幅LR = 位os始柱波类 + 26
'------------------------
Public Const 位os终柱波类 = 位os始柱波类 + 26
'----------------------------------------------
'(3)柱组信息
'----------------------------------------------
Public Const 位os始柱组类 = 位os终柱波类 + 1
'------------------------
Public Const 位os结幅PR0 = 位os始柱组类 + 0
Public Const 位os结幅PR1 = 位os始柱组类 + 1
Public Const 位os结幅PR2 = 位os始柱组类 + 2
Public Const 位os结幅PR3 = 位os始柱组类 + 3
Public Const 位os结幅PR4 = 位os始柱组类 + 4
Public Const 位os结幅PR5 = 位os始柱组类 + 5
Public Const 位os结幅PR6 = 位os始柱组类 + 6
Public Const 位os结幅PR7 = 位os始柱组类 + 7
Public Const 位os结幅PR8 = 位os始柱组类 + 8
Public Const 位os结幅PR9 = 位os始柱组类 + 9
'------------------------
Public Const 位os结幅HR0 = 位os始柱组类 + 10
Public Const 位os结幅HR1 = 位os始柱组类 + 11
Public Const 位os结幅HR2 = 位os始柱组类 + 12
Public Const 位os结幅HR3 = 位os始柱组类 + 13
Public Const 位os结幅HR4 = 位os始柱组类 + 14
Public Const 位os结幅HR5 = 位os始柱组类 + 15
Public Const 位os结幅HR6 = 位os始柱组类 + 16
Public Const 位os结幅HR7 = 位os始柱组类 + 17
Public Const 位os结幅HR8 = 位os始柱组类 + 18
Public Const 位os结幅HR9 = 位os始柱组类 + 19
'------------------------
Public Const 位os结幅LR0 = 位os始柱组类 + 20
Public Const 位os结幅LR1 = 位os始柱组类 + 21
Public Const 位os结幅LR2 = 位os始柱组类 + 22
Public Const 位os结幅LR3 = 位os始柱组类 + 23
Public Const 位os结幅LR4 = 位os始柱组类 + 24
Public Const 位os结幅LR5 = 位os始柱组类 + 25
Public Const 位os结幅LR6 = 位os始柱组类 + 26
Public Const 位os结幅LR7 = 位os始柱组类 + 27
Public Const 位os结幅LR8 = 位os始柱组类 + 28
Public Const 位os结幅LR9 = 位os始柱组类 + 29
'------------------------
Public Const 位os价H0 = 位os始柱组类 + 30
Public Const 位os价H1 = 位os始柱组类 + 31
Public Const 位os价H2 = 位os始柱组类 + 32
Public Const 位os价H3 = 位os始柱组类 + 33
Public Const 位os价H4 = 位os始柱组类 + 34
Public Const 位os价H5 = 位os始柱组类 + 35
Public Const 位os价H6 = 位os始柱组类 + 36
Public Const 位os价H7 = 位os始柱组类 + 37
Public Const 位os价H8 = 位os始柱组类 + 38
Public Const 位os价H9 = 位os始柱组类 + 39
'------------------------
Public Const 位os价L0 = 位os始柱组类 + 40
Public Const 位os价L1 = 位os始柱组类 + 41
Public Const 位os价L2 = 位os始柱组类 + 42
Public Const 位os价L3 = 位os始柱组类 + 43
Public Const 位os价L4 = 位os始柱组类 + 44
Public Const 位os价L5 = 位os始柱组类 + 45
Public Const 位os价L6 = 位os始柱组类 + 46
Public Const 位os价L7 = 位os始柱组类 + 47
Public Const 位os价L8 = 位os始柱组类 + 48
Public Const 位os价L9 = 位os始柱组类 + 49
'------------------------
Public Const 位os价O0 = 位os始柱组类 + 50
Public Const 位os价O1 = 位os始柱组类 + 51
Public Const 位os价O2 = 位os始柱组类 + 52
Public Const 位os价O3 = 位os始柱组类 + 53
Public Const 位os价O4 = 位os始柱组类 + 54
Public Const 位os价O5 = 位os始柱组类 + 55
Public Const 位os价O6 = 位os始柱组类 + 56
Public Const 位os价O7 = 位os始柱组类 + 57
Public Const 位os价O8 = 位os始柱组类 + 58
Public Const 位os价O9 = 位os始柱组类 + 59
'------------------------
Public Const 位os价C0 = 位os始柱组类 + 60
Public Const 位os价C1 = 位os始柱组类 + 61
Public Const 位os价C2 = 位os始柱组类 + 62
Public Const 位os价C3 = 位os始柱组类 + 63
Public Const 位os价C4 = 位os始柱组类 + 64
Public Const 位os价C5 = 位os始柱组类 + 65
Public Const 位os价C6 = 位os始柱组类 + 66
Public Const 位os价C7 = 位os始柱组类 + 67
Public Const 位os价C8 = 位os始柱组类 + 68
Public Const 位os价C9 = 位os始柱组类 + 69
'------------------------
Public Const 位osBTPRb = 位os始柱组类 + 70
Public Const 位osBTPR0 = 位os始柱组类 + 71
Public Const 位osBTPR1 = 位os始柱组类 + 72
Public Const 位osBTPR3 = 位os始柱组类 + 73
Public Const 位osBTPR9 = 位os始柱组类 + 74
'------------------------
Public Const 位osBTHR0 = 位os始柱组类 + 75
Public Const 位osBTHR1 = 位os始柱组类 + 76
Public Const 位osBTHR3 = 位os始柱组类 + 77
Public Const 位osBTHR9 = 位os始柱组类 + 78
'------------------------
Public Const 位os终柱组类 = 位os始柱组类 + 78
'----------------------------------------------
'(4)均线信息
'----------------------------------------------
Public Const 位os始均线类 = 位os终柱组类 + 1
'------------------------
Public Const 位osJZ = 位os始均线类 + 0
Public Const 位osJA = 位os始均线类 + 1
Public Const 位osJB = 位os始均线类 + 2
Public Const 位osJC = 位os始均线类 + 3
Public Const 位osJD = 位os始均线类 + 4
Public Const 位osJE = 位os始均线类 + 5
Public Const 位osJF = 位os始均线类 + 6
Public Const 位osJG = 位os始均线类 + 7
'-------------------------
Public Const 位osBTZA = 位os始均线类 + 8
Public Const 位osBTZB = 位os始均线类 + 9
Public Const 位osBTAB = 位os始均线类 + 10
Public Const 位osBTZC = 位os始均线类 + 11
Public Const 位osBTAC = 位os始均线类 + 12
Public Const 位osBTBC = 位os始均线类 + 13
Public Const 位osBTZD = 位os始均线类 + 14
Public Const 位osBTAD = 位os始均线类 + 15
Public Const 位osBTBD = 位os始均线类 + 16
Public Const 位osBTCD = 位os始均线类 + 17
Public Const 位osBTZE = 位os始均线类 + 18
Public Const 位osBTAE = 位os始均线类 + 19
Public Const 位osBTCE = 位os始均线类 + 20
Public Const 位osBTDE = 位os始均线类 + 21
Public Const 位osBTZF = 位os始均线类 + 22
Public Const 位osBTAF = 位os始均线类 + 23
Public Const 位osBTCF = 位os始均线类 + 24
Public Const 位osBTDF = 位os始均线类 + 25
Public Const 位osBTEF = 位os始均线类 + 26
Public Const 位osBTZG = 位os始均线类 + 27
Public Const 位osBTAG = 位os始均线类 + 28
Public Const 位osBTCG = 位os始均线类 + 29
Public Const 位osBTEG = 位os始均线类 + 30
Public Const 位osBTFG = 位os始均线类 + 31
'------------------------
Public Const 位osBTZA1 = 位os始均线类 + 32
Public Const 位osBTZA2 = 位os始均线类 + 33
Public Const 位osBTZA3 = 位os始均线类 + 34
Public Const 位osBTZA4 = 位os始均线类 + 35
Public Const 位osBTZA5 = 位os始均线类 + 36
Public Const 位osBTZA暂下破 = 位os始均线类 + 37
'------------------------
Public Const 位os终均线类 = 位os始均线类 + 37
'----------------------------------------------
'(6)奏信息
'----------------------------------------------
Public Const 位os始奏类 = 位os终均线类 + 1
'------------------------
Public Const 位os奏数交CD总 = 位os始奏类 + 0       '周级别
Public Const 位os奏数交BC总 = 位os始奏类 + 1       '月级别
'------------------------
Public Const 位os奏丘启XEDC = 位os始奏类 + 2        '周级别
Public Const 位os奏丘启XCBA = 位os始奏类 + 3        '月级别
'-----
Public Const 位os奏数DE叉DC = 位os始奏类 + 4
Public Const 位os奏数DE叉CB = 位os始奏类 + 5
Public Const 位os奏数DE叉EZ = 位os始奏类 + 6
Public Const 位os奏数DE叉DZ = 位os始奏类 + 7
'-----
Public Const 位os奏数CE叉DC = 位os始奏类 + 8
Public Const 位os奏数CE叉CB = 位os始奏类 + 9
Public Const 位os奏数CE叉EZ = 位os始奏类 + 10
Public Const 位os奏数CE叉DZ = 位os始奏类 + 11
'-----
Public Const 位os奏数CD叉CB = 位os始奏类 + 12
Public Const 位os奏数CD叉CZ = 位os始奏类 + 13
'-----
Public Const 位os奏数BC叉CA = 位os始奏类 + 14
Public Const 位os奏数BC叉BA = 位os始奏类 + 15
Public Const 位os奏数BC叉CZ = 位os始奏类 + 16
Public Const 位os奏数BC叉BZ = 位os始奏类 + 17
'-----
Public Const 位os奏数AC叉BA = 位os始奏类 + 18
Public Const 位os奏数AC叉CZ = 位os始奏类 + 19
Public Const 位os奏数AC叉BZ = 位os始奏类 + 20
'------------------------
Public Const 位os终奏类 = 位os始奏类 + 20
'----------------------------------------------
'(5)阶部信息
'----------------------------------------------
Public Const 位os始阶部类 = 位os终奏类 + 1
'------------------------
'局系统
Public Const 位os局势周基 = 位os始阶部类 + 0
Public Const 位os局势日基 = 位os始阶部类 + 1
Public Const 位os局ZEFG = 位os始阶部类 + 2
Public Const 位os局ZCDE = 位os始阶部类 + 3
Public Const 位os局ZABC = 位os始阶部类 + 4
Public Const 位os终阶部类 = 位os始阶部类 + 14
'----------------------------------------------
'(3a)波动信息
'----------------------------------------------
Public Const 位os始龟类 = 位os终阶部类 + 1
'------------------------
Public Const 位os龟前顶 = 位os始龟类 + 0
Public Const 位os龟结顶 = 位os始龟类 + 1
Public Const 位os龟临顶 = 位os始龟类 + 2
Public Const 位os龟BT顶 = 位os始龟类 + 3
Public Const 位os龟前底 = 位os始龟类 + 4
Public Const 位os龟结底 = 位os始龟类 + 5
Public Const 位os龟临底 = 位os始龟类 + 6
Public Const 位os龟BT底 = 位os始龟类 + 7
'------------------------
Public Const 位os龟前哼 = 位os始龟类 + 8
Public Const 位os龟结哼 = 位os始龟类 + 9
Public Const 位os龟临哼 = 位os始龟类 + 10
Public Const 位os龟BT哼 = 位os始龟类 + 11
Public Const 位os龟前哈 = 位os始龟类 + 12
Public Const 位os龟结哈 = 位os始龟类 + 13
Public Const 位os龟临哈 = 位os始龟类 + 14
Public Const 位os龟BT哈 = 位os始龟类 + 15
'------------------------
Public Const 位os龟结哼幅 = 位os始龟类 + 16
Public Const 位os龟结哈幅 = 位os始龟类 + 17
'------------------------
Public Const 位os龟BT合顶 = 位os始龟类 + 18
Public Const 位os龟BT合底 = 位os始龟类 + 19
'------------------------
Public Const 位os龟叠幅0 = 位os始龟类 + 20
Public Const 位os龟叠幅1 = 位os始龟类 + 21
Public Const 位os龟叠幅2 = 位os始龟类 + 22
Public Const 位os龟叠幅3 = 位os始龟类 + 23
Public Const 位os龟叠幅4 = 位os始龟类 + 24
'------------------------
Public Const 位os龟具极五 = 位os始龟类 + 25
Public Const 位os龟具顶态 = 位os始龟类 + 26
Public Const 位os龟具顶触 = 位os始龟类 + 27
'------------------------
Public Const 位os终龟类 = 位os始龟类 + 27
'----------------------------------------------
'(7)工具箱
'----------------------------------------------
Public Const 位os始具类 = 位os终龟类 + 1
'------------------------
Public Const 位os具锚ZD = 位os始具类 + 0
Public Const 位os具锚ZC = 位os始具类 + 1
'-----
Public Const 位os具BTIB = 位os始具类 + 2
Public Const 位os具比柱JB = 位os始具类 + 3
Public Const 位os具BT鼎 = 位os始具类 + 4
'-----
Public Const 位os具上符范 = 位os始具类 + 5
Public Const 位os具上符数触顶 = 位os始具类 + 6
Public Const 位os具上符数触哼 = 位os始具类 + 7
Public Const 位os具上符数触底 = 位os始具类 + 8
Public Const 位os具上符数触哈 = 位os始具类 + 9
Public Const 位os具上符串 = 位os始具类 + 10
Public Const 位os具上符0 = 位os始具类 + 11
Public Const 位os具上符1 = 位os始具类 + 12
Public Const 位os具上符2 = 位os始具类 + 13
Public Const 位os具上符3 = 位os始具类 + 14
Public Const 位os具上符4 = 位os始具类 + 15
'-----
Public Const 位os具中符串 = 位os始具类 + 16
Public Const 位os具中符0 = 位os始具类 + 17
Public Const 位os具中符范 = 位os始具类 + 18
Public Const 位os具中符数A = 位os始具类 + 19
Public Const 位os具中符数B = 位os始具类 + 20
Public Const 位os具中符数C = 位os始具类 + 21
Public Const 位os具中符数D = 位os始具类 + 22
'-----
Public Const 位os具并符串 = 位os始具类 + 23
Public Const 位os具并符0 = 位os始具类 + 24
Public Const 位os具并符范 = 位os始具类 + 25
Public Const 位os具宽符串 = 位os始具类 + 26
Public Const 位os具幅符串 = 位os始具类 + 27
'------------------------
Public Const 位os终具类 = 位os始具类 + 27
'----------------------------------------------
'(7)算法信息
'----------------------------------------------
Public Const 位os始算法类 = 位os终具类 + 1
'------------------------
Public Const 位os算法名 = 位os始算法类 + 0
Public Const 位os算累持 = 位os始算法类 + 1
Public Const 位os算累赚 = 位os始算法类 + 2
Public Const 位os算今赚 = 位os始算法类 + 3
Public Const 位os算今手 = 位os始算法类 + 4
Public Const 位os算今仓 = 位os始算法类 + 5
Public Const 位os算变仓 = 位os始算法类 + 6
'------------------------
Public Const 位os基横类 = 位os始算法类 + 7
Public Const 位os基层类 = 位os始算法类 + 8
Public Const 位os基顶型 = 位os始算法类 + 9
Public Const 位os基竖态 = 位os始算法类 + 10
'------------------------
Public Const 位os层界 = 位os始算法类 + 11
Public Const 位os层地型 = 位os始算法类 + 12
Public Const 位os层护型 = 位os始算法类 + 13
Public Const 位os层护段AB = 位os始算法类 + 14
Public Const 位os层护级AB = 位os始算法类 + 15
Public Const 位os层护段CD = 位os始算法类 + 16
Public Const 位os层护级CD = 位os始算法类 + 17
'------------------------
Public Const 位os终算法类 = 位os始算法类 + 17
'----------------------------------------------
'(9)统计信息
'----------------------------------------------
Public Const 位os始基类 = 位os终算法类 + 1
Public Const 位os基代称 = 位os始基类 + 0
Public Const 位os基市期 = 位os始基类 + 1
Public Const 位os基累龄 = 位os始基类 + 2
Public Const 位os终基类 = 位os始基类 + 2
'----------------------------------------------
'(10)统计信息
'----------------------------------------------
Public Const 位os始统涨类 = 位os终基类 + 1
'-----
Public Const 位os统全数总 = 位os始统涨类 + 0
Public Const 位os统全复涨总 = 位os始统涨类 + 1
Public Const 位os统全和涨总 = 位os始统涨类 + 2
Public Const 位os统全和高总 = 位os始统涨类 + 3
Public Const 位os统全数正 = 位os始统涨类 + 4
Public Const 位os统全和涨正 = 位os始统涨类 + 5
'-------------------------
Public Const 位os始统线类 = 位os始统涨类 + 6
'-----
Public Const 位os统数交DE全 = 位os始统线类 + 0
Public Const 位os统值最正DE = 位os始统线类 + 1
Public Const 位os统值最负DE = 位os始统线类 + 2
Public Const 位os统数交CD全 = 位os始统线类 + 3
Public Const 位os统数交CD震 = 位os始统线类 + 4
Public Const 位os统值最正CD = 位os始统线类 + 5
Public Const 位os统值最负CD = 位os始统线类 + 6
Public Const 位os统数交BC全 = 位os始统线类 + 7
Public Const 位os统数交BC震 = 位os始统线类 + 8
Public Const 位os统值最正BC = 位os始统线类 + 9
Public Const 位os统值最负BC = 位os始统线类 + 10
'-------------------------
Public Const 位os始统区类 = 位os始统线类 + 11
'-----
Public Const 位os统C类是否 = 位os始统区类 + 0
Public Const 位os统C类数总 = 位os始统区类 + 1
Public Const 位os统C类数正 = 位os始统区类 + 2
Public Const 位os统C类和涨总 = 位os始统区类 + 3
Public Const 位os统B类是否 = 位os始统区类 + 4
Public Const 位os统B类数总 = 位os始统区类 + 5
Public Const 位os统B类数正 = 位os始统区类 + 6
Public Const 位os统B类和涨总 = 位os始统区类 + 7
Public Const 位os统A类是否 = 位os始统区类 + 8
Public Const 位os统A类数总 = 位os始统区类 + 9
Public Const 位os统A类和涨总 = 位os始统区类 + 10
Public Const 位os统A类和高总 = 位os始统区类 + 11
Public Const 位os统A类数正 = 位os始统区类 + 12
Public Const 位os统A类和涨正 = 位os始统区类 + 13
'-----
Public Const 位os统A类数子2c = 位os始统区类 + 14
Public Const 位os统A类数子2d = 位os始统区类 + 15
Public Const 位os统A类数子2e = 位os始统区类 + 16
Public Const 位os统A类数子余 = 位os始统区类 + 17
Public Const 位os统A类数子甲ZB总 = 位os始统区类 + 18
Public Const 位os统A类数子甲ZB正 = 位os始统区类 + 19
Public Const 位os统A类数子乙BZ总 = 位os始统区类 + 20
Public Const 位os统A类数子乙BZ正 = 位os始统区类 + 21
Public Const 位os统A类数子丙CZ总 = 位os始统区类 + 22
Public Const 位os统A类数子丙CZ正 = 位os始统区类 + 23
'-------------------------
Public Const 位os始统高类 = 位os始统区类 + 24
'-----
Public Const 位os统A类是否BSHRL0 = 位os始统高类 + 0   '是否最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类数单BSHRL0 = 位os始统高类 + 1   '个数of最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类数双BSHRL0 = 位os始统高类 + 2   '个数of连续最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类是否BSHRL1 = 位os始统高类 + 3   '是否最高波动小于1：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类数单BSHRL1 = 位os始统高类 + 4   '个数of最高波动小于1：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类数双BSHRL1 = 位os始统高类 + 5   '个数of连续最高波动小于1：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类是否BSHRL3 = 位os始统高类 + 6   '是否最高波动小于2：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类数单BSHRL3 = 位os始统高类 + 7   '个数of最高波动小于2：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类数双BSHRL3 = 位os始统高类 + 8   '个数of连续最高波动小于2：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类是否BSHRL5 = 位os始统高类 + 9   '是否最高波动小于3：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类数单BSHRL5 = 位os始统高类 + 10   '个数of最高波动小于3：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位os统A类数双BSHRL5 = 位os始统高类 + 11   '个数of连续最高波动小于3：仅针对周类（WBTCD>0 and WBTZC>0）
'-----
Public Const 位os终统高类 = 位os始统高类 + 12
'----------------------------------------------
Public Const 位os容积 = 位os终统高类
'========================================================================================
'定义QT列
'========================================================================================
Public Const 位qt代码 = 1
Public Const 位qt代称 = 2
'----------------------------------------------
Public Const 位qt今涨幅 = 3
Public Const 位qt今高幅 = 4
Public Const 位qt今收 = 5
Public Const 位qt前收 = 6
Public Const 位qt今开 = 7
Public Const 位qt今高 = 8
Public Const 位qt今低 = 9
Public Const 位qt今量 = 10
Public Const 位qt量比 = 11
Public Const 位qt换手 = 12
Public Const 位qt今额 = 13
Public Const 位qt市值 = 14
'-----------
Public Const 位qt停牌 = 15  '判断是否停牌的总开关
Public Const 位qt今时 = 16
Public Const 位qt今期 = 17
'----------------------------------------------
Public Const 位qt成分 = 18
Public Const 位qt市板 = 19
Public Const 位qt行业 = 20
Public Const 位qt行益 = 21
Public Const 位qt概念 = 22
'----------------------------------------------
Public Const 位qt仓主 = 23
Public Const 位qt仓周 = 24
Public Const 位qt今池 = 25
Public Const 位qt在池 = 26
Public Const 位qt盯盘类别 = 27
'----------------------------------------------
Public Const 位qt主宽 = 27
'========================================================================================
'花天表AI提示列（在OS车道之后 = 花宽全道 + 花宽单道 + 1）
'========================================================================================
Public Const 位列花天AI提示 = 245

'========================================================================================

