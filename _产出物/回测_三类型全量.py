"""
回测_三类型全量.py — 在ETF/指数/股票三类资产上跑5个算法
"""
import os, sys, datetime

def _f(v):
    try: return float(v) if v else None
    except: return None

def parse_wxcd(s):
    s=str(s or ''); return {'金':'金' in s,'升':'升' in s}

def parse_wxab(s):
    s=str(s or '')
    for k in ['甲','乙','己']:
        if k in s: return k
    return ''

D = os.path.join(os.path.dirname(__file__), "..", "昭明算展")
files = [f.replace('算展.','').replace('.xlsx','') for f in os.listdir(D) if f.endswith('.xlsx') and '算展.' in f]

categories = [
    ('ETF', [f for f in files if f[:4] in ['sh51','sh56','sh58','sz15']]),
    ('指数', [f for f in files if f[:4] in ['sh00','sz39']]),
    ('股票', [f for f in files if f[:4] not in ['sh51','sh56','sh58','sz15','sh00','sz39']]),
]

# 要测试的5个条件
conditions = [
    ('(1)金升+甲乙+ZA<5+升排+非孕',
     lambda w: w['金升'] and w['甲乙'] and 0<w['za']<5 and w['升排'] and not w['尾反孕']),
    ('(2)金升+甲乙+ZA<5+升排',
     lambda w: w['金升'] and w['甲乙'] and 0<w['za']<5 and w['升排']),
    ('(3)金升+甲乙+ZA>0+升排',
     lambda w: w['金升'] and w['甲乙'] and w['za']>0 and w['升排']),
    ('(4)金升+甲乙+ZA<5',
     lambda w: w['金升'] and w['甲乙'] and 0<w['za']<5),
    ('(5)金升+甲乙+ZA>0',
     lambda w: w['金升'] and w['甲乙'] and w['za']>0),
    ('基准(全部)', lambda w: True),
]

import win32com.client
try: excel = win32com.client.GetActiveObject('Excel.Application')
except: excel = win32com.client.Dispatch('Excel.Application'); excel.Visible = False

for cat_name, codes in categories:
    print(f'\n======== {cat_name} ({len(codes)}只) ========')

    results = {name:[] for name,fn in conditions}

    for code in codes:
        fpath = os.path.join(D, f'算展.{code}.xlsx')
        if not os.path.exists(fpath): continue
        try:
            wb = excel.Workbooks.Open(fpath)
            ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
            ws = wb.Sheets(ld); rows = ws.UsedRange.Rows.Count
            arr = ws.Range(ws.Cells(2,4), ws.Cells(rows,310)).Value
            wb.Close(False)
        except:
            try: wb.Close(False)
            except: pass
            continue

        weeks = []
        for r in range(len(arr)):
            row=arr[r]; dt=row[0]; chg=_f(row[1])
            if dt is None: continue
            if isinstance(dt,(int,float)):
                dt=datetime.datetime(1899,12,30)+datetime.timedelta(days=int(dt))
            mon=dt.date()-datetime.timedelta(days=dt.date().weekday())
            if not weeks or mon!=weeks[-1]['mon']:
                weeks.append({'mon':mon,'days':[]})
            weeks[-1]['days'].append({'chg':chg,'jj':_f(row[32]),
                'wxcd':str(row[84] or ''),'wxab':str(row[75] or ''),'za':_f(row[278]) or 0,
                'col':str(row[78] or ''),'wave':str(row[77] or '')})

        for wk in weeks:
            if not wk['days']: continue
            jj=wk['days'][0]['jj'] or 0; c=jj
            for d in wk['days']:
                if d['chg'] is not None: c*=(1+d['chg']/100)
            wk['close']=c; last=wk['days'][-1]
            wxcd=parse_wxcd(last['wxcd']); wxab=parse_wxab(last['wxab'])
            wk['金升']=wxcd['金'] and wxcd['升']
            wk['甲乙']=wxab in ('甲','乙','己')
            wk['za']=last['za']
            wk['升排']=last['col'][:1]=='升' if last['col'] else False
            wk['尾反孕']='尾反孕' in last['col']

        for i in range(len(weeks)-1):
            w=weeks[i]; nw=weeks[i+1]
            ret=(nw['close']-w['close'])/w['close']*100
            for name,fn in conditions:
                if fn(w):
                    results[name].append(ret)

    hdr = '条件                          样本    成功   成功率   平均收益'
    print(hdr)
    print('-'*60)
    for name,fn in conditions:
        r=results[name]
        if r:
            h=sum(1 for v in r if v>0)
            avg=sum(r)/len(r)
            print(f'{name:>28} {len(r):>6} {h:>5} {h/len(r)*100:>6.0f}% {avg:>7.2f}%')
