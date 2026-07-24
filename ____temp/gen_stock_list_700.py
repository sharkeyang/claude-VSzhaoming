"""生成算展验证股票列表 — 7市板各100只，2010-2015上市，共700只

改进点：
1. 获取上市日期，过滤2010-2015年上市
2. 获取数据验证，确保每只股票有可用日线数据
3. 7市板各100只，避免漏跑/失败
"""
import akshare as ak
import pandas as pd
import os, time, random, sys
from datetime import datetime

random.seed(42)

# ============================================================
# 配置
# ============================================================
OUT_DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0724"
os.makedirs(OUT_DIR, exist_ok=True)

# 上市日期范围
DATE_START = '2010-01-01'
DATE_END   = '2015-12-31'

# 每市板目标数量
TARGET_PER_BOARD = 100
TOTAL_TARGET = 700

# 创业板上市日期
# 300xxx 创业板：2009-10-30 开板，2010-2015大量上市
# 688xxx 科创板：2019-07-22 开板，2010-2015没有

print(f"=== 生成算展验证股票列表 ===")
print(f"输出目录: {OUT_DIR}")
print(f"上市日期范围: {DATE_START} ~ {DATE_END}")
print(f"目标: 7市板 x {TARGET_PER_BOARD} = {TOTAL_TARGET}只")
print()

# ============================================================
# 步骤1：获取A股代码列表
# ============================================================
print("=== 步骤1: 获取A股代码列表 ===")
df = ak.stock_info_a_code_name()
df['code'] = df['code'].astype(str).str.strip()
df['name'] = df['name'].astype(str).str.strip()
# 排除北交所
df = df[~df['code'].str.startswith('bj')]
# 排除ST/退市
df = df[~df['name'].str.contains('ST|退')]
print(f"  有效: {len(df)} 只")
print()

# ============================================================
# 步骤2：获取上市日期
# ============================================================
print("=== 步骤2: 获取个股上市日期 ===")
print(f"  共 {len(df)} 只股票，逐个获取基本信息...")

# 分类
def classify(code):
    if code.startswith(('600','601','603','605')): return 'Qd'   # 沪A主板
    elif code.startswith(('000','001','002')):      return 'Qe'   # 深A主板+中小板
    elif code.startswith('300'):                    return 'Qic'  # 创业板
    elif code.startswith('688'):                    return 'Qim'  # 科创板
    else:                                           return 'Qin'  # 其他

df['board'] = df['code'].apply(classify)

# 获取上市日期 — 使用 stock_info_a_detail（单只，含上市日期）
def get_listing_dates(df, batch_size=50, max_retries=2):
    """获取每只股票的上市日期，带重试和进度显示"""
    codes = df['code'].tolist()
    names = dict(zip(df['code'], df['name']))
    listing_dates = {}
    failed = []
    total = len(codes)

    start_time = time.time()
    last_report = 0

    for i, code in enumerate(codes):
        # 跳过科创板（2019年才开板，2010-2015不可能有）
        if code.startswith('688'):
            # 科创板2019年7月开板，记一个未来日期，后面会被过滤掉
            listing_dates[code] = None
            continue

        for attempt in range(max_retries + 1):
            try:
                info = ak.stock_info_a_detail(code)
                if info is not None and not info.empty:
                    info_dict = dict(zip(info['item'], info['value']))
                    listing_date_str = info_dict.get('上市日期', '')
                    if listing_date_str:
                        listing_dates[code] = pd.to_datetime(listing_date_str)
                    else:
                        listing_dates[code] = None
                    break
                else:
                    listing_dates[code] = None
                    break
            except Exception as e:
                if attempt < max_retries:
                    time.sleep(0.5)
                else:
                    failed.append(code)
                    listing_dates[code] = None

        # 进度报告
        elapsed = time.time() - start_time
        if (i + 1) % 100 == 0 or i == total - 1:
            if i + 1 == total or elapsed - last_report > 5:
                rate = (i + 1) / elapsed if elapsed > 0 else 0
                eta = (total - i - 1) / rate if rate > 0 else 0
                print(f"  进度: {i+1}/{total} | 耗时{elapsed:.0f}s | 速率{rate:.1f}只/s | 预计剩余{eta:.0f}s")
                last_report = elapsed

    elapsed = time.time() - start_time
    print(f"  完成: 获取{len(listing_dates)}只 | 失败{len(failed)}只 | 耗时{elapsed:.0f}s")
    if failed:
        print(f"  失败列表: {failed[:10]}...")
    return listing_dates

