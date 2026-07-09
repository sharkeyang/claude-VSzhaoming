#!/usr/bin/env python3
import urllib.request, json

api = json.loads(urllib.request.urlopen('http://127.0.0.1:5000/api/data').read())
print('API positions:', len(api.get('positions',[])))
print('API market_prices:', len(api.get('market_prices',{})))
print('API intraday:', len(api.get('intraday',{})))
print('API watch_rules:', len(api.get('watch_rules',[])))

html = urllib.request.urlopen('http://127.0.0.1:5000/').read().decode('utf-8')
print()
print('HTML size:', len(html))
print('Has posCards:', 'id="posCards"' in html or 'posCards' in html)
print('Has pieChart:', 'pieChart' in html)
print('Has 策卡:', '策卡' in html)
print('Has setInterval:', 'setInterval' in html)
print('Has refresh():', 'refresh()' in html)
print('Has fetch:', "fetch('/api/data')" in html)