#!/usr/bin/env python3
"""全自动验证：大盘DXZC/DXZA与个股走势关系"""
import os, shutil, time, csv, tempfile, subprocess
from collections import Counter

SRC_DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba"
XLSM_SRC = r"D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化.xlsm"
CSV_OUT = r"D:\@VSwork\VS昭明计划VBA优化\____temp\大盘个股联动.csv"

def main():
    # 1. 复制 xlsm + 转换 .bas 为 GBK
    tmp_dir = os.path.join(tempfile.gettempdir(), "zhaoming_verify_" + str(int(time.time())))
    os.makedirs(tmp_dir)

    xlsm_copy = os.path.join(tmp_dir, "verify.xlsm")
    shutil.copy2(XLSM_SRC, xlsm_copy)

    gbk_dir = os.path.join(tmp_dir, "bas_gbk")
    os.makedirs(gbk_dir)
    bas_files = sorted([f for f in os.listdir(SRC_DIR) if f.endswith('.bas')])
    for fname in bas_files:
        src_path = os.path.join(SRC_DIR, fname)
        try:
            with open(src_path, 'r', encoding='utf-8') as fh:
                text = fh.read()
            dst_path = os.path.join(gbk_dir, fname)
            with open(dst_path, 'w', encoding='gbk') as fh:
                fh.write(text)
        except:
            continue

    print(f"[1] 已复制 xlsm + 转换 {len(bas_files)} 个 .bas 为 GBK")

    # 2. 导入 .bas + 运行宏
    import win32com.client, pythoncom
    pythoncom.CoInitialize()
    excel = None
    try:
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        wb = excel.Workbooks.Open(xlsm_copy)
        vbproj = wb.VBProject

        import_count = 0
        for fname in bas_files:
            gbk_path = os.path.join(gbk_dir, fname)
            if not os.path.exists(gbk_path):
                continue
            try:
                with open(gbk_path, 'r', encoding='gbk') as fh:
                    first_line = fh.readline().strip()
                if not first_line.startswith('Attribute VB_Name'):
                    continue
                q1 = first_line.find('"')
                q2 = first_line.find('"', q1 + 1)
                mod_name = first_line[q1+1:q2] if q1 > 0 and q2 > q1 else None
                if not mod_name:
                    continue
                for comp in vbproj.VBComponents:
                    if comp.Name == mod_name:
                        vbproj.VBComponents.Remove(comp)
                        break
                vbproj.VBComponents.Import(gbk_path)
                import_count += 1
            except:
                continue
        print(f"[2] 导入 {import_count} 个模块")

        # 3. 运行宏
        print(f"[3] 运行宏 XL算研_展探大盘个股联动 ...")
        try:
            excel.Application.Run("XL算研_展探大盘个股联动")
            time.sleep(5)
        except Exception as e:
            print(f"  宏运行失败: {e}")
            # 尝试用 Application.Run 的另一种方式
            try:
                excel.Application.Run("'verify.xlsm'!XL算研_展探大盘个股联动")
                time.sleep(5)
            except:
                pass

        wb.Close(SaveChanges=False)
        excel.Quit()
    finally:
        if excel:
            pythoncom.CoUninitialize()
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # 4. 分析 CSV
    print(f"[4] 分析数据...")
    if not os.path.exists(CSV_OUT):
        print("CSV 文件不存在，请先手动运行宏 XL算研_展探大盘个股联动")
        return

    with open(CSV_OUT, 'r', encoding='gbk') as f:
        reader = csv.reader(f)
        header = next(reader)
        data = []
        for row in reader:
            if not row or not row[0]:
                continue
            ri_chong = float(row[2]) if len(row) > 2 and row[2] else None
            cang_zhou = row[3] if len(row) > 3 else ""
            dai_zhou = row[4] if len(row) > 4 else ""
            is_wide = row[7] if len(row) > 7 else ""
            cang_first = cang_zhou[0] if cang_zhou else ""
            data.append((row[0], row[1] if len(row) > 1 else "",
                        ri_chong, cang_first, dai_zhou, is_wide))

    print(f"读取 {len(data)} 行数据")

    indexes = [d for d in data if d[5] == "是"]
    stocks = [d for d in data if d[5] != "是"]

    print(f"\n指数: {len(indexes)} 个")
    for idx in indexes:
        print(f"  {idx[0]} {idx[1]} 日冲策分={idx[2]} 仓周类={idx[3]} 月基带周={idx[4]}")
    print(f"个股: {len(stocks)} 个")

    def classify(c):
        return "好" if c in ("金", "银") else ("坏" if c in ("屎", "尿") else "中")

    cls_all = Counter()
    for s in stocks:
        cls_all[classify(s[3])] += 1
    total = sum(cls_all.values())
    print(f"\n个股整体分布:")
    for k in ["好", "中", "坏"]:
        pct = cls_all[k] / total * 100 if total else 0
        print(f"  {k}: {cls_all[k]}({pct:.1f}%)")

    def get_promote(dz):
        return dz[3] if len(dz) >= 4 else ""

    idx_promotes = [get_promote(d[4]) for d in indexes]
    idx_scores = [d[2] for d in indexes if d[2] is not None]
    print(f"\n指数月基带周促动: {idx_promotes}")
    print(f"指数日冲策分: {idx_scores}")

    bad_p = sum(1 for p in idx_promotes if p in ("\u2198", "\u25bd"))  # ↘, ▽
    good_p = sum(1 for p in idx_promotes if p in ("\u25b2", "\u2197"))  # ▲, ↗
    low_s = sum(1 for s in idx_scores if s is not None and s < 50)
    high_s = sum(1 for s in idx_scores if s is not None and s >= 50)

    print(f"\n{'='*50}")
    print(f"方法一: 月基带周促动方向")
    print(f"{'='*50}")
    if bad_p >= 2:
        cls_bad = Counter()
        for s in stocks:
            cls_bad[classify(s[3])] += 1
        print(f"当 {bad_p}/3 指数方向为坏时:")
        for k in ["好", "中", "坏"]:
            print(f"  个股{k}: {cls_bad[k]}({cls_bad[k]/total*100:.1f}%)")
    if good_p >= 2:
        cls_good = Counter()
        for s in stocks:
            cls_good[classify(s[3])] += 1
        print(f"当 {good_p}/3 指数方向为好时:")
        for k in ["好", "中", "坏"]:
            print(f"  个股{k}: {cls_good[k]}({cls_good[k]/total*100:.1f}%)")

    print(f"\n{'='*50}")
    print(f"方法二: 日冲策分(对应DXZC/DXZA)")
    print(f"{'='*50}")
    if low_s >= 2:
        cls_low = Counter()
        for s in stocks:
            cls_low[classify(s[3])] += 1
        print(f"当 {low_s}/3 指数日冲策分<50时:")
        for k in ["好", "中", "坏"]:
            print(f"  个股{k}: {cls_low[k]}({cls_low[k]/total*100:.1f}%)")
    if high_s >= 2:
        cls_high = Counter()
        for s in stocks:
            cls_high[classify(s[3])] += 1
        print(f"当 {high_s}/3 指数日冲策分>=50时:")
        for k in ["好", "中", "坏"]:
            print(f"  个股{k}: {cls_high[k]}({cls_high[k]/total*100:.1f}%)")

    print(f"\n{'='*50}")
    print(f"分析完成")

if __name__ == "__main__":
    main()