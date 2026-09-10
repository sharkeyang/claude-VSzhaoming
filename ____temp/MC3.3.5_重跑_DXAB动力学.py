# -*- coding: utf-8 -*-
"""MC3.3.5 重跑 - DXAB动力学(转负/持续时间/交叉/必要性)"""
import pandas as pd, numpy as np, os, glob, json, sys, warnings
from collections import defaultdict
warnings.simplefilter('ignore')
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)
DATA_DIR = r'昭明算展/谕组日'
BOARD_MAP_PATH = r'_产出物/MP1_花册分类映射.json'
MIN_SAMPLE = 100
C_DXCD=8; C_DXAB=9; C_日ZA=13; C_日ZC=14; C_BSHA=21; C_次日高幅=26; C_日等型=44
def load_board_map():
    with open(BOARD_MAP_PATH,'r',encoding='utf-8') as f: return json.load(f)
def parse_hx(s):
    if not s: return ''
    return {'a':'甲','b':'乙','c':'丙','z':'丁','y':'戊','r':'己'}.get(s[0],'')
def parse_za(s):
    """DXAB第2字符: + = ZA>0, - = ZA<0"""
    if not s or len(s)<2: return ''
    return '+' if s[1]=='+' else ('-' if s[1]=='-' else '')
board_map=load_board_map()
files=sorted(glob.glob(os.path.join(DATA_DIR,'谕组日_*.csv')))
def run_pool(pool_name, 目标板块):
    # 转负: (护型) -> [n, 转负数]
    zhuanfu=defaultdict(lambda:[0,0])
    # 持续时间: (护型, 持续天数) -> [n, hr3, sum]
    dur=defaultdict(lambda:[0,0,0.0])
    # 交叉次数: (护型, 交叉次数) -> [n, hr3, sum]
    cross=defaultdict(lambda:[0,0,0.0])
    # 必要性: (护型, 是否DXZC>0) -> [n, hr3, sum]
    nec=defaultdict(lambda:[0,0,0.0])
    # BSHA交叉: (护型, BSHA档) -> [n, hr3, sum]
    bsha=defaultdict(lambda:[0,0,0.0])
    nfiles=0
    for f in files:
        code=os.path.basename(f).replace('谕组日_','').replace('.csv','')
        if board_map.get(code,'') not in 目标板块: continue
        nfiles+=1
        try: df=pd.read_csv(f,encoding='gbk',header=None,skiprows=1)
        except: continue
        if len(df)<5: continue
        dxab=df[C_DXAB].astype(str).values
        hr=pd.to_numeric(df[C_次日高幅],errors='coerce').values
        zc=pd.to_numeric(df[C_日ZC],errors='coerce').values
        bs=pd.to_numeric(df[C_BSHA],errors='coerce').values
        hxs=[parse_hx(s) for s in dxab]
        zas=[parse_za(s) for s in dxab]
        # 转负: 当前护型ZA>0, 次日ZA<0
        for j in range(len(df)-1):
            hx=hxs[j]
            if not hx: continue
            if zas[j]=='+' and zas[j+1]=='-':
                zhuanfu[hx][0]+=1; zhuanfu[hx][1]+=1
            elif zas[j]=='+':
                zhuanfu[hx][0]+=1
        # 持续时间: 连续同护型
        i=0
        while i<len(df):
            hx=hxs[i]
            if not hx: i+=1; continue
            j=i
            while j<len(df) and hxs[j]==hx: j+=1
            d=j-i
            # 该段最后一天的次日高幅
            if j-1<len(df):
                h=hr[j-1]
                if not np.isnan(h) and -50<=h<=50:
                    dur[(hx,min(d,30))][0]+=1; dur[(hx,min(d,30))][1]+=(1 if h>=3 else 0); dur[(hx,min(d,30))][2]+=h
            i=j
        # 交叉次数: 段内DXZC>0的连续段数
        i=0
        while i<len(df):
            hx=hxs[i]
            if not hx: i+=1; continue
            j=i
            while j<len(df) and hxs[j]==hx: j+=1
            # 段内DXZC>0连续段数
            cnt=0; k=i; inrun=False
            while k<j:
                if not np.isnan(zc[k]) and zc[k]>0:
                    if not inrun: cnt+=1; inrun=True
                else: inrun=False
                k+=1
            if j-1<len(df):
                h=hr[j-1]
                if not np.isnan(h) and -50<=h<=50:
                    cross[(hx,min(cnt,5))][0]+=1; cross[(hx,min(cnt,5))][1]+=(1 if h>=3 else 0); cross[(hx,min(cnt,5))][2]+=h
            i=j
        # 必要性: 全样本 vs DXZC>0
        for j in range(len(df)):
            hx=hxs[j]
            if not hx: continue
            h=hr[j]
            if np.isnan(h) or h<-50 or h>50: continue
            nec[(hx,'全')][0]+=1; nec[(hx,'全')][1]+=(1 if h>=3 else 0); nec[(hx,'全')][2]+=h
            if not np.isnan(zc[j]) and zc[j]>0:
                nec[(hx,'ZC>0')][0]+=1; nec[(hx,'ZC>0')][1]+=(1 if h>=3 else 0); nec[(hx,'ZC>0')][2]+=h
        # BSHA交叉
        for j in range(len(df)):
            hx=hxs[j]
            if not hx: continue
            if np.isnan(zc[j]) or zc[j]<=0: continue
            h=hr[j]
            if np.isnan(h) or h<-50 or h>50: continue
            if not np.isnan(bs[j]):
                b='BSHA5+' if bs[j]>=5 else 'BSHA<5'
                bsha[(hx,b)][0]+=1; bsha[(hx,b)][1]+=(1 if h>=3 else 0); bsha[(hx,b)][2]+=h
    print()
    print('='*90)
    print(f'【{pool_name}】文件数:{nfiles}')
    print('='*90)
    # 3.1 转负概率
    print('\n【3.1 DXAB正交后转负概率】(ZA>0→ZA<0)')
    for hx in ['甲','乙','己','戊']:
        s=zhuanfu[hx]
        if s[0]>=MIN_SAMPLE:
            print(f'  {hx}: 转负={s[1]/s[0]*100:.1f}% (n={s[0]:,})')
    # 3.2 持续时间
    print('\n【3.2 持续时间×P(≥3%)】')
    for hx in ['甲','乙']:
        row=[]
        for d in [1,2,3,5,7,10,15,20,30]:
            s=dur[(hx,d)]
            row.append(f'{d}天:{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else f'{d}天:-')
        print(f'  {hx}: '+' | '.join(row))
    # 3.3 交叉次数
    print('\n【3.3 DXZC>0区域内DXAB交叉次数】')
    for hx in ['甲','乙','己','戊']:
        row=[]
        for c in [0,1,2,3,4,5]:
            s=cross[(hx,c)]
            row.append(f'{c}次:{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else f'{c}次:-')
        print(f'  {hx}: '+' | '.join(row))
    # 3.5 必要性
    print('\n【3.5 DXAB必要性】(全样本 vs DXZC>0)')
    for hx in ['甲','乙','己','戊','丙','丁']:
        s_all=nec[(hx,'全')]; s_zc=nec[(hx,'ZC>0')]
        if s_all[0]>=MIN_SAMPLE:
            print(f'  {hx}: 全样本={s_all[1]/s_all[0]*100:.1f}%({s_all[0]:,})  DXZC>0={s_zc[1]/s_zc[0]*100:.1f}%({s_zc[0]:,})')
    # 3.6 BSHA交叉
    print('\n【3.6 BSHA交叉关系】(DXZC>0)')
    for hx in ['甲','乙','己','戊']:
        row=[]
        for b in ['BSHA5+','BSHA<5']:
            s=bsha[(hx,b)]
            row.append(f'{b}:{s[1]/s[0]*100:.1f}%({s[0]:,})' if s[0]>=MIN_SAMPLE else f'{b}:-')
        print(f'  {hx}: '+' | '.join(row))
高波池={'Qic','Qim','Qit'}; 低波池={'Qd','Qe','Qif'}
print('########## 高波池 ##########'); run_pool('高波池',高波池)
print('\n########## 低波池 ##########'); run_pool('低波池',低波池)