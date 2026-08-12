# -*- coding: utf-8 -*-
"""从花册外部工作簿导出 花天 表 CIDL→市板 映射"""
import os, csv, io
import win32com.client

OUT = os.path.join('____temp', '花册_市板映射.csv')

xl = win32com.client.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

try:
    wb = xl.Workbooks.Open('D:/zdata/昭明花册.xlsx', ReadOnly=True)
    ws = wb.Worksheets('花天')

    # 读取CIDL(1)和市板(3)
    rows = []
    r = 2  # 第1行表头
    while True:
        cidl = ws.Cells(r, 1).Value
        if cidl is None or str(cidl).strip() == '':
            break
        board = ws.Cells(r, 3).Value
        rows.append((str(cidl).strip(), str(board).strip() if board else ''))
        r += 1

    print(f'Total rows: {len(rows)}')
    from collections import Counter
    board_cnt = Counter(b for _, b in rows)
    for k, v in sorted(board_cnt.items()):
        print(f'  {k}: {v}')

    with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['CIDL', '市板'])
        for cidl, board in rows:
            w.writerow([cidl, board])

    print(f'Saved: {OUT}')
    wb.Close(SaveChanges=False)

finally:
    xl.Quit()
    import gc; gc.collect()
    import subprocess
    subprocess.run(['taskkill', '/f', '/im', 'EXCEL.EXE'], capture_output=True)

print('Done')