"""调试: 读算展文件表头，找涨幅/WXCD/柱排等正确列号"""
import win32com.client, os, datetime, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

code = 'sz159919'
fp = os.path.join(D, f'算展.{code}.xlsx')
wb = excel.Workbooks.Open(fp)
ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
ws = wb.Sheets(ld)

# 读表头(row1)
headers = ws.Range(ws.Cells(1,1), ws.Cells(1,40)).Value[0]
print(f'{code} LD sheet 表头 (col1-40):')
for i, h in enumerate(headers, 1):
    print(f'  col{i}: {h}')

# 找涨幅相关
print('\n含"涨/幅/收/益"的列:')
for i, h in enumerate(headers, 1):
    if h and any(k in str(h) for k in ['涨','幅','收','益','开','高','低']):
        print(f'  col{i}: {h}')

# 读第3行数据验证
print('\n第3行(col1-15):')
row3 = ws.Range(ws.Cells(3,1), ws.Cells(3,15)).Value[0]
for i, v in enumerate(row3, 1):
    print(f'  col{i}: {v!r}')

wb.Close(False)
