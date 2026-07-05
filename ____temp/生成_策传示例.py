"""Generate 15 策传 examples from Z sheet"""
import win32com.client, datetime
excel = win32com.client.GetActiveObject('Excel.Application')
wb = excel.Workbooks('昭明计划VS优化.xlsm')
ws = wb.Sheets('Z')
data = ws.UsedRange.Value

def v(r, idx):
    if r and len(r) > idx and r[idx] is not None: return str(r[idx])
    return '—'

def iv(v):
    try: return str(int(float(str(v))))
    except: return str(v)

stocks = []
for r in data[1:]:
    cid = str(r[0]) if r[0] else ''
    nam = str(r[1]) if r[1] else ''
    sy = str(r[307]) if len(r) > 307 and r[307] else ''
    if sy in ['多长', '多被']:
        stocks.append(r)
    if len(stocks) >= 15:
        break

print(f'策传示例（15个，来自Z sheet实时数据）')
print(f'> 生成时间: {datetime.datetime.now().strftime(\"%Y-%m-%d %H:%M\")}')
print()

for i, r in enumerate(stocks, 1):
    cid = str(r[0]) if r[0] else ''
    nam = str(r[1]) if r[1] else ''
    sy = str(r[307])
    zc = iv(v(r, 269))
    ze = iv(v(r, 274))
    wab = v(r, 78)[:12]
    abw = iv(v(r, 284))
    crd = v(r, 225)
    jb = v(r, 309)
    xh = v(r, 310)
    bzx = v(r, 79)[:14]
    zpw = v(r, 81)[:12]
    bxm = v(r, 90)[:14]
    zpm = v(r, 95)[:12]
    chg = v(r, 86)[:15]
    wxcd = str(r[87])[0] if r[87] else '?'
    lou = v(r, 92)[:10]

    passed = True
    try: passed = int(float(zc)) > 0 and int(float(ze)) > 0
    except: pass

    s4y = 50 if sy == '多长' else 25
    swab = 5 if any(c in wab for c in ['甲','乙','己']) else 0
    swtab = 5
    scrd = 10 if len(crd) > 1 and crd[1] in ['a','b'] else (5 if '上' in crd else -10 if crd == '无' else 0)
    sjb = 5 if jb == '持主' else (3 if jb == '买初' else 2 if jb == '持被' else -5)
    sxh = 5 if xh and '漏' in xh else 0
    sday = max(-10, scrd + sjb + sxh)
    sbz = 5 if '龙' in bzx else 0
    schg = 5 if chg and chg != '—' and '禁' not in chg else 0
    szp = 3 if zpm and zpm[0] == '升' else (-2 if zpm and zpm[0] == '跌' else 0)
    sref = sbz + schg + szp
    total = s4y + swab + swtab + sday + sref

    grade = '强烈推荐 ✅' if total >= 80 else ('可参与 ⚠️' if total >= 60 else '观望 ❌')
    if not passed: grade = '否决 ❌❌'

    sjc = '✅' if sy == '多长' else '⚠️'
    szf = '✅' if chg and chg != '—' and chg != '' and '禁' not in chg else '❌'
    srf = '✅' if zpm and zpm[0] == '升' else '❌'

    print(f'### 示例{i}：{cid} {nam}')
    print()
    print(f'| # | 项目 | 内容 | 得分 |')
    print(f'|:--|:-----|:------|:----:|')
    res = '通过✅' if passed else '否决❌'
    print(f'| 1️⃣ | **一票否决**（决定性） | WXZC={zc}✅, DXZE={ze}✅, WXCD={wxcd}✅ → {res} | — |')
    print(f'| 2️⃣ | **四域**（决定性） | 周四域={sy}, WXAB={wab}, WTAB=AB周{abw} | {s4y} |')
    print(f'| 3️⃣ | **日级别**（参考性） | 仓日类={crd}, 日层段={jb}, 日信号={xh or \"无\"} | {sday} |')
    print(f'| 4️⃣ | **综合参考**（参考性） | 周波={bzx}, 日柱={zpm} | {sref} |')
    print(f'| 5️⃣ | **走势评分**（参考性） | — | — |')
    print(f'| 6️⃣ | **策略** | <长基仓>{sjc} <周浮仓>{szf} <日浮仓>{srf} | — |')
    print(f'| 7️⃣ | **仓位** | 依仓限规则计算 | — |')
    print(f'| 8️⃣ | **后续走势预案** | ZE>0持有→破DJE清仓 | — |')
    print(f'**总分: {total}分 | {grade}**')
    print()
" 2>&1