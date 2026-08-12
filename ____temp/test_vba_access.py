# -*- coding: utf-8 -*-
"""测试VBA项目访问权限"""
import win32com.client
import pythoncom

pythoncom.CoInitialize()
excel = None
try:
    excel = win32com.client.DispatchEx("Excel.Application")
    excel.Visible = False
    excel.DisplayAlerts = False

    wb = excel.Workbooks.Open(r'D:\@VSwork\VS昭明计划VBA优化\____temp\昭明计划VS优化_20260803_180051.xlsm')
    print(f"Opened: {wb.Name}")

    try:
        vbproj = wb.VBProject
        print(f"VBProject accessible: {vbproj.Name}")
        for i in range(1, vbproj.VBComponents.Count + 1):
            comp = vbproj.VBComponents(i)
            print(f"  Component {i}: {comp.Name}")
    except Exception as e:
        print(f"VBProject access error: {e}")

    wb.Close(False)
except Exception as e:
    print(f"Error: {e}")
finally:
    if excel:
        excel.Quit()
        pythoncom.CoUninitialize()
        print("Done")