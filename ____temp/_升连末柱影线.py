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
wk['下周并符'] = wk.groupby('fid')['并符串周'].shift(-1)
wk['WXZC'] = pd.to_numeric(wk['ZC周'], errors='coerce')
def 柱型(bf):
    if not isinstance(bf,str) or bf=='': return '空'
    z=bf[-1]
    return {'O':'升吞','Q':'升连','o':'升孕','V':'跌吞','W':'跌连','v':'跌孕'}.get(z,'其他')
wk['柱型'] = wk['并符串周'].astype(str).apply(柱型)
wk['下周柱型'] = wk['下周并符'].astype(str).apply(柱型)
wk = wk[wk['WXZC']>0].copy()

末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))]
非末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型']=='升连')]

# 上符串周: 5字符, 每字符=某日上影状态(A=上影,B=长上影,_=无)
# 分析: 末位(最后一日)的上影状态
def 末位影(s):
    if not isinstance(s,str) or len(s)<1: return '空'
    return s[-1]
末柱['末位影'] = 末柱['上符串周'].astype(str).apply(末位影)
非末柱['末位影'] = 非末柱['上符串周'].astype(str).apply(末位影)

print('=== 升连末柱 vs 非末柱 末位影线(上符串周末位) ===')
print(f'{"末位影":<8}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
for v in ['A','B','_']:
    m = (末柱['末位影']==v).mean()*100
    n = (非末柱['末位影']==v).mean()*100
    name = {'A':'上影','B':'长上影','_':'无上影'}.get(v,v)
    print(f'{name:<8}{m:>9.1f}%{n:>9.1f}%{m-n:>+9.1f}pp')
print()

# 上符串周 是否含 B(长上影)
def 含长上影(s):
    return 'B' in str(s)
末柱['含长上影'] = 末柱['上符串周'].astype(str).apply(含长上影)
非末柱['含长上影'] = 非末柱['上符串周'].astype(str).apply(含长上影)
m = (末柱['含长上影']).mean()*100
n = (非末柱['含长上影']).mean()*100
print(f'含长上影(B): 末柱={m:.1f}%  非末柱={n:.1f}%  差异={m-n:+.1f}pp')
print()

# 十字星: 周涨接近0 且 有上下影
# 用周涨|绝对值|<0.5 近似十字星
末柱['周涨'] = pd.to_numeric(末柱['周涨'], errors='coerce')
非末柱['周涨'] = pd.to_numeric(非末柱['周涨'], errors='coerce')
m = (末柱['周涨'].abs()<0.5).mean()*100
n = (非末柱['周涨'].abs()<0.5).mean()*100
print(f'十字星(|周涨|<0.5%): 末柱={m:.1f}%  非末柱={n:.1f}%  差异={m-n:+.1f}pp')
