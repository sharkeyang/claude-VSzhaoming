# -*- coding: utf-8 -*-
"""测试：导入.bas到副本xlsm，运行组合管理仅A2，检查总资产是否正常"""
import os, sys, traceback

ts = "20260803_180051"
xlsm_path = f'D:\\@VSwork\\VS昭明计划VBA优化\\____temp\\昭明计划VS优化_{ts}.xlsm'
bas_dir = r'D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba'
bas_file = os.path.join(bas_dir, 'IQQQ跨码_D据擎4跨码管理.bas')

import win32com.client
from win32com.client import DispatchEx

excel = None
try:
    excel = DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    wb = excel.Workbooks.Open(xlsm_path)
    print(f"Opened: {wb.Name}")

    # Remove old module if exists
    vbproj = wb.VBProject
    for i in range(vbproj.VBComponents.Count, 0, -1):
        comp = vbproj.VBComponents(i)
        if comp.Name == "IQQQ跨码_D据擎4跨码管理":
            vbproj.VBComponents.Remove(comp)
            print("Removed old module")
            break

    # Import new .bas module
    vbaMod = vbproj.VBComponents.Import(bas_file)
    print(f"Imported: {bas_file}")

    # Run the test
    excel.Application.Run("IQQQ展擎主前调_组合管理仅A2")
    print("Ran: IQQQ展擎主前调_组合管理仅A2")

    # Check the output sheet
    for ws in wb.Worksheets:
        if ws.Name == "A2组合管理检查":
            val_福总资 = ws.Cells(5, 3).Value
            val_彦总资 = ws.Cells(5, 5).Value
            val_福现金 = ws.Cells(6, 3).Value
            val_彦现金 = ws.Cells(6, 5).Value
            val_福持仓 = ws.Cells(7, 3).Value
            val_彦持仓 = ws.Cells(7, 5).Value

            print(f"\n=== 结果 ===")
            print(f"福总资={val_福总资}, 彦总资={val_彦总资}")
            print(f"福现金={val_福现金}, 彦现金={val_彦现金}")
            print(f"福持仓={val_福持仓}, 彦持仓={val_彦持仓}")

            if val_福总资 and float(val_福总资) > 0:
                print("\n✓ 总资产正常！")
            else:
                print("\n✗ 总资产为0，问题未修复！")
            break

    wb.Save()
    print("Saved")

except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
finally:
    if excel:
        excel.Quit()
        import win32com.client as wc
        wc.ReleaseComObject(excel)
        print("Excel closed")