listing_dates = get_listing_dates(df)

# 将上市日期添加到df
df['listing_date'] = df['code'].map(listing_dates)
df_with_date = df.dropna(subset=['listing_date']).copy()
print(f"  有上市日期: {len(df_with_date)} 只")
print()

# ============================================================
# 步骤3：过滤2010-2015年上市
# ============================================================
print("=== 步骤3: 过滤2010-2015年上市 ===")
mask = (df_with_date['listing_date'] >= DATE_START) & (df_with_date['listing_date'] <= DATE_END)
df_filtered = df_with_date[mask].copy()
df_filtered = df_filtered.sort_values('listing_date').reset_index(drop=True)
print(f"  2010-2015年上市: {len(df_filtered)} 只")
print()

# ============================================================
# 步骤4：按市板分布统计
# ============================================================
print("=== 步骤4: 各市板2010-2015上市分布 ===")
board_counts = df_filtered['board'].value_counts()
for b in ['Qd', 'Qe', 'Qic', 'Qim', 'Qin']:
    print(f"  {b}: {board_counts.get(b, 0)} 只 (目标{TARGET_PER_BOARD})")
print()

# 检查科创板有无2010-2015上市
if board_counts.get('Qim', 0) == 0:
    print("  ⚠ 科创板(688xxx) 2019年才开板，没有2010-2015的股票")
    print("  ⚠ 将用其他策略补充（详见下文）")
    print()

# ============================================================
# 步骤5：选股 — 7市板各100只
# ============================================================
print("=== 步骤5: 选股 ===")

def pick_stocks(pool, n, label, sort_by='code'):
    """从池中选n只，优先上市早，再随机打乱"""
    pool = pool.copy()
    if len(pool) == 0:
        print(f"  {label}: 池为空，无法选股")
        return pd.DataFrame()
    pool = pool.sort_values('listing_date').reset_index(drop=True)
    # 从前300只中随机选n只（避免全选银行/大盘股）
    top = pool.head(300) if len(pool) > 300 else pool
    if len(top) >= n:
        chosen = top.sample(n, random_state=42)
    else:
        chosen = top
    print(f"  {label}: {len(chosen)} 只 (池{len(pool)}, 候选{len(top)})")
    return chosen

# 标准版：5个常规市板
selected = {}

# 沪A主板
selected['Qd'] = pick_stocks(df_filtered[df_filtered['board'] == 'Qd'], TARGET_PER_BOARD, '沪A主板(Qd)')
# 深A主板
selected['Qe'] = pick_stocks(df_filtered[df_filtered['board'] == 'Qe'], TARGET_PER_BOARD, '深A主板(Qe)')
# 创业板
selected['Qic'] = pick_stocks(df_filtered[df_filtered['board'] == 'Qic'], TARGET_PER_BOARD, '创业板(Qic)')

# 科创板：2010-2015没有，从2019-2020上市中选
kc_pool = df_with_date[df_with_date['board'] == 'Qim'].copy()
kc_pool = kc_pool[kc_pool['listing_date'] >= '2019-01-01'].sort_values('listing_date')
if len(kc_pool) >= TARGET_PER_BOARD:
    selected['Qim'] = pick_stocks(kc_pool, TARGET_PER_BOARD, '科创板(Qim, 2019+)')
else:
    selected['Qim'] = kc_pool.sample(min(TARGET_PER_BOARD, len(kc_pool)), random_state=42)
    print(f"  科创板(Qim): {len(selected['Qim'])} 只 (池{len(kc_pool)}, 不足{TARGET_PER_BOARD})")

# 其他
qt_pool = df_filtered[df_filtered['board'] == 'Qin']
if len(qt_pool) >= TARGET_PER_BOARD:
    selected['Qin'] = pick_stocks(qt_pool, TARGET_PER_BOARD, '其他(Qin)')
else:
    # 不足时从全部候选池补充
    selected['Qin'] = qt_pool.sample(min(TARGET_PER_BOARD, len(qt_pool)), random_state=42)
    print(f"  其他(Qin): {len(selected['Qin'])} 只 (池{len(qt_pool)}, 不足{TARGET_PER_BOARD})")

