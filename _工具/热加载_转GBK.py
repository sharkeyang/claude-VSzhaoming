#!/usr/bin/env python3
"""热加载辅助工具 — 将 UTF-8 .bas 文件转为 GBK 临时目录，供 VBA Import 使用"""
import sys, os, shutil, tempfile, locale

def main():
    src_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(__file__)
    # 默认到上级目录的 昭明计划VS优化_vba
    if not os.path.isdir(src_dir):
        src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '昭明计划VS优化_vba')

    sys_enc = locale.getpreferredencoding()
    if sys_enc.upper() in ('UTF-8', 'UTF8'):
        sys_enc = 'gbk'

    tmp_dir = tempfile.mkdtemp(prefix='vba_hot_reload_')
    count = 0
    for f in sorted(os.listdir(src_dir)):
        if not f.endswith('.bas'):
            continue
        src_path = os.path.join(src_dir, f)
        # 读 UTF-8
        with open(src_path, 'r', encoding='utf-8') as fh:
            text = fh.read()
        # 写 GBK
        dst_path = os.path.join(tmp_dir, f)
        with open(dst_path, 'w', encoding=sys_enc) as fh:
            fh.write(text)
        count += 1

    print(tmp_dir)  # 只输出目录路径，VBA 用这个路径
    return 0

if __name__ == '__main__':
    sys.exit(main())