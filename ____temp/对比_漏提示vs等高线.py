# -*- coding: utf-8 -*-
"""漏提示(首防诱/上持) vs 等高线基座+连阳 完整对比"""
import pandas as pd, numpy as np, os, glob, time, warnings
warnings.filterwarnings('ignore')
BASE = r'昭明算展/算展0724'
files = sorted(glob.glob(os.path.join(BASE, '算展.*.xlsx')))[:5]
# 列索引（已在算展文件中定位）
COL_漏=85; COL_护型=86; COL_柱排=91; COL_中符=96; COL_ZA=109; COL_阳连=110; COL_HR=111; COL_ZC=265; COL_ZE=270

def 等高线(za, mid):
    if pd.isna(za) or za=='': return 'NA'
    za=float(za); mid=str(mid) if pd.notna(mid) else ''
    lc=mid[-1] if len(mid)>0 else ''
    ab=lc in'AB'; cdef=lc in'CDEF'
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

frames=[]; t0=time.time()
for fi,f in enumerate(files):
    try:
        df = pd.read_excel(f, sheet_name=0, usecols=[COL_漏,COL_护型,COL_柱排,COL_中符,COL_ZA,COL_阳连,COL_HR,COL_ZC,COL_ZE])
        df.columns = ['漏提示','护型','柱排','中符','ZA','阳连','HR','ZC','ZE']
        df['等高线']=df.apply(lambda r:等高线(r['ZA'],r['中符']),axis=1)
        df['柱排类']=df['柱排'].fillna('').str[0].apply(lambda x:'升'if x=='升'else('跌'if x=='跌'else'人'))
        df['护型强']=df['护型'].fillna('').str[1:2].apply(lambda x:'强'if x in'甲乙己'else('弱'if x in'丙丁戊'else'其他'))
        df['门开']=(df['ZC']>0)&(df['ZE']>0)
        df['连阳']=df['阳连']>=3
        # 漏提示子类
        df['漏串']=df['漏提示'].astype(str)
        df['首防诱']=df['漏串'].str.contains('首防诱',na=False)
        df['上持']=df['漏串'].str.contains('上持',na=False)
        df['首上']=df['首防诱']|df['上持']
        frames.append(df)
    except Exception as e: print(f'  {f}: {e}')
    if(fi+1)%2==0: print(f'  {fi+1}/{len(files)} ({time.time()-t0:.0f}s)',flush=True)
data=pd.concat(frames,ignore_index=True)
data['HR']=pd.to_numeric(data['HR'],errors='coerce')
print(f'\n总行: {len(data):,} ({time.time()-t0:.0f}s)')

# 门开后
gate=data[data['门开']].copy()
print(f'门开后: {len(gate):,} 行')

# 对比
print('\n' + '='*70)
print('等权对比（门开后）')
print('='*70)
def show(label, sub):
    if len(sub)<30: return
    hr=sub['HR'].dropna()
    print(f'  {label:>24}: n={len(sub):>6,} P(HR>2)={(hr>2).mean():6.1%} P(HR>3)={(hr>3).mean():6.1%} 均HR={hr.mean():.2f}%')

print('\n--- 漏提示子类（有周级门）---')
show('全部首防诱+上持', gate[gate['首上']])
show('  首防诱', gate[gate['首防诱']])
show('  上持', gate[gate['上持']])

print('\n--- 等高线基座+连阳（无周级门）---')
show('等3_升_强+连阳', gate[(gate['等高线']=='等3')&(gate['柱排类']=='升')&(gate['护型强']=='强')&(gate['连阳'])])
show('等3_升_强', gate[(gate['等高线']=='等3')&(gate['柱排类']=='升')&(gate['护型强']=='强')])
show('全局基线', gate)

print('\n--- 叠加：有周级门 + 等高线基座+连阳 ---')
show('首上+等3升强', gate[gate['首上']&(gate['等高线']=='等3')&(gate['柱排类']=='升')&(gate['护型强']=='强')])
show('首上+等3升强+连阳', gate[gate['首上']&(gate['等高线']=='等3')&(gate['柱排类']=='升')&(gate['护型强']=='强')&(gate['连阳'])])

# 组内净提升对比
print('\n' + '='*70)
print('组内净提升（在等高线×柱排×护型基座内）')
print('='*70)
gate['基座']=gate['等高线']+'_'+gate['柱排类']+'_'+gate['护型强']
for 名,mask in [('首防诱+上持',gate['首上']),('等高线+连阳',gate['连阳'])]:
    s=0;n=0;groups=0;pos=0
    for key,g in gate.groupby('基座'):
        if key.startswith('等0') or key.startswith('零'):continue
        gs=g[mask.loc[g.index]]; gb=g[~mask.loc[g.index]]
        if len(gs)<30 or len(gb)<30:continue
        s+=((gs['HR'].dropna()>2).mean()-(gb['HR'].dropna()>2).mean())*len(gs)
        n+=len(gs);groups+=1
        if(gs['HR'].dropna()>2).mean()>(gb['HR'].dropna()>2).mean():pos+=1
    if n>=100:
        print(f'  {名}: 净提升P2={s/n:+.1%} 一致率={pos/groups:.0%} 覆盖{groups}组 n={n:,}')
print(f'\n耗时 {time.time()-t0:.0f}s')