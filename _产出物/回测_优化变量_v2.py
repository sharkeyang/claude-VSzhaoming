"""
回测_优化变量_v2.py — 深度优化：ZA阈值扫描+多变量组合
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

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
    targets = ['sh000852','sh512480','sz159663','sh515320','sh588000','sz399678','sz159919']
    files = []
    for f in sorted(os.listdir(D)):
        if f.endswith('.xlsx') and '算展' in f:
            b = f.replace('算展.','').replace('.xlsx','')
            if b in targets: files.append(os.path.join(D, f))

    weeks = []
    for fpath in files:
        try:
            wb = excel.Workbooks.Open(fpath)
            ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
            ws = wb.Sheets(ld); rows = ws.UsedRange.Rows.Count
            last_jj = None
            wdata = []
            for r in range(2, rows+1):
                jj = _f(ws.Cells(r, 36).value)
                if jj is None: continue
                if last_jj and abs(jj-last_jj)<0.001: continue
                last_jj = jj
                wdata.append({
                    'close_prev': jj,
                    'wxcd': str(ws.Cells(r, 88).value or ''),
                    'wxab': str(ws.Cells(r, 79).value or ''),
                    'za': _f(ws.Cells(r, 282).value) or 0,
                    'zb': _f(ws.Cells(r, 283).value) or 0,
                    'zc': _f(ws.Cells(r, 284).value) or 0,
                    'zd': _f(ws.Cells(r, 288).value) or 0,
                    'ze': _f(ws.Cells(r, 292).value) or 0,
                    'wave': str(ws.Cells(r, 80).value or ''),
                    'column': str(ws.Cells(r, 82).value or ''),
                    'profit': str(ws.Cells(r, 85).value or ''),
                    'die': _f(ws.Cells(r, 37).value) or 0,  # 叠幅
                    'wja': str(ws.Cells(r, 81).value or ''),
                })
            for i in range(len(wdata)-1):
                w = wdata[i]; nw = wdata[i+1]
                ret = (nw['close_prev']-w['close_prev'])/w['close_prev']*100
                if w['close_prev'] <= 0: continue
                wxcd = parse_wxcd(w['wxcd']); wxab = parse_wxab(w['wxab'])
                if wxcd['金'] and wxcd['升'] and wxab in ('甲','乙','己') and w['za'] > 0:
                    weeks.append({
                        'ret': ret, 'za': w['za'], 'zb': w['zb'], 'zc': w['zc'],
                        'zd': w['zd'], 'ze': w['ze'], 'die': w['die'],
                        'wave': w['wave'], 'column': w['column'], 'profit': w['profit'],
                        'wja': w['wja'],
                        '龙': '龙' in w['wave'], '猪': '龙猪' in w['wave'],
                        '管': '龙管' in w['wave'], '头': '头' in w['wave'],
                        '升': w['column'][:1]=='升' if w['column'] else False,
                        '跌': w['column'][:1]=='跌' if w['column'] else False,
                        '盈': bool(w['profit']), '盈高': '高' in w['profit'],
                    })
            wb.Close(False)
        except: pass

    print(f"样本: {len(weeks)}周")
    if not weeks: return
    base = sum(w['ret'] for w in weeks)/len(weeks)
    pos_base = sum(1 for w in weeks if w['ret']>0)/len(weeks)*100
    print(f"基准: 平均{base:.2f}% 上涨率{pos_base:.0f}%")

    # 1. ZA阈值扫描
    print("\n" + "="*60)
    print("  ZA阈值扫描（找最佳区间）")
    print("="*60)
    print(f"{'ZA范围':>12} {'样本':>6} {'平均':>8} {'上涨率':>8}")
    for lo, hi in [(0,2),(2,5),(5,10),(10,15),(15,25),(25,99)]:
        sub = [w for w in weeks if lo < w['za'] <= hi]
        if sub:
            avg = sum(w['ret'] for w in sub)/len(sub)
            pos = sum(1 for w in sub if w['ret']>0)/len(sub)*100
            print(f"{f'{lo}<ZA<={hi}':>12} {len(sub):>6} {avg:>7.2f}% {pos:>7.0f}%")

    # 2. 波型细分
    print("\n" + "="*60)
    print("  波型细分")
    print("="*60)
    for label, fn in [('龙猪', lambda w: w['猪']), ('龙管', lambda w: w['管']),
                       ('龙猪+龙管', lambda w: w['龙']), ('头', lambda w: w['头']),
                       ('其他', lambda w: not w['龙'] and not w['头'])]:
        sub = [w for w in weeks if fn(w)]
        if sub:
            avg = sum(w['ret'] for w in sub)/len(sub)
            pos = sum(1 for w in sub if w['ret']>0)/len(sub)*100
            print(f"  {label:>12} {len(sub):>6} {avg:>7.2f}% {pos:>7.0f}%")

    # 3. 柱排尾部形态
    print("\n" + "="*60)
    print("  柱排尾部形态")
    print("="*60)
    for label, kw in [('尾连', '尾连'), ('尾吞', '尾吞'), ('尾反孕', '尾反孕'),
                       ('连后吞', '连后吞'), ('升开头', None)]:
        if kw:
            sub = [w for w in weeks if kw in w['column']]
        else:
            sub = [w for w in weeks if w['升']]
        if sub:
            avg = sum(w['ret'] for w in sub)/len(sub)
            pos = sum(1 for w in sub if w['ret']>0)/len(sub)*100
            print(f"  {label:>12} {len(sub):>6} {avg:>7.2f}% {pos:>7.0f}%")

    # 4. 叠幅（波动率）过滤
    print("\n" + "="*60)
    print("  叠幅（波动率）过滤")
    print("="*60)
    mids = sorted(weeks, key=lambda w: w['die'])
    sub_low = mids[:len(mids)//3]
    sub_mid = mids[len(mids)//3:2*len(mids)//3]
    sub_high = mids[2*len(mids)//3:]
    for label, sub in [('低波动', sub_low), ('中波动', sub_mid), ('高波动', sub_high)]:
        avg = sum(w['ret'] for w in sub)/len(sub)
        pos = sum(1 for w in sub if w['ret']>0)/len(sub)*100
        print(f"  {label:>12} {len(sub):>6} {avg:>7.2f}% {pos:>7.0f}%")

    # 5. 最优复合条件
    print("\n" + "="*60)
    print("  最优复合条件（Top 组合）")
    print("="*60)
    combos = [
        ('龙+升+ZA<5', lambda w: w['龙'] and w['升'] and w['za'] < 5),
        ('龙+升+盈', lambda w: w['龙'] and w['升'] and w['盈']),
        ('龙+升+ZA<3', lambda w: w['龙'] and w['升'] and w['za'] < 3),
        ('龙+升+ZA<2', lambda w: w['龙'] and w['升'] and w['za'] < 2),
        ('龙+跌+ZA<5', lambda w: w['龙'] and w['跌'] and w['za'] < 5),
        ('龙+盈+ZA<5', lambda w: w['龙'] and w['盈'] and w['za'] < 5),
        ('升+盈+ZA<5', lambda w: w['升'] and w['盈'] and w['za'] < 5),
        ('龙+升+尾连', lambda w: w['龙'] and w['升'] and '尾连' in w['column']),
        ('龙+升+尾吞', lambda w: w['龙'] and w['升'] and '尾吞' in w['column']),
        ('龙+升+尾反孕', lambda w: w['龙'] and w['升'] and '尾反孕' in w['column']),
        ('龙+升+盈高', lambda w: w['龙'] and w['升'] and w['盈高']),
    ]
    print(f"{'组合':>20} {'样本':>6} {'平均':>8} {'上涨率':>8} {'vs基准':>8}")
    for label, fn in combos:
        sub = [w for w in weeks if fn(w)]
        if sub and len(sub) >= 30:
            avg = sum(w['ret'] for w in sub)/len(sub)
            pos = sum(1 for w in sub if w['ret']>0)/len(sub)*100
            diff = avg - base
            print(f"{label:>20} {len(sub):>6} {avg:>7.2f}% {pos:>7.0f}% {diff:>+7.2f}%")

    print("\n✅ 完成")

if __name__ == "__main__":
    main()