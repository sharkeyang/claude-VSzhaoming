# -*- coding: utf-8 -*-
"""将硬编码行号改为相对递增模式，操作副本文件"""
import re

src = r'd:\@VSwork\VS昭明计划VBA优化\____temp\IQQQ跨码_D据擎4跨码管理_相对行号.bas'

with open(src, 'rb') as f:
    raw = f.read()
text = raw.decode('utf-8')
NL = '\r\n'

# 验证文件内容
assert '末行 = 5' + NL + '    WSTO.Cells(末行, 1).Value = "持仓"' in text, '文件不是预期格式'

# ============================================================
# Phase 1: 概览区 - 末行 = N → 末行 = 末行 + 1
# ============================================================

# 1.1 插入 概览始 变量（在第一个 末行=5 之前）
old = '末行 = 5' + NL + '    WSTO.Cells(末行, 1).Value = "持仓"'
new = 'Dim 概览始 As Integer: 概览始 = 末行 + 1' + NL + old
text = text.replace(old, new, 1)

# 1.2 替换概览区 末行 = N → 末行 = 末行 + 1
for n in range(5, 17):
    old = '    末行 = ' + str(n) + NL + '    '
    new = '    末行 = 末行 + 1' + NL + '    '
    if old in text:
        text = text.replace(old, new, 1)
    else:
        # 尝试不带后续缩进（行末）
        old = '    末行 = ' + str(n) + NL
        new = '    末行 = 末行 + 1' + NL
        text = text.replace(old, new, 1)

# 1.3 替换格式化范围
text = text.replace('For X = 6 To 13', 'For X = 概览始 + 1 To 末行 - 1', 1)
text = text.replace('For X = 5 To 17', 'For X = 概览始 To 末行', 1)

# ============================================================
# Phase 2: 大盘仓位限制区
# ============================================================

# 2.1 插入 大盘始 变量
old = 'WSTO.Cells(18, 8).Value = 大盘评分明细'
new = 'Dim 大盘始 As Integer: 大盘始 = 末行 + 1' + NL + old
text = text.replace(old, new, 1)

# 2.2 替换所有 WSTO.Cells(18,
repls = [
    ('WSTO.Cells(18, 8).Value', 'WSTO.Cells(大盘始, 8).Value'),
    ('WSTO.Cells(18, 8).Font.Size', 'WSTO.Cells(大盘始, 8).Font.Size'),
    ('WSTO.Cells(18, 8).Font.Color', 'WSTO.Cells(大盘始, 8).Font.Color'),
    ('WSTO.Range(WSTO.Cells(18, 8), WSTO.Cells(18, 14)).Merge',
     'WSTO.Range(WSTO.Cells(大盘始, 8), WSTO.Cells(大盘始, 14)).Merge'),
    ('WSTO.Cells(18, 1).Value = "大盘仓位限制"', 'WSTO.Cells(大盘始, 1).Value = "大盘仓位限制"'),
    ('WSTO.Cells(18, 3).Value = Format(总上限, "0%")', 'WSTO.Cells(大盘始, 3).Value = Format(总上限, "0%")'),
    ('WSTO.Cells(18, 5).Value = Format(总上限, "0%")', 'WSTO.Cells(大盘始, 5).Value = Format(总上限, "0%")'),
    ('WSTO.Cells(18, 7).Value = Format(总上限, "0%")', 'WSTO.Cells(大盘始, 7).Value = Format(总上限, "0%")'),
    ('WSTO.Rows(18).HorizontalAlignment', 'WSTO.Rows(大盘始).HorizontalAlignment'),
]
for old, new in repls:
    text = text.replace(old, new, 1)

# 2.3 替换 大盘行 = N → 大盘行 = 大盘行 + 1
# 第一个 大盘行=19（变量声明区）
old = '    大盘行 = 19' + NL + '    \'福账户'
new = '    大盘行 = 大盘始 + 1' + NL + '    \'福账户'
if old in text:
    text = text.replace(old, new, 1)
else:
    old = '    大盘行 = 19' + NL + '    WSTO.Cells(大盘行, 1).Value = "福账户限额"'
    new = '    大盘行 = 大盘行 + 1' + NL + '    WSTO.Cells(大盘行, 1).Value = "福账户限额"'
    text = text.replace(old, new, 1)

# 剩余的 大盘行 = N（20~28）
for n in range(20, 29):
    old = '    大盘行 = ' + str(n) + NL + '    '
    if old in text:
        text = text.replace(old, '    大盘行 = 大盘行 + 1' + NL + '    ', 1)
    else:
        # 可能行末
        old = '    大盘行 = ' + str(n) + NL
        text = text.replace(old, '    大盘行 = 大盘行 + 1' + NL, 1)

# 2.4 替换右对齐范围
text = text.replace('For X = 18 To 28', 'For X = 大盘始 To 大盘行', 1)

# ============================================================
# Phase 3: 行业分布区
# ============================================================

# 3.1 插入 行业始 变量
old = '    末行 = 32' + NL + '    WSTO.Cells(末行, 1).Value = "二、行业分布"'
new = ('    Dim 行业始 As Integer: 行业始 = 末行 + 2' + NL +
       '    末行 = 行业始' + NL +
       '    WSTO.Cells(末行, 1).Value = "二、行业分布"')
text = text.replace(old, new, 1)

# 3.2 替换 末行=33 → 末行=末行+1
old = '    末行 = 33' + NL + '    WSTO.Cells(末行, 1).Value = "行业"'
text = text.replace(old, '    末行 = 末行 + 1' + NL + '    WSTO.Cells(末行, 1).Value = "行业"', 1)

# 3.3 替换 末行=34 → 末行=末行+1
old = '    末行 = 34' + NL + '    For Each 行业 In 行业典集.Keys'
text = text.replace(old, '    末行 = 末行 + 1' + NL + '    For Each 行业 In 行业典集.Keys', 1)

# 3.4 替换格式化范围
text = text.replace('For X = 32 To 末行整', 'For X = 行业始 To 末行整', 1)
text = text.replace("WSTO.Rows(32).RowHeight = 20  '行业表头行高", "WSTO.Rows(行业始).RowHeight = 20  '行业表头行高", 1)

# ============================================================
# 写入
# ============================================================
raw_out = text.encode('utf-8')
with open(src, 'wb') as f:
    f.write(raw_out)

print('OK')