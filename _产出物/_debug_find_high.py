"""找到每日变化的列(前5天值不同)，找盘中最高价列"""
import win32com.client, os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

for code in ['sz159919', 'sh512480', 'sz002550']:
    fp = os.path.join(D, f'算展.{code}.xlsx')
    wb = excel.Workbooks.Open(fp)
    ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
    ws = wb.Sheets(ld)
    rows = ws.UsedRange.Rows.Count
    # 批量读前20行
    arr = ws.Range(ws.Cells(2,1), ws.Cells(20,310)).Value
    wb.Close(False)

    # 扫col1~310, 找前5天值不同的列
    varying_cols = []
    for c in range(310):
        vals = [arr[r][c] for r in range(5)]  # 第1周5天
        non_none = [v for v in vals if v is not None]
        if len(non_none) >= 3 and len(set(str(v) for v in non_none)) >= 3:
            varying_cols.append((c+1, vals))

    print(f'\n{code}: 每日变化的列(前5天值差异≥3个) 共{len(varying_cols)}列')
    for col, vals in varying_cols[:20]:
        print(f'  col{col}: {vals}')

    # 特别检查 col34(H3) 和其他可能的最高价列
    print(f'  col34(H3)={[arr[r][33] for r in range(10)]}')
    print(f'  col35(H9)={[arr[r][34] for r in range(10)]}')
    print(f'  col29(P0)={[arr[r][28] for r in range(10)]}')
    print(f'  col30(P1)={[arr[r][29] for r in range(10)]}')
    print(f'  col31(P3)={[arr[r][30] for r in range(10)]}')