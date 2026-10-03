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

# 诊断：当前周降转(WXAB<0且WXZB>0)，前周丁/戊(WXZA<0)的样本
# 打印前几行的完整字段，确认护型判断
cnt=0
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
        if i-1<0:continue
        prow=rows[i-1]
        if len(prow)<=20:continue
        phx=HX.get(str(prow[4])[:1],'')
        pza=f(prow[14])
        if phx not in ('丁','戊') or pza is None or pza>=0:continue
        # 前周丁/戊(WXZA<0) + 本周降转
        nxt=rows[i+1]
        if len(nxt)<=20:continue
        nab=f(nxt[20]);nzb=f(nxt[15])
        nz=(nab is not None and nzb is not None and nab>0 and nzb>0)
        if cnt<5:
            print(f'文件={fn} 行={i}')
            print(f'  前周: 护型串="{prow[4]}" 护型={phx} WXZA={pza} WXZB={f(prow[15])} WXAB={f(prow[20])}')
            print(f'  本周: 护型串="{row[4]}" WXZA={wxza} WXZB={wxzb} WXAB={wxab}')
            print(f'  下周: WXAB={nab} WXZB={nzb} 主升={nz}')
            cnt+=1
    if cnt>=5:break
print(f'\n(打印了{cnt}个样本)')