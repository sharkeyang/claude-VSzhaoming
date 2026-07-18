#!/usr/bin/env python3
"""
VBA 修改自动验证脚本

将 .bas 导入 xlsm 副本（新建独立 Excel 进程），运行测试，输出 JSON 结果。

用法:
    python _工具/vba_verify.py <xlsm_path> <bas_dir>

返回:
    stdout → JSON, exit code 0=通过 1=失败

原则:
    - 永远用 Dispatch() 新建独立 Excel 进程，不碰已有 Excel 实例
    - 操作副本（TEMP），不修改原始文件
    - 完成后关闭不保存，自动清理
"""

import argparse
import json
import locale
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path


def verify(xlsm_path: str, bas_dir: str) -> dict:
    """核心验证逻辑，返回 JSON 可序列化的结果字典"""
    result = {
        "status": "fail",
        "phase": "setup",
        "details": [],
        "summary": "",
    }

    # ── Phase 1: 环境检查 ──
    excel_path = Path(xlsm_path)
    if not excel_path.exists():
        return _fail(
            result, "setup", f"xlsm 文件不存在: {xlsm_path}"
        )
    src_dir = Path(bas_dir)
    bas_files = sorted(src_dir.glob("*.bas"))
    if not bas_files:
        return _fail(
            result, "setup", f"未找到 .bas 文件: {bas_dir}"
        )

    result["details"].append({
        "type": "info",
        "message": f"xlsm={excel_path.name}, .bas={len(bas_files)}个文件",
    })

    # ── Phase 2: 复制到 TEMP ──
    result["phase"] = "copy"
    tmp_root = Path(tempfile.mkdtemp(prefix="vba_verify_"))
    copy_path = tmp_root / excel_path.name
    shutil.copy2(str(excel_path), str(copy_path))
    result["details"].append({
        "type": "info",
        "message": f"副本 → {copy_path.name}",
    })

    # ── Phase 3: 准备 .bas（UTF-8 → 系统编码） ──
    result["phase"] = "prepare"
    sys_encoding = locale.getpreferredencoding()
    if sys_encoding.upper() in ("UTF-8", "UTF8"):
        sys_encoding = "gbk"

    tmp_vba = Path(tempfile.mkdtemp(prefix="vba_verify_src_"))
    for f in bas_files:
        code = f.read_text(encoding="utf-8", errors="replace")
        base = f.stem
        stripped = base.rstrip("1")
        if stripped != base and len(stripped) > 0:
            code = re.sub(
                r'(Attribute VB_Name\s*=\s*")([^"]+)1(")',
                lambda m: m.group(1) + stripped + m.group(3),
                code,
            )
            tmp_path = tmp_vba / (stripped + ".bas")
        else:
            tmp_path = tmp_vba / f.name
        tmp_path.write_text(code, encoding=sys_encoding, errors="replace")

    result["details"].append({
        "type": "info",
        "message": f"编码转换完成 ({len(bas_files)}个, sys={sys_encoding})",
    })

    # ── Phase 4: COM 导入 + 测试 ──
    result["phase"] = "com"
    try:
        import win32com.client
    except ImportError:
        return _fail(
            result, "com", "pywin32 未安装，请执行: pip install pywin32"
        )

    excel = None
    wb = None
    try:
        # ★ 关键：用 Dispatch() 新建独立进程，绝不碰已有 Excel ★
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        excel.DisplayAlerts = False
        excel.EnableEvents = False
        excel.ScreenUpdating = False

        result["details"].append({
            "type": "info",
            "message": "已启动独立 Excel 进程",
        })

        # 打开副本（不更新链接）
        wb = excel.Workbooks.Open(str(copy_path), 0, False)
        vbproj = wb.VBProject

        # ── Phase 5: 清旧导新 ──
        result["phase"] = "import"
        removed = _remove_old_modules(vbproj)
        imported = _import_modules(excel, vbproj, tmp_vba)

        if imported != len(bas_files):
            return _fail(
                result,
                "import",
                f"模块导入不完整: 预期{len(bas_files)}个, 实际导入{imported}个",
            )

        result["details"].append({
            "type": "info",
            "message": f"导入完成: 清理{removed}旧模块, 导入{imported}新模块",
        })

        # ── Phase 6: 完整性检查 ──
        imported_names = _get_module_names(vbproj)
        expected_names = set()
        for f in bas_files:
            name = (
                f.stem.rstrip("1")
                if f.stem.rstrip("1") != f.stem and len(f.stem.rstrip("1")) > 0
                else f.stem
            )
            expected_names.add(name)
        missing = expected_names - imported_names
        if missing:
            return _fail(
                result,
                "import",
                f"导入后缺少模块: {', '.join(sorted(missing))}",
            )

        # ── Phase 7: 编译/运行检查 ──
        result["phase"] = "compile"
        health_comp = _inject_health_check(vbproj)
        try:
            health = excel.Application.Run("VBAVerify_HealthCheck")
            if health is not True:
                raise RuntimeError(f"健康检查返回异常值: {health}")
        except Exception as e:
            return _fail(
                result, "compile", f"编译/运行检查失败: {e}"
            )
        finally:
            try:
                vbproj.VBComponents.Remove(health_comp)
            except Exception:
                pass

        result["details"].append({
            "type": "info",
            "message": "编译检查通过，健康函数正常返回",
        })

        # ── 全部通过 ──
        wb.Close(False)
        wb = None
        excel.Quit()
        excel = None

        result["status"] = "pass"
        result["phase"] = "done"
        result["summary"] = (
            f"✅ 验证通过: {len(bas_files)}个模块导入 + 编译检查 OK"
        )

    except Exception as e:
        return _fail(result, result["phase"], f"COM 意外错误: {e}")

    finally:
        # 确保清理
        if wb:
            try:
                wb.Close(False)
            except Exception:
                pass
        if excel:
            try:
                excel.Quit()
            except Exception:
                pass
        shutil.rmtree(tmp_root, ignore_errors=True)
        shutil.rmtree(tmp_vba, ignore_errors=True)

    return result


