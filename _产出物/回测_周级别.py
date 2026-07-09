"""
回测_周级别.py — 严格按日→周转换后重新验证三个算法

方法：
  1. 逐行读取日数据，按日期标记每周的第一天
  2. 用每日涨跌幅(C5)计算每日收盘价
  3. 每周的最后一天 = 当周收盘，取周级指标(WXCD/WXAB/ZA)
  4. 逐周对比：第N周条件 → 第N+1周收益
"""
import os, sys, datetime
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
    files = []
    for f in sorted(os.listdir(D)):
        if f.endswith('.xlsx') and '算展.' in f:
            base = f.replace('算展.','').replace('.xlsx','')
            if base in ['sh000852','sh512480','sz159663','sh515320','sh588000',
                        'sz399678','sz159919','sh000001']:
                files.append(os.path.join(D, f))
    print(f"文件: {len(files)}个")

    all_data = []

    for fpath in files:
        fname = os.path.basename(fpath)
        try:
            wb = excel.Workbooks.Open(fpath)
            ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
            ws = wb.Sheets(ld); rows = ws.UsedRange.Rows.Count
            # 读取日期(C4=1), 涨跌幅(C5=2), 周级指标(C36=33,C79=76,C80=77,C82=79,C85=82,C88=85,C282=279)
            # 读取C4~C310（需要C282的ZA数据）
            arr = ws.Range(ws.Cells(2, 4), ws.Cells(rows, 310)).Value
            wb.Close(False)

            # 逐日处理，按周分组
            prev_close = None
            week_rows = []  # 存放同一周的所有行
            weeks = []      # 存放每周汇总

            for r in range(len(arr)):
                row = arr[r]
                date_val = row[0]  # C4 = 日期
                chg = _f(row[1])   # C5 = 涨跌幅日

                if date_val is None: continue

                # 日期转为datetime
                if isinstance(date_val, datetime.datetime):
                    dt = date_val
                elif isinstance(date_val, (int, float)):
                    dt = datetime.datetime(1899, 12, 30) + datetime.timedelta(days=int(date_val))
                else:
                    continue

                # 周一 = 新一周开始
                if dt.weekday() == 0 and week_rows:
                    # 结束上一周，开始新一周
                    weeks.append(week_rows)
                    week_rows = []

                week_rows.append({
                    'date': dt, 'chg': chg,
                    'jj': _f(row[32]),   # C36
                    'wxcd': str(row[81] or ''),  # C88 = 84-4+1=81
                    'wxab': str(row[72] or ''),  # C79 = 76-4=72
                    'za': _f(row[278]) if len(row) > 278 else 0,  # C282 = 278
                    'wave': str(row[73] or ''),  # C80
                    'col': str(row[75] or ''),   # C82
                    'profit': str(row[78] or ''),# C85
                })

            if week_rows:
                weeks.append(week_rows)

            # 逐周计算
            for i in range(len(weeks)):
                wk = weeks[i]
                # 本周收盘 = 从结价周前开始，累加每日涨跌幅
                jj = wk[0]['jj'] if wk[0]['jj'] else 0
                close = jj
                for d in wk:
                    if d['chg'] is not None:
                        close *= (1 + d['chg'] / 100)

                # 周级指标取自最后一行（行末）
                last = wk[-1]
                wxcd = parse_wxcd(last['wxcd'])
                wxab = parse_wxab(last['wxab'])
                za = last['za']

                all_data.append({
                    'close': close, 'jj': jj,
                    'wxcd_gold': wxcd['金'], 'wxcd_up': wxcd['升'],
                    'wxab': wxab, 'za': za,
                    'wave': last['wave'], 'col': last['col'], 'profit': last['profit'],
                    'weeks': len(wk), 'date': wk[0]['date'],
                })

            print(f"  {fname}: {len(weeks)}周", flush=True)
        except:
            try: wb.Close(False)
            except: pass

    # 逐周对比
    print(f"\n总周数: {len(all_data)}")
    stats = {'up': [], 'down': [], 'gold_ab': [], 'gold_ab_next': []}

    for i in range(len(all_data) - 1):
        w = all_data[i]       # 第N周
        nw = all_data[i + 1]  # 第N+1周
        next_ret = (nw['close'] - w['close']) / w['close'] * 100 if w['close'] > 0 else 0

        # 检查金升+甲乙+ZA>0条件
        if w['wxcd_gold'] and w['wxcd_up'] and w['wxab'] in ('甲','乙','己') and w['za'] > 0:
            stats['gold_ab'].append(next_ret)

    if stats['gold_ab']:
        avg = sum(stats['gold_ab']) / len(stats['gold_ab'])
        pos = sum(1 for r in stats['gold_ab'] if r > 0) / len(stats['gold_ab']) * 100
        print(f"\n金升+甲乙+ZA>0 → 下周收益率:")
        print(f"  样本: {len(stats['gold_ab'])}周")
        print(f"  平均: {avg:.2f}%")
        print(f"  上涨率: {pos:.0f}%")
        print(f"  中位: {sorted(stats['gold_ab'])[len(stats['gold_ab'])//2]:.2f}%")

    print("\n✅ 完成")

if __name__ == "__main__":
    main()