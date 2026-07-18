"""验证：周冲策略/周冲策分 数据写入是否正确"""
import win32com.client as win32
import sys, os, time

XLSM = sys.argv[1]
print(f"打开: {XLSM}")

# 独立Excel进程
xl = win32.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

wb = xl.Workbooks.Open(XLSM)
ws = wb.Sheets(1)  # 花天表

# 读取常量值 - 先在花天表末行写测试值
# 位谕始of族策 = 位谕终of族月均 + 1
# 周冲策略 = 位谕始of族策 + 7
# 周冲策分 = 位谕始of族策 + 8

# 方案：直接在Excel中通过VBA读取常量值
# 添加临时模块读取常量
vba_mod = None
try:
    vba_mod = wb.VBProject.VBComponents.Add(1)  # vbext_ct_StdModule
    vba_mod.CodeModule.AddFromString("""
Public Function 取常量值(ConstName As String) As Long
    Select Case ConstName
        Case "位谕始of族策": 取常量值 = 位谕始of族策
        Case "位谕of周冲策略": 取常量值 = 位谕of周冲策略
        Case "位谕of周冲策分": 取常量值 = 位谕of周冲策分
        Case "位谕of策传": 取常量值 = 位谕of策传
        Case "位谕of月基策略": 取常量值 = 位谕of月基策略
        Case "位谕of月基策分": 取常量值 = 位谕of月基策分
        Case "位谕列终全部": 取常量值 = 位谕列终全部
        Case Else: 取常量值 = -1
    End Select
End Function
""")

    # 读取每个常量的值
    consts = ["位谕始of族策", "位谕of周冲策略", "位谕of周冲策分",
              "位谕of策传", "位谕of月基策略", "位谕of月基策分", "位谕列终全部"]
    vals = {}
    for c in consts:
        try:
            vals[c] = xl.Run("取常量值", c)
        except Exception as e:
            vals[c] = f"ERROR: {e}"

    print("\n=== 常量值验证 ===")
    for c in consts:
        print(f"  {c} = {vals[c]}")

    # 验证偏移关系
    base = vals["位谕始of族策"]
    if isinstance(base, int):
        print(f"\n=== 偏移关系验证 ===")
        expected = {
            "位谕of策传": base + 0,
            "位谕of周冲策略": base + 7,
            "位谕of周冲策分": base + 8,
            "位谕of月基策略": base + 5,
            "位谕of月基策分": base + 6,
        }
        for name, exp in expected.items():
            actual = vals[name]
            status = "OK" if actual == exp else "FAIL"
            print(f"  {status}: {name} = {actual} (期望 {exp})")

    # 读取花天表的数据 - 检查周冲策略/策分列是否有值
    print(f"\n=== 花天表数据抽样（末行50只）===")
    末行 = ws.Cells(ws.Rows.Count, 1).End(-4162).Row  # xlUp
    print(f"  数据行数: {末行 - 1}")

    周冲策略列 = vals["位谕of周冲策略"]
    周冲策分列 = vals["位谕of周冲策分"]

    if isinstance(周冲策略列, int) and isinstance(周冲策分列, int):
        has_data = 0
        no_data = 0
        sample = []
        start = max(2, 末行 - 50)
        for r in range(start, 末行 + 1):
            v1 = ws.Cells(r, 周冲策略列).Value
            v2 = ws.Cells(r, 周冲策分列).Value
            if v1 is not None and v1 != "" and v1 != 0:
                has_data += 1
                if len(sample) < 5:
                    sample.append((r, v1, v2))
            else:
                no_data += 1

        print(f"  周冲策略有数据: {has_data}/{has_data + no_data}")
        print(f"  周冲策略为空:   {no_data}/{has_data + no_data}")
        if sample:
            print(f"  样例({len(sample)}只):")
            for r, v1, v2 in sample:
                print(f"    行{r}: 策略='{v1}' 策分={v2}")

    # 运行神谕生成(需要调用STBASE景深处理→神谕)
    # 但完整运行需要10-15分钟，先不跑

finally:
    if vba_mod:
        wb.VBProject.VBComponents.Remove(vba_mod)
    wb.Save()
    wb.Close(False)
    xl.Quit()
    import pythoncom
    pythoncom.CoUninitialize()
    print("\n=== 完成 ===")