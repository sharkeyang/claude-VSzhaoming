# ============================================================================
# vba2VS.ps1 — 导出 VBA 模块到 .bas 文本文件
# ============================================================================
# 用法: 在项目根目录下执行
#   _产出物\_工具\vba2VS.ps1
#   或（如果 PATH 已配置）直接: vba2VS
# ============================================================================
# 说明: 从昭明计划VS优化.xlsm 导出所有标准模块到昭明计划VS优化_vba/
#       仅保存目标工作簿，不关闭 Excel，不影响其他工作簿
# ============================================================================

$ErrorActionPreference = "Stop"
$脚本目录 = Split-Path -Parent $MyInvocation.MyCommand.Path
$项目根目录 = Resolve-Path "$脚本目录\..\.."
$target = "昭明计划VS优化.xlsm"

# ============================================================================
# 1. 若 Excel 已打开 → 仅保存目标工作簿
# ============================================================================
try {
    $excel = [Runtime.Interopservices.Marshal]::GetActiveObject("Excel.Application")
    foreach ($wb in $excel.Workbooks) {
        if ($wb.Name -eq $target) {
            $wb.Save()
            Write-Host "已保存 [$target]。"
            break
        }
    }
} catch {
    Write-Host "Excel 未运行，跳过保存。"
}

# ============================================================================
# 2. 导出 xlsm → .bas（通过临时目录中转）
# ============================================================================
Copy-Item "$项目根目录\$target" "$env:TEMP\$target" -Force
$src = "$env:TEMP\昭明计划VS优化_vba"
if (Test-Path $src) { Remove-Item -Recurse -Force $src; Start-Sleep 1 }

python "$脚本目录\vba2宏操作.py" export "$env:TEMP\$target" -m -c NONE

# ============================================================================
# 3. 写入项目目录（先清空旧 .bas）
# ============================================================================
$dst = "$项目根目录\昭明计划VS优化_vba"
if (Test-Path $dst) { Remove-Item -Recurse -Force $dst; Start-Sleep 1 }
New-Item -ItemType Directory -Force $dst | Out-Null
Copy-Item "$src\*.bas" $dst -Force
Write-Host "导出完成: $dst\  ($((Get-ChildItem $dst\*.bas).Count) 个模块)"