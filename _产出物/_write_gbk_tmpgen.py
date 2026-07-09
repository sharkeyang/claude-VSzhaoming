"""Write tmpGen.bas without blank lines, in GBK encoding"""
import os
# 紧凑版: 没有多余空行
lines = [
    'Attribute VB_Name = "tmpGen"',
    "'临时: 批量生成算展(单代码)",
    "'使用方法: 导入到昭明计划VS优化.xlsm, 然后在Python中:",
    "'  excel.Application.Run(\"tmpGen\", \"sz159864\")",
    "Public Sub tmpGen(ByVal 被研代码 As String)",
    "    Dim ARRLLL As Variant, 谕组 As Variant",
    "    Dim 计数 As Integer",
    "    计数 = XL算展数程跨期(ARRLLL, 被研代码, , , 谕组, \"T@乾坤\", \"W\")",
    "    If 计数 < 1 Then Exit Sub",
    "    Dim wb As Workbook",
    "    Set wb = Workbooks.Add",
    "    Dim ws As Worksheet",
    "    Set ws = wb.Sheets(1)",
    "    ws.Name = \"LD\" & 被研代码",
    "    计数 = XL算展格程跨期_通用生成(ARRLLL, ws, 被研代码, \"W\", 谕组)",
    "    If 计数 > 0 Then",
    "        Dim 路径 As String",
    "        路径 = ThisWorkbook.Path & \"\\昭明算展\\算展.\" & 被研代码 & \".xlsx\"",
    "        Application.DisplayAlerts = False",
    "        wb.SaveAs 路径, 51",
    "        Application.DisplayAlerts = True",
    "    End If",
    "    wb.Close False",
    "End Sub",
]
content = '\r\n'.join(lines) + '\r\n'

for d in [r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba', r'd:\@VSwork\VS昭明计划VBA优化\____temp']:
    path = os.path.join(d, 'tmpGen.bas')
    with open(path, 'wb') as f:
        f.write(content.encode('gbk'))
    with open(path, 'rb') as f:
        raw = f.read(100)
    # 检查 \r\n  vs \r\r\n
    double_rn = raw.count(b'\r\r\n')
    print(f'{os.path.basename(path)}: {len(content)}bytes, \r\r\n次数={double_rn}')
    # 期望: double_rn == 0