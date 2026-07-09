"""
回测_周级别_条件.py — 理论周一法 + 算展WXCD/WXAB/ZA + 3个算法验证
"""
import os, sys, datetime

def _f(v):
    try: return float(v) if v else None
    except: return None

def parse_wxcd(s):
    s = str(s or ''); return {'金': '金' in s, '升': '升' in s}

def parse_wxab(s):
    s = str(s or '')
    for k in ['甲','乙','己']:
        if k in s: return k
    return ''

targets = [('sh000001','上证指数'),('sh000852','中证1000'),('sz159919','沪深300ETF'),
           ('sh512480','半导体ETF'),('sh515320','电子50ETF'),('sh588000','科创50ETF'),
           ('sz159663','机床ETF')]

D = r'D:\@VSwork\VS昭明计划VBA优化\昭明算展'
import win32com.client
try: excel = win32com.client.GetActiveObject('Excel.Application')
except: excel = win32com.client.Dispatch('Excel.Application'); excel.Visible = False

print('%-14s %5s %5s %6s %8s %8s %8s  |  %6s %8s %8s  |  %6s %8s' % (
    '标的', '周数', '条件', '上涨率', '平均', '涨高幅', '跌低幅', '基上涨率', '基涨高幅', '基跌低幅', '提升', '提升幅'))
print('-'*120)

for code, name in targets:
    fpath = os.path.join(D, '算展.' + code + '.xlsx')
    if not os.path.exists(fpath): continue
    wb = excel.Workbooks.Open(fpath)
    ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
    ws = wb.Sheets(ld); rows = ws.UsedRange.Rows.Count

    arr = ws.Range(ws.Cells(2, 4), ws.Cells(rows, 310)).Value
    wb.Close(False)

    # 理论周一法分组
    week_rows = []; weeks = []
    for r in range(len(arr)):
        row = arr[r]; dt = row[0]; chg = _f(row[1])
        if dt is None: continue
        if isinstance(dt, (int, float)):
            dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=int(dt))
        mon = dt.date() - datetime.timedelta(days=dt.date().weekday())
        if mon != (weeks[-1]['mon'] if weeks else None):
            weekly = []
            weeks.append({'mon': mon, 'rows': weekly, 'close': 0})
            weekly = weeks[-1]['rows']
        weeks[-1]['rows'].append({'chg': chg, 'jj': _f(row[32]),
            'wxcd': str(row[84] or ''), 'wxab': str(row[75] or ''),
            'za': _f(row[278]) or 0,
            'wave': str(row[44] or ''), 'col': str(row[46] or ''), 'profit': str(row[49] or '')})

    # 计算每周数据
    cond_rets = []; all_rets = []
    for i in range(len(weeks)):
        wk = weeks[i]; rows = wk['rows']
        jj = rows[0]['jj'] or 0; close = jj
        for d in rows:
            if d['chg'] is not None: close *= (1 + d['chg']/100)
        wk['close'] = close
        last = rows[-1]
        wxcd = parse_wxcd(last['wxcd']); wxab = parse_wxab(last['wxab'])
        wk['gold'] = wxcd['金'] and wxcd['升'] and wxab in ('甲','乙','己')
        wk['za'] = last['za']

    for i in range(len(weeks)-1):
        ret = (weeks[i+1]['close'] - weeks[i]['close']) / weeks[i]['close'] * 100
        all_rets.append(ret)
        if weeks[i]['gold'] and weeks[i]['za'] > 0:
            cond_rets.append(ret)

    n = len(cond_rets); bn = len(all_rets)
    if n == 0 or bn == 0: continue

    up = sum(1 for r in cond_rets if r>0)
    b_up = sum(1 for r in all_rets if r>0)
    avg = sum(cond_rets)/n
    b_avg = sum(all_rets)/bn
    ua = sum(r for r in cond_rets if r>0)/up if up else 0
    da = sum(r for r in cond_rets if r<0)/(n-up) if n-up else 0
    bua = sum(r for r in all_rets if r>0)/b_up if b_up else 0
    bda = sum(r for r in all_rets if r<0)/(bn-b_up) if bn-b_up else 0

    print('%-14s %5d %5d %5.0f%% %7.2f%% %7.2f%% %7.2f%%  |  %5.0f%% %7.2f%% %7.2f%%  |  %+5.0f%% %+6.2f%%' % (
        name, len(weeks), n, up/n*100, avg, ua, da,
        b_up/bn*100, bua, bda,
        up/n*100 - b_up/bn*100, avg - b_avg))

print('\n✅ 完成')