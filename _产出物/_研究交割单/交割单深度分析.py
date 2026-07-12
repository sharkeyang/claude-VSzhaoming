#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交割单深度分析 — ⑥择时 → ⑦仓位 → ⑤成本 → ①盈亏 → ③T+0
"""

import csv
import os
import re
from collections import defaultdict, Counter

FILE_PATH = r'd:\@VSwork\VS昭明计划VBA优化\20260710交割单查询.txt'

def load_data(filepath):
    """加载GBK编码的空白分隔交割单数据"""
    records = []
    with open(filepath, 'r', encoding='gbk') as f:
        lines = f.readlines()

    print(f'总行数: {len(lines)}')

    for line in lines[3:]:  # skip header
        line = line.strip()
        if not line:
            continue
        parts = re.split(r'\s{3,}', line)
        if len(parts) < 15:
            continue
        try:
            rec = {
                '日期': parts[0].strip(),
                '时间': parts[1].strip(),
                '股东代码': parts[2].strip(),
                '证券代码': parts[3].strip(),
                '证券名称': parts[4].strip(),
                '委托类别': parts[5].strip(),
                '成交价格': float(parts[6].strip()),
                '成交数量': float(parts[7].strip()),
                '成交金额': float(parts[8].strip()),
                '发生金额': float(parts[9].strip()),
                '佣金': float(parts[10].strip()),
                '印花税': float(parts[11].strip()),
                '过户费': float(parts[12].strip()),
                '其他费': float(parts[13].strip()),
                '成交编号': parts[14].strip(),
            }
            records.append(rec)
        except (ValueError, IndexError):
            continue

    return records

def time_to_minutes(t):
    parts = t.split(':')
    return int(parts[0]) * 60 + int(parts[1])

def time_slot_label(t):
    m = time_to_minutes(t)
    if 570 <= m < 600:  # 9:30-10:00
        return '早盘9:30-10:00'
    elif 600 <= m < 690:  # 10:00-11:30
        return '上午中段10:00-11:30'
    elif 690 <= m < 720:  # 11:00-11:30 (sub of 10-11:30)
        return '午前收盘11:00-11:30'
    elif 780 <= m < 840:  # 13:00-14:00
        return '午盘13:00-14:00'
    elif 840 <= m < 900:  # 14:00-15:00
        return '尾盘14:00-15:00'
    else:
        return '其他时段'

def position_label(amt):
    if amt <= 5000:
        return '1小微<5千'
    elif amt <= 20000:
        return '2小1-2万'
    elif amt <= 50000:
        return '3中2-5万'
    elif amt <= 100000:
        return '4中大5-10万'
    elif amt <= 200000:
        return '5大10-20万'
    else:
        return '6超大>20万'

def print_sep(title):
    print(f'\n{"=" * 60}')
    print(f'  {title}')
    print(f'{"=" * 60}')

# ================================================================
# MAIN
# ================================================================
records = load_data(FILE_PATH)
print(f'解析交易记录: {len(records)} 条')

# 过滤有效买卖
trades = [r for r in records if r['委托类别'] in ('买入', '卖出')]
peihao = [r for r in records if r['委托类别'] == '配号']
print(f'有效买卖记录: {len(trades)} 条 (配号 {len(peihao)} 条)')

buy_trades = [r for r in trades if r['委托类别'] == '买入']
sell_trades = [r for r in trades if r['委托类别'] == '卖出']

# 添加派生字段
for r in trades:
    r['_time_min'] = time_to_minutes(r['时间'])
    r['_slot'] = time_slot_label(r['时间'])
    r['_position'] = position_label(r['成交金额'])

# =====================================================================
# ⑥ 择时能力分析
# =====================================================================
print_sep('⑥ 择时能力分析')

# 时段分布
slot_order = ['早盘9:30-10:00', '上午中段10:00-11:30', '午前收盘11:00-11:30',
              '午盘13:00-14:00', '尾盘14:00-15:00', '其他时段']
slot_counts = Counter(r['_slot'] for r in trades)
total = len(trades)

print('\n--- 各时段交易分布 ---')
for slot in slot_order:
    cnt = slot_counts.get(slot, 0)
    if cnt == 0:
        continue
    buys = sum(1 for r in trades if r['_slot'] == slot and r['委托类别'] == '买入')
    sells = sum(1 for r in trades if r['_slot'] == slot and r['委托类别'] == '卖出')
    buy_amt = sum(r['成交金额'] for r in trades if r['_slot'] == slot and r['委托类别'] == '买入')
    sell_amt = sum(r['成交金额'] for r in trades if r['_slot'] == slot and r['委托类别'] == '卖出')
    print(f'  {slot:<18}: {cnt:>4}笔 ({cnt/total*100:>4.1f}%)  |  买入{buys:>3}笔({buy_amt:>9,.0f}元)  |  卖出{sells:>3}笔({sell_amt:>9,.0f}元)')

# 买卖方向时间偏好
print('\n--- 买卖方向的时间偏好 ---')
for slot in slot_order:
    cnt = slot_counts.get(slot, 0)
    if cnt == 0:
        continue
    buys = sum(1 for r in trades if r['_slot'] == slot and r['委托类别'] == '买入')
    sells = sum(1 for r in trades if r['_slot'] == slot and r['委托类别'] == '卖出')
    if buys > sells:
        print(f'  {slot}: 偏买入 (买{buys}/卖{sells}, 买多{buys-sells}笔)')
    elif sells > buys:
        print(f'  {slot}: 偏卖出 (买{buys}/卖{sells}, 卖多{sells-buys}笔)')
    else:
        print(f'  {slot}: 均衡 (买{buys}/卖{sells})')

# 分钟级活跃度
print('\n--- 分钟级交易活跃度(TOP 15) ---')
minute_counter = Counter(r['时间'][:5] for r in trades)
for t, cnt in minute_counter.most_common(15):
    print(f'  {t}: {cnt}笔')

# 开盘 vs 收盘
morning_open = [r for r in trades if '09:30' <= r['时间'] < '09:45']
afternoon_close = [r for r in trades if '14:30' <= r['时间'] < '15:00']
print(f'\n--- 开盘 vs 收盘 对比 ---')
print(f'  开盘(9:30-9:45): {len(morning_open):>3}笔 '
      f'(买入{sum(1 for r in morning_open if r["委托类别"]=="买入")}, '
      f'卖出{sum(1 for r in morning_open if r["委托类别"]=="卖出")})')
print(f'  收盘(14:30-15:00): {len(afternoon_close):>3}笔 '
      f'(买入{sum(1 for r in afternoon_close if r["委托类别"]=="买入")}, '
      f'卖出{sum(1 for r in afternoon_close if r["委托类别"]=="卖出")})')

# 上午 vs 下午
am_trades = [r for r in trades if r['时间'] < '12:00']
pm_trades = [r for r in trades if r['时间'] >= '12:00']
print(f'\n--- 上午 vs 下午 交易量对比 ---')
print(f'  上午(9:30-11:30): {len(am_trades):>4}笔 ({len(am_trades)/total*100:.1f}%)')
print(f'  下午(13:00-15:00): {len(pm_trades):>4}笔 ({len(pm_trades)/total*100:.1f}%)')

# 各时段买卖金额净额
print('\n--- 各时段买卖净额 ---')
for slot in slot_order:
    cnt = slot_counts.get(slot, 0)
    if cnt == 0:
        continue
    buy_amt = sum(r['成交金额'] for r in trades if r['_slot'] == slot and r['委托类别'] == '买入')
    sell_amt = sum(r['成交金额'] for r in trades if r['_slot'] == slot and r['委托类别'] == '卖出')
    net = sell_amt - buy_amt
    direction = '净买入' if net < 0 else '净卖出' if net > 0 else '平衡'
    print(f'  {slot:<18}: 买{buy_amt:>9,.0f}元 / 卖{sell_amt:>9,.0f}元 / 净额{net:>+9,.0f}元 ({direction})')

# =====================================================================
# ⑦ 仓位管理分析
# =====================================================================
print_sep('⑦ 仓位管理分析')

pos_labels_ordered = ['1小微<5千', '2小1-2万', '3中2-5万', '4中大5-10万', '5大10-20万', '6超大>20万']
pos_counts = Counter(r['_position'] for r in trades)
total_amt = sum(r['成交金额'] for r in trades)

print('\n--- 仓位分段统计 ---')
for label in pos_labels_ordered:
    cnt = pos_counts.get(label, 0)
    if cnt == 0:
        continue
    amt = sum(r['成交金额'] for r in trades if r['_position'] == label)
    name = label[1:]  # remove sorting prefix
    print(f'  {name:<14}: {cnt:>5}笔 ({cnt/total*100:>4.1f}%), 累计{amt:>12,.0f}元 ({amt/total_amt*100:.1f}%)')

# 集中度
print('\n--- 仓位集中度分析 ---')
sorted_trades = sorted(trades, key=lambda r: r['成交金额'], reverse=True)
for pct in [0.01, 0.02, 0.05, 0.10, 0.20]:
    n = max(1, int(len(sorted_trades) * pct))
    top_n = sorted_trades[:n]
    top_amt = sum(r['成交金额'] for r in top_n)
    print(f'  前{pct*100:>3.0f}%交易(前{n:>3}笔)占总金额: {top_amt/total_amt*100:>4.1f}%')

# 单笔最大TOP 10
print('\n--- 单笔最大交易 TOP 10 ---')
for r in sorted_trades[:10]:
    print(f'  {r["日期"]} {r["时间"]} | {r["证券名称"]:<8} | {r["成交金额"]:>8,.0f}元 | {r["委托类别"]}')

# 两账号对比
print('\n--- 两账号仓位对比 ---')
for code in sorted(set(r['股东代码'] for r in trades)):
    group = [r for r in trades if r['股东代码'] == code]
    amounts = sorted([r['成交金额'] for r in group])
    n = len(amounts)
    print(f'\n  ===== 账号: {code} =====')
    print(f'    总笔数: {n}')
    print(f'    总金额: {sum(amounts):>12,.0f}元')
    print(f'    均价:   {sum(amounts)/n:>8,.0f}元' if n > 0 else '')
    print(f'    中位数: {amounts[n//2]:>8,.0f}元')
    print(f'    最大值: {max(amounts):>8,.0f}元')
    print(f'    最小值: {min(amounts):>8,.0f}元')
    print(f'    Q1(25%): {amounts[n//4]:>8,.0f}元, Q3(75%): {amounts[3*n//4]:>8,.0f}元')

# =====================================================================
# ⑤ 交易成本分析
# =====================================================================
print_sep('⑤ 交易成本分析')

# 佣金率
print('\n--- 佣金率分析 ---')
comm_rates = []
for r in trades:
    if r['成交金额'] > 0 and r['佣金'] > 0:
        comm_rates.append(r['佣金'] / r['成交金额'] * 10000)  # 万分比

if comm_rates:
    comm_rates_sorted = sorted(comm_rates)
    avg_comm = sum(comm_rates) / len(comm_rates)
    med_comm = comm_rates_sorted[len(comm_rates_sorted)//2]
    p5 = comm_rates_sorted[int(len(comm_rates_sorted)*0.05)]
    p95 = comm_rates_sorted[int(len(comm_rates_sorted)*0.95)]
    print(f'  平均佣金率: {avg_comm:.2f}%% (万分之{avg_comm:.2f})')
    print(f'  中位佣金率: {med_comm:.2f}%%')
    print(f'  P5 ~ P95区间: {p5:.2f}%% ~ {p95:.2f}%%')
    print(f'  最低佣金率: {comm_rates_sorted[0]:.2f}%%')
    print(f'  最高佣金率: {comm_rates_sorted[-1]:.2f}%%')

    # 佣金率分布
    print('\n--- 佣金率分布 ---')
    bins = [('0~0.5%%', 0, 0.5), ('0.5~1%%', 0.5, 1), ('1~1.5%%', 1, 1.5),
            ('1.5~2%%', 1.5, 2), ('2~2.5%%', 2, 2.5), ('2.5~3%%', 2.5, 3),
            ('3~4%%', 3, 4), ('4~5%%', 4, 5), ('>5%%', 5, 100)]
    for label, lo, hi in bins:
        cnt = sum(1 for r in comm_rates if lo <= r < hi)
        print(f'  {label}: {cnt}笔 ({cnt/len(comm_rates)*100:.1f}%)')

# 分账号佣金率
print('\n--- 分账号佣金率 ---')
for code in sorted(set(r['股东代码'] for r in trades)):
    group = [r for r in trades if r['股东代码'] == code]
    rates = [r['佣金']/r['成交金额']*10000 for r in group if r['成交金额'] > 0 and r['佣金'] > 0]
    if rates:
        print(f'  {code}: 笔数{len(rates)}, 平均佣金率 {sum(rates)/len(rates):.2f}%%')

# 费用结构
print('\n--- 费用结构汇总 ---')
total_com = sum(r['佣金'] for r in trades)
total_stamp = sum(r['印花税'] for r in trades)
total_trans = sum(r['过户费'] for r in trades)
total_other = sum(r['其他费'] for r in trades)
total_fee = total_com + total_stamp + total_trans + total_other
total_trade_amt = sum(r['成交金额'] for r in trades)

print(f'  总成交金额:               {total_trade_amt:>12,.0f}元')
print(f'  佣金总计:     {total_com:>12,.2f}元 (费率{total_com/total_trade_amt*100:.3f}%, '
      f'每万元{total_com/total_trade_amt*10000:.2f}元)')
print(f'  印花税总计:   {total_stamp:>12,.2f}元 (费率{total_stamp/total_trade_amt*100:.3f}%)')
print(f'  过户费总计:   {total_trans:>12,.2f}元 (费率{total_trans/total_trade_amt*100:.4f}%)')
print(f'  其他费总计:   {total_other:>12,.2f}元')
print(f'  ─────────────────────────────────────')
print(f'  全部费用合计: {total_fee:>12,.2f}元 (总费率{total_fee/total_trade_amt*100:.3f}%)')

# 卖出时印花税
sell_trade_amt = sum(r['成交金额'] for r in sell_trades)
sell_stamp = sum(r['印花税'] for r in sell_trades)
if sell_trade_amt > 0:
    print(f'\n  卖出时实际印花税率: {sell_stamp/sell_trade_amt*10000:.2f}%% (万分之{sell_stamp/sell_trade_amt*10000:.2f}, 标准为万分之5)')

# =====================================================================
# ① 盈亏分析
# =====================================================================
print_sep('① 盈亏分析')

# 按股票计算盈亏
stock_groups = defaultdict(list)
for r in trades:
    key = (r['证券代码'], r['证券名称'])
    stock_groups[key].append(r)

profit_results = []
for (code, name), group in stock_groups.items():
    buys = [r for r in group if r['委托类别'] == '买入']
    sells = [r for r in group if r['委托类别'] == '卖出']

    buy_total = sum(r['成交金额'] for r in buys)
    sell_total = sum(r['成交金额'] for r in sells)
    buy_com = sum(r['佣金'] for r in buys)
    sell_com = sum(r['佣金'] for r in sells)
    buy_stamp = sum(r['印花税'] for r in buys)
    sell_stamp = sum(r['印花税'] for r in sells)
    buy_trans = sum(r['过户费'] for r in buys)
    sell_trans = sum(r['过户费'] for r in sells)

    net_profit = sell_total - buy_total - buy_com - sell_com - buy_stamp - sell_stamp - buy_trans - sell_trans
    buy_qty = sum(r['成交数量'] for r in buys)
    sell_qty = sum(r['成交数量'] for r in sells)
    rem_qty = buy_qty - sell_qty

    profit_results.append({
        '代码': code,
        '名称': name,
        '买入额': buy_total,
        '卖出额': sell_total,
        '净利润': net_profit,
        '笔数': len(group),
        '买入笔数': len(buys),
        '卖出笔数': len(sells),
        '买入数量': buy_qty,
        '卖出数量': sell_qty,
        '剩余数量': rem_qty,
        '总费用': buy_com + sell_com + buy_stamp + sell_stamp + buy_trans + sell_trans,
    })

# 盈利 TOP 15
print('\n--- 盈利 TOP 15 ---')
for r in sorted(profit_results, key=lambda x: x['净利润'], reverse=True)[:15]:
    yield_pct = r['净利润'] / r['买入额'] * 100 if r['买入额'] > 0 else 0
    print(f'  {r["代码"]:<6} {r["名称"]:<8}: 净利润{r["净利润"]:>+9,.2f}元 | '
          f'收益率{yield_pct:>6.2f}% | {r["笔数"]}笔({r["买入笔数"]}买{r["卖出笔数"]}卖) | '
          f'费用{r["总费用"]:>7,.0f}元')

# 亏损 TOP 15
print('\n--- 亏损 TOP 15 ---')
for r in sorted(profit_results, key=lambda x: x['净利润'])[:15]:
    yield_pct = r['净利润'] / r['买入额'] * 100 if r['买入额'] > 0 else 0
    print(f'  {r["代码"]:<6} {r["名称"]:<8}: 净利润{r["净利润"]:>+9,.2f}元 | '
          f'收益率{yield_pct:>6.2f}% | {r["笔数"]}笔({r["买入笔数"]}买{r["卖出笔数"]}卖) | '
          f'费用{r["总费用"]:>7,.0f}元')

# 可能仍有持仓的股票
holdings = [r for r in profit_results if r['剩余数量'] > 0]
holdings.sort(key=lambda x: x['剩余数量'], reverse=True)
print(f'\n--- 可能仍有持仓的股票(买入>卖出) ---')
print(f'  持仓中股票: {len(holdings)}只')
for r in holdings[:10]:
    print(f'  {r["代码"]:<6} {r["名称"]:<8}: 净买入{r["剩余数量"]:>6,.0f}股, 成本{r["买入额"]:>9,.0f}元, 已卖回笼{r["卖出额"]:>9,.0f}元')
if len(holdings) > 10:
    print(f'  ...还有{len(holdings)-10}只未列出')

# 胜率
analyzed = [r for r in profit_results if r['买入笔数'] > 0]
win_count = sum(1 for r in analyzed if r['净利润'] > 0)
lose_count = sum(1 for r in analyzed if r['净利润'] <= 0)
total_profit = sum(r['净利润'] for r in analyzed)
total_buy_all = sum(r['买入额'] for r in analyzed)

print(f'\n--- 胜率汇总 ---')
print(f'  交易过股票总数:          {len(analyzed)}')
print(f'  盈利股票:                {win_count}只 ({win_count/len(analyzed)*100:.1f}%)')
print(f'  亏损股票:                {lose_count}只 ({lose_count/len(analyzed)*100:.1f}%)')
print(f'  总净利润:                {total_profit:>+12,.2f}元')
print(f'  总收益率:                {total_profit/total_buy_all*100:.2f}%')

# ETF vs 个股
etf_prefixes = ('159', '511', '512', '513', '515', '516', '517', '518', '588')
etf_profits = [r for r in analyzed if r['代码'].startswith(etf_prefixes)]
stock_profits = [r for r in analyzed if not r['代码'].startswith(etf_prefixes)]

etf_total_profit = sum(r['净利润'] for r in etf_profits)
stock_total_profit = sum(r['净利润'] for r in stock_profits)
etf_buy = sum(r['买入额'] for r in etf_profits)
stock_buy = sum(r['买入额'] for r in stock_profits)

print(f'\n--- ETF vs 个股盈亏对比 ---')
print(f'  ETF投资: {len(etf_profits)}只, 净利润{etf_total_profit:>+9,.2f}元, 收益率{etf_total_profit/etf_buy*100:.2f}%' if etf_buy > 0 else '')
print(f'  个股投资: {len(stock_profits)}只, 净利润{stock_total_profit:>+9,.2f}元, 收益率{stock_total_profit/stock_buy*100:.2f}%' if stock_buy > 0 else '')

# =====================================================================
# ③ T+0识别分析
# =====================================================================
print_sep('③ T+0识别分析')

# 按(日期, 股票)分组
daily_stock_groups = defaultdict(list)
for r in trades:
    key = (r['日期'], r['证券代码'], r['证券名称'])
    daily_stock_groups[key].append(r)

t0_details = []
for key, group in daily_stock_groups.items():
    buys = [r for r in group if r['委托类别'] == '买入']
    sells = [r for r in group if r['委托类别'] == '卖出']
    if buys and sells:
        buy_amt = sum(r['成交金额'] for r in buys)
        sell_amt = sum(r['成交金额'] for r in sells)
        t0_details.append({
            '日期': key[0],
            '代码': key[1],
            '名称': key[2],
            '买入金额': buy_amt,
            '卖出金额': sell_amt,
            '总笔数': len(group),
            '买入笔数': len(buys),
            '卖出笔数': len(sells),
        })

print(f'  T+0交易日次数: {len(t0_details)}')
t0_stocks = set((d['代码'], d['名称']) for d in t0_details)
print(f'  涉及不同股票数: {len(t0_stocks)}')

t0_buy_total = sum(d['买入金额'] for d in t0_details)
t0_sell_total = sum(d['卖出金额'] for d in t0_details)
print(f'  T+0买入总金额: {t0_buy_total:>10,.0f}元')
print(f'  T+0卖出总金额: {t0_sell_total:>10,.0f}元')
print(f'  T+0占全部交易比例: {len(t0_details)/len(trades)*100:.1f}%')

# T+0最频繁股票
t0_by_stock = defaultdict(list)
for d in t0_details:
    key = (d['代码'], d['名称'])
    t0_by_stock[key].append(d)

print(f'\n--- T+0最频繁股票 TOP 15 ---')
for (code, name), events in sorted(t0_by_stock.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
    total_buy = sum(e['买入金额'] for e in events)
    total_sell = sum(e['卖出金额'] for e in events)
    print(f'  {code:<6} {name:<8}: {len(events)}次, 买{total_buy:>8,.0f}元/卖{total_sell:>8,.0f}元')

# T+0占比高的股票
print(f'\n--- T+0占比较高的股票(日常做T) ---')
for (code, name), events in sorted(t0_by_stock.items(), key=lambda x: len(x[1]), reverse=True):
    total_for_stock = len(stock_groups.get((code, name), []))
    ratio = len(events) / total_for_stock * 100 if total_for_stock > 0 else 0
    if ratio > 30 and len(events) >= 3:
        print(f'  {code:<6} {name:<8}: T+0{len(events)}次/总{total_for_stock}次 = {ratio:.1f}%, 高频做T')

# T+0日志摘要
print(f'\n--- T+0日志摘要(前30条) ---')
for d in sorted(t0_details, key=lambda x: x['日期'])[:30]:
    print(f'  {d["日期"]} | {d["代码"]:<6} {d["名称"]:<8} | '
          f'买{d["买入笔数"]:>2}笔{d["买入金额"]:>8,.0f}元 + 卖{d["卖出笔数"]:>2}笔{d["卖出金额"]:>8,.0f}元')
if len(t0_details) > 30:
    print(f'  ...还有{len(t0_details)-30}条未显示')

# =====================================================================
# 总结
# =====================================================================
print_sep('综合分析结论')

# 择时风格
am_cnt = len(am_trades)
pm_cnt = len(pm_trades)
time_style = '偏好上午交易' if am_cnt > pm_cnt else '偏好下午交易'
open_close_style = '开盘密集操作型' if len(morning_open) > len(afternoon_close) else '尾盘密集操作型'

# 仓位风格
small_trades = sum(1 for r in trades if r['成交金额'] <= 50000)
position_style = '分散建仓型(小单为主)' if small_trades / total > 0.6 else '中大型仓位型'

# 佣金评级
avg_comm_rate = sum(comm_rates) / len(comm_rates) if comm_rates else 0
if avg_comm_rate <= 1.5:
    comm_rating = '较低(<=1.5万分)'
elif avg_comm_rate <= 3:
    comm_rating = '中等(约2万分)'
else:
    comm_rating = '偏高(>3万分)'

# T+0模式
t0_mode = '积极做T模式' if len(t0_details) > 100 else '轻度做T或纯趋势模式'

print(f'''
1. 【择时风格】:
   - {time_style} (上午{am_cnt}笔/下午{pm_cnt}笔, {am_cnt/pm_cnt:.2f}:1)
   - {open_close_style}
   - 最活跃时段: {slot_counts.most_common(1)[0][0] if slot_counts else "N/A"}

2. 【仓位风格】:
   - 总成交金额: {total_trade_amt/10000:.0f}万元
   - {position_style}
   - 单笔中位数: {sorted([r['成交金额'] for r in trades])[len(trades)//2]:,.0f}元

3. 【交易成本】:
   - 佣金率: {comm_rating} (平均{avg_comm_rate:.2f}万分之)
   - 总交易成本: {total_fee:,.2f}元
   - 总费率: {total_fee/total_trade_amt*100:.3f}%

4. 【盈亏表现】:
   - 胜率: {win_count}/{len(analyzed)} = {win_count/len(analyzed)*100:.1f}%
   - 总净利润: {total_profit:+,.2f}元
   - 总收益率: {total_profit/total_buy_all*100:.2f}%

5. 【交易模式】:
   - T+0 占比: {len(t0_details)}/{len(trades)} = {len(t0_details)/len(trades)*100:.1f}%
   - {t0_mode}
   - 最常做T股票: {
        ', '.join(f'{c} {n}' for c, n in [sorted(t0_by_stock.items(), key=lambda x: len(x[1]), reverse=True)[0][0]])
        if t0_by_stock else "N/A"} ({
        len(sorted(t0_by_stock.items(), key=lambda x: len(x[1]), reverse=True)[0][1])
        if t0_by_stock else 0}次)
''')

print('分析完成!')