# -*- coding: utf-8 -*-
"""从花册读取市板数据，用于V2评分验证"""
import os, shutil, csv, time, atexit
import win32com.client

SRC = r"d:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化.xlsm"
TEMP = r"d:\@VSwork\VS昭明计划VBA优化\____temp"
TEMP_XLSM = os.path.join(TEMP, "_temp_花册读取.xlsm")
PWD = "1376435"

# 复制到临时文件
shutil.copy2(SRC, TEMP_XLSM)
print(f"复制到: {TEMP_XLSM}")

# 启动独立Excel进程
excel = win32com.client.DispatchEx("Excel.Application")
excel.Visible = False
excel.DisplayAlerts = False

wb = None
try:
    wb = excel.Workbooks.Open(TEMP_XLSM, Password:=PWD)
    ws = wb.Sheets("花天中股")
    print(f"花册行数: {ws.UsedRange.Rows.Count}")

    # 读取CIDL列和市板列
    # 需要找到位列花天CIDL和位列花天市板的列号
    # 从SET_设0常量1.bas看: 位qt市板 = 18
    # 从花册管理看: 列号需要从表头找

    # 读取表头
    headers = []
    for col in range(1, 100):
        val = ws.Cells(1, col).Value
        if val is None:
            break
        headers.append(str(val).strip())

    print(f"表头列数: {len(headers)}")

    # 找CIDL列和市板列
    cidl_col = None
    市板_col = None
    for i, h in enumerate(headers):
        if "CIDL" in h.upper() or "代码" in h:
            cidl_col = i + 1
        if "市板" in h:
            市板_col = i + 1

    print(f"CIDL列: {cidl_col}, 市板列: {市板_col}")

    if cidl_col is None or 市板_col is None:
        print("错误: 找不到列")
        # 打印所有表头
        for i, h in enumerate(headers):
            print(f"  {i+1}: {h}")
    else:
        # 读取所有数据
        市板映射 = {}
        last_row = ws.UsedRange.Rows.Count
        for r in range(2, last_row + 1):
            cidl = ws.Cells(r, cidl_col).Value
            市板 = ws.Cells(r, 市板_col).Value
            if cidl and 市板:
                市板映射[str(cidl).strip()] = str(市板).strip()

        print(f"读取市板数据: {len(市板映射)}条")

        # 输出到CSV
        csv_out = os.path.join(TEMP, "市板映射.csv")
        with open(csv_out, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["代码", "市板"])
            for cidl, 市板 in sorted(市板映射.items()):
                w.writerow([cidl, 市板])
        print(f"已保存: {csv_out}")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    if wb:
        wb.Close(SaveChanges=False)
    excel.Quit()
    import win32com.client
    # 清理临时文件
    if os.path.exists(TEMP_XLSM):
        os.remove(TEMP_XLSM)