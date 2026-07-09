"""调试: 是否有办法计算下周每日最高价?"""
import win32com.client, os, datetime, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

code = 'sz159919'
fp = os.path.join(D, f'算展.{code}.xlsx')
wb = excel.Workbooks.Open(fp)
ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
ws = wb.Sheets(ld)
rows = ws.UsedRange.Rows.Count

# 批量读col1-50
arr = ws.Range(ws.Cells(2,1), ws.Cells(rows, 50)).Value
wb.Close(False)

# 第1周5天: 看哪些列每天变化
print('第1周5天, col1-40 各列值:')
for r in range(5):
    row = arr[r]
    dt = row[3]  # col4
    if isinstance(dt, (int,float)):
        dt = str(datetime.datetime(1899,12,30)+datetime.timedelta(days=int(dt)).date())
    chg = row[8]  # col9 日涨
    # 关键列: col28~36
    vals = {c: row[c-1] for c in range(28, 37)}
    print(f'  row{r+2}({dt}): 日涨={chg:>5}  P0={vals[28]} H0={vals[31]} H3={vals[33]} 结价={vals[35]}')

# 但! 我可以从日涨推导每日最高价的下限:
# 每日最高价至少 >= 每日收盘价
# 每日收盘 = 前日收盘 * (1+日涨/100)
# 所以下周最高 >= max(下周每日收盘)

# 也可以从日涨+开盘价推导
# 日涨 = (收盘-开盘)/前日收盘? 不, 日涨 = (收盘-前日收盘)/前日收盘
# 所以如果日涨>0, 收盘>前日收盘, 最高>=收盘
# 如果日涨<0, 最高>=开盘 (但开盘未知)

# 更好的方法: 用"冲高" = 下周至少有一天收盘 > 本周收盘
# 等价于 max(下周每日日涨) > 0
# 这可以近似冲高信号

# 验证: 冲高成功率 vs 下周收涨成功率
print('\n用"下周至少有一天涨"近似冲高:')
weeks = []
for r in range(len(arr)):
    row = arr[r]
    dt = row[3]
    chg = row[8]
    if dt is None: continue
    if isinstance(dt, (int,float)):
        dt = datetime.datetime(1899,12,30)+datetime.timedelta(days=int(dt))
    mon = dt.date() - datetime.timedelta(days=dt.date().weekday())
    if not weeks or mon != weeks[-1]['mon']:
        weeks.append({'mon':mon, 'days':[]})
    weeks[-1]['days'].append({'chg':chg})

valid = [w for w in weeks if len(w['days'])>=3]
close_win = 0
high_win = 0
total = 0
for i in range(len(valid)-1):
    w = valid[i]; nw = valid[i+1]
    wr = 1.0
    for d in nw['days']:
        if d['chg'] is not None: wr *= (1+d['chg']/100)
    nw_ret = (wr-1)*100
    has_positive_day = any(d['chg'] and d['chg']>0 for d in nw['days'] if d['chg'] is not None)
    close_win += 1 if nw_ret > 0 else 0
    high_win += 1 if has_positive_day else 0
    total += 1

print(f'{code}: {total}周')
print(f'  下周收涨(收盘): {close_win/total*100:.0f}%  ({close_win}/{total})')
print(f'  下周冲高(至少一天涨): {high_win/total*100:.0f}%  ({high_win}/{total})')