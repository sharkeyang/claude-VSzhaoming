# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A quantitative trading/investment research system built in Excel VBA (57 standard modules). The VBA source lives in `昭明计划VS优化.xlsm`. Python scripts export/import VBA code so it can be edited with proper tooling. Use `/vba2VS` and `/vba2EXCEL` skills in Claude Code chat for daily workflow.

## VBA workflow

### Quick: use skills

In Claude Code chat, use `/vba2VS` and `/vba2EXCEL`. These skills handle Excel lifecycle (save/quit via COM), temp dir cleanup, and file sync automatically.

### Manual commands (PowerShell, working dir = project root)

**Export (xlsm → text files):**
```powershell
try { 
    $excel = [Runtime.Interopservices.Marshal]::GetActiveObject("Excel.Application")
    $excel.Workbooks | ForEach-Object { $_.Save() }
} catch { }
# 导出
Copy-Item .\昭明计划VS优化.xlsm $env:TEMP\昭明计划VS优化.xlsm -Force
$src = "$env:TEMP\昭明计划VS优化_vba"
if (Test-Path $src) { Remove-Item -Recurse -Force $src }
python ".\VBA宏操作_导出_Python版.py" $env:TEMP\昭明计划VS优化.xlsm -m -c NONE
$dst = ".\昭明计划VS优化_vba"
if (Test-Path $dst) { Remove-Item -Recurse -Force $dst }
New-Item -ItemType Directory -Force $dst | Out-Null
Copy-Item "$src\*.bas" $dst -Force
```
`-m` exports only standard modules (.bas), skipping worksheets/ThisWorkbook/forms.  
`-c NONE` skips auto-detected password files.

**Import (text files → xlsm):**
```powershell
try { 
    $excel = [Runtime.Interopservices.Marshal]::GetActiveObject("Excel.Application")
    $excel.Workbooks | ForEach-Object { $_.Save() }
    $excel.Quit()
    [Runtime.Interopservices.Marshal]::ReleaseComObject($excel) | Out-Null
    Start-Sleep 2
} catch { }
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item .\昭明计划VS优化.xlsm ".\昭明计划VS优化_$ts.xlsm"
$tmpvba = "$env:TEMP\昭明计划VS优化_vba"
$tmpxlsm = "$env:TEMP\昭明计划VS优化.xlsm"
if (Test-Path $tmpvba) { Remove-Item -Recurse -Force $tmpvba }
New-Item -ItemType Directory -Force $tmpvba | Out-Null
Copy-Item ".\昭明计划VS优化_vba\*.bas" $tmpvba -Force
Copy-Item .\昭明计划VS优化.xlsm $tmpxlsm -Force
python ".\VBA宏操作_导入_Python版.py" $tmpxlsm -s $tmpvba -m -c NONE
Copy-Item $tmpxlsm .\昭明计划VS优化.xlsm -Force
```
Uses Excel COM — requires Excel with "Trust access to VBA project object model" enabled.  
Import script removes ALL old modules before importing fresh, preventing duplicates.  
Saves timestamped backup before overwriting (e.g. `昭明计划VS优化_20260608_153000.xlsm`).

**Dependencies:** `pip install oletools msoffcrypto` (export), `pip install pywin32` (import).

**Dry-run before import** to preview changes: add `--dry-run` flag.

## Module naming

All 60 modules use Chinese identifiers. Prefix conventions:
- `SET_` — constants and menu config
- `SOP_` — workflow operations (sort, filter, clean, organize)
- `WMR现市_` — market data (CN stocks A/B/C, HK, US, futures)
- `WMH历研_` / `WMH_T历研统时_` — historical research / time-series stats
- `PX算研_` — calculation engines (RAP, ZAL)
- `IQQQ跨码_` — cross-code engines (screen, spectrum, pool)
  - 出章模式参数: `"周仓"`（周粒度分类，原"仓月"）、`"日仓"`（日粒度分类，原"仓日"/"日乾"）、`"混"`、`"活"`、`"停"`
  - 出节模式参数: `"周层"`、`"周地"`、`"日层"`、`"日机"`、`"周仓"`（仓周型维度，原"仓周"）
  - 瓜分类型: `"周仓仓周"`、`"周仓周地"`、`"周仓周层"`、`"周仓日层"`、`"周仓日层滤"`、`"日仓日层"`、`"日仓日层滤"`、`"日仓日机"`、`"活"`、`"混*"`
  - C3章按日乾函数已删除，日乾/日仓统一走C1章按仓类
- `ZUTL_` — utilities (delivery note, Python runner, notes)
- `OS核管_` — core management (book management, settlement, data engines)

## OneDrive file locking

OneDrive may lock `.xlsm` files, causing `[Errno 13] Permission denied`. Always work on a copy in `/tmp/` and copy results back.

## Password config

Password config files use `key=value` format, `#` for comments:
```
excel_password=<file-open password>
vba_password=<VBA project password>
```
Auto-discovered from `<excel_name>_passwords.txt` or `vba_passwords.txt` next to the Excel file or script. When no password is set, use `-c NONE` to skip auto-detection.

## ⚠️ 禁止在 VSCode 中直接打开 .bas 文件保存

**绝对不要**在 VSCode 中直接打开 `.bas` 文件并保存！原因：

1. VSCode 全局默认编码为 `GBK`，而 `.bas` 文件是 `UTF-8` 编码
2. 保存时 VSCode 会在 `End Function`、`===`/`###`/`@@@` 分隔符之间插入大量空行
3. 已多次发生该问题，导致 .bas 文件被污染

**正确做法：** 只通过 `/vba2VS` 重新导出，或在 Claude Code 中直接用 Read/Edit 编辑。不要用 VSCode 直接改 .bas 文件！

## 项目结构

- `_产出物/` — 交付产物（MC2-MC5代码、文档）
- `_工具/` — VBA工作流脚本（已加入PATH，可直接运行）
- `_分析输出/` — 分析报告与映射文档
- `_分析脚本/` — 文档格式化工具
- `_规则文档/` — 三文件+益盟公式

## Harness 工程规则

### 何时启动 Harness
当涉及以下任一场景时，必须优先使用 Harness 工程体系：
- 修改多个文件 / 新增功能 / 重构
- 需要联网查资料、查最新文档
- 需要多 Agent 并行工作
- 任何代码变更（包括 Bug 修复）

### 5 条核心方法
1. **先方案后编码**：输出完整方案 → 人工确认 → 才能写代码
2. **MCP + Skills 配工具**：如有需要，先检查 MCP 和 Skill 是否可用
3. **自动测试验证**：写完后运行验证脚本，确认通过
4. **文档+Git 存档**：每功能一提交，更新进度文档
5. **规则文件先行**：遵循 CLAUDE.md 中的项目规范

### 规则卡片
- **启动新项目**：创建 CLAUDE.md → 配置 settings.json → 创建验证脚本 → Git 初始化
- **开始新功能**：先方案后编码 → 可并行则用多 Agent → 跑通测试 → 提交
- **需要 MCP**：判断是否必须 → 选对应 MCP（Playwright/Context7/Sequential Thinking等）
- **代码审查**：使用 /code-review → 高风险用 Playwright 验证 → 不通过不提交
- **项目维护**：定期跑验证 → 清理 temp → 规范提交 → 同步文档

### 实施指南路径
完整实施指南：`D:\@VSwork\VSteach\_SHARK\Harness工程体系实施指南.md`
```powershell
vba2VS.ps1        # 导出VBA -> .bas
vba2EXCEL.ps1     # 导入 .bas -> VBA
```
