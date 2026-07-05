---
name: vba2VS
description: Export VBA modules from 昭明计划VS优化.xlsm to .bas text files. Use when needing to read or edit VBA code outside Excel.
---

# VBA Export

Exports all standard modules (.bas) from `昭明计划VS优化.xlsm` to `昭明计划VS优化_vba/`. Skips worksheet/ThisWorkbook code.

Paths are relative to `d:\@VSwork\VS昭明计划VBA优化`.

## Execution (one shot)

```powershell
# 若Excel已打开 → 静默保存，不退出Excel
try { 
    $excel = [Runtime.Interopservices.Marshal]::GetActiveObject("Excel.Application")
    $excel.Workbooks | ForEach-Object { $_.Save() }
} catch { }

# 备份原xlsm
$ts = Get-Date -Format "yyyyMMdd_HHmmss"
Copy-Item .\昭明计划VS优化.xlsm ".\昭明计划VS优化_$ts.xlsm" -Force

# 导出
Copy-Item .\昭明计划VS优化.xlsm $env:TEMP\昭明计划VS优化.xlsm -Force
$src = "$env:TEMP\昭明计划VS优化_vba"
if (Test-Path $src) { Remove-Item -Recurse -Force $src; Start-Sleep 1 }
python ".\VBA宏操作_导出_Python版.py" $env:TEMP\昭明计划VS优化.xlsm -m -c NONE

# 清理旧bas → 写入新bas（确保无残留、无(1)后缀）
$dst = ".\昭明计划VS优化_vba"
if (Test-Path $dst) { Remove-Item -Recurse -Force $dst; Start-Sleep 1 }
New-Item -ItemType Directory -Force $dst | Out-Null
Copy-Item "$src\*.bas" $dst -Force
```

After export, `.bas` files are in `昭明计划VS优化_vba/` for editing.
