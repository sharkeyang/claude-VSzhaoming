param(
    [string]$FilePath = "d:\@VSwork\VS昭明计划VBA优化\20260710交割单查询.txt"
)

# ======================================================
# 交割单多维深度分析脚本
# 优先级: ⑥择时 → ⑦仓位 → ⑤成本 → ①盈亏 → ③T+0
# ======================================================

function Write-Section {
    param([string]$Title)
    $line = "=" * 60
    Write-Host "`n$line"
    Write-Host "  $Title"
    Write-Host $line
}

function Write-SubSection {
    param([string]$Title)
    Write-Host "`n--- $Title ---"
}

# ----- 数据加载 -----
Write-Host "正在加载数据..."

$content = [System.IO.File]::ReadAllText($FilePath, [System.Text.Encoding]::GetEncoding("GBK"))
$lines = $content -split "`n"
Write-Host "总行数: $($lines.Length)"

$records = @()
for ($i = 3; $i -lt $lines.Length; $i++) {
    $line = $lines[$i].Trim()
    if ($line.Length -eq 0) { continue }
    $parts = $line -split "`t"
    if ($parts.Length -ge 15) {
        $records += [PSCustomObject]@{
            日期 = $parts[0].Trim()
            时间 = $parts[1].Trim()
            股东代码 = $parts[2].Trim()
            证券代码 = $parts[3].Trim()
            证券名称 = $parts[4].Trim()
            委托类别 = $parts[5].Trim()
            成交价格 = [double]($parts[6].Trim() -replace '[^\d.]','')
            成交数量 = [double]($parts[7].Trim() -replace '[^\d.]','')
            成交金额 = [double]($parts[8].Trim() -replace '[^\d.-]','')
            发生金额 = [double]($parts[9].Trim() -replace '[^\d.-]','')
            佣金 = [double]($parts[10].Trim() -replace '[^\d.]','')
            印花税 = [double]($parts[11].Trim() -replace '[^\d.]','')
            过户费 = [double]($parts[12].Trim() -replace '[^\d.]','')
            其他费 = [double]($parts[13].Trim() -replace '[^\d.]','')
            成交编号 = $parts[14].Trim()
        }
    }
}
Write-Host "解析交易记录: $($records.Count) 条"

# 排除配号
$trades = $records | Where-Object { $_.委托类别 -in @("买入","卖出","买开","卖平") }
$peihao = $records | Where-Object { $_.委托类别 -eq "配号" }
Write-Host "有效买卖记录: $($trades.Count) 条 (配号 $($peihao.Count) 条)"

# 给每条记录加时段标签
$trades | ForEach-Object {
    $parts = $_.时间 -split ":"
    $h = [int]$parts[0]
    $m = [int]$parts[1]
    if ($h -eq 9) { $_ | Add-Member -NotePropertyName 时段 -NotePropertyValue "早盘9:30-10:00" -Force }
    elseif ($h -eq 10) { $_ | Add-Member -NotePropertyName 时段 -NotePropertyValue "上午中段10:00-11:30" -Force }
    elseif ($h -eq 11) { $_ | Add-Member -NotePropertyName 时段 -NotePropertyValue "午前收盘11:00-11:30" -Force }
    elseif ($h -eq 13) { $_ | Add-Member -NotePropertyName 时段 -NotePropertyValue "午盘13:00-14:00" -Force }
    elseif ($h -eq 14) { $_ | Add-Member -NotePropertyName 时段 -NotePropertyValue "尾盘14:00-15:00" -Force }
    else { $_ | Add-Member -NotePropertyName 时段 -NotePropertyValue "其他" -Force }
}

# 给每条记录加仓位标签
$trades | ForEach-Object {
    $amt = $_.成交金额
    if ($amt -le 5000) { $_ | Add-Member -NotePropertyName 仓位标签 -NotePropertyValue "小微<5千" -Force }
    elseif ($amt -le 20000) { $_ | Add-Member -NotePropertyName 仓位标签 -NotePropertyValue "小1-2万" -Force }
    elseif ($amt -le 50000) { $_ | Add-Member -NotePropertyName 仓位标签 -NotePropertyValue "中2-5万" -Force }
    elseif ($amt -le 100000) { $_ | Add-Member -NotePropertyName 仓位标签 -NotePropertyValue "中大5-10万" -Force }
    elseif ($amt -le 200000) { $_ | Add-Member -NotePropertyName 仓位标签 -NotePropertyValue "大10-20万" -Force }
    else { $_ | Add-Member -NotePropertyName 仓位标签 -NotePropertyValue "超大>20万" -Force }
}

