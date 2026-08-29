# -*- coding: utf-8 -*-
# 全面重算 C3 文档的转移矩阵与护型统计（基于当前谕组周 CSV）
# 输出：所有 3.3.x 需要的数字
import csv, glob, json
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
board_map = json.load(open('_产出物/MP1_花册分类映射.json', encoding='utf-8'))
GBP = {'Qic','Qim','Qit'}
files = sorted(glob.glob('昭明算展/谕组周/*.csv'))

def hx_key(ab, za):
    if not ab or ab[0] not in HX: return None
    h = HX[ab[0]]
    if h in ('乙','戊'):
        return f"{h}(ZA{'0' if za>0 else 'n'})"
    return h

# ---- 收集所有(代码, 行) ----
# 每条记录: (code, date, 周涨[1], PR[2], HR[3], WXAB[4], WXCD[13], ZA[14], ZC[16])
data_by_code = {}
for f in files:
    code = f.split('谕组周_')[-1].replace('.csv','')
    if board_map.get(code) not in GBP: continue
    rows=[]
    with open(f, encoding='gbk') as fh:
        r = csv.reader(fh); next(r)
        for row in r: rows.append(row)
    rows.sort(key=lambda x: x[0])
    data_by_code[code] = rows

# ============ 通用转移计数 ============
# trans[(cond, cur, nxt)] -> (PR_sum, up_count, count)
# cond: 'ALL','ZC>0','ZC≤0','金','银','唏','嘘','尿','屎'
def build_trans(cond_key, wxd_filter=None):
    agg = defaultdict(lambda: [0.0,0,0])
    for code, rows in data_by_code.items():
        for i in range(len(rows)-1):
            cur, nxt = rows[i], rows[i+1]
            try:
                za_cur=int(cur[14]); za_nxt=int(nxt[14])
                zc=float(cur[16]); pr=float(nxt[2]); wxcd=cur[13]
            except: continue
            ck=hx_key(cur[4],za_cur); nk=hx_key(nxt[4],za_nxt)
            if not ck or not nk: continue
            if cond_key=='ZC>0' and not (zc>0): continue
            if cond_key=='ZC≤0' and not (zc<=0): continue
            if cond_key=='WXCD' and wxcd!=wxd_filter: continue
            agg[(ck,nk)][0]+=pr; agg[(ck,nk)][1]+= (1 if pr>0 else 0); agg[(ck,nk)][2]+=1
    return agg

# ============ 护型排序（3.2.1 复用）============
def hx_stats_this_week():
    # 本周涨幅/涨率 by 护型 and ZC 域
    st=defaultdict(lambda: [0.0,0,0])  # (cond,ck)->(sum_gain, up, count)
    for code, rows in data_by_code.items():
        for cur in rows:
            try:
                g=float(cur[1]); zc=float(cur[16]); za=int(cur[14]); ab=cur[4]
            except: continue
            ck=hx_key(ab,za)
            if not ck: continue
            for cond,ok in [('ALL',True),('ZC>0',zc>0),('ZC≤0',zc<=0)]:
                if ok:
                    st[(cond,ck)][0]+=g; st[(cond,ck)][1]+=(1 if g>0 else 0); st[(cond,ck)][2]+=1
    return st

# ============ 各护型专题（3.3.4-3.3.8）============
# 样本/今均涨幅/今涨率/ZA中位数/持续天数/转移去向/转移来源
# 持续天数: 连续相同护型的周数
def duration_stats():
    dur=defaultdict(list)
    for code, rows in data_by_code.items():
        # 连续段
        seq=[]  # (ck,)
        for row in rows:
            try: za=int(row[14]); ab=row[4]
            except: continue
            ck=hx_key(ab,za)
            if not ck: ck='__gap__'
            seq.append(ck)
        i=0
        while i<len(seq):
            ck=seq[i]
            if ck=='__gap__':
                i+=1; continue
            j=i
            while j<len(seq) and seq[j]==ck: j+=1
            dur[ck].append(j-i)
            i=j
    out={}
    for ck in ['甲','乙(ZA0)','乙(ZAn)','丙','丁','戊(ZA0)','戊(ZAn)','己']:
        vals=dur[ck]
        if not vals: continue
        vals.sort()
        med=vals[len(vals)//2] if len(vals)%2 else (vals[len(vals)//2-1]+vals[len(vals)//2])/2
        out[ck]=(len(vals), sum(vals)/len(vals), med)
    return out

print("="*60)
print("【3.3.2 ZA持有状态】（本周涨幅 by 护型×ZA）")
st=hx_stats_this_week()
for ck in ['甲','乙(ZA0)','乙(ZAn)','戊(ZA0)','戊(ZAn)','己']:
    if ('ALL',ck) in st:
        s,up,n=st[('ALL',ck)]
        print(f"{ck}: 样本{n:,} 今均{s/n:+.2f}% 今涨率{up/n*100:.1f}%")

print()
print("="*60)
print("【3.3.1.1 按WXZC符号 - 转移矩阵(全8x8)】")
for cond in ['ZC>0','ZC≤0']:
    agg=build_trans(cond)
    print(f"\n--- {cond} ---")
    order=['甲','乙(ZA0)','乙(ZAn)','丙','丁','戊(ZA0)','戊(ZAn)','己']
    cols=order
    for cur in order:
        row_agg={nk:v for (c,nk),v in agg.items() if c==cur}
        tot=sum(v[2] for v in row_agg.values())
        if tot==0: continue
        cells=[]
        for nk in cols:
            if nk in row_agg:
                cells.append(f"{row_agg[nk][2]/tot*100:.1f}")
            else:
                cells.append("0")
        print(f"{cur}({tot:,}): "+" ".join(cells))

print()
print("="*60)
print("【3.3.1.3 按WXCD - 转移矩阵(全8x8)】")
wxd_order=['金','银','唏','嘘','尿','屎']
for wd in wxd_order:
    agg=build_trans('WXCD', wd)
    print(f"\n--- WXCD={wd} ---")
    order=['甲','乙(ZA0)','乙(ZAn)','丙','丁','戊(ZA0)','戊(ZAn)','己']
    for cur in order:
        row_agg={nk:v for (c,nk),v in agg.items() if c==cur}
        tot=sum(v[2] for v in row_agg.values())
        if tot==0: continue
        cells=[]
        for nk in order:
            if nk in row_agg:
                cells.append(f"{row_agg[nk][2]/tot*100:.1f}")
            else:
                cells.append("0")
        print(f"{cur}({tot:,}): "+" ".join(cells))
