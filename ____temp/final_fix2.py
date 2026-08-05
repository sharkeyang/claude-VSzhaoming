# -*- coding: utf-8 -*-
with open(r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'r', encoding='utf-8') as f:
    text = f.read()

# Search for the old block markers - use simple text matching
# The old block has 持仓 at 行5, then 现金余额 at 行14, 总资产 at 行15, 满仓率 at 行16, 仓位目标 at 行17
# Find the start: 末行 = 5 followed by 持仓
mark1 = '末行 = 5\n    WSTO.Cells(末行, 1).Value = "持仓"'
# Find the end: 末行 = 17 followed by 仓位目标
mark2 = '末行 = 17\n    WSTO.Cells(末行, 1).Value = "仓位目标"'

idx1 = text.find(mark1)
if idx1 < 0:
    # Try with bold line
    idx1 = text.find('末行 = 5\n    WSTO.Cells(末行, 1).Value = "持仓"\n    WSTO.Cells(末行, 2).Value = 福票数')
    if idx1 < 0:
        print("ERROR: start not found")
        exit(1)

idx2 = text.find(mark2)
if idx2 < 0:
    print("ERROR: end not found")
    exit(1)

# Find the end of the 仓位目标 block
# The block ends at the line after the last If statement for 仓位目标
after_仓位目标 = text.find('If 福总资 + 彦总资 > 0 Then WSTO.Cells(末行, 7).Value = Format(总持仓额 / (福总资 + 彦总资), "0%")', idx2)
if after_仓位目标 < 0:
    print("ERROR: 仓位目标 end not found")
    exit(1)

# Find end of line
eol = text.find('\n', after_仓位目标)
if eol < 0:
    print("ERROR: eol not found")
    exit(1)

end_idx = eol + 1

# Now find the 浅灰间隔 and 数字格式 after this
# These should be replaced too
灰间隔_mark = text.find("'--- 持仓构成数据行(6-13)浅灰间隔 ---", end_idx)
if 灰间隔_mark >= 0 and 灰间隔_mark < end_idx + 200:
    # Find the Next that closes For X = 6 To 13
    next_mark = text.find('\n    Next\n', 灰间隔_mark)
    if next_mark > 0:
        end_idx = next_mark + 10  # len('\n    Next\n') = 10

# Find the 数字格式 section
数格_mark = text.find("'--- 概览/持仓构成数字格式 ---", end_idx)
if 数格_mark >= 0 and 数格_mark < end_idx + 200:
    next_mark = text.find('\n    Next', 数格_mark)
    if next_mark > 0:
        end_idx = next_mark + 10  # len('\n    Next') = 10

