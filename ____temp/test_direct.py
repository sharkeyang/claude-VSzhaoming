# -*- coding: utf-8 -*-
"""直接修改xlsm中的VBA代码，然后测试"""
import os, sys, traceback, win32com.client, pythoncom

pythoncom.CoInitialize()
excel = None
try:
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    xlsm = r'D:\@VSwork\VS昭明计划VBA优化\____temp\昭明计划VS优化_20260803_180051.xlsm'
    wb = excel.Workbooks.Open(xlsm)
    print(f"Opened")

    # 获取模块
    vbproj = wb.VBProject
    comp = vbproj.VBComponents("IQQQ跨码_D据擎4跨码管理")
    cm = comp.CodeModule

    # 查找并替换 Evaluate 行
    for i in range(1, cm.CountOfLines + 1):
        line = cm.Lines(i, 1)
        if 'Evaluate("ZF总资产")' in line or 'Evaluate("ZJ总资产")' in line or \
           'Evaluate("ZF可用资金")' in line or 'Evaluate("ZJ可用资金")' in line:
            old_line = line
            new_line = line.replace('Evaluate("', 'ThisWorkbook.Evaluate("')
            cm.ReplaceLine(i, new_line)
            print(f"Line {i}: {old_line.strip()} -> {new_line.strip()}")

    # 运行测试
    excel.Application.Run("IQQQ展擎主前调_组合管理仅A2")
    print("Ran test")

    # 检查结果
    for ws in wb.Worksheets:
        if ws.Name == "A2组合管理检查":
            val_福总资 = ws.Cells(5, 3).Value
            val_彦总资 = ws.Cells(5, 5).Value
            val_福现金 = ws.Cells(6, 3).Value
            val_彦现金 = ws.Cells(6, 5).Value
            print(f"\n=== 结果 ===")
            print(f"福总资={val_福总资}, 彦总资={val_彦总资}")
            print(f"福现金={val_福现金}, 彦现金={val_彦现金}")
            if val_福总资 and float(val_福总资) > 0:
                print("✓ 总资产正常！")
            else:
                print("✗ 总资产为0，问题未修复！")
            break

    wb.Close(False)

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
finally:
    if excel:
        excel.Quit()
        pythoncom.CoUninitialize()
        print("Done")