$buyTrades = $trades | Where-Object { $_.委托类别 -eq "买入" }
$sellTrades = $trades | Where-Object { $_.委托类别 -eq "卖出" }

# =====================================================================
# ⑥ 择时能力分析
# =====================================================================
Write-Section "⑥ 择时能力分析"

Write-SubSection "各时段交易分布"
$timeGroups = $trades | Group-Object 时段
$timeSlotOrder = @("早盘9:30-10:00","上午中段10:00-11:30","午前收盘11:00-11:30","午盘13:00-14:00","尾盘14:00-15:00")
$totalTrades = $trades.Count

foreach ($slot in $timeSlotOrder) {
    $group = $timeGroups | Where-Object { $_.Name -eq $slot }
    if ($group) {
        $cnt = $group.Count
        $buy = ($group.Group | Where-Object { $_.委托类别 -eq "买入" }).Count
        $sell = ($group.Group | Where-Object { $_.委托类别 -eq "卖出" }).Count
        $buyAmt = ($group.Group | Where-Object { $_.委托类别 -eq "买入" } | Measure-Object -Property 成交金额 -Sum).Sum
        $sellAmt = ($group.Group | Where-Object { $_.委托类别 -eq "卖出" } | Measure-Object -Property 成交金额 -Sum).Sum
        Write-Host ("  {0,-18}: {1,4}笔 ({2,4:N1}%)  |  买入{3,3}笔({4,9:N0}元)  |  卖出{5,3}笔({6,9:N0}元)" -f $slot, $cnt, ($cnt/$totalTrades*100), $buy, $buyAmt, $sell, $sellAmt)
    }
}

Write-SubSection "买卖方向的时间偏好"
foreach ($slot in $timeSlotOrder) {
    $group = $timeGroups | Where-Object { $_.Name -eq $slot }
    if ($group) {
        $buy = ($group.Group | Where-Object { $_.委托类别 -eq "买入" }).Count
        $sell = ($group.Group | Where-Object { $_.委托类别 -eq "卖出" }).Count
        if ($buy -gt $sell) {
            Write-Host ("  {0}: 偏买入 (买{1}/卖{2}, 买多{3}笔)" -f $slot, $buy, $sell, ($buy-$sell))
        } elseif ($sell -gt $buy) {
            Write-Host ("  {0}: 偏卖出 (买{1}/卖{2}, 卖多{3}笔)" -f $slot, $buy, $sell, ($sell-$buy))
        } else {
            Write-Host ("  {0}: 均衡 (买{1}/卖{2})" -f $slot, $buy, $sell)
        }
    }
}

Write-SubSection "分钟级交易活跃度(TOP 15)"
$trades | Group-Object { $_.时间.Substring(0,5) } | Sort-Object Count -Descending | Select-Object -First 15 | ForEach-Object {
    Write-Host ("  {0}: {1}笔" -f $_.Name, $_.Count)
}

Write-SubSection "开盘(9:30-9:45) vs 收盘(14:30-15:00) 对比"
$morningOpen = $trades | Where-Object { $_.时间 -ge "09:30" -and $_.时间 -lt "09:45" }
$afternoonClose = $trades | Where-Object { $_.时间 -ge "14:30" -and $_.时间 -lt "15:00" }
$morningBuy = ($morningOpen | Where-Object { $_.委托类别 -eq "买入" }).Count
$morningSell = ($morningOpen | Where-Object { $_.委托类别 -eq "卖出" }).Count
$closeBuy = ($afternoonClose | Where-Object { $_.委托类别 -eq "买入" }).Count
$closeSell = ($afternoonClose | Where-Object { $_.委托类别 -eq "卖出" }).Count
Write-Host ("  开盘(9:30-9:45): {0,3}笔 (买入{1}, 卖出{2})" -f $morningOpen.Count, $morningBuy, $morningSell)
Write-Host ("  收盘(14:30-15:00): {0,3}笔 (买入{1}, 卖出{2})" -f $afternoonClose.Count, $closeBuy, $closeSell)

