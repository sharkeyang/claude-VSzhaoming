# -*- coding: utf-8 -*-
"""计算保留条件叠加到日层等基座后的实际P(≥2%)"""
import pandas as pd, numpy as np, os, glob, random, warnings
warnings.filterwarnings('ignore')
DATA_DIR='昭明算展/谕组日'
COL_ZA='日ZA';COL_ZC='日ZC';COL_ZE='日ZE';COL_MID='中符串';COL_NEXT='次日高幅'
COL_柱排='柱排';COL_护型='DXAB';COL_涨幅='涨幅';COL_连阳='BT连阳';COL_顶型='顶型'
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
frames=[];import time;t=time.time()
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
        df['c_龙']=df[COL_顶型].fillna('').str.contains('龙',na=False)
        # 组合条件（按优先级）
        df['c_连阳I1']=df['c_连阳']&df['c_I1']
        df['c_连阳O1']=df['c_连阳']&df['c_O1']
        frames.append(df[['等高线','柱排','护型','门开',COL_NEXT,'c_I1','c_O1','c_连阳','c_龙','c_连阳I1','c_连阳O1']])
    except Exception as e:print('err',f,e)
    if(fi+1)%100==0:print(f'  {fi+1}/500 ({time.time()-t:.0f}s)',flush=True)
data=pd.concat(frames,ignore_index=True)
data=data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8','零轴'])]
gate=data[data['门开']&data[COL_NEXT].notna()].copy()
base_p2=(gate[COL_NEXT]>2).mean();base_p3=(gate[COL_NEXT]>3).mean()
print(f'\n核心池门后: {len(gate):,} 行')
print(f'全局基线: P(≥2%)={base_p2:.1%}  P(≥3%)={base_p3:.1%}')
# 仅日层等基座（不加条件）
print('\n=== 日层等基座（仅等高线8类，门后核心池）===')
print(f'{"分类":>8} | {"样本":>8} | {"P(≥2%)":>8} | {"P(≥3%)":>8} | {"均冲高":>8}')
for c in ['等1','等2','等3','等4','等5','等6','等7','等8']:
    s=gate[gate['等高线']==c];nh=s[COL_NEXT].dropna()
    if len(nh)<200:continue
    print(f'{c:>8} | {len(s):>8,} | {(nh>2).mean():>7.1%} | {(nh>3).mean():>7.1%} | {nh.mean():>6.2f}%')
# 条件叠加
print('\n=== 条件叠加到日层等基座 ===')
print(f'{"条件组合":>24} | {"样本":>8} | {"P(≥2%)":>8} | {"P(≥3%)":>8} | {"提升P2":>8} | {"提升P3":>8}')
conds=[
    ('c_连阳','连阳≥3'),('c_I1','I1穿越'),('c_O1','O1穿越'),
    ('c_龙','顶型龙'),('c_连阳I1','连阳+I1'),('c_连阳O1','连阳+O1'),
    ('c_连阳','连阳≥3'),('c_I1','I1穿越'),('c_O1','O1穿越'),
]
# 单条件
for col,lab in [('c_连阳','连阳≥3'),('c_I1','I1穿越'),('c_O1','O1穿越'),('c_龙','顶型龙'),
                 ('c_连阳I1','连阳+I1'),('c_连阳O1','连阳+O1')]:
    s=gate[gate[col]]
    if len(s)<50:continue
    nh=s[COL_NEXT].dropna()
    p2=(nh>2).mean();p3=(nh>3).mean()
    print(f'{lab:>24} | {len(s):>8,} | {p2:>7.1%} | {p3:>7.1%} | {p2-base_p2:>+7.1%} | {p3-base_p3:>+7.1%}')
# 日层等×柱排×护型×条件叠加（最佳组合）
print('\n=== 日层等×柱排×护型 + 条件叠加（最佳组合TOP10）===')
# 先算基座组合
gate['基座']=gate['等高线']+'_'+gate['柱排']+'_'+gate['护型']
print(f'{"基座+条件":>30} | {"样本":>8} | {"P(≥2%)":>8} | {"P(≥3%)":>8} | {"均冲高":>8}')
rows=[]
for key, sub in gate.groupby('基座'):
    if len(sub)<500:continue
    nh=sub[COL_NEXT].dropna();base_p2_g=(nh>2).mean();base_p3_g=(nh>3).mean()
    # 加各条件
    for col,lab in [('c_连阳','+连阳'),('c_I1','+I1'),('c_O1','+O1'),('c_龙','+龙'),
                     ('c_连阳I1','+连阳I1')]:
        s=sub[sub[col]]
        if len(s)<30:continue
        nh2=s[COL_NEXT].dropna()
        p2=(nh2>2).mean();p3=(nh2>3).mean()
        rows.append((f'{key}{lab}',len(s),p2,p3,nh2.mean(),p2-base_p2_g))
for r in sorted(rows,key=lambda x:-x[2])[:10]:
    print(f'{r[0]:>30} | {r[1]:>8,} | {r[2]:>7.1%} | {r[3]:>7.1%} | {r[4]:>6.2f}%')
# 对比：仅日层等 vs 日层等+条件
best_仅基座=gate.groupby('基座')[COL_NEXT].apply(lambda x:(x>2).mean()).max()
best_叠加=max(r[2] for r in rows) if rows else 0
print(f'\n=== 对比 ===')
print(f'仅日层等基座最佳: {best_仅基座:.1%}')
print(f'日层等+条件叠加最佳: {best_叠加:.1%}')
print(f'提升: {best_叠加-best_仅基座:.1%}')
print(f'\n耗时 {time.time()-t:.0f}s')
