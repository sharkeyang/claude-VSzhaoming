"""
回测_优化变量.py — 在金升+甲乙+ZA>0基础上，测试各附加变量的边际收益
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

def _f(v):
    try: return float(v) if v else None
    except: return None

def parse_wxcd(s):
    s = str(s or '')
    return {'金': '金' in s, '升': '升' in s}

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

    算展目录 = os.path.join(os.path.dirname(__file__), "..", "昭明算展")
    targets = ['sh000852','sh512480','sz159663','sh515320','sh588000','sz399678','sz159919']
    文件列表 = []
    for f in sorted(os.listdir(算展目录)):
        if f.endswith('.xlsx') and '算展' in f:
            base = f.replace('算展.','').replace('.xlsx','')
            if base in targets:
                文件列表.append(os.path.join(算展目录, f))

    # 收集所有符合条件的周数据，带附加变量
    base_weeks = []  # 金升+甲乙+ZA>0 的周数据

    for fpath in 文件列表:
        fname = os.path.basename(fpath)
        try:
            wb = excel.Workbooks.Open(fpath)
            ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
            ws = wb.Sheets(ld)
            rows = ws.UsedRange.Rows.Count

            last_jj = None
            weekly = []
            for r in range(2, rows + 1):
                jj = _f(ws.Cells(r, 36).value)
                if jj is None: continue
                if last_jj is not None and abs(jj - last_jj) < 0.001: continue
                last_jj = jj
                weekly.append({
                    'close_prev': jj,
                    'sy': str(ws.Cells(r, 310).value or ''),
                    'wxcd': str(ws.Cells(r, 88).value or ''),
                    'wxab': str(ws.Cells(r, 79).value or ''),
                    'za': _f(ws.Cells(r, 282).value) or 0,
                    'zb': _f(ws.Cells(r, 283).value) or 0,
                    'zc': _f(ws.Cells(r, 284).value) or 0,
                    'ze': _f(ws.Cells(r, 292).value) or 0,
                    'wave': str(ws.Cells(r, 80).value or ''),
                    'column': str(ws.Cells(r, 82).value or ''),
                    'profit': str(ws.Cells(r, 85).value or ''),
                })

            for i in range(len(weekly) - 1):
                w = weekly[i]
                nw = weekly[i+1]
                ret = (nw['close_prev'] - w['close_prev']) / w['close_prev'] * 100
                if w['close_prev'] <= 0: continue

                wxcd = parse_wxcd(w['wxcd'])
                wxab = parse_wxab(w['wxab'])
                if wxcd['金'] and wxcd['升'] and wxab in ('甲','乙','己') and w['za'] > 0:
                    base_weeks.append({
                        'ret': ret,
                        'za': w['za'], 'zb': w['zb'], 'zc': w['zc'], 'ze': w['ze'],
                        '龙': '龙' in w['wave'],
                        '头': '头' in w['wave'],
                        '柱升': '升' in w['column'][:1] if w['column'] else False,
                        '柱跌': '跌' in w['column'][:1] if w['column'] else False,
                        '盈': bool(w['profit']),
                        '四域多长': w['sy'] == '多长',
                        '四域多被': w['sy'] == '多被',
                    })

            wb.Close(False)
        except:
            try: wb.Close(False)
            except: pass

    print(f"基础样本（金升+甲乙+ZA>0）: {len(base_weeks)}周")
    if not base_weeks:
        return

    avg_base = sum(w['ret'] for w in base_weeks) / len(base_weeks)
    pos_base = sum(1 for w in base_weeks if w['ret'] > 0) / len(base_weeks) * 100
    print(f"  基准: 平均{avg_base:.2f}% 上涨率{pos_base:.0f}%")

    # 测试各个附加变量的分组效果
    tests = [
        ('ZB>0', lambda w: w['zb'] > 0),
        ('ZC>0', lambda w: w['zc'] > 0),
        ('ZE>0', lambda w: w['ze'] > 0),
        ('波型含龙', lambda w: w['龙']),
        ('柱排升开头', lambda w: w['柱升']),
        ('柱排跌开头', lambda w: w['柱跌']),
        ('盈提示非空', lambda w: w['盈']),
        ('四域=多长', lambda w: w['四域多长']),
        ('四域=多被', lambda w: w['四域多被']),
        ('ZA>5', lambda w: w['za'] > 5),
        ('ZA>10', lambda w: w['za'] > 10),
    ]

    print(f"\n{'变量':>16} {'样本':>6} {'平均':>8} {'上涨率':>8} {'vs基准':>8}")
    print("-"*55)
    for name, fn in tests:
        subset = [w for w in base_weeks if fn(w)]
        if subset:
            avg = sum(w['ret'] for w in subset) / len(subset)
            pos = sum(1 for w in subset if w['ret'] > 0) / len(subset) * 100
            diff = avg - avg_base
            tag = "✅" if diff > 0.2 else ("❌" if diff < -0.2 else "➖")
            print(f"{name:>16} {len(subset):>6} {avg:>7.2f}% {pos:>7.0f}% {diff:>+7.2f}% {tag}")

    # 复合条件测试
    print(f"\n{'复合条件':>20} {'样本':>6} {'平均':>8} {'上涨率':>8} {'vs基准':>8}")
    print("-"*60)
    combos = [
        ('ZB>0+龙', lambda w: w['zb'] > 0 and w['龙']),
        ('ZC>0+龙', lambda w: w['zc'] > 0 and w['龙']),
        ('ZB>0+多长', lambda w: w['zb'] > 0 and w['四域多长']),
        ('龙+柱升', lambda w: w['龙'] and w['柱升']),
        ('ZC>0+多长', lambda w: w['zc'] > 0 and w['四域多长']),
        ('ZA>5+龙', lambda w: w['za'] > 5 and w['龙']),
    ]
    for name, fn in combos:
        subset = [w for w in base_weeks if fn(w)]
        if subset and len(subset) > 30:
            avg = sum(w['ret'] for w in subset) / len(subset)
            pos = sum(1 for w in subset if w['ret'] > 0) / len(subset) * 100
            diff = avg - avg_base
            tag = "✅" if diff > 0.3 else ("❌" if diff < -0.3 else "➖")
            print(f"{name:>20} {len(subset):>6} {avg:>7.2f}% {pos:>7.0f}% {diff:>+7.2f}% {tag}")

    print("\n✅ 完成")

if __name__ == "__main__":
    main()