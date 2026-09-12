# -*- coding: utf-8 -*-
"""
周级别验证：DXZC+DXAB护型分析是否映射到周类
====================================================
日级别结论（§4.8）：操作区域=DXCD上/忐 + 甲/乙ZA>0/己/乙ZA<0
周级别等价：ZC周>0 + 甲/乙ZA>0/己/乙ZA<0

输出：
  ① 周级别各护型 P(HR≥3%)（操作区域内）——对比日级别
  ② 周级别操作区域占比
  ③ 周级别各护型转移（对比日级别交叉路口/死胡同/跳板）

周CSV列序：1=周涨, 3=HR, 4=WXAB, 13=WXCD, 14=ZA周, 16=ZC周
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row) >= 2: pool[row[0]] = row[1]
high = {k for k, v in pool.items() if v in ('Qic', 'Qim', 'Qit')}

护型映射 = {'a': '甲', 'b': '乙', 'c': '丙', 'r': '己', 'y': '戊', 'z': '丁'}

def to_f(v):
    try: return float(v)
    except: return None

# 各护型统计（操作区域内）: key -> [n, hr3, sum_hr]
stats = defaultdict(lambda: [0, 0, 0.0])
# 全样本基线
baseline = [0, 0, 0.0]
# 操作区域占比
tot_days = 0
tot_region = 0
# 转移: (cur_key, nxt_key) -> count
trans = defaultdict(int)
files_core = 0

for fname in sorted(os.listdir('昭明算展/谕组周')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组周_sz') or fname.startswith('谕组周_sh')): continue
    code = fname.replace('谕组周_', '').replace('.csv', '')
    if code not in high: continue
    files_core += 1
    prev_key = None
    try:
        with open(os.path.join('昭明算展/谕组周', fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            for row in r:
                if len(row) <= 16: continue
                wxab = row[4].strip()
                za = to_f(row[14])
                zc = to_f(row[16])
                hr = to_f(row[3])
                if za is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                hx = 护型映射.get(wxab[0], '') if wxab else ''
                if not hx: continue
                za_key = 'ZA>0' if za > 0 else ('ZA=0' if za == 0 else 'ZA<0')
                key = f'{hx}({za_key})'
                baseline[0]+=1; baseline[1]+= (1 if hr>=3 else 0); baseline[2]+=hr
                tot_days += 1
                # 操作区域：ZC周>0 + 甲/乙ZA>0/己/乙ZA<0
                in_region = (zc > 0) and (hx in ('甲', '乙', '己'))
                if in_region:
                    tot_region += 1
                    stats[key][0]+=1; stats[key][1]+= (1 if hr>=3 else 0); stats[key][2]+=hr
                # 转移
                if prev_key is not None:
                    trans[(prev_key, key)] += 1
                prev_key = key
    except Exception:
        pass

print(f'周级别高波池文件: {files_core}')
print(f'总周数: {tot_days:,}, 操作区域周数: {tot_region:,}, 占比: {tot_region/tot_days*100:.2f}%')
print()

print('=' * 70)
print('周级别 操作区域内各护型 P(HR≥3%)')
print('=' * 70)
print(f'{"护型":<12} {"n":>10} {"P(≥3%)":>8} {"均高幅":>8}')
print('-' * 45)
for k in ['甲(ZA>0)', '乙(ZA>0)', '乙(ZA<0)', '己(ZA>0)']:
    s = stats[k]
    if s[0] == 0: continue
    print(f'{k:<12} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]:>7.2f}%')
print(f'{"基线(全样本)":<12} {baseline[0]:>10,} {baseline[1]/baseline[0]*100:>7.2f}% {baseline[2]/baseline[0]:>7.2f}%')

print()
print('=' * 70)
print('周级别 各护型转移（对比日级别交叉路口/死胡同/跳板）')
print('=' * 70)
for k in ['乙(ZA<0)', '戊(ZA>0)', '丁(ZA<0)', '戊(ZA<0)']:
    all_t = {nk: c for (ck, nk), c in trans.items() if ck == k}
    tot = sum(all_t.values())
    if tot == 0: continue
    print(f'\n--- {k}（次日转移，n={tot:,}）---')
    for nk, c in sorted(all_t.items(), key=lambda x: -x[1])[:5]:
        print(f'  {nk:<12} {c:>8,}  {c/tot*100:>6.2f}%')
