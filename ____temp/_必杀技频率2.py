# -*- coding: utf-8 -*-
import glob, pandas as pd, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
files = sorted(glob.glob('昭明算展/谕组周/谕组周_*.csv'))
n_stocks = len(files)
print(f'股票数: {n_stocks}')
# 读一个文件看年份范围
df0 = pd.read_csv(files[0], encoding='gbk')
df0['年'] = df0['主期'].astype(str).str[:4]
years = df0['年'].unique()
print(f'年份范围: {years.min()} ~ {years.max()}  年数: {len(years)}')
print(f'总周数(单股): {len(df0)}')
