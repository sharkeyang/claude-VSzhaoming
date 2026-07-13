"""周冲周冲策分卡全量验证 — 每个赋分条件独立回测下周成功率

输出同时写到 stdout 和 _产出物/验证_周冲周冲策分卡_结果.txt (UTF-8)
"""
import win32com.client, os, datetime, sys, io
from collections import defaultdict

# 强制 UTF-8 输出
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

OUT_PATH = os.path.join(os.path.dirname(__file__), '验证_周冲周冲策分卡_结果.txt')
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
    return {'金':'金' in s, '银':'银' in s, '升':'升' in s, '降':'降' in s}

def parse_WXAB(s):
    s = str(s or '')
    for k in ['甲','乙','丙','丁','戊','己']:
        if k in s: return k
    return ''

def parse_柱排(s):
    s = str(s or '')
    d = {'升': s.startswith('升'), '跌': s.startswith('跌'), '人': ('人' in s and not s.startswith('升') and not s.startswith('跌'))}
    d['尾反孕'] = ('尾反孕' in s)
    d['尾连'] = ('尾连' in s)
    d['尾吞'] = ('尾吞' in s)
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

P(f'总标的: {len(all_items)} 指数={sum(1 for _,c,_ in all_items if c=="指数")} 宽基={sum(1 for _,c,_ in all_items if c=="宽基指数")} 行业ETF={sum(1 for _,c,_ in all_items if c=="行业ETF")} 个股={sum(1 for _,c,_ in all_items if c=="个股")}')
P()

# ============================================================
# 逐标的周数据解析
# 列位置确认(2026-07-09):
#   col 4=日期 col 9=日涨 col 36=结价 col 79=WXAB col 80=波型
#   col 82=柱排周 col 88=大局WXCD col 89=日周联动(含盈='盈')
#   col 96=柱排日 col 282=ZA周 col 308=日机警 col 309=日层段
# ============================================================
all_weeks = []

for code, cat, fp in all_items:
    try:
        wb = excel.Workbooks.Open(fp)
        ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
        ws = wb.Sheets(ld)
        rows = ws.UsedRange.Rows.Count
        arr = ws.Range(ws.Cells(2,1), ws.Cells(rows,310)).Value
        wb.Close(False)
    except Exception as e:
        P(f'  SKIP {code}: {e}')
        continue

    # 日→周聚合 (按理论周一)
    weeks = []
    for r in range(len(arr)):
        row = arr[r]
        dt = row[3]  # col 4: 主期(日期)
        chg = _f(row[8])  # col 9: 日涨
        if dt is None: continue
        if isinstance(dt, (int, float)):
            dt = datetime.datetime(1899,12,30) + datetime.timedelta(days=int(dt))
        mon = dt.date() - datetime.timedelta(days=dt.date().weekday())

        if not weeks or mon != weeks[-1]['mon']:
            weeks.append({'mon': mon, 'days': []})
        weeks[-1]['days'].append({
            'dt': dt.date(), 'chg': chg,
            'wxcd_full': str(row[87] or ''),  # col 88: 大局WXCD
            'wxab': str(row[78] or ''),        # col 79: 护型WXAB
            'zc_zhou': _f(row[283]) or 0,      # col 284: ZC周
            'za_zhou': _f(row[281]) or 0,      # col 282: ZA周
            'col_zhou': str(row[81] or ''),     # col 82: 柱排周
            'ying_col89': str(row[88] or ''),   # col 89: 日周联动(含盈='盈')
            'wave_zhou': str(row[79] or ''),    # col 80: 波型周
            'ri_cengduan': str(row[308] or ''), # col 309: 日层段
            'ri_ji': str(row[307] or ''),       # col 308: 日机警
            'p0': _f(row[27]) or 0,            # col 28: P0(开盘)
            'p3': _f(row[34]) or 0,            # col 35: H3(最高)
            'prev_close': _f(row[35]) or 0,     # col 36: 结价(前周收盘)
        })

    # 计算每周: 周收益=∏(1+日涨幅)-1
    for wk in weeks:
        if not wk['days']: continue
        wr = 1.0
        for d in wk['days']:
            if d['chg'] is not None:
                wr *= (1 + d['chg']/100)
        wk['周收益'] = (wr - 1) * 100
        last = wk['days'][-1]
        wxc = parse_WXCD(last['wxcd_full'])
        col_p = parse_柱排(last['col_zhou'])
        wk['WXCD金'] = wxc['金']
        wk['WXCD银'] = wxc['银']
        wk['WXCD升'] = wxc['升']
        wk['WXAB'] = parse_WXAB(last['wxab'])
        wk['ZA周'] = last['za_zhou']
        wk['ZC周'] = last['zc_zhou']
        wk['柱排升'] = col_p['升']
        wk['柱排跌'] = col_p['跌']
        wk['柱排人'] = col_p['人']
        wk['尾反孕'] = col_p['尾反孕']
        wk['非孕'] = not col_p['尾反孕']
        wk['盈提示'] = '盈' in last['ying_col89']
        wk['波型周'] = str(last['wave_zhou'] or '')
        wk['日层段'] = str(last['ri_cengduan'] or '')
        wk['日机警'] = str(last['ri_ji'] or '')
        wk['code'] = code
        wk['cat'] = cat
        # 上影线 = (最高-开盘)/前周收盘
        h = last['p3']; o = last['p0']; pc = last['prev_close']
        wk['上影占比'] = (h - o) / pc * 100 if (pc and pc > 0 and h and o) else 0

    # 下周收益 = 下一周的周收益
    valid = [w for w in weeks if w['days']]
    for i in range(len(valid)-1):
        w = valid[i]; nw = valid[i+1]
        w['下周涨'] = nw['周收益'] > 0
        w['下周收益'] = nw['周收益']
        all_weeks.append(w)

    del weeks, valid

