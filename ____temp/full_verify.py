"""手动导入.bas + 验证 - 处理编码问题"""
import win32com.client as win32
import pythoncom, time, os, sys, shutil, tempfile

XLSM = sys.argv[1]
BAS_DIR = os.path.abspath(sys.argv[2])

pythoncom.CoInitialize()
xl = win32.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False
xl.AutomationSecurity = 1  # 低安全

wb = xl.Workbooks.Open(XLSM)
time.sleep(2)
vba = wb.VBProject

# 第一步: 将所有.bas从UTF-8转GBK到临时目录
tmp_dir = tempfile.mkdtemp(prefix="vba_batch_")
print(f"临时目录: {tmp_dir}")

for f in sorted(os.listdir(BAS_DIR)):
    if not f.endswith('.bas'):
        continue
    src = os.path.join(BAS_DIR, f)
    dst = os.path.join(tmp_dir, f)
    with open(src, 'r', encoding='utf-8') as fr:
        content = fr.read()
    with open(dst, 'w', encoding='gbk') as fw:
        fw.write(content)

# 第二步: 删除所有旧模块 + 导入新模块
print(f"导入 {len([f for f in os.listdir(tmp_dir) if f.endswith('.bas')])} 个模块...")
count = 0
for f in sorted(os.listdir(tmp_dir)):
    if not f.endswith('.bas'):
        continue
    mod_name = f.replace('.bas', '')
    # 删除旧模块
    for i in range(vba.VBComponents.Count, 0, -1):
        comp = vba.VBComponents(i)
        if comp.Name == mod_name:
            vba.VBComponents.Remove(comp)
            break
    # 导入新模块
    vba.VBComponents.Import(os.path.join(tmp_dir, f))
    count += 1

print(f"导入完成: {count} 模块")
wb.Save()

# 清理临时目录
shutil.rmtree(tmp_dir, ignore_errors=True)

# 第三步: 验证
print("\n=== 验证1: 查概率表 ===")
for s in ["金最优(全部)", "金+多长", "银+盈提示有", "全量基准", ""]:
    try:
        p = xl.Run("查概率表", s, "Qd")
        print(f"  OK: '{s or '(空)'}' = {p}")
    except Exception as e:
        print(f"  ERROR: '{s}' -> {e}")

print("\n=== 验证2: 策略匹配模拟 ===")
try:
    xl.Run("ZPY_策略匹配_模拟", "金", "甲", 7, "升.尾连QQ.Q3", "高", "Aa龙猪.初")
    print("  OK: 策略匹配 调用成功")
except Exception as e:
    print(f"  ERROR: 策略匹配 -> {e}")

print("\n=== 验证3: 常量偏移 ===")
vba_mod = vba.VBComponents.Add(1)
vba_mod.CodeModule.AddFromString("""
Public Function GetConst(c As String) As Long
    Select Case c
        Case "base": GetConst = 位谕始of族策
        Case "策": GetConst = 位谕of周冲策略
        Case "分": GetConst = 位谕of周冲策分
    End Select
End Function
""")
base = xl.Run("GetConst", "base")
策 = xl.Run("GetConst", "策")
分 = xl.Run("GetConst", "分")
print(f"  base={base} 周冲策略={策}(={base+7}) 周冲策分={分}(={base+8})")
ok = (策 == base+7 and 分 == base+8)
print(f"  {'全部正确' if ok else '有误'}")
vba.VBComponents.Remove(vba_mod)

wb.Save()
wb.Close(False)
xl.Quit()
pythoncom.CoUninitialize()
print(f"\n=== 完成 ===")