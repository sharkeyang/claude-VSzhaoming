"""周冲周冲策分卡回测 — 下周冲高版（高幅 = 下周最高价 > 本周收盘价）"""
import win32com.client, os, datetime, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
from collections import defaultdict

OUT_PATH = os.path.join(os.path.dirname(__file__), '验证_周冲周冲策分卡_冲高版本.txt')
_out_lines = []
def P(s=''):
    print(s)
    _out_lines.append(s)
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

P(f'总标的: {len(all_items)}')
P()

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
        continue

    weeks = []
    for r in range(len(arr)):
        row = arr[r]
        dt = row[3]
        chg = _f(row[8])
        if dt is None: continue
        if isinstance(dt, (int,float)):
            dt = datetime.datetime(1899,12,30)+datetime.timedelta(days=int(dt))
        mon = dt.date() - datetime.timedelta(days=dt.date().weekday())
        if not weeks or mon != weeks[-1]['mon']:
            weeks.append({'mon':mon, 'days':[]})
        weeks[-1]['days'].append({
            'chg': chg,
            'h3': _f(row[33]) or 0,  # col34 H3最高
            'jj': _f(row[35]) or 0,  # col36 结价周前
            'wxcd_full': str(row[87] or ''),
            'wxab': str(row[78] or ''),
            'za_zhou': _f(row[281]) or 0,
            'col_zhou': str(row[81] or ''),
            'ying': str(row[84] or ''),
            'wave_zhou': str(row[79] or ''),
        })

    for wk in weeks:
        if not wk['days']: continue
        # 周收益(收盘→收盘)
        wr = 1.0
        for d in wk['days']:
            if d['chg'] is not None: wr *= (1 + d['chg']/100)
        wk['周收益'] = (wr - 1)*100

        # 本周收盘价 = 本周首日结价 * 周收益因子
        # 结价(first day of current week) = 前周收盘
        # 结价(first day of next week) = 本周收盘
        # 所以 本周收盘 = next周首日结价
        jj_first = wk['days'][0]['jj']

        # 本周最高价 = max(日H3)
        wk['高'] = max(d['h3'] for d in wk['days'])
        wk['低'] = min(d['h3'] for d in wk['days'])  # 近似用最低

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
        wk['jj_first'] = jj_first  # 本周首日结价 = 前周收盘

    valid = [w for w in weeks if w['days']]
    for i in range(len(valid)-1):
        w = valid[i]; nw = valid[i+1]
        # 本周收盘 = 下周首日结价
        w['本周收盘'] = nw['jj_first']
        # 下周冲高幅 = (下周最高 - 本周收盘) / 本周收盘
        if w['本周收盘'] and w['本周收盘'] > 0:
            w['下周冲高幅'] = (nw['高'] - w['本周收盘']) / w['本周收盘'] * 100
            w['下周冲高成功'] = w['下周冲高幅'] > 0  # 下周最高 > 本周收盘
            w['下周冲高3%'] = w['下周冲高幅'] >= 3.0  # 下周冲到+3%以上
            w['下周冲高5%'] = w['下周冲高幅'] >= 5.0
        # 下周收涨(沿用旧定义)
        w['下周涨'] = nw['周收益'] > 0
        w['下周收益'] = nw['周收益']
        all_weeks.append(w)

P(f'总周数(有下周数据): {len(all_weeks)}')
P()

def test_condition(name, filter_fn, weeks=None):
    if weeks is None: weeks = all_weeks
    matched = [w for w in weeks if filter_fn(w)]
    if not matched:
        return {'name':name, 'n':0}
    n = len(matched)
    # 下周收盘→收盘成功率
    win_close = sum(1 for w in matched if w['下周涨'])
    # 下周冲高成功率
    win_high = sum(1 for w in matched if w['下周冲高成功'])
    win_3pct = sum(1 for w in matched if w['下周冲高3%'])
    win_5pct = sum(1 for w in matched if w['下周冲高5%'])
    avg_high = sum(w['下周冲高幅'] for w in matched) / n
    avg_ret = sum(w['下周收益'] for w in matched) / n
    return {'name':name, 'n':n, 'close_win':win_close/n*100, 'high_win':win_high/n*100,
            'high_3pct':win_3pct/n*100, 'high_5pct':win_5pct/n*100,
            'avg_ret':avg_ret, 'avg_high':avg_high}

def print_results(title, results, key='high_win'):
    P(f'\n{"="*80}')
    P(f'  {title}')
    P(f'{"="*80}')
    P(f'{"条件":<34} {"样本":>6} {"下周涨":>7} {"下周冲高":>8} {"冲高≥3%":>8} {"冲高≥5%":>8} {"均冲高幅":>8} {"均收涨":>7}')
    for r in sorted(results, key=lambda x: -(x.get(key,0) or 0)):
        P(f'{r["name"]:<34} {r["n"]:>6} {r["close_win"]:>6.0f}% {r["high_win"]:>7.0f}% {r["high_3pct"]:>7.0f}% {r["high_5pct"]:>7.0f}% {r["avg_high"]:>7.2f}% {r["avg_ret"]:>6.2f}%')

# ============================================================
# 基准
# ============================================================
baseline_all = test_condition('基准(全部周)', lambda w: True)
P(f'总基准: {baseline_all["n"]}周')
P(f'  下周收涨: {baseline_all["close_win"]:.0f}%')
P(f'  下周冲高: {baseline_all["high_win"]:.0f}%')
P(f'  冲高≥3%: {baseline_all["high_3pct"]:.0f}%')
P(f'  均冲高幅: {baseline_all["avg_high"]:.2f}%')
P()

# ============================================================
# 各策略验证
# ============================================================
S = test_condition  # 别名

