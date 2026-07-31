import re

with open(r'昭明计划VS优化_vba\IQQQ跨码_D据擎2神谕.bas', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Insert V3 constant and shift V4+ constants
# 位谕of月基带日 = +6 → +7
content = content.replace(
    'Public Const 位谕of月基带日 = 位谕始of族策 + 6     \'V4 月基带日: (DXAB)同上(DXCD)同上(DXEF) 日级别DXAB→DXCD→DXEF带动',
    'Public Const 位谕of月基带周 = 位谕始of族策 + 6     \'V3 月基带周: (WXCD)同上(↘)反向(↗)正向(▽)同下 WXCD→WXAB带动\nPublic Const 位谕of月基带日 = 位谕始of族策 + 7     \'V4 月基带日: (DXAB)同上(DXCD)同上(DXEF) 日级别DXAB→DXCD→DXEF带动'
)

# Shift all subsequent constants: +7→+8, +8→+9, ... +16→+17
# 日层段 +7 → +8
content = content.replace('Public Const 位谕of日层段 = 位谕始of族策 + 7', 'Public Const 位谕of日层段 = 位谕始of族策 + 8')
# 日冲策分 +8 → +9
content = content.replace('Public Const 位谕of日冲策分 = 位谕始of族策 + 8', 'Public Const 位谕of日冲策分 = 位谕始of族策 + 9')
# 日冲H2分 +9 → +10
content = content.replace('Public Const 位谕of日冲H2分 = 位谕始of族策 + 9', 'Public Const 位谕of日冲H2分 = 位谕始of族策 + 10')
# 日冲策略 +10 → +11
content = content.replace('Public Const 位谕of日冲策略 = 位谕始of族策 + 10', 'Public Const 位谕of日冲策略 = 位谕始of族策 + 11')
# 日层联动 +11 → +12
content = content.replace('Public Const 位谕of日层联动 = 位谕始of族策 + 11', 'Public Const 位谕of日层联动 = 位谕始of族策 + 12')
# 日层漏提示 +12 → +13
content = content.replace('Public Const 位谕of日层漏提示 = 位谕始of族策 + 12', 'Public Const 位谕of日层漏提示 = 位谕始of族策 + 13')
# 日层机警 +13 → +14
content = content.replace('Public Const 位谕of日层机警 = 位谕始of族策 + 13', 'Public Const 位谕of日层机警 = 位谕始of族策 + 14')
# 日层盈提示 +14 → +15
content = content.replace('Public Const 位谕of日层盈提示 = 位谕始of族策 + 14', 'Public Const 位谕of日层盈提示 = 位谕始of族策 + 15')
# 周层四域 +15 → +16
content = content.replace('Public Const 位谕of周层四域 = 位谕始of族策 + 15', 'Public Const 位谕of周层四域 = 位谕始of族策 + 16')
# 日层四域 +16 → +17
content = content.replace('Public Const 位谕of日层四域 = 位谕始of族策 + 16', 'Public Const 位谕of日层四域 = 位谕始of族策 + 17')

# 2. Insert V3 calculation logic after V2 (位谕of月基策分赋值)
# Find the V4 section start and insert V3 before it
v4_start = content.index("'V4 月基带日（日级别三联动）— DXAB→DXCD→DXEF带动")
v3_code = """'============================================================================
            'V3 月基带周（周级别WXCD→WXAB带动）
            '设计思路：WXCD（大局）→WXAB（护型）双向带动
            '  输出格式：信号 + (WXCD护型) + (WXAB护型)
            '  信号：▲同上向好 / ↘反向风险 / ↗正向潜力 / ▽同下向差
            '============================================================================
            Dim 月基带周 As String: 月基带周 = ""
            Dim V3周局 As String: V3周局 = 谕组(X, 位谕of周层大局)
            Dim V3周护 As String: V3周护 = 谕组(X, 位谕of周层护型)
            Dim V3CD方向 As String: V3CD方向 = Mid$(V3周局, 1, 1)  'WXCD方向: 升/降/待
            Dim V3CD金银 As Boolean: V3CD金银 = (InStr(V3周局, "金") > 0 Or InStr(V3周局, "银") > 0)
            Dim V3AB甲乙 As Boolean: V3AB甲乙 = (InStr(V3周护, "甲") > 0 Or InStr(V3周护, "乙") > 0)
            Dim V3AB丙丁戊己 As Boolean: V3AB丙丁戊己 = (InStr(V3周护, "丙") > 0 Or InStr(V3周护, "丁") > 0 Or InStr(V3周护, "戊") > 0 Or InStr(V3周护, "己") > 0)

            If V3CD金银 And V3AB甲乙 Then
                月基带周 = "▲"       '同上向好：大局+护型双强
            ElseIf V3CD金银 And V3AB丙丁戊己 Then
                月基带周 = "↘"       '反向风险：大局好但护型破
            ElseIf Not V3CD金银 And V3AB甲乙 Then
                月基带周 = "↗"       '正向潜力：大局差但护型好
            Else
                月基带周 = "▽"       '同下向差：双弱
            End If
            月基带周 = 月基带周 & "(" & V3CD方向 & ")"
            谕组(X, 位谕of月基带周) = 月基带周
            '============================================================================
            """

content = content[:v4_start] + v3_code + content[v4_start:]

# 3. Update Excel header/color/width
# Add 月基带周 header after 月基策分
old_header = '.Cells(1, 位谕of月基策分) = "月基策分" & vbCrLf & "(5周维持)"'
new_header = '.Cells(1, 位谕of月基策分) = "月基策分" & vbCrLf & "(5周维持)" & vbCrLf & vbCrLf & .Cells(1, 位谕of月基带周) = "月基带周" & vbCrLf & "(CD→AB)"'
content = content.replace(old_header, new_header)

# Actually, the header setting is a separate line, let me find the exact pattern
# Find the 月基带日 header line
old_v4_header = '.Cells(1, 位谕of月基带日) = "月基带日(AB-CD-EF)"'
# Add V3 header before V4
new_v3_v4_headers = '.Cells(1, 位谕of月基带周) = "月基带周" & vbCrLf & "(CD→AB)"' + "\n" + '        ' + old_v4_header
content = content.replace(old_v4_header, new_v3_v4_headers)

# Add V3 color
old_v4_color = '.Columns(位谕of月基带日).Interior.Color = 常色四碧'
new_v3_v4_color = '.Columns(位谕of月基带周).Interior.Color = 常色四碧' + "\n" + '        ' + old_v4_color
content = content.replace(old_v4_color, new_v3_v4_color)

# Add V3 column width
old_v4_width = '.Columns(位谕of月基带日).ColumnWidth = 14'
new_v3_v4_width = '.Columns(位谕of月基带周).ColumnWidth = 9' + "\n" + '        ' + old_v4_width
content = content.replace(old_v4_width, new_v3_v4_width)

with open(r'昭明计划VS优化_vba\IQQQ跨码_D据擎2神谕.bas', 'w', encoding='utf-8') as f:
    f.write(content)

print('OK')