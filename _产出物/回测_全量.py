"""
回测_全量_v3.py — 整块读取+逐周对比，全量验证
"""
import os, sys, time

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

def main():
    import win32com.client
    try:
        excel = win32com.client.GetActiveObject('Excel.Application')
    except:
        excel = win32com.client.Dispatch('Excel.Application')
        excel.Visible = False

    D = os.path.join(os.path.dirname(__file__), "..", "昭明算展")
    all_files = sorted([f for f in os.listdir(D) if f.endswith('.xlsx') and '算展.' in f])
    print(f"算展文件: {len(all_files)}个")

    # 精选45个文件：15宽基+15行业+15个股
    idx = ['sh000001','sh000852','sz399905','sz399678','sz159919','sz159949',
           'sh588000','sh000016','sz399808','sh000003','sz159531','sh000139',
           'sz159920','sh510880','sz159931']
    etf = ['sh512480','sh515320','sz159663','sz159770','sh515980','sz159755',
           'sh512660','sh515880','sh516880','sh512690','sh512800','sh515210',
           'sh513100','sh513000','sh516950']
    stk = ['sh600906','sz300142','sh600048','sh600109','sh600702','sz000596',
           'sz300688','sz002555','sz300261','sh601888','sh600738','sh603536',
           'sz300413','sz300973','sh600155']

    for cat_name, files in [('宽基指数',idx),('行业ETF',etf),('个股',stk)]:
        print(f"\n{'='*60}")
        print(f"  {cat_name} ({len(files)}个)")
        print(f"{'='*60}")
        all_w = []
        t0 = time.time()

        for fname in files:
            fpath = os.path.join(D, f'算展.{fname}.xlsx')
            if not os.path.exists(fpath): continue
            try:
                wb = excel.Workbooks.Open(fpath)
                ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
                ws = wb.Sheets(ld)
                rows = ws.UsedRange.Rows.Count
                arr = ws.Range(ws.Cells(2, 36), ws.Cells(rows, 310)).Value
                wb.Close(False)

                # 每周只取一行
                weekly = []
                last_jj = None
                for r in range(len(arr)):
                    row = arr[r]
                    if row[0] is None: continue
                    try: jj = float(row[0])
                    except: continue
                    if last_jj and abs(jj-last_jj)<0.001: continue
                    last_jj = jj
                    weekly.append({
                        'close': jj,
                        'wxcd': str(row[52] or ''),  # C88
                        'wxab': str(row[43] or ''),  # C79
                        'za': _f(row[246]) or 0,     # C282
                        'wave': str(row[44] or ''),  # C80
                        'col': str(row[46] or ''),   # C82
                        'profit': str(row[49] or ''),# C85
                    })

                # 逐周对比
                for i in range(len(weekly)-1):
                    w = weekly[i]; nw = weekly[i+1]
                    if w['close'] <= 0: continue
                    ret = (nw['close'] - w['close']) / w['close'] * 100
                    wxcd = parse_wxcd(w['wxcd']); wxab = parse_wxab(w['wxab'])
                    if wxcd['金'] and wxcd['升'] and wxab in ('甲','乙','己') and w['za'] > 0:
                        all_w.append({
                            'ret': ret, 'za': w['za'],
                            '龙': '龙' in w['wave'],
                            '升': w['col'][:1]=='升' if w['col'] else False,
                            '盈': bool(w['profit']),
                        })
            except:
                try: wb.Close(False)
                except: pass

        print(f"  耗时: {time.time()-t0:.0f}s, 样本: {len(all_w)}周")
        if not all_w: continue

        base = sum(w['ret'] for w in all_w)/len(all_w)
        pos = sum(1 for w in all_w if w['ret']>0)/len(all_w)*100
        print(f"  基准: 平均{base:.2f}% 上涨率{pos:.0f}%")

        print(f"  {'条件':>18} {'样本':>6} {'平均':>8} {'上涨率':>8} {'vs基准':>8}")
        for label, fn in [('ZA<5', lambda w: w['za']<5),
                          ('2<ZA<5', lambda w: 2<w['za']<=5),
                          ('龙', lambda w: w['龙']),
                          ('升', lambda w: w['升']),
                          ('盈', lambda w: w['盈']),
                          ('龙+升', lambda w: w['龙'] and w['升']),
                          ('龙+升+ZA<5', lambda w: w['龙'] and w['升'] and w['za']<5)]:
            sub = [w for w in all_w if fn(w)]
            if sub and len(sub)>=20:
                a = sum(w['ret'] for w in sub)/len(sub)
                p = sum(1 for w in sub if w['ret']>0)/len(sub)*100
                print(f"  {label:>18} {len(sub):>6} {a:>7.2f}% {p:>7.0f}% {a-base:>+7.2f}%")

    print("\n✅ 完成")

if __name__ == "__main__":
    main()