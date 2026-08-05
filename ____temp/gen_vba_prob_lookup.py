'''
生成VBA代码：概率表字典查询函数
输出：可直接粘贴到 PX算研_ZPY接口.bas 的VBA代码
'''
import csv

CSV = r'd:\@VSwork\VS昭明计划VBA优化\____temp\DXEF_DXCD_DXAB_完整概率表2.csv'
DXEF_MAP = {'金': 0, '银': 1, '嘘': 2, '唏': 3, '屎': 4, '尿': 5}
DXCD_MAP = {'上': 0, '中': 1, '下': 2, '忐': 3, '忠': 4, '忑': 5}
DXAB_MAP = {'上': 0, '中': 1, '下': 2, '忐': 3, '忠': 4, '忑': 5}

# 读取数据
data = {}  # (dxef, dxcd, dxab) -> {N, ze, zc, za, dsha0, dsha1, dsha3, avg_hr, med_hr, parent_n, shrink}
with open(CSV, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        key = (row[0], row[1], row[2])
        n = int(row[3])
        data[key] = {
            'N': n,
            'ze': float(row[4]) if row[4] else 0,
            'zc': float(row[5]) if row[5] else 0,
            'za': float(row[6]) if row[6] else 0,
            'dsha0': float(row[7]) if row[7] else 0,
            'dsha1': float(row[8]) if row[8] else 0,
            'dsha3': float(row[9]) if row[9] else 0,
            'hr': row[10] if row[10] else '',
            'med_hr': row[11] if row[11] else '',
            'parent_n': int(row[12]) if row[12] else 0,
            'shrink': row[13] if row[13] else ''
        }

# 生成VBA代码：二维数组方式（6×6×6）
# 先按DXEF分组，每组输出一个二维数组
print("' ===== 日冲策略概率评分表 ===== ")
print("' 数据来源：MC3.3_日冲216分支分析报告.md")
print("' 生成日期：2026-07-26")
print("' 用法：Call 日冲评分(DXEF, DXCD, DXAB, pZE, pZC, pZA, pDSHA1, 小样本)")
print("' 返回：→ZE>0, →ZE+ZC, →ZE+ZC+ZA, 下日DSHA>1, 是否小样本标记")
print()

# 生成查找函数
print("' === 概率评分主函数 ===")
print("Public Function 日冲评分(ByVal sDXEF As String, ByVal sDXCD As String, ByVal sDXAB As String, _")
print("    ByRef pZE As Double, ByRef pZC As Double, ByRef pZA As Double, _")
print("    ByRef pDSHA1 As Double, ByRef 小样本标记 As String) As Boolean")
print("    ' 返回值：True=找到匹配，False=未找到")
print("    Dim iEF As Long, iCD As Long, iAB As Long")
print("    Dim arrData As Variant")
print()
print("    ' DXEF映射")
print("    Select Case sDXEF")
print("        Case ""金"": iEF = 0")
print("        Case ""银"": iEF = 1")
print("        Case ""嘘"": iEF = 2")
print("        Case ""唏"": iEF = 3")
print("        Case ""屎"": iEF = 4")
print("        Case ""尿"": iEF = 5")
print("        Case Else: 日冲评分 = False: Exit Function")
print("    End Select")
print()
print("    ' DXCD映射")
print("    Select Case sDXCD")
print("        Case ""上"": iCD = 0")
print("        Case ""中"": iCD = 1")
print("        Case ""下"": iCD = 2")
print("        Case ""忐"": iCD = 3")
print("        Case ""忠"": iCD = 4")
print("        Case ""忑"": iCD = 5")
print("        Case Else: 日冲评分 = False: Exit Function")
print("    End Select")
print()
print("    ' DXAB映射")
print("    Select Case sDXAB")
print("        Case ""上"": iAB = 0")
print("        Case ""中"": iAB = 1")
print("        Case ""下"": iAB = 2")
print("        Case ""忐"": iAB = 3")
print("        Case ""忠"": iAB = 4")
print("        Case ""忑"": iAB = 5")
print("        Case Else: 日冲评分 = False: Exit Function")
print("    End Select")
print()

# 生成6个战场的数组数据
battle_names = ['金', '银', '嘘', '唏', '屎', '尿']
for bi, ef_name in enumerate(battle_names):
    print(f"    ' === {ef_name}战场 ===")
    lines = []
    for cd_name in ['上', '中', '下', '忐', '忠', '忑']:
        vals = []
        for ab_name in ['上', '中', '下', '忐', '忠', '忑']:
            key = (ef_name, cd_name, ab_name)
            d = data.get(key)
            if d:
                n = d['N']
                ze = d['ze']
                zc = d['zc']
                za = d['za']
                dsha1 = d['dsha1']
                shrink = 1 if d['shrink'] else 0
                vals.append(f"Array({n},{ze},{zc},{za},{dsha1},{shrink})")
            else:
                vals.append("Array(0,0,0,0,0,0)")
        lines.append(f"        Array({', '.join(vals)})")

    arr_body = ",\n".join(lines)
    print(f"    arrData = Array({arr_body})")
    print()

print("    ' 查找并返回")
print("    Dim rowData As Variant")
print("    rowData = arrData(iCD)(iAB)")
print("    pZE = rowData(1)       ' →ZE>0")
print("    pZC = rowData(2)       ' →ZE>0+ZC>0")
print("    pZA = rowData(3)       ' →ZE>0+ZC>0+ZA>0")
print("    pDSHA1 = rowData(4)    ' 下日DSHA>1")
print("    If rowData(5) = 1 Then")
print("        小样本标记 = ""小样本""")
print("    Else")
print("        小样本标记 = """"")
print("    End If")
print("    日冲评分 = (rowData(0) > 0)")
print("End Function")
print()

# 生成简化评分函数
print("' === 简化评分函数（返回综合分0-100） ===")
print("Public Function 日冲综合分(ByVal sDXEF As String, ByVal sDXCD As String, ByVal sDXAB As String) As Double")
print("    ' 综合评分 = (→ZE>0 * 0.4 + →ZE+ZC * 0.3 + →ZE+ZC+ZA * 0.2 + 下日DSHA>1 * 0.1)")
print("    ' 排除小样本分支")
print("    Dim pZE As Double, pZC As Double, pZA As Double, pDSHA1 As Double")
print("    Dim 小样本标记 As String")
print("    If Not 日冲评分(sDXEF, sDXCD, sDXAB, pZE, pZC, pZA, pDSHA1, 小样本标记) Then")
print("        日冲综合分 = 0: Exit Function")
print("    End If")
print("    If 小样本标记 <> """" Then")
print("        日冲综合分 = 0: Exit Function  ' 小样本不评分")
print("    End If")
print("    日冲综合分 = pZE * 0.4 + pZC * 0.3 + pZA * 0.2 + pDSHA1 * 0.1")
print("End Function")
print()

# 生成决策函数
print("' === 日冲决策建议函数 ===")
print("Public Function 日冲建议(ByVal sDXEF As String, ByVal sDXCD As String, ByVal sDXAB As String) As String")
print("    ' 返回：""可操作"" / ""谨慎"" / ""禁止"" / ""无数据""")
print("    Dim pZE As Double, pZC As Double, pZA As Double, pDSHA1 As Double")
print("    Dim 小样本标记 As String")
print("    If Not 日冲评分(sDXEF, sDXCD, sDXAB, pZE, pZC, pZA, pDSHA1, 小样本标记) Then")
print("        日冲建议 = ""无数据"": Exit Function")
print("    End If")
print("    If 小样本标记 <> """" Then")
print("        日冲建议 = ""无数据"": Exit Function")
print("    End If")
print("    ' 决策规则：")
print("    ' →ZE>0 >= 90% 且 →ZE+ZC+ZA >= 30% → 可操作")
print("    ' →ZE>0 >= 70% 且 →ZE+ZC+ZA >= 10% → 谨慎")
print("    ' 其他 → 禁止")
print("    If pZE >= 90 And pZA >= 30 Then")
print("        日冲建议 = ""可操作""")
print("    ElseIf pZE >= 70 And pZA >= 10 Then")
print("        日冲建议 = ""谨慎""")
print("    Else")
print("        日冲建议 = ""禁止""")
print("    End If")
print("End Function")