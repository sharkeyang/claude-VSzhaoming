# -*- coding: utf-8 -*-
import re

with open(r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'r', encoding='utf-8') as f:
    text = f.read()

# Find the old block to replace
old_start = '末行 = 5\n    WSTO.Cells(末行, 1).Value = "持仓"'
old_end_marker = 'Next\n    End With'

new_block = '''末行 = 5
    WSTO.Cells(末行, 1).Value = "总资产(千元)"
    WSTO.Cells(末行, 3).Value = Round(福总资, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 5).Value = Round(彦总资, 1)
    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 7).Value = Round(福总资 + 彦总资, 1)
    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    WSTO.Rows(末行).Font.Bold = True
    末行 = 6
    WSTO.Cells(末行, 1).Value = "现金余额(千元)"
    WSTO.Cells(末行, 3).Value = Round(福现金, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 5).Value = Round(彦现金, 1)
    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 7).Value = Round(福现金 + 彦现金, 1)
    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    WSTO.Rows(末行).Font.Bold = True
    末行 = 7
    WSTO.Cells(末行, 1).Value = "持仓"
    WSTO.Cells(末行, 2).Value = 福票数
    WSTO.Cells(末行, 3).Value = Round(福仓额, 1)
    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦票数
    WSTO.Cells(末行, 5).Value = Round(彦仓额, 1)
    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 持票数
    WSTO.Cells(末行, 7).Value = Round(总持仓额, 1)
    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    WSTO.Rows(末行).Font.Bold = True
    '--- 持仓构成（直接展开在持仓之下） ---
    末行 = 8
    WSTO.Cells(末行, 1).Value = "  ├─ETF"
    WSTO.Cells(末行, 2).Value = 福ETF数: WSTO.Cells(末行, 3).Value = Round(福ETF额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦ETF数: WSTO.Cells(末行, 5).Value = Round(彦ETF额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = ETF数: WSTO.Cells(末行, 7).Value = Round(ETF额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    WSTO.Rows(末行).Font.Bold = True
    末行 = 9
    WSTO.Cells(末行, 1).Value = "  └─股票"
    WSTO.Cells(末行, 2).Value = 福股数: WSTO.Cells(末行, 3).Value = Round(福股额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦股数: WSTO.Cells(末行, 5).Value = Round(彦股额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 持票数 - ETF数: WSTO.Cells(末行, 7).Value = Round(总持仓额 - ETF额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    WSTO.Rows(末行).Font.Bold = True
    '交易所细分
    末行 = 10
    WSTO.Cells(末行, 1).Value = "   ├─上证"
    WSTO.Cells(末行, 2).Value = 福上证数: WSTO.Cells(末行, 3).Value = Round(福上证额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦上证数: WSTO.Cells(末行, 5).Value = Round(彦上证额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 上证股数: WSTO.Cells(末行, 7).Value = Round(上证股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 11
    WSTO.Cells(末行, 1).Value = "   ├─科创"
    WSTO.Cells(末行, 2).Value = 福科创数: WSTO.Cells(末行, 3).Value = Round(福科创额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦科创数: WSTO.Cells(末行, 5).Value = Round(彦科创额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 科创股数: WSTO.Cells(末行, 7).Value = Round(科创股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 12
    WSTO.Cells(末行, 1).Value = "   ├─深证"
    WSTO.Cells(末行, 2).Value = 福深证数: WSTO.Cells(末行, 3).Value = Round(福深证额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦深证数: WSTO.Cells(末行, 5).Value = Round(彦深证额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 深证股数: WSTO.Cells(末行, 7).Value = Round(深证股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 13
    WSTO.Cells(末行, 1).Value = "   ├─创业"
    WSTO.Cells(末行, 2).Value = 福创业数: WSTO.Cells(末行, 3).Value = Round(福创业额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦创业数: WSTO.Cells(末行, 5).Value = Round(彦创业额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 创业股数: WSTO.Cells(末行, 7).Value = Round(创业股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 14
    WSTO.Cells(末行, 1).Value = "   ├─北交"
    WSTO.Cells(末行, 2).Value = 福北交数: WSTO.Cells(末行, 3).Value = Round(福北交额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦北交数: WSTO.Cells(末行, 5).Value = Round(彦北交额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 北交股数: WSTO.Cells(末行, 7).Value = Round(北交股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 15
    WSTO.Cells(末行, 1).Value = "   └─港股"
    WSTO.Cells(末行, 2).Value = 福港股数: WSTO.Cells(末行, 3).Value = Round(福港股额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 4).Value = 彦港股数: WSTO.Cells(末行, 5).Value = Round(彦港股额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"
    WSTO.Cells(末行, 6).Value = 港股数: WSTO.Cells(末行, 7).Value = Round(港股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"
    末行 = 16
    WSTO.Cells(末行, 1).Value = "满仓率"
    If 福总资 > 0 Then WSTO.Cells(末行, 3).Value = Format(福仓额 / 福总资, "0%")
    If 彦总资 > 0 Then WSTO.Cells(末行, 5).Value = Format(彦仓额 / 彦总资, "0%")
    If 福总资 + 彦总资 > 0 Then WSTO.Cells(末行, 7).Value = Format(总持仓额 / (福总资 + 彦总资), "0%")
    '--- 持仓构成数据行(8-15)浅灰间隔 ---
    For X = 8 To 15
        With WSTO.Range(WSTO.Cells(X, 1), WSTO.Cells(X, 7)).Interior
            .Color = RGB(245, 245, 245)
        End With
    Next
    '--- 概览/持仓构成数字格式 ---
    For X = 5 To 16
        WSTO.Rows(X).HorizontalAlignment = xlRight
        WSTO.Cells(X, 1).HorizontalAlignment = xlLeft
    Next'''

# Find the exact old block
old_start_idx = text.find(old_start)
if old_start_idx < 0:
    print('ERROR: old_start not found')
    exit(1)

old_end_idx = text.find(old_end_marker, old_start_idx)
if old_end_idx < 0:
    print('ERROR: old_end not found')
    exit(1)

old_end_idx = old_end_idx + len(old_end_marker)

# Replace
text = text[:old_start_idx] + new_block + text[old_end_idx:]

with open(r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'w', encoding='utf-8') as f:
    f.write(text)

print('OK - replaced %d chars' % (old_end_idx - old_start_idx))