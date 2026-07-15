Attribute VB_Name = "WMH_T历研统时_B9统时分析"
Option Explicit

'待完成：是否与【历调】合并？
'----------------------------------------------------------------------------------------
'指标群：周级波动
'作用：衔接周类操盘体系
'-----------
Public Const 位谕始of族周结统 = 位谕列始全部 + 1
'-----------
Public Const 位谕of周类全数总 = 位谕始of族周结统 + 0
Public Const 位谕of周类全数正 = 位谕始of族周结统 + 1
Public Const 位谕of周类比正总 = 位谕始of族周结统 + 2
Public Const 位谕of周类全复涨总 = 位谕始of族周结统 + 3
Public Const 位谕of周类全和涨正 = 位谕始of族周结统 + 4
Public Const 位谕of周类全和高总 = 位谕始of族周结统 + 5
'-----------
Public Const 位谕始of族周结统类均 = 位谕of周类全和高总 + 1
Public Const 位谕of周类比交总CD2DE = 位谕始of族周结统类均 + 0
Public Const 位谕of周类比交总BC2DE = 位谕始of族周结统类均 + 1
Public Const 位谕of周类数交DE全 = 位谕始of族周结统类均 + 2
Public Const 位谕of周类值最正DE = 位谕始of族周结统类均 + 3
Public Const 位谕of周类值最负DE = 位谕始of族周结统类均 + 4
Public Const 位谕of周类数交CD震 = 位谕始of族周结统类均 + 5
Public Const 位谕of周类值最正CD = 位谕始of族周结统类均 + 6
Public Const 位谕of周类值最负CD = 位谕始of族周结统类均 + 7
Public Const 位谕of周类数交BC震 = 位谕始of族周结统类均 + 8
Public Const 位谕of周类值最正BC = 位谕始of族周结统类均 + 9
Public Const 位谕of周类值最负BC = 位谕始of族周结统类均 + 10
'-----------
Public Const 位谕始of族周结统类区 = 位谕of周类值最负BC + 1
Public Const 位谕of周C类数总 = 位谕始of族周结统类区 + 0
Public Const 位谕of周C类比类全 = 位谕始of族周结统类区 + 1
Public Const 位谕of周C类比正类 = 位谕始of族周结统类区 + 2
Public Const 位谕of周C类均涨总 = 位谕始of族周结统类区 + 3
Public Const 位谕of周B类数总 = 位谕始of族周结统类区 + 4
Public Const 位谕of周B类比类全 = 位谕始of族周结统类区 + 5
Public Const 位谕of周B类比正类 = 位谕始of族周结统类区 + 6
Public Const 位谕of周B类均涨总 = 位谕始of族周结统类区 + 7
Public Const 位谕of周A类数总 = 位谕始of族周结统类区 + 8
Public Const 位谕of周A类比类全 = 位谕始of族周结统类区 + 9
Public Const 位谕of周A类比正类 = 位谕始of族周结统类区 + 10
Public Const 位谕of周A类均涨总 = 位谕始of族周结统类区 + 11
Public Const 位谕of周A类均高总 = 位谕始of族周结统类区 + 12
Public Const 位谕of周A类均涨正 = 位谕始of族周结统类区 + 13
Public Const 位谕of周A类均涨负 = 位谕始of族周结统类区 + 14
Public Const 位谕of周A类比正子甲ZB正 = 位谕始of族周结统类区 + 20        '最重要统计结果：代表在所有A类阳柱中W2c占比多少（绝大多数）
Public Const 位谕of周A类比正子2c = 位谕始of族周结统类区 + 21        '最重要统计结果：代表在所有A类阳柱中W2c占比多少（绝大多数）
Public Const 位谕of周A类比类子2c = 位谕始of族周结统类区 + 22
Public Const 位谕of周A类比类子2d = 位谕始of族周结统类区 + 23
Public Const 位谕of周A类比类子2e = 位谕始of族周结统类区 + 24
Public Const 位谕of周A类比例子甲ZB正 = 位谕始of族周结统类区 + 25
Public Const 位谕of周A类比类子甲ZB总 = 位谕始of族周结统类区 + 26
Public Const 位谕of周A类比类子乙BZ总 = 位谕始of族周结统类区 + 27
Public Const 位谕of周A类比类子丙CZ总 = 位谕始of族周结统类区 + 28
Public Const 位谕of周C类是否 = 位谕始of族周结统类区 + 29
Public Const 位谕of周B类是否 = 位谕始of族周结统类区 + 30
Public Const 位谕of周A类是否 = 位谕始of族周结统类区 + 31
'-----------
Public Const 位谕始of族周结统类高 = 位谕of周A类是否 + 1
Public Const 位谕of周A类是否BSHRL0 = 位谕始of族周结统类高 + 0   '是否最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类数单BSHRL0 = 位谕始of族周结统类高 + 1   '个数of最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类数双BSHRL0 = 位谕始of族周结统类高 + 2   '个数of连续最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类是否BSHRL1 = 位谕始of族周结统类高 + 3   '是否最高波动小于1：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类数单BSHRL1 = 位谕始of族周结统类高 + 4   '个数of最高波动小于1：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类数双BSHRL1 = 位谕始of族周结统类高 + 5   '个数of连续最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类是否BSHRL3 = 位谕始of族周结统类高 + 6   '是否最高波动小于2：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类数单BSHRL3 = 位谕始of族周结统类高 + 7   '个数of最高波动小于2：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类数双BSHRL3 = 位谕始of族周结统类高 + 8   '个数of连续最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类是否BSHRL5 = 位谕始of族周结统类高 + 9   '是否最高波动小于2：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类数单BSHRL5 = 位谕始of族周结统类高 + 10   '个数of最高波动小于2：仅针对周类（WBTCD>0 and WBTZC>0）
Public Const 位谕of周A类数双BSHRL5 = 位谕始of族周结统类高 + 11   '个数of连续最高波动小于0：仅针对周类（WBTCD>0 and WBTZC>0）
'-----------
Public Const 位谕of周A类数单BSHRL0比 = 位谕始of族周结统类高 + 12
Public Const 位谕of周A类数单BSHRL1比 = 位谕始of族周结统类高 + 13
Public Const 位谕of周A类数单BSHRL3比 = 位谕始of族周结统类高 + 14
Public Const 位谕of周A类数单BSHRL5比 = 位谕始of族周结统类高 + 15
Public Const 位谕of周A类数非BSHRL0比 = 位谕始of族周结统类高 + 16
Public Const 位谕of周A类数非BSHRL1比 = 位谕始of族周结统类高 + 17
Public Const 位谕of周A类数非BSHRL3比 = 位谕始of族周结统类高 + 18
Public Const 位谕of周A类数非BSHRL5比 = 位谕始of族周结统类高 + 19
'-----------
Public Const 位谕终of族周结统 = 位谕始of族周结统类高 + 19
'----------------------------------------------------------------------------------------
Public Const 位谕始of族日结统 = 位谕终of族周结统 + 1
'-----------
Public Const 位谕of日类全数总 = 位谕始of族日结统 + 0
Public Const 位谕of日类全数正 = 位谕始of族日结统 + 1
Public Const 位谕of日类比正总 = 位谕始of族日结统 + 2
Public Const 位谕of日类全复涨总 = 位谕始of族日结统 + 3
Public Const 位谕of日类全和涨正 = 位谕始of族日结统 + 4
Public Const 位谕of日类全和高总 = 位谕始of族日结统 + 5
'-----------
Public Const 位谕始of族日结统类区 = 位谕of日类全和高总 + 1
Public Const 位谕of日C类数总 = 位谕始of族日结统类区 + 0
Public Const 位谕of日C类比类全 = 位谕始of族日结统类区 + 1
Public Const 位谕of日C类比正类 = 位谕始of族日结统类区 + 2
Public Const 位谕of日C类均涨总 = 位谕始of族日结统类区 + 3
Public Const 位谕of日B类数总 = 位谕始of族日结统类区 + 4
Public Const 位谕of日B类比类全 = 位谕始of族日结统类区 + 5
Public Const 位谕of日B类比正类 = 位谕始of族日结统类区 + 6
Public Const 位谕of日B类均涨总 = 位谕始of族日结统类区 + 7
Public Const 位谕of日A类数总 = 位谕始of族日结统类区 + 8
Public Const 位谕of日A类比类全 = 位谕始of族日结统类区 + 9
Public Const 位谕of日A类比正类 = 位谕始of族日结统类区 + 10
Public Const 位谕of日A类均涨总 = 位谕始of族日结统类区 + 11
Public Const 位谕of日A类均高总 = 位谕始of族日结统类区 + 12
Public Const 位谕of日C类是否 = 位谕始of族日结统类区 + 13
Public Const 位谕of日B类是否 = 位谕始of族日结统类区 + 14
Public Const 位谕of日A类是否 = 位谕始of族日结统类区 + 15
'-----------
Public Const 位谕始of族日结统类高 = 位谕of日A类是否 + 1
Public Const 位谕of日A类是否BSHRL0 = 位谕始of族日结统类高 + 0   '是否最高波动小于0：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数单BSHRL0 = 位谕始of族日结统类高 + 1   '个数of最高波动小于0：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数双BSHRL0 = 位谕始of族日结统类高 + 2   '个数of连续最高波动小于0：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类是否BSHRL1 = 位谕始of族日结统类高 + 3   '是否最高波动小于1：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数单BSHRL1 = 位谕始of族日结统类高 + 4   '个数of最高波动小于1：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数双BSHRL1 = 位谕始of族日结统类高 + 5   '个数of连续最高波动小于0：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类是否BSHRL3 = 位谕始of族日结统类高 + 6   '是否最高波动小于2：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数单BSHRL3 = 位谕始of族日结统类高 + 7   '个数of最高波动小于2：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数双BSHRL3 = 位谕始of族日结统类高 + 8   '个数of连续最高波动小于0：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类是否BSHRL5 = 位谕始of族日结统类高 + 9   '是否最高波动小于2：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数单BSHRL5 = 位谕始of族日结统类高 + 10   '个数of最高波动小于2：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数双BSHRL5 = 位谕始of族日结统类高 + 11   '个数of连续最高波动小于0：仅针对日类（WBTCD>0 and WBTZC>0）
Public Const 位谕of日A类数单BSHRL0比 = 位谕始of族日结统类高 + 12
Public Const 位谕of日A类数单BSHRL1比 = 位谕始of族日结统类高 + 13
Public Const 位谕of日A类数单BSHRL3比 = 位谕始of族日结统类高 + 14
Public Const 位谕of日A类数单BSHRL5比 = 位谕始of族日结统类高 + 15
Public Const 位谕of日A类数非BSHRL0比 = 位谕始of族日结统类高 + 16
Public Const 位谕of日A类数非BSHRL1比 = 位谕始of族日结统类高 + 17
Public Const 位谕of日A类数非BSHRL3比 = 位谕始of族日结统类高 + 18
Public Const 位谕of日A类数非BSHRL5比 = 位谕始of族日结统类高 + 19
'-----------
Public Const 位谕终of族日结统 = 位谕始of族日结统类高 + 19






