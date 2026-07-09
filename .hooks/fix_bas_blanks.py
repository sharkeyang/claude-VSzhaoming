"""
PostToolUse hook: 自动修复 .bas 文件空行污染
检查所有被修改的 .bas 文件，将连续超过 2 个空行压缩为 1 个。
"""
import sys
import json
import os
import re


def main():
    try:
        data = json.load(sys.stdin)
        fp = data.get("tool_input", {}).get("file_path", "")
        if not fp or not fp.endswith(".bas"):
            return
        if not os.path.exists(fp):
            return

        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()

        # 压缩连续空行：将 3+ 个连续空行压缩为 1 个
        original = content
        content = re.sub(r'\n[ \t]*\n[ \t]*\n[ \t]*', '\n\n', content)

        # 也处理 CRLF 版本
        content = re.sub(r'\r\n[ \t]*\r\n[ \t]*\r\n[ \t]*', '\r\n\r\n', content)

        if content != original:
            with open(fp, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"[fix_bas_blanks] 已修复空行: {os.path.basename(fp)}")
    except Exception:
        pass  # 永不阻塞


if __name__ == "__main__":
    main()