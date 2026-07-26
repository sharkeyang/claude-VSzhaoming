#!/usr/bin/env python3
"""分析DXEF-DXCD框架概率"""
import csv, os, sys, glob
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

DIR = 'D:/@VSwork/VS昭明计划VBA优化/____temp/谕组日/'
files = sorted(glob.glob(os.path.join(DIR, '谕组日_*.csv')))
print(f'文件: {len(files)} 只')

def safe_int(v):
    try: return int(float(v)) if v else 0
    except: return 0

stats = defaultdict(lambda: {'n':0, 'ze':0, 'zc':0, 'za':0})
count = 0

for f in files:
    with open(f, 'r', encoding='gbk') as fh:
        rows = list(csv.DictReader(fh))
    # 提取DXEF非空的行
    valid = [(rows[i], rows[i+1]) for i in range(len(rows)-1) if rows[i].get('DXEF','')]

    for r, n in valid:
        dxef = r.get('DXEF','') or ''
        dxcd = r.get('DXCD','') or ''
        za = safe_int(r.get('日ZA','0'))
        zc = safe_int(r.get('日ZC','0'))
        ze = safe_int(r.get('日ZE','0'))
        n_ze = safe_int(n.get('日ZE','0'))
        n_zc = safe_int(n.get('日ZC','0'))
        n_za = safe_int(n.get('日ZA','0'))

        ef = '?'
        for tag in ['金','银','唏','嘘','屎','尿']:
            if tag in dxef: ef = tag; break

        cd_pos = dxcd in ('上','中','下')
        zc_pos = zc > 0
        za_pos = za > 0
        ze_pos = ze > 0

        if ef in ('金','银') and ze_pos:
            if cd_pos and zc_pos:
                state = '金银/主战场/主动' if za_pos else '金银/主战场/被动持有'
            elif cd_pos and not zc_pos:
                state = '金银/可暂退'
            else:
                state = '金银/其他'
        elif ef in ('金','银') and not ze_pos:
            state = '嘘/必须退出'
        elif ef in ('唏','嘘') and ze_pos:
            if dxcd in ('上','忐'): state = '唏/可试仓'
            elif dxcd in ('下','忑'): state = '唏/可警惕'
            else: state = '唏/仅观察'
        elif ef in ('唏','嘘') and not ze_pos:
            state = '唏/仅观察'
        else:
            if cd_pos and zc_pos:
                state = '屎尿/主战场/主动' if za_pos else '屎尿/主战场/被动持有'
            elif cd_pos and not zc_pos:
                state = '屎尿/可暂退'
            elif not cd_pos and zc_pos:
                state = '屎尿/以DJC为丘试仓'
            elif not cd_pos and not zc_pos:
                state = '屎尿/完全禁止(最危险)' if za_pos else '屎尿/完全禁止'
            else:
                state = '屎尿/其他'

        s = stats[state]
        s['n'] += 1
        if n_ze > 0: s['ze'] += 1
        if n_ze > 0 and n_zc > 0: s['zc'] += 1
        if n_ze > 0 and n_zc > 0 and n_za > 0: s['za'] += 1
        count += 1

    if count % 100000 == 0:
        print(f'  已处理: {count} 行')

print(f'\n总行数: {count}')
print()
print(f'{"="*75}')
print(f'DXEF-DXCD完整验证（{len(files)}只股票）')
print(f'{"="*75}')
print(f'{"状态":<30s} {"样本":>8s} {"→ZE>0":>8s} {"→ZE>0+ZC>0":>12s} {"→ZE>0+ZC+ZA>0":>14s}')
print(f'{"-"*70}')
for state in sorted(stats.keys()):
    s = stats[state]
    if s['n'] < 5: continue
    p1 = s['ze']/s['n']*100
    p2 = s['zc']/s['n']*100
    p3 = s['za']/s['n']*100
    mark = '✅' if p1 > 80 else ('⚠️' if p1 > 50 else ('❌' if p1 < 20 else ''))
    print(f'{state:<30s} {s["n"]:>8d} {p1:>7.1f}% {p2:>10.1f}% {p3:>12.1f}%  {mark}')