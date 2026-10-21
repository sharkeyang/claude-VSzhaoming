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

末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型'].isin(['跌孕','跌吞']))].copy()
非末柱 = wk[(wk['柱型']=='升连') & (wk['下周柱型']=='升连')].copy()

# 上符串周: A=触顶, B=触哼, w=触底, v=触哈, _=未触
# 取末位(本周最后一日)
def 触哼(s):
    if not isinstance(s,str) or len(s)<1: return '空'
    return s[-1]
末柱['触哼'] = 末柱['上符串周'].astype(str).apply(触哼)
非末柱['触哼'] = 非末柱['上符串周'].astype(str).apply(触哼)

print('=== 升连末柱 vs 非末柱 触哼状态(上符串周末位) ===')
print(f'{"触哼":<10}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
for v, name in [('A','触顶'),('B','触哼'),('w','触底'),('v','触哈'),('_','未触')]:
    m = (末柱['触哼']==v).mean()*100
    n = (非末柱['触哼']==v).mean()*100
    print(f'{name:<10}{m:>9.1f}%{n:>9.1f}%{m-n:>+9.1f}pp')
print()

# 宽符串周: X/4/3/2/K/I/s/o/_ (喇叭宽度)
def 宽符(s):
    if not isinstance(s,str) or len(s)<1: return '空'
    return s[-1]
末柱['宽符'] = 末柱['宽符串周'].astype(str).apply(宽符)
非末柱['宽符'] = 非末柱['宽符串周'].astype(str).apply(宽符)
print('=== 升连末柱 vs 非末柱 宽符(喇叭宽度末位) ===')
print(f'{"宽符":<10}{"末柱":>10}{"非末柱":>10}{"差异":>10}')
for v, name in [('X','>=50'),('4','>=40'),('3','>=30'),('2','>=20'),('K','>=15'),('I','>=10'),('s','>=5'),('o','>=0'),('_','负')]:
    m = (末柱['宽符']==v).mean()*100
    n = (非末柱['宽符']==v).mean()*100
    if m>0.5 or n>0.5:
        print(f'{name:<10}{m:>9.1f}%{n:>9.1f}%{m-n:>+9.1f}pp')
