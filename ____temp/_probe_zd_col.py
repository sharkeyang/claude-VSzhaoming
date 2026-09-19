# -*- coding: utf-8 -*-
"""验证用户理论：中升忠跌（用EMA60长均线作为方向锚）
用户逻辑：短均线(EMA26)容易被破，长均线(EMA60)才是趋势锚
- 中(EMA26>P>EMA60)：价格在EMA60之上，长均线支持升势 → 更可能升势
- 忠(P>EMA26, EMA26<EMA60)：价格在EMA60之下，长均线支持跌势 → 更可能跌势
关键：应该用次日ZD(价格vs EMA60)验证，而非次日ZC(价格vs EMA26)
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

# 需要日ZD列。检查列位置：日ZC在col14，日ZD应该在col15附近
# 先探测日ZD列
import os
f0 = files[0]
df0 = pd.read_csv(f0, encoding='gbk', header=None, nrows=3)
hdr = df0.iloc[0].tolist()
print('表头:', [f'{i}:{h}' for i,h in enumerate(hdr) if 'ZD' in str(h) or 'ZC' in str(h) or 'ZE' in str(h)])

# 从memory：日ZC在col14，日ZE在col15。日ZD应该在col14和col15之间？
# 实际表头：col13=日ZA, col14=日ZC, col15=日ZE
# 日ZD可能没有单独列，或需要从其他列推断
# 让我检查所有含D的列
print('含D列:', [f'{i}:{h}' for i,h in enumerate(hdr) if 'D' in str(h)])