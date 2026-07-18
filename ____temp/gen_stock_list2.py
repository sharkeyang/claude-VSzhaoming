"""生成算展验证股票列表 — 使用实时行情筛选活跃股"""
import akshare as ak
import pandas as pd
import os, random

OUT_DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0718"
os.makedirs(OUT_DIR, exist_ok=True)

print("=== 获取A股实时行情(含代码+名称+市值+换手率) ===")
df = ak.stock_zh_a_spot()
print(f"全量: {len(df)} 只")

# 过滤条件：有数据、有市值
df = df[df['代码'].notna()].copy()
df['代码'] = df['代码'].astype(str).str.strip()
df['名称'] = df.get('名称', '').astype(str).str.strip()

# 过滤ST/退市
df = df[~df['名称'].str.contains('ST|退|N')]
print(f"排除ST/退市: {len(df)} 只")

# 按交易所分类
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

df['市板'] = df['代码'].apply(classify)

# 按市值排序（市值大的代表活跃+上市早）
# 沪深300 = Qd+Qe中最大的300只 近似
# 中证500 = 第301-800只 近似
# 中证1000 = 第801-1800只
df = df.sort_values('流通市值', ascending=False) if '流通市值' in df.columns else df

# 划入各板
q_pool = df[df['市板'].isin(['Qd','Qe'])].copy()
cy_pool = df[df['市板'] == 'Qic'].copy()
kc_pool = df[df['市板'] == 'Qim'].copy()
qt_pool = df[df['市板'] == 'Qin'].copy()

# 从沪深A选出市值前300为Qif(沪深300级), 301-800为Qic(中证500级), 801-1800为Qim, 1801+为Qit
q_top300 = q_pool.head(300) if len(q_pool) > 300 else q_pool
q_301_800 = q_pool.iloc[300:800] if len(q_pool) > 800 else q_pool.iloc[300:]
q_801_1800 = q_pool.iloc[800:1800] if len(q_pool) > 1800 else q_pool.iloc[800:]
q_rest = q_pool.iloc[1800:] if len(q_pool) > 1800 else pd.DataFrame()

# 各板取100只（随机选以提高代表性）
def pick100(pool, label):
    pool = pool.copy()
    if len(pool) >= 100:
        chosen = pool.sample(100, random_state=42)
    else:
        chosen = pool
    print(f"  {label}: {len(chosen)} 只 (池{len(pool)})")
    return chosen

selected = {
    'Qif': pick100(q_top300, '沪深300级(Qif)'),
    'Qic': pick100(pd.concat([q_301_800, cy_pool]), '中证500级(Qic)'),
    'Qim': pick100(pd.concat([q_801_1800, kc_pool]), '中证1000级(Qim)'),
    'Qit': pick100(q_rest, '中证2000级(Qit)'),
    'Qd':  pick100(q_top300.head(100), '沪A主板(Qd)'),
    'Qe':  pick100(q_pool[q_pool['代码'].str.startswith(('000','001','002'))].head(300), '深A主板(Qe)'),
}

# 写入文件
list_path = os.path.join(OUT_DIR, "stocks.txt")
with open(list_path, 'w', encoding='utf-8') as f:
    f.write("# 算展验证股票列表\n")
    f.write("# 格式: 市板,股票代码,股票名称,用途说明\n")
    f.write("# Qd=沪A主板 Qe=深A主板 Qif=沪深300级 Qic=中证500级 Qim=中证1000级 Qit=中证2000级\n")
    f.write(f"# 生成: 2026-07-18\n\n")
    for board in ['Qd', 'Qe', 'Qif', 'Qic', 'Qim', 'Qit']:
        f.write(f"[{board}]\n")
        for _, row in selected[board].iterrows():
            name = row.get('名称', '')
            f.write(f"{board},{row['代码']},{name}\n")
        f.write("\n")

print(f"\n=== 保存: {list_path} ===")
total = sum(len(v) for v in selected.values())
print(f"总计: {total} 只")
for b in ['Qd', 'Qe', 'Qif', 'Qic', 'Qim', 'Qit']:
    print(f"  [{b}] {len(selected[b])} 只")