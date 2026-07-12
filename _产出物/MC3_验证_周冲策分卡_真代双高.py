"""周冲周冲策分卡验证 — 真高幅+代高幅双版

真高幅 = 下周盘中最高价 vs 本周收盘  (使用col47 HR本周临)
代高幅 = 下周最高收盘价 vs 本周收盘 (使用col46 PR本周临)
"""
import win32com.client, os, datetime, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from collections import defaultdict

OUT_PATH = os.path.join(os.path.dirname(__file__), '验证_周冲周冲策分卡_真代双高.txt')
_out_lines = []
def P(s=''): print(s); _out_lines.append(s)
def flush_out():
    with open(OUT_PATH, 'w', encoding='utf-8') as f:
        f.write('\n'.join(_out_lines))

def _f(v):
    try: return float(v) if v else None
    except: return None

def parse_WXCD(s):
    s = str(s or '')
    return {'金':'金' in s, '银':'银' in s, '升':'升' in s}

def parse_WXAB(s):
    s = str(s or '')
    for k in ['甲','乙','丙','丁','戊','己']:
        if k in s: return k
    return ''

def parse_柱排(s):
    s = str(s or '')
    d = {'升': s.startswith('升'), '跌': s.startswith('跌'), '人': ('人' in s and not s.startswith('升') and not s.startswith('跌'))}
    d['尾反孕'] = ('尾反孕' in s)
    return d

D = os.path.join(os.path.dirname(__file__), '..', '昭明算展')
excel = win32com.client.GetActiveObject('Excel.Application')

all_items = []
for f in os.listdir(D):
    if f.startswith('算展.') and f.endswith('.xlsx'):
        code = f.replace('算展.', '').replace('.xlsx', '')
        fp = os.path.join(D, f)
        if code.startswith('sh000') or code.startswith('sz399'):
            cat = '指数'
        elif code in ('sz159919','sz159915','sh588000','sh510050','sz159920','sz159949','sh000016'):
            cat = '宽基指数'
        elif code.startswith('sz15') or code.startswith('sh51'):
            cat = '行业ETF'
        else:
            cat = '个股'
        all_items.append((code, cat, fp))
P(f'总标的: {len(all_items)}'); P()

all_weeks = []
for code, cat, fp in all_items:
    try:
        wb = excel.Workbooks.Open(fp)
        ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
        ws = wb.Sheets(ld)
        rows = ws.UsedRange.Rows.Count
        arr = ws.Range(ws.Cells(2,1), ws.Cells(rows,310)).Value
        wb.Close(False)
    except:
        P(f'  SKIP {code}'); continue

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
            'chg': _f(row[8]),
            'pr': _f(row[45]) or 0,   # col46 PR本 周临 (累计收盘收益率)
            'hr': _f(row[46]) or 0,   # col47 HR本 周临 (累计最高收益率)
            'jj': _f(row[35]) or 0,   # col36 结价(前日收盘)
            'wxcd_full': str(row[87] or ''),
            'wxab': str(row[78] or ''),
            'za_zhou': _f(row[281]) or 0,
            'col_zhou': str(row[81] or ''),
            'ying': str(row[84] or ''),
            'wave_zhou': str(row[79] or ''),
        })

    for wk in weeks:
        if not wk['days']: continue
        wr = 1.0
        for d in wk['days']:
            if d['chg'] is not None: wr *= (1 + d['chg']/100)
        wk['周收益'] = (wr - 1)*100

        # 本周收盘价 = 首日结价 * ∏(1+日涨)
        jj_start = wk['days'][0]['jj']
        if jj_start and jj_start > 0:
            c = jj_start
            closes = []
            for d in wk['days']:
                if d['chg'] is not None: c *= (1 + d['chg']/100)
                closes.append(c)
            wk['本周收盘'] = closes[-1]
            wk['本周最高收盘'] = max(closes)
            # 真代幅: 从本周首日算起
            wk['本周真幅'] = wk['days'][-1]['hr']   # HR本 周临 = 本周最高盘中收益率
            wk['本周代幅'] = wk['days'][-1]['pr']   # PR本 周临 = 本周收盘收益率(最后一天)
        else:
            wk['本周收盘'] = 0; wk['本周最高收盘'] = 0
            wk['本周真幅'] = 0; wk['本周代幅'] = 0

        last = wk['days'][-1]
        wxc = parse_WXCD(last['wxcd_full'])
        col_p = parse_柱排(last['col_zhou'])
        wk['WXCD金'] = wxc['金']; wk['WXCD银'] = wxc['银']; wk['WXCD升'] = wxc['升']
        wk['WXAB'] = parse_WXAB(last['wxab'])
        wk['ZA周'] = last['za_zhou']
        wk['柱排升'] = col_p['升']; wk['柱排跌'] = col_p['跌']; wk['柱排人'] = col_p['人']
        wk['尾反孕'] = col_p['尾反孕']; wk['非孕'] = not col_p['尾反孕']
        wk['盈提示'] = last['ying'] not in ('', '/', None, 'None')
        wk['波型周'] = str(last['wave_zhou'] or '')
        wk['code'] = code; wk['cat'] = cat

    valid = [w for w in weeks if w['days'] and w['本周收盘'] > 0]
    for i in range(len(valid)-1):
        w = valid[i]; nw = valid[i+1]
        w['下周涨'] = nw['周收益'] > 0
        w['下周收益'] = nw['周收益']

        # 🏆 真高幅: 下周盘中最高 vs 本周收盘
        # VBA公式: 临幅HR = (临高/结收-1)*100, 结收=本周首日收盘=上周五收盘
        # 下周结收 = 本周收盘, 所以 下周HR = (下周最高/本周收盘-1)*100 = 真高幅
        # HR已经是running max, 取最后一天的值即可
        nw_last = nw['days'][-1]  # 最后一天
        nw_hr = nw_last['hr']     # HR本周临(最后一天) = 本周最高盘中累积收益率
        # 代高幅需要取PR本周临的周内最大值(PR不是running max)
        nw_pr_max = max(d['pr'] for d in nw['days'])
        w['真高幅'] = nw_hr
        w['真冲高成功'] = nw_hr > 0
        w['真冲高3%'] = nw_hr >= 3
        w['真冲高5%'] = nw_hr >= 5
        w['代高幅'] = nw_pr_max
        w['代冲高成功'] = nw_pr_max > 0
        w['代冲高3%'] = nw_pr_max >= 3
        w['代冲高5%'] = nw_pr_max >= 5
        all_weeks.append(w)

