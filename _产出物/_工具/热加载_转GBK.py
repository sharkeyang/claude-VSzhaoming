#!/usr/bin/env python3
"""热加载辅助工具 — 将 UTF-8 .bas 文件转为 GBK 临时目录，供 VBA Import 使用
固定输出到 %TEMP%\vba_hot_reload\，VBA 宏直接读取此目录"""
import sys, os, locale, shutil, tempfile

def main():
    src_dir = r"D:\@VSwork\VS昭明计划VBA优化\昭明计划VS优化_vba"
    if len(sys.argv) > 1:
        src_dir = sys.argv[1]

    if not os.path.isdir(src_dir):
        return 1

    sys_enc = locale.getpreferredencoding()
    if sys_enc.upper() in ('UTF-8', 'UTF8'):
        sys_enc = 'gbk'

    # 固定临时目录
    tmp_dir = os.path.join(os.environ.get('TEMP', tempfile.gettempdir()), 'vba_hot_reload')
    if os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.makedirs(tmp_dir)

    for f in sorted(os.listdir(src_dir)):
        if not f.endswith('.bas'):
            continue
        src_path = os.path.join(src_dir, f)
        try:
            with open(src_path, 'r', encoding='utf-8') as fh:
                text = fh.read()
            dst_path = os.path.join(tmp_dir, f)
            with open(dst_path, 'w', encoding=sys_enc) as fh:
                fh.write(text)
        except:
            print(f"跳过: {f} - 读取失败", file=sys.stderr)
            continue

    return 0

if __name__ == '__main__':
    sys.exit(main())