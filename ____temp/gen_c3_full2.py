# -*- coding: utf-8 -*-
# 全面重算 C3 文档（全量统一到当前谕组周 CSV）
# 输出所有 3.3.x 需要的数字：3.3.1.1(WXZC) / 3.3.1.3(WXCD六域) / 3.3.2 / 3.3.4-3.3.8 专题
import csv, glob, json
from collections import defaultdict
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

HX = {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}
ZONE = {chr(0x91d1):'金', chr(0x94f6):'银', chr(0x5618):'唏', chr(0x550f):'嘘', chr(0x5c3f):'尿', chr(0x5c4e):'屎'}
board_map = json.load(open('_产出物/MP1_花册分类映射.json', encoding='utf-8'))
GBP = {'Qic','Qim','Qit'}
files = sorted(glob.glob('昭明算展/谕组周/*.csv'))

def hx_key(ab, za):
    if not ab or ab[0] not in HX: return None
    h = HX[ab[0]]
    if h in ('乙','戊'):
        return f"{h}(ZA{'0' if za>0 else 'n'})"
    return h

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

def build_trans(pred):
    agg = defaultdict(lambda: [0.0,0,0])
    for code, rows in data_by_code.items():
        for i in range(len(rows)-1):
            cur, nxt = rows[i], rows[i+1]
            try:
                za_cur=int(cur[14]); za_nxt=int(nxt[14]); pr=float(nxt[2]); zc=float(cur[16])
                wxcd=cur[13][0] if cur[13] else ''
            except: continue
            ck=hx_key(cur[4],za_cur); nk=hx_key(nxt[4],za_nxt)
            if not ck or not nk: continue
            if not pred(zc, wxcd): continue
            agg[(ck,nk)][0]+=pr; agg[(ck,nk)][1]+= (1 if pr>0 else 0); agg[(ck,nk)][2]+=1
    return agg

def fmt_matrix(agg, order):
    lines=[]
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
        lines.append(f"{cur}({tot:,}): "+" | ".join(cells))
    return "\n".join(lines)

order=['甲','乙(ZA0)','乙(ZAn)','丙','丁','戊(ZA0)','戊(ZAn)','己']

print("### 3.3.1.1 按WXZC符号 (col order: 甲 乙0 乙n 丙 丁 戊0 戊n 己)")
for condname, pred in [('ZC>0', lambda z,w: z>0), ('ZC≤0', lambda z,w: z<=0)]:
    print(f"\n--- {condname} ---")
    print(fmt_matrix(build_trans(pred), order))

print("\n\n### 3.3.1.3 按WXCD六域")
for zn in ['金','银','唏','嘘','尿','屎']:
    zc_ok = zn in ('金','银','唏')
    print(f"\n--- WXCD={zn} ({'ZC>0' if zc_ok else 'ZC≤0'}) ---")
    print(fmt_matrix(build_trans(lambda z,w,zn=zn: ZONE.get(w)==zn), order))

# ========== 3.3.2 ZA 持有状态 ==========
print("\n\n### 3.3.2 ZA持有状态")
st=defaultdict(lambda:[0.0,0,0])
for code, rows in data_by_code.items():
    for row in rows:
        try:
            g=float(row[1]); za=int(row[14]); ab=row[4]
        except: continue
        ck=hx_key(ab,za)
        if not ck: continue
        st[ck][0]+=g; st[ck][1]+=(1 if g>0 else 0); st[ck][2]+=1
for ck in ['甲','乙(ZA0)','乙(ZAn)','戊(ZA0)','戊(ZAn)','己']:
    if ck in st:
        s,up,n=st[ck]
        print(f"{ck}: 样本{n:,} 今均{s/n:+.2f}% 今涨率{up/n*100:.1f}%")
