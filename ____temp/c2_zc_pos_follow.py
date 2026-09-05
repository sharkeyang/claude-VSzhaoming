# -*- coding: utf-8 -*-
"""验证：DXZC<0 + DXAB=甲乙己 的后续归属（次日DXZC状态）
看是否"很快转为 DXZC>0"（印证空间小、收益有限的假说）。
用法: python c2_zc_pos_follow.py [文件数]
输出: ____temp/c2_zc_pos_follow_result.txt
"""
import io, sys, glob, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'c2_zc_pos_follow_result.txt')
out = io.open(OUT, 'w', encoding='utf-8')
sys.stdout = out

N_FILES = int(sys.argv[1]) if len(sys.argv) > 1 else 7460
DATA_DIR = r'd:\@VSwork\VS昭明计划VBA优化\昭明算展\谕组日'
files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))[:N_FILES]
print(f'处理 {len(files)} 个文件')

def new():
    return {'n':0, 'zc_pos_next':0, 'zc_neg_next':0}

# 分类：按 DXAB(甲乙己 vs 其他) × DXEF(金/其他)
stats = {
    'all': new(),
    'ab_gyj': new(),   # 甲乙己
    'ab_other': new(), # 非甲乙己
    'ab_gyj_by_ef': {}, # 甲乙己按DXEF
    'ab_gyj_ze_pos': new(), 'ab_gyj_ze_neg': new(),
}
DXEF_ORDER = ['金','银','唏','嘘','尿','屎']
AB_GOOD = ('a','b','r')  # 甲a 乙b 己r

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
                # 只看 DXZC<0 的样本，统计次日归属
                if p_zc <= 0:
                    is_gyj = p_ab.startswith(AB_GOOD)
                    next_pos = 1 if zc>0 else 0
                    next_neg = 1 if zc<=0 else 0
                    stats['all']['n']+=1
                    stats['all']['zc_pos_next']+=next_pos
                    stats['all']['zc_neg_next']+=next_neg
                    key='ab_gyj' if is_gyj else 'ab_other'
                    stats[key]['n']+=1
                    stats[key]['zc_pos_next']+=next_pos
                    stats[key]['zc_neg_next']+=next_neg
                    if is_gyj:
                        if p_ef not in stats['ab_gyj_by_ef']:
                            stats['ab_gyj_by_ef'][p_ef]=new()
                        stats['ab_gyj_by_ef'][p_ef]['n']+=1
                        stats['ab_gyj_by_ef'][p_ef]['zc_pos_next']+=next_pos
                        stats['ab_gyj_by_ef'][p_ef]['zc_neg_next']+=next_neg
                        if p_ze>0:
                            stats['ab_gyj_ze_pos']['n']+=1
                            stats['ab_gyj_ze_pos']['zc_pos_next']+=next_pos
                        else:
                            stats['ab_gyj_ze_neg']['n']+=1
                            stats['ab_gyj_ze_neg']['zc_pos_next']+=next_pos
            prev=(cd,ab,zc,ze,ef)

print('\n=== DXZC<0 各群体 次日转正率（次日变为 ZC>0）===')
def show(name,s):
    if s['n']>0:
        print(f'{name}: n={s["n"]}, 次日转ZC>0={s["zc_pos_next"]/s["n"]*100:.2f}%, 次日仍ZC<=0={s["zc_neg_next"]/s["n"]*100:.2f}%')
    else:
        print(f'{name}: n=0')
show('全部DXZC<0', stats['all'])
show('  +AB甲乙己', stats['ab_gyj'])
show('  +AB非甲乙己', stats['ab_other'])

print('\n--- 甲乙己 按 DXEF 分级 次日转正率 ---')
for ef in DXEF_ORDER:
    if ef in stats['ab_gyj_by_ef']:
        show(f'  {ef}', stats['ab_gyj_by_ef'][ef])
print('\n--- 甲乙己 按 DXZE ---')
show('  ZE>0', stats['ab_gyj_ze_pos'])
show('  ZE<=0', stats['ab_gyj_ze_neg'])
out.close()