P(f'总周数(有下周数据): {len(all_weeks)}')
P()

# ============================================================
# 验证函数
# ============================================================
def test_condition(name, filter_fn, weeks=None):
    if weeks is None: weeks = all_weeks
    matched = [w for w in weeks if filter_fn(w)]
    if not matched:
        return {'name': name, 'n': 0, 'win': None, 'avg_ret': None}
    n = len(matched)
    win = sum(1 for w in matched if w['下周涨'])
    avg = sum(w['下周收益'] for w in matched) / n
    return {'name': name, 'n': n, 'win': win/n*100, 'avg_ret': avg}

def print_results(title, results, baseline=None):
    P(f'\n{"="*72}')
    P(f'  {title}')
    P(f'{"="*72}')
    if baseline and baseline.get('win') is not None:
        P(f'{"条件":<34} {"样本":>6} {"成功率":>7} {"均收益":>8} {"vs基准":>8}')
        for r in results:
            vs = f'{r["win"]-baseline["win"]:+.1f}%' if r.get('win') is not None else ''
            win_s = f'{r["win"]:.0f}%' if r.get('win') is not None else '   -'
            ret_s = f'{r["avg_ret"]:.2f}%' if r.get('avg_ret') is not None else '    -'
            P(f'{r["name"]:<34} {r["n"]:>6} {win_s:>7} {ret_s:>8} {vs:>8}')
    else:
        P(f'{"条件":<34} {"样本":>6} {"成功率":>7} {"均收益":>8}')
        for r in results:
            win_s = f'{r["win"]:.0f}%' if r.get('win') is not None else '   -'
            ret_s = f'{r["avg_ret"]:.2f}%' if r.get('avg_ret') is not None else '    -'
            P(f'{r["name"]:<34} {r["n"]:>6} {win_s:>7} {ret_s:>8}')