'已在调用处废弃，不会被调用。
'========================================================================================
'========================================================================================
'在核心单点基础上进行统计
'========================================================================================
'========================================================================================
Function STBASE结算引擎_单点统时核程( _
          ByRef ARROS As Variant _
        ) As Integer
'========================================================================================
'读取信息
'========================================================================================
                Dim 结收#, 结高#
                Dim 前收#
                前收 = ARROS(位os前收)
                结收 = ARROS(位os结收)
                结高 = ARROS(位os结高)
                '========================================================================
                Dim 结涨幅#, 结高幅#
                结涨幅 = ARROS(位os结幅PR0)
                结高幅 = ARROS(位os结幅HR0)
                '========================================================================
                Dim JZ#, JA#, JB#, JC#, JD#, JE#, JF#, JG#
                JZ = ARROS(位osJZ)
                JA = ARROS(位osJA)
                JB = ARROS(位osJB)
                JC = ARROS(位osJC)
                JD = ARROS(位osJD)
                JE = ARROS(位osJE)
                JF = ARROS(位osJF)
                JG = ARROS(位osJG)
'========================================================================================


'########################################################################################
'########################################################################################
'##################################      OS衍生      #####################################
'##################################   统计相关指标   #####################################
'########################################################################################
'########################################################################################
    '====================================================================================
    '衍生：统计系统
    '三个区域包含关系：C类区域 》 B类区域 》 A类区域
    '最重要均线为WJE，在其上添加别的均线
    '====================================================================================
    If ARROS(位os结期) >= "2012/1/1" Then
                '========================================================================
                '类别：区间相关（非均线相关）
                '========================================================================
                ARROS(位os统全数总) = ARROS(位os统全数总) + 1
                ARROS(位os统全复涨总) = (1 + ARROS(位os统全复涨总)) * (1 + 结涨幅 / 100) - 1
                ARROS(位os统全和涨总) = ARROS(位os统全和涨总) + 结涨幅
                ARROS(位os统全和高总) = ARROS(位os统全和高总) + 结高幅
                ARROS(位os统全数正) = ARROS(位os统全数正) + IIf(结涨幅 >= 0, 1, 0)
                ARROS(位os统全和涨正) = ARROS(位os统全和涨正) + IIf(结涨幅 >= 0, 结涨幅, 0)
                '========================================================================
                '类别：重要均线交叉计数
                '用途：用于剔除频繁交叉
                '========================================================================
                If ARROS(位os期类) = 常期类为周 Then
                        '-----------------------------------------
                        '选择CE的原因：是确认M1b的重要性，即WJC上穿WJE后开启主升浪
                        ARROS(位os统数交DE全) = ARROS(位os统数交DE全) + IIf(ARROS(位osBTDE) = 1, 1, 0)
                        '-----------------------------------------
                        '统计两种BC交叉数：一是全部交叉数；一是交叉时WJC大于WJE的交叉数（空中大洗盘假信号）
                        '统计CD、BC相交次数。用三个次数去除以【DE次数+1】.用以剔除过于频繁的股票
                        If ARROS(位osBTCD) = 1 Then
                            ARROS(位os统数交CD全) = ARROS(位os统数交CD全) + 1
                            If JD >= JE Then
                                ARROS(位os统数交CD震) = ARROS(位os统数交CD震) + 1
                            End If
                        End If
                        '-----------------------------------------
                        If ARROS(位osBTBC) = 1 Then
                            ARROS(位os统数交BC全) = ARROS(位os统数交BC全) + 1
                            If JD >= JE Then
                                ARROS(位os统数交BC震) = ARROS(位os统数交BC震) + 1
                            End If
                        End If
                        '-----------------------------------------
                        If ARROS(位os统值最正DE) < ARROS(位osBTCE) Then ARROS(位os统值最正DE) = ARROS(位osBTCE)
                        If ARROS(位os统值最负DE) > ARROS(位osBTCE) Then ARROS(位os统值最负DE) = ARROS(位osBTCE)
                        If ARROS(位os统值最正CD) < ARROS(位osBTAB) Then ARROS(位os统值最正CD) = ARROS(位osBTAB)
                        If ARROS(位os统值最负CD) > ARROS(位osBTAB) Then ARROS(位os统值最负CD) = ARROS(位osBTAB)
                        If ARROS(位os统值最正BC) < ARROS(位osBTZC) Then ARROS(位os统值最正BC) = ARROS(位osBTZC)
                        If ARROS(位os统值最负BC) > ARROS(位osBTZC) Then ARROS(位os统值最负BC) = ARROS(位osBTZC)
                        '-----------------------------------------
                End If
                '========================================================================
                '类别：重要均线区域类型
                '========================================================================
                Dim 是否C类周类 As Boolean
                Dim 是否B类周类 As Boolean
                Dim 是否A类周类 As Boolean
                '计数：全部符合C类的K柱
                是否C类周类 = IIf(ARROS(位os期类) = 常期类为周 And (JC >= JD), True, False)
                If 是否C类周类 = True Then
                    ARROS(位os统C类数总) = ARROS(位os统C类数总) + 1
                    ARROS(位os统C类数正) = ARROS(位os统C类数正) + IIf(结涨幅 >= 0, 1, 0)
                    ARROS(位os统C类和涨总) = ARROS(位os统C类和涨总) + 结涨幅
                    ARROS(位os统C类是否) = 1
                Else
                    ARROS(位os统C类是否) = 0
                End If
                '------------------------------------------------------------------------
                '计数：全部符合B类的K柱：这是现有【月类横操盘】的定义
                是否B类周类 = IIf(ARROS(位os期类) = 常期类为周 And (JC >= JD And JZ >= JD), True, False)
                If 是否B类周类 = True Then
                    ARROS(位os统B类数总) = ARROS(位os统B类数总) + 1
                    ARROS(位os统B类数正) = ARROS(位os统B类数正) + IIf(结涨幅 >= 0, 1, 0)
                    ARROS(位os统B类和涨总) = ARROS(位os统B类和涨总) + 结涨幅
                    '因为需要判断前后柱组合情况，所以把属性放到最后
                    ARROS(位os统B类是否) = 1
                Else
                    ARROS(位os统B类是否) = 0
                End If
                '------------------------------------------------------------------------
                '注意20220326：这是现有【周类横操盘】的定义，不要使用日类定义。将A类定义为ZE>0且CD>0且ZD>0
                是否A类周类 = IIf(ARROS(位os期类) = 常期类为周 And (JZ >= JE And JZ >= JD And JA >= JC), True, False)
                If 是否A类周类 = True Then
                    '---------------------------------------------------------------------
                    '统计计数
                    '---------------------------------------------------------------------
                    ARROS(位os统A类数总) = ARROS(位os统A类数总) + 1
                    ARROS(位os统A类数正) = ARROS(位os统A类数正) + IIf(结涨幅 >= 0, 1, 0)
                    '因为统计了（本柱）的结涨幅，所以不能基于（前柱）是否是A类进行判断
                    ARROS(位os统A类和涨总) = ARROS(位os统A类和涨总) + 结涨幅
                    ARROS(位os统A类和涨正) = ARROS(位os统A类和涨正) + IIf(结涨幅 >= 0, 结涨幅, 0)
                    ARROS(位os统A类和高总) = ARROS(位os统A类和高总) + 结高幅
                    '---------------------------------------------------------------------
                    '统计各局
                    '针对周类
                    '---------------------------------------------------------------------
                    '统计各局
                    If JZ <= JC Then
                        ARROS(位os统A类数子丙CZ总) = ARROS(位os统A类数子丙CZ总) + 1
                        ARROS(位os统A类数子丙CZ正) = ARROS(位os统A类数子丙CZ正) + IIf(结涨幅 >= 0, 1, 0)
                    ElseIf JZ <= JB Then
                        ARROS(位os统A类数子乙BZ总) = ARROS(位os统A类数子乙BZ总) + 1
                        ARROS(位os统A类数子乙BZ正) = ARROS(位os统A类数子乙BZ正) + IIf(结涨幅 >= 0, 1, 0)
                    Else
                        ARROS(位os统A类数子甲ZB总) = ARROS(位os统A类数子甲ZB总) + 1
                        ARROS(位os统A类数子甲ZB正) = ARROS(位os统A类数子甲ZB正) + IIf(结涨幅 >= 0, 1, 0)
                        If ARROS(位os局ZABC) = "2c" Then
                            ARROS(位os统A类数子2c) = ARROS(位os统A类数子2c) + 1
                        ElseIf ARROS(位os局ZABC) = "2d" Then
                            ARROS(位os统A类数子2d) = ARROS(位os统A类数子2d) + 1
                        ElseIf ARROS(位os局ZABC) = "2e" Then
                            ARROS(位os统A类数子2e) = ARROS(位os统A类数子2e) + 1
                        Else
                            ARROS(位os统A类数子余) = ARROS(位os统A类数子余) + 1
                        End If
                    End If
                    '---------------------------------------------------------------------
                    '最后：更新类型判断
                    ARROS(位os统A类是否) = 1
                Else
                    ARROS(位os统A类是否) = 0
                End If
                '========================================================================
                '类别：重要均线区域类型 相邻涨幅细分
                '========================================================================
                If 是否A类周类 = True Then
                    '---------------------------------------------------------------------
                    '统计：最高幅情况
                    '注意：数单对于L0/L1/L2/L3情况均为排斥，即各自类型分别计数
                    '注意：数双对于L0/L1/L2/L3情况均为排斥，即各自类型分别计数
                    '---------------------------------------------------------------------
                            '本周期最高点小于（前期收盘价）
                            If 结高 <= 前收 Then
                                '单数累加1
                                ARROS(位os统A类数单BSHRL0) = ARROS(位os统A类数单BSHRL0) + 1
                                '如果上期也是BSHRL0，则相邻数累加1
                                If ARROS(位os统A类是否BSHRL0) = 1 Then
                                    ARROS(位os统A类数双BSHRL0) = ARROS(位os统A类数双BSHRL0) + 1
                                ElseIf ARROS(位os统A类是否BSHRL1) = 1 Then
                                    ARROS(位os统A类数双BSHRL1) = ARROS(位os统A类数双BSHRL1) + 1
                                ElseIf ARROS(位os统A类是否BSHRL3) = 1 Then
                                    ARROS(位os统A类数双BSHRL3) = ARROS(位os统A类数双BSHRL3) + 1
                                ElseIf ARROS(位os统A类是否BSHRL5) = 1 Then
                                    ARROS(位os统A类数双BSHRL5) = ARROS(位os统A类数双BSHRL5) + 1
                                End If
                                '设置本期BSHRL
                                ARROS(位os统A类是否BSHRL0) = 1
                                ARROS(位os统A类是否BSHRL1) = 1
                                ARROS(位os统A类是否BSHRL3) = 1
                                ARROS(位os统A类是否BSHRL5) = 1
                            '-----------------------------------
                            '本周期最高点小于（前期收盘价*1.01）
                            ElseIf 结高 <= 前收 * 1.01 Then
                                '单数累加1
                                ARROS(位os统A类数单BSHRL1) = ARROS(位os统A类数单BSHRL1) + 1
                                '如果上期也是BSHRL1，则相邻数累加1
                                If ARROS(位os统A类是否BSHRL1) = 1 Then
                                    ARROS(位os统A类数双BSHRL1) = ARROS(位os统A类数双BSHRL1) + 1
                                ElseIf ARROS(位os统A类是否BSHRL3) = 1 Then
                                    ARROS(位os统A类数双BSHRL3) = ARROS(位os统A类数双BSHRL3) + 1
                                ElseIf ARROS(位os统A类是否BSHRL5) = 1 Then
                                    ARROS(位os统A类数双BSHRL5) = ARROS(位os统A类数双BSHRL5) + 1
                                End If
                                '设置本期BSHRL
                                ARROS(位os统A类是否BSHRL0) = 0
                                ARROS(位os统A类是否BSHRL1) = 1
                                ARROS(位os统A类是否BSHRL3) = 1
                                ARROS(位os统A类是否BSHRL5) = 1
                            '-----------------------------------
                            '本周期最高点小于（前期收盘价*1.03）
                            ElseIf 结高 <= 前收 * 1.03 Then
                                '单数累加1
                                ARROS(位os统A类数单BSHRL3) = ARROS(位os统A类数单BSHRL3) + 1
                                '如果上期也是BSHRL3，则相邻数累加1
                                If ARROS(位os统A类是否BSHRL3) = 1 Then
                                    ARROS(位os统A类数双BSHRL3) = ARROS(位os统A类数双BSHRL3) + 1
                                ElseIf ARROS(位os统A类是否BSHRL5) = 1 Then
                                    ARROS(位os统A类数双BSHRL5) = ARROS(位os统A类数双BSHRL5) + 1
                                End If
                                '设置本期BSHRL
                                ARROS(位os统A类是否BSHRL0) = 0
                                ARROS(位os统A类是否BSHRL1) = 0
                                ARROS(位os统A类是否BSHRL3) = 1
                                ARROS(位os统A类是否BSHRL5) = 1
                            '-----------------------------------
                            '本周期最高点小于（前期收盘价*1.05）
                            ElseIf 结高 <= 前收 * 1.05 Then
                                '单数累加1
                                ARROS(位os统A类数单BSHRL5) = ARROS(位os统A类数单BSHRL5) + 1
                                '如果上期也是BSHRL5，则相邻数累加1
                                If ARROS(位os统A类是否BSHRL5) = 1 Then
                                    ARROS(位os统A类数双BSHRL5) = ARROS(位os统A类数双BSHRL5) + 1
                                End If
                                '设置本期BSHRL
                                ARROS(位os统A类是否BSHRL0) = 0
                                ARROS(位os统A类是否BSHRL1) = 0
                                ARROS(位os统A类是否BSHRL3) = 0
                                ARROS(位os统A类是否BSHRL5) = 1
                            '-----------------------------------
                            Else
                                '设置本期BSHRL
                                ARROS(位os统A类是否BSHRL0) = 0
                                ARROS(位os统A类是否BSHRL1) = 0
                                ARROS(位os统A类是否BSHRL3) = 0
                                ARROS(位os统A类是否BSHRL5) = 0
                            End If
                    '---------------------------------------------------------------------
                End If
                '========================================================================
    End If