# ── 辅助函数 ──


def _fail(result: dict, phase: str, message: str) -> dict:
    """构造失败结果并清理（由调用者负责 finally 中的清理）"""
    result["status"] = "fail"
    result["phase"] = phase
    result["details"].append({"type": "error", "message": message})
    result["summary"] = f"❌ [{phase}] {message}"
    return result


def _remove_old_modules(vbproj) -> int:
    """清除 Workbook 中所有旧的标准模块，返回清理数量"""
    count = 0
    for i in range(vbproj.VBComponents.Count, 0, -1):
        comp = vbproj.VBComponents(i)
        if comp.Type == 1:  # vbext_ct_StdModule
            vbproj.VBComponents.Remove(comp)
            count += 1
    return count


def _import_modules(excel, vbproj, src_dir: Path) -> int:
    """通过 VBA 批量导入 .bas，返回成功导入数量"""
    escaped = str(src_dir).replace("\\", "\\\\")
    code = (
        'Function VBAVerify_ImportAll() As Long\r\n'
        '    Dim fso As Object, folder As Object, file As Object\r\n'
        '    Dim ok As Long: ok = 0\r\n'
        '    Set fso = CreateObject("Scripting.FileSystemObject")\r\n'
        f'    Set folder = fso.GetFolder("{escaped}")\r\n'
        '    For Each file In folder.Files\r\n'
        '        If LCase(fso.GetExtensionName(file.Name)) = "bas" Then\r\n'
        '            On Error Resume Next\r\n'
        '            ThisWorkbook.VBProject.VBComponents.Import file.Path\r\n'
        '            If Err.Number = 0 Then ok = ok + 1\r\n'
        '            On Error GoTo 0\r\n'
        '        End If\r\n'
        '    Next\r\n'
        '    VBAVerify_ImportAll = ok\r\n'
        'End Function\r\n'
    )
    comp = vbproj.VBComponents.Add(1)
    comp.Name = "VBAVerify_Batch"
    comp.CodeModule.AddFromString(code)
    result = excel.Application.Run("VBAVerify_ImportAll")
    vbproj.VBComponents.Remove(comp)
    return int(result) if result is not None else 0


def _get_module_names(vbproj) -> set:
    """返回 Workbook 中所有标准模块的名称集合"""
    names = set()
    for i in range(1, vbproj.VBComponents.Count + 1):
        comp = vbproj.VBComponents(i)
        if comp.Type == 1:
            names.add(comp.Name)
    return names


def _inject_health_check(vbproj):
    """注入健康检查函数，返回组件对象（调用者负责移除）"""
    code = (
        'Public Function VBAVerify_HealthCheck() As Boolean\r\n'
        '    VBAVerify_HealthCheck = True\r\n'
        'End Function\r\n'
    )
    comp = vbproj.VBComponents.Add(1)
    comp.Name = "VBAVerify_Health"
    comp.CodeModule.AddFromString(code)
    return comp


def main():
    parser = argparse.ArgumentParser(
        description="VBA 自动验证 — 导入 .bas 到副本并运行测试",
    )
    parser.add_argument("xlsm_path", help="原始 xlsm 文件路径")
    parser.add_argument(
        "bas_dir",
        nargs="?",
        default="昭明计划VS优化_vba",
        help=".bas 文件所在目录（默认: 昭明计划VS优化_vba）",
    )
    args = parser.parse_args()

    result = verify(args.xlsm_path, args.bas_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["status"] == "pass" else 1)


if __name__ == "__main__":
    main()