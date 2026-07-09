"""检查 col46/col108/col109 等每日变化列的列名"""
import win32com.client, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

code = 'sz159919'
fp = os.path.join(D, f'算展.{code}.xlsx')
wb = excel.Workbooks.Open(fp)
ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
ws = wb.Sheets(ld)
headers = ws.Range(ws.Cells(1,1), ws.Cells(1,310)).Value[0]

# 扫col1-120列名
print('每日变化的列名:')
interesting = [4,9,46,47,77,78,79,80,81,82,85,88,89,90,91,93,94,95,96,106,107,108,109,110]
for c in interesting:
    h = headers[c-1] if c <= len(headers) else 'N/A'
    print(f'  col{c}: {str(h).replace(chr(10)," ").strip()!r}')

# 看col46+47 前5行值
arr = ws.Range(ws.Cells(2,1), ws.Cells(10,310)).Value
print('\ncol46-47前5行:')
for r in range(5):
    print(f'  row{r+2}: col46={arr[r][45]}, col47={arr[r][46]}')

# 尝试用col36(结价)找每周首日的真实收盘
# 然后用日涨推导每日收盘价，再找最大收盘
print('\n推导每日收盘价(从col36首日值 + 日涨累积):')
# 第1周
c = arr[0][35]  # col36 of first day
print(f'  首日结价={c}')
for r in range(5):
    if r > 0:
        c *= (1 + arr[r][8]/100)
    print(f'    day{r+1}: 收盘≈{c:.4f} (日涨={arr[r][8]}%)')

# 看col34的最後一個值(周五)與col36首日值
print(f'\n  周五col34(H3)={arr[4][33]}, 下周一col36={arr[5][35] if len(arr)>5 else "N/A"}')

wb.Close(False)