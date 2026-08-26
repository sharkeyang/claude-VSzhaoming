# -*- coding: utf-8 -*-
import json, datetime

def load(f):
    return json.load(open(f, encoding='utf-8'))

snap = load('snapshot.json')['data']
hist = load('history.json')['data']

items = hist['item']
# Trim to last 250 trading days
items = items[-250:]

# Convert to clean records
def fmt_date(ms):
    return datetime.datetime.fromtimestamp(ms/1000).strftime('%Y-%m-%d')

records = []
for it in items:
    records.append({
        'date': fmt_date(it['date_ms']),
        'date_ms': it['date_ms'],
        'open': round(it['open_price'], 2),
        'high': round(it['high_price'], 2),
        'low': round(it['low_price'], 2),
        'close': round(it['close_price'], 2),
        'volume': it['volume'],
        'turnover': it['turnover'],
    })

closes = [r['close'] for r in records]
n = len(records)

# --- Metrics ---
# Interval return (first close -> last close)
first_close = closes[0]
last_close = closes[-1]
interval_return = (last_close - first_close) / first_close * 100

# MA20/MA60/MA120 (last value)
def ma(period):
    if n < period:
        return None
    return round(sum(closes[-period:]) / period, 2)
ma20 = ma(20)
ma60 = ma(60)
ma120 = ma(120)

# 60-day max drawdown (from peak to trough over last 60 bars)
window60 = closes[-60:]
peak = window60[0]
max_dd = 0.0
for c in window60:
    if c > peak:
        peak = c
    dd = (peak - c) / peak * 100
    if dd > max_dd:
        max_dd = dd
max_drawdown_60 = round(max_dd, 2)

# 20-day average turnover (成交额)
turn20 = [r['turnover'] for r in records[-20:]]
avg_turnover_20 = sum(turn20) / len(turn20)

# Snapshot fields
snap_item = snap['item'][0]
snapshot = {
    'thscode': snap_item['thscode'],
    'ticker': snap_item['ticker'],
    'name': '同花顺',
    'last_price': snap_item['last_price'],
    'price_change': snap_item['price_change'],
    'price_change_ratio_pct': snap_item['price_change_ratio_pct'],
    'open_price': snap_item['open_price'],
    'high_price': snap_item['high_price'],
    'low_price': snap_item['low_price'],
    'prev_price': snap_item['prev_price'],
    'volume': snap_item['volume'],
    'turnover': snap_item['turnover'],
    'snapshot_time': datetime.datetime.fromtimestamp(snap['timestamp']/1000).strftime('%Y-%m-%d %H:%M:%S'),
}

# MA series for chart (compute rolling MA for all points)
def ma_series(period):
    out = []
    for i in range(n):
        if i < period - 1:
            out.append(None)
        else:
            out.append(round(sum(closes[i-period+1:i+1]) / period, 2))
    return out

ma20_series = ma_series(20)
ma60_series = ma_series(60)
ma120_series = ma_series(120)

# Attach MA to records
for i, r in enumerate(records):
    r['ma20'] = ma20_series[i]
    r['ma60'] = ma60_series[i]
    r['ma120'] = ma120_series[i]

data = {
    'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    'snapshot': snapshot,
    'metrics': {
        'interval_return_pct': round(interval_return, 2),
        'ma20': ma20,
        'ma60': ma60,
        'ma120': ma120,
        'max_drawdown_60_pct': max_drawdown_60,
        'avg_turnover_20': avg_turnover_20,
        'first_date': records[0]['date'],
        'last_date': records[-1]['date'],
        'bars': n,
        'adjust': 'forward',
        'interval': '1d',
    },
    'records': records,
}

with open('_consolidated.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

print('written _consolidated.json')
print('bars:', n, 'first:', records[0]['date'], 'last:', records[-1]['date'])
print('interval_return:', round(interval_return,2), '%')
print('ma20/60/120:', ma20, ma60, ma120)
print('max_dd_60:', max_drawdown_60, '%')
print('avg_turnover_20:', round(avg_turnover_20, 0))
print('snapshot:', snapshot['name'], snapshot['last_price'], snapshot['price_change_ratio_pct'])