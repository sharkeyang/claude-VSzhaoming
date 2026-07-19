"""
回测_算法12_四域WXZC_v2.py — 用真实周收盘价验证

方法：对比连续两周的结价周前计算真实周收益率
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

def _f(v):
    try: return float(v) if v else None
    except: return None

def parse_wxcd(s):
    s = str(s or '')
    return {'金': '金' in s, '银': '银' in s, '升': '升' in s}

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
    targets = ['sh000001','sh000852','sh512480','sz159663','sh515320','sh588000',
               'sz399678','sh600906','sh600109','sz002174','sz300142','sz159919']
    文件列表 = []
    for f in sorted(os.listdir(算展目录)):
        if f.endswith('.xlsx') and '算展' in f:
            base = f.replace('算展.','').replace('.xlsx','')
            if base in targets:
                文件列表.append(os.path.join(算展目录, f))
    print(f"文件: {len(文件列表)}个")

    stats = {'多长':[],'多被':[],'空看':[],'空长':[]}
    detail = {'金升+甲乙+ZA>0':[],'金升+其他':[],'银升+甲乙':[],'其他':[]}

    for fpath in 文件列表:
        fname = os.path.basename(fpath)
        try:
            wb = excel.Workbooks.Open(fpath)
            ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
            ws = wb.Sheets(ld)
            rows = ws.UsedRange.Rows.Count
            print(f"  {fname}...", end=' ', flush=True)

            # 收集每周的结价和条件（去重：同一周只取一行）
            weekly = []
            last_jj = None
            for r in range(2, rows + 1):
                jj = _f(ws.Cells(r, 36).value)  # 结价周前
                if jj is None:
                    continue
                # 同一周内结价周前不变，跳过重复行
                if last_jj is not None and abs(jj - last_jj) < 0.001:
                    continue
                last_jj = jj  # 非周数据

                weekly.append({
                    'close_prev': jj,  # 本周开盘价 = 前周收盘
                    'sy': str(ws.Cells(r, 310).value or ''),
                    'wxcd': str(ws.Cells(r, 88).value or ''),
                    'wxab': str(ws.Cells(r, 79).value or ''),
                    'za': _f(ws.Cells(r, 282).value) or 0,
                    'row': r,
                })

            # 逐周计算收益率
            weeks_used = 0
            for i in range(len(weekly) - 1):
                w = weekly[i]       # 第N周
                nw = weekly[i+1]    # 第N+1周
                # 第N周收盘价 = 第N+1周的结价周前
                close_n = nw['close_prev']
                close_n_minus_1 = w['close_prev']
                if close_n_minus_1 <= 0:
                    continue
                ret = (close_n - close_n_minus_1) / close_n_minus_1 * 100
                weeks_used += 1

                sy = w['sy']
                if sy in stats:
                    stats[sy].append(ret)

                wxcd = parse_wxcd(w['wxcd'])
                wxab = parse_wxab(w['wxab'])
                if wxcd['金'] and wxcd['升'] and wxab in ('甲','乙','己') and w['za'] > 0:
                    detail['金升+甲乙+ZA>0'].append(ret)
                elif wxcd['金'] and wxcd['升']:
                    detail['金升+其他'].append(ret)
                elif '银' in w['wxcd'] and '升' in w['wxcd'] and wxab in ('甲','乙','己'):
                    detail['银升+甲乙'].append(ret)
                else:
                    detail['其他'].append(ret)

            wb.Close(False)
            print(f"{weeks_used}周")
        except Exception as e:
            print(f"错误: {e}")
            try: wb.Close(False)
            except: pass

    # 输出结果
    print("\n" + "="*70)
    print("  四域 vs 真实周收益率")
    print("="*70)
    print(f"{'分类':>6} {'样本':>6} {'平均':>8} {'中位':>8} {'上涨':>8} {'上涨率':>8}")
    print("-"*55)
    for k in ['多长','多被','空看','空长']:
        v = stats[k]
        if v:
            avg = sum(v)/len(v)
            mid = sorted(v)[len(v)//2]
            pos = sum(1 for x in v if x > 0)
            neg = sum(1 for x in v if x < 0)
            print(f"{k:>6} {len(v):>6} {avg:>7.2f}% {mid:>7.2f}% {pos:>6} {pos/len(v)*100:>5.0f}%")

    print("\n" + "="*70)
    print("  WXCD+WXAB+ZA vs 真实周收益率")
    print("="*70)
    print(f"{'条件':>16} {'样本':>6} {'平均':>8} {'中位':>8} {'上涨率':>8}")
    print("-"*55)
    for k in ['金升+甲乙+ZA>0','金升+其他','银升+甲乙','其他']:
        v = detail[k]
        if v:
            avg = sum(v)/len(v)
            mid = sorted(v)[len(v)//2]
            pos = sum(1 for x in v if x > 0)
            neg = sum(1 for x in v if x < 0)
            print(f"{k:>16} {len(v):>6} {avg:>7.2f}% {mid:>7.2f}% {pos/len(v)*100:>5.0f}%")

    print("\n✅ 完成")

if __name__ == "__main__":
    main()