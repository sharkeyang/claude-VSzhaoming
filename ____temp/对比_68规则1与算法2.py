# -*- coding: utf-8 -*-
"""
对比 §6.8 规则1（进入C+D即持有，不区分DXZE）与 算法2（多持介入，区分DXZE）的收益差异。
数据：昭明算展/谕组日/谕组日_*.csv（GBK，135列）
列索引：0=日期, 1=收, 5=涨幅, 17=日ZC, 18=日ZE, 69=DTZD, 71=DTCD
"""
import csv, glob, os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '昭明算展', '谕组日')

def load_rows(path):
    with open(path, encoding='gbk') as fh:
        r = csv.reader(fh)
        next(r)
        return list(r)

def parse_int(v):
    try:
        return int(float(v))
    except (ValueError, TypeError):
        return 0

def zone_of(zd, zc):
    """返回区域：C+D两线之上 / C-D两线之下 / MID中间区"""
    if zd > 0 and zc > 0:
        return 'C+D'
    elif zd < 0 and zc < 0:
        return 'C-D'
    else:
        return 'MID'

def simulate_rule1(rows):
    """§6.8 规则1：进入C+D即持有（不区分DXZE），直到C-D退出，中间区保持持有。
    注意：中间区保持持有（从C+D降入）或保持退出（从C-D升入）——按路径。
    """
    trades = []
    in_pos = False
    entry_idx = None
    entry_price = None
    for i, row in enumerate(rows):
        zd = parse_int(row[69])
        zc = parse_int(row[17])
        zone = zone_of(zd, zc)
        price = parse_int(row[1]) if row[1] else 0
        if not in_pos:
            # 未持仓：进入C+D即介入
            if zone == 'C+D':
                in_pos = True
                entry_idx = i
                entry_price = price if price else 0
        else:
            # 已持仓：C-D退出；中间区保持持有
            if zone == 'C-D':
                exit_price = price if price else 0
                if entry_price and exit_price:
                    ret = (exit_price - entry_price) / entry_price * 100
                else:
                    ret = 0
                trades.append((rows[entry_idx][0], row[0], ret, i - entry_idx))
                in_pos = False
    return trades

def calc_ri_ying(rows):
    """算法2：用底层列计算日层赢状态（多持/多截/空持/空截）"""
    states = []
    for row in rows:
        ze = parse_int(row[18])
        zd = parse_int(row[69])
        zc = parse_int(row[17])
        cd = parse_int(row[71])
        if zd > 0 and zc > 0:
            zone = 'C+D'
        elif zd < 0 and zc < 0:
            zone = 'C-D'
        else:
            zone = 'MID'
        if ze > 0:
            if zone == 'C+D':
                state = '多持'
            elif zone == 'C-D':
                state = '多截'
            else:
                if cd > 0:
                    state = '多持' if abs(zc) < abs(zd) else '多截'
                else:
                    state = '多持' if abs(zd) < abs(zc) else '多截'
        else:
            if zone == 'C-D':
                state = '空持'
            elif zone == 'C+D':
                state = '空截'
            else:
                if cd < 0:
                    state = '空截' if abs(zd) < abs(zc) else '空持'
                else:
                    state = '空截' if abs(zc) < abs(zd) else '空持'
        states.append(state)
    return states

def simulate_alg2(rows, states):
    """算法2：从多持介入，空截不退出，空持/多截退出"""
    trades = []
    in_pos = False
    entry_idx = None
    entry_price = None
    for i, row in enumerate(rows):
        state = states[i]
        price = parse_int(row[1]) if row[1] else 0
        if not in_pos:
            if state == '多持':
                in_pos = True
                entry_idx = i
                entry_price = price if price else 0
        else:
            if state == '空持' or state == '多截':
                exit_price = price if price else 0
                if entry_price and exit_price:
                    ret = (exit_price - entry_price) / entry_price * 100
                else:
                    ret = 0
                trades.append((rows[entry_idx][0], row[0], ret, i - entry_idx))
                in_pos = False
    return trades

def simulate_rule1_full(rows, states):
    """§6.8 完整执行（规则1+规则5，区分DXZE）：
    仅做多：C+D+ZE+（多持）介入持有；C+D+ZE-（空截）不介入；C-D退出；中间区按路径。
    即：从多持介入，空截不介入（但已持仓不退出），空持/多截退出。
    """
    trades = []
    in_pos = False
    entry_idx = None
    entry_price = None
    for i, row in enumerate(rows):
        state = states[i]
        price = parse_int(row[1]) if row[1] else 0
        if not in_pos:
            # 未持仓：仅多持（C+D+ZE+）介入
            if state == '多持':
                in_pos = True
                entry_idx = i
                entry_price = price if price else 0
        else:
            # 已持仓：空持/多截退出；空截不退出
            if state == '空持' or state == '多截':
                exit_price = price if price else 0
                if entry_price and exit_price:
                    ret = (exit_price - entry_price) / entry_price * 100
                else:
                    ret = 0
                trades.append((rows[entry_idx][0], row[0], ret, i - entry_idx))
                in_pos = False
    return trades

def stats(trades, label):
    if not trades:
        print(f'{label}: 无交易')
        return
    rets = [t[2] for t in trades]
    days = [t[3] for t in trades]
    pos = sum(1 for r in rets if r > 0)
    total = len(rets)
    avg = sum(rets) / total
    med = sorted(rets)[total // 2]
    cum = sum(rets)
    avg_days = sum(days) / total
    print(f'{label}:')
    print(f'  交易数={total}, 正收益={pos} ({pos/total*100:.1f}%), 平均={avg:.2f}%, 中位={med:.2f}%, 累计={cum:.1f}%, 平均持有={avg_days:.1f}天')

def main():
    files = sorted(glob.glob(os.path.join(DATA_DIR, '谕组日_*.csv')))
    t1, t2, t3 = [], [], []
    n = 0
    for f in files:
        rows = load_rows(f)
        if len(rows) < 100:
            continue
        n += 1
        t1.extend(simulate_rule1(rows))
        states = calc_ri_ying(rows)
        t2.extend(simulate_alg2(rows, states))
        t3.extend(simulate_rule1_full(rows, states))
        if n % 1000 == 0:
            print(f'  已处理 {n} 个文件...')
    print(f'有效文件数: {n}')
    print('=' * 60)
    stats(t1, '§6.8规则1（进入C+D即持有，不区分DXZE）')
    print('-' * 60)
    stats(t2, '算法2（多持介入，区分DXZE）')
    print('-' * 60)
    stats(t3, '§6.8完整执行（规则1+规则5，区分DXZE）')

if __name__ == '__main__':
    main()