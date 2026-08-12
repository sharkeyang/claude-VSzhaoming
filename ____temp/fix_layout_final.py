# -*- coding: utf-8 -*-
import re

with open(r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'r', encoding='utf-8') as f:
    text = f.read()

NL = '\n'

# Fix 持仓构成行号: 末行=6~13 → 末行=8~15
# 满仓率: 末行=14 → 末行=16
pairs = [
    ('末行 = 6\n    WSTO.Cells(末行, 1).Value = "  ├─ETF"', '末行 = 8\n    WSTO.Cells(末行, 1).Value = "  ├─ETF"'),
    ('末行 = 7\n    WSTO.Cells(末行, 1).Value = "  └─股票"', '末行 = 9\n    WSTO.Cells(末行, 1).Value = "  └─股票"'),
    ('末行 = 8\n    WSTO.Cells(末行, 1).Value = "   ├─上证"', '末行 = 10\n    WSTO.Cells(末行, 1).Value = "   ├─上证"'),
    ('末行 = 9\n    WSTO.Cells(末行, 1).Value = "   ├─科创"', '末行 = 11\n    WSTO.Cells(末行, 1).Value = "   ├─科创"'),
    ('末行 = 10\n    WSTO.Cells(末行, 1).Value = "   ├─深证"', '末行 = 12\n    WSTO.Cells(末行, 1).Value = "   ├─深证"'),
    ('末行 = 11\n    WSTO.Cells(末行, 1).Value = "   ├─创业"', '末行 = 13\n    WSTO.Cells(末行, 1).Value = "   ├─创业"'),
    ('末行 = 12\n    WSTO.Cells(末行, 1).Value = "   ├─北交"', '末行 = 14\n    WSTO.Cells(末行, 1).Value = "   ├─北交"'),
    ('末行 = 13\n    WSTO.Cells(末行, 1).Value = "   └─港股"', '末行 = 15\n    WSTO.Cells(末行, 1).Value = "   └─港股"'),
    ('末行 = 14\n    WSTO.Cells(末行, 1).Value = "满仓率"', '末行 = 16\n    WSTO.Cells(末行, 1).Value = "满仓率"'),
]

for old, new in pairs:
    count = text.count(old)
    if count > 0:
        text = text.replace(old, new, 1)
        print(f'OK: {old[:30]}')
    else:
        # Try with \r\n
        old2 = old.replace('\n', '\r\n')
        if text.count(old2) > 0:
            text = text.replace(old2, new.replace('\n', '\r\n'), 1)
            print(f'OK(CRLF): {old[:30]}')
        else:
            print(f'NOT FOUND: {old[:30]}')

# Delete 仓位目标
old = '    末行 = 17\n    WSTO.Cells(末行, 1).Value = "仓位目标"\n    If 福总资 > 0 Then WSTO.Cells(末行, 3).Value = Format(福仓额 / 福总资, "0%") & "(目标30%)"\n    If 福总资 > 0 Then WSTO.Cells(末行, 3).Font.Color = IIf(Abs(福仓额 / 福总资 - 0.3) > 0.15, 常色主黄, 常色主黑)\n    If 彦总资 > 0 Then WSTO.Cells(末行, 5).Value = Format(彦仓额 / 彦总资, "0%") & "(目标60%)"\n    If 彦总资 > 0 Then WSTO.Cells(末行, 5).Font.Color = IIf(Abs(彦仓额 / 彦总资 - 0.6) > 0.2, 常色主黄, 常色主黑)\n    If 福总资 + 彦总资 > 0 Then WSTO.Cells(末行, 7).Value = Format(总持仓额 / (福总资 + 彦总资), "0%")'
if text.count(old) > 0:
    text = text.replace(old, '', 1)
    print('仓位目标 deleted')
else:
    old2 = old.replace('\n', '\r\n')
    if text.count(old2) > 0:
        text = text.replace(old2, '', 1)
        print('仓位目标 deleted (CRLF)')
    else:
        print('仓位目标 NOT FOUND')

# Fix 格式范围
text = text.replace('For X = 6 To 13', 'For X = 8 To 15', 1)
text = text.replace('For X = 5 To 17', 'For X = 5 To 16', 1)

# Fix 大盘仓位限制
text = text.replace('WSTO.Cells(18, 8).Value', 'WSTO.Cells(17, 8).Value', 1)
text = text.replace('WSTO.Cells(18, 8).Font.Size', 'WSTO.Cells(17, 8).Font.Size', 1)
text = text.replace('WSTO.Cells(18, 8).Font.Color', 'WSTO.Cells(17, 8).Font.Color', 1)
text = text.replace('WSTO.Range(WSTO.Cells(18, 8), WSTO.Cells(18, 14)).Merge', 'WSTO.Range(WSTO.Cells(17, 8), WSTO.Cells(17, 14)).Merge', 1)
text = text.replace('WSTO.Cells(18, 1).Value = "大盘仓位限制"', 'WSTO.Cells(17, 1).Value = "大盘仓位限制"', 1)
text = text.replace('WSTO.Cells(18, 3).Value = Format(总上限, "0%")', 'WSTO.Cells(17, 3).Value = Format(总上限, "0%")', 1)
text = text.replace('WSTO.Cells(18, 5).Value = Format(总上限, "0%")', 'WSTO.Cells(17, 5).Value = Format(总上限, "0%")', 1)
text = text.replace('WSTO.Cells(18, 7).Value = Format(总上限, "0%")', 'WSTO.Cells(17, 7).Value = Format(总上限, "0%")', 1)
text = text.replace('WSTO.Rows(18).HorizontalAlignment', 'WSTO.Rows(17).HorizontalAlignment', 1)
text = text.replace('For X = 18 To 28', 'For X = 17 To 27', 1)

# 大盘行
for old_n, new_n in [(19,18),(20,19),(21,20),(22,21),(23,22),(24,23),(25,24),(26,25),(27,26),(28,27)]:
    text = text.replace(f'    大盘行 = {old_n}\n', f'    大盘行 = {new_n}\n', 1)

# 行业分布
text = text.replace('末行 = 32\n    WSTO.Cells(末行, 1).Value = "二、行业分布"', '末行 = 31\n    WSTO.Cells(末行, 1).Value = "二、行业分布"', 1)
text = text.replace('末行 = 33\n    WSTO.Cells(末行, 1).Value = "行业"', '末行 = 32\n    WSTO.Cells(末行, 1).Value = "行业"', 1)
text = text.replace('末行 = 34\n    For Each 行业 In 行业典集.Keys', '末行 = 33\n    For Each 行业 In 行业典集.Keys', 1)
text = text.replace('For X = 32 To 末行整', 'For X = 31 To 末行整', 1)
text = text.replace("WSTO.Rows(32).RowHeight = 20  '行业表头行高", "WSTO.Rows(31).RowHeight = 20  '行业表头行高", 1)

with open(r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'w', encoding='utf-8') as f:
    f.write(text)

print('\nDONE')