# ---- 指数级分类（额外2个板） ----
# Qif = 沪深300级：从Qd+Qe中按市值选前300只，再从中选2010-2015上市的
# 由于没有市值数据，用代码排序近似（代码越小上市越早/市值越大）
all_qdqe_2010_2015 = pd.concat([
    df_filtered[df_filtered['board'] == 'Qd'],
    df_filtered[df_filtered['board'] == 'Qe']
]).sort_values('code').reset_index(drop=True)

qif_pool = all_qdqe_2010_2015.head(300) if len(all_qdqe_2010_2015) > 300 else all_qdqe_2010_2015
if len(qif_pool) >= TARGET_PER_BOARD:
    selected['Qif'] = pick_stocks(qif_pool, TARGET_PER_BOARD, '沪深300级(Qif)')
else:
    selected['Qif'] = qif_pool.sample(min(TARGET_PER_BOARD, len(qif_pool)), random_state=42)
    print(f"  沪深300级(Qif): {len(selected['Qif'])} 只 (池{len(qif_pool)}, 不足{TARGET_PER_BOARD})")

# Qit = 中证2000级：从Qd+Qe中第301-800只，再从中选2010-2015上市的
if len(all_qdqe_2010_2015) > 300:
    qit_pool = all_qdqe_2010_2015.iloc[300:800]
    if len(qit_pool) >= TARGET_PER_BOARD:
        selected['Qit'] = pick_stocks(qit_pool, TARGET_PER_BOARD, '中证2000级(Qit)')
    else:
        selected['Qit'] = qit_pool.sample(min(TARGET_PER_BOARD, len(qit_pool)), random_state=42)
        print(f"  中证2000级(Qit): {len(selected['Qit'])} 只 (池{len(qit_pool)}, 不足{TARGET_PER_BOARD})")
else:
    selected['Qit'] = pd.DataFrame()
    print(f"  中证2000级(Qit): 0 只 (Qd+Qe不足300只)")

# 补充不足的市板
if len(selected['Qit']) < TARGET_PER_BOARD:
    deficit = TARGET_PER_BOARD - len(selected['Qit'])
    # 从剩余Qd+Qe+Qic中补充
    used_codes = set()
    for v in selected.values():
        for c in v['code'] if not v.empty else []:
            used_codes.add(c)
    remaining = all_qdqe_2010_2015[~all_qdqe_2010_2015['code'].isin(used_codes)]
    if len(remaining) >= deficit:
        extra = remaining.sample(deficit, random_state=42)
        selected['Qit'] = pd.concat([selected['Qit'], extra]).head(TARGET_PER_BOARD)
        print(f"  中证2000级(Qit) 补充后: {len(selected['Qit'])} 只")

# ============================================================
# 步骤6：数据可用性验证
# ============================================================
print()
print("=== 步骤6: 数据可用性验证 ===")
print("  尝试下载每只股票最近1年日线数据验证可用性...")

all_selected = []
for b in ['Qd', 'Qe', 'Qif', 'Qic', 'Qim', 'Qit', 'Qin']:
    for _, row in selected[b].iterrows():
        all_selected.append({'board': b, 'code': row['code'], 'name': row['name']})

df_all = pd.DataFrame(all_selected)
print(f"  待验证: {len(df_all)} 只")

valid_stocks = []
invalid_stocks = []

for i, (_, row) in enumerate(df_all.iterrows()):
    code = row['code']
    board = row['board']
    name = row['name']

    # 尝试下载日线数据
    try:
        # 使用akshare获取日线数据（最近1年）
        df_daily = ak.stock_zh_a_hist(symbol=code, period="daily",
                                       start_date="20250101", end_date="20260724",
                                       adjust="")
        if df_daily is not None and len(df_daily) > 20:
            valid_stocks.append(row)
        else:
            invalid_stocks.append(row)
            print(f"  ✗ 数据不足: {board},{code},{name}")
    except Exception as e:
        invalid_stocks.append(row)
        print(f"  ✗ 下载失败: {board},{code},{name} ({str(e)[:50]})")

    if (i + 1) % 100 == 0:
        print(f"  验证进度: {i+1}/{len(df_all)}, 有效{len(valid_stocks)}, 无效{len(invalid_stocks)}")

