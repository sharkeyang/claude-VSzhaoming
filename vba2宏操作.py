"""
VBA 宏操作 — 导出/导入 统一脚本

用法
----
    python "vba宏操作.py" export 昭明计划VS优化.xlsm -m [-o output_dir] [-p 文件密码] [-v VBA密码] [-c NONE]
    python "vba宏操作.py" import 昭明计划VS优化.xlsm -m [-s source_dir] [-p 文件密码] [-v VBA密码] [-c NONE] [--dry-run]

参数
----
    export / import   子命令
    -m, --modules-only    仅标准模块 (.bas)
    -o, --outdir          导出输出目录（默认: <excel>_vba）
    -s, --srcdir          导入源目录（默认: <excel>_vba）
    -p, --password        文件打开密码
    -v, --vba-password    VBA 工程密码
    -c, --config          密码配置文件
    --dry-run             预览导入，不实际修改

依赖
----
    导出: pip install oletools msoffcrypto
    导入: pip install pywin32 msoffcrypto olefile
"""

import argparse
import sys
import os
import re
import tempfile
import shutil
import locale
from pathlib import Path


# ────────────────────────────────────────────
# 密码配置
# ────────────────────────────────────────────

def sanitize_filename(name):
    return re.sub(r'[\\/:*?"<>|]', '_', name)


