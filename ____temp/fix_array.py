import sys
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

with open('昭明计划VS优化_vba/PX算研_ZSM交割单.bas', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add array initialization after WS出.Cells(1,1) = "证券代码"
init_old = 'WS出.Cells(1, 1) = "证券代码"'
init_new = 'WS出.Cells(1, 1) = "证券代码"\n    ReDim 割单数组(1 To 5000, 1 To 常割单列数)\n    割单行数 = 0'
content = content.replace(init_old, init_new, 1)

# 2. Mark the three output points with array writes
# Point A: 配对部分 (line 1587-1588)
pa_old = 'WS出.Cells(行号, 8) = "配对交易"\n                    行号 = 行号 + 1\n                End If\n                WS出.Cells(行号, 3) = ""\n                WS出.Cells(行号, 4) = ARRYM(r, 1)\n                WS出.Cells(行号, 5) = 类别r\n                WS出.Cells(行号, 6) = 未配对\n                WS出.Cells(行号, 7) = Val(ARRYM(r, 9)) * 未配对 / qty\n                WS出.Cells(行号, 8) = "未配对交易"'
pa_new = 'WS出.Cells(行号, 8) = "配对交易"\n                    行号 = 行号 + 1\n                    割单行数 = 割单行数 + 1\n                    割单数组(割单行数, 1) = ARRYM(r, 1)\n                    割单数组(割单行数, 4) = sCIDL\n                    割单数组(割单行数, 5) = 名称\n                    割单数组(割单行数, 6) = 类别r\n                    割单数组(割单行数, 8) = 配对数量\n                    割单数组(割单行数, 9) = Val(ARRYM(r, 9)) * 配对数量 / qty\n                    割单数组(割单行数, 常割单列状态) = "配对交易"\n                    割单数组(割单行数, 常割单列配对类型) = "和持仓配对"\n                    割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(r, 3))\n                End If\n                WS出.Cells(行号, 3) = ""\n                WS出.Cells(行号, 4) = ARRYM(r, 1)\n                WS出.Cells(行号, 5) = 类别r\n                WS出.Cells(行号, 6) = 未配对\n                WS出.Cells(行号, 7) = Val(ARRYM(r, 9)) * 未配对 / qty\n                WS出.Cells(行号, 8) = "未配对交易"'

# Point B: 未配对部分 (line 1595-1598)
pb_old = 'WS出.Cells(行号, 8) = "未配对交易"\n                WS出.Rows(行号).Interior.Color = 常色十红\n                行号 = 行号 + 1\n                总不完整 = 总不完整 + 1\n            Else'
pb_new = 'WS出.Cells(行号, 8) = "未配对交易"\n                WS出.Rows(行号).Interior.Color = 常色十红\n                割单行数 = 割单行数 + 1\n                割单数组(割单行数, 1) = ARRYM(r, 1)\n                割单数组(割单行数, 4) = sCIDL\n                割单数组(割单行数, 5) = 名称\n                割单数组(割单行数, 6) = 类别r\n                割单数组(割单行数, 8) = 未配对\n                割单数组(割单行数, 9) = Val(ARRYM(r, 9)) * 未配对 / qty\n                割单数组(割单行数, 常割单列状态) = "未配对交易"\n                割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(r, 3))\n                行号 = 行号 + 1\n                总不完整 = 总不完整 + 1\n            Else'

# Point C: 正常交易 (line 1600-1606)
pc_old = 'WS出.Cells(行号, 3) = ""\n                WS出.Cells(行号, 4) = ARRYM(r, 1)\n                WS出.Cells(行号, 5) = 类别r\n                WS出.Cells(行号, 6) = qty\n                WS出.Cells(行号, 7) = Val(ARRYM(r, 9))\n                WS出.Cells(行号, 8) = "配对交易"\n                行号 = 行号 + 1\n            End If\n        Next\n        跳过:'
pc_new = 'WS出.Cells(行号, 3) = ""\n                WS出.Cells(行号, 4) = ARRYM(r, 1)\n                WS出.Cells(行号, 5) = 类别r\n                WS出.Cells(行号, 6) = qty\n                WS出.Cells(行号, 7) = Val(ARRYM(r, 9))\n                WS出.Cells(行号, 8) = "配对交易"\n                行号 = 行号 + 1\n                割单行数 = 割单行数 + 1\n                割单数组(割单行数, 1) = ARRYM(r, 1)\n                割单数组(割单行数, 4) = sCIDL\n                割单数组(割单行数, 5) = 名称\n                割单数组(割单行数, 6) = 类别r\n                割单数组(割单行数, 8) = qty\n                割单数组(割单行数, 9) = Val(ARRYM(r, 9))\n                割单数组(割单行数, 常割单列状态) = "配对交易"\n                割单数组(割单行数, 常割单列配对类型) = "历史买卖配对"\n                割单数组(割单行数, 常割单列账户) = STCALL割单工具_识别账户(ARRYM(r, 3))\n            End If\n        Next\n        跳过:'

if pa_old in content:
    content = content.replace(pa_old, pa_new, 1)
    print('Point A replaced')
else:
    print('Point A not found')

if pb_old in content:
    content = content.replace(pb_old, pb_new, 1)
    print('Point B replaced')
else:
    print('Point B not found')

if pc_old in content:
    content = content.replace(pc_old, pc_new, 1)
    print('Point C replaced')
else:
    print('Point C not found')

with open('昭明计划VS优化_vba/PX算研_ZSM交割单.bas', 'w', encoding='utf-8') as f:
    f.write(content)

print('Done')