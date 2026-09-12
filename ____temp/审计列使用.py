# -*- coding: utf-8 -*-
"""审计所有脚本的列使用 vs VBA权威列映射"""
import io, re, sys, os, glob
sys.stdout.reconfigure(encoding='utf-8')

VBA = {0:'日期',1:'收',2:'开',3:'高',4:'低',5:'涨幅',6:'高幅',7:'日周联动',
 8:'DXCD',9:'DXAB',10:'柱排',11:'波型',12:'盈提示',13:'日ZA',14:'日ZC',
 15:'日ZE',16:'日BTEF',17:'日机警',18:'四域',19:'BSHA',20:'BSAC',
 21:'脸哼JA',22:'宽哼JC',23:'偏顶JC',24:'上身',25:'叠幅',26:'次日高幅',
 27:'柱型',28:'层界',29:'上符范',30:'上符串',31:'宽符串',32:'中符范',
 33:'中符串',34:'并符串',35:'管释',36:'撤哼JC',37:'类合',38:'BSLA',
 39:'宽哈JC',40:'BT鼎',41:'BTZA',42:'BT连阳',43:'顶型',44:'日等型',
 45:'仓日类',46:'仓日期',47:'日层赢',48:'日BTEF',49:'日BTZF',50:'月策带日',
 51:'日策分坏',52:'日策分好',53:'日龟BT顶',54:'日龟BT哼',55:'日龟顶触',
 56:'日龟BT合顶哼',57:'日基月局',58:'日基周局',59:'日基日局',60:'日基乾局',61:'日基坤局'}

# 脚本头部注释声明的列用途（用于判断是否用错）
scripts = sorted(glob.glob('____temp/*.py'))
for script in scripts:
    try:
        content = io.open(script, encoding='utf-8').read()
    except:
        continue
    refs = re.findall(r'row\[(\d+)\]', content)
    if not refs:
        continue
    uniq = sorted(set(int(r) for r in refs))
    # 提取脚本头部注释中的列声明
    header = content[:600]
    declared = {}
    for m in re.finditer(r'(\d+)=([^,\s]+)', header):
        declared[int(m.group(1))] = m.group(2)
    print(f'【{os.path.basename(script)}】')
    for n in uniq:
        if n in VBA:
            print(f'  col{n}={VBA[n]}', end='')
            if n in declared:
                print(f'  [脚本声明:{declared[n]}]', end='')
            print()
