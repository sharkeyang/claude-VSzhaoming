# -*- coding: utf-8 -*-
"""快速验证C8关键策略的P(>=3%)，用修正后口径(下周HR)"""
import csv, os, glob
from collections import defaultdict

csv_dir = "昭明算展/谕组周"
files = glob.glob(os.path.join(csv_dir, "*.csv"))

# 策略条件
def match(row):
    wxcd = str(row.get('WXCD',''))
    wxab = str(row.get('WXAB',''))
    zhu = str(row.get('柱排周',''))
    bo = str(row.get('波型',''))
    ying = str(row.get('盈提示',''))
    za = row.get('ZA周', 0)
    is_gold = '金' in wxcd
    is_silver = '银' in wxcd
    wxab_good = any(x in wxab for x in ['甲','乙','己'])
    is_sheng = zhu and zhu[0]=='升'
    not_preg = '尾反孕' not in zhu
    ying_s = str(ying)
    ying_gao = '高' in ying_s
    ying_gao_kuan = ('高' in ying_s) or ('宽' in ying_s)
    is_lz_lg = ('龙猪' in bo) or ('龙管' in bo)
    is_lz = '龙猪' in bo
    if is_gold and wxab_good:
        if is_sheng and not_preg:
            if ying_gao:
                return '金升非盈龙' if is_lz_lg else '金升非盈'
            else: return '金升非'
        elif is_sheng: return '金升'
        else: return '金长'
    elif is_silver:
        if ying_gao_kuan: return '银盈'
        elif '己' in wxab: return '银己'
        elif is_sheng: return '银升'
        elif is_lz: return '银猪'
        elif za>5 and za<=10: return '银ZA'
    return None

stats = defaultdict(list)
for i, f in enumerate(files):
    if i % 2000 == 0: print(f"  {i}/{len(files)}", flush=True)
    try:
        with open(f, encoding='gbk') as fh:
            r = csv.DictReader(fh)
            rows = list(r)
        for j in range(len(rows)-1):
            hr = rows[j+1].get('HR','')
            try: hr = float(hr)
            except: continue
            s = match(rows[j])
            if s: stats[s].append(hr)
    except: continue

print("\n=== 修正后口径(下周HR) 关键策略 P(>=3%) ===")
for s in ['金升非盈龙','金升非盈','金升非','金升','金长','银盈','银升','银猪','银ZA','银己']:
    v = stats.get(s, [])
    if len(v) >= 100:
        p3 = sum(1 for x in v if x>=3)/len(v)*100
        p5 = sum(1 for x in v if x>=5)/len(v)*100
        avg = sum(v)/len(v)
        print(f"{s:<10} 样本={len(v):>8}  P(>=3%)={p3:>6.1f}%  P(>=5%)={p5:>6.1f}%  均HR={avg:>6.2f}%")
