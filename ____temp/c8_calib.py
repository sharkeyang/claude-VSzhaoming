# -*- coding: utf-8 -*-
"""C8 校准：计算全量基准 P(>=3%) 与 金升 各定义，对比文档 §3.1.3"""
import glob, csv, os

DATA_DIR = r"d:/@VSwork/VS昭明计划VBA优化/昭明算展/谕组周"
OUT = r"d:/@VSwork/VS昭明计划VBA优化/____temp/c8_calib.txt"

C_HR=3; C_HUXING=4; C_BOXING=5; C_ZHUP=6; C_YING=12; C_ZC=15; C_CD=24; C_ZB=14

def is_jin(hx): return hx[0] in ('a','b','r') if hx else False
def is_sheng(zp): return '升' in zp if zp else False

files = glob.glob(os.path.join(DATA_DIR, "谕组周_*.csv"))
out = open(OUT,'w',encoding='utf-8')

# 统计
tot_n=0; tot_hit=0
# 金升 定义A: 甲乙己+升排 (无ZC)
a_n=0; a_hit=0
# 金升 定义B: ZC>0+甲乙己+升排
b_n=0; b_hit=0
# 金升 定义C: 甲乙己+升排+ZC>0+CD>0+ZB>0 (多长)
c_n=0; c_hit=0

for f in files:
    with open(f,encoding='gbk') as fh:
        r=csv.reader(fh); header=next(r); rows=list(r)
    for i in range(len(rows)-1):
        cur=rows[i]; nxt=rows[i+1]
        hx=cur[C_HUXING]; zp=cur[C_ZHUP]
        try: hr=float(nxt[C_HR])
        except: hr=0.0
        hit = hr>=3.0
        tot_n+=1
        if hit: tot_hit+=1
        if is_jin(hx) and is_sheng(zp):
            a_n+=1
            if hit: a_hit+=1
            try: zc=float(cur[C_ZC])
            except: zc=0.0
            if zc>0:
                b_n+=1
                if hit: b_hit+=1
                try: cd=float(cur[C_CD]); zb=float(cur[C_ZB])
                except: cd=0.0; zb=0.0
                if cd>0 and zb>0:
                    c_n+=1
                    if hit: c_hit+=1

def pct(n,h): return f"{100.0*h/n:.1f}%" if n else "0"
print(f"全量基准: 样本={tot_n} P(>=3%)={pct(tot_n,tot_hit)}", file=out)
print(f"金升A(甲乙己+升排): 样本={a_n} P={pct(a_n,a_hit)}", file=out)
print(f"金升B(ZC>0+甲乙己+升排): 样本={b_n} P={pct(b_n,b_hit)}", file=out)
print(f"金升C(多长+甲乙己+升排): 样本={c_n} P={pct(c_n,c_hit)}", file=out)
print("DONE", file=out)
out.close()