Write-SubSection "上午 vs 下午 交易量对比"
$amTrades = $trades | Where-Object { $_.时间 -lt "12:00" }
$pmTrades = $trades | Where-Object { $_.时间 -ge "12:00" }
Write-Host ("  上午({0}:00-{1}:30): {2,4}笔 ({3,4:N1}%)" -f 9, 11, $amTrades.Count, ($amTrades.Count/$totalTrades*100))
Write-Host ("  下午({0}:00-{1}:00): {2,4}笔 ({3,4:N1}%)" -f 13, 15, $pmTrades.Count, ($pmTrades.Count/$totalTrades*100))

# =====================================================================
# ⑦ 仓位管理分析
# =====================================================================
Write-Section "⑦ 仓位管理分析"

Write-SubSection "仓位分段统计"
$slotLabels = @("小微<5千","小1-2万","中2-5万","中大5-10万","大10-20万","超大>20万")
$positionGroups = $trades | Group-Object 仓位标签
foreach ($label in $slotLabels) {
    $group = $positionGroups | Where-Object { $_.Name -eq $label }
    if ($group) {
        $cnt = $group.Count
        $sumAmt = ($group.Group | Measure-Object -Property 成交金额 -Sum).Sum
        Write-Host ("  {0,-14}: {1,5}笔 ({2,4:N1}%), 累计{3,12:N0}元" -f $label, $cnt, ($cnt/$totalTrades*100), $sumAmt)
    }
}

Write-SubSection "仓位集中度分析"
$totalAmt = ($trades | Measure-Object -Property 成交金额 -Sum).Sum
$sortedDesc = $trades | Sort-Object 成交金额 -Descending
$topPct = @(0.01, 0.02, 0.05, 0.10, 0.20)
foreach ($p in $topPct) {
    $n = [Math]::Max(1, [int]($trades.Count * $p))
    $topN = $sortedDesc | Select-Object -First $n
    $topAmt = ($topN | Measure-Object -Property 成交金额 -Sum).Sum
    Write-Host ("  前{0,3}%交易(前{1,3}笔)占总金额: {2,4:N1}%" -f ($p*100), $n, ($topAmt/$totalAmt*100))
}

Write-SubSection "单笔最大交易 TOP 10"
$sortedDesc | Select-Object -First 10 | ForEach-Object {
    Write-Host ("  {0} {1} | {2,-8} | {3,8:N0}元 | {4}" -f $_.日期, $_.时间, $_.证券名称, $_.成交金额, $_.委托类别)
}

Write-SubSection "两账号仓位对比"
$trades | Group-Object 股东代码 | ForEach-Object {
    $g = $_.Group
    Write-Host ("`n  ===== 账号: {0} =====" -f $_.Name)
    Write-Host ("    总笔数: {0}" -f $g.Count)
    Write-Host ("    总金额: {0:N0}元" -f ($g | Measure-Object -Property 成交金额 -Sum).Sum)
    Write-Host ("    均价: {0:N0}元" -f ($g | Measure-Object -Property 成交金额 -Average).Average)
    $sortedG = $g | Sort-Object 成交金额
    $midIdx = [int]($g.Count/2)
    Write-Host ("    中位数: {0:N0}元" -f $sortedG[$midIdx].成交金额)
    Write-Host ("    最大值: {0:N0}元" -f ($g | Measure-Object -Property 成交金额 -Maximum).Maximum)
    Write-Host ("    最小值: {0:N0}元" -f ($g | Measure-Object -Property 成交金额 -Minimum).Minimum)
    $g75 = $sortedG[[int]($g.Count*0.75)].成交金额
    $g25 = $sortedG[[int]($g.Count*0.25)].成交金额
    Write-Host ("    Q1(25%): {0:N0}元, Q3(75%): {1:N0}元" -f $g25, $g75)
}

# =====================================================================
# ⑤ 交易成本分析
# =====================================================================
Write-Section "⑤ 交易成本分析"

# 计算佣金率(万分比)
$tradesWithRate = $trades | Where-Object { $_.成交金额 -gt 0 } | ForEach-Object {
    $commRate = if ($_.佣金 -gt 0) { $_.佣金 / $_.成交金额 * 10000 } else { 0 }
    $stampRate = if ($_.印花税 -gt 0) { $_.印花税 / $_.成交金额 * 10000 } else { 0 }
    $_ | Add-Member -NotePropertyName 佣金率(万) -NotePropertyValue $commRate -Force
    $_ | Add-Member -NotePropertyName 印花税率(万) -NotePropertyValue $stampRate -Force
    $_
}

