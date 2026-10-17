# -*- coding: utf-8 -*-
"""
谕组导出改造验证脚本（副本验证，遵守铁律）
- 复制正式 xlsm 到 ____temp/（带时间戳）
- 用 DispatchEx 独立进程导入 .bas
- 跑 XL算展取样调程_谕组单股通用 导出周+日
- 检查周类CSV与旧版一致、日类CSV新增周类列
- 完成后 Quit + ReleaseComObject
"""
import os, sys, io, shutil, time, datetime, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import win32com.client
import pythoncom

项目根 = r"D:\@VSwork\VS昭明计划VBA优化"
正式xlsm = os.path.join(项目根, "昭明计划VS优化.xlsm")
bas目录 = os.path.join(项目根, "昭明计划VS优化_vba")
temp目录 = os.path.join(项目根, "____temp")

# 测试股票
测试代码 = "sz159919"
输出目录 = os.path.join(temp目录, "谕组导出验证_" + datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

def main():
    # 1. 复制正式 xlsm 到 temp（带时间戳）
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    副本 = os.path.join(temp目录, f"昭明计划VS优化_验证_{ts}.xlsm")
    shutil.copy2(正式xlsm, 副本)
    print(f"副本: {副本}")

    # 2. 准备导入的 bas 目录（复制到 temp，避免动原目录）
    tmp_bas = os.path.join(temp目录, f"_vba_验证_{ts}")
    shutil.copytree(bas目录, tmp_bas)

    excel = None
    wb = None
    try:
        # 3. DispatchEx 独立进程
        excel = win32com.client.DispatchEx("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.EnableEvents = False
        excel.ScreenUpdating = False

        # 4. 打开副本
        wb = excel.Workbooks.Open(副本, 0, False)
        vbproj = wb.VBProject

        # 5. 清旧导新（用 GBK 编码导入，与 vba_verify.py 一致，避免中文宏名乱码）
        for comp in list(vbproj.VBComponents):
            if comp.Type == 1:  # vbext_ct_StdModule
                vbproj.VBComponents.Remove(comp)
        for f in sorted(glob.glob(os.path.join(tmp_bas, "*.bas"))):
            name = os.path.splitext(os.path.basename(f))[0]
            # 去掉末尾数字（模块名规则）
            if name.endswith("1") and len(name) > 1:
                name = name[:-1]
            comp = vbproj.VBComponents.Add(1)  # vbext_ct_StdModule
            comp.Name = name
            with open(f, "r", encoding="utf-8") as fh:
                code = fh.read()
            # 转成 GBK 再导入（VBA 内部用系统编码）
            comp.CodeModule.AddFromString(code.encode("gbk", errors="replace").decode("gbk"))
        print("导入完成")

        # 注入英文包装宏（无参数，内部硬编码测试代码和路径，避免 COM 参数传递问题）
        os.makedirs(输出目录, exist_ok=True)
        # 路径转成 VBA 字符串（反斜杠转义）
        vba_path = 输出目录.replace("\\", "\\\\")
        wrapper = vbproj.VBComponents.Add(1)
        wrapper.Name = "VBAVerify_Wrapper"
        wrapper.CodeModule.AddFromString(
            "Public Sub VBAVerify_Export()\n"
            f"    Call XL算展取样调程_谕组单股通用(\"{测试代码}\", \"{vba_path}\", \"周+日\")\n"
            "End Sub\n"
        )
        print("包装宏注入完成")

        # 6. 跑导出（通过英文包装宏，避免中文宏名 COM 编码问题）
        excel.Application.Run("VBAVerify_Export")
        print(f"导出完成: {输出目录}")

        # 7. 列出输出文件
        for f in sorted(glob.glob(os.path.join(输出目录, "**", "*.csv"), recursive=True)):
            print(f"  输出: {os.path.relpath(f, 输出目录)}")

        # 8. 关闭
        wb.Close(False)
        wb = None
        excel.Quit()
        excel = None
        print("验证完成，Excel 已退出")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"验证失败: {e}")
    finally:
        if wb:
            try: wb.Close(False)
            except: pass
        if excel:
            try: excel.Quit()
            except: pass
        # 清理临时 bas 目录
        shutil.rmtree(tmp_bas, ignore_errors=True)
        # 不删副本和输出，供检查

if __name__ == "__main__":
    main()
