# -*- coding: utf-8 -*-
"""按 DXCD=中/下/忑 拆分，验证各 CD 在 DXZC<0 + AB甲乙己 时的次日转正率。
看下/忑 是否也有"很快转正→窗口太短"机制。
用法: python c2_zc_pos_follow_bycd.py [文件数]
输出: ____temp/c2_zc_pos_follow_bycd_result.txt
"""
import io, sys, glob, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c2_zc_pos_follow_bycd_result.txt')
out = io.open(OUT, 'w', encoding='utf-8')
sys.stdout = out

N_FILES = int(sys.argv[1]) if len(sys.argv) > 1 else 7460
DATA_DIR = r'd:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))[:N_FILES]
print(f'处理 {len(files)} 个文件')

def new():
    return {'n':0,'pos':0,'neg':0}

# 按 CD × 甲乙己 拆分
stats = {}   # cd -> {'gyj':new(), 'oth':new(), 'gyj_by_ef':{}}
CDS = ['中','下','忑']
DXEF_ORDER = ['金','银','唏','嘘','尿','屎']
AB_GOOD = ('a','b','r')

for fname in files:
    with open(fname,'rb') as f:
        f.readline()
        prev=None
        for raw in f:
            row = raw.decode('gbk').strip().split(',')
            if len(row)<51: continue
            cd,ab = row[8], row[9]
            try: zc=int(row[14])
            except: zc=0
            try: ze=int(row[15])
            except: ze=0
            ef=row[50][1] if len(row[50])>1 else '?'
            if prev is not None:
                p_cd,p_ab,p_zc,p_ze,p_ef = prev
                if p_zc <= 0 and p_cd in CDS:
                    if p_cd not in stats:
                        stats[p_cd] = {'gyj':new(),'oth':new(),'gyj_by_ef':{}}
                    is_gyj = p_ab.startswith(AB_GOOD)
                    pos = 1 if zc>0 else 0
                    neg = 1 if zc<=0 else 0
                    d = stats[p_cd]
                    key = 'gyj' if is_gyj else 'oth'
                    d[key]['n']+=1; d[key]['pos']+=pos; d[key]['neg']+=neg
                    if is_gyj:
                        if p_ef not in d['gyj_by_ef']:
                            d['gyj_by_ef'][p_ef]=new()
                        d['gyj_by_ef'][p_ef]['n']+=1
                        d['gyj_by_ef'][p_ef]['pos']+=pos
                        d['gyj_by_ef'][p_ef]['neg']+=neg
            prev=(cd,ab,zc,ze,ef)

print('\n=== 按 DXCD 拆分：DXZC<0 各 CD × AB 的次日转正率 ===')
def show(name,s):
    if s['n']>0:
        print(f'  {name}: n={s["n"]}, 次日转ZC>0={s["pos"]/s["n"]*100:.2f}%, 仍ZC<=0={s["neg"]/s["n"]*100:.2f}%')
    else:
        print(f'  {name}: n=0')

for cd in CDS:
    if cd in stats:
        d=stats[cd]
        print(f'\n--- DXZC<0 + DXCD={cd} ---')
        show('AB甲乙己', d['gyj'])
        show('AB非甲乙己', d['oth'])
        print(f'  甲乙己 按DXEF转正率:')
        for ef in DXEF_ORDER:
            if ef in d['gyj_by_ef']:
                show(ef, d['gyj_by_ef'][ef])
out.close()
