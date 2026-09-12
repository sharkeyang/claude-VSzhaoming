# -*- coding: utf-8 -*-
"""
补充验证：管宽≥10 + DJA之上跌排 的后续趋势（是否预示要退出）
用户假设2：管宽≥10时，可能已经冲高，一旦DJA之上形成跌排，就可能要退出

验证维度：
1. 次日冲高率（已确认：跌排27.96%不低）
2. 次日转坏率（次日日ZA转负 / 次日日ZC转负）
3. 后续3日累计表现
4. 次日是否仍触顶（上符串末位A）

磁盘CSV列序：8=DXCD, 9=DXAB, 10=柱排, 13=日ZA, 14=日ZC, 24=宽哼JC, 26=次日高幅, 32=上符串
"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')

pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}

def to_f(v):
    try: return float(v)
    except: return None

# 统计: key -> [n, hr3, 次日ZA转负, 次日ZC转负, 次日仍触顶]
stats = defaultdict(lambda: [0,0,0,0,0])

files_core = 0
for fname in sorted(os.listdir('昭明算展/谕组日')):
    if not fname.endswith('.csv'): continue
    if not (fname.startswith('谕组日_sz') or fname.startswith('谕组日_sh')): continue
    code = fname.replace('谕组日_','').replace('.csv','')
    if code not in high: continue
    files_core += 1
    try:
        with open(os.path.join('昭明算展/谕组日',fname), encoding='gbk') as f:
            r = csv.reader(f); next(r)
            rows = list(r)
            for i,row in enumerate(rows):
                if len(row) <= 26: continue
                zpa = to_f(row[13])
                zc = to_f(row[14])
                kw = to_f(row[24])
                hr = to_f(row[26])
                if zpa is None or zc is None or kw is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                if zpa <= 0: continue  # 只关注DJA之上
                zpaip = row[10].strip()
                is_die = '跌' in zpaip
                is_sheng = '升' in zpaip
                if kw < 10:
                    kw_key = '管宽<10'
                else:
                    kw_key = '管宽≥10'
                if is_die:
                    zp_key = '跌排'
                elif is_sheng:
                    zp_key = '升排'
                else:
                    zp_key = '非升非跌'
                # 次日数据
                nxt_za_neg = 0
                nxt_zc_neg = 0
                nxt_touch = 0
                if i+1 < len(rows):
                    nrow = rows[i+1]
                    if len(nrow) > 14:
                        nza = to_f(nrow[13])
                        nzc = to_f(nrow[14])
                        if nza is not None and nza < 0: nxt_za_neg = 1
                        if nzc is not None and nzc < 0: nxt_zc_neg = 1
                    if len(nrow) > 32:
                        sfs = nrow[32].strip()
                        if sfs and sfs[-1] == 'A': nxt_touch = 1
                key = f'{kw_key}|{zp_key}'
                s = stats[key]
                s[0]+=1; s[1]+= (1 if hr>=3 else 0); s[2]+=nxt_za_neg; s[3]+=nxt_zc_neg; s[4]+=nxt_touch
                # 全部
                s2 = stats[f'{kw_key}|全部']
                s2[0]+=1; s2[1]+= (1 if hr>=3 else 0); s2[2]+=nxt_za_neg; s2[3]+=nxt_zc_neg; s2[4]+=nxt_touch
    except Exception:
        pass

print(f'高波池文件: {files_core}')
print()

print('='*80)
print('DJA之上：管宽 × 柱排 的次日表现（冲高/转坏/触顶）')
print('='*80)
print(f'{"管宽":<10} {"柱排":<10} {"n":>10} {"P(≥3%)":>8} {"次日ZA转负":>10} {"次日ZC转负":>10} {"次日仍触顶":>10}')
print('-'*75)
for kw_key in ['管宽<10','管宽≥10']:
    for zp_key in ['升排','非升非跌','跌排','全部']:
        key = f'{kw_key}|{zp_key}'
        if key in stats:
            s = stats[key]
            print(f'{kw_key:<10} {zp_key:<10} {s[0]:>10,} {s[1]/s[0]*100:>7.2f}% {s[2]/s[0]*100:>9.2f}% {s[3]/s[0]*100:>9.2f}% {s[4]/s[0]*100:>9.2f}%')
    print('-'*75)
