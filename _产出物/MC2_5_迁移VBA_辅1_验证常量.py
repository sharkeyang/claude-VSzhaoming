"""验证位谕常量_config.py 所有关键列数值"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from MC2_5_迁移VBA_核4_位谕常量_config import *

print("=== 基础 ===")
print(f"位谕列始全部 = {位谕列始全部}")

print("\n=== 周层 ===")
print(f"位谕of周层三鳄 = {位谕of周层三鳄}")
print(f"位谕of周层大局 = {位谕of周层大局}")
print(f"位谕of周层猪操作 = {位谕of周层猪操作}")
print(f"位谕of周层下柱冲高提示 = {位谕of周层下柱冲高提示}")
print(f"位谕of周层护型 = {位谕of周层护型}")
print(f"位谕of周层波型 = {位谕of周层波型}")
print(f"位谕of周层柱排 = {位谕of周层柱排}")

print("\n=== 日层 ===")
print(f"位谕of日层联动 = {位谕of日层联动}")
print(f"位谕of日层护型 = {位谕of日层护型}")
print(f"位谕of日层柱排 = {位谕of日层柱排}")
print(f"位谕of日层盈提示 = {位谕of日层盈提示}")

print("\n=== 日类BTZ ===")
print(f"位谕of日类BTZA = {位谕of日类BTZA}")
print(f"位谕of日类BTZB = {位谕of日类BTZB}")
print(f"位谕of日类BTZC = {位谕of日类BTZC}")
print(f"位谕of日类BTZD = {位谕of日类BTZD}")
print(f"位谕of日类BTZE = {位谕of日类BTZE}")
print(f"位谕of日类BTCD = {位谕of日类BTCD}")
print(f"位谕of日类BTAB = {位谕of日类BTAB}")
print(f"位谕of日类BTBC = {位谕of日类BTBC}")

print("\n=== 周类BTZ ===")
print(f"位谕of周类BTZA = {位谕of周类BTZA}")
print(f"位谕of周类BTZE = {位谕of周类BTZE}")

print("\n=== 神谕起止 & AI列 ===")
print(f"位谕列终全部 = {位谕列终全部}")
print(f"位谕of周层下周冲高 = {位谕of周层下周冲高}")
print(f"位谕of周层下日冲高 = {位谕of周层下日冲高}")

print("\n=== 花天表 ===")
print(f"花列甲道 = {花列甲道}")
print(f"花宽全道 = {花宽全道}")

# VS Excel已知列号验算
print("\n=== VS Excel列号验证 ===")
# 在Excel中，BTZ列的绝对列号 = 花列甲道 + 位谕of日类BTZE - 位谕列始全部
日类基列偏移 = 花列甲道 - 位谕列始全部
print(f"日类BTZE Excel列 = {日类基列偏移 + 位谕of日类BTZE}  (期望~275)")
print(f"日类BTZA Excel列 = {日类基列偏移 + 位谕of日类BTZA}  (期望~268)")
print(f"日类BTCD Excel列 = {日类基列偏移 + 位谕of日类BTCD}  (期望~276)")
print(f"日层联动 Excel列 = {日类基列偏移 + 位谕of日层联动}  (期望~89)")
print(f"日层柱排 Excel列 = {日类基列偏移 + 位谕of日层柱排}  (期望~96)")
print(f"日层护型 Excel列 = {日类基列偏移 + 位谕of日层护型}  (期望~90)")

print("\n✅ 验证完成")