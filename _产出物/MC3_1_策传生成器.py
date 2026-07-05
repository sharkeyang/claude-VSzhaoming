"""小传.py — 从复波A/B读取股票数据，生成小传文件"""
import openpyxl, sys
from datetime import date

XLSM = r'D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化.xlsm'

def g(row, i):
    if i is None or i >= len(row): return ''
    v = row[i]
    if v is None: return ''
    return str(v).replace('\n','').replace('_x000D_','').replace('_x000A_','').strip()

def main(stock_list=None):
    wb = openpyxl.load_workbook(XLSM, data_only=True, read_only=True)
    sheets = ['.复波A', '.复波B']

    lines = []
    today = date.today().strftime('%Y%m%d')
    lines.append(f'# 小传{today}')
    lines.append(f'> 生成日期: {today} | 数据源: .复波A + .复波B')
    lines.append('')
    lines.append('---')
    lines.append('')

    total = 0
    for sname in sheets:
        ws = wb[sname]
        for row in ws.iter_rows(min_row=2, values_only=True):
            cid = row[0]
            if cid is None: continue
            cid = str(cid).strip()
            if not cid: continue
            if stock_list is not None and cid not in stock_list: continue
            if not cid[0].isalpha(): continue
            if not (cid.startswith('sz') or cid.startswith('sh')): continue
            total += 1

            nam = g(row, 1)
            wxcd = g(row, 87)
            dxab = g(row, 89)
            rizhou = g(row, 88)
            zhupai_r = g(row, 95)
            zhuxing_dja = g(row, 93)
            zhuxing_wja = g(row, 80)
            boxing_r = g(row, 90)
            chonggao = g(row, 86)
            lou = g(row, 92)
            cangzhu = g(row, 22)
            jinchi = g(row, 24)
            dxze = g(row, 273)

            lines.append(f'## {cid} {nam}')
            lines.append('')

            # WXCD 判定
            if '金' in wxcd: wxcd_ev = '✅ 金'
            elif '银' in wxcd: wxcd_ev = '⚠️ 银（小仓试错）'
            elif any(x in wxcd for x in ['屎','尿','唏嘘']): wxcd_ev = '❌ '+wxcd[:15]
            else: wxcd_ev = '🟡 '+wxcd[:20]

            # DXAB 判定
            if '甲' in dxab: dxab_ev = '✅ 甲（正交持续）'
            elif '乙' in dxab: dxab_ev = '✅ 乙（正交持续）'
            elif '己' in dxab: dxab_ev = '⚠️ 己（将正交，警惕诱多）'
            else: dxab_ev = '🔴 '+dxab[:15] if dxab else '—'

            # DXZE＞0 判定
            dxze_ok = bool(dxze and dxze != '—' and dxze != '0' and dxze != '')

            # 开仓自问
            r1 = '✅' if ('金' in wxcd or '银' in wxcd) else ('❌' if any(x in wxcd for x in ['屎','尿','唏嘘']) else '🟡')
            r2 = '✅' if rizhou.startswith(('金','银')) else '🟡' if rizhou else '❓'
            r3 = '✅' if dxze_ok else '❌'
            r5 = '✅'
            r7 = '⏳'
            r8 = '✅'

            lines.append(f'### ✅ 开仓自问')
            lines.append(f'| # | 问题 | 结果 |')
            lines.append(f'|:--|:-----|:----:|')
            lines.append(f'| ① | WXCD=金/银 | {r1} |')
            lines.append(f'| ② | 前周WXZC＞0 | {r2} |')
            lines.append(f'| ③ | DXZE＞0 | {r3} |')
            lines.append(f'| ⑤ | 防日诱 | {r5} |')
            lines.append(f'| ⑦ | 尾盘操作(14:50-15:00) | {r7} |')
            lines.append(f'| ⑧ | 单向二戒 | {r8} |')

            if '金' in wxcd or '银' in wxcd:
                if '金' in rizhou or '银' in rizhou:
                    if dxze_ok:
                        lines.append(f'\n> 🟢 全程绿灯，推荐操作')
                    elif '升' in zhupai_r:
                        lines.append(f'\n> 🟡 DXZE未达标，但柱排升链，信号面待确认')
                    else:
                        lines.append(f'\n> 🟡 注意：DXZE未达标')
                else:
                    lines.append(f'\n> 🔴 日周联动偏弱')
            else:
                lines.append(f'\n> 🔴 WXCD不达标，放弃')
            lines.append('')

            # 趋势
            lines.append(f'### 📊 趋势')
            lines.append(f'| 指标 | 值 |')
            lines.append(f'|:-----|:----|')
            lines.append(f'| WXCD | `{wxcd}` |')
            lines.append(f'| DXAB | `{dxab}` |')
            lines.append(f'| 日周联动 | `{rizhou}` |')
            lines.append(f'| 柱排日 | `{zhupai_r}` |')
            lines.append(f'| 柱型DJA | `{zhuxing_dja}` |')
            lines.append(f'| 柱型WJA | `{zhuxing_wja}` |')
            lines.append(f'| 波型日 | `{boxing_r}` |')
            lines.append(f'| DXZE | `{dxze}` |')
            lines.append('')

            # 信号
            lines.append(f'### 🔔 信号')
            signals = []
            if chonggao and chonggao != '—': signals.append(f'下周冲高 `{chonggao}`')
            if lou and lou != '—': signals.append(f'漏提示 `{lou}`')
            if cangzhu and cangzhu != '—': signals.append(f'仓主 `{cangzhu}`')
            if jinchi and jinchi != '—': signals.append(f'今池 `{jinchi}`')
            for s in signals: lines.append(f'- {s}')
            if not signals: lines.append('- 无突出信号')
            lines.append('')

            # 场景
            lines.append(f'### 🏷️ 场景')
            scenes = []
            if '金' in wxcd or '银' in wxcd:
                if chonggao and chonggao != '—': scenes.append('下周冲高')
                if '升' in zhupai_r: scenes.append('下日冲高')
                if dxze_ok: scenes.append('基仓持有')
                if lou and lou != '—': scenes.append('日漏浮仓')
            lines.append('、'.join(scenes) if scenes else '—')
            lines.append('')
            lines.append('---')
            lines.append('')

    outpath = f'd:\\@VSwork\\VS昭明计划VBA优化\\小传{today}.md'
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    print(f'✅ 生成: {outpath}  ({len(lines)}行, {total}只股票)')

if __name__ == '__main__':
    codes = sys.argv[1:] if len(sys.argv) > 1 else None
    if codes: print(f'请求代码: {codes}')
    main(codes)
