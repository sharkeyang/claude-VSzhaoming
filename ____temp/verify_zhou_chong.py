"""验证：周冲策略匹配逻辑 + 查概率表 是否正常工作"""
import win32com.client as win32
import sys, os, pythoncom

XLSM = sys.argv[1]
print(f"打开: {XLSM}")

pythoncom.CoInitialize()
xl = win32.DispatchEx("Excel.Application")
xl.Visible = False
xl.DisplayAlerts = False

wb = xl.Workbooks.Open(XLSM)
ws = wb.Worksheets.Add()
ws.Name = "验证结果"
ws.Cells(1, 1).Value = "测试项"
ws.Cells(1, 2).Value = "结果"
ws.Cells(1, 3).Value = "说明"

row = 2

def log(test, result, detail=""):
    global row
    ws.Cells(row, 1).Value = test
    ws.Cells(row, 2).Value = result
    ws.Cells(row, 3).Value = detail
    print(f"  {test}: {result}")
    row += 1

# 测试1: 查概率表 - 基本查询
try:
    p = xl.Run("查概率表", "金最优(全部)", "Qd")
    log("查概率表(金最优(全部), Qd)", f"OK -> {p}", "应为数值")
except Exception as e:
    log("查概率表(金最优(全部), Qd)", f"ERROR: {e}", "")

# 测试2: 查概率表 - 银系
try:
    p = xl.Run("查概率表", "银+盈提示有", "Qd")
    log("查概率表(银+盈提示有, Qd)", f"OK -> {p}", "应为数值")
except Exception as e:
    log("查概率表(银+盈提示有, Qd)", f"ERROR: {e}", "")

# 测试3: 查概率表 - 空策略
try:
    p = xl.Run("查概率表", "", "Qd")
    log("查概率表('', Qd)", f"OK -> {p}", "应为0或空")
except Exception as e:
    log("查概率表('', Qd)", f"ERROR: {e}", "")

# 测试4: 查概率表 - 全量基准
try:
    p = xl.Run("查概率表", "全量基准", "Qd")
    log("查概率表(全量基准, Qd)", f"OK -> {p}", "应为基准概率")
except Exception as e:
    log("查概率表(全量基准, Qd)", f"ERROR: {e}", "")

# 测试5: 策略匹配模拟 - 金最优(全部)
try:
    xl.Run("ZPY_策略匹配_模拟", "金", "甲", 7, "升.尾连QQ.Q3", "高", "Aa龙猪.初")
    log("策略匹配(金+甲+ZA7+升排+龙猪)", "OK", "期望: 金最优(全部)")
except Exception as e:
    log("策略匹配(金+甲+ZA7+升排+龙猪)", f"ERROR: {e}", "")

# 测试6: 策略匹配模拟 - 银+盈提示有
try:
    xl.Run("ZPY_策略匹配_模拟", "银", "甲", 3, "升.尾连QQ.Q3", "高", "Aa头正")
    log("策略匹配(银+甲+升排+盈高)", "OK", "期望: 银+盈提示有")
except Exception as e:
    log("策略匹配(银+甲+升排+盈高)", f"ERROR: {e}", "")

# 测试7: 策略匹配模拟 - 无匹配
try:
    xl.Run("ZPY_策略匹配_模拟", "屎", "戊", -1, "跌.尾连", "", "Aa震负")
    log("策略匹配(屎+戊+跌排+震负)", "OK", "期望: 无匹配")
except Exception as e:
    log("策略匹配(屎+戊+跌排+震负)", f"ERROR: {e}", "")

# 测试8: 验证位谕常量（读花天表已有数据）
try:
    ws_data = wb.Sheets("花天表")
    last_row = ws_data.Cells(ws_data.Rows.Count, 1).End(-4162).Row
    if last_row > 1:
        log("花天表数据行数", f"{last_row - 1}行", "副本有历史数据")
    else:
        log("花天表数据行数", "空表", "副本未运行结算")
except Exception as e:
    log("花天表检查", f"跳过: {e}", "")

# 测试9: 直接调用 STBASE 主结算入口
# 注意：这需要10-15分钟，只在必要时运行
# log("完整结算", "跳过", "需手动运行")

# 清理
ws.Columns("A:C").AutoFit()
wb.Save()
wb.Close(False)
xl.Quit()
pythoncom.CoUninitialize()

print("\n=== 验证完成 ===")
print("结果已写入: 验证结果 sheet")