"""全量60个标的算法验证"""
import win32com.client, os, datetime, sys

def _f(v):
    try: return float(v) if v else None
    except: return None

def pw(s):
    s=str(s or ''); return {'金':'金' in s,'升':'升' in s}

def pa(s):
    s=str(s or '')
    for k in ['甲','乙','己']:
        if k in s: return k
    return ''

excel=win32com.client.GetActiveObject('Excel.Application')
D=os.path.join(os.path.dirname(__file__),'..','昭明算展')

all_items = []
for cat,cs in [
    ('宽基ETF',['sz159919','sh588000','sz159949','sz159531','sz159920']),
    ('半导体',['sh512480','sh513310','sh515320','sh515980']),
    ('科技',['sh516000','sh516510','sz159613','sz159998','sh515230']),
    ('新能源',['sh516880','sz159755','sh516780','sh515220','sh515210']),
    ('医药',['sh512170','sz159992','sh513060','sz159766']),
    ('金融',['sh512070','sh512800','sz159931','sh513190','sh510880']),
    ('军工',['sh512660','sh563380','sh516320']),
    ('消费',['sh515710','sh512690','sh562960']),
    ('传媒',['sh515880','sh512980','sz159869','sh516620']),
    ('海外',['sh513000','sh513100','sh513050','sh513330','sh513360','sh510900']),
    ('行业其他',['sz159825','sz159867','sz159663','sz159770','sz159745','sz159768']),
    ('指数',['sh000001','sh000852','sz399905','sz399678','sz399808']),
]:
    for c in cs:
        fp = os.path.join(D,f'算展.{c}.xlsx')
        if os.path.exists(fp) and c not in [x[1] for x in all_items]:
            all_items.append((cat,c))

print(f'标的总数: {len(all_items)}')
print()

from collections import defaultdict
by_cat = defaultdict(list)

for cat, code in all_items:
    try:
        wb = excel.Workbooks.Open(os.path.join(D,f'算展.{code}.xlsx'))
        ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
        ws = wb.Sheets(ld); rows = ws.UsedRange.Rows.Count
        arr = ws.Range(ws.Cells(2,4), ws.Cells(rows,310)).Value
        wb.Close(False)
    except: continue

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
            'col':str(row[78] or '')})

    for wk in weeks:
        if not wk['days']: continue
        jj=wk['days'][0]['jj'] or 0; c=jj
        for d in wk['days']:
            if d['chg'] is not None: c*=(1+d['chg']/100)
        wk['close']=c; last=wk['days'][-1]
        wxcd=pw(last['wxcd']); wxab=pa(last['wxab'])
        wk['金升']=wxcd['金'] and wxcd['升']
        wk['甲乙']=wxab in ('甲','乙','己')
        wk['za']=last['za']
        wk['升排']=last['col'][:1]=='升' if last['col'] else False
        wk['非孕']='尾反孕' not in last['col']

    # 算法1: 最优条件
    rets = []
    for i in range(len(weeks)-1):
        w=weeks[i]; nw=weeks[i+1]
        if w['金升'] and w['甲乙'] and 0<w['za']<5 and w['升排'] and w['非孕']:
            rets.append((nw['close']-w['close'])/w['close']*100)
    by_cat[code] = (cat, len(weeks), len(rets), rets)

output_lines = []
for code, (cat, tw, n, rets) in sorted(by_cat.items(), key=lambda x: -(sum(1 for r in x[1][3] if r>0)/len(x[1][3])*100 if x[1][3] else 0)):
    if rets:
        h = sum(1 for r in rets if r>0)
        avg = sum(rets)/len(rets)
        output_lines.append(f'{code:>12} {cat:>10} {tw:>5} {n:>5} {h/len(rets)*100:>6.0f}% {avg:>7.2f}%')
        if len(output_lines) <= 60:
            print(output_lines[-1])

print(f'\n--- 汇总 ---')
print(f'覆盖标的: {len(output_lines)}')
print(f'平均成功率: {sum(int(l.split()[4].replace(chr(37),"")) for l in output_lines)/len(output_lines):.0f}%')
