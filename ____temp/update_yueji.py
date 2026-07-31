import os
os.chdir("d:/@VSwork/VS昭明计划VBA优化")

with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas', 'r', encoding='utf-8') as f:
    content = f.read()

# Build the replacement
old_start = "'============================================================================\n            'V2 \u6708\u57fa\u7b56\u5206"
# Find the exact section
idx = content.find("'============================================================================\n            'V2 \u6708\u57fa\u7b56\u5206")
idx_end = content.find("            Else\n                '\u975e\u591a\u957f\u533a\u57df\u4e0d\u8bc4\u5206\n                \u6708\u57fa\u7b56\u5206 = 0\n            End If", idx)
idx_end += len("            Else\n                '\u975e\u591a\u957f\u533a\u57df\u4e0d\u8bc4\u5206\n                \u6708\u57fa\u7b56\u5206 = 0\n            End If")

old_section = content[idx:idx_end]

new_section = """            '============================================================================
            'V2 月基策分（存续分）— 多长+多被评分，查表赋值
            '设计原理：基于波型×柱排二维表，查续持率作为基础分
            '  50分为敏感阈值：≥50持有，<50归零不输出
            '多长数据来源：全量7463只验证（2026-07-19）
            '多被数据来源：全量7463只抽样验证（2026-07-31）
            '============================================================================
            If 四域 = "多长" Or 四域 = "多被" Then
                '解析波型
                Dim V2波型 As String: V2波型 = "其他"
                If InStr(周波型, "龙猪") > 0 Then
                    V2波型 = "龙猪"
                ElseIf InStr(周波型, "龙管") > 0 Then
                    V2波型 = "龙管"
                ElseIf InStr(周波型, "头正") > 0 Then
                    V2波型 = "头正"
                ElseIf InStr(周波型, "震正") > 0 Then
                    V2波型 = "震正"
                ElseIf InStr(周波型, "震负") > 0 Then
                    V2波型 = "震负"
                End If

                '解析柱排
                Dim V2柱排 As String: V2柱排 = "其他"
                Dim 柱排首字 As String: 柱排首字 = Left$(周柱排, 1)
                If 柱排首字 = "升" Then
                    V2柱排 = "升排"
                ElseIf 柱排首字 = "人" Then
                    V2柱排 = "人排"
                ElseIf 柱排首字 = "跌" Then
                    V2柱排 = "跌排"
                End If

                If 四域 = "多长" Then
                    '多长区域：金系评分（高续持率）
                    Select Case V2波型
                    Case "龙猪"
                        Select Case V2柱排
                        Case "升排": 月基策分 = 75
                        Case "人排": 月基策分 = 61
                        Case "跌排": 月基策分 = 58
                        Case Else:   月基策分 = 65
                        End Select
                    Case "龙管"
                        Select Case V2柱排
                        Case "升排": 月基策分 = 70
                        Case "人排": 月基策分 = 58
                        Case "跌排": 月基策分 = 56
                        Case Else:   月基策分 = 61
                        End Select
                    Case "头正"
                        Select Case V2柱排
                        Case "升排": 月基策分 = 63
                        Case "人排": 月基策分 = 58
                        Case "跌排": 月基策分 = 51
                        Case Else:   月基策分 = 57
                        End Select
                    Case "震正"
                        Select Case V2柱排
                        Case "升排": 月基策分 = 65
                        Case "人排": 月基策分 = 56
                        Case "跌排": 月基策分 = 51
                        Case Else:   月基策分 = 57
                        End Select
                    Case "震负"
                        Select Case V2柱排
                        Case "升排": 月基策分 = 62
                        Case "人排": 月基策分 = 58
                        Case "跌排": 月基策分 = 50
                        Case Else:   月基策分 = 57
                        End Select
                    Case Else
                        Select Case V2柱排
                        Case "升排": 月基策分 = 65
                        Case "人排": 月基策分 = 57
                        Case "跌排": 月基策分 = 52
                        Case Else:   月基策分 = 58
                        End Select
                    End Select
                Else
                    '多被区域：银系评分（低续持率，数据有限）
                    Select Case V2波型
                    Case "震正"
                        Select Case V2柱排
                        Case "升排": 月基策分 = 55
                        Case "人排": 月基策分 = 50
                        Case "跌排": 月基策分 = 48
                        Case Else:   月基策分 = 50
                        End Select
                    Case "震负"
                        Select Case V2柱排
                        Case "升排": 月基策分 = 54
                        Case "人排": 月基策分 = 50
                        Case "跌排": 月基策分 = 45
                        Case Else:   月基策分 = 50
                        End Select
                    Case "头正", "头负", "龙猪", "龙管"
                        Select Case V2柱排
                        Case "升排": 月基策分 = 52
                        Case "人排": 月基策分 = 50
                        Case "跌排": 月基策分 = 45
                        Case Else:   月基策分 = 50
                        End Select
                    Case Else
                        月基策分 = 48
                    End Select
                End If

                'WXAB调节：甲+3, 乙-3, 己-5
                If InStr(周护, "甲") > 0 Then
                    月基策分 = 月基策分 + 3
                ElseIf InStr(周护, "己") > 0 Then
                    月基策分 = 月基策分 - 5
                ElseIf InStr(周护, "乙") > 0 Then
                    月基策分 = 月基策分 - 3
                End If

                '盈提示调节
                If InStr(周盈提, "高") > 0 And InStr(周盈提, "宽") > 0 Then
                    月基策分 = 月基策分 + 8
                ElseIf InStr(周盈提, "高") > 0 Then
                    月基策分 = 月基策分 + 4
                End If

                '分类调节：按市板
                If 周市板 = "Qe" Or 周市板 = "Qd" Then
                    月基策分 = 月基策分 + 7
                ElseIf 周市板 = "Qit" Or 周市板 = "Qin" Then
                    月基策分 = 月基策分 - 3
                End If

                '限幅
                If 月基策分 < 0 Then 月基策分 = 0
                If 月基策分 > 100 Then 月基策分 = 100

                '分数太低(<=50)则归零不输出
                If 月基策分 <= 50 Then 月基策分 = 0
            Else
                '非多长/多被区域不评分
                月基策分 = 0
            End If"""

content = content.replace(old_section, new_section, 1)

with open('昭明计划VS优化_vba/IQQQ跨码_D据擎2神谕.bas', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done - 月基策分 updated")