Write-SubSection "佣金率分析"
$commRates = $tradesWithRate | Where-Object { $_."佣金率(万)" -gt 0 } | ForEach-Object { $_."佣金率(万)" }

if ($commRates.Count -gt 0) {
    $commRatesSorted = $commRates | Sort-Object
    $avgComm = ($commRates | Measure-Object -Average).Average
    $medComm = $commRatesSorted[[int]($commRatesSorted.Count/2)]
    Write-Host ("  平均佣金率: {0:F2}‱ (万分之{0:F2})" -f $avgComm)
    Write-Host ("  中位佣金率: {0:F2}‱" -f $medComm)
    Write-Host ("  P5~P95区间: {0:F2}‱ ~ {1:F2}‱" -f $commRatesSorted[[int]($commRatesSorted.Count*0.05)], $commRatesSorted[[int]($commRatesSorted.Count*0.95)])

    # 佣金率分布
    Write-SubSection "佣金率分布"
    $commHist = @{ "0~0.5‱"=0; "0.5~1‱"=0; "1~1.5‱"=0; "1.5~2‱"=0; "2~2.5‱"=0; "2.5~3‱"=0; "3~4‱"=0; "4~5‱"=0; ">5‱"=0 }
    foreach ($r in $commRates) {
        if ($r -le 0.5) { $commHist["0~0.5‱"]++ }
        elseif ($r -le 1) { $commHist["0.5~1‱"]++ }
        elseif ($r -le 1.5) { $commHist["1~1.5‱"]++ }
        elseif ($r -le 2) { $commHist["1.5~2‱"]++ }
        elseif ($r -le 2.5) { $commHist["2~2.5‱"]++ }
        elseif ($r -le 3) { $commHist["2.5~3‱"]++ }
        elseif ($r -le 4) { $commHist["3~4‱"]++ }
        elseif ($r -le 5) { $commHist["4~5‱"]++ }
        else { $commHist[">5‱"]++ }
    }
    $commHist.GetEnumerator() | Sort-Object Name | ForEach-Object {
        Write-Host ("  {0}: {1}笔 ({2:F1}%)" -f $_.Key, $_.Value, ($_.Value/$commRates.Count*100))
    }
}

Write-SubSection "分账号佣金率"
$tradesWithRate | Group-Object 股东代码 | ForEach-Object {
    $g = $_.Group
    $rates = $g | Where-Object { $_."佣金率(万)" -gt 0 } | ForEach-Object { $_."佣金率(万)" }
    if ($rates.Count -gt 0) {
        $avg = ($rates | Measure-Object -Average).Average
        Write-Host ("  {0}: 笔数{1}, 平均佣金率 {2:F2}‱" -f $_.Name, $rates.Count, $avg)
    }
}

Write-SubSection "费用结构汇总"
$totalCom = ($trades | Measure-Object -Property 佣金 -Sum).Sum
$totalStamp = ($trades | Measure-Object -Property 印花税 -Sum).Sum
$totalTrans = ($trades | Measure-Object -Property 过户费 -Sum).Sum
$totalFee = $totalCom + $totalStamp + $totalTrans
$totalTradeAmt = ($trades | Measure-Object -Property 成交金额 -Sum).Sum

Write-Host ("  总成交金额:                 {0,12:N0}元" -f $totalTradeAmt)
Write-Host ("  佣金总计:     {0,12:N2}元 (费率{1:F3}%, 交易额每万元{2:F2}元)" -f $totalCom, ($totalCom/$totalTradeAmt*100), ($totalCom/$totalTradeAmt*10000))
Write-Host ("  印花税总计:   {0,12:N2}元 (费率{1:F3}%)" -f $totalStamp, ($totalStamp/$totalTradeAmt*100))
Write-Host ("  过户费总计:   {0,12:N2}元 (费率{1:F4}%)" -f $totalTrans, ($totalTrans/$totalTradeAmt*100))
Write-Host ("  ─────────────────────────────────────")
Write-Host ("  全部费用合计: {0,12:N2}元 (总费率{1:F3}%)" -f $totalFee, ($totalFee/$totalTradeAmt*100))