P(f'总周数(有下周数据): {len(all_weeks)}'); P()

def test_condition(name, filter_fn, weeks=None):
    if weeks is None: weeks = all_weeks
    matched = [w for w in weeks if filter_fn(w)]
    if not matched: return {'name':name,'n':0, 'codes':0}
    n = len(matched)
    unique_codes = len(set(w['code'] for w in matched))
    res = {'name':name, 'n':n, 'codes':unique_codes}
    for prefix, label in [('真','真'), ('代','代')]:
        suc = f'{prefix}冲高成功'
        hi3 = f'{prefix}冲高3%'
        hi5 = f'{prefix}冲高5%'
        amp = f'{prefix}高幅'
        res[f'{label}_冲高'] = sum(1 for w in matched if w.get(suc,False))/n*100
        res[f'{label}_≥3%'] = sum(1 for w in matched if w.get(hi3,False))/n*100
        res[f'{label}_≥5%'] = sum(1 for w in matched if w.get(hi5,False))/n*100
        res[f'{label}_均幅'] = sum(w.get(amp,0) for w in matched)/n
    res['下周涨'] = sum(1 for w in matched if w['下周涨'])/n*100
    res['均收涨'] = sum(w['下周收益'] for w in matched)/n
    return res

def print_results(title, results):
    P(f'\n{"="*95}')
    P(f'  {title}')
    P(f'{"="*95}')
    P(f'{"条件":<28} {"代码数":>6} {"周数":>6} {"真冲高":>7} {"真≥3%":>6} {"真≥5%":>6} {"真均幅":>7} {"代冲高":>7} {"代≥3%":>6} {"代≥5%":>6} {"代均幅":>7}')
    for r in sorted(results, key=lambda x: -(x.get('真_冲高',0) or 0)):
        P(f'{r["name"]:<28} {r["codes"]:>6} {r["n"]:>6} {r["真_冲高"]:>6.0f}% {r["真_≥3%"]:>5.0f}% {r["真_≥5%"]:>5.0f}% {r["真_均幅"]:>6.2f}% {r["代_冲高"]:>6.0f}% {r["代_≥3%"]:>5.0f}% {r["代_≥5%"]:>5.0f}% {r["代_均幅"]:>6.2f}%')

S = test_condition

# ===== 基准 =====
base_all = S('全部周(基准)', lambda w: True)
P(f'基准: {base_all["n"]}周, {base_all["codes"]}标的')
for t in ['真','代']:
    P(f'  {t}冲高={base_all[f"{t}_冲高"]:.0f}%  {t}≥3%={base_all[f"{t}_≥3%"]:.0f}%  {t}≥5%={base_all[f"{t}_≥5%"]:.0f}%  {t}均幅={base_all[f"{t}_均幅"]:.2f}%')
P()

base_jin = lambda w: w['WXCD金'] and w['WXCD升']

