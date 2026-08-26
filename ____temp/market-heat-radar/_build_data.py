import json, datetime

def load(f):
    d=json.load(open(f,encoding='utf-8'))
    return d['data']

def fmt_ts(ms):
    return datetime.datetime.fromtimestamp(ms/1000).strftime('%Y-%m-%d %H:%M:%S')

hot_day=load('hot_day.json'); hot_hour=load('hot_hour.json')
sky_day=load('sky_day.json'); sky_hour=load('sky_hour.json')

trends={}
for code in ['688836','600487','600127']:
    trends[code]=load(f'trend_{code}.json')['item']

name_map={it['thscode']:it['name'] for it in hot_day['item']}

def clean(items):
    out=[]
    for it in items:
        out.append({
            'rank':it['rank'],'name':it['name'],'thscode':it['thscode'],
            'ticker':it['ticker'],'heat':it['heat'],
            'rank_change':it['rank_change'],'rank_trend':it['rank_trend']
        })
    return out

def codes(items): return {it['thscode'] for it in items}
hd,hh,sd,sh=codes(hot_day['item']),codes(hot_hour['item']),codes(sky_day['item']),codes(sky_hour['item'])

trend_series=[]
for code in ['688836','600487','600127']:
    items=trends[code]
    series=[{'date':it['date'],'rank':it['rank']} for it in items]
    ths=items[0]['thscode']
    trend_series.append({'thscode':ths,'name':name_map.get(ths,ths),'series':series})

data={
  'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
  'timestamps':{
    'hot_day':fmt_ts(hot_day['timestamp']),
    'hot_hour':fmt_ts(hot_hour['timestamp']),
    'sky_day':fmt_ts(sky_day['timestamp']),
    'sky_hour':fmt_ts(sky_hour['timestamp']),
  },
  'lists':{
    'hot_day':clean(hot_day['item']),
    'hot_hour':clean(hot_hour['item']),
    'sky_day':clean(sky_day['item']),
    'sky_hour':clean(sky_hour['item']),
  },
  'overlap':{
    'hot_day_hot_hour':len(hd&hh),
    'sky_day_sky_hour':len(sd&sh),
    'hot_day_sky_day':len(hd&sd),
    'hot_hour_sky_hour':len(hh&sh),
    'hot_day_sky_hour':len(hd&sh),
  },
  'trends':trend_series,
}

with open('_consolidated.json','w',encoding='utf-8') as f:
    json.dump(data,f,ensure_ascii=False,indent=1)
print('written')
print('trends:',[(t['thscode'],t['name'],len(t['series'])) for t in data['trends']])
