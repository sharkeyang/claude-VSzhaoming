# -*- coding: utf-8 -*-
import csv, sys, glob, json
from collections import defaultdict
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
board_map = json.load(open('_产出物/MP1_花册分类映射.json', encoding='utf-8'))
GBP = {'Qic','Qim','Qit'}
files = sorted(glob.glob('昭明算展/谕组周/*.csv'))
agg = defaultdict(lambda: [0.0,0,0])
def hx_key(ab,za):
    if not ab or ab[0] not in HX: return None
    h=HX[ab[0]]
    if h in ('乙','戊'):
        return f"{h}(ZA{'0' if za>0 else 'n'})"
    return h
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
        agg[(ck,nk)][0]+=pr; agg[(ck,nk)][1]+=1 if pr>0 else 0; agg[(ck,nk)][2]+=1

# 含义标注（逻辑正确）
MEANING = {
    ('甲','甲'):'维持正交，稳定',
    ('甲','乙(ZA0)'):'正交延续（降级为乙，ZA仍>0）',
    ('甲','乙(ZAn)'):'甲→乙(ZA≤0)是诱多/转弱',
    ('甲','丙'):'甲→丙是强烈下跌信号',
    ('甲','丁'):'甲→丁是转弱',
    ('甲','戊(ZA0)'):'甲→戊(ZA>0)转强',
    ('甲','戊(ZAn)'):'甲→戊(ZA≤0)转弱',
    ('甲','己'):'甲→己是转强',
    ('乙(ZA0)','乙(ZA0)'):'维持正交，稳定',
    ('乙(ZA0)','乙(ZAn)'):'ZA转负，转弱',
    ('乙(ZA0)','丙'):'乙(ZA>0)→丙是转弱信号',
    ('乙(ZA0)','丁'):'乙(ZA>0)→丁转弱',
    ('乙(ZA0)','甲'):'升级转甲',
    ('乙(ZA0)','戊(ZA0)'):'转强',
    ('乙(ZA0)','戊(ZAn)'):'转弱',
    ('乙(ZA0)','己'):'转强',
    ('乙(ZAn)','乙(ZA0)'):'重新站上WJA，转正',
    ('乙(ZAn)','乙(ZAn)'):'维持脆弱平衡',
    ('乙(ZAn)','丙'):'乙(ZA≤0)→丙是转坏（死亡螺旋起点）',
    ('乙(ZAn)','丁'):'乙(ZA≤0)→丁继续恶化',
    ('乙(ZAn)','甲'):'升级转甲',
    ('乙(ZAn)','戊(ZA0)'):'转强',
    ('乙(ZAn)','戊(ZAn)'):'转弱',
    ('乙(ZAn)','己'):'转强',
    ('丙','乙(ZA0)'):'丙→乙(ZA>0)反转成功（正交）',
    ('丙','乙(ZAn)'):'丙→乙(ZA≤0)弱反转（仍负交）',
    ('丙','丙'):'维持死亡螺旋',
    ('丙','丁'):'丙→丁继续恶化',
    ('丙','甲'):'丙→甲反转',
    ('丙','戊(ZA0)'):'转强',
    ('丙','戊(ZAn)'):'转弱',
    ('丙','己'):'转强',
    ('丁','甲'):'丁→甲底部反转',
    ('丁','乙(ZA0)'):'转强',
    ('丁','乙(ZAn)'):'转弱',
    ('丁','丙'):'丁→丙恶化',
    ('丁','丁'):'维持死水',
    ('丁','戊(ZA0)'):'丁→戊(ZA>0)筑底完成',
    ('丁','戊(ZAn)'):'转弱',
    ('丁','己'):'丁→己强势反转',
    ('戊(ZA0)','甲'):'戊(ZA>0)→甲反转',
    ('戊(ZA0)','乙(ZA0)'):'转强',
    ('戊(ZA0)','乙(ZAn)'):'转弱',
    ('戊(ZA0)','丙'):'恶化',
    ('戊(ZA0)','丁'):'转弱',
    ('戊(ZA0)','戊(ZA0)'):'维持',
    ('戊(ZA0)','戊(ZAn)'):'戊(ZA>0)→戊(ZA≤0)转弱',
    ('戊(ZA0)','己'):'戊(ZA>0)→己转强',
    ('戊(ZAn)','甲'):'戊(ZA≤0)→甲反转',
    ('戊(ZAn)','乙(ZA0)'):'转强',
    ('戊(ZAn)','乙(ZAn)'):'转弱',
    ('戊(ZAn)','丙'):'恶化',
    ('戊(ZAn)','丁'):'转弱',
    ('戊(ZAn)','戊(ZA0)'):'戊(ZA≤0)→戊(ZA>0)转正',
    ('戊(ZAn)','戊(ZAn)'):'维持死水',
    ('戊(ZAn)','己'):'戊(ZA≤0)→己转强',
    ('己','甲'):'己→甲转正交成功',
    ('己','乙(ZA0)'):'转强',
    ('己','乙(ZAn)'):'转弱',
    ('己','丙'):'恶化',
    ('己','丁'):'转弱',
    ('己','戊(ZA0)'):'己→戊(ZA>0)转弱',
    ('己','戊(ZAn)'):'己→戊(ZA≤0)转弱',
    ('己','己'):'维持己，横盘',
}
HX_LABEL={'甲':'甲','乙(ZA0)':'乙(ZA>0)','乙(ZAn)':'乙(ZA≤0)','丙':'丙','丁':'丁','戊(ZA0)':'戊(ZA>0)','戊(ZAn)':'戊(ZA≤0)','己':'己'}
cur_order=['甲','乙(ZA0)','乙(ZAn)','丙','丁','戊(ZA0)','戊(ZAn)','己']
out=[]
for cur in cur_order:
    total=sum(agg[(cur,n)][2] for (c,n) in agg if c==cur)
    out.append(f"**{HX_LABEL[cur]}（总样本 {total:,}）：**")
    out.append("| →护型 | 样本 | 转移概率 | 下周均涨幅 | 下周涨率 | 含义 |")
    out.append("|:-----|:----:|:--------:|:---------:|:--------:|:-----|")
    # 按转移概率降序
    rows=[(n,agg[(cur,n)]) for (c,n) in agg if c==cur]
    rows.sort(key=lambda x:-x[1][2])
    for n,(s,up,nn) in rows:
        mean=s/nn if nn else 0; rate=up/nn*100 if nn else 0; pct=nn/total*100 if total else 0
        m=MEANING.get((cur,n),'')
        out.append(f"| →{HX_LABEL[n]} | {nn:,} | {pct:.1f}% | {mean:+.2f}% | {rate:.1f}% | {m} |")
    out.append("")
print("\n".join(out))