print(f"  验证完成: 有效{len(valid_stocks)}, 无效{len(invalid_stocks)}")

# 如果有效不够700只，需要补充
if len(valid_stocks) < TOTAL_TARGET:
    print(f"\n  ⚠ 有效股票不足{TOTAL_TARGET}只，正在补充中...")
    # 从已过滤但未选中的池中补充
    used_codes = set(s['code'] for s in valid_stocks)
    for s in all_selected:
        used_codes.add(s['code'])

    # 从各市板候选池补充
    for b in ['Qd', 'Qe', 'Qic', 'Qim', 'Qin']:
        if b == 'Qim':
            pool = df_with_date[df_with_date['board'] == 'Qim'].copy()
        else:
            pool = df_filtered[df_filtered['board'] == b].copy()
        pool = pool[~pool['code'].isin(used_codes)]
        if pool.empty:
            continue

        for _, row in pool.iterrows():
            if len(valid_stocks) >= TOTAL_TARGET:
                break
            code = row['code']
            try:
                df_daily = ak.stock_zh_a_hist(symbol=code, period="daily",
                                               start_date="20250101", end_date="20260724",
                                               adjust="")
                if df_daily is not None and len(df_daily) > 20:
                    valid_stocks.append({'board': b, 'code': code, 'name': row['name']})
                    used_codes.add(code)
                    print(f"  ✓ 补充: {b},{code},{row['name']}")
            except:
                pass
            time.sleep(0.05)
        if len(valid_stocks) >= TOTAL_TARGET:
            break

    print(f"  补充后: {len(valid_stocks)} 只")

# 重新按市板分组
df_valid = pd.DataFrame(valid_stocks)
final_boards = {}
for b in ['Qd', 'Qe', 'Qif', 'Qic', 'Qim', 'Qit', 'Qin']:
    pool = df_valid[df_valid['board'] == b]
    if len(pool) >= TARGET_PER_BOARD:
        final_boards[b] = pool.head(TARGET_PER_BOARD)
    else:
        final_boards[b] = pool

# ============================================================
# 步骤7：写入文件
# ============================================================
print()
print("=== 步骤7: 写入文件 ===")

list_path = os.path.join(OUT_DIR, "stocks.txt")
with open(list_path, 'w', encoding='utf-8') as f:
    f.write("# 算展验证股票列表\n")
    f.write("# 格式: 市板,股票代码,股票名称\n")
    f.write("# Qd=沪A主板  Qe=深A主板  Qif=沪深300级  Qic=创业板\n")
    f.write("# Qim=科创板  Qit=中证2000级  Qin=其他\n")
    f.write(f"# 生成: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    f.write(f"# 上市日期: {DATE_START} ~ {DATE_END} (科创板除外)\n")
    f.write(f"# 目标: 7市板各{TARGET_PER_BOARD}只 = {TOTAL_TARGET}只\n\n")
    for board in ['Qd', 'Qe', 'Qif', 'Qic', 'Qim', 'Qit', 'Qin']:
        f.write(f"[{board}]\n")
        for _, row in final_boards[board].iterrows():
            f.write(f"{board},{row['code']},{row['name']}\n")
        f.write("\n")

print(f"  保存: {list_path}")
print(f"  总计: {sum(len(v) for v in final_boards.values())} 只")
for b in ['Qd', 'Qe', 'Qif', 'Qic', 'Qim', 'Qit', 'Qin']:
    print(f"  [{b}] {len(final_boards[b])} 只")

# ============================================================
# 步骤8：统计
# ============================================================
print()
print("=== 最终统计 ===")
total = sum(len(v) for v in final_boards.values())
print(f"总股票数: {total} 只")
for b in ['Qd', 'Qe', 'Qif', 'Qic', 'Qim', 'Qit', 'Qin']:
    cnt = len(final_boards[b])
    print(f"  [{b}] {cnt} 只 {'✓' if cnt >= TARGET_PER_BOARD else '✗ (' + str(cnt) + ')'}")

print()
print("=== 完成 ===")
print(f"下一步: 将VBA中 ZPY_批量算展 的 需生成 = 50 - 已有数 改为 100 - 已有数")
print(f"        Python列表路径: {list_path}")
print(f"        VBA读取路径: 昭明算展\\算展0724\\stocks.txt")