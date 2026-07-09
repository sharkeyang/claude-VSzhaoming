"""调试: 找每日最高价/最低价/收盘价列"""
import win32com.client, os, datetime, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

code = 'sz159919'
fp = os.path.join(D, f'算展.{code}.xlsx')
wb = excel.Workbooks.Open(fp)
ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
ws = wb.Sheets(ld)
rows = ws.UsedRange.Rows.Count

# 先找表头含"开盘/最高/最低/收盘"的列
headers = ws.Range(ws.Cells(1,1), ws.Cells(1,310)).Value[0]
print(f'{code} 表头含"开/高/低/收"的列:')
for i, h in enumerate(headers, 1):
    if h and any(k in str(h) for k in ['开','高','低','收','涨']):
        print(f'  col{i}: {str(h).replace(chr(10)," ").strip()!r}')

# 读前20行关键OHLC列验证
row2 = [ws.Cells(2,c).Value for c in range(1, 60)]
row3 = [ws.Cells(3,c).Value for c in range(1, 60)]
row4 = [ws.Cells(4,c).Value for c in range(1, 60)]

print('\n前3行关键列对比:')
key_cols = [4,9,28,29,30,31,32,33,34,35,36]
for r_idx, r in enumerate([row2, row3, row4], 2):
    vals = {c: r[c-1] for c in key_cols}
    print(f'  row{r_idx}: col4(主期)={vals[4]}  col9(日涨)={vals[9]}'
          f'  P0(col29)={vals[29]}  H3(col34)={vals[34]}  结价(col36)={vals[36]}')

# 检查第1周(第1-5行)每天的高/低价
print('\n第1周5天的高/低价对比:')
for r_idx in range(2, 7):
    r = [ws.Cells(r_idx,c).Value for c in range(1, 310)]
    vals = {c: r[c-1] for c in range(28, 38)}
    print(f'  row{r_idx}: '
          f'P0={vals[28]} P1={vals[29]} P3={vals[30]} '
          f'H0={vals[31]} H1={vals[32]} H3={vals[33]} H9={vals[34]} '
          f'结价={vals[35]}')

# 找col90-120中可能的日高/日低
print('\ncol88-120含"高/低"的表头:')
for i in range(88, 121):
    h = headers[i-1] if i <= len(headers) else None
    if h and any(k in str(h) for k in ['高','低']):
        print(f'  col{i}: {str(h).replace(chr(10)," ").strip()!r}')

wb.Close(False)