# 印花税: 买入不收, 卖出收
$sellTradeAmt = ($sellTrades | Measure-Object -Property 成交金额 -Sum).Sum
$sellTotalStamp = ($sellTrades | Measure-Object -Property 印花税 -Sum).Sum
if ($sellTradeAmt -gt 0) {
    Write-Host ("`n  卖出时实际印花税率: {0:F2}‱ (万分之{0:F2}, 标准为万分之5)" -f ($sellTotalStamp/$sellTradeAmt*10000))
}

# =====================================================================
# ① 盈亏分析
# =====================================================================
Write-Section "① 盈亏分析"

$stockGroups = $trades | Group-Object 证券代码, 证券名称
$profitResults = @()

foreach ($sg in $stockGroups) {
    $codeName = $sg.Name
    $codeParts = $codeName -split ", "
    $code = $codeParts[0]
    $name = $codeParts[1]

    $buyRecords = $sg.Group | Where-Object { $_.委托类别 -eq "买入" }
    $sellRecords = $sg.Group | Where-Object { $_.委托类别 -eq "卖出" }

    $buyTotal = ($buyRecords | Measure-Object -Property 成交金额 -Sum).Sum
    $sellTotal = ($sellRecords | Measure-Object -Property 成交金额 -Sum).Sum
    $buyComm = ($buyRecords | Measure-Object -Property 佣金 -Sum).Sum
    $sellComm = ($sellRecords | Measure-Object -Property 佣金 -Sum).Sum
    $buyStamp = ($buyRecords | Measure-Object -Property 印花税 -Sum).Sum
    $sellStamp = ($sellRecords | Measure-Object -Property 印花税 -Sum).Sum
    $buyTrans = ($buyRecords | Measure-Object -Property 过户费 -Sum).Sum
    $sellTrans = ($sellRecords | Measure-Object -Property 过户费 -Sum).Sum

    $netProfit = $sellTotal - $buyTotal - $buyComm - $sellComm - $buyStamp - $sellStamp - $buyTrans - $sellTrans
    $buyQty = ($buyRecords | Measure-Object -Property 成交数量 -Sum).Sum
    $sellQty = ($sellRecords | Measure-Object -Property 成交数量 -Sum).Sum
    $remQty = $buyQty - $sellQty  # 可能还有持仓

    $profitResults += [PSCustomObject]@{
        代码 = $code
        名称 = $name
        买入额 = $buyTotal
        卖出额 = $sellTotal
        净利润 = $netProfit
        笔数 = $sg.Group.Count
        买入笔数 = $buyRecords.Count
        卖出笔数 = $sellRecords.Count
        买入数量 = $buyQty
        卖出数量 = $sellQty
        剩余数量 = $remQty
        总费用 = $buyComm + $sellComm + $buyStamp + $sellStamp + $buyTrans + $sellTrans
    }
}

# 只分析既有买又有卖的(已闭环或有部分持仓)
$closedStocks = $profitResults | Where-Object { $_.买入笔数 -gt 0 }

Write-SubSection "盈利 TOP 15"
$closedStocks | Sort-Object 净利润 -Descending | Select-Object -First 15 | ForEach-Object {
    $yield = if ($_.买入额 -gt 0) { $_.净利润 / $_.买入额 * 100 } else { 0 }
    Write-Host ("  {0,-6} {1,-8}: 净利润{2,9:N2}元 | 收益率{3,6:N2}% | {4}笔({5}买{6}卖) | 费用{7:N0}元" -f $_.代码, $_.名称, $_.净利润, $yield, $_.笔数, $_.买入笔数, $_.卖出笔数, $_.总费用)
}

Write-SubSection "亏损 TOP 15"
$closedStocks | Sort-Object 净利润 | Select-Object -First 15 | ForEach-Object {
    $yield = if ($_.买入额 -gt 0) { $_.净利润 / $_.买入额 * 100 } else { 0 }
    Write-Host ("  {0,-6} {1,-8}: 净利润{2,9:N2}元 | 收益率{3,6:N2}% | {4}笔({5}买{6}卖) | 费用{7:N0}元" -f $_.代码, $_.名称, $_.净利润, $yield, $_.笔数, $_.买入笔数, $_.卖出笔数, $_.总费用)
}

