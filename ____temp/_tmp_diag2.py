# -*- coding: utf-8 -*-
import sys; sys.stdout.reconfigure(encoding='utf-8')
import csv, os, json
from collections import defaultdict
DATA_DIR='昭明算展/谕组周'
BM=json.load(open('_产出物/MP1_花册分类映射.json',encoding='utf-8'))
高波池={'Qic','Qim','Qit'}
HX={'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
def f(v):
    try:return float(v)
    except:return None

# 1. 本周降转(WXAB<0且WXZB>0)时，本周护型分布
# 2. 本周降转时，前周护型分布
# 3. 前周丁/戊(WXZA<0)+本周降转 → 下周主升率（重新验证）
cur_hx_dist=defaultdict(int)
prev_hx_dist=defaultdict(int)
stat=defaultdict(lambda:[0,0])  # key->[n, 下周主升]

for fn in sorted(os.listdir(DATA_DIR)):
    if not fn.startswith('谕组周_') or not fn.endswith('.csv'):continue
    cid=fn.replace('谕组周_','').replace('.csv','')
    if BM.get(cid,'') not in 高波池:continue
    try:
        rows=list(csv.reader(open(os.path.join(DATA_DIR,fn),encoding='gbk')))
        rows=rows[1:]
    except:continue
    for i in range(len(rows)-1):
        row=rows[i]
        if len(row)<=20:continue
        wxab=f(row[20]);wxzb=f(row[15]);wxza=f(row[14])
        if wxab is None or wxzb is None or wxza is None:continue
        if not (wxab<0 and wxzb>0):continue
        # 本周降转
        cur_hx=HX.get(str(row[4])[:1],'')
        cur_hx_dist[cur_hx]+=1
        # 前周
        if i-1<0:continue
        prow=rows[i-1]
        if len(prow)<=20:continue
        phx=HX.get(str(prow[4])[:1],'')
        pza=f(prow[14])
        prev_hx_dist[phx]+=1
        # 下周
        nxt=rows[i+1]
        if len(nxt)<=20:continue
        nab=f(nxt[20]);nzb=f(nxt[15])
        if nab is None or nzb is None:continue
        nz=(nab>0 and nzb>0)
        # 分组：前周丁/戊(WXZA<0)
        if phx in ('丁','戊') and pza is not None and pza<0:
            key=f'前周{phx}(WXZA<0)'
            s=stat[key];s[0]+=1
            if nz:s[1]+=1

print('=== 本周降转(WXAB<0且WXZB>0)时，本周护型分布 ===')
for k,v in sorted(cur_hx_dist.items(),key=lambda x:-x[1]):
    print(f'  本周护型 {k}: {v}')

print()
print('=== 本周降转时，前周护型分布 ===')
for k,v in sorted(prev_hx_dist.items(),key=lambda x:-x[1]):
    print(f'  前周护型 {k}: {v}')

print()
print('=== 前周丁/戊(WXZA<0)+本周降转 → 下周主升率 ===')
for k,s in sorted(stat.items(),key=lambda kv:-(kv[1][1]/kv[1][0] if kv[1][0] else 0)):
    print(f'  {k}: n={s[0]}, 下周主升={s[1]} ({s[1]/s[0]*100:.1f}%)')