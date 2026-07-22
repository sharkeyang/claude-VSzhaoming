import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

with open('昭明计划VS优化_vba/PX算研_ZSM交割单.bas', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the section to replace: from "反向递推（从最新到最旧）" to the end of the output loop
old_start = '        \' 反向递推（从最新到最旧）'
old_end = '        Next\n        跳过:'

start_idx = content.find(old_start)
end_idx = content.find(old_end, start_idx) + len(old_end)

if start_idx < 0 or end_idx < len(old_end):
    print(f'Could not find boundaries: start={start_idx}, end={end_idx}')
    sys.exit(1)

new_code = """        ' 计算净余和持仓量
        Dim 净余 As Double
        净余 = 0
        For 交易索引 = 1 To 计数
            R = 交易行(交易索引)
            qty = Val(ARRYM(R, 8))
            类别r = ARRYM(R, 6)
            If VarType(类别r) = vbString Then
                类别r = Replace(类别r, "=", "")
                类别r = Replace(类别r, \"\"\"\", "")
            End If
            If 类别r = "买入" Then 净余 = 净余 + qty Else 净余 = 净余 - qty
        Next
        Dim 老仓 As Double
        老仓 = 持仓量 - 净余
        ' 输出该股票结果
        Dim 名称 As String
        名称 = Trim(ARRYM(交易行(1), 5))
        WS出.Cells(行号, 1) = sCIDL
        WS出.Cells(行号, 2) = 名称
        WS出.Cells(行号, 3) = 持仓量
        WS出.Cells(行号, 4) = "---"
        WS出.Cells(行号, 5) = "---"
        WS出.Cells(行号, 6) = "---"
        WS出.Cells(行号, 7) = "---"
        WS出.Cells(行号, 8) = "汇总"
        WS出.Rows(行号).Font.Bold = True
        行号 = 行号 + 1
        总完整 = 总完整 + 1
        ' 从最旧到最新遍历，标记未配对交易
        Dim 待中和 As Double
        待中和 = 老仓
        Dim 标记 As String
        For 交易索引 = 1 To 计数
            r = 交易行(交易索引)
            qty = Val(ARRYM(r, 8))
            类别r = ARRYM(r, 6)
            If VarType(类别r) = vbString Then
                类别r = Replace(类别r, "=", "")
                类别r = Replace(类别r, \"\"\"\", "")
            End If
            ' 决定标记
            If 待中和 > 0 And 类别r = "卖出" Then
                ' 卖出是在平老仓
                If qty <= 待中和 Then
                    标记 = "未配对交易"
                    待中和 = 待中和 - qty
                Else
                    ' 拆分卖出：待中和(未配对) + 剩余(配对)
                    ' 先输出未配对部分
                    WS出.Cells(行号, 3) = ""
                    WS出.Cells(行号, 4) = ARRYM(r, 1)
                    WS出.Cells(行号, 5) = 类别r
                    WS出.Cells(行号, 6) = 待中和
                    WS出.Cells(行号, 7) = Val(ARRYM(r, 9)) * 待中和 / qty
                    WS出.Cells(行号, 8) = "未配对交易"
                    WS出.Rows(行号).Interior.Color = 常色十红
                    割单行数 = 割单行数 + 1
                    Dim ac_s As Long
                    For ac_s = 1 To 15: 割单数组(割单行数, ac_s) = ARRYM(r, ac_s): Next
                    割单数组(割单行数, 6) = 类别r
                    割单数组(割单行数, 8) = 待中和
                    割单数组(割单行数, 9) = Val(ARRYM(r, 9)) * 待中和 / qty
                    割单数组(割单行数, 常割单列状态) = "未配对交易"
                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(r, 3))
                    未配对计数 = 未配对计数 + 1
                    未配对行(未配对计数) = 割单行数
                    总不完整 = 总不完整 + 1
                    行号 = 行号 + 1
                    ' 输出配对部分
                    WS出.Cells(行号, 3) = ""
                    WS出.Cells(行号, 4) = ARRYM(r, 1)
                    WS出.Cells(行号, 5) = 类别r
                    WS出.Cells(行号, 6) = qty - 待中和
                    WS出.Cells(行号, 7) = Val(ARRYM(r, 9)) * (qty - 待中和) / qty
                    WS出.Cells(行号, 8) = "配对交易"
                    割单行数 = 割单行数 + 1
                    For ac_s = 1 To 15: 割单数组(割单行数, ac_s) = ARRYM(r, ac_s): Next
                    割单数组(割单行数, 6) = 类别r
                    割单数组(割单行数, 8) = qty - 待中和
                    割单数组(割单行数, 9) = Val(ARRYM(r, 9)) * (qty - 待中和) / qty
                    割单数组(割单行数, 常割单列状态) = "配对交易"
                    割单数组(割单行数, 常割单列配对类型) = "历史买卖配对"
                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(r, 3))
                    行号 = 行号 + 1
                    待中和 = 0
                    GoTo 下一交易
                End If
            ElseIf 待中和 < 0 And 类别r = "买入" Then
                ' 买入是在填补缺口
                If qty <= -待中和 Then
                    标记 = "未配对交易"
                    待中和 = 待中和 + qty
                Else
                    ' 拆分买入
                    WS出.Cells(行号, 3) = ""
                    WS出.Cells(行号, 4) = ARRYM(r, 1)
                    WS出.Cells(行号, 5) = 类别r
                    WS出.Cells(行号, 6) = -待中和
                    WS出.Cells(行号, 7) = Val(ARRYM(r, 9)) * (-待中和) / qty
                    WS出.Cells(行号, 8) = "未配对交易"
                    WS出.Rows(行号).Interior.Color = 常色十红
                    割单行数 = 割单行数 + 1
                    Dim ac_b As Long
                    For ac_b = 1 To 15: 割单数组(割单行数, ac_b) = ARRYM(r, ac_b): Next
                    割单数组(割单行数, 6) = 类别r
                    割单数组(割单行数, 8) = -待中和
                    割单数组(割单行数, 9) = Val(ARRYM(r, 9)) * (-待中和) / qty
                    割单数组(割单行数, 常割单列状态) = "未配对交易"
                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(r, 3))
                    未配对计数 = 未配对计数 + 1
                    未配对行(未配对计数) = 割单行数
                    总不完整 = 总不完整 + 1
                    行号 = 行号 + 1
                    ' 输出配对部分
                    WS出.Cells(行号, 3) = ""
                    WS出.Cells(行号, 4) = ARRYM(r, 1)
                    WS出.Cells(行号, 5) = 类别r
                    WS出.Cells(行号, 6) = qty + 待中和
                    WS出.Cells(行号, 7) = Val(ARRYM(r, 9)) * (qty + 待中和) / qty
                    WS出.Cells(行号, 8) = "配对交易"
                    割单行数 = 割单行数 + 1
                    For ac_b = 1 To 15: 割单数组(割单行数, ac_b) = ARRYM(r, ac_b): Next
                    割单数组(割单行数, 6) = 类别r
                    割单数组(割单行数, 8) = qty + 待中和
                    割单数组(割单行数, 9) = Val(ARRYM(r, 9)) * (qty + 待中和) / qty
                    割单数组(割单行数, 常割单列状态) = "配对交易"
                    割单数组(割单行数, 常割单列配对类型) = "历史买卖配对"
                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(r, 3))
                    行号 = 行号 + 1
                    待中和 = 0
                    GoTo 下一交易
                End If
            Else
                标记 = "配对交易"
            End If
            ' 输出交易
            WS出.Cells(行号, 3) = ""
            WS出.Cells(行号, 4) = ARRYM(r, 1)
            WS出.Cells(行号, 5) = 类别r
            WS出.Cells(行号, 6) = qty
            WS出.Cells(行号, 7) = Val(ARRYM(r, 9))
            WS出.Cells(行号, 8) = 标记
            If 标记 = "未配对交易" Then
                WS出.Rows(行号).Interior.Color = 常色十红
                总不完整 = 总不完整 + 1
            End If
            割单行数 = 割单行数 + 1
            Dim ac As Long
            For ac = 1 To 15: 割单数组(割单行数, ac) = ARRYM(r, ac): Next
            割单数组(割单行数, 6) = 类别r
            割单数组(割单行数, 8) = qty
            割单数组(割单行数, 9) = Val(ARRYM(r, 9))
            割单数组(割单行数, 常割单列状态) = 标记
            If 标记 = "未配对交易" Then
                未配对计数 = 未配对计数 + 1
                未配对行(未配对计数) = 割单行数
            Else
                割单数组(割单行数, 常割单列配对类型) = "历史买卖配对"
            End If
            割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(r, 3))
            行号 = 行号 + 1
下一交易:
        Next
        跳过:"""

content = content[:start_idx] + new_code + content[end_idx:]

with open('昭明计划VS优化_vba/PX算研_ZSM交割单.bas', 'w', encoding='utf-8') as f:
    f.write(content)

print('Algorithm replaced. Checking balance...')
subs = content.count('Sub ') + content.count('Function ')
ends = content.count('End Sub') + content.count('End Function')
print(f'Sub/Function: {subs}, End Sub/Function: {ends}')