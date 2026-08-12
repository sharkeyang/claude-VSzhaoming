# -*- coding: utf-8 -*-
"""计算保留条件叠加到日层等基座后的实际P(>=2%)，并对比现有策略"""
import pandas as pd, numpy as np, os, glob, random, time, warnings
warnings.filterwarnings('ignore')
DATA_DIR='昭明算展/谕组日'
COL_ZA='日ZA';COL_ZC='日ZC';COL_ZE='日ZE';COL_MID='中符串';COL_NEXT='次日高幅'
COL_柱排='柱排';COL_护型='DXAB';COL_涨幅='涨幅';COL_连阳='BT连阳';COL_顶型='顶型'
市板映射=pd.read_csv('____temp/市板映射.csv',encoding='utf-8')
市板映射['CIDL']=市板映射['CIDL'].astype(str).str.strip()
市板dict=dict(zip(市板映射['CIDL'],市板映射['市板']))
核心={'Qic','Qim','Qit','Qin'}
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
random.seed(42);random.shuffle(files);files=files[:500]
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
        df['前日ZA']=df[COL_ZA].shift(1)
        df['门开']=(df[COL_ZC]>0)&(df[COL_ZE]>0)
        df['c_I1']=(df['前日ZA']<0)&(df[COL_ZA]>=0)&((df[COL_ZA]-df['前日ZA'])>=3)&(df[COL_涨幅]>=2)
        df['c_O1']=(df['前日ZA']>0)&(df[COL_ZA]<=0)&((df[COL_ZA]-df['前日ZA'])<=-3)&(df[COL_涨幅]<=-2)
        df['c_连阳']=df[COL_连阳]>=3
        df['c_龙']=df[COL_顶型].fillna('').str.contains('龙',na=False)
        df['c_连阳I1']=df['c_连阳']&df['c_I1']
        df['c_连阳龙']=df['c_连阳']&df['c_龙']
        df['c_连阳I1龙']=df['c_连阳']&df['c_I1']&df['c_龙']
        frames.append(df[['等高线','柱排','护型','门开',COL_NEXT,'c_I1','c_O1','c_连阳','c_龙','c_连阳I1','c_连阳龙','c_连阳I1龙']])
    except:pass
    if(fi+1)%100==0:print(f'  {fi+1}/500 ({time.time()-t0:.0f}s)',flush=True)
data=pd.concat(frames,ignore_index=True)
data=data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8','零轴'])]
gate=data[data['门开']&data[COL_NEXT].notna()].copy()
base_p2=(gate[COL_NEXT]>2).mean();base_p3=(gate[COL_NEXT]>3).mean()
print(f'核心池门后: {len(gate):,} 行')
print(f'全局基线: P(>=2%)={base_p2:.1%}  P(>=3%)={base_p3:.1%}')
# 日层等×柱排×护型 基座最佳（n>=500）
gate['基座']=gate['等高线']+'_'+gate['柱排']+'_'+gate['护型']
grp_best=[]
for k,g in gate.groupby('基座'):
    if len(g)<500:continue
    nh=g[COL_NEXT].dropna()
    grp_best.append((k,len(g),(nh>2).mean(),(nh>3).mean(),nh.mean()))
grp_best.sort(key=lambda x:-x[2])
print(f'\n日层等×柱排×护型基座最佳（n>=500）:')
for r in grp_best[:5]:
    print(f'  {r[0]}: P(>=2%)={r[2]:.1%} P(>=3%)={r[3]:.1%} n={r[1]:,} 均冲高={r[4]:.2f}%')
# 日层等×柱排×护型 + 条件叠加
rows=[]
for k,sub in gate.groupby('基座'):
    if len(sub)<500:continue
    nh=sub[COL_NEXT].dropna();bp2=(nh>2).mean();bp3=(nh>3).mean()
    for col,lab in [('c_连阳','+连阳'),('c_I1','+I1'),('c_O1','+O1'),('c_龙','+龙'),
                     ('c_连阳I1','+连阳I1'),('c_连阳龙','+连阳龙'),('c_连阳I1龙','+连阳I1龙')]:
        s=sub[sub[col]]
        if len(s)<30:continue
        nh2=s[COL_NEXT].dropna()
        rows.append((k+lab,len(s),(nh2>2).mean(),(nh2>3).mean(),nh2.mean(),(nh2>2).mean()-bp2))
# 大样本组合（n>=500）
rows500=[r for r in rows if r[1]>=500]
print(f'\n日层等+条件叠加 最佳大样本组合（n>=500）:')
for r in sorted(rows500,key=lambda x:-x[2])[:5]:
    print(f'  {r[0]}: P(>=2%)={r[2]:.1%} P(>=3%)={r[3]:.1%} n={r[1]:,} 均冲高={r[4]:.2f}%')
# 最佳任意组合（n>=30）
print(f'\n日层等+条件叠加 最佳任意组合（n>=30）:')
for r in sorted(rows,key=lambda x:-x[2])[:10]:
    print(f'  {r[0]}: P(>=2%)={r[2]:.1%} P(>=3%)={r[3]:.1%} n={r[1]:,} 均冲高={r[4]:.2f}%')
# 对比
print(f'\n=== 当前日冲策略 vs 新架构（核心池门后） ===')
print(f'{"策略描述":>28} | {"P(>=2%)":>8} | {"P(>=3%)":>8} | {"样本":>8}')
print(f'{"全局基线(无条件)":>28} | {base_p2:>7.1%} | {base_p3:>7.1%} | {len(gate):>8,}')
i1=gate[gate['c_I1']]
print(f'{"日冲22 I1态(当前最佳)":>28} | {(i1[COL_NEXT].dropna()>2).mean():>7.1%} | {(i1[COL_NEXT].dropna()>3).mean():>7.1%} | {len(i1):>8,}')
for r in sorted(rows,key=lambda x:-x[2])[:3]:
    print(f'{"新架构 "+r[0]:>28} | {r[2]:>7.1%} | {r[3]:>7.1%} | {r[1]:>8,}')
print(f'\n耗时 {time.time()-t0:.0f}s')