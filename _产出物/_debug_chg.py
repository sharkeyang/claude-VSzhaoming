"""调试: 检查算展文件 col5(涨幅) 的实际数值范围"""
import win32com.client, os, datetime

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

code = 'sz159919'
fp = os.path.join(D, f'算展.{code}.xlsx')
wb = excel.Workbooks.Open(fp)
ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
ws = wb.Sheets(ld)
rows = ws.UsedRange.Rows.Count
arr = ws.Range(ws.Cells(2,1), ws.Cells(rows,10)).Value
wb.Close(False)

print(f'{code} 前10行:')
print(f'{"行":>3} {"col1龄":>6} {"col2期":>12} {"col3键":>5} {"col4七":>5} {"col5涨":>10}')
for r in range(min(10, len(arr))):
    row = arr[r]
    dt = row[1]
    if isinstance(dt, (int,float)):
        dts = str((datetime.datetime(1899,12,30)+datetime.timedelta(days=int(dt))).date())
    else:
        dts = str(dt)
    print(f'{r:>3} {str(row[0]):>6} {dts:>12} {str(row[2]):>5} {str(row[3]):>5} {row[4]!r:>10}')

# 统计 col5 数值范围
vals = [row[4] for row in arr if isinstance(row[4], (int,float))]
if vals:
    print(f'\ncol5(涨) 数值统计:')
    print(f'  样本数: {len(vals)}')
    print(f'  最小值: {min(vals)}')
    print(f'  最大值: {max(vals)}')
    print(f'  均值: {sum(vals)/len(vals):.4f}')
    print(f'  前10个值: {vals[:10]}')
