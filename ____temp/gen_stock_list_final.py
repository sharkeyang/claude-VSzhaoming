"""生成算展验证股票列表 — 7个市板各50只"""
import akshare as ak
import pandas as pd
import os, random
random.seed(42)

OUT_DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0718"
os.makedirs(OUT_DIR, exist_ok=True)

print("=== 获取A股代码列表 ===")
df = ak.stock_info_a_code_name()
df['code'] = df['code'].astype(str).str.strip()
df['name'] = df['name'].astype(str).str.strip()
# 排除北交所和ST
df = df[~df['code'].str.startswith('bj')]
df = df[~df['name'].str.contains('ST|退')]
print(f"有效: {len(df)} 只")

# 按前缀分类
def classify(code):
    if code.startswith(('600','601','603','605')): return 'Qd'
    elif code.startswith(('000','001','002')): return 'Qe'
    elif code.startswith('300'): return 'Qic'
    elif code.startswith('688'): return 'Qim'
    else: return 'Qin'

df['board'] = df['code'].apply(classify)

# 按代码排序(越小上市越早)
df = df.sort_values('code').reset_index(drop=True)

# 从各池取前300只中随机选50只
def pick50(pool, label):
    pool = pool.head(300) if len(pool) > 300 else pool
    if len(pool) >= 50:
        chosen = pool.sample(50, random_state=42)
    else:
        chosen = pool
    print(f"  {label}: {len(chosen)} 只 (池{len(pool)})")
    return chosen

# 沪深300级(Qif): 从Qd+Qe中取市值前300只
# 中证500级(Qic): 从Qd+Qe中取第301-800只
# 中证2000级(Qit): 从Qd+Qe+Qic中取剩余
# 这里简化：用代码排序代替市值排序
all_qdqe = pd.concat([df[df['board'] == 'Qd'], df[df['board'] == 'Qe']]).sort_values('code').reset_index(drop=True)
cy = df[df['board'] == 'Qic']
kc = df[df['board'] == 'Qim']
qt = df[df['board'] == 'Qin']

selected = {
    'Qd':  pick50(df[df['board'] == 'Qd'], '沪A主板(Qd)'),
    'Qe':  pick50(df[df['board'] == 'Qe'], '深A主板(Qe)'),
    'Qif': pick50(all_qdqe.head(300), '沪深300级(Qif)'),
    'Qic': pick50(cy, '创业板(Qic)'),
    'Qim': pick50(kc, '科创板(Qim)'),
    'Qit': pick50(all_qdqe.iloc[300:800] if len(all_qdqe) > 300 else pd.DataFrame(), '中证2000级(Qit)'),
    'Qin': pick50(qt, '其他(Qin)'),
}
# 如果Qit不够50只，从剩余补
if len(selected['Qit']) < 50:
    extra = all_qdqe.iloc[800:].sample(min(50-len(selected['Qit']), len(all_qdqe.iloc[800:])), random_state=42)
    selected['Qit'] = pd.concat([selected['Qit'], extra]).head(50)

# 写入文件
list_path = os.path.join(OUT_DIR, "stocks.txt")
with open(list_path, 'w', encoding='utf-8') as f:
    f.write("# 算展验证股票列表\n")
    f.write("# 格式: 市板,股票代码,股票名称\n")
    f.write("# Qd=沪A主板  Qe=深A主板  Qif=沪深300级  Qic=创业板  Qim=科创板  Qit=中证2000级  Qin=其他\n")
    f.write(f"# 生成: 2026-07-18  共7市板各50只\n\n")
    for board in ['Qd','Qe','Qif','Qic','Qim','Qit','Qin']:
        f.write(f"[{board}]\n")
        for _, row in selected[board].iterrows():
            f.write(f"{board},{row['code']},{row['name']}\n")
        f.write("\n")

print(f"\n=== 保存: {list_path} ===")
total = sum(len(v) for v in selected.values())
print(f"总计: {total} 只")
for b in ['Qd','Qe','Qif','Qic','Qim','Qit','Qin']:
    print(f"  [{b}] {len(selected[b])} 只")