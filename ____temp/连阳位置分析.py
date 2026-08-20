# -*- coding: utf-8 -*-
"""连阳位置分析：第一个连阳 vs 后续连阳，下日冲高概率"""
import warnings;warnings.filterwarnings('ignore')
import pandas as pd,numpy as np,os,glob,random,time
DATA_DIR='昭明算展/谕组日'
COL_ZA='日ZA';COL_ZC='日ZC';COL_ZE='日ZE';COL_MID='中符串';COL_NEXT='次日高幅'
COL_柱排='柱排';COL_护型='DXAB';COL_连阳='BT连阳'
市板映射=pd.read_csv('____temp/市板映射.csv',encoding='utf-8')
市板映射['CIDL']=市板映射['CIDL'].astype(str).str.strip()
市板dict=dict(zip(市板映射['CIDL'],市板映射['市板']))
核心={'Qic','Qim','Qit'}  # 高波池（已剔除Qin）
def dg(za,mid):
    if pd.isna(za)or za=='':return'NA'
    za=float(za);mid=str(mid)if pd.notna(mid)else'';lc=mid[-1]if len(mid)>0 else''
    ab=lc in'AB';cdef=lc in'CDEF'
    if za>0:
        if za==1:return'等1'
        elif za>=2 and ab:return'等3'
        elif za>=2 and cdef and za<=3:return'等2'
        elif za>3 and cdef:return'等4'
        else:return'等0'
    elif za<0:
        if za==-1:return'等5'
        elif za>=-3 and ab:return'等6'
        elif za<=-2 and cdef:return'等7'
        elif za<-3 and ab:return'等8'
        else:return'等0'
    else:return'零轴'
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
random.seed(42);random.shuffle(files);files=files[:800]
frames=[];t0=time.time()
for fi,f in enumerate(files):
    cidl=os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if 市板dict.get(cidl) not in 核心:continue
    try:
        df=pd.read_csv(f,encoding='gbk')
        if COL_ZA not in df.columns or len(df)<55:continue
        df['等高线']=df.apply(lambda r:dg(r[COL_ZA],r[COL_MID]),axis=1)
        df['柱排']=df[COL_柱排].fillna('').str[0].apply(lambda x:'升'if x=='升'else('跌'if x=='跌'else'人'))
        df['护型']=df[COL_护型].fillna('').str[1].apply(lambda x:'强'if x in'甲乙己'else('弱'if x in'丙丁戊'else'其他'))
        df['门开']=(df[COL_ZC]>0)&(df[COL_ZE]>0)
        df['连阳']=df[COL_连阳]
        frames.append(df[['等高线','柱排','护型','门开',COL_NEXT,'连阳']])
    except:pass
    if(fi+1)%200==0:print(f'  {fi+1}/800 ({time.time()-t0:.0f}s)',flush=True)
data=pd.concat(frames,ignore_index=True)
data=data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8','零轴'])]
gate=data[data['门开']&data[COL_NEXT].notna()].copy()
base_p2=(gate[COL_NEXT]>2).mean()
print(f'\n核心池门后: {len(gate):,} 行, 基线P(>=2%)={base_p2:.1%}')

# 连阳值分布
print('\n=== 连阳位置（BT连阳值）下日冲高 ===')
print(f'{"连阳值":>6} | {"样本":>8} | {"P(>=2%)":>8} | {"P(>=3%)":>8} | {"均HR":>7} | {"相对基线":>8}')
for v in [1,2,3,4,5,6,7,8,9,10]:
    sub=gate[gate['连阳']==v]
    if len(sub)<50:continue
    nh=sub[COL_NEXT].dropna()
    print(f'{v:>6} | {len(sub):>8,} | {(nh>2).mean():>7.1%} | {(nh>3).mean():>7.1%} | {nh.mean():>6.2f}% | {(nh>2).mean()-base_p2:>+7.1%}')

# 连阳>=3 内，位置细分
print('\n=== 连阳>=3 内位置细分 ===')
print(f'{"连阳值":>6} | {"样本":>8} | {"P(>=2%)":>8} | {"P(>=3%)":>8} | {"均HR":>7}')
for v in [3,4,5,6,7,8]:
    sub=gate[gate['连阳']==v]
    if len(sub)<50:continue
    nh=sub[COL_NEXT].dropna()
    print(f'{v:>6} | {len(sub):>8,} | {(nh>2).mean():>7.1%} | {(nh>3).mean():>7.1%} | {nh.mean():>6.2f}%')

# 第一根 vs 后续
print('\n=== 关键：连阳第1根 vs 后续 ===')
# 连阳=1 表示今天正好是第1根阳线（刚转多）
first=gate[gate['连阳']==1]
later=gate[gate['连阳']>=2]
later3=gate[gate['连阳']>=3]
nh_f=first[COL_NEXT].dropna();nh_l=later[COL_NEXT].dropna();nh_l3=later3[COL_NEXT].dropna()
print(f'连阳第1根: n={len(first):,} P(>=2%)={(nh_f>2).mean():.1%}')
print(f'连阳>=2:  n={len(later):,} P(>=2%)={(nh_l>2).mean():.1%}')
print(f'连阳>=3:  n={len(later3):,} P(>=2%)={(nh_l3>2).mean():.1%}')

# 等高线基座内，连阳位置
print('\n=== 等高线基座(等3_升_强)内，连阳位置 ===')
base=gate[(gate['等高线']=='等3')&(gate['柱排']=='升')&(gate['护型']=='强')]
print(f'{"连阳值":>6} | {"样本":>8} | {"P(>=2%)":>8} | {"P(>=3%)":>8} | {"均HR":>7}')
for v in [1,2,3,4,5,6,7,8]:
    sub=base[base['连阳']==v]
    if len(sub)<20:continue
    nh=sub[COL_NEXT].dropna()
    print(f'{v:>6} | {len(sub):>8,} | {(nh>2).mean():>7.1%} | {(nh>3).mean():>7.1%} | {nh.mean():>6.2f}%')
print(f'等高线等3升强基线: n={len(base):,} P(>=2%)={(base[COL_NEXT].dropna()>2).mean():.1%}')

print(f'\n耗时 {time.time()-t0:.0f}s')