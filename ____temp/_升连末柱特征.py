# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))
dfs=[]
for i,f in enumerate(files):
    try:
        df = pd.read_csv(f, encoding='gbk')
        if len(df)>=2:
            df['fid']=i
            dfs.append(df)
    except: pass
wk = pd.concat(dfs, ignore_index=True)
wk['下周涨'] = wk.groupby('fid')['周涨'].shift(-1)
wk['下周HR'] = wk.groupby('fid')['HR'].shift(-1)
wk['下周柱排'] = wk.groupby('fid')['柱排周'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周柱排'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()

# 升连链最后一柱: 当前是升连, 下周不是升连(链结束)
# 且下周未冲高(下周HR<3) 或 下周阴柱(下周涨<0)
sub = wk[(wk['柱型']=='升连') & (wk['下周柱型']!='升连')]
print(f'升连链末柱(下周非升连) 样本: {len(sub):,}')
print()

# ① 升连末柱 下周表现
print('=== ① 升连末柱 下周表现 ===')
print(f'  下周涨>0: {(sub["下周涨"]>0).mean()*100:.1f}%')
print(f'  下周HR>=3%: {(sub["下周HR"]>=3).mean()*100:.1f}%')
print(f'  下周阴柱: {(sub["下周涨"]<0).mean()*100:.1f}%')
print()

# ② 升连末柱 特征: 上影线/巨柱/十字星
# 上影线: 用上符串周 或 柱排周 判断
# 巨柱: 周涨大
# 十字星: 周涨接近0
wk['周涨'] = pd.to_numeric(wk['周涨'], errors='coerce')
sub2 = sub.copy()
sub2['周涨'] = pd.to_numeric(sub2['周涨'], errors='coerce')
print('=== ② 升连末柱 特征 ===')
# 巨柱: 周涨>=5%
print(f'  巨柱(周涨>=5%): {(sub2["周涨"]>=5).mean()*100:.1f}%')
print(f'  中柱(周涨2-5%): {((sub2["周涨"]>=2)&(sub2["周涨"]<5)).mean()*100:.1f}%')
print(f'  小柱(周涨<2%): {(sub2["周涨"]<2).mean()*100:.1f}%')
# 十字星: 周涨接近0(|周涨|<0.5%)
print(f'  十字星(|周涨|<0.5%): {(sub2["周涨"].abs()<0.5).mean()*100:.1f}%')
print()

# ③ 升连末柱 下周阴柱 vs 下周阳柱 的末柱特征对比
print('=== ③ 升连末柱 下周阴柱 vs 阳柱 特征对比 ===')
sub_yin = sub2[sub2['下周涨']<0]
sub_yang = sub2[sub2['下周涨']>0]
print(f'  下周阴柱: n={len(sub_yin):,}  末柱巨柱(>=5%): {(sub_yin["周涨"]>=5).mean()*100:.1f}%  十字星: {(sub_yin["周涨"].abs()<0.5).mean()*100:.1f}%')
print(f'  下周阳柱: n={len(sub_yang):,}  末柱巨柱(>=5%): {(sub_yang["周涨"]>=5).mean()*100:.1f}%  十字星: {(sub_yang["周涨"].abs()<0.5).mean()*100:.1f}%')
