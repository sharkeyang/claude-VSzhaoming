"""生成算展验证股票列表 — 基于A股代码列表"""
import akshare as ak
import pandas as pd
import os, random

random.seed(42)

OUT_DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0718"
os.makedirs(OUT_DIR, exist_ok=True)

print("=== 获取A股代码列表 ===")
df = ak.stock_info_a_code_name()
print(f"全量: {len(df)} 只")

df['code'] = df['code'].astype(str).str.strip()
df['name'] = df['name'].astype(str).str.strip()

# 排除北交所(bj开头)
df = df[~df['code'].str.startswith('bj')]

# 排除ST(按名称)
df = df[~df['name'].str.contains('ST|退')]

# 分类
def classify(code):
    if code.startswith(('600','601','603','605')):
        return 'Qd'   # 沪A主板
    elif code.startswith(('000','001','002')):
        return 'Qe'   # 深A主板+中小板
    elif code.startswith('300'):
        return 'Qic'  # 创业板
    elif code.startswith('688'):
        return 'Qim'  # 科创板
    else:
        return 'Qin'

df['board'] = df['code'].apply(classify)

# 沪A和深A按代码排序(代码越小上市越早)
# 从中选上市早+活跃的
def pick100_sorted(pool):
    pool = pool.sort_values('code').reset_index(drop=True)
    # 取前200只中随机选100（避免全选银行股）
    top = pool.head(200)
    if len(top) >= 100:
        chosen = top.sample(100, random_state=42)
    else:
        chosen = top
    return chosen

# 沪A: 取前200中随机100
sh_pool = df[df['board'] == 'Qd']
sh_chosen = pick100_sorted(sh_pool)

# 深A: 取前200中随机100
sz_pool = df[df['board'] == 'Qe']
sz_chosen = pick100_sorted(sz_pool)

# 创业板: 全部取(936只, 随机100)
cy_pool = df[df['board'] == 'Qic']
cy_chosen = cy_pool.sample(min(100, len(cy_pool)), random_state=42)

# 科创板: 全部取(609只, 随机100)
kc_pool = df[df['board'] == 'Qim']
kc_chosen = kc_pool.sample(min(100, len(kc_pool)), random_state=42)

# 其他: 随机100
qt_pool = df[df['board'] == 'Qin']
qt_chosen = qt_pool.sample(min(100, len(qt_pool)), random_state=42)

boards = {
    'Qd':  sh_chosen,
    'Qe':  sz_chosen,
    'Qic': cy_chosen,
    'Qim': kc_chosen,
    'Qin': qt_chosen,
}

# 写入文件
list_path = os.path.join(OUT_DIR, "stocks.txt")
with open(list_path, 'w', encoding='utf-8') as f:
    f.write("# 算展验证股票列表\n")
    f.write("# 格式: 市板,股票代码,股票名称\n")
    f.write("# Qd=沪A主板  Qe=深A主板  Qic=创业板  Qim=科创板  Qin=其他\n")
    f.write(f"# 生成: 2026-07-18\n\n")
    for board in ['Qd', 'Qe', 'Qic', 'Qim', 'Qin']:
        f.write(f"[{board}]\n")
        for _, row in boards[board].iterrows():
            f.write(f"{board},{row['code']},{row['name']}\n")
        f.write("\n")

print(f"\n=== 保存: {list_path} ===")
total = sum(len(v) for v in boards.values())
print(f"总计: {total} 只")
for b in ['Qd', 'Qe', 'Qic', 'Qim', 'Qin']:
    print(f"  [{b}] {len(boards[b])} 只")