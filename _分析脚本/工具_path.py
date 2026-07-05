import subprocess, os

# 1. Add _tools path to PowerShell profile
profile_path = os.path.expanduser("~/Documents/WindowsPowerShell/Microsoft.PowerShell_profile.ps1")
tools_path = "d:/@VSwork/VS昭明计划VBA优化/_工具"

profile_content = f"""
# 昭明计划工具路径
$env:Path += ';{tools_path}'
"""

os.makedirs(os.path.dirname(profile_path), exist_ok=True)
with open(profile_path, 'a', encoding='utf-8') as f:
    f.write(profile_content)

print(f"1. PATH added to {profile_path}")

# 2. Update CLAUDE.md
claude_path = "d:/@VSwork/VS昭明计划VBA优化/CLAUDE.md"
claude_content = """
## 项目结构

- `_产出物/` — 交付产物（MC2-MC5代码、文档）
- `_工具/` — VBA工作流脚本（已加入PATH，可直接运行）
- `_分析输出/` — 分析报告与映射文档
- `_分析脚本/` — 文档格式化工具
- `_规则文档/` — 三文件+益盟公式

### 常用命令
```powershell
vba2VS.ps1        # 导出VBA -> .bas
vba2EXCEL.ps1     # 导入 .bas -> VBA
```
"""

with open(claude_path, 'a', encoding='utf-8') as f:
    f.write(claude_content)

print(f"2. CLAUDE.md updated at {claude_path}")