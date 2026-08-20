# -*- coding: utf-8 -*-
"""复核 Agent B 的矛盾点：O1穿越 和 连阳≥3 在 P(≥2%) 口径下的真实提升"""
import pandas as pd, numpy as np, os, glob, random, warnings
warnings.filterwarnings('ignore')
DATA_DIR='昭明算展/谕组日'
COL_ZA='日ZA';COL_ZC='日ZC';COL_ZE='日ZE';COL_MID='中符串';COL_NEXT='次日高幅'
COL_柱排='柱排';COL_护型='DXAB';COL_涨幅='涨幅';COL_连阳='BT连阳'
市板映射=pd.read_csv('____temp/市板映射.csv',encoding='utf-8');市板映射['CIDL']=市板映射['CIDL'].astype(str).str.strip()
市板dict=dict(zip(市板映射['CIDL'],市板映射['市板']));核心={'Qic','Qim','Qit'}  # 高波池（已剔除Qin）
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
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')));random.seed(42);random.shuffle(files);files=files[:500]
frames=[];t=time.time() if False else 0
import time;t=time.time()
for fi,f in enumerate(files):
    cidl=os.path.basename(f).replace('谕组日_','').replace('.csv','')
    if 市板dict.get(cidl) not in 核心:continue
    try:
        df=pd.read_csv(f,encoding='gbk')
        if COL_ZA not in df.columns or len(df)<55:continue
        df['等高线']=df.apply(lambda r:dg(r[COL_ZA],r[COL_MID]),axis=1)
        df['柱排']=df[COL_柱排].fillna('').str[0].apply(lambda x:'升'if x=='升'else('跌'if x=='跌'else'人'))
        df['护型']=df[COL_护型].fillna('').str[1].apply(lambda x:'强'if x in'甲乙己'else('弱'if x in'丙丁戊'else'其他'))
        df['前日ZA']=df[COL_ZA].shift(1)
        df['门开']=(df[COL_ZC]>0)&(df[COL_ZE]>0)
        df['c_I1']=(df['前日ZA']<0)&(df[COL_ZA]>=0)&((df[COL_ZA]-df['前日ZA'])>=3)&(df[COL_涨幅]>=2)
        df['c_O1']=(df['前日ZA']>0)&(df[COL_ZA]<=0)&((df[COL_ZA]-df['前日ZA'])<=-3)&(df[COL_涨幅]<=-2)
        df['c_连阳']=df[COL_连阳]>=3
        frames.append(df[['等高线','柱排','护型','门开',COL_NEXT,'c_I1','c_O1','c_连阳']])
    except Exception as e:print('err',f,e)
    if(fi+1)%100==0:print(f'  {fi+1}/500 ({time.time()-t:.0f}s)',flush=True)
data=pd.concat(frames,ignore_index=True)
data=data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8','零轴'])]
gate=data[data['门开']&data[COL_NEXT].notna()].copy()
print(f'门后核心池: {len(gate):,} 行')
base_p2=(gate[COL_NEXT]>2).mean();base_p3=(gate[COL_NEXT]>3).mean()
print(f'全局基线 P(≥2%)={base_p2:.1%} P(≥3%)={base_p3:.1%}')
for 名,col in [('O1穿越','c_O1'),('连阳≥3','c_连阳'),('I1穿越','c_I1')]:
    sub=gate[gate[col]]
    p2=(sub[COL_NEXT]>2).mean();p3=(sub[COL_NEXT]>3).mean()
    # 组内加权净提升
    s=0;n=0;groups=0;pos=0
    for key,g in gate.groupby(['等高线','柱排','护型']):
        gs=g[g[col]];gb=g[~g[col]]
        if len(gs)<30 or len(gb)<30:continue
        s+=( (gs[COL_NEXT]>2).mean() - (gb[COL_NEXT]>2).mean() )*len(gs);n+=len(gs);groups+=1
        if (gs[COL_NEXT]>2).mean()>(gb[COL_NEXT]>2).mean():pos+=1
    net=s/n if n else 0;rate=pos/groups if groups else 0
    print(f'\n{名}: n={len(sub):,} 全局P2={p2:.1%}(+{p2-base_p2:.1%}) 全局P3={p3:.1%}(+{p3-base_p3:.1%})')
    print(f'  组内净提升P2={net:+.1%} 一致率={rate:.0%} 覆盖{n}组={groups}')
print(f'\n耗时 {time.time()-t:.0f}s')