'########################################################################################
'##################################      OS衍生      #####################################
'##################################   统计相关指标   #####################################
'########################################################################################
'========================================================================================
'返回
'========================================================================================
        STBASE结算引擎_单点统时核程 = 1
End Function




'========================================================================================
'设置跨码信息（与单码跨时间相区别）
'后续将统计信息移到此过程
'========================================================================================
Function IQQQ跨码据擎_数程生成跨码基础( _
          谕组 As Variant _
        , 来组 As Variant _
        , Optional 基列 As Integer = 花列甲道 _
        ) As Integer
'========================================================================================
'声明变量
'========================================================================================
    Dim 基位日类 As Integer
    基位日类 = 基列 - 1
    Dim 基位周类 As Integer
    基位周类 = 基列 - 1 + 花宽单道
'========================================================================================
'设置跨码信息
'========================================================================================
    Dim X As Integer
    For X = LBound(来组, 1) To UBound(来组, 1)
    If UBCID是代码(来组(X, 基位日类 + 位os代码)) = True Then
        '################################################################################
        '################################################################################
        '重组：统计
        '是否拿到跨码全息生成之中（因为对于单码跨期所有信息都是一致的）
        '################################################################################
        '################################################################################
                '========================================================================
                '统计：周类
                '========================================================================
                谕组(X, 位谕of周类全数总) = 来组(X, 基位周类 + 位os统全数总)
                谕组(X, 位谕of周类全数正) = 来组(X, 基位周类 + 位os统全数正)
                If 谕组(X, 位谕of周类全数总) > 0 Then
                    谕组(X, 位谕of周类比正总) = Round(来组(X, 基位周类 + 位os统全数正) / 谕组(X, 位谕of周类全数总), 2)
                End If
                谕组(X, 位谕of周类全复涨总) = Round(来组(X, 基位周类 + 位os统全复涨总), 2)
                谕组(X, 位谕of周类全和高总) = Round(来组(X, 基位周类 + 位os统全和高总), 2)
                谕组(X, 位谕of周类全和涨正) = Round(来组(X, 基位周类 + 位os统全和涨正), 2)
                '-------------------------------------------------
                谕组(X, 位谕of周类数交BC震) = 来组(X, 基位周类 + 位os统数交BC震)
                谕组(X, 位谕of周类数交CD震) = 来组(X, 基位周类 + 位os统数交CD震)
                谕组(X, 位谕of周类数交DE全) = 来组(X, 基位周类 + 位os统数交DE全)
                '统计小波动的比例
                谕组(X, 位谕of周类比交总BC2DE) = Round(谕组(X, 位谕of周类数交BC震) / (1 + 谕组(X, 位谕of周类数交DE全)), 1)
                谕组(X, 位谕of周类比交总CD2DE) = Round(谕组(X, 位谕of周类数交CD震) / (1 + 谕组(X, 位谕of周类数交DE全)), 1)
                '统计波动的持续时间
                谕组(X, 位谕of周类值最正BC) = 来组(X, 基位周类 + 位os统值最正BC)
                谕组(X, 位谕of周类值最负BC) = 来组(X, 基位周类 + 位os统值最负BC)
                谕组(X, 位谕of周类值最正CD) = 来组(X, 基位周类 + 位os统值最正CD)
                谕组(X, 位谕of周类值最负CD) = 来组(X, 基位周类 + 位os统值最负CD)
                谕组(X, 位谕of周类值最正DE) = 来组(X, 基位周类 + 位os统值最正DE)
                谕组(X, 位谕of周类值最负DE) = 来组(X, 基位周类 + 位os统值最负DE)
                '-------------------------------------------------
                谕组(X, 位谕of周C类是否) = 来组(X, 基位周类 + 位os统C类是否)
                谕组(X, 位谕of周B类是否) = 来组(X, 基位周类 + 位os统B类是否)
                谕组(X, 位谕of周A类是否) = 来组(X, 基位周类 + 位os统A类是否)
                谕组(X, 位谕of周C类数总) = 来组(X, 基位周类 + 位os统C类数总)
                谕组(X, 位谕of周B类数总) = 来组(X, 基位周类 + 位os统B类数总)
                谕组(X, 位谕of周A类数总) = 来组(X, 基位周类 + 位os统A类数总)
                If 谕组(X, 位谕of周类全数总) > 0 Then
                    谕组(X, 位谕of周C类比类全) = Round(来组(X, 基位周类 + 位os统C类数总) / 谕组(X, 位谕of周类全数总), 2)
                    谕组(X, 位谕of周B类比类全) = Round(来组(X, 基位周类 + 位os统B类数总) / 谕组(X, 位谕of周类全数总), 2)
                    谕组(X, 位谕of周A类比类全) = Round(来组(X, 基位周类 + 位os统A类数总) / 谕组(X, 位谕of周类全数总), 2)
                End If
                If 来组(X, 基位周类 + 位os统C类数总) > 0 Then
                    谕组(X, 位谕of周C类比正类) = Round(来组(X, 基位周类 + 位os统C类数正) / 来组(X, 基位周类 + 位os统C类数总), 2)
                    谕组(X, 位谕of周C类均涨总) = Round(来组(X, 基位周类 + 位os统C类和涨总) / 来组(X, 基位周类 + 位os统C类数总), 2)
                End If
                If 来组(X, 基位周类 + 位os统B类数总) > 0 Then
                    谕组(X, 位谕of周B类比正类) = Round(来组(X, 基位周类 + 位os统B类数正) / 来组(X, 基位周类 + 位os统B类数总), 2)
                    谕组(X, 位谕of周B类均涨总) = Round(来组(X, 基位周类 + 位os统B类和涨总) / 来组(X, 基位周类 + 位os统B类数总), 2)
                End If
                If 来组(X, 基位周类 + 位os统A类数总) > 0 Then
                    谕组(X, 位谕of周A类比正类) = Round(来组(X, 基位周类 + 位os统A类数正) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类均涨总) = Round(来组(X, 基位周类 + 位os统A类和涨总) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类均高总) = Round(来组(X, 基位周类 + 位os统A类和高总) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    '统计：各种周局的分布
                    谕组(X, 位谕of周A类比类子甲ZB总) = Round(来组(X, 基位周类 + 位os统A类数子甲ZB总) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类比类子乙BZ总) = Round(来组(X, 基位周类 + 位os统A类数子乙BZ总) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类比类子丙CZ总) = Round(来组(X, 基位周类 + 位os统A类数子丙CZ总) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类比类子2c) = Round(来组(X, 基位周类 + 位os统A类数子2c) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类比类子2d) = Round(来组(X, 基位周类 + 位os统A类数子2d) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类比类子2e) = Round(来组(X, 基位周类 + 位os统A类数子2e) / 来组(X, 基位周类 + 位os统A类数总), 2)
                End If
                If 来组(X, 基位周类 + 位os统A类数子甲ZB总) > 0 Then     '统计A类甲子类中阳柱占比
                    谕组(X, 位谕of周A类比例子甲ZB正) = Round(来组(X, 基位周类 + 位os统A类数子甲ZB正) / 来组(X, 基位周类 + 位os统A类数子甲ZB总), 2)
                End If
                If 来组(X, 基位周类 + 位os统A类数正) > 0 Then     '统计A类阳柱中各类占比
                    谕组(X, 位谕of周A类比正子甲ZB正) = Round((来组(X, 基位周类 + 位os统A类数子甲ZB正)) / 来组(X, 基位周类 + 位os统A类数正), 2)
                    谕组(X, 位谕of周A类比正子2c) = Round(来组(X, 基位周类 + 位os统A类数子2c) / 来组(X, 基位周类 + 位os统A类数正), 2)
                End If
                If 来组(X, 基位周类 + 位os统A类数正) > 0 Then     '统计阳柱的平均涨幅
                    谕组(X, 位谕of周A类均涨正) = Round(来组(X, 基位周类 + 位os统A类和涨正) / 来组(X, 基位周类 + 位os统A类数正), 2)
                End If
                If 来组(X, 基位周类 + 位os统A类数总) - 来组(X, 基位周类 + 位os统A类数正) > 0 Then     '统计阴柱的平均涨幅
                    谕组(X, 位谕of周A类均涨负) = Round((来组(X, 基位周类 + 位os统A类和涨总) - 来组(X, 基位周类 + 位os统A类和涨正)) / (来组(X, 基位周类 + 位os统A类数总) - 来组(X, 基位周类 + 位os统A类数正)), 2)
                End If
                '-------------------------------------------------
                谕组(X, 位谕of周A类是否BSHRL0) = 来组(X, 基位周类 + 位os统A类是否BSHRL0)
                谕组(X, 位谕of周A类数单BSHRL0) = 来组(X, 基位周类 + 位os统A类数单BSHRL0)
                谕组(X, 位谕of周A类数双BSHRL0) = 来组(X, 基位周类 + 位os统A类数双BSHRL0)
                谕组(X, 位谕of周A类是否BSHRL1) = 来组(X, 基位周类 + 位os统A类是否BSHRL1)
                谕组(X, 位谕of周A类数单BSHRL1) = 来组(X, 基位周类 + 位os统A类数单BSHRL1)
                谕组(X, 位谕of周A类数双BSHRL1) = 来组(X, 基位周类 + 位os统A类数双BSHRL1)
                谕组(X, 位谕of周A类是否BSHRL3) = 来组(X, 基位周类 + 位os统A类是否BSHRL3)
                谕组(X, 位谕of周A类数单BSHRL3) = 来组(X, 基位周类 + 位os统A类数单BSHRL3)
                谕组(X, 位谕of周A类数双BSHRL3) = 来组(X, 基位周类 + 位os统A类数双BSHRL3)
                谕组(X, 位谕of周A类是否BSHRL5) = 来组(X, 基位周类 + 位os统A类是否BSHRL5)
                谕组(X, 位谕of周A类数单BSHRL5) = 来组(X, 基位周类 + 位os统A类数单BSHRL5)
                谕组(X, 位谕of周A类数双BSHRL5) = 来组(X, 基位周类 + 位os统A类数双BSHRL5)
                If 来组(X, 基位周类 + 位os统A类数总) > 0 Then
                    谕组(X, 位谕of周A类数单BSHRL0比) = Round(来组(X, 基位周类 + 位os统A类数单BSHRL0) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类数单BSHRL1比) = Round(来组(X, 基位周类 + 位os统A类数单BSHRL1) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类数单BSHRL3比) = Round(来组(X, 基位周类 + 位os统A类数单BSHRL3) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类数单BSHRL5比) = Round(来组(X, 基位周类 + 位os统A类数单BSHRL5) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类数非BSHRL0比) = Round((来组(X, 基位周类 + 位os统A类数总) - (来组(X, 基位周类 + 位os统A类数单BSHRL0))) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类数非BSHRL1比) = Round((来组(X, 基位周类 + 位os统A类数总) - (来组(X, 基位周类 + 位os统A类数单BSHRL1) + 来组(X, 基位周类 + 位os统A类数单BSHRL0))) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类数非BSHRL3比) = Round((来组(X, 基位周类 + 位os统A类数总) - (来组(X, 基位周类 + 位os统A类数单BSHRL3) + 来组(X, 基位周类 + 位os统A类数单BSHRL1) + 来组(X, 基位周类 + 位os统A类数单BSHRL0))) / 来组(X, 基位周类 + 位os统A类数总), 2)
                    谕组(X, 位谕of周A类数非BSHRL5比) = Round((来组(X, 基位周类 + 位os统A类数总) - (来组(X, 基位周类 + 位os统A类数单BSHRL5) + 来组(X, 基位周类 + 位os统A类数单BSHRL3) + 来组(X, 基位周类 + 位os统A类数单BSHRL1) + 来组(X, 基位周类 + 位os统A类数单BSHRL0))) / 来组(X, 基位周类 + 位os统A类数总), 2)
                End If
                '========================================================================
                '统计：日类
                '========================================================================
                谕组(X, 位谕of日类全数总) = 来组(X, 基位日类 + 位os统全数总)
                谕组(X, 位谕of日类全数正) = 来组(X, 基位日类 + 位os统全数正)
                If 谕组(X, 位谕of日类全数总) > 0 Then
                    谕组(X, 位谕of日类比正总) = Round(来组(X, 基位日类 + 位os统全数正) / 谕组(X, 位谕of日类全数总), 2)
                End If
                谕组(X, 位谕of日类全复涨总) = Round(来组(X, 基位日类 + 位os统全复涨总), 2)
                谕组(X, 位谕of日类全和涨正) = Round(来组(X, 基位日类 + 位os统全和涨正), 2)
                谕组(X, 位谕of日类全和高总) = Round(来组(X, 基位日类 + 位os统全和高总), 2)
                '-------------------------------------------------
                谕组(X, 位谕of日C类是否) = 来组(X, 基位日类 + 位os统C类是否)
                谕组(X, 位谕of日B类是否) = 来组(X, 基位日类 + 位os统B类是否)
                谕组(X, 位谕of日A类是否) = 来组(X, 基位日类 + 位os统A类是否)
                谕组(X, 位谕of日C类数总) = 来组(X, 基位日类 + 位os统C类数总)
                谕组(X, 位谕of日B类数总) = 来组(X, 基位日类 + 位os统B类数总)
                谕组(X, 位谕of日A类数总) = 来组(X, 基位日类 + 位os统A类数总)
                If 谕组(X, 位谕of日类全数总) > 0 Then
                    谕组(X, 位谕of日C类比类全) = Round(来组(X, 基位日类 + 位os统C类数总) / 谕组(X, 位谕of日类全数总), 2)
                    谕组(X, 位谕of日B类比类全) = Round(来组(X, 基位日类 + 位os统B类数总) / 谕组(X, 位谕of日类全数总), 2)
                    谕组(X, 位谕of日A类比类全) = Round(来组(X, 基位日类 + 位os统A类数总) / 谕组(X, 位谕of日类全数总), 2)
                End If
                If 来组(X, 基位日类 + 位os统C类数总) > 0 Then
                    谕组(X, 位谕of日C类比正类) = Round(来组(X, 基位日类 + 位os统C类数正) / 来组(X, 基位日类 + 位os统C类数总), 2)
                    谕组(X, 位谕of日C类均涨总) = Round(来组(X, 基位日类 + 位os统C类和涨总) / 来组(X, 基位日类 + 位os统C类数总), 2)
                End If
                If 来组(X, 基位日类 + 位os统B类数总) > 0 Then
                    谕组(X, 位谕of日B类比正类) = Round(来组(X, 基位日类 + 位os统B类数正) / 来组(X, 基位日类 + 位os统B类数总), 2)
                    谕组(X, 位谕of日B类均涨总) = Round(来组(X, 基位日类 + 位os统B类和涨总) / 来组(X, 基位日类 + 位os统B类数总), 2)
                End If
                If 来组(X, 基位日类 + 位os统A类数总) > 0 Then
                    谕组(X, 位谕of日A类比正类) = Round(来组(X, 基位日类 + 位os统A类数正) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类均涨总) = Round(来组(X, 基位日类 + 位os统A类和涨总) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类均高总) = Round(来组(X, 基位日类 + 位os统A类和高总) / 来组(X, 基位日类 + 位os统A类数总), 2)
                End If
                '-------------------------------------------------
                谕组(X, 位谕of日A类是否BSHRL0) = 来组(X, 基位日类 + 位os统A类是否BSHRL0)
                谕组(X, 位谕of日A类数单BSHRL0) = 来组(X, 基位日类 + 位os统A类数单BSHRL0)
                谕组(X, 位谕of日A类数双BSHRL0) = 来组(X, 基位日类 + 位os统A类数双BSHRL0)
                谕组(X, 位谕of日A类是否BSHRL1) = 来组(X, 基位日类 + 位os统A类是否BSHRL1)
                谕组(X, 位谕of日A类数单BSHRL1) = 来组(X, 基位日类 + 位os统A类数单BSHRL1)
                谕组(X, 位谕of日A类数双BSHRL1) = 来组(X, 基位日类 + 位os统A类数双BSHRL1)
                谕组(X, 位谕of日A类是否BSHRL3) = 来组(X, 基位日类 + 位os统A类是否BSHRL3)
                谕组(X, 位谕of日A类数单BSHRL3) = 来组(X, 基位日类 + 位os统A类数单BSHRL3)
                谕组(X, 位谕of日A类数双BSHRL3) = 来组(X, 基位日类 + 位os统A类数双BSHRL3)
                谕组(X, 位谕of日A类是否BSHRL5) = 来组(X, 基位日类 + 位os统A类是否BSHRL5)
                谕组(X, 位谕of日A类数单BSHRL5) = 来组(X, 基位日类 + 位os统A类数单BSHRL5)
                谕组(X, 位谕of日A类数双BSHRL5) = 来组(X, 基位日类 + 位os统A类数双BSHRL5)
                If 来组(X, 基位日类 + 位os统A类数总) > 0 Then
                    谕组(X, 位谕of日A类数单BSHRL0比) = Round(来组(X, 基位日类 + 位os统A类数单BSHRL0) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类数单BSHRL1比) = Round(来组(X, 基位日类 + 位os统A类数单BSHRL1) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类数单BSHRL3比) = Round(来组(X, 基位日类 + 位os统A类数单BSHRL3) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类数单BSHRL5比) = Round(来组(X, 基位日类 + 位os统A类数单BSHRL5) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类数非BSHRL0比) = Round((来组(X, 基位日类 + 位os统A类数总) - (来组(X, 基位日类 + 位os统A类数单BSHRL0))) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类数非BSHRL1比) = Round((来组(X, 基位日类 + 位os统A类数总) - (来组(X, 基位日类 + 位os统A类数单BSHRL1) + 来组(X, 基位日类 + 位os统A类数单BSHRL0))) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类数非BSHRL3比) = Round((来组(X, 基位日类 + 位os统A类数总) - (来组(X, 基位日类 + 位os统A类数单BSHRL3) + 来组(X, 基位日类 + 位os统A类数单BSHRL1) + 来组(X, 基位日类 + 位os统A类数单BSHRL0))) / 来组(X, 基位日类 + 位os统A类数总), 2)
                    谕组(X, 位谕of日A类数非BSHRL5比) = Round((来组(X, 基位日类 + 位os统A类数总) - (来组(X, 基位日类 + 位os统A类数单BSHRL5) + 来组(X, 基位日类 + 位os统A类数单BSHRL3) + 来组(X, 基位日类 + 位os统A类数单BSHRL1) + 来组(X, 基位日类 + 位os统A类数单BSHRL0))) / 来组(X, 基位日类 + 位os统A类数总), 2)
                End If
                '========================================================================
    End If
    Next
'========================================================================================
'返回
'========================================================================================
    IQQQ跨码据擎_数程生成跨码基础 = UBound(谕组, 1) - LBound(谕组, 1) + 1
End Function







Function IQQQ跨码展擎_按列神谕区域跨码( _
          WS As Worksheet _
        , Optional 基列 As Integer = 1 _
        , Optional 基行 As Integer = 1 _
        ) As Integer
'========================================================================================
'格式化：全局
'========================================================================================
    With WS.Cells(基行, 基列).Cells(1, 位谕列始全部).Resize(1, 位谕列终全部 - 位谕列始全部 + 1).EntireColumn
        .RowHeight = 12
    End With
    '------------------------------------------------------------------------------------
    '列
    '------------------------------------------------------------------------------------
    '列宽：全部
    With WS.Cells(基行, 基列).Cells(1, 位谕列始全部).Resize(1, 位谕列终全部 - 位谕列始全部 + 1).EntireColumn
        .ColumnWidth = 3
        .HorizontalAlignment = xlCenter
        .NumberFormatLocal = "0_);[蓝色](0)"
        .Interior.ColorIndex = 35
    End With
    '------------------------------------------------------------------------------------
    '首行
    '------------------------------------------------------------------------------------
    With WS.Cells(基行, 基列)
        .Cells(1, 位谕列终全部) = "占位"
    End With
'========================================================================================
'格式化：周类统计
'========================================================================================
    '------------------------------------------------------------------------------------
    '首行
    '------------------------------------------------------------------------------------
    With WS.Cells(基行, 基列)
        .Cells(1, 位谕of周类比正总) = "%阳全" & vbCrLf & "周"
        
        .Cells(1, 位谕of周A类比类全) = "%A" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类比正类) = "A%阳" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类均涨总) = "均涨总" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类均高总) = "均高总" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类均涨正) = "均涨正" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类均涨负) = "均涨负" & vbCrLf & "周A类"
        
        .Cells(1, 位谕of周A类比正子甲ZB正) = "正甲比" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类比正子2c) = "正2c比" & vbCrLf & "周A类"
        
        .Cells(1, 位谕of周A类比类子2c) = "2c总比" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类比类子2d) = "2d总比" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类比类子2e) = "2e总比" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类比例子甲ZB正) = "甲正比" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类比类子甲ZB总) = "甲总比" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类比类子乙BZ总) = "乙总比" & vbCrLf & "周A类"
        .Cells(1, 位谕of周A类比类子丙CZ总) = "丙总比" & vbCrLf & "周A类"
        
        .Cells(1, 位谕of周类数交DE全) = "#DE" & vbCrLf & "周"
        .Cells(1, 位谕of周类数交CD震) = "#AB" & vbCrLf & "周"
        .Cells(1, 位谕of周类数交BC震) = "#ZC" & vbCrLf & "周"
        .Cells(1, 位谕of周类比交总CD2DE) = "%AC" & vbCrLf & "周"
        .Cells(1, 位谕of周类比交总BC2DE) = "%ZC" & vbCrLf & "周"
    End With
    '------------------------------------------------------------------------------------
    '列：边框
    '------------------------------------------------------------------------------------
    With WS.Columns(基列)
        With .Columns(位谕始of族周结统).Borders(xlEdgeLeft)
           .Color = 常色主黑
           .Weight = xlMedium
        End With
        With .Columns(位谕终of族周结统).Borders(xlEdgeRight)
           .Color = 常色主黑
           .Weight = xlMedium
        End With
            '-------------------------------------
            With .Columns(位谕始of族周结统类均).Borders(xlEdgeLeft)
                .Color = 常色主碧
                .Weight = xlMedium
            End With
            With .Columns(位谕始of族周结统类区).Borders(xlEdgeLeft)
                .Color = 常色主碧
                .Weight = xlMedium
            End With
            With .Columns(位谕始of族周结统类高).Borders(xlEdgeLeft)
                .Color = 常色主碧
                .Weight = xlMedium
            End With
            '-------------------------------------
            With .Columns(位谕of周类全数总).Borders(xlEdgeRight)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            '-------------------------------------
            With .Columns(位谕of周C类数总).Borders(xlEdgeLeft)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of周B类数总).Borders(xlEdgeLeft)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of周A类数总).Borders(xlEdgeLeft)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of周C类是否).Borders(xlEdgeLeft)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            '-------------------------------------
            With .Columns(位谕of周A类数双BSHRL0).Borders(xlEdgeRight)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of周A类数双BSHRL1).Borders(xlEdgeRight)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of周A类数双BSHRL3).Borders(xlEdgeRight)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            '-------------------------------------
            With .Columns(位谕of周A类数单BSHRL0比).Borders(xlEdgeLeft)
                .Color = 常色四靛
                .Weight = xlThin
            End With
            With .Columns(位谕of周A类数非BSHRL0比).Borders(xlEdgeLeft)
                .Color = 常色四靛
                .Weight = xlThin
            End With
    End With
    '------------------------------------------------------------------------------------
    '列：显示
    '------------------------------------------------------------------------------------
    With WS.Cells(基行, 基列).Cells(1, 位谕始of族周结统).Resize(1, 位谕终of族周结统 - 位谕始of族周结统 + 1).EntireColumn
        .HorizontalAlignment = xlRight
        .Interior.ColorIndex = 16
        .NumberFormatLocal = "0_);[蓝色](0)"
        .ColumnWidth = 3
        .Font.Size = 9
    End With
    With WS.Columns(基列)
        '-------------------------------------
        .Columns(位谕of周类全数总).ColumnWidth = 4

        .Columns(位谕of周类值最正BC).ColumnWidth = 4
        .Columns(位谕of周类值最负BC).ColumnWidth = 4
        .Columns(位谕of周类值最正CD).ColumnWidth = 4
        .Columns(位谕of周类值最负CD).ColumnWidth = 4
        .Columns(位谕of周类值最正DE).ColumnWidth = 4
        .Columns(位谕of周类值最负DE).ColumnWidth = 4
        '-------------------------------------
        .Columns(位谕of周类比正总).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周类全数正).ColumnWidth = 4
        .Columns(位谕of周类全复涨总).ColumnWidth = 4
        .Columns(位谕of周类全和涨正).ColumnWidth = 5
        .Columns(位谕of周类全和高总).ColumnWidth = 5
        '-------------------------------------
        .Columns(位谕of周C类比类全).ColumnWidth = 4
        .Columns(位谕of周C类比类全).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周C类比正类).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周C类均涨总).NumberFormatLocal = 全设格式of零位

        .Columns(位谕of周B类比类全).ColumnWidth = 4
        .Columns(位谕of周B类比类全).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周B类比正类).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周B类均涨总).NumberFormatLocal = 全设格式of零位

        .Columns(位谕of周A类比类全).ColumnWidth = 4
        .Columns(位谕of周A类比类全).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比正类).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类均涨总).NumberFormatLocal = 全设格式of零位
        .Columns(位谕of周A类均高总).NumberFormatLocal = 全设格式of零位
        .Columns(位谕of周A类均涨正).NumberFormatLocal = 全设格式of零位
        .Columns(位谕of周A类均涨负).NumberFormatLocal = 全设格式of零位
        '-------------------------------------
        .Columns(位谕of周A类比例子甲ZB正).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比例子甲ZB正).Interior.ColorIndex = 36
        .Columns(位谕of周A类比正子甲ZB正).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比正子甲ZB正).Interior.ColorIndex = 37
        .Columns(位谕of周A类比正子2c).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比正子2c).Interior.ColorIndex = 37
        .Columns(位谕of周A类比类子2c).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比类子2d).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比类子2e).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比类子甲ZB总).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比类子乙BZ总).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类比类子丙CZ总).NumberFormatLocal = 全设格式of百分
        '-------------------------------------
        .Columns(位谕of周A类数单BSHRL0比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类数单BSHRL1比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类数单BSHRL3比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类数单BSHRL5比).NumberFormatLocal = 全设格式of百分

        .Columns(位谕of周A类数非BSHRL0比).ColumnWidth = 4
        .Columns(位谕of周A类数非BSHRL1比).ColumnWidth = 4
        .Columns(位谕of周A类数非BSHRL3比).ColumnWidth = 4
        .Columns(位谕of周A类数非BSHRL5比).ColumnWidth = 4
        .Columns(位谕of周A类数非BSHRL0比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类数非BSHRL1比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类数非BSHRL3比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of周A类数非BSHRL5比).NumberFormatLocal = 全设格式of百分
        '-------------------------------------
    End With
    With WS.Cells(基行, 基列).Cells(1, 位谕始of族周结统).Resize(1, 位谕终of族周结统 - 位谕始of族周结统 + 1).EntireColumn
        .Hidden = True
    End With
    With WS.Columns(基列)
        .Columns(位谕of周A类比类全).Hidden = False
        .Columns(位谕of周A类比正类).Hidden = False
        
        .Columns(位谕of周A类均涨总).Hidden = False
        .Columns(位谕of周A类均涨正).Hidden = False
        .Columns(位谕of周A类均涨负).Hidden = False
        .Columns(位谕of周A类均高总).Hidden = False
        
        .Columns(位谕of周A类比正子甲ZB正).Hidden = False
        .Columns(位谕of周A类比正子2c).Hidden = False
        .Columns(位谕of周A类比例子甲ZB正).Hidden = False
        
        .Columns(位谕of周A类比类子2c).Hidden = False
        .Columns(位谕of周A类比类子2d).Hidden = False
        .Columns(位谕of周A类比类子2e).Hidden = False
        .Columns(位谕of周A类比类子甲ZB总).Hidden = False
        .Columns(位谕of周A类比类子乙BZ总).Hidden = False
        .Columns(位谕of周A类比类子丙CZ总).Hidden = False
    End With
    With WS.Cells(基行, 基列).Cells(1, 位谕始of族周结统).Resize(1, 位谕终of族周结统 - 位谕始of族周结统 + 1).EntireColumn
        .Hidden = True
    End With
