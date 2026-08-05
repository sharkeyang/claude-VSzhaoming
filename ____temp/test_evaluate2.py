# -*- coding: utf-8 -*-
"""测试：导入.bas到副本xlsm，运行组合管理仅A2"""
import os, sys, traceback, shutil, time

ts = "20260803_180051"
xlsm_path = f'D:\\@VSwork\\VS昭明计划VBA优化\\____temp\\昭明计划VS优化_{ts}.xlsm'
bas_dir = r'D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba'
bas_file = os.path.join(bas_dir, 'IQQQ跨码_D据擎4跨码管理.bas')

# 使用VBA宏操作_导入_Python版.py的方式
# 先复制bas到临时目录
tmp_vba = r'D:\@VSwork\VS昭明计划VBA优化\____temp\vba_test'
if os.path.exists(tmp_vba):
    shutil.rmtree(tmp_vba)
os.makedirs(tmp_vba, exist_ok=True)
shutil.copy2(bas_file, os.path.join(tmp_vba, 'IQQQ跨码_D据擎4跨码管理.bas'))

# 使用Python脚本导入
import win32com.client
excel = None
try:
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    # 尝试打开（可能需要密码）
    try:
        wb = excel.Workbooks.Open(xlsm_path, Password="")
    except:
        # 尝试无密码
        wb = excel.Workbooks.Open(xlsm_path)

    print(f"Opened: {wb.Name}")

    # 删除旧模块
    vbproj = wb.VBProject
    comp_names = []
    for i in range(1, vbproj.VBComponents.Count + 1):
        comp_names.append(vbproj.VBComponents(i).Name)

    if "IQQQ跨码_D据擎4跨码管理" in comp_names:
        comp = vbproj.VBComponents("IQQQ跨码_D据擎4跨码管理")
        vbproj.VBComponents.Remove(comp)
        print("Removed old module")

    # 导入新模块
    vbproj.VBComponents.Import(os.path.join(tmp_vba, 'IQQQ跨码_D据擎4跨码管理.bas'))
    print("Imported new module")

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
        import pythoncom
        pythoncom.CoUninitialize()
        print("Excel closed")