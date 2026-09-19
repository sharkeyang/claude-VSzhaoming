# -*- coding: utf-8 -*-
"""Q5修正2：升连链后第1柱分布（用形态最后字母判断单柱形态）
单柱形态 = 柱排字符串形态字母的最后一个字母：
  Q=升连 W=跌连 O=升吞 V=跌吞 o=升孕 v=跌孕
升连链 = 连续多根最后字母为Q(升连)的柱排
用户指出：升连之后不会立刻出现跌连，且升孕只能跟在阴柱后面
"""
import pandas as pd, glob, sys
from collections import defaultdict
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = '昭明算展/谕组日/'
files = sorted(glob.glob(DATA_DIR + '谕组日_*.csv'))
print(f'共 {len(files)} 个文件')

def last_letter(v):
    v = str(v)
    if '.' in v:
        s = v.split('.')[1]
    else:
        s = v
    letters = [c for c in s if c in 'QOoWVv']
    return letters[-1] if letters else '?'

def form_name(l):
    return {'Q':'升连','W':'跌连','O':'升吞','V':'跌吞','o':'升孕','v':'跌孕'}.get(l, l)

# 升连链后第1柱分布
after1 = defaultdict(int)
trans = defaultdict(int)
trans_dtza = defaultdict(lambda: [0,0,0])

for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', header=None, usecols=[10,13])
    df.columns = ['柱排','日ZA']
    df['日ZA'] = pd.to_numeric(df['日ZA'], errors='coerce')
    ll = [last_letter(v) for v in df['柱排'].astype(str).tolist()]
    za = df['日ZA'].values
    n = len(ll)
    j = 0
    while j < n:
        if ll[j] == 'Q':  # 升连
            k = j
            while k < n and ll[k] == 'Q':
                k += 1
            end_za = za[k-1] if k-1 < n else None
            after = ll[k:k+10]
            if len(after) > 0:
                after1[after[0]] += 1
                first_die = None
                for idx, v in enumerate(after):
                    if v == 'W':  # 跌连
                        first_die = idx
                        break
                if after[0] == 'W':
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
                    b[1] += int(after[0] == 'W')
                    b[2] += int(first_die is not None)
            j = k
        else:
            j += 1
    if (i+1) % 2000 == 0:
        print(f'  {i+1}', flush=True)

print('\n=== 升连链后第1柱分布（形态最后字母） ===')
tot = sum(after1.values())
for v, c in sorted(after1.items(), key=lambda x: -x[1]):
    print(f'  {form_name(v)}({v}): {c} ({c/tot*100:.1f}%)')

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