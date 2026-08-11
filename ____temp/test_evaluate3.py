# -*- coding: utf-8 -*-
"""测试：导入.bas到副本xlsm，运行组合管理仅A2"""
import os, sys, traceback, win32com.client, pythoncom

pythoncom.CoInitialize()
excel = None
try:
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    xlsm = r'D:\@VSwork\VS昭明计划VBA优化\____temp\昭明计划VS优化_20260803_180051.xlsm'
    wb = excel.Workbooks.Open(xlsm)
    print(f"Opened: {wb.Name}")

    vbproj = wb.VBProject

    # 先删除旧模块
    try:
        comp = vbproj.VBComponents("IQQQ跨码_D据擎4跨码管理")
        vbproj.VBComponents.Remove(comp)
        print("Removed old module")
    except:
        print("Old module not found")

    # 使用VBComponents.Import导入
    bas = r'D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba\IQQQ跨码_D据擎4跨码管理.bas'
    comp = vbproj.VBComponents.Import(bas)
    print(f"Imported: {comp.Name}")

    # 运行测试
    excel.Application.Run("IQQQ展擎主前调_组合管理仅A2")
    print("Ran test")

    # 检查结果
    for ws in wb.Worksheets:
        if ws.Name == "A2组合管理检查":
            val_福总资 = ws.Cells(5, 3).Value
            val_彦总资 = ws.Cells(5, 5).Value
            print(f"\n=== 结果 ===")
            print(f"福总资={val_福总资}, 彦总资={val_彦总资}")
            if val_福总资 and float(val_福总资) > 0:
                print("✓ 总资产正常！")
            else:
                print("✗ 总资产为0，问题未修复！")
            break

    wb.Close(False)
    print("Done")

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
finally:
    if excel:
        excel.Quit()
        pythoncom.CoUninitialize()
        print("Excel closed")