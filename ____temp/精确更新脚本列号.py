# -*- coding: utf-8 -*-
"""
精确更新 _产出物/_工具/ 下脚本的谕组日/周 CSV 列号（2026-10-04 元数据更新后）
====================================================
只替换代码中的 row[N] 引用（正则匹配），不替换注释，避免占位符冲突。

日类映射（旧→新）：顶型[43]→[42] 日等型[44]→[43] 仓日类[45]→[44] BT连阳[42]→[41]
  DTZB[62]→[66] DTZD[63]→[67] DTAB[64]→[68] DTCD[65]→[69]
周类映射（旧→新）：WXZA[14]→[13] WXZB[15]→[14] WXZC[16]→[15] WXZD[17]→[16]
  WXZE[18]→[17] WXZF[19]→[18] WXAB[20]→[19] ... WXCD[25]→[24] ... 周龄[51]→[60]
"""
import os, re, sys

sys.stdout.reconfigure(encoding='utf-8')
工具目录 = '_产出物/_工具'

日类映射 = {42:41, 43:42, 44:43, 45:44, 62:66, 63:67, 64:68, 65:69}
周类映射 = {14:13,15:14,16:15,17:16,18:17,19:18,20:19,21:20,22:21,23:22,24:23,
            25:24,26:25,27:26,28:27,29:28,30:29,31:30,32:31,33:32,34:33,35:34,
            36:35,37:36,38:37,39:38,40:39,41:40,42:41,43:42,44:43,45:44,46:45,
            47:46,48:47,49:48,50:49,51:60}

# 只匹配代码中的 row[N] 引用：row[数字] / rows[idx][数字] / rows[idx - 1][数字] / to_f(row[数字]) / float(row[数字])
# 用负向断言避免匹配注释（注释里通常是 [N] 含义说明，如 "[44] 日等型"）
# 匹配模式：row 后紧跟 [数字]，且前面不是 "[" 或 "列" 等
列引用 = re.compile(r'(row\s*\[\s*)(\d+)(\s*\])')

def 判断类别(content):
    if '谕组日' in content and '谕组周' not in content:
        return '日类'
    if '谕组周' in content and '谕组日' not in content:
        return '周类'
    if "DATA_DIR = '昭明算展/谕组日'" in content or "DATADIR = r'昭明算展/谕组日'" in content:
        return '日类'
    if "DATA_DIR = '昭明算展/谕组周'" in content or "DATADIR = r'昭明算展/谕组周'" in content:
        return '周类'
    return None

def 替换(content, 映射):
    def repl(m):
        旧 = int(m.group(2))
        if 旧 in 映射:
            return f'{m.group(1)}{映射[旧]}{m.group(3)}'
        return m.group(0)
    return 列引用.sub(repl, content)

调整数 = 0
for fname in sorted(os.listdir(工具目录)):
    if not fname.endswith('.py'):
        continue
    path = os.path.join(工具目录, fname)
    with open(path, encoding='utf-8') as f:
        content = f.read()
    类别 = 判断类别(content)
    if 类别 is None:
        continue
    映射 = 日类映射 if 类别 == '日类' else 周类映射
    new_content = 替换(content, 映射)
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'  [调整] {fname} ({类别})')
        调整数 += 1

print(f'\n完成：调整 {调整数} 个脚本')
