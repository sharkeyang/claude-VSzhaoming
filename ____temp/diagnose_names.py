# -*- coding: utf-8 -*-
"""诊断：检查 xlsm 中 ZF总资产 等名称是否存在及值"""
import win32com.client, pythoncom, traceback, sys

pythoncom.CoInitialize()
excel = None
try:
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    xlsm = r'D:\@VSwork\VS昭明计划VBA优化\____temp\昭明计划VS优化_20260803_180051.xlsm'
    wb = excel.Workbooks.Open(xlsm)
    print(f"工作簿: {wb.Name}\n")

    # 搜索的名称为
    names_to_find = ["ZF总资产", "ZJ总资产", "ZF可用资金", "ZJ可用资金", "ZF总资产", "ZJ总资产"]

    # 1. 检查工作簿级名称
    print("=== 工作簿级名称 ===")
    for i in range(1, wb.Names.Count + 1):
        n = wb.Names(i)
        for target in names_to_find:
            if target in n.Name:
                try:
                    val = n.RefersToRange.Value
                    print(f"  {n.Name} = {val}  (引用: {n.RefersTo})")
                except Exception as e:
                    print(f"  {n.Name} 读取失败: {e}")
                break

    # 2. 检查每个工作表的名称
    print("\n=== 工作表级名称 ===")
    for ws in wb.Worksheets:
        try:
            for i in range(1, ws.Names.Count + 1):
                n = ws.Names(i)
                for target in names_to_find:
                    if target in n.Name:
                        try:
                            val = n.RefersToRange.Value
                            print(f"  [{ws.Name}] {n.Name} = {val}  (引用: {n.RefersTo})")
                        except Exception as e:
                            print(f"  [{ws.Name}] {n.Name} 读取失败: {e}")
                        break
        except:
            pass

    # 3. 直接 Evaluate 测试
    print("\n=== Evaluate 测试 ===")
    for name in ["ZF总资产", "ZJ总资产", "ZF可用资金", "ZJ可用资金"]:
        try:
            val = excel.Evaluate(name)
            print(f"  Evaluate(\"{name}\") = {val}")
        except Exception as e:
            print(f"  Evaluate(\"{name}\") 失败: {e}")

    # 4. 尝试 ThisWorkbook.Evaluate
    print("\n=== ThisWorkbook 测试 ===")
    for name in ["ZF总资产", "ZJ总资产", "ZF可用资金", "ZJ可用资金"]:
        try:
            val = wb.Worksheets(1).Evaluate(name)  # 在第一个sheet上Evaluate
            print(f"  Sheet1.Evaluate(\"{name}\") = {val}")
        except Exception as e:
            print(f"  Sheet1.Evaluate(\"{name}\") 失败: {e}")

    wb.Close(False)
    print("\n完成")

except Exception as e:
    print(f"错误: {e}")
    traceback.print_exc()
finally:
    if excel:
        excel.Quit()
        pythoncom.CoUninitialize()