"""调试: 验证算展文件WXCD/柱排/ZA周等关键列的位置"""
import win32com.client, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

code = 'sz159919'
fp = os.path.join(D, f'算展.{code}.xlsx')
wb = excel.Workbooks.Open(fp)
ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
ws = wb.Sheets(ld)

# 读表头到310列
headers = ws.Range(ws.Cells(1,1), ws.Cells(1,310)).Value[0]
print(f'{code} LD sheet 关键列查找:')
lookups = ['大局','护型','柱排','ZA','ZC','波型','盈提示','日层','机警','日涨','四域','BTZ','结价','叠幅','涨幅迷']
cols_found = {}
for i, h in enumerate(headers, 1):
    if h:
        hs = str(h).replace('\n',' ').strip()
        for kw in lookups:
            if kw in hs:
                cols_found.setdefault(kw, []).append((i, hs))
for kw in sorted(cols_found):
    for i, hs in cols_found[kw]:
        print(f'  col{i}: {hs}')

# 验证值: 读第3行数据验证
print('\n第3行, 已知关键列:')
row3 = ws.Range(ws.Cells(3,1), ws.Cells(3,310)).Value[0]
print(f'  col4(主期): {row3[3]}')
print(f'  col9(日涨): {row3[8]}')
print(f'  col10(周涨): {row3[9]}')
# 验证WXCD/柱排/ZA
for name, col in [('ZA周',282),('ZC周',284),('柱排周',82),('大局WXCD',88),('护型WXAB',79)]:
    val = row3[col-1] if col <= len(row3) else 'N/A'
    print(f'  col{col}({name}): {val!r}')

# 验证1行完整数据
print('\n最后1行(最后10列):')
last = ws.Range(ws.Cells(ws.UsedRange.Rows.Count,1), ws.Cells(ws.UsedRange.Rows.Count,310)).Value[0]
# 检查col79-90
print('  col79-90:', [f'col{i}={last[i-1]!r}' for i in range(79,91)])
# 检查col280-290
print('  col280-290:', [f'col{i}={last[i-1]!r}' for i in range(280,291)])

wb.Close(False)