Write-SubSection "可能仍有持仓的股票(买入>卖出)"
$holdingStocks = $closedStocks | Where-Object { $_.剩余数量 -gt 0 } | Sort-Object 剩余数量 -Descending
Write-Host ("  持仓中股票: {0}只" -f $holdingStocks.Count)
$holdingStocks | Select-Object -First 10 | ForEach-Object {
    Write-Host ("  {0,-6} {1,-8}: 净买入{2,6}股, 成本{3,9:N0}元, 已卖回笼{4,9:N0}元" -f $_.代码, $_.名称, $_.剩余数量, $_.买入额, $_.卖出额)
}
if ($holdingStocks.Count -gt 10) {
    Write-Host ("  ...还有{0}只未列出" -f ($holdingStocks.Count - 10))
}

Write-SubSection "胜率汇总"
$winCount = ($closedStocks | Where-Object { $_.净利润 -gt 0 }).Count
$loseCount = ($closedStocks | Where-Object { $_.净利润 -le 0 }).Count
$totalAnalyzed = $closedStocks.Count
$totalProfit = ($closedStocks | Measure-Object -Property 净利润 -Sum).Sum
$totalBuyAll = ($closedStocks | Measure-Object -Property 买入额 -Sum).Sum
$totalSellAll = ($closedStocks | Measure-Object -Property 卖出额 -Sum).Sum

Write-Host ("  {0,-20}: {1}" -f "交易过股票总数", $totalAnalyzed)
Write-Host ("  {0,-20}: {1}只 ({2:N1}%)" -f "盈利股票", $winCount, ($winCount/$totalAnalyzed*100))
Write-Host ("  {0,-20}: {1}只 ({2:N1}%)" -f "亏损股票", $loseCount, ($loseCount/$totalAnalyzed*100))
Write-Host ("  {0,-20}: {1:N2}元" -f "总净利润", $totalProfit)
Write-Host ("  {0,-20}: {1:N2}%" -f "总收益率", ($totalProfit/$totalBuyAll*100))

Write-SubSection "ETF vs 个股盈亏对比"
$etfCodes = @("159","511","512","513","515","516","517","518","588")
$etfResults = $closedStocks | Where-Object {
    $found = $false
    foreach ($ec in $etfCodes) { if ($_.代码 -match "^$ec") { $found = $true; break } }
    $found
}
$stockResults = $closedStocks | Where-Object {
    $found = $false
    foreach ($ec in $etfCodes) { if ($_.代码 -match "^$ec") { $found = $true; break } }
    -not $found
}

$etfProfit = ($etfResults | Measure-Object -Property 净利润 -Sum).Sum
$stockProfit = ($stockResults | Measure-Object -Property 净利润 -Sum).Sum
$etfBuy = ($etfResults | Measure-Object -Property 买入额 -Sum).Sum
$stockBuy = ($stockResults | Measure-Object -Property 买入额 -Sum).Sum

Write-Host ("  ETF投资: {0}只, 净利润{1,9:N2}元, 收益率{2:N2}%" -f $etfResults.Count, $etfProfit, ($etfProfit/$etfBuy*100))
Write-Host ("  个股投资: {0}只, 净利润{1,9:N2}元, 收益率{2:N2}%" -f $stockResults.Count, $stockProfit, ($stockProfit/$stockBuy*100))

# =====================================================================
# ③ T+0识别分析
# =====================================================================
Write-Section "③ T+0识别分析"

$dailyStockGroups = $trades | Group-Object 日期, 证券代码, 证券名称
$t0Count = 0
$t0Details = @()

foreach ($ds in $dailyStockGroups) {
    $buyCount = ($ds.Group | Where-Object { $_.委托类别 -eq "买入" }).Count
    $sellCount = ($ds.Group | Where-Object { $_.委托类别 -eq "卖出" }).Count
    if ($buyCount -gt 0 -and $sellCount -gt 0) {
        $t0Count++
        $buyAmt = ($ds.Group | Where-Object { $_.委托类别 -eq "买入" } | Measure-Object -Property 成交金额 -Sum).Sum
        $sellAmt = ($ds.Group | Where-Object { $_.委托类别 -eq "卖出" } | Measure-Object -Property 成交金额 -Sum).Sum
        $parts = $ds.Name -split ", "
        $t0Details += [PSCustomObject]@{
            日期 = $parts[0]
            代码 = $parts[1]
            名称 = $parts[2]
            买入金额 = $buyAmt
            卖出金额 = $sellAmt
            总笔数 = $ds.Group.Count
            买入笔数 = $buyCount
            卖出笔数 = $sellCount
        }
    }
}

