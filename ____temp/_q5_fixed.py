# -*- coding: utf-8 -*-
"""Q5修正：升连链后第1柱分布（正确柱排分类）
用户指出：升孕只能跟在阴柱后面，所以升连链后第1柱不可能是升孕
柱排分类（按前缀）：
  升.尾连 = 升连（升排）
  跌.尾连 = 跌连（跌排）
  升.尾吞 = 升吞
  跌.尾吞 = 跌吞
  升.尾反孕 = 升孕（升排孕线）
  跌.尾反孕 = 跌孕
  (升)人.连后吞 = 连后吞偏升
  (跌)人.连后吞 = 连后吞偏跌
  (升)人.吞吞 / (跌)人.吞吞 / (人)人.吞吞 = 吞吞
  (升)人.孕孕 / (跌)人.孕孕 / (人)人.孕孕 = 孕孕
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

def classify_zp(v):
    v = str(v)
    if v.startswith('升.尾连'): return '升连'
    if v.startswith('跌.尾连'): return '跌连'
    if v.startswith('升.尾吞'): return '升吞'
    if v.startswith('跌.尾吞'): return '跌吞'
    if v.startswith('升.尾反孕'): return '升孕'
    if v.startswith('跌.尾反孕'): return '跌孕'
    if '连后吞' in v: return '连后吞'
    if '吞吞' in v: return '吞吞'
    if '孕孕' in v: return '孕孕'
    if v.startswith('首柱'): return '首柱'
    return '其他'

# 升连链后第1柱分布 + 到跌连的过渡
after1 = defaultdict(int)
trans = defaultdict(int)
trans_dtza = defaultdict(lambda: [0,0,0])

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10,13])
    df.columns = ['柱排','日ZA']
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    cls = [classify_zp(v) for v in df['柱排'].astype(str).tolist()]
    za = df['日ZA'].values
    n = len(cls)
    j = 0
    while j < n:
        if cls[j] == '升连':
            k = j
            while k < n and cls[k] == '升连':
                k += 1
            length = k - j
            end_za = za[k-1] if k-1 < n else None
            after = cls[k:k+10]
            if len(after) > 0:
                after1[after[0]] += 1
                first_die = None
                for idx, v in enumerate(after):
                    if v == '跌连':
                        first_die = idx
                        break
                if after[0] == '跌连':
                    t = '立即跌连'
                elif first_die is not None:
                    t = '过渡后跌连'
                else:
                    t = '10柱内无跌连'
                trans[t] += 1
                if end_za is not None:
                    if end_za >= 4: zone = 'DTZA>=4'
                    elif end_za >= 2: zone = 'DTZA2-3'
                    elif end_za >= 0: zone = 'DTZA0-2'
                    else: zone = 'DTZA<0'
                    b = trans_dtza[zone]
                    b[0] += 1
                    b[1] += int(after[0] == '跌连')
                    b[2] += int(first_die is not None)
            j = k
        else:
            j += 1
    if (i+1) % 2000 == 0:
        print(f'  {i+1}', flush=True)

print('\n=== 升连链后第1柱分布 ===')
tot = sum(after1.values())
for v, c in sorted(after1.items(), key=lambda x: -x[1]):
    print(f'  {v}: {c} ({c/tot*100:.1f}%)')

print('\n=== 过渡类型（所有升连链） ===')
tot2 = sum(trans.values())
for t, c in sorted(trans.items(), key=lambda x: -x[1]):
    print(f'  {t}: {c} ({c/tot2*100:.1f}%)')

print('\n=== 按链末DTZA ===')
print(f"{'区间':<10}{'样本':>8}{'立即跌连%':>10}{'最终跌连%':>10}")
for zone in ['DTZA>=4','DTZA2-3','DTZA0-2','DTZA<0']:
    b = trans_dtza[zone]
    if b[0] > 0:
        print(f"{zone:<10}{b[0]:>8}{b[1]/b[0]*100:>10.2f}{b[2]/b[0]*100:>10.2f}")