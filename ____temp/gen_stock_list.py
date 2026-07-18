"""生成算展验证股票列表：各市板100只，2000-2010年上市+交易活跃"""
import akshare as ak
import pandas as pd
import os, time, random

OUT_DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0718"
os.makedirs(OUT_DIR, exist_ok=True)

print("=== 下载A股列表 ===")
df = ak.stock_info_a_code_name()
print(f"  全量: {len(df)} 只")

# 获取上市日期和退市信息
print("下载个股基本信息(含上市日期)...")
all_info = []
codes = df['code'].tolist()
batch_size = 50
for i in range(0, len(codes), batch_size):
    batch = codes[i:i+batch_size]
    for code in batch:
        try:
            info = ak.stock_info_a_detail(code)
            if info is not None and not info.empty:
                row = {'code': code}
                for _, r in info.iterrows():
                    row[r['item']] = r['value']
                all_info.append(row)
        except:
            pass
        time.sleep(0.1)
    print(f"  进度: {min(i+batch_size, len(codes))}/{len(codes)}, 成功: {len(all_info)}")

info_df = pd.DataFrame(all_info)
print(f"获取基本信息: {len(info_df)} 只")

# 解析上市日期
info_df['上市日期'] = pd.to_datetime(info_df.get('上市日期', pd.NaT), errors='coerce')
info_df = info_df.dropna(subset=['上市日期'])
# 过滤：2000-01-01 ~ 2010-12-31 之间上市
mask = (info_df['上市日期'] >= '2000-01-01') & (info_df['上市日期'] <= '2010-12-31')
info_df = info_df[mask].copy()
print(f"2000-2010年上市: {len(info_df)} 只")

# 按交易所分类
# 沪A: 600, 601, 603, 605开头; 深A: 000, 001, 002开头; 创业板: 300开头; 科创板: 688开头
def classify(code):
    if code.startswith(('600','601','603','605')):
        return 'Qd'  # 沪A主板
    elif code.startswith(('000','001','002')):
        return 'Qe'  # 深A主板+中小板
    elif code.startswith('300'):
        return 'Qic'  # 创业板 → 归入中证1000级
    elif code.startswith('688'):
        return 'Qim'  # 科创板 → 归入中证1000级
    else:
        return 'Qin'  # 其他

info_df['市板'] = info_df['code'].apply(classify)

# 各板选100只，优先选上市早+成交活跃的
# 按上市日期排序(越早越好)，再随机打乱以有代表性
boards = info_df['市板'].unique()
print(f"\n市板分布: {boards}")

selected = {}
for board in sorted(boards):
    pool = info_df[info_df['市板'] == board].copy()
    pool = pool.sort_values('上市日期')  # 优先上市早的
    # 前200只中随机选100只
    top = pool.head(200)
    if len(top) >= 100:
        chosen = top.sample(100, random_state=42)
    else:
        chosen = top  # 不够100就全取
    selected[board] = chosen
    print(f"  {board}: {len(chosen)} 只 (池{len(pool)})")

# 写入股票列表
list_path = os.path.join(OUT_DIR, "stocks.txt")
with open(list_path, 'w', encoding='utf-8') as f:
    f.write("# 算展验证股票列表\n")
    f.write("# 格式: 市板,股票代码,股票名称,上市日期\n")
    f.write("# 生成日期: 2026-07-18\n\n")
    for board in sorted(selected.keys()):
        f.write(f"[{board}]\n")
        for _, row in selected[board].iterrows():
            name = row.get('股票简称', row.get('code', ''))
            date = row['上市日期'].strftime('%Y-%m-%d')
            f.write(f"{board},{row['code']},{name},{date}\n")
        f.write("\n")

print(f"\n股票列表已保存: {list_path}")
print(f"总计: {sum(len(v) for v in selected.values())} 只")

# 统计
print("\n=== 各市板统计 ===")
for board in sorted(selected.keys()):
    print(f"  [{board}] {len(selected[board])} 只")