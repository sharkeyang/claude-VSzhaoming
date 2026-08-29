# -*- coding: utf-8 -*-
# 构建 3.3.1.2 拆分表（原始单表格式，乙/戊按当前ZA拆分，甲→{甲,乙(ZA>0)}合并为正交维持）
import csv, glob, json
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HX={'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
board_map=json.load(open('_产出物/MP1_花册分类映射.json',encoding='utf-8'))
GBP={'Qic','Qim','Qit'}
files=sorted(glob.glob('昭明算展/谕组周/*.csv'))
def hx_key(ab,za):
    if not ab or ab[0] not in HX: return None
    h=HX[ab[0]]
    if h in ('乙','戊'): return f"{h}(ZA{'0' if za>0 else 'n'})"
    return h
agg=defaultdict(lambda:[0.0,0,0])
for f in files:
    code=f.split('谕组周_')[-1].replace('.csv','')
    if board_map.get(code) not in GBP: continue
    rows=[]
    with open(f,encoding='gbk') as fh:
        r=csv.reader(fh); next(r)
        for row in r: rows.append(row)
    rows.sort(key=lambda x:x[0])
    for i in range(len(rows)-1):
        cur,nxt=rows[i],rows[i+1]
        try:
            za_cur=int(cur[14]); za_nxt=int(nxt[14]); pr=float(nxt[2])
        except: continue
        ck=hx_key(cur[4],za_cur); nk=hx_key(nxt[4],za_nxt)
        if not ck or not nk: continue
        agg[(ck,nk)][0]+=pr; agg[(ck,nk)][1]+=(1 if pr>0 else 0); agg[(ck,nk)][2]+=1
lab={'甲':'甲','乙(ZA0)':'乙(ZA>0)','乙(ZAn)':'乙(ZA≤0)','丙':'丙','丁':'丁','戊(ZA0)':'戊(ZA>0)','戊(ZAn)':'戊(ZA≤0)','己':'己','甲/乙(ZA0)':'甲/乙(ZA>0)'}

MEAN={}
def setm(k,n,t): MEAN[(k,n)]=t
setm('甲','甲/乙(ZA0)','维持正交，稳定（甲+乙(ZA>0)合并）')
setm('甲','乙(ZAn)','甲→乙(ZA≤0)是诱多/转弱')
setm('甲','丙','甲→丙是强烈下跌信号')
setm('甲','丁','甲→丁是转弱')
setm('甲','己','甲→己是转强')
setm('甲','戊(ZA0)','甲→戊(ZA>0)转强')
setm('甲','戊(ZAn)','甲→戊(ZA≤0)转弱')
setm('乙(ZA0)','乙(ZA0)','维持正交，稳定')
setm('乙(ZA0)','乙(ZAn)','ZA转负，转弱')
setm('乙(ZA0)','丙','乙(ZA>0)→丙是转弱信号')
setm('乙(ZA0)','丁','乙(ZA>0)→丁转弱')
setm('乙(ZA0)','甲','升级转甲')
setm('乙(ZA0)','戊(ZAn)','转弱')
setm('乙(ZA0)','己','转强')
setm('乙(ZA0)','戊(ZA0)','转强')
setm('乙(ZAn)','乙(ZA0)','重新站上WJA，转正')
setm('乙(ZAn)','丙','乙(ZA≤0)→丙是转坏（死亡螺旋起点）')
setm('乙(ZAn)','乙(ZAn)','维持脆弱平衡')
setm('乙(ZAn)','甲','升级转甲')
setm('乙(ZAn)','丁','乙(ZA≤0)→丁继续恶化')
setm('乙(ZAn)','己','转强')
setm('乙(ZAn)','戊(ZAn)','转弱')
setm('乙(ZAn)','戊(ZA0)','转强')
setm('丙','丁','丙→丁继续恶化')
setm('丙','丙','维持死亡螺旋')
setm('丙','乙(ZA0)','丙→乙(ZA>0)反转成功（正交）')
setm('丙','甲','丙→甲反转')
setm('丙','乙(ZAn)','丙→乙(ZA≤0)弱反转（仍负交）')
setm('丙','己','转强')
setm('丙','戊(ZA0)','转强')
setm('丙','戊(ZAn)','转弱')
setm('丁','丁','维持死水')
setm('丁','戊(ZA0)','丁→戊(ZA>0)筑底完成')
setm('丁','甲','丁→甲底部反转')
setm('丁','己','丁→己强势反转')
setm('丁','丙','丁→丙恶化')
setm('丁','戊(ZAn)','转弱')
setm('丁','乙(ZAn)','转弱')
setm('丁','乙(ZA0)','转强')
setm('戊(ZA0)','戊(ZAn)','戊(ZA>0)→戊(ZA≤0)转弱')
setm('戊(ZA0)','戊(ZA0)','维持')
setm('戊(ZA0)','己','戊(ZA>0)→己转强')
setm('戊(ZA0)','丁','转弱')
setm('戊(ZA0)','甲','戊(ZA>0)→甲反转')
setm('戊(ZA0)','丙','恶化')
setm('戊(ZA0)','乙(ZA0)','转强')
setm('戊(ZA0)','乙(ZAn)','转弱')
setm('戊(ZAn)','戊(ZAn)','维持死水')
setm('戊(ZAn)','戊(ZA0)','戊(ZA≤0)→戊(ZA>0)转正')
setm('戊(ZAn)','己','戊(ZA≤0)→己转强')
setm('戊(ZAn)','甲','戊(ZA≤0)→甲反转')
setm('戊(ZAn)','丁','转弱')
setm('戊(ZAn)','丙','恶化')
setm('戊(ZAn)','乙(ZA0)','转强')
setm('戊(ZAn)','乙(ZAn)','转弱')
setm('己','甲','己→甲转正交成功')
setm('己','戊(ZAn)','己→戊(ZA≤0)转弱')
setm('己','己','维持己，横盘')
setm('己','丁','转弱')
setm('己','戊(ZA0)','己→戊(ZA>0)转弱')
setm('己','丙','恶化')
setm('己','乙(ZA0)','转强')
setm('己','乙(ZAn)','转弱')

order=['甲','乙(ZA0)','乙(ZAn)','丙','丁','戊(ZA0)','戊(ZAn)','己']
out=[]
out.append("| 当前护型 | →护型 | 样本 | 转移概率 | 下周均涨幅 | 下周涨率 | 含义 |")
out.append("|:--------|:-----:|:----:|:--------:|:---------:|:--------:|:-----|")
for cur in order:
    total=sum(agg[(cur,n)][2] for (c,n) in agg if c==cur)
    if cur=='甲':
        mz=agg[('甲','甲')][2]+agg[('甲','乙(ZA0)')][2]
        prs=agg[('甲','甲')][0]+agg[('甲','乙(ZA0)')][0]
        ups=agg[('甲','甲')][1]+agg[('甲','乙(ZA0)')][1]
        rows=[('甲/乙(ZA0)',mz,prs,ups,MEAN[('甲','甲/乙(ZA0)')])]
        rest=[(n,agg[('甲',n)]) for (c,n) in agg if c=='甲' and n not in ('甲','乙(ZA0)')]
        rest.sort(key=lambda x:-x[1][2])
        for n,(s,up,nn) in rest:
            rows.append((n,nn,s,up,MEAN.get(('甲',n),'')))
    else:
        rest=[(n,agg[(cur,n)]) for (c,n) in agg if c==cur]
        rest.sort(key=lambda x:-x[1][2])
        rows=[(n,v[2],v[0],v[1],MEAN.get((cur,n),'')) for n,v in rest]
    first=True
    for n,nn,s,up,t in rows:
        curcell=f"**{lab[cur]}**" if first else ""
        out.append(f"| {curcell} | →{lab[n]} | {nn:,} | {nn/total*100:.1f}% | {s/nn:+.2f}% | {up/nn*100:.1f}% | {t} |")
        first=False
    out.append("")
print("\n".join(out))
