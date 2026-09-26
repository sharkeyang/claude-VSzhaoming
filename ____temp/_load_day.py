import glob, pandas as pd, numpy as np, os, sys
sys.stdout.reconfigure(encoding='utf-8')
files = glob.glob('昭明算展/谕组日0926/*.csv')
print('文件数:', len(files))
chunks = []
for i, f in enumerate(files):
    df = pd.read_csv(f, encoding='gbk', dtype=str)
    # col0=日期, col5=涨幅PR, col6=高幅HR, col8=DXCD, col9=DXAB, col13=日ZA, col14=日ZC, col15=日ZE, col26=次日高幅
    df = df.iloc[:, [0,5,6,8,9,13,14,15,26]]
    df.columns = ['日期','PR','HR','DXCD','DXAB','ZA','ZC','ZE','次日高幅']
    fid = os.path.basename(f).replace('.csv','').replace('谕组日_','')
    df['fid'] = fid
    chunks.append(df)
    if (i+1)%1000==0: print('已加载', i+1)
df = pd.concat(chunks, ignore_index=True)
print('总行数:', len(df))
for c in ['PR','HR','ZA','ZC','ZE','次日高幅']:
    df[c] = pd.to_numeric(df[c], errors='coerce')
df['日期'] = pd.to_datetime(df['日期'])
df = df.sort_values(['fid','日期']).reset_index(drop=True)
for n in [1,3,5,10,20]:
    df[f'ret{n}'] = df.groupby('fid')['PR'].transform(lambda x: (1+x/100).rolling(n).apply(np.prod, raw=True).shift(-n) - 1) * 100
df['次日P3'] = (df['次日高幅']>=3).astype(int)
# 未来N日是否回到DXCD=上
for n in [1,3,5,10,20]:
    df[f'to_up{n}'] = df.groupby('fid')['DXCD'].transform(lambda x: (x.shift(-n)=='上').astype(int))
# 未来N日DXCD
df['次日DXCD'] = df.groupby('fid')['DXCD'].shift(-1)
df.to_parquet('____temp/_day_data.parquet')
print('已保存, shape:', df.shape)
print('基线P3:', df['次日P3'].mean()*100)
