# -*- coding: utf-8 -*-
"""验证己/戊(ZA>0)不转甲的情况（DXZC>0）"""
import csv, os, sys
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8')
pool = {}
with open('____temp/花册_市板映射.csv', encoding='utf-8-sig') as f:
    r = csv.reader(f); next(r)
    for row in r:
        if len(row)>=2: pool[row[0]]=row[1]
high = {k for k,v in pool.items() if v in ('Qic','Qim','Qit')}
护型映射 = {'a':'甲','b':'乙','c':'丙','r':'己','y':'戊','z':'丁'}
def to_f(v):
    try: return float(v)
    except: return None
def parse_hx(dxab):
    if not dxab or len(dxab)<1: return ''
    return 护型映射.get(dxab[0],'')
# (护型, 指标, 值) -> [n, 转甲n]
stats = defaultdict(lambda: [0,0])
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
                if len(row) <= 46: continue
                dxab = row[9].strip()
                za = to_f(row[13]); zc = to_f(row[14]); hr = to_f(row[26])
                if za is None or zc is None or hr is None: continue
                if hr < -50 or hr > 50: continue
                if zc <= 0: continue
                hx = parse_hx(dxab)
                if hx not in ('己','戊'): continue
                if hx=='戊' and za<=0: continue
                nxt_hx = ''
                if i+1 < len(rows):
                    nrow = rows[i+1]
                    if len(nrow) > 9: nxt_hx = parse_hx(nrow[9].strip())
                to_jia = 1 if nxt_hx=='甲' else 0
                # 柱排
                zpaip = row[10].strip()
                if '跌' in zpaip: zp='跌排'
                elif '升' in zpaip: zp='升排'
                else: zp='非升非跌'
                stats[(hx,'柱排',zp)][0]+=1; stats[(hx,'柱排',zp)][1]+=to_jia
                # 盈提示
                ying = row[12].strip()
                if '偏' in ying or '宽' in ying: yk='偏/宽'
                elif ying=='a' or ying=='雀': yk='a系/雀'
                else: yk='其他'
                stats[(hx,'盈提示',yk)][0]+=1; stats[(hx,'盈提示',yk)][1]+=to_jia
                # 日等型（col44，等1-等7）
                deng = row[44].strip()
                stats[(hx,'日等型',deng)][0]+=1; stats[(hx,'日等型',deng)][1]+=to_jia
                # 管宽（宽哼JC[22]）
                kw = to_f(row[22])
                if kw is not None:
                    kk = '管宽≥10' if kw>=10 else '管宽<10'
                    stats[(hx,'管宽',kk)][0]+=1; stats[(hx,'管宽',kk)][1]+=to_jia
                # BSHA[19]
                bsha = to_f(row[19])
                if bsha is not None:
                    bk = 'BSHA≥8' if bsha>=8 else ('BSHA3-8' if bsha>=3 else 'BSHA<3')
                    stats[(hx,'BSHA',bk)][0]+=1; stats[(hx,'BSHA',bk)][1]+=to_jia
    except Exception:
        pass
print(f'高波池文件: {files_core}')
print()
for hx in ['己','戊']:
    print(f'=== {hx} 转甲率（DXZC>0）===')
    for ind in ['柱排','盈提示','日等型','管宽','BSHA']:
        for val in sorted(set(k[2] for k in stats if k[0]==hx and k[1]==ind)):
            key=(hx,ind,val)
            if key in stats:
                s=stats[key]
                if s[0]>=500:
                    print(f'  {ind}={val}: n={s[0]:,} 转甲率={s[1]/s[0]*100:.2f}%')
    print()