# ============================================================
# 基准条件
# ============================================================
baseline_all = test_condition('基准(全部周)', lambda w: True)
baseline_jin = test_condition('基准(金升+甲乙己)', lambda w: w['WXCD金'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己'))
P(f'全量基准: {baseline_all["n"]}周, 成功率={baseline_all["win"]:.0f}%, 均收益={baseline_all["avg_ret"]:.3f}%')
P(f'金升+甲乙己基准: {baseline_jin["n"]}周, 成功率={baseline_jin["win"]:.0f}%, 均收益={baseline_jin["avg_ret"]:.3f}%')

# ============================================================
# 验证1: 四域完整度细分
# ============================================================
base_jin = lambda w: w['WXCD金'] and w['WXCD升']
results_wxab = [
    test_condition('金升+甲乙己 (多长)', lambda w: base_jin(w) and w['WXAB'] in ('甲','乙','己')),
    test_condition('金升+丙丁戊 (多被)', lambda w: base_jin(w) and w['WXAB'] in ('丙','丁','戊')),
    test_condition('银升+甲乙己', lambda w: w['WXCD银'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己')),
    test_condition('银升+丙丁戊', lambda w: w['WXCD银'] and w['WXCD升'] and w['WXAB'] in ('丙','丁','戊')),
    test_condition('金+降', lambda w: w['WXCD金'] and (not w['WXCD升'])),
]
print_results('验证1: 四域完整度 (基准=金升+甲乙己)', results_wxab, baseline_jin)

# ============================================================
# 验证2: ZA区间细分 (在 金升+甲乙己 基础上)
# ============================================================
baseline_za = test_condition('金升+甲乙+ZA>0', lambda w: w['WXCD金'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己') and w['ZA周'] > 0)
base_za = lambda w: w['WXCD金'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己') and w['ZA周'] > 0
results_za = [
    test_condition('ZA 1~2', lambda w: base_za(w) and 1 <= w['ZA周'] < 3),
    test_condition('ZA 3~5', lambda w: base_za(w) and 3 <= w['ZA周'] < 5),
    test_condition('ZA 5~7', lambda w: base_za(w) and 5 <= w['ZA周'] < 7),
    test_condition('ZA 7~10', lambda w: base_za(w) and 7 <= w['ZA周'] < 10),
    test_condition('ZA ≥10', lambda w: base_za(w) and w['ZA周'] >= 10),
    test_condition('ZA=0(刚上DJZ)', lambda w: w['WXCD金'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己') and w['ZA周'] == 0),
]
print_results('验证2: ZA区间 (基准=金升+甲乙+ZA>0)', results_za, baseline_za)

# ============================================================
# 验证3: 柱排形态细分 (在 金升+甲乙+ZA<5 基础上)
# ============================================================
base_col_ref = test_condition('金升+甲乙+ZA<5 (柱排基准)', lambda w: w['WXCD金'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己') and 0 < w['ZA周'] < 5)
base_col = lambda w: w['WXCD金'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己') and 0 < w['ZA周'] < 5
results_col = [
    test_condition('升排+非尾反孕 (最优)', lambda w: base_col(w) and w['柱排升'] and w['非孕']),
    test_condition('升排+尾反孕 (最后一柱)', lambda w: base_col(w) and w['柱排升'] and w['尾反孕']),
    test_condition('升排+尾连', lambda w: base_col(w) and w['柱排升'] and '尾连' in str(w.get('col_zhou',''))),
    test_condition('升排+尾吞', lambda w: base_col(w) and w['柱排升'] and '尾吞' in str(w.get('col_zhou',''))),
    test_condition('人排', lambda w: base_col(w) and w['柱排人']),
    test_condition('跌排', lambda w: base_col(w) and w['柱排跌']),
]
print_results('验证3: 柱排形态 (基准=金升+甲乙+ZA<5)', results_col, base_col_ref)

# ============================================================
# 验证4: 盈提示 (分资产类型)
# ============================================================
base_jin_za5 = lambda w: w['WXCD金'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己') and 0 < w['ZA周'] < 5
results_ying = [
    test_condition('盈提示=有', lambda w: base_jin_za5(w) and w['盈提示']),
    test_condition('盈提示=无', lambda w: base_jin_za5(w) and not w['盈提示']),
]
print_results('验证4: 盈提示全量 (基准=金升+甲乙+ZA<5)', results_ying, base_col_ref)

for cat_name in ['宽基指数','指数','行业ETF','个股']:
    cat_weeks = [w for w in all_weeks if w['cat'] == cat_name]
    if not cat_weeks: continue
    b = test_condition(f'{cat_name} 基准', base_jin_za5, cat_weeks)
    r1 = test_condition(f'{cat_name} 盈=有', lambda w: base_jin_za5(w) and w['盈提示'], cat_weeks)
    r2 = test_condition(f'{cat_name} 盈=无', lambda w: base_jin_za5(w) and not w['盈提示'], cat_weeks)
    print_results(f'盈提示-{cat_name}', [r1, r2], b)

# ============================================================
# 验证5: 被移除指标 — 波型 (在最优基础上叠加)
# ============================================================
base_best = lambda w: w['WXCD金'] and w['WXCD升'] and w['WXAB'] in ('甲','乙','己') and 0 < w['ZA周'] < 5 and w['柱排升'] and w['非孕']
base_best_ref = test_condition('最优基准(金升+甲乙+ZA<5+升排+非孕)', base_best)
results_wave = [
    test_condition('波型=龙猪', lambda w: base_best(w) and '龙猪' in w['波型周']),
    test_condition('波型=龙管', lambda w: base_best(w) and '龙管' in w['波型周']),
    test_condition('波型=头正', lambda w: base_best(w) and '头正' in w['波型周']),
    test_condition('波型=震正', lambda w: base_best(w) and '震正' in w['波型周']),
    test_condition('波型=头负/震负', lambda w: base_best(w) and ('头负' in w['波型周'] or '震负' in w['波型周'])),
    test_condition('波型=龙(合并)', lambda w: base_best(w) and ('龙猪' in w['波型周'] or '龙管' in w['波型周'])),
]
print_results('验证5: 波型叠加', results_wave, base_best_ref)

# ============================================================
# 验证6: 被移除指标 — WTAB(用ZA周近似)
# ============================================================
results_wtab = [
    test_condition('WTAB刚交(ZA≤3)', lambda w: base_best(w) and 0 < w['ZA周'] <= 3),
    test_condition('WTAB正交(ZA 3~10)', lambda w: base_best(w) and 3 < w['ZA周'] <= 10),
    test_condition('WTAB久交(ZA>10)', lambda w: base_best(w) and w['ZA周'] > 10),
]
print_results('验证6: WTAB(ZA周近似)叠加', results_wtab, base_best_ref)

# ============================================================
# 验证7: 被移除指标 — 日级别
# ============================================================
results_riduan = [
    test_condition('日层段=持主', lambda w: base_best(w) and w['日层段'] == '持主'),
    test_condition('日层段=买初', lambda w: base_best(w) and w['日层段'] == '买初'),
    test_condition('日层段=持被', lambda w: base_best(w) and w['日层段'] == '持被'),
    test_condition('日层段=卖浮', lambda w: base_best(w) and w['日层段'] == '卖浮'),
]
print_results('验证7a: 日层段叠加', results_riduan, base_best_ref)

results_riji = [
    test_condition('日机警=含漏日', lambda w: base_best(w) and '漏日' in w['日机警']),
    test_condition('日机警=含漏周', lambda w: base_best(w) and '漏周' in w['日机警']),
    test_condition('日机警=含警盈', lambda w: base_best(w) and '警盈' in w['日机警']),
    test_condition('日机警=含警诱', lambda w: base_best(w) and '警诱' in w['日机警']),
    test_condition('日机警=无信号', lambda w: base_best(w) and w['日机警'] in ('','/','无','None')),
]
print_results('验证7b: 日机警叠加', results_riji, base_best_ref)

# ============================================================
# 验证8: 上影线分档
# ============================================================
results_shadow = [
    test_condition('上影占比<1.0%', lambda w: base_best(w) and w['上影占比'] < 1.0),
    test_condition('上影占比1.0~1.5%', lambda w: base_best(w) and 1.0 <= w['上影占比'] < 1.5),
    test_condition('上影占比1.5~2.0%', lambda w: base_best(w) and 1.5 <= w['上影占比'] < 2.0),
    test_condition('上影占比2.0~2.5%', lambda w: base_best(w) and 2.0 <= w['上影占比'] < 2.5),
    test_condition('上影占比≥2.5%', lambda w: base_best(w) and w['上影占比'] >= 2.5),
]
print_results('验证8: 上影线分档', results_shadow, base_best_ref)

# ============================================================
# 汇总: 按成功率排序
# ============================================================
P(f'\n{"="*72}')
P(f'  📊 最终汇总排名 (样本≥30)')
P(f'{"="*72}')
P(f'{"条件":<34} {"样本":>6} {"成功率":>7} {"均收益":>8}')
all_results = results_wxab + results_za + results_col + results_ying + results_wave + results_wtab + results_riduan + results_riji + results_shadow
sorted_results = sorted(all_results + [baseline_all, baseline_jin, base_col_ref, base_best_ref], key=lambda r: -(r['win'] or 0))
for r in sorted_results:
    if r['n'] >= 30:
        win_s = f'{r["win"]:.0f}%' if r.get('win') is not None else '   -'
        ret_s = f'{r["avg_ret"]:.2f}%' if r.get('avg_ret') is not None else '    -'
        P(f'{r["name"]:<34} {r["n"]:>6} {win_s:>7} {ret_s:>8}')

flush_out()
P(f'\n✅ 验证完成，结果 -> {OUT_PATH}')