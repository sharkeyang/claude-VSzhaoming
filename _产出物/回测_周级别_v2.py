"""
回测_周级别_v2.py — 正确的理论周一周边界 + OHLC + 基准结果
"""
import os, sys, datetime, csv

def _f(v):
    try: return float(v) if v else None
    except: return None

targets = [
    ('sh000001','上证指数'), ('sh000852','中证1000'), ('sh600519','贵州茅台'),
    ('sz159919','沪深300ETF'), ('sh510050','上证50ETF'), ('sh510300','沪深300ETF华'),
    ('sh512480','半导体ETF'), ('sh515320','电子50ETF'), ('sh588000','科创50ETF'),
    ('sz159663','机床ETF'),
]

results = []
for code, name in targets:
    csv_path = 'D:/zdata/data中股/' + code + '.csv'
    if not os.path.exists(csv_path): continue

    days = []
    with open(csv_path) as f:
        for row in csv.reader(f):
            if len(row) >= 6:
                try:
                    dt = datetime.datetime.strptime(row[1], '%Y-%m-%d').date()
                    days.append({'date': dt, 'open': float(row[2]), 'high': float(row[3]),
                                 'low': float(row[4]), 'close': float(row[5])})
                except: pass

    weeks = []
    cur = None
    for d in days:
        mon = d['date'] - datetime.timedelta(days=d['date'].weekday())
        if cur is None or mon != cur['mon']:
            if cur: weeks.append(cur)
            cur = {'mon': mon, 'open': d['open'], 'high': d['high'], 'low': d['low'],
                   'close': d['close']}
        else:
            cur['high'] = max(cur['high'], d['high'])
            cur['low'] = min(cur['low'], d['low'])
            cur['close'] = d['close']
    if cur: weeks.append(cur)

    all_rets = []
    for i in range(len(weeks)-1):
        ret = (weeks[i+1]['close'] - weeks[i]['close']) / weeks[i]['close'] * 100
        all_rets.append(ret)

    n = len(all_rets)
    if n > 0:
        up = sum(1 for r in all_rets if r>0)
        avg = sum(all_rets)/n
        ua = sum(r for r in all_rets if r>0)/up if up else 0
        da = sum(r for r in all_rets if r<0)/(n-up) if n-up else 0
        results.append((name, len(weeks), n, up/n*100, avg, ua, da))
        print('%12s %5d %5d %6.0f%% %7.2f%% %8.2f%% %8.2f%%' % (name, len(weeks), n, up/n*100, avg, ua, da))

print('\n✅ 完成')