# -*- coding: utf-8 -*-
"""计算各护型 P(>=3%) 下周HR，对比 §2.1.7"""
import glob, csv, os
DATA_DIR = r"d:/@VSwork/VS昭明计划VBA优化/昭明算展/谕组周"
OUT = r"d:/@VSwork/VS昭明计划VBA优化/____temp/c8_huxing.txt"
C_HR=3; C_HUXING=4
files = glob.glob(os.path.join(DATA_DIR,"谕组周_*.csv"))
stats={}
for f in files:
    with open(f,encoding='gbk') as fh:
        r=csv.reader(fh); next(r); rows=list(r)
    for i in range(len(rows)-1):
        cur=rows[i]; nxt=rows[i+1]
        hx=cur[C_HUXING]
        if not hx: continue
        key=hx[0]
        try: hr=float(nxt[C_HR])
        except: hr=0.0
        stats.setdefault(key,[0,0])
        stats[key][0]+=1
        if hr>=3.0: stats[key][1]+=1
out=open(OUT,'w',encoding='utf-8')
names={'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
for k in ['a','b','c','z','y','r']:
    if k in stats:
        n,h=stats[k]
        print(f"{names[k]}({k}): 样本={n} P(>=3%)={100.0*h/n:.1f}%", file=out)
out.close()