def load_password_config(config_path):
    config = {}
    if not config_path or not os.path.exists(config_path):
        return config
    with open(config_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' in line:
                key, value = line.split('=', 1)
                config[key.strip()] = value.strip()
    return config


def find_auto_config(excel_path):
    base = os.path.splitext(os.path.basename(excel_path))[0]
    excel_dir = os.path.dirname(excel_path) or '.'
    script_dir = os.path.dirname(__file__) or '.'
    candidates = [
        os.path.join(excel_dir, base + '_passwords.txt'),
        os.path.join(script_dir, base + '_passwords.txt'),
        os.path.join(excel_dir, 'vba_passwords.txt'),
        os.path.join(script_dir, 'vba_passwords.txt'),
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


# ────────────────────────────────────────────
# 导出
# ────────────────────────────────────────────

def decrypt_file(encrypted_path, password):
    import msoffcrypto
    fd, decrypted_path = tempfile.mkstemp(suffix='.xlsm', prefix='vba_export_')
    os.close(fd)
    os.unlink(decrypted_path)
    with open(encrypted_path, 'rb') as f:
        office_file = msoffcrypto.OfficeFile(f)
        office_file.load_key(password=password)
        with open(decrypted_path, 'wb') as out:
            office_file.decrypt(out)
    return decrypted_path, True


def cmd_export(args):
    excel_path = Path(args.excel_path)
    if not excel_path.exists():
        print(f"Error: file not found: {excel_path}")
        sys.exit(1)

    config_path = args.config or find_auto_config(str(excel_path))
    config = load_password_config(config_path)
    excel_password = args.password or config.get('excel_password')
    vba_password = args.vba_password or config.get('vba_password')
    outdir = Path(args.outdir) if args.outdir else excel_path.parent / (excel_path.stem + "_vba")
    outdir.mkdir(parents=True, exist_ok=True)

    process_path = str(excel_path)
    delete_after = False

    if excel_password:
        print(f"Decrypting with password...")
        try:
            process_path, _ = decrypt_file(str(excel_path), excel_password)
            delete_after = True
            print(f"Decrypted OK")
        except Exception as e:
            print(f"Decrypt failed: {e}")
            sys.exit(1)

    try:
        from oletools.olevba import VBA_Parser
        import inspect
        if vba_password and 'vbapassword' in inspect.signature(VBA_Parser.__init__).parameters:
            vba = VBA_Parser(process_path, vbapassword=vba_password)
        else:
            vba = VBA_Parser(process_path)
            if vba_password:
                print("Note: oletools version does not support VBA password; trying without it.")
    except Exception as e:
        print(f"Error opening VBA container: {e}")
        sys.exit(1)

    if not vba.detect_vba_macros():
        print("No VBA macros found in this workbook.")
        vba.close()
        if delete_after:
            os.unlink(process_path)
        sys.exit(1)

    count = 0
    for (subfilename, stream_path, vba_filename, vba_code) in vba.extract_macros():
        if not vba_code or not vba_code.strip():
            continue

        if vba_filename.endswith(".frm"):
            ext = ".frm"
        elif vba_filename.endswith(".frx"):
            continue
        elif vba_filename.endswith(".cls"):
            ext = ".cls"
        elif vba_filename.endswith(".bas"):
            ext = ".bas"
        else:
            ext = ".bas"

        if args.modules_only and ext != ".bas":
            continue

        name_no_ext = vba_filename.rsplit(".", 1)[0] if vba_filename.endswith((".bas", ".cls", ".frm")) else vba_filename
        safe = sanitize_filename(name_no_ext)
        key = safe + ext
        outpath = outdir / key
        normalized = vba_code.replace('\r\n', '\n').replace('\r', '\n')
        outpath.write_text(normalized, encoding="utf-8")
        count += 1
        print(f"  [OK] {key}")

    vba.close()
    if delete_after:
        try:
            os.unlink(process_path)
        except:
            pass

    if count:
        print(f"\nExported {count} modules -> {outdir}")
    else:
        print("No VBA macros found.")


# ────────────────────────────────────────────
# 导入
# ────────────────────────────────────────────

def prepare_workbook(excel_path, excel_password, vba_password):
    work_path = str(excel_path)
    delete_after = False

    if not excel_password and not vba_password:
        return work_path, delete_after

    import zipfile
    print("Preparing workbook...")

    if excel_password:
        print("  Decrypting...")
        try:
            import msoffcrypto
            fd, decrypted_path = tempfile.mkstemp(suffix='.xlsm', prefix='vba_import_dec_')
            os.close(fd)
            os.unlink(decrypted_path)
            with open(str(excel_path), 'rb') as f:
                office_file = msoffcrypto.OfficeFile(f)
                office_file.load_key(password=excel_password)
                with open(decrypted_path, 'wb') as out:
                    office_file.decrypt(out)
            work_path = decrypted_path
            delete_after = True
            print("  Decrypted OK")
        except Exception as e:
            print(f"  Decrypt failed: {e}")
            sys.exit(1)

    if vba_password and work_path:
        print("  Removing VBA password...")
        try:
            import olefile
            with zipfile.ZipFile(work_path, 'r') as z:
                vba_bin = z.read('xl/vbaProject.bin')
                zip_entries = {name: z.read(name) for name in z.namelist()}

            fd2, vba_tmp = tempfile.mkstemp(suffix='.vbapatch', prefix='vba_proj_patch_')
            os.close(fd2)
            os.unlink(vba_tmp)
            with open(vba_tmp, 'wb') as f:
                f.write(vba_bin)

            ole = olefile.OleFileIO(vba_tmp, write_mode=True)
            project_data = ole.openstream('PROJECT').read()
            new_data = project_data.replace(b'DPB=', b'DPx=')
            vba_patched = (new_data != project_data)
            if vba_patched:
                ole.write_stream('PROJECT', new_data)
            ole.close()

            if vba_patched:
                with open(vba_tmp, 'rb') as f:
                    new_vba_bin = f.read()
                with zipfile.ZipFile(work_path, 'w', zipfile.ZIP_DEFLATED) as zout:
                    for name, data in zip_entries.items():
                        zout.writestr(name, new_vba_bin if name == 'xl/vbaProject.bin' else data)
                print("  VBA password removed OK")
            else:
                print("  VBA password marker not found.")
            os.unlink(vba_tmp)
        except Exception as e:
            print(f"  Patch failed: {e}")

    return work_path, delete_after


def cmd_import(args):
    excel_path = Path(args.excel_path).resolve()
    if not excel_path.exists():
        print(f"Error: file not found: {excel_path}")
        sys.exit(1)

    config_path = args.config or find_auto_config(str(excel_path))
    config = load_password_config(config_path)
    excel_password = args.password or config.get('excel_password')
    vba_password = args.vba_password or config.get('vba_password')

    srcdir = Path(args.srcdir).resolve() if args.srcdir else (excel_path.parent / (excel_path.stem + "_vba")).resolve()
    if not srcdir.exists():
        print(f"Error: source directory not found: {srcdir}")
        sys.exit(1)

    files = []
    exts = ('.bas',) if args.modules_only else ('.bas', '.cls', '.frm')
    for ext in exts:
        files.extend(sorted(srcdir.glob(f'*{ext}')))

    if not files:
        print(f"No .bas/.cls/.frm files found in {srcdir}")
        sys.exit(1)

    print(f"Excel:  {excel_path}")
    print(f"Source: {srcdir}")
    print(f"Modules: {len(files)}")
    print()

    if args.dry_run:
        print("Dry run — would import:")
        for f in files:
            print(f"  {f.name}")
        sys.exit(0)

    # Convert UTF-8 to system encoding
    sys_encoding = locale.getpreferredencoding()
    if sys_encoding.upper() in ('UTF-8', 'UTF8'):
        sys_encoding = 'gbk'

    tmpdir = tempfile.mkdtemp(prefix='vba_batch_')
    for f in files:
        code = f.read_text(encoding='utf-8', errors='replace')
        base = f.stem
        stripped = base.rstrip('1')
        if stripped != base and len(stripped) > 0:
            # Fix VB_Name attribute in content
            code = re.sub(
                r'(Attribute VB_Name\s*=\s*")([^"]+)1(")',
                lambda m: m.group(1) + stripped + m.group(3),
                code,
            )
            new_fname = stripped + '.bas'
            tmp_path = os.path.join(tmpdir, new_fname)
        else:
            tmp_path = os.path.join(tmpdir, f.name)
        with open(tmp_path, 'w', encoding=sys_encoding, errors='replace') as fout:
            fout.write(code)
    print(f"Converted {len(files)} files -> {tmpdir}")

    work_path, delete_after = prepare_workbook(excel_path, excel_password, vba_password)

    try:
        import win32com.client
    except ImportError:
        print("Error: pywin32 not installed. Run: pip install pywin32")
        sys.exit(1)

    was_excel_running = False
    try:
        excel = win32com.client.GetActiveObject("Excel.Application")
        was_excel_running = True
        print("Connected to existing Excel instance.")
    except Exception:
        excel = win32com.client.Dispatch("Excel.Application")
        print("Created new Excel instance.")

    try:
        prev_visible = excel.Visible
    except Exception:
        prev_visible = True
    try:
        prev_display_alerts = excel.DisplayAlerts
    except Exception:
        prev_display_alerts = True
    try:
        prev_enable_events = excel.EnableEvents
    except Exception:
        prev_enable_events = True
    try:
        prev_automation_security = excel.AutomationSecurity
    except Exception:
        prev_automation_security = 2

    try:
        excel.DisplayAlerts = False
        excel.EnableEvents = False
        excel.AutomationSecurity = 1
    except Exception:
        pass

    wb = None
    try:
        print("Opening workbook...")
        wb = excel.Workbooks.Open(work_path, 0, False)
        if wb is None:
            raise RuntimeError(f"Excel failed to open workbook: {work_path}")
        vbproj = wb.VBProject

        tmpdir_vba = tmpdir.replace('\\', '\\\\')
        if args.modules_only:
            exts_vba = '"bas"'
        else:
            exts_vba = '"bas", "cls", "frm"'

        batch_code = (
            'Sub VBAImport_Batch()\r\n'
            '    Dim fso As Object, folder As Object, file As Object\r\n'
            '    Dim comp As Object, i As Long, ext As String\r\n'
            '    Dim removed As Long, ok As Long\r\n'
            '    removed = 0: ok = 0\r\n'
            '    For i = ThisWorkbook.VBProject.VBComponents.Count To 1 Step -1\r\n'
            '        Set comp = ThisWorkbook.VBProject.VBComponents(i)\r\n'
            '        If comp.Type = 1 Then\r\n'
            '            On Error Resume Next\r\n'
            '            ThisWorkbook.VBProject.VBComponents.Remove comp\r\n'
            '            On Error GoTo 0\r\n'
            '            removed = removed + 1\r\n'
            '        End If\r\n'
            '    Next\r\n'
            '    Set fso = CreateObject("Scripting.FileSystemObject")\r\n'
            f'    Set folder = fso.GetFolder("{tmpdir_vba}")\r\n'
            '    For Each file In folder.Files\r\n'
            f'        ext = LCase(fso.GetExtensionName(file.Name))\r\n'
            f'        If ext = {exts_vba} Then\r\n'
            '            ThisWorkbook.VBProject.VBComponents.Import file.Path\r\n'
            '            ok = ok + 1\r\n'
            '        End If\r\n'
            '    Next\r\n'
            f'    Application.StatusBar = "Cleaned " & removed & " + Imported " & ok & " modules"\r\n'
            'End Sub\r\n'
        )

        try:
            existing = vbproj.VBComponents("VBAImportBatch")
            vbproj.VBComponents.Remove(existing)
        except Exception:
            pass

        batch_comp = vbproj.VBComponents.Add(1)
        batch_comp.Name = "VBAImportBatch"
        batch_comp.CodeModule.AddFromString(batch_code)

        print("Running batch import...")
        excel.Application.Run("VBAImport_Batch")
        print("Import completed.")

        try:
            vbproj.VBComponents.Remove(batch_comp)
        except Exception:
            pass

        # Save
        fd3, temp_save = tempfile.mkstemp(suffix='.xlsm', prefix='vba_save_')
        os.close(fd3)
        os.unlink(temp_save)

        if excel_password:
            wb.Password = excel_password
        wb.SaveAs(temp_save, wb.FileFormat)
        wb.Close()
        print("Saved OK.")

        # Replace original
        if os.path.exists(temp_save):
            backup = str(excel_path) + ".backup"
            try:
                os.unlink(backup)
            except Exception:
                pass
            os.replace(str(excel_path), backup)
            os.replace(temp_save, str(excel_path))
            print(f"Backed up to: {backup}")

    except Exception as e:
        print(f"Fatal error: {e}")
        if wb:
            try:
                wb.Close(False)
            except Exception:
                pass
        try:
            if not was_excel_running:
                excel.Quit()
        except Exception:
            pass
        if delete_after:
            try:
                os.unlink(work_path)
            except Exception:
                pass
        shutil.rmtree(tmpdir, ignore_errors=True)
        sys.exit(1)

    try:
        excel.DisplayAlerts = prev_display_alerts
        excel.EnableEvents = prev_enable_events
        excel.AutomationSecurity = prev_automation_security
    except Exception:
        pass

    if was_excel_running:
        print("Preserved existing Excel instance.")
    else:
        try:
            excel.Quit()
        except Exception:
            pass

    if delete_after:
        try:
            os.unlink(work_path)
        except Exception:
            pass
    shutil.rmtree(tmpdir, ignore_errors=True)
    print("Done.")


# ────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="VBA 宏操作 — 导出/导入 统一脚本",
        epilog="用法: python vba宏操作.py export workbook.xlsm -m\n       python vba宏操作.py import workbook.xlsm -m",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest='command', required=True)

    # export
    exp = subparsers.add_parser('export', help='导出 VBA 宏到 .bas 文本文件')
    exp.add_argument('excel_path', help='Excel 文件路径')
    exp.add_argument('-o', '--outdir', default=None, help='输出目录（默认: <excel>_vba）')
    exp.add_argument('-p', '--password', default=None, help='文件打开密码')
    exp.add_argument('-v', '--vba-password', default=None, help='VBA 工程密码')
    exp.add_argument('-c', '--config', default=None, help='密码配置文件')
    exp.add_argument('-m', '--modules-only', action='store_true', help='仅导出标准模块 (.bas)')

    # import
    imp = subparsers.add_parser('import', help='导入 .bas 文本文件到 VBA 模块')
    imp.add_argument('excel_path', help='Excel 文件路径')
    imp.add_argument('-s', '--srcdir', default=None, help='源目录（默认: <excel>_vba）')
    imp.add_argument('-p', '--password', default=None, help='文件打开密码')
    imp.add_argument('-v', '--vba-password', default=None, help='VBA 工程密码')
    imp.add_argument('-c', '--config', default=None, help='密码配置文件')
    imp.add_argument('--dry-run', action='store_true', help='预览导入')
    imp.add_argument('-m', '--modules-only', action='store_true', help='仅导入标准模块 (.bas)')

    args = parser.parse_args()

    if args.command == 'export':
        cmd_export(args)
    elif args.command == 'import':
        cmd_import(args)


if __name__ == "__main__":
    main()