'========================================================================================
'格式化：日类统计
'========================================================================================
    '------------------------------------------------------------------------------------
    '首行
    '------------------------------------------------------------------------------------
    With WS.Cells(基行, 基列)
        .Cells(1, 位谕of日A类数非BSHRL0比) = "H0" & vbCrLf & "日"
        .Cells(1, 位谕of日A类数非BSHRL1比) = "H1" & vbCrLf & "日"
        .Cells(1, 位谕of日A类数非BSHRL3比) = "H3" & vbCrLf & "日"
        .Cells(1, 位谕of日A类数非BSHRL5比) = "H5" & vbCrLf & "日"
    End With
    '------------------------------------------------------------------------------------
    '列：边框
    '------------------------------------------------------------------------------------
    With WS.Columns(基列)
        With .Columns(位谕始of族日结统).Borders(xlEdgeLeft)
           .Color = 常色主黑
           .Weight = xlMedium
        End With
        With .Columns(位谕终of族日结统).Borders(xlEdgeRight)
           .Color = 常色主黑
           .Weight = xlMedium
        End With
            '-------------------------------------
            With .Columns(位谕始of族日结统类区).Borders(xlEdgeLeft)
                .Color = 常色主碧
                .Weight = xlMedium
            End With
            With .Columns(位谕始of族日结统类高).Borders(xlEdgeLeft)
                .Color = 常色主碧
                .Weight = xlMedium
            End With
            '-------------------------------------
            With .Columns(位谕of日类全数总).Borders(xlEdgeRight)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            '-------------------------------------
            With .Columns(位谕of日C类数总).Borders(xlEdgeLeft)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of日B类数总).Borders(xlEdgeLeft)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of日A类数总).Borders(xlEdgeLeft)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of日C类是否).Borders(xlEdgeLeft)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            '-------------------------------------
            With .Columns(位谕of日A类数双BSHRL0).Borders(xlEdgeRight)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of日A类数双BSHRL1).Borders(xlEdgeRight)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            With .Columns(位谕of日A类数双BSHRL3).Borders(xlEdgeRight)
                .Color = 常色八绿
                .Weight = xlThin
            End With
            '-------------------------------------
            With .Columns(位谕of日A类数单BSHRL0比).Borders(xlEdgeLeft)
                .Color = 常色四靛
                .Weight = xlThin
            End With
            With .Columns(位谕of日A类数非BSHRL0比).Borders(xlEdgeLeft)
                .Color = 常色四靛
                .Weight = xlThin
            End With
    End With
    '------------------------------------------------------------------------------------
    '列：显示
    '------------------------------------------------------------------------------------
    With WS.Cells(基行, 基列).Cells(1, 位谕始of族日结统).Resize(1, 位谕终of族日结统 - 位谕始of族日结统 + 1).EntireColumn
        .HorizontalAlignment = xlRight
        .Interior.ColorIndex = 15
        .NumberFormatLocal = "0_);[蓝色](0)"
        .ColumnWidth = 3
        .Font.Size = 9
    End With
    With WS.Columns(基列)
        .Columns(位谕of日类全数总).ColumnWidth = 4