# 1. 四域
base_jin = lambda w: w['WXCD金'] and w['WXCD升']
results = [
    S('多长(金升+甲乙己)', lambda w: base_jin(w) and w['WXAB'] in ('甲','乙','己')),
    S('多被(金升+丙丁戊)', lambda w: base_jin(w) and w['WXAB'] in ('丙','丁','戊')),
]
print_results('验证1: 四域完整度', results)

# 2. ZA区间
base_za = lambda w: base_jin(w) and w['WXAB'] in ('甲','乙','己')
results = [
    S('ZA 1~2', lambda w: base_za(w) and 1 <= w['ZA周'] <= 2),
    S('ZA 3~5', lambda w: base_za(w) and 3 <= w['ZA周'] <= 5),
    S('ZA 5~7', lambda w: base_za(w) and 5 < w['ZA周'] <= 7),
    S('ZA 7~10', lambda w: base_za(w) and 7 < w['ZA周'] <= 10),
    S('ZA≥10', lambda w: base_za(w) and w['ZA周'] > 10),
    S('ZA>0', lambda w: base_za(w) and w['ZA周'] > 0),
    S('ZA<5', lambda w: base_za(w) and 0 < w['ZA周'] < 5),
]
print_results('验证2: ZA区间 (多长基础上)', results)

# 3. 柱排
base_col = lambda w: base_za(w) and 0 < w['ZA周'] < 5
results = [
    S('升排+非尾反孕', lambda w: base_col(w) and w['柱排升'] and w['非孕']),
    S('升排+尾反孕', lambda w: base_col(w) and w['柱排升'] and w['尾反孕']),
    S('人排', lambda w: base_col(w) and w['柱排人']),
    S('跌排', lambda w: base_col(w) and w['柱排跌']),
]
print_results('验证3: 柱排 (多长+ZA<5基础上)', results)

# 4. 盈提示
results = [
    S('盈提示=有(全量)', lambda w: base_col(w) and w['盈提示']),
    S('盈提示=无(全量)', lambda w: base_col(w) and not w['盈提示']),
]
print_results('验证4a: 盈提示全量', results)

for cat_name in ['宽基指数','指数','行业ETF','个股']:
    cw = [w for w in all_weeks if w['cat']==cat_name]
    r1 = S(f'{cat_name} 盈=有', lambda w: base_col(w) and w['盈提示'], cw)
    r2 = S(f'{cat_name} 盈=无', lambda w: base_col(w) and not w['盈提示'], cw)
    print_results(f'验证4b: 盈提示-{cat_name}', [r1,r2])

# 5. 波型
base_best = lambda w: base_col(w) and w['柱排升'] and w['非孕']
results = [
    S('波型=龙猪', lambda w: base_best(w) and '龙猪' in w['波型周']),
    S('波型=头正', lambda w: base_best(w) and '头正' in w['波型周']),
    S('波型=震正', lambda w: base_best(w) and '震正' in w['波型周']),
    S('波型=头负/震负', lambda w: base_best(w) and ('头负' in w['波型周'] or '震负' in w['波型周'])),
]
print_results('验证5: 波型', results)

# 6. 最优复合条件排序
P(f'\n{"="*80}')
P(f'  🏆 最优复合条件排名 (下周冲高成功率降序)')
P(f'{"="*80}')
P(f'{"条件铺叠":<34} {"样本":>6} {"下周涨":>7} {"下周冲高":>8} {"≥3%":>8} {"≥5%":>8} {"均冲高幅":>8}')

# 从简到繁铺叠条件
layers = {
    '全部周': lambda w: True,
    '多长(金升+甲乙己)': lambda w: base_jin(w) and w['WXAB'] in ('甲','乙','己'),
    '+ ZA>0': lambda w: base_za(w) and w['ZA周'] > 0,
    '+ ZA<5': lambda w: base_za(w) and 0 < w['ZA周'] < 5,
    '+ ZA 3~10': lambda w: base_za(w) and 3 <= w['ZA周'] <= 10,
    '+ ZA 7~10': lambda w: base_za(w) and 7 < w['ZA周'] <= 10,
    '+ 升排': lambda w: base_za(w) and 0 < w['ZA周'] < 5 and w['柱排升'],
    '+ 升排+非孕': lambda w: base_za(w) and 0 < w['ZA周'] < 5 and w['柱排升'] and w['非孕'],
    '+ 升排+非孕+盈有': lambda w: base_za(w) and 0 < w['ZA周'] < 5 and w['柱排升'] and w['非孕'] and w['盈提示'],
    '+ 升排+非孕+盈无': lambda w: base_za(w) and 0 < w['ZA周'] < 5 and w['柱排升'] and w['非孕'] and not w['盈提示'],
    '+ ZA 3~10+升排+非孕': lambda w: base_za(w) and 3 <= w['ZA周'] <= 10 and w['柱排升'] and w['非孕'],
    '+ ZA 7~10+升排+非孕': lambda w: base_za(w) and 7 < w['ZA周'] <= 10 and w['柱排升'] and w['非孕'],
}
layer_results = []
for label, fn in layers.items():
    sr = test_condition(label, fn)
    layer_results.append(sr)
for r in sorted(layer_results, key=lambda x: -(x.get('high_win',0) or 0)):
    P(f'{r["name"]:<34} {r["n"]:>6} {r["close_win"]:>6.0f}% {r["high_win"]:>7.0f}% {r["high_3pct"]:>7.0f}% {r["high_5pct"]:>7.0f}% {r["avg_high"]:>7.2f}%')

flush_out()
P(f'\n✅ 完成, 结果已写入: {OUT_PATH}')