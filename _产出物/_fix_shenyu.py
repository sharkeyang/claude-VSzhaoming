# -*- coding: utf-8 -*-
"""Insert scoring logic into 神谕.bas"""
import os

fp = r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎2神谕.bas'
marker = "'@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@"

with open(fp, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add constant after 策传
text = text.replace(
    "Public Const 位谕of策传 = 位谕终of族月均 + 8      '策传综合信息，供Python读取",
    "Public Const 位谕of策传 = 位谕终of族月均 + 8      '策传综合信息，供Python读取\nPublic Const 位谕of策分周浮仓 = 位谕终of族月均 + 9      '策分: 周浮仓评分(0~100)"
)
text = text.replace(
    "Public Const 位谕列终全部 = 位谕of策传",
    "Public Const 位谕列终全部 = 位谕of策分周浮仓"
)

# 2. Find the insertion point before 仓系统
target = "'########################################################################################\n'########################################################################################\n'仓系统"
idx = text.find(target)
if idx < 0:
    print("ERROR: Cannot find 仓系统")
else:
    # Find the preceding @@@@@@ marker
    before = text.rfind(marker, 0, idx)
    if before < 0:
        print("ERROR: Cannot find marker before 仓系统")
    else:
        scoring_code = (
            marker + "\n"
            "'策分: 周浮仓评分 (0~100), 基于真高幅回测数据\n"
            + marker + "\n"
            "    Dim 策分 As Integer: 策分 = 0\n"
            "    Dim 周局 As String: 周局 = 谕组(X, 位谕of周层大局)\n"
            "    Dim 周护 As String: 周护 = 谕组(X, 位谕of周层护型)\n"
            "    Dim 周ZA As Double: 周ZA = 谕组(X, 位谕of周类BTZA)\n"
            "    Dim 周柱排 As String: 周柱排 = 谕组(X, 位谕of周层柱排)\n"
            "    Dim 周盈提 As String: 周盈提 = 谕组(X, 位谕of周层盈提示)\n"
            "    Dim 周波型 As String: 周波型 = 谕组(X, 位谕of周层波型)\n"
            "    '----------------------------------------------------------------------------------------\n"
            "    '① 四域 (20分)\n"
            '    If InStr(周局, "金") > 0 And InStr(周护, "甲") + InStr(周护, "乙") + InStr(周护, "己") > 0 Then\n'
            "        策分 = 策分 + 20\n"
            '    ElseIf InStr(周局, "银") > 0 And InStr(周护, "甲") + InStr(周护, "乙") + InStr(周护, "己") > 0 Then\n'
            "        策分 = 策分 + 15\n"
            '    ElseIf InStr(周局, "金") > 0 Then\n'
            "        策分 = 策分 + 5\n"
            "    End If\n"
            "    '----------------------------------------------------------------------------------------\n"
            "    '② ZA区间 (30分)\n"
            "    If 周ZA > 5 And 周ZA <= 10 Then\n"
            "        策分 = 策分 + 30\n"
            "    ElseIf (周ZA >= 3 And 周ZA <= 5) Or 周ZA > 10 Then\n"
            "        策分 = 策分 + 20\n"
            "    ElseIf 周ZA >= 1 And 周ZA < 3 Then\n"
            "        策分 = 策分 + 10\n"
            "    End If\n"
            "    '----------------------------------------------------------------------------------------\n"
            "    '③ 柱排+盈提示 (25分)\n"
            '    If InStr(周柱排, "尾反孕") = 0 And InStr(周盈提, "高") > 0 And Left$(周柱排, 1) = "升" Then\n'
            "        策分 = 策分 + 25\n"
            '    ElseIf Left$(周柱排, 1) = "升" Then\n'
            "        策分 = 策分 + 15\n"
            '    ElseIf InStr(周柱排, "人") > 0 Then\n'
            "        策分 = 策分 + 8\n"
            '    ElseIf Left$(周柱排, 1) = "跌" Then\n'
            "        策分 = 策分 + 5\n"
            "    End If\n"
            "    '----------------------------------------------------------------------------------------\n"
            "    '④ 波型 (25分)\n"
            '    If InStr(周波型, "龙猪") > 0 Or InStr(周波型, "龙管") > 0 Then\n'
            "        策分 = 策分 + 25\n"
            '    ElseIf InStr(周波型, "头正") > 0 Then\n'
            "        策分 = 策分 + 15\n"
            '    ElseIf InStr(周波型, "头负") > 0 Or InStr(周波型, "震负") > 0 Then\n'
            "        策分 = 策分 + 10\n"
            '    ElseIf InStr(周波型, "震正") > 0 Then\n'
            "        策分 = 策分 + 5\n"
            "    End If\n"
            "    '----------------------------------------------------------------------------------------\n"
            "    谕组(X, 位谕of策分周浮仓) = 策分\n"
        )

        # Replace from marker to 仓系统
        old_block = text[before:idx]
        text = text.replace(old_block, scoring_code, 1)
        print("OK")

with open(fp, 'w', encoding='utf-8') as f:
    f.write(text)

# Verify
cnt = text.count("策分周浮仓")
print(f"策分周浮仓出现: {cnt}次")
