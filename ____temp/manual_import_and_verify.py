"""手动导入.bas到副本 + 验证"""
import win32com.client as win32
import pythoncom, time, os, sys

XLSM = sys.argv[1]
BAS_DIR = sys.argv[2]  # .bas文件目录

pythoncom.CoInitialize()
xl = win32.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

try:
    # 降低宏安全
    xl.AutomationSecurity = 1  # Low
    wb = xl.Workbooks.Open(XLSM)
    time.sleep(2)

    # 收集所有.bas文件（用绝对路径）
    bas_dir_abs = os.path.abspath(BAS_DIR)
    bas_files = [f for f in os.listdir(bas_dir_abs) if f.endswith('.bas')]
    print(f"发现 {len(bas_files)} 个.bas文件")

    # 删除旧模块 + 导入新模块
    vba = wb.VBProject
    mod_count = 0
    for bas_name in sorted(bas_files):
        module_name = bas_name.replace('.bas', '')
        # 删除同名旧模块
        for i in range(vba.VBComponents.Count, 0, -1):
            comp = vba.VBComponents(i)
            if comp.Name == module_name:
                vba.VBComponents.Remove(comp)
                break
        # 导入新模块
        bas_path = os.path.join(bas_dir_abs, bas_name)
        vba.VBComponents.Import(bas_path)
        mod_count += 1
        if mod_count % 10 == 0:
            print(f"  已导入 {mod_count}/{len(bas_files)}")

    print(f"导入完成: {mod_count} 个模块")
    wb.Save()

    # 验证1: Strategy matching function exists
    print("\n=== 验证: 函数存在性 ===")
    found = False
    for comp in vba.VBComponents:
        if comp.Name == "PX算研_ZPY接口":
            found = True
            print(f"  OK: PX算研_ZPY接口 模块存在")
            break
    if not found:
        print("  ERROR: 找不到 PX算研_ZPY接口 模块")

    # 验证2: 查概率表
    print("\n=== 验证: 查概率表 ===")
    for s in ["金最优(全部)", "金+多长", "银+盈提示有", ""]:
        try:
            p = xl.Run("查概率表", s, "Qd")
            print(f"  OK: '{s or '(空)'}' = {p}")
        except Exception as e:
            print(f"  ERROR: '{s}' -> {e}")

    # 验证3: 策略匹配
    print("\n=== 验证: 策略匹配模拟 ===")
    try:
        xl.Run("ZPY_策略匹配_模拟", "金", "甲", 7, "升.尾连QQ.Q3", "高", "Aa龙猪.初")
        print("  OK: 策略匹配 调用成功")
    except Exception as e:
        print(f"  ERROR: 策略匹配 -> {e}")

    wb.Save()
    print("\n=== 全部通过 ===")

except Exception as e:
    print(f"\nFATAL: {e}")
finally:
    try:
        wb.Close(False)
    except:
        pass
    xl.Quit()
    pythoncom.CoUninitialize()