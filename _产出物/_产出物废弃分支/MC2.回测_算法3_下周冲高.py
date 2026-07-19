"""
回测_算法3_下周冲高.py v3 — 含波型过滤
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))

def _f(v):
    try: return float(v) if v else 0.0
    except: return 0.0

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
    targets = ['sh000852','sh512480','sz159663','sh515320','sh588000',
               'sz399678','sh600906','sh600109','sz002174','sz300142']
    文件列表 = []
    for f in sorted(os.listdir(算展目录)):
        if f.endswith('.xlsx') and '算展' in f:
            base = f.replace('算展.','').replace('.xlsx','')
            if base in targets:
                文件列表.append(os.path.join(算展目录, f))
    print(f"文件: {len(文件列表)}个")

    # 回测计数器
    stats = {
        '金升_甲_乙_all': {'hit': 0, 'total': 0},
        '金升_甲_乙_wave_dragon': {'hit': 0, 'total': 0},
        '金升_甲_乙_wave_head': {'hit': 0, 'total': 0},
        '银升_甲_乙_all': {'hit': 0, 'total': 0},
    }

    for fpath in 文件列表:
        fname = os.path.basename(fpath)
        try:
            wb = excel.Workbooks.Open(fpath)
            ld = [s.Name for s in wb.Sheets if s.Name.startswith('LD')][0]
            ws = wb.Sheets(ld)
            rows = ws.UsedRange.Rows.Count
            print(f"  {fname}...", end=' ', flush=True)

            for r in range(2, rows + 1):
                wxcd_raw = ws.Cells(r, 88).value
                wxab_raw = ws.Cells(r, 79).value
                za = _f(ws.Cells(r, 282).value)
                xzg = str(ws.Cells(r, 87).value or '')
                wave = str(ws.Cells(r, 80).value or '')

                if not wxcd_raw or not wxab_raw:
                    continue
                wxcd = parse_wxcd(wxcd_raw)
                wxab = parse_wxab(wxab_raw)

                # 基础条件：WXCD=金升 + WXAB甲/乙/己 + ZA>0
                if wxcd['金'] and wxcd['升'] and wxab in ('甲','乙','己') and za > 0:
                    stats['金升_甲_乙_all']['total'] += 1
                    if xzg.strip():
                        stats['金升_甲_乙_all']['hit'] += 1

                    # 波型过滤：龙猪/龙管
                    if '龙' in wave:
                        stats['金升_甲_乙_wave_dragon']['total'] += 1
                        if xzg.strip():
                            stats['金升_甲_乙_wave_dragon']['hit'] += 1

                    # 波型过滤：头正/头负
                    if '头' in wave:
                        stats['金升_甲_乙_wave_head']['total'] += 1
                        if xzg.strip():
                            stats['金升_甲_乙_wave_head']['hit'] += 1

                # 对比：银升条件
                if wxcd['银'] and wxcd['升'] and wxab in ('甲','乙','己') and za > 0:
                    stats['银升_甲_乙_all']['total'] += 1
                    if xzg.strip():
                        stats['银升_甲_乙_all']['hit'] += 1

            wb.Close(False)
            print(f"done")
        except Exception as e:
            print(f"错误: {e}")
            try: wb.Close(False)
            except: pass

    # 输出结果
    print("\n" + "="*70)
    print("  算法③回测结果")
    print("="*70)

    results = [
        ("金升+甲乙+ZA>0（全部）", stats['金升_甲_乙_all']),
        ("  + 波型=龙猪/龙管    ", stats['金升_甲_乙_wave_dragon']),
        ("  + 波型=头正/头负    ", stats['金升_甲_乙_wave_head']),
        ("银升+甲乙+ZA>0（对比)", stats['银升_甲_乙_all']),
    ]

    for label, s in results:
        hit, total = s['hit'], s['total']
        if total > 0:
            pct = hit / total * 100
            tag = "✅" if pct >= 85 else ("⚠️" if pct >= 60 else "❌")
            print(f"  {label}: {hit}/{total}={pct:.0f}% {tag}")
        else:
            print(f"  {label}: 无数据")

    print("\n✅ 完成")

if __name__ == "__main__":
    main()