Write-Host ("  T+0交易日次数: {0}" -f $t0Count)
Write-Host ("  涉及不同股票数: {0}" -f (($t0Details | Group-Object 代码).Count))

$t0BuyTotal = ($t0Details | Measure-Object -Property 买入金额 -Sum).Sum
$t0SellTotal = ($t0Details | Measure-Object -Property 卖出金额 -Sum).Sum
Write-Host ("  T+0买入总金额: {0:N0}元" -f $t0BuyTotal)
Write-Host ("  T+0卖出总金额: {0:N0}元" -f $t0SellTotal)
Write-Host ("  占全部交易比例: {0:N1}%" -f ($t0Count/$totalTrades*100))

Write-SubSection "T+0最频繁股票 TOP 15"
$t0Details | Group-Object 代码, 名称 | Sort-Object Count -Descending | Select-Object -First 15 | ForEach-Object {
    $n = $_.Name
    $totalBuy = ($_.Group | Measure-Object -Property 买入金额 -Sum).Sum
    $totalSell = ($_.Group | Measure-Object -Property 卖出金额 -Sum).Sum
    Write-Host ("  {0}: {1}次, 买{2:N0}元/卖{3:N0}元" -f $n, $_.Count, $totalBuy, $totalSell)
}

Write-SubSection "T+0占比较高的股票(日常做T)"
$t0ByStock = $t0Details | Group-Object 代码, 名称 | Sort-Object Count -Descending
$stockTradeCounts = $trades | Group-Object 证券代码, 证券名称 | ForEach-Object { $_.Name }
foreach ($ts in $t0ByStock) {
    $totalForStock = ($trades | Where-Object { "$($_.证券代码), $($_.证券名称)" -eq $ts.Name }).Count
    $ratio = $ts.Count / $totalForStock * 100
    if ($ratio -gt 30 -and $ts.Count -ge 3) {
        Write-Host ("  {0}: T+0{1}次/总{2}次 = {3:N1}%, 高频做T" -f $ts.Name, $ts.Count, $totalForStock, $ratio)
    }
}

Write-SubSection "T+0日志摘要(前30条)"
$t0Details | Sort-Object 日期 | Select-Object -First 30 | ForEach-Object {
    Write-Host ("  {0} | {1,-6} {2,-8} | 买{3,3}笔{4,8:N0}元 + 卖{5,3}笔{6,8:N0}元" -f $_.日期, $_.代码, $_.名称, $_.买入笔数, $_.买入金额, $_.卖出笔数, $_.卖出金额)
}
if ($t0Details.Count -gt 30) {
    Write-Host ("  ...还有{0}条未显示" -f ($t0Details.Count - 30))
}

# =====================================================================
# 总结
# =====================================================================
Write-Section "综合分析结论"

Write-Host @"

1. 【择时风格】:
   - $(if ((($trades | Where-Object {$_._时间 -lt "12:00"}).Count) -gt (($trades | Where-Object {$_._时间 -ge "12:00"}).Count)) {"偏好上午交易"} else {"偏好下午交易"})
   - $(if ((($morningOpen.Count) -gt ($afternoonClose.Count))) {"开盘密集操作型"} else {"尾盘密集操作型"})

2. 【仓位风格】:
   - 总成交金额 $(if ($totalTradeAmt -gt 100000000) {"过亿"} if ($totalTradeAmt -gt 10000000) {"千万级"} else {"百万级"})
   - 属于 $(if (($trades | Where-Object {$_的成交金额 -le 50000}).Count / $totalTrades -gt 0.6) {"分散建仓型"} else {"中大型仓位型"})

3. 【交易成本】:
   - 佣金率 $(if ($avgComm -le 1.5) {"较低(≤1.5‱)"} elseif ($avgComm -le 3) {"中等(~2‱)"} else {"偏高(>3‱)"})
   - 总交易成本 $totalFee 元

4. 【盈亏表现】:
   - 胜率: $($winCount/$totalAnalyzed*100)N1%
   - 总净利润: $totalProfit 元
   - 总收益率: $($totalProfit/$totalBuyAll*100)N2%

5. 【交易模式】:
   - T+0 占比: $($t0Count/$totalTrades*100)N1%
   - $(if ($t0Count -gt 100) {"积极做T模式"} else {"轻度做T或纯趋势模式"})
"@

Write-Host "`n分析完成!"