# -*- coding: utf-8 -*-
import re

with open(r'D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'r', encoding='utf-8') as f:
    text = f.read()

# Step 1: Insert 持仓构成 data after 持仓 row
old = 'WSTO.Cells(末行, 7).Value = Round(总持仓额, 1)\n    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 6\n    WSTO.Cells(末行, 1).Value = "现金余额"'

new = 'WSTO.Cells(末行, 7).Value = Round(总持仓额, 1)\n    WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 6\n    WSTO.Cells(末行, 1).Value = "  \u251c\u2500ETF"\n    WSTO.Cells(末行, 2).Value = \u798fETF\u6570: WSTO.Cells(末行, 3).Value = Round(\u798fETF\u989d, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = \u5f66ETF\u6570: WSTO.Cells(末行, 5).Value = Round(\u5f66ETF\u989d, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = ETF\u6570: WSTO.Cells(末行, 7).Value = Round(ETF\u989d, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 7\n    WSTO.Cells(末行, 1).Value = "  \u2514\u2500\u80a1\u7968"\n    WSTO.Cells(末行, 2).Value = \u798f\u80a1\u6570: WSTO.Cells(末行, 3).Value = Round(\u798f\u80a1\u989d, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = \u5f66\u80a1\u6570: WSTO.Cells(末行, 5).Value = Round(\u5f66\u80a1\u989d, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = \u6301\u7968\u6570 - ETF\u6570: WSTO.Cells(末行, 7).Value = Round(\u603b\u6301\u4ed3\u989d - ETF\u989d, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 8\n    WSTO.Cells(末行, 1).Value = "    \u251c\u2500\u4e0a\u8bc1"\n    WSTO.Cells(末行, 2).Value = \u798f\u4e0a\u8bc1\u6570: WSTO.Cells(末行, 3).Value = Round(\u798f\u4e0a\u8bc1\u989d, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = \u5f66\u4e0a\u8bc1\u6570: WSTO.Cells(末行, 5).Value = Round(\u5f66\u4e0a\u8bc1\u989d, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = \u4e0a\u8bc1\u80a1\u6570: WSTO.Cells(末行, 7).Value = Round(\u4e0a\u8bc1\u80a1\u989d, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 9\n    WSTO.Cells(末行, 1).Value = "    \u251c\u2500\u79d1\u521b"\n    WSTO.Cells(末行, 2).Value = \u798f\u79d1\u521b\u6570: WSTO.Cells(末行, 3).Value = Round(\u798f\u79d1\u521b\u989d, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = \u5f66\u79d1\u521b\u6570: WSTO.Cells(末行, 5).Value = Round(\u5f66\u79d1\u521b\u989d, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = \u79d1\u521b\u80a1\u6570: WSTO.Cells(末行, 7).Value = Round(\u79d1\u521b\u80a1\u989d, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 10\n    WSTO.Cells(末行, 1).Value = "    \u251c\u2500\u6df1\u8bc1"\n    WSTO.Cells(末行, 2).Value = \u798f\u6df1\u8bc1\u6570: WSTO.Cells(末行, 3).Value = Round(\u798f\u6df1\u8bc1\u989d, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = \u5f66\u6df1\u8bc1\u6570: WSTO.Cells(末行, 5).Value = Round(\u5f66\u6df1\u8bc1\u989d, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = \u6df1\u8bc1\u80a1\u6570: WSTO.Cells(末行, 7).Value = Round(\u6df1\u8bc1\u80a1\u989d, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 11\n    WSTO.Cells(末行, 1).Value = "    \u251c\u2500\u521b\u4e1a"\n    WSTO.Cells(末行, 2).Value = \u798f\u521b\u4e1a\u6570: WSTO.Cells(末行, 3).Value = Round(\u798f\u521b\u4e1a\u989d, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = \u5f66\u521b\u4e1a\u6570: WSTO.Cells(末行, 5).Value = Round(\u5f66\u521b\u4e1a\u989d, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = \u521b\u4e1a\u80a1\u6570: WSTO.Cells(末行, 7).Value = Round(\u521b\u4e1a\u80a1\u989d, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 12\n    WSTO.Cells(末行, 1).Value = "    \u251c\u2500\u5317\u4ea4"\n    WSTO.Cells(末行, 2).Value = \u798f\u5317\u4ea4\u6570: WSTO.Cells(末行, 3).Value = Round(\u798f\u5317\u4ea4\u989d, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = \u5f66\u5317\u4ea4\u6570: WSTO.Cells(末行, 5).Value = Round(\u5f66\u5317\u4ea4\u989d, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = \u5317\u4ea4\u80a1\u6570: WSTO.Cells(末行, 7).Value = Round(\u5317\u4ea4\u80a1\u989d, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 13\n    WSTO.Cells(末行, 1).Value = "    \u2514\u2500\u6e2f\u80a1"\n    WSTO.Cells(末行, 2).Value = \u798f\u6e2f\u80a1\u6570: WSTO.Cells(末行, 3).Value = Round(\u798f\u6e2f\u80a1\u989d, 1): WSTO.Cells(末行, 3).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 4).Value = \u5f66\u6e2f\u80a1\u6570: WSTO.Cells(末行, 5).Value = Round(\u5f66\u6e2f\u80a1\u989d, 1): WSTO.Cells(末行, 5).NumberFormatLocal = "#,##0.0"\n    WSTO.Cells(末行, 6).Value = \u6e2f\u80a1\u6570: WSTO.Cells(末行, 7).Value = Round(\u6e2f\u80a1\u989d, 1): WSTO.Cells(末行, 7).NumberFormatLocal = "#,##0.0"\n    末行 = 14\n    WSTO.Cells(末行, 1).Value = "\u73b0\u91d1\u4f59\u989d"'

text = text.replace(old, new, 1)

# Step 2: Shift 末行 values 6-9 to 14-17
for old_n in range(6, 10):
    new_n = old_n + 8
    text = re.sub(rf'末行 = {old_n}\n', f'末行 = {new_n}\n', text)

# Step 3: Shift 大盘行 values 10-20 to 18-28
for old_n in range(10, 21):
    new_n = old_n + 8
    text = re.sub(rf'大盘行 = {old_n}\n', f'大盘行 = {new_n}\n', text)

# Step 4: Update 大盘评分明细
text = text.replace('WSTO.Cells(9, 8).Value', 'WSTO.Cells(17, 8).Value')
text = text.replace('WSTO.Cells(9, 8).Font.Size', 'WSTO.Cells(17, 8).Font.Size')
text = text.replace('WSTO.Cells(9, 8).Font.Color', 'WSTO.Cells(17, 8).Font.Color')
text = text.replace('WSTO.Range(WSTO.Cells(9, 8), WSTO.Cells(9, 14)).Merge', 'WSTO.Range(WSTO.Cells(17, 8), WSTO.Cells(17, 14)).Merge')

# Step 5: Update 行业分布
text = text.replace('\n末行 = 31\n', '\n末行 = 39\n')
text = text.replace('\n末行 = 32\n', '\n末行 = 40\n')
text = text.replace('\n末行 = 33\n', '\n末行 = 41\n')

# Step 6: Update formatting references
text = text.replace('WSTO.Rows(32).RowHeight', 'WSTO.Rows(40).RowHeight')
text = text.replace('行业分布表头(行32)', '行业分布表头(行40)')
text = text.replace('WSTO.Cells(32, 1), WSTO.Cells(32, 14)', 'WSTO.Cells(40, 1), WSTO.Cells(40, 14)')
text = text.replace('行业分布数据行(33至末行)', '行业分布数据行(41至末行)')
text = text.replace('For X = 33 To 末行整', 'For X = 41 To 末行整')

# Step 7: Update 大盘仓位限制 data range
text = text.replace('大盘仓位限制数据行(10-20)', '大盘仓位限制数据行(18-28)')
text = text.replace('For X = 10 To 20', 'For X = 18 To 28')

# Step 8: Update 右对齐
text = text.replace('For X = 10 To 20\n            .Rows(X).HorizontalAlignment', 'For X = 18 To 28\n            .Rows(X).HorizontalAlignment')

# Step 9: Update 各节标题行
text = text.replace('Array(3, 10, 21, 31)', 'Array(3, 18, 29, 39)')

# Step 10: Update 概览/持仓构成右对齐 range
text = text.replace('For X = 5 To 29', 'For X = 5 To 28')

# Step 11: Remove old 持仓构成 formatting references
text = text.replace('    ' + "'--- 持仓构成表头(行21)灰底 ---\n", '')
text = text.replace('    ' + "'--- 持仓构成数据行(22-29)浅灰间隔 ---\n", '')

with open(r'D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas', 'w', encoding='utf-8') as f:
    f.write(text)
print('Done')