'        .Columns(位谕of日类值最正ZE).ColumnWidth = 4
'        .Columns(位谕of日类值最负ZE).ColumnWidth = 4
'        .Columns(位谕of日类值最正ZC).ColumnWidth = 4
'        .Columns(位谕of日类值最负ZC).ColumnWidth = 4
'        .Columns(位谕of日类值最正CD).ColumnWidth = 4
'        .Columns(位谕of日类值最负CD).ColumnWidth = 4

        .Columns(位谕of日类比正总).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日类全数正).ColumnWidth = 4
        .Columns(位谕of日类全复涨总).ColumnWidth = 4
        .Columns(位谕of日类全和涨正).ColumnWidth = 5
        .Columns(位谕of日类全和高总).ColumnWidth = 5


        .Columns(位谕of日A类比类全).ColumnWidth = 4
        .Columns(位谕of日A类比类全).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日A类比正类).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日A类均涨总).NumberFormatLocal = 全设格式of零位

        .Columns(位谕of日B类比类全).ColumnWidth = 4
        .Columns(位谕of日B类比类全).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日B类比正类).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日B类均涨总).NumberFormatLocal = 全设格式of零位

        .Columns(位谕of日C类比类全).ColumnWidth = 4
        .Columns(位谕of日C类比类全).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日C类比正类).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日C类均涨总).NumberFormatLocal = 全设格式of零位


        .Columns(位谕of日A类数单BSHRL0比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日A类数单BSHRL1比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日A类数单BSHRL3比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日A类数单BSHRL5比).NumberFormatLocal = 全设格式of百分

        .Columns(位谕of日A类数非BSHRL0比).ColumnWidth = 3
        .Columns(位谕of日A类数非BSHRL1比).ColumnWidth = 3
        .Columns(位谕of日A类数非BSHRL3比).ColumnWidth = 3
        .Columns(位谕of日A类数非BSHRL5比).ColumnWidth = 3
        .Columns(位谕of日A类数非BSHRL0比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日A类数非BSHRL1比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日A类数非BSHRL3比).NumberFormatLocal = 全设格式of百分
        .Columns(位谕of日A类数非BSHRL5比).NumberFormatLocal = 全设格式of百分
    End With
    With WS.Cells(基行, 基列).Cells(1, 位谕始of族日结统).Resize(1, 位谕终of族日结统 - 位谕始of族日结统 + 1).EntireColumn
        .Hidden = True
    End With
'    With WS.Columns(基列)
'        .Columns(位谕of日A类数非BSHRL0比).Hidden = False
'        .Columns(位谕of日A类数非BSHRL1比).Hidden = False
'        .Columns(位谕of日A类数非BSHRL3比).Hidden = False
'        .Columns(位谕of日A类数非BSHRL5比).Hidden = False
'    End With
'========================================================================================
'返回
'========================================================================================
End Function




