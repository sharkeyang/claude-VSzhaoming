# -*- coding: utf-8 -*-
"""验证位谕of日层漏提示的日级条件是否有预测力"""
import warnings;warnings.filterwarnings('ignore')
import pandas as pd,numpy as np,os,glob,random,time
DATA_DIR='昭明算展/谕组日'
COL_ZA='日ZA';COL_ZC='日ZC';COL_ZE='日ZE'
COL_MID='中符串';COL_NEXT='次日高幅';COL_涨幅='涨幅'
COL_柱排='柱排';COL_护型='DXAB';COL_柱型='柱型';COL_鼎='BT鼎'
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
        df['护型']=df[COL_护型].fillna('').str[1]
        df['护型强']=df['护型'].apply(lambda x:'强'if x in'甲乙己'else('弱'if x in'丙丁戊'else'其他'))
        df['门开']=(df[COL_ZC]>0)&(df[COL_ZE]>0)
        # 漏提示的日级条件
        df['BTZA']=df[COL_ZA]
        df['今涨']=df[COL_涨幅]
        df['BT鼎']=df[COL_鼎].fillna(0)
        # 上漏: 护型强 + BTZA>1 + 今涨<=0
        df['c_上漏']=(df['护型强']=='强')&(df['BTZA']>1)&(df['今涨']<=0)
        # 上持: 护型强 + BTZA>1 + 今涨>0
        df['c_上持']=(df['护型强']=='强')&(df['BTZA']>1)&(df['今涨']>0)
        # 被: 丁/戊
        df['c_被']=df['护型'].isin(['丁','戊'])
        # 丙漏
        df['c_丙漏']=df['护型']=='丙'
        # 鼎信号
        df['c_鼎']=df['BT鼎']==1
        # 柱型含梯/栏/栅/枝
        df['c_特柱']=df[COL_柱型].fillna('').str.contains('梯|栏|栅|枝',na=False)
        # e漏: 护型强 + BTZA<0
        df['c_e漏']=(df['护型强']=='强')&(df['BTZA']<0)
        # 首防诱: 护型强 + BTZA<=1
        df['c_首防诱']=(df['护型强']=='强')&(df['BTZA']<=1)
        # 完整漏信号: 上漏+鼎+特柱 ≈ 漏提示完整信号
        df['c_完整漏']=df['c_上漏']&df['c_鼎']
        frames.append(df[['等高线','柱排','护型强','门开',COL_NEXT,
                          'c_上漏','c_上持','c_被','c_丙漏','c_鼎','c_特柱',
                          'c_e漏','c_首防诱','c_完整漏']])
    except:pass
    if(fi+1)%100==0:print(f'  {fi+1}/500 ({time.time()-t0:.0f}s)',flush=True)
data=pd.concat(frames,ignore_index=True)
data=data[data['等高线'].isin(['等1','等2','等3','等4','等5','等6','等7','等8','零轴'])]
gate=data[data['门开']&data[COL_NEXT].notna()].copy()
base_p2=(gate[COL_NEXT]>2).mean();base_p3=(gate[COL_NEXT]>3).mean()
print(f'\n核心池门后: {len(gate):,} 行')
print(f'全局基线: P(>=2%)={base_p2:.1%}  P(>=3%)={base_p3:.1%}')
# 测试每个条件
conds=[
    ('c_上漏','上漏(强+BTZA>1+阴柱)'),
    ('c_上持','上持(强+BTZA>1+阳柱)'),
    ('c_被','被(丁戊)'),
    ('c_丙漏','丙漏(丙)'),
    ('c_鼎','鼎信号'),
    ('c_特柱','特柱(梯/栏/栅/枝)'),
    ('c_e漏','e漏(强+BTZA<0)'),
    ('c_首防诱','首防诱(强+BTZA<=1)'),
    ('c_完整漏','完整漏(上漏+鼎)'),
]
print(f'\n{"条件":>20} | {"样本":>8} | {"P(>=2%)":>8} | {"P(>=3%)":>8} | {"提升P2":>8} | {"提升P3":>8}')
print('-'*70)
for col,lab in conds:
    s=gate[gate[col]]
    if len(s)<50:continue
    nh=s[COL_NEXT].dropna()
    p2=(nh>2).mean();p3=(nh>3).mean()
    print(f'{lab:>20} | {len(s):>8,} | {p2:>7.1%} | {p3:>7.1%} | {p2-base_p2:>+7.1%} | {p3-base_p3:>+7.1%}')
# 组内净提升（在等高线×柱排×护型基座内）
print(f'\n=== 组内加权净提升（方法同赛马）===')
gate['基座']=gate['等高线']+'_'+gate['柱排']+'_'+gate['护型强']
for col,lab in conds:
    s=0;n=0;groups=0;pos=0
    for key,g in gate.groupby('基座'):
        gs=g[g[col]];gb=g[~g[col]]
        if len(gs)<30 or len(gb)<30:continue
        s+=((gs[COL_NEXT]>2).mean()-(gb[COL_NEXT]>2).mean())*len(gs)
        n+=len(gs);groups+=1
        if(gs[COL_NEXT]>2).mean()>(gb[COL_NEXT]>2).mean():pos+=1
    net=s/n if n else 0;rate=pos/groups if groups else 0
    if n>=100:
        print(f'{lab:>20}: 净提升P2={net:+.1%} 一致率={rate:.0%} 覆盖{groups}组 n={n:,}')
print(f'\n耗时 {time.time()-t0:.0f}s')