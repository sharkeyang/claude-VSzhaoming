# -*- coding: utf-8 -*-
"""Fix 筛选 module: 8个典码按A-H分开"""
lines = open('昭明计划VS优化_vba/IQQQ跨码_P展擎1筛选.bas', encoding='utf-8').readlines()

# 找到旧block
start = None
for i, line in enumerate(lines):
    if '日冲策略（4个典码' in line:
        start = i
        break

if start:
    # 找到block结束
    end = None
    for j in range(start, start + 25):
        if 'End If' in lines[j] and '复盘' in lines[j+1]:
            end = j
            break
    if end is None:
        for j in range(start, start + 25):
            if 'End If' in lines[j] and '类别' in lines[j+1]:
                end = j
                break

    if end:
        new_block = [
            '            \'============================================================================\n',
            '            \'日冲策略（8个典码，按首字母A-H匹配）\n',
            '            \'============================================================================\n',
            '            Dim 日冲策名 As String: 日冲策名 = 谕组(X, 位谕of日冲策略)\n',
            '            Dim 日冲首字 As String\n',
            '            If Len(日冲策名) >= 1 Then 日冲首字 = Left$(日冲策名, 1)\n',
            '            If 日冲首字 = "A" Then\n',
            '                典日策_A.Add Item:=X, key:=CIDL\n',
            '            ElseIf 日冲首字 = "B" Then\n',
            '                典日策_B.Add Item:=X, key:=CIDL\n',
            '            ElseIf 日冲首字 = "C" Then\n',
            '                典日策_C.Add Item:=X, key:=CIDL\n',
            '            ElseIf 日冲首字 = "D" Then\n',
            '                典日策_D.Add Item:=X, key:=CIDL\n',
            '            ElseIf 日冲首字 = "E" Then\n',
            '                典日策_E.Add Item:=X, key:=CIDL\n',
            '            ElseIf 日冲首字 = "F" Then\n',
            '                典日策_F.Add Item:=X, key:=CIDL\n',
            '            ElseIf 日冲首字 = "G" Then\n',
            '                典日策_G.Add Item:=X, key:=CIDL\n',
            '            ElseIf 日冲首字 = "H" Then\n',
            '                典日策_H.Add Item:=X, key:=CIDL\n',
            '            End If\n',
        ]
        lines[start:end+1] = new_block
        open('昭明计划VS优化_vba/IQQQ跨码_P展擎1筛选.bas', 'w', encoding='utf-8').writelines(lines)
        print(f'Done: replaced {end-start+1} lines')
    else:
        print('Could not find End If')
else:
    print('Could not find start')