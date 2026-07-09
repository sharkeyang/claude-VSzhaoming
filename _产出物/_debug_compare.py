"""调试: 对比新旧两种周收益计算方法"""
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
arr = ws.Range(ws.Cells(2,1), ws.Cells(rows,310)).Value
wb.Close(False)

# 日→周聚合
weeks = []
for r in range(len(arr)):
    row = arr[r]
    dt = row[3]  # col4 主期
    chg = row[8]  # col9 日涨
    jj = row[35]  # col36 结价周前
    if dt is None: continue
    if isinstance(dt, (int,float)):
        dt = datetime.datetime(1899,12,30)+datetime.timedelta(days=int(dt))
    mon = dt.date() - datetime.timedelta(days=dt.date().weekday())
    if not weeks or mon != weeks[-1]['mon']:
        weeks.append({'mon':mon, 'days':[]})
    weeks[-1]['days'].append({'chg':chg, 'jj':jj, 'dt':dt.date()})

# 方法A（旧）: close = 结价周前 * ∏(1+chg/100), chg用col5(主七)
# 方法B（新）: 周收益 = ∏(1+日涨/100)-1, 日涨用col9

print(f'{code} 两周对比:')
print(f'{"周":>6} {"天数":>4} {"方法A(旧)close":>16} {"方法B(新)wr%":>12} {"col36_jj":>10} {"col5_主七":>10} {"col9_日涨":>10}')
for i in range(min(10, len(weeks))):
    wk = weeks[i]
    ds = wk['days']
    # 方法A: 用col5(主七)当chg, 用col36(jj)当close base
    c_old = ds[0]['jj'] or 0
    if c_old == 0: c_old = 1
    for d in ds:
        chg_old = d.get('chg_old', 0)  # col5 — 但我们没有存col5!
    # 方法B: 用col9(日涨)
    wr = 1.0
    for d in ds:
        chg = d['chg']
        if chg is not None: wr *= (1 + chg/100)
    wr_pct = (wr - 1)*100

    # 信息
    jj_val = ds[0]['jj']
    if len(ds) >= 2:
        next_jj = ds[1]['jj']
    else:
        next_jj = 0
    print(f'{i:>6} {len(ds):>4} {0:>16.2f} {wr_pct:>12.2f} {jj_val:>10} {0:>10} 日涨={[d["chg"] for d in ds[:3]]}')

# 检查 日涨 vs 结价 的关系
print(f'\n前5周各组日涨:')
for i in range(min(5, len(weeks))):
    wk = weeks[i]
    chgs = [d['chg'] for d in wk['days'][:5]]
    jjs = [d['jj'] for d in wk['days'][:5]]
    print(f'  周{i}: 日涨={chgs}, 结价={jjs}')
    # 如果结价周前在周内相同，则应该都相等
    if len(set(str(v) for v in jjs if v)) > 1:
        print(f'    ⚠️ 结价周前在周内不一致!')

# 对比两个连续周的 结价
print('\n连续周 结价对比:')
for i in range(min(10, len(weeks)-1)):
    wk = weeks[i]
    nwk = weeks[i+1]
    jj_this = wk['days'][0]['jj']
    jj_next = nwk['days'][0]['jj']
    if jj_this and jj_this > 0 and jj_next and jj_next > 0:
        ret_old = (jj_next - jj_this) / jj_this * 100  # 方法A: 纯结价比
    else:
        ret_old = 0
    # 方法B
    wr_new = 1.0
    for d in nwk['days']:
        if d['chg'] is not None: wr_new *= (1 + d['chg']/100)
    ret_new = (wr_new - 1)*100
    print(f'  周{i}→周{i+1}: 结价比={ret_old:.2f}% 日涨累积={ret_new:.2f}% 差异={abs(ret_old-ret_new):.2f}pp')