# 1. 四域
print_results('1.四域', [
    S('多长(金升+甲乙己)', lambda w: base_jin(w) and w['WXAB'] in ('甲','乙','己')),
    S('多被(金升+丙丁戊)', lambda w: base_jin(w) and w['WXAB'] in ('丙','丁','戊')),
    S('银升+甲乙己', lambda w: w['WXCD银'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己')),
])

# 2. ZA
base_za = lambda w: base_jin(w) and w['WXAB'] in ('甲','乙','己')
print_results('2.ZA区间(多长基础上)', [
    S('ZA 1~2', lambda w: base_za(w) and 1 <= w['ZA周'] <= 2),
    S('ZA 3~5', lambda w: base_za(w) and 3 <= w['ZA周'] <= 5),
    S('ZA 5~7', lambda w: base_za(w) and 5 < w['ZA周'] <= 7),
    S('ZA 7~10', lambda w: base_za(w) and 7 < w['ZA周'] <= 10),
    S('ZA≥10', lambda w: base_za(w) and w['ZA周'] > 10),
])

# 3. 柱排
base_col = lambda w: base_za(w) and 0 < w['ZA周'] < 5
print_results('3.柱排(多长+ZA<5基础上)', [
    S('升排+非尾反孕', lambda w: base_col(w) and w['柱排升'] and w['非孕']),
    S('升排+尾反孕', lambda w: base_col(w) and w['柱排升'] and w['尾反孕']),
    S('人排', lambda w: base_col(w) and w['柱排人']),
    S('跌排', lambda w: base_col(w) and w['柱排跌']),
])

# 4. 盈提示(分资产)
print_results('4a.盈提示全量', [
    S('盈=有', lambda w: base_col(w) and w['盈提示']),
    S('盈=无', lambda w: base_col(w) and not w['盈提示']),
])
for cat in ['宽基指数','指数','行业ETF','个股']:
    cw = [w for w in all_weeks if w['cat']==cat]
    print_results(f'4b.盈-{cat}', [
        S(f'{cat}盈有', lambda w: base_col(w) and w['盈提示'], cw),
        S(f'{cat}盈无', lambda w: base_col(w) and not w['盈提示'], cw),
    ])

# 5. 波型
base_best = lambda w: base_col(w) and w['柱排升'] and w['非孕']
print_results('5.波型', [
    S('龙猪', lambda w: base_best(w) and '龙猪' in w['波型周']),
    S('头正', lambda w: base_best(w) and '头正' in w['波型周']),
    S('震正', lambda w: base_best(w) and '震正' in w['波型周']),
    S('头负/震负', lambda w: base_best(w) and ('头负' in w['波型周'] or '震负' in w['波型周'])),
])

# 6. 复合条件排名
P(f'\n{"="*85}')
P(f'  🏆 最优条件排名 (按真冲高成功率)')
P(f'{"="*85}')
P(f'{"条件铺叠":<28} {"代码数":>6} {"周数":>6} {"真冲高":>7} {"真≥3%":>6} {"真≥5%":>6} {"真均幅":>7} {"代冲高":>7} {"代≥3%":>6} {"代≥5%":>6} {"代均幅":>7}')
combo = []
combo.append(('全部周(基准)', lambda w: True))
combo.append(('多长(金升+甲乙己)', lambda w: base_jin(w) and w['WXAB'] in ('甲','乙','己')))
combo.append(('+ ZA>0', lambda w: base_za(w) and w['ZA周'] > 0))
combo.append(('+ ZA<5', lambda w: base_za(w) and 0 < w['ZA周'] < 5))
combo.append(('+ ZA 3~10', lambda w: base_za(w) and 3 <= w['ZA周'] <= 10))
combo.append(('+ ZA 7~10', lambda w: base_za(w) and 7 < w['ZA周'] <= 10))
combo.append(('+ 升排+非孕', lambda w: base_col(w) and w['柱排升'] and w['非孕']))
combo.append(('+ 升排+非孕+盈有', lambda w: base_col(w) and w['柱排升'] and w['非孕'] and w['盈提示']))
combo.append(('+ 升排+非孕+盈无', lambda w: base_col(w) and w['柱排升'] and w['非孕'] and not w['盈提示']))
combo.append(('+ ZA 7~10+升排+非孕', lambda w: base_za(w) and 7 < w['ZA周'] <= 10 and w['柱排升'] and w['非孕']))
combo.append(('+ ZA 3~10+升排+非孕', lambda w: base_za(w) and 3 <= w['ZA周'] <= 10 and w['柱排升'] and w['非孕']))

lr = [S(name, fn) for name, fn in combo]
for r in sorted(lr, key=lambda x: -(x.get('真_冲高',0) or 0)):
    P(f'{r["name"]:<28} {r["codes"]:>6} {r["n"]:>6} {r["真_冲高"]:>6.0f}% {r["真_≥3%"]:>5.0f}% {r["真_≥5%"]:>5.0f}% {r["真_均幅"]:>6.2f}% {r["代_冲高"]:>6.0f}% {r["代_≥3%"]:>5.0f}% {r["代_≥5%"]:>5.0f}% {r["代_均幅"]:>6.2f}%')

flush_out()
P(f'\n✅ 完成: {OUT_PATH}')