# New block: 总资产 at 行5, 现金余额 at 行6, 持仓 at 行7, 持仓构成 at 行8-15, 满仓率 at 行16
new_block = '末行 = 5\n    WSTO.Cells(末行, 1).Value = "总资产(千元)"\n    WSTO.Cells(末行, 3).Value = Round(福总资, 1)\n    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 5).Value = Round(彦总资, 1)\n    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 7).Value = Round(福总资 + 彦总资, 1)\n    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    WSTO.Rows(末行).Font.Bold = True\n    末行 = 6\n    WSTO.Cells(末行, 1).Value = "现金余额(千元)"\n    WSTO.Cells(末行, 3).Value = Round(福现金, 1)\n    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 5).Value = Round(彦现金, 1)\n    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 7).Value = Round(福现金 + 彦现金, 1)\n    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    WSTO.Rows(末行).Font.Bold = True\n    末行 = 7\n    WSTO.Cells(末行, 1).Value = "持仓"\n    WSTO.Cells(末行, 2).Value = 福票数\n    WSTO.Cells(末行, 3).Value = Round(福仓额, 1)\n    WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦票数\n    WSTO.Cells(末行, 5).Value = Round(彦仓额, 1)\n    WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = 持票数\n    WSTO.Cells(末行, 7).Value = Round(总持仓额, 1)\n    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    WSTO.Rows(末行).Font.Bold = True\n    \'--- 持仓构成（直接展开在持仓之下） ---\n    末行 = 8\n    WSTO.Cells(末行, 1).Value = "  \u251c\u2500ETF"\n    WSTO.Cells(末行, 2).Value = 福ETF数: WSTO.Cells(末行, 3).Value = Round(福ETF额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦ETF数: WSTO.Cells(末行, 5).Value = Round(彦ETF额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = ETF数: WSTO.Cells(末行, 7).Value = Round(ETF额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    WSTO.Rows(末行).Font.Bold = True\n    末行 = 9\n    WSTO.Cells(末行, 1).Value = "  \u2514\u2500股票"\n    WSTO.Cells(末行, 2).Value = 福股数: WSTO.Cells(末行, 3).Value = Round(福股额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦股数: WSTO.Cells(末行, 5).Value = Round(彦股额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = 持票数 - ETF数: WSTO.Cells(末行, 7).Value = Round(总持仓额 - ETF额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    WSTO.Rows(末行).Font.Bold = True\n    \'交易所细分\n    末行 = 10\n    WSTO.Cells(末行, 1).Value = "   \u251c\u2500上证"\n    WSTO.Cells(末行, 2).Value = 福上证数: WSTO.Cells(末行, 3).Value = Round(福上证额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦上证数: WSTO.Cells(末行, 5).Value = Round(彦上证额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = 上证股数: WSTO.Cells(末行, 7).Value = Round(上证股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 11\n    WSTO.Cells(末行, 1).Value = "   \u251c\u2500科创"\n    WSTO.Cells(末行, 2).Value = 福科创数: WSTO.Cells(末行, 3).Value = Round(福科创额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦科创数: WSTO.Cells(末行, 5).Value = Round(彦科创额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = 科创股数: WSTO.Cells(末行, 7).Value = Round(科创股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 12\n    WSTO.Cells(末行, 1).Value = "   \u251c\u2500深证"\n    WSTO.Cells(末行, 2).Value = 福深证数: WSTO.Cells(末行, 3).Value = Round(福深证额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦深证数: WSTO.Cells(末行, 5).Value = Round(彦深证额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = 深证股数: WSTO.Cells(末行, 7).Value = Round(深证股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 13\n    WSTO.Cells(末行, 1).Value = "   \u251c\u2500创业"\n    WSTO.Cells(末行, 2).Value = 福创业数: WSTO.Cells(末行, 3).Value = Round(福创业额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦创业数: WSTO.Cells(末行, 5).Value = Round(彦创业额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = 创业股数: WSTO.Cells(末行, 7).Value = Round(创业股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 14\n    WSTO.Cells(末行, 1).Value = "   \u251c\u2500北交"\n    WSTO.Cells(末行, 2).Value = 福北交数: WSTO.Cells(末行, 3).Value = Round(福北交额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦北交数: WSTO.Cells(末行, 5).Value = Round(彦北交额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = 北交股数: WSTO.Cells(末行, 7).Value = Round(北交股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 15\n    WSTO.Cells(末行, 1).Value = "   \u2514\u2500港股"\n    WSTO.Cells(末行, 2).Value = 福港股数: WSTO.Cells(末行, 3).Value = Round(福港股额, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = 彦港股数: WSTO.Cells(末行, 5).Value = Round(彦港股额, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = 港股数: WSTO.Cells(末行, 7).Value = Round(港股额, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 16\n    WSTO.Cells(末行, 1).Value = "满仓率"\n    If 福总资 > 0 Then WSTO.Cells(末行, 3).Value = Format(福仓额 / 福总资, "0%")\n    If 彦总资 > 0 Then WSTO.Cells(末行, 5).Value = Format(彦仓额 / 彦总资, "0%")\n    If 福总资 + 彦总资 > 0 Then WSTO.Cells(末行, 7).Value = Format(总持仓额 / (福总资 + 彦总资), "0%")\n    \'--- 持仓构成数据行(8-15)浅灰间隔 ---\n    For X = 8 To 15\n        With WSTO.Range(WSTO.Cells(X, 1), WSTO.Cells(X, 7)).Interior\n            .Color = RGB(245, 245, 245)\n        End With\n    Next\n    \'--- 概览/持仓构成数字格式 ---\n    For X = 5 To 16\n        WSTO.Rows(X).HorizontalAlignment = xlRight\n        WSTO.Cells(X, 1).HorizontalAlignment = xlLeft\n    Next'

text = text[:idx1] + new_block + text[end_idx:]

with open(r'd:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'w', encoding='utf-8') as f:
    f.write(text)

print("OK - replaced from", idx1, "to", end_idx)