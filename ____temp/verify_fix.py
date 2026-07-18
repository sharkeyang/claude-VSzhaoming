"""验证: ZPY_策略匹配_模拟 修复"""
import win32com.client as win32
import sys, pythoncom, time, os

XLSM = sys.argv[1]
pythoncom.CoInitialize()
xl = win32.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

try:
    wb = xl.Workbooks.Open(XLSM)
    time.sleep(1)

    print("=== 测试1: 策略匹配调用 ===")
    try:
        xl.Run("ZPY_策略匹配_模拟", "金", "甲", 7, "升.尾连QQ.Q3", "高", "Aa龙猪.初")
        print("OK: ZPY_策略匹配_模拟 调用成功 (结果见立即窗口)")
    except Exception as e:
        print(f"ERROR: {e}")

    print("\n=== 测试2: 查概率表 ===")
    for s in ["金最优(全部)", "金+多长+升排+非孕+盈高", "金+多长", "银+盈提示有", "全量基准"]:
        try:
            p = xl.Run("查概率表", s, "Qd")
            print(f"  OK: '{s}' = {p}")
        except Exception as e:
            print(f"  ERROR: '{s}' -> {e}")

    print("\n=== 测试3: 常量读取 ===")
    vba_mod = wb.VBProject.VBComponents.Add(1)
    vba_mod.CodeModule.AddFromString("""
Public Function 取常量值2(ConstName As String) As Long
    Select Case ConstName
        Case "位谕始of族策": 取常量值2 = 位谕始of族策
        Case "位谕of周冲策略": 取常量值2 = 位谕of周冲策略
        Case "位谕of周冲策分": 取常量值2 = 位谕of周冲策分
        Case Else: 取常量值2 = -1
    End Select
End Function
""")
    base = xl.Run("取常量值2", "位谕始of族策")
    策 = xl.Run("取常量值2", "位谕of周冲策略")
    分 = xl.Run("取常量值2", "位谕of周冲策分")
    print(f"  位谕始of族策 = {base}")
    print(f"  位谕of周冲策略 = {策} (期望 {base+7})")
    print(f"  位谕of周冲策分 = {分} (期望 {base+8})")
    wb.VBProject.VBComponents.Remove(vba_mod)

    print("\n=== 全部完成 ===")

finally:
    wb.Close(False)
    xl.Quit()
    pythoncom.CoUninitialize()