"""快速验证 - 只检查Else:修复是否编译通过"""
import win32com.client as win32
import pythoncom, time, os, sys

XLSM = sys.argv[1]
BAS = sys.argv[2]  # 单个.bas文件

pythoncom.CoInitialize()
xl = win32.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False
xl.AutomationSecurity = 1

print(f"打开: {XLSM}")
wb = xl.Workbooks.Open(XLSM)
time.sleep(2)
vba = wb.VBProject

# 删除旧模块，导入新模块
bas_path = os.path.abspath(BAS)
bas_name = os.path.basename(bas_path)
mod_name = bas_name.replace('.bas', '')

print(f"更新模块: {mod_name}")
for i in range(vba.VBComponents.Count, 0, -1):
    comp = vba.VBComponents(i)
    if comp.Name == mod_name:
        vba.VBComponents.Remove(comp)
        print(f"  已删除旧模块")
        break

vba.VBComponents.Import(bas_path)
print(f"  已导入新模块")

wb.Save()
time.sleep(1)

# 测试查概率表
print("\n=== 验证 ===")
try:
    p = xl.Run("查概率表", "金最优(全部)", "Qd")
    print(f"OK: 查概率表 = {p}")
except Exception as e:
    print(f"查概率表: {e}")

# 测试策略匹配 (Sub, 不返回值)
try:
    xl.Run("ZPY_策略匹配_模拟", "金", "甲", 7, "升.尾连QQ.Q3", "高", "Aa龙猪.初")
    print("OK: 策略匹配 调用成功")
except Exception as e:
    print(f"策略匹配: {e}")

wb.Close(False)
xl.Quit()
pythoncom.CoUninitialize()
print("\n完成")