"""调试2: 对齐后比较 结价比 vs 日涨累积"""
import win32com.client, os, datetime, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

for code in ['sz159919', 'sh000001', 'sh512480']:
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
        dt = row[3]
        if dt is None: continue
        if isinstance(dt, (int,float)):
            dt = datetime.datetime(1899,12,30)+datetime.timedelta(days=int(dt))
        mon = dt.date() - datetime.timedelta(days=dt.date().weekday())
        if not weeks or mon != weeks[-1]['mon']:
            weeks.append({'mon':mon, 'days':[]})
        weeks[-1]['days'].append({
            'date': dt.date(),
            'chg': row[8],     # col9 日涨
            'jj': row[35],     # col36 结价周前
            'p0': row[28],     # col29 P0开盘
            'p3': row[33],     # col34 H3最高
        })

    errors = []
    for i in range(min(len(weeks)-1, 200)):
        wk = weeks[i]
        nwk = weeks[i+1]

        # 方法A: 结价比 = next周首日结价 / 本周首日结价 - 1
        # 本周首日结价 = 上周五收盘, next周首日结价 = 本周五收盘
        jj_this = wk['days'][0]['jj']
        jj_next = nwk['days'][0]['jj']
        if jj_this and jj_next and jj_this > 0 and jj_next > 0:
            ret_jj = (jj_next / jj_this - 1) * 100
        else:
            ret_jj = None

        # 方法B: 本周日涨累积 = ∏(1+日涨/100)-1
        wr = 1.0
        for d in wk['days']:
            if d['chg'] is not None: wr *= (1 + d['chg']/100)
        ret_chg = (wr - 1)*100

        if ret_jj is not None and ret_jj != 0:
            err = abs(ret_jj - ret_chg)
            errors.append(err)
            if len(errors) <= 10:
                print(f'{code} 周{i}: 结价={jj_this:.3f}→{jj_next:.3f}={ret_jj:.2f}% 日涨累积={ret_chg:.2f}% 差异={err:.2f}pp')

    avg_err = sum(errors)/len(errors) if errors else 0
    print(f'{code}: 均差异={avg_err:.2f}pp (共{len(errors)}周) 日涨值样本={[d["chg"] for d in weeks[0]["days"][:5]]}')
    print()