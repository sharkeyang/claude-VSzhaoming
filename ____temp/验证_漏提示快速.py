# -*- coding: utf-8 -*-
"""快速提取算展xlsx中的漏提示+HR列 - 直接解析XML"""
import zipfile, xml.parsers.expat, os, glob, time, sys, re

BASE = r'昭明算展/算展0724'
files = sorted(glob.glob(os.path.join(BASE, '算展.*.xlsx')))
print(f'共 {len(files)} 个文件')

总_有漏 = 0; 总_无漏 = 0; 有漏_HR2 = 0; 无漏_HR2 = 0; 有漏_HR3 = 0; 无漏_HR3 = 0
有漏_sum = 0.0; 无漏_sum = 0.0
子类统计 = {}
正文件 = 0; 负文件 = 0; 可统计文件 = 0
t0 = time.time()

for fi, f in enumerate(files):
    try:
        with zipfile.ZipFile(f, 'r') as z:
            # 找sheet1的xml
            sheet_xml = [n for n in z.namelist() if 'xl/worksheets/sheet' in n and n.endswith('.xml')]
            if not sheet_xml: continue
            # 找shared strings
            shared = None
            if 'xl/sharedStrings.xml' in z.namelist():
                ss_raw = z.read('xl/sharedStrings.xml').decode('utf-8', errors='replace')
                shared = re.findall(r'<t[^>]*>([^<]+)</t>', ss_raw)

            xml_data = z.read(sheet_xml[0]).decode('utf-8', errors='replace')

            # 解析行
            rows = re.findall(r'<row[^>]*>(.*?)</row>', xml_data, re.DOTALL)
            if not rows: continue

            file_有漏=0; file_无漏=0; file_有HR2=0; file_无HR2=0

            for ri, row_xml in enumerate(rows):
                if ri == 0:  # 标题行，找列索引
                    cells = re.findall(r'<c[^>]*>(.*?)</c>', row_xml, re.DOTALL)
                    漏i = None; HRi = None
                    for ci, cell in enumerate(cells):
                        v = re.search(r'<v>([^<]+)</v>', cell)
                        if v:
                            val = v.group(1)
                            if shared and val.isdigit() and int(val) < len(shared):
                                val = shared[int(val)]
                            if '漏提示' in str(val): 漏i = ci
                            if val == 'HR': HRi = ci
                    continue

                # 数据行
                cells = re.findall(r'<c[^>]*>(.*?)</c>', row_xml, re.DOTALL)
                if max(漏i, HRi) >= len(cells): continue

                vals = []
                for ci in range(max(漏i, HRi) + 1):
                    v = re.search(r'<v>([^<]+)</v>', cells[ci]) if ci < len(cells) else None
                    if v:
                        val = v.group(1)
                        if shared and val.isdigit() and int(val) < len(shared):
                            val = shared[int(val)]
                        vals.append(val)
                    else:
                        vals.append(None)

                if len(vals) <= max(漏i, HRi): continue
                漏v = vals[漏i] if 漏i < len(vals) else None
                HRv = vals[HRi] if HRi < len(vals) else None
                if HRv is None: continue
                try: HRv = float(HRv)
                except: continue

                if 漏v and str(漏v).strip():
                    file_有漏 += 1; 有漏_sum += HRv
                    if HRv > 2: file_有HR2 += 1; 有漏_HR2 += 1
                    if HRv > 3: 有漏_HR3 += 1
                    for 词 in ['上持','上漏','e漏','首防诱','被','丙漏','鼎']:
                        if 词 in str(漏v): 子类统计[词] = 子类统计.get(词,0) + 1
                else:
                    file_无漏 += 1; 无漏_sum += HRv
                    if HRv > 2: file_无HR2 += 1; 无漏_HR2 += 1
                    if HRv > 3: 无漏_HR3 += 1

            总_有漏 += file_有漏; 总_无漏 += file_无漏
            if file_有漏 >= 30 and file_无漏 >= 30:
                可统计文件 += 1
                if file_有HR2/file_有漏 > file_无HR2/file_无漏: 正文件 += 1
                else: 负文件 += 1
    except Exception as e:
        print(f'  {f}: {e}', flush=True)

    if (fi+1) % 5 == 0:
        print(f'  {fi+1}/{len(files)} ({time.time()-t0:.0f}s)', flush=True)

总 = 总_有漏 + 总_无漏
print(f'\n总行: {总:,} (耗时 {time.time()-t0:.0f}s)')
print(f'有漏: n={总_有漏:,} P(HR>2)={有漏_HR2/总_有漏:.1%} P(HR>3)={有漏_HR3/总_有漏:.1%} 均HR={有漏_sum/总_有漏:.2f}%')
print(f'无漏: n={总_无漏:,} P(HR>2)={无漏_HR2/总_无漏:.1%} P(HR>3)={无漏_HR3/总_无漏:.1%} 均HR={无漏_sum/总_无漏:.2f}%')
print(f'差异: P(HR>2)={有漏_HR2/总_有漏-无漏_HR2/总_无漏:+.1%}  P(HR>3)={有漏_HR3/总_有漏-无漏_HR3/总_无漏:+.1%}')
print(f'文件稳定性: {正文件}正 {负文件}负 ({正文件/(正文件+负文件)*100:.0f}%正向) 可统计{可统计文件}个')
print(f'子类分布:')
for 词, n in sorted(子类统计.items(), key=lambda x:-x[1]):
    print(f'  {词}: {n:,}')