"""PostToolUse hook: ensure .ps1 files are UTF-8 with BOM."""
import sys, json, os

try:
    data = json.load(sys.stdin)
    fp = data.get("tool_input", {}).get("file_path", "")
    if fp and fp.endswith(".ps1") and os.path.exists(fp):
        with open(fp, "r", encoding="utf-8-sig") as f:
            content = f.read()
        with open(fp, "w", encoding="utf-8-sig") as f:
            f.write(content)
        print(f"[fix_ps1_encoding] UTF-8 BOM ensured: {fp}")
except Exception:
    pass  # never block on encoding fix
