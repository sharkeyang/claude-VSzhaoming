"""
回测_算法3_下周冲高_真实走势.py — 验证条件满足后，下周真实最高价是否>本周收盘价

方法：
  1. 找到每周的边界行（涨幅迷周有值）
  2. 记录第N周的条件（WXCD/WXAB/ZA/波型）和收盘价
  3. 记录第N+1周的最高价
  4. 判断：第N+1周最高价 > 第N周收盘价 = 冲高成功
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

def _f(v):
    try: return float(v) if v else 0.0
    except: return 0.0

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
    targets = ['sh000852','sh512480','sz159663','sh515320','sh588000',
               'sz399678','sh600906','sh600109','sz002174','sz300142']
    文件列表 = []
    for f in sorted(os.listdir(算展目录)):
        if f.endswith('.xlsx') and '算展' in f:
            base = f.replace('算展.','').replace('.xlsx','')
            if base in targets:
                文件列表.append(os.path.join(算展目录, f))
    print(f"文件: {len(文件列表)}个")

    # 统计
    stats = {
        '金升_甲乙_ZA大于0': {'成功': 0, '失败': 0, 'total': 0},
        '金升_甲乙_ZA大于0_龙猪': {'成功': 0, '失败': 0, 'total': 0},
        '金升_甲乙_ZA大于0_头正': {'成功': 0, '失败': 0, 'total': 0},
        '银升_甲乙': {'成功': 0, '失败': 0, 'total': 0},
    }

    for fpath in 文件列表:
        fname = os.path.basename(fpath)
        try:
            wb = excel.Workbooks.Open(fpath)
            ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
            ws = wb.Sheets(ld)
            rows = ws.UsedRange.Rows.Count
            print(f"  {fname}...", end=' ', flush=True)

            # 扫描所有行，记录每周数据
            weeks = []  # [{close, high, wxcd, wxab, za, wave, row}, ...]
            prev_close = None  # 上一周的收盘价(即本周的结价周前)

            for r in range(2, rows + 1):
                zf = _f(ws.Cells(r, 39).value)  # 涨幅迷周（有值=周边界）
                if zf == 0.0:
                    continue  # 非周边界行

                wxcd_raw = ws.Cells(r, 88).value
                wxab_raw = ws.Cells(r, 79).value
                za = _f(ws.Cells(r, 282).value)
                wave = str(ws.Cells(r, 80).value or '')
                jj = _f(ws.Cells(r, 36).value)  # 结价周前 = 前周收盘
                df = _f(ws.Cells(r, 37).value)  # 叠幅周 = (本周高-本周低)/前周收

                # 本周收盘价 = 前周收盘 * (1 + 涨幅迷/100)
                close = jj * (1 + zf / 100) if jj > 0 else 0
                # 本周最高价 = 前周收盘 * (1 + 叠幅/100)  [近似，叠幅是最低到最高的总幅度]
                # 更准确：最高价 = 前周收盘 + 叠幅 * 前周收盘 / 100
                high = jj + df * jj / 100 if jj > 0 else 0

                weeks.append({
                    'close': close, 'high': high, 'jj': jj,
                    'wxcd': str(wxcd_raw or ''),
                    'wxab': str(wxab_raw or ''),
                    'za': za, 'wave': wave,
                    'zf': zf, 'df': df,
                    'row': r,
                })

            # 逐周对比：第N周的条件 → 第N+1周的最高价是否>第N周收盘价
            for i in range(len(weeks) - 1):
                w = weeks[i]       # 第N周（信号周）
                nw = weeks[i+1]    # 第N+1周（验证周）

                wxcd = parse_wxcd(w['wxcd'])
                wxab = parse_wxab(w['wxab'])
                is_up = nw['high'] > w['close']  # 第N+1周最高价 > 第N周收盘价

                # 条件1：金升+甲乙+ZA>0
                if wxcd['金'] and wxcd['升'] and wxab in ('甲','乙','己') and w['za'] > 0:
                    stats['金升_甲乙_ZA大于0']['total'] += 1
                    if is_up:
                        stats['金升_甲乙_ZA大于0']['成功'] += 1
                    else:
                        stats['金升_甲乙_ZA大于0']['失败'] += 1

                    # 子条件：波型=龙猪/龙管
                    if '龙' in w['wave']:
                        stats['金升_甲乙_ZA大于0_龙猪']['total'] += 1
                        if is_up:
                            stats['金升_甲乙_ZA大于0_龙猪']['成功'] += 1
                        else:
                            stats['金升_甲乙_ZA大于0_龙猪']['失败'] += 1

                    # 子条件：波型=头正/头负
                    if '头' in w['wave']:
                        stats['金升_甲乙_ZA大于0_头正']['total'] += 1
                        if is_up:
                            stats['金升_甲乙_ZA大于0_头正']['成功'] += 1
                        else:
                            stats['金升_甲乙_ZA大于0_头正']['失败'] += 1

                # 条件2：银升（对比）
                if '银' in w['wxcd'] and '升' in w['wxcd'] and wxab in ('甲','乙','己'):
                    stats['银升_甲乙']['total'] += 1
                    if is_up:
                        stats['银升_甲乙']['成功'] += 1
                    else:
                        stats['银升_甲乙']['失败'] += 1

            wb.Close(False)
            print(f"{len(weeks)}周")
        except Exception as e:
            print(f"错误: {e}")
            try: wb.Close(False)
            except: pass

    # 输出结果
    print("\n" + "="*70)
    print("  算法③真实走势回测结果")
    print("  定义：第N周满足条件 → 第N+1周最高价 > 第N周收盘价 = 冲高成功")
    print("="*70)

    items = [
        ("金升+甲乙+ZA>0（全部）", stats['金升_甲乙_ZA大于0']),
        ("  + 波型=龙猪/龙管    ", stats['金升_甲乙_ZA大于0_龙猪']),
        ("  + 波型=头正/头负    ", stats['金升_甲乙_ZA大于0_头正']),
        ("银升+甲乙（对比）     ", stats['银升_甲乙']),
    ]

    for label, s in items:
        total = s['total']
        if total > 0:
            ok = s['成功']
            pct = ok / total * 100
            tag = "✅" if pct >= 80 else ("⚠️" if pct >= 60 else "❌")
            print(f"  {label}: {ok}/{total}={pct:.0f}% {tag}")
        else:
            print(f"  {label}: 无数据")

    print("\n✅ 完成")

if __name__ == "__main__":
    main()