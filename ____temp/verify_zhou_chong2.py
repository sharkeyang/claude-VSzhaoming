"""验证：查概率表 + 周冲策略常量 是否正常"""
import win32com.client as win32
import sys, os, pythoncom, time

XLSM = sys.argv[1]
print(f"打开: {XLSM}")

pythoncom.CoInitialize()
xl = win32.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

wb = xl.Workbooks.Open(XLSM)
time.sleep(1)

# 测试查概率表 - 各种策略
tests = [
    ("金最优(全部)", "Qd"),
    ("金+多长+升排+非孕+盈高", "Qd"),
    ("金+多长+升排+非孕", "Qd"),
    ("金+多长+升排", "Qd"),
    ("金+多长", "Qd"),
    ("银+盈提示有", "Qd"),
    ("银+WXAB=己", "Qd"),
    ("银+柱排=升", "Qd"),
    ("银+龙猪", "Qd"),
    ("银+ZA5~10", "Qd"),
    ("全量基准", "Qd"),
    ("", "Qd"),
]

print("\n=== 查概率表 验证 ===")
all_ok = True
for strategy, board in tests:
    try:
        p = xl.Run("查概率表", strategy, board)
        label = strategy if strategy else "(空字符串)"
        status = "OK" if p is not None else "NONE"
        print(f"  {status}: 查概率表('{label}', '{board}') = {p}")
    except Exception as e:
        print(f"  ERROR: 查概率表('{strategy}', '{board}') -> {e}")
        all_ok = False

# 验证常量值（通过临时模块）
vba_mod = wb.VBProject.VBComponents.Add(1)
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

base = xl.Run("取常量值", "位谕始of族策")
print(f"\n=== 常量偏移验证 (base={base}) ===")
checks = [
    ("位谕of策传", 0),
    ("位谕of月基策略", 5),
    ("位谕of月基策分", 6),
    ("位谕of周冲策略", 7),
    ("位谕of周冲策分", 8),
    ("位谕列终全部", 8),  # = 周冲策分，所以 = base+8
]
for name, offset in checks:
    actual = xl.Run("取常量值", name)
    expected = base + offset
    status = "OK" if actual == expected else "FAIL"
    print(f"  {status}: {name} = {actual} (期望 {expected})")
    if actual != expected:
        all_ok = False

# 清理
wb.VBProject.VBComponents.Remove(vba_mod)
wb.Close(False)
xl.Quit()
pythoncom.CoUninitialize()

print(f"\n=== 结论: {'全部通过' if all_ok else '有失败项'} ===")