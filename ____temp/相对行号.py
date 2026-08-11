# -*- coding: utf-8 -*-
"""将硬编码行号改为相对递增模式，操作副本文件"""
import re

src = r'd:\@VSwork\VS昭明计划VBA优化\____temp\IQQQ跨码_D据擎4跨码管理_相对行号.bas'

with open(src, 'r', encoding='utf-8') as f:
    text = f.read()

# ============================================================
# Phase 1: 概览区 — 末行 = N → 末行 = 末行 + 1
# ============================================================

# 1.1 插入 概览始 变量（在第一个 末行=5 之前）
old = '末行 = 5\n    WSTO.Cells(末行, 1).Value = "总资产(千元)"'
new = 'Dim 概览始 As Integer: 概览始 = 末行 + 1\n' + old
text = text.replace(old, new, 1)

# 1.2 替换概览区所有 末行 = N → 末行 = 末行 + 1（N=5~16）
for n in range(5, 17):
    # 每个替换只替换1次，确保不会误改其他区段
    text = text.replace('\n末行 = ' + str(n) + '\n', '\n末行 = 末行 + 1\n', 1)

# 1.3 替换格式化范围
text = text.replace('For X = 6 To 13', 'For X = 概览始 + 1 To 末行 - 1', 1)
text = text.replace('For X = 5 To 17', 'For X = 概览始 To 末行', 1)

# ============================================================
# Phase 2: 大盘仓位限制区
# ============================================================

# 2.1 插入 大盘始 变量（在 WSTO.Cells(18, 8) 之前）
old = "WSTO.Cells(18, 8).Value = 大盘评分明细"
new = "Dim 大盘始 As Integer: 大盘始 = 末行 + 1\n" + old
text = text.replace(old, new, 1)

# 2.2 替换所有 WSTO.Cells(18, → WSTO.Cells(大盘始,
text = text.replace('WSTO.Cells(18, 8).Value', 'WSTO.Cells(大盘始, 8).Value')
text = text.replace('WSTO.Cells(18, 8).Font.Size', 'WSTO.Cells(大盘始, 8).Font.Size')
text = text.replace('WSTO.Cells(18, 8).Font.Color', 'WSTO.Cells(大盘始, 8).Font.Color')
text = text.replace('WSTO.Range(WSTO.Cells(18, 8), WSTO.Cells(18, 14)).Merge',
                     'WSTO.Range(WSTO.Cells(大盘始, 8), WSTO.Cells(大盘始, 14)).Merge')
text = text.replace('WSTO.Cells(18, 1).Value = "大盘仓位限制"', 'WSTO.Cells(大盘始, 1).Value = "大盘仓位限制"', 1)
text = text.replace('WSTO.Cells(18, 3).Value = Format(总上限, "0%")', 'WSTO.Cells(大盘始, 3).Value = Format(总上限, "0%")', 1)
text = text.replace('WSTO.Cells(18, 5).Value = Format(总上限, "0%")', 'WSTO.Cells(大盘始, 5).Value = Format(总上限, "0%")', 1)
text = text.replace('WSTO.Cells(18, 7).Value = Format(总上限, "0%")', 'WSTO.Cells(大盘始, 7).Value = Format(总上限, "0%")', 1)
text = text.replace('WSTO.Rows(18).HorizontalAlignment', 'WSTO.Rows(大盘始).HorizontalAlignment')

# 2.3 替换 大盘行 = N → 大盘行 = 大盘行 + 1（N=19~28）
# 注意：第1个 大盘行=19 是变量声明区，改成 大盘行 = 大盘始 + 1
first_replace = text.replace('大盘行 = 19\n    \'福账户', '大盘行 = 大盘始 + 1\n    \'福账户', 1)
if first_replace != text:
    text = first_replace
else:
    # Try alternate
    text = text.replace('大盘行 = 19\n    \'福账户', '大盘行 = 大盘始 + 1\n    \'福账户', 1)

# 剩余的 大盘行 = N（19~28）
for n in range(19, 29):
    # 每个替换只替换1次
    text = text.replace('\n大盘行 = ' + str(n) + '\n', '\n大盘行 = 大盘行 + 1\n', 1)

# 2.4 替换右对齐范围
text = text.replace('For X = 18 To 28', 'For X = 大盘始 To 大盘行', 1)

# ============================================================
# Phase 3: 行业分布区
# ============================================================

# 3.1 插入 行业始 变量（在 末行=32 之前）
old = '末行 = 32\n    WSTO.Cells(末行, 1).Value = "二、行业分布"'
new = 'Dim 行业始 As Integer: 行业始 = 末行 + 2\n    末行 = 行业始\n    WSTO.Cells(末行, 1).Value = "二、行业分布"'
text = text.replace(old, new, 1)

# 3.2 替换 末行=33 → 末行=末行+1（header）
text = text.replace('末行 = 33\n    WSTO.Cells(末行, 1).Value = "行业"', '末行 = 末行 + 1\n    WSTO.Cells(末行, 1).Value = "行业"', 1)

# 3.3 替换 末行=34 → 末行=末行+1（data start）
text = text.replace('末行 = 34\n    For Each 行业 In 行业典集.Keys', '末行 = 末行 + 1\n    For Each 行业 In 行业典集.Keys', 1)

# 3.4 替换格式化范围
text = text.replace('For X = 32 To 末行整', 'For X = 行业始 To 末行整', 1)
text = text.replace('WSTO.Rows(32).RowHeight = 20  \'行业表头行高', 'WSTO.Rows(行业始).RowHeight = 20  \'行业表头行高', 1)

# ============================================================
# 写入
# ============================================================
with open(src, 'w', encoding='utf-8') as f:
    f.write(text)

print("OK - 相对行号已写入副本")