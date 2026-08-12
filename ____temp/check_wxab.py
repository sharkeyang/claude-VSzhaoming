# -*- coding: utf-8 -*-
import pandas as pd, os, glob

# 找第一个文件
files = glob.glob('D:\\@VSwork\\VS昭明计划VBA优化\\昭明算展\\谕组周\\谕组周_*.csv')
print(f'文件数: {len(files)}')
if files:
    df = pd.read_csv(files[0], encoding='gbk')
    wx = df['WXAB'].dropna()
    print('WXAB样例:')
    for v in wx.iloc[:10]:
        print(f'  repr={repr(str(v))}')
    print('\n护型提取:')
    def q(s):
        if len(s)>=2 and s[0] in 'az': return s[1]
        return '?'
    for v in wx.iloc[:10]:
        print(f'  {q(str(v))}')
    # 检查护型分布
    alls = wx.apply(lambda v: q(str(v)))
    print(f'\n护型分布: {alls.value_counts().to_dict()}')