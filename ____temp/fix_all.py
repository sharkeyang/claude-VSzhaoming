# -*- coding: utf-8 -*-
with open(r'D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'r', encoding='utf-8') as f:
    text = f.read()

# STEP 1: Remove 大盘评分 row
old = '    大盘行 = 21\n    WSTO.Cells(大盘行, 1).Value = "大盘评分"\n    WSTO.Cells(大盘行, 7).Value = Format(总上限, "0%")'
text = text.replace(old, '')

# STEP 2: Fix 福账户 33% position
old = 'WSTO.Cells(大盘行, 3).Value = Round(福上限, 1): WSTO.Cells(大盘行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(大盘行, 7).Value = Format(总上限, "0%")'
new = 'WSTO.Cells(大盘行, 2).Value = Format(总上限, "0%")\n    WSTO.Cells(大盘行, 3).Value = Round(福上限, 1): WSTO.Cells(大盘行, 3).NumberFormatLocal = "#,##0.0"'
text = text.replace(old, new, 1)

# STEP 3: Fix 彦账户 33% position
old = 'WSTO.Cells(大盘行, 5).Value = Round(彦上限, 1): WSTO.Cells(大盘行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(大盘行, 7).Value = Format(总上限, "0%")'
new = 'WSTO.Cells(大盘行, 4).Value = Format(总上限, "0%")\n    WSTO.Cells(大盘行, 5).Value = Round(彦上限, 1): WSTO.Cells(大盘行, 5).NumberFormatLocal = "#,##0.0"'
text = text.replace(old, new, 1)

# STEP 4: Fix status display in brackets
pairs = [
    ('WSTO.Cells(大盘行, 3).Value = Round(福月基额, 1) & "(" & Format(福月基比, "0%") & ")"',
     'WSTO.Cells(大盘行, 3).Value = Round(福月基额, 1) & "(" & IIf(福月基额 >= 福月基目标, "达标", "缺额") & ")"'),
    ('WSTO.Cells(大盘行, 3).Value = Round(福周冲额, 1) & "(" & Format(福周冲比, "0%") & ")"',
     'WSTO.Cells(大盘行, 3).Value = Round(福周冲额, 1) & "(" & IIf(福周冲额 <= 福周冲目标, "达标", "超额") & ")"'),
    ('WSTO.Cells(大盘行, 3).Value = Round(福日冲额, 1) & "(" & Format(福日冲比, "0%") & ")"',
     'WSTO.Cells(大盘行, 3).Value = Round(福日冲额, 1) & "(" & IIf(福日冲额 <= 福日冲目标, "达标", "超额") & ")"'),
    ('WSTO.Cells(大盘行, 5).Value = Round(彦月基额, 1) & "(" & Format(彦月基比, "0%") & ")"',
     'WSTO.Cells(大盘行, 5).Value = Round(彦月基额, 1) & "(" & IIf(彦月基额 >= 彦月基目标, "达标", "缺额") & ")"),
    ('WSTO.Cells(大盘行, 5).Value = Round(彦周冲额, 1) & "(" & Format(彦周冲比, "0%") & ")"',
     'WSTO.Cells(大盘行, 5).Value = Round(彦周冲额, 1) & "(" & IIf(彦周冲额 <= 彦周冲目标, "达标", "超额") & ")"),
    ('WSTO.Cells(大盘行, 5).Value = Round(彦日冲额, 1) & "(" & Format(彦日冲比, "0%") & ")"',
     'WSTO.Cells(大盘行, 5).Value = Round(彦日冲额, 1) & "(" & IIf(彦日冲额 <= 彦日冲目标, "达标", "超额") & ")"),
    ('WSTO.Cells(大盘行, 3).Value = Round(福非策额, 1) & "(无目标)"',
     'WSTO.Cells(大盘行, 3).Value = Round(福非策额, 1) & "(" & IIf(福非策额 > 0, "超额", "0%") & ")"'),
    ('WSTO.Cells(大盘行, 5).Value = Round(彦非策额, 1) & "(无目标)"',
     'WSTO.Cells(大盘行, 5).Value = Round(彦非策额, 1) & "(" & IIf(彦非策额 > 0, "超额", "0%") & ")"'),
]
for old, new in pairs:
    if old in text:
        text = text.replace(old, new, 1)

# STEP 5: Fix 彦日冲 label
old = 'WSTO.Cells(大盘行, 1).Value = "  \u251c\u2500\u65e5\u51b2"'
new = 'WSTO.Cells(大盘行, 1).Value = "  \u251c\u2500\u65e5\u51b2(<=20%)"'
text = text.replace(old, new, 1)

# STEP 6: Add 彦日冲目标
old = 'Dim 彦周冲目标 As Double: 彦周冲目标 = 彦上限 * 0.5'
new = 'Dim 彦周冲目标 As Double: 彦周冲目标 = 彦上限 * 0.5\n    Dim 彦日冲目标 As Double: 彦日冲目标 = 彦上限 * 0.2'
text = text.replace(old, new, 1)

# STEP 7: Shift row numbers
for old_val in range(22, 32):
    new_val = old_val - 1
    text = text.replace('\u5927\u76d8\u884c = {}'.format(old_val), '\u5927\u76d8\u884c = {}'.format(new_val))

# STEP 8: Update 行业分布 row numbers
text = text.replace('\n末行 = 32\n', '\n末行 = 31\n')
text = text.replace('\n末行 = 33\n', '\n末行 = 32\n')
text = text.replace('\n末行 = 34\n', '\n末行 = 33\n')

# STEP 9: Update formatting references
text = text.replace('WSTO.Rows(33).RowHeight', 'WSTO.Rows(32).RowHeight')
text = text.replace('行业分布表头(行33)', '行业分布表头(行32)')
text = text.replace('WSTO.Cells(33, 1), WSTO.Cells(33, 14)', 'WSTO.Cells(32, 1), WSTO.Cells(32, 14)')
text = text.replace('行业分布数据行(34至末行)', '行业分布数据行(33至末行)')
text = text.replace('For X = 34 To 末行整', 'For X = 33 To 末行整')
text = text.replace('行业分布数据行(31至末行)', '行业分布数据行(33至末行)')
text = text.replace('For X = 31 To 末行整', 'For X = 33 To 末行整')

# STEP 10: Update 大盘仓位限制 data range
text = text.replace('大盘仓位限制数据行(21-31)', '大盘仓位限制数据行(20-30)')
text = text.replace('For X = 21 To 31', 'For X = 20 To 30')

# STEP 11: Update 末列整
text = text.replace('末列整 = 10', '末列整 = 14')

# STEP 12: Update 各节标题行
text = text.replace('Array(3, 11, 20, 29)', 'Array(3, 11, 20, 31)')

# STEP 13: 右对齐 block
new_align = """    '--- 右对齐 ---
    With WSTO
        For X = 20 To 30
            .Rows(X).HorizontalAlignment = xlRight
            .Cells(X, 1).HorizontalAlignment = xlLeft
        Next
    End With"""
if "--- 右对齐 ---" in text:
    # Already has 右对齐, skip
    pass
else:
    # Add after 大盘仓位限制 formatting
    text = text.replace("'--- 大盘仓位限制数据行(20-30)浅灰间隔 ---",
                        "'--- 大盘仓位限制数据行(20-30)浅灰间隔 ---\n" + new_align)

with open(r'D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'w', encoding='utf-8') as f:
    f.write(text)
print('All fixes applied')