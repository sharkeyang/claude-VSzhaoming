"""
分析_失败案例.py — 金升+甲乙+ZA>0条件下，下周仍然下跌的案例特征
"""
import os, sys, datetime

def _f(v):
    try: return float(v) if v else None
    except: return None

def parse_wxcd(s):
    s = str(s or '')
    return {'金': '金' in s, '银': '银' in s, '升': '升' in s, '降': '降' in s, '源': s[:20]}

def parse_wxab(s):
    s = str(s or '')
    for k in ['甲','乙','己','丙','丁','戊']:
        if k in s: return k
    return ''

targets = [('sh000001','上证指数'),('sh000852','中证1000'),('sz159919','沪深300ETF'),
           ('sh512480','半导体ETF'),('sh515320','电子50ETF'),('sh588000','科创50ETF'),
           ('sz159663','机床ETF')]

D = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展'
import win32com.client
try: excel = win32com.client.GetActiveObject('Excel.Application')
except: excel = win32com.client.Dispatch('Excel.Application'); excel.Visible = False

all_fails = []

for code, name in targets:
    fpath = os.path.join(D, '算展.' + code + '.xlsx')
    if not os.path.exists(fpath): continue
    wb = excel.Workbooks.Open(fpath)
    ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
    ws = wb.Sheets(ld); rows = ws.UsedRange.Rows.Count
    arr = ws.Range(ws.Cells(2, 4), ws.Cells(rows, 310)).Value
    wb.Close(False)

    weeks = []; cur_days = None
    for r in range(len(arr)):
        row = arr[r]; dt = row[0]; chg = _f(row[1])
        if dt is None: continue
        if isinstance(dt, (int, float)):
            dt = datetime.datetime(1899,12,30) + datetime.timedelta(days=int(dt))
        mon = dt.date() - datetime.timedelta(days=dt.date().weekday())
        if not weeks or mon != weeks[-1]['mon']:
            if cur_days: weeks[-1]['close'] = cur_close
            weeks.append({'mon': mon, 'days': [], 'close': 0})
        jj = _f(row[32]);
        close = jj if jj else 0
        weeks[-1]['days'].append({
            'chg': chg, 'jj': jj,
            'wxcd': str(row[84] or ''), 'wxab': str(row[75] or ''),
            'za': _f(row[278]) or 0,
            'wave': str(row[44] or ''), 'col': str(row[46] or ''),
            'profit': str(row[49] or ''), 'date': dt,
        })
        cur_close = close
        if len(weeks[-1]['days']) > 1:
            jj0 = weeks[-1]['days'][0]['jj'] or 0; c = jj0
            for d in weeks[-1]['days']:
                if d['chg'] is not None: c *= (1 + d['chg']/100)
            weeks[-1]['close'] = c

    for wk in weeks:
        if not wk['days']: continue
        wk['close'] = wk['days'][-1]['close']  # approximate
        # Actually compute close properly
        jj = wk['days'][0]['jj'] or 0
        c = jj
        for d in wk['days']:
            if d['chg'] is not None: c *= (1 + d['chg']/100)
        wk['close'] = c
        last = wk['days'][-1]
        wxcd = parse_wxcd(last['wxcd']); wxab = parse_wxab(last['wxab'])
        wk['gold'] = wxcd['金'] and wxcd['升'] and wxab in ('甲','乙','己')
        wk['za'] = last['za']
        wk['wxcd_raw'] = last['wxcd']
        wk['wxab_raw'] = last['wxab']
        wk['wave'] = last['wave']
        wk['col'] = last['col']
        wk['profit'] = last['profit']
        wk['end_date'] = last['date']

    for i in range(len(weeks)-1):
        w = weeks[i]; nw = weeks[i+1]
        if not w['gold'] or w['za'] <= 0: continue
        ret = (nw['close'] - w['close']) / w['close'] * 100
        if ret < 0:
            # 检查下一周WXCD是否变了
            nwxcd = parse_wxcd(weeks[i+1]['wxcd_raw'])
            wxcd_changed = not nwxcd['金'] or not nwxcd['升']
            all_fails.append({
                'name': name, 'date': str(w['mon']), 'ret': ret,
                'za': w['za'], 'wxcd': str(w['wxcd_raw'])[:25], 'wxab': str(w['wxab_raw'])[:20],
                'wave': str(w['wave'])[:15], 'col': str(w['col'])[:15], 'profit': bool(w['profit']),
                'wxcd_changed': wxcd_changed,
                'nw_wxcd': str(weeks[i+1]['wxcd_raw'])[:20],
            })

print(f'总失败案例: {len(all_fails)}')
print()

# 按原因分类
reasons = {}
for f in all_fails:
    # 下周WXCD变了？
    if f['wxcd_changed']:
        key = '下周金升→其他'
    elif f['za'] > 10:
        key = 'ZA过高(>10)'
    elif f['za'] > 5:
        key = 'ZA偏高(5-10)'
    elif f['wave'] and '头' in f['wave']:
        key = '波型=头'
    elif f['col'] and '跌' in f['col'][:1]:
        key = '柱排=跌开头'
    elif f['profit']:
        key = '有盈提示'
    else:
        key = '无明显特征'
    reasons[key] = reasons.get(key, 0) + 1

print('失败原因分布:')
total = len(all_fails)
for k, v in sorted(reasons.items(), key=lambda x: -x[1]):
    print(f'  {k:>20}: {v:>4}次 ({v/total*100:.0f}%)')

print()
print('失败案例明细（前15条）:')
for f in all_fails[:15]:
    print(f'  {f[\"name\"]:>8} {f[\"date\"]} 跌幅={f[\"ret\"]:>5.1f}% ZA={f[\"za\"]:>2.0f} WXCD={f[\"wxcd\"]:>25} WXAB={f[\"wxab\"]:>15} 波型={f[\"wave\"]:>12} 柱排={f[\"col\"]:>10} 盈={f[\"profit\"]}')

# 统计：失败案例中，下周WXCD变化的占比
changed = sum(1 for f in all_fails if f['wxcd_changed'])
print(f'\n失败案例中下周WXCD变化的: {changed}/{total} ({changed/total*100:.0f}%)')