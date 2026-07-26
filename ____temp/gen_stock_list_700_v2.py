"""生成算展验证股票列表 — 7市板各100只，共700只
基于花册CSV（本地数据，不依赖网络API）
"""
import pandas as pd
import os

OUT_DIR = r"D:\@VSwork\VS昭明计划VBA优化\昭明算展\算展0724"
os.makedirs(OUT_DIR, exist_ok=True)
TARGET = 100

# ============================================================
# 读取花册CSV
# ============================================================
print("=== 读取花册CSV ===")
df = pd.read_csv(r"D:\@VSwork\VS昭明计划VBA优化\____temp\市板映射.csv")
print(f"  花册总: {len(df)} 只")

# 排除北交所+ST
df = df[~df['代码'].str.startswith('bj')]
df = df[df['市板'] != 'Qst']
print(f"  排除北交所+ST: {len(df)} 只")

# 提取纯数字代码（去掉 sh/sz 前缀）
def 取数字码(code):
    if code.startswith('sh') or code.startswith('sz'):
        return code[2:]
    return code

df['数字码'] = df['代码'].apply(取数字码)
df['前缀3'] = df['数字码'].str[:3]

# ============================================================
# 分类：按代码前缀（与原脚本一致）
# ============================================================
print("\n=== 按代码前缀分类 ===")

def 分类(code):
    if code.startswith(('600','601','603','605')): return 'Qd'   # 沪A主板
    elif code.startswith(('000','001','002')):      return 'Qe'   # 深A主板
    elif code.startswith('300'):                    return 'Qic'  # 创业板
    elif code.startswith('688'):                    return 'Qim'  # 科创板
    else:                                           return 'Qin'  # 其他

df['7板'] = df['数字码'].apply(分类)

# 排除非股票数据（ETF/指数/基金等）
# 只保留：600,601,603,605,000,001,002,003,300,301,688 等A股代码
股票前缀 = ['600','601','603','605','000','001','002','003','300','301','688']
df = df[df['前缀3'].isin(股票前缀)]
print(f"  过滤后(A股): {len(df)} 只")

# 按代码排序
df = df.sort_values('数字码').reset_index(drop=True)

# 各板统计
for b in ['Qd','Qe','Qic','Qim','Qin']:
    cnt = len(df[df['7板'] == b])
    print(f"  {b}: {cnt} 只")

# ============================================================
# 构建Qif(沪深300级)和Qit(中证2000级)
# ============================================================
print("\n=== 构建指数级分类 ===")
all_qdqe = pd.concat([df[df['7板'] == 'Qd'], df[df['7板'] == 'Qe']]).sort_values('数字码').reset_index(drop=True)
print(f"  Qd+Qe 合计: {len(all_qdqe)} 只")

df_qif = all_qdqe.head(300).copy()
df_qif['7板'] = 'Qif'
df_qit = all_qdqe.iloc[300:800].copy() if len(all_qdqe) > 300 else pd.DataFrame()
if not df_qit.empty:
    df_qit['7板'] = 'Qit'
print(f"  Qif(沪深300级): {len(df_qif)} 只")
print(f"  Qit(中证2000级): {len(df_qit)} 只")

# 科创板：全部归入Qim
df_qim = df[df['7板'] == 'Qim'].copy()
print(f"  Qim(科创板): {len(df_qim)} 只")

# 创业板：全部归入Qic
df_qic = df[df['7板'] == 'Qic'].copy()
print(f"  Qic(创业板): {len(df_qic)} 只")

# 其他(Qin)：去掉已被Qif/Qit/Qic/Qim占用的
used_qd = set(df_qif['代码'].tolist() + df_qit['代码'].tolist())
df_qin = df[df['7板'] == 'Qin'].copy()
df_qin = df_qin[~df_qin['代码'].isin(used_qd)]
print(f"  Qin(其他): {len(df_qin)} 只")

# ============================================================
# 选股：各板均匀采样100只
# ============================================================
print("\n=== 选股 ===")

def 均匀采样(pool, n, label):
    """从池中均匀采样n只（按代码排序，等步长取）"""
    pool = pool.sort_values('数字码').reset_index(drop=True)
    if len(pool) == 0:
        print(f"  {label}: 空池，0只")
        return pd.DataFrame()
    if len(pool) <= n:
        print(f"  {label}: {len(pool)}/{n} 只 (池不足)")
        return pool
    step = len(pool) / n
    indices = [min(int(i * step), len(pool) - 1) for i in range(n)]
    result = pool.iloc[indices].copy()
    print(f"  {label}: {n}/{n} 只 (池{len(pool)}, 步长{step:.1f})")
    print(f"    代码范围: {result['数字码'].iloc[0]} ~ {result['数字码'].iloc[-1]}")
    return result

selected = {}
selected['Qd'] = 均匀采样(df[df['7板'] == 'Qd'], TARGET, '沪A主板(Qd)')
selected['Qe'] = 均匀采样(df[df['7板'] == 'Qe'], TARGET, '深A主板(Qe)')
selected['Qif'] = 均匀采样(df_qif, TARGET, '沪深300级(Qif)')
selected['Qic'] = 均匀采样(df_qic, TARGET, '创业板(Qic)')
selected['Qim'] = 均匀采样(df_qim, TARGET, '科创板(Qim)')
selected['Qit'] = 均匀采样(df_qit, TARGET, '中证2000级(Qit)')
selected['Qin'] = 均匀采样(df_qin, TARGET, '其他(Qin)')

# ============================================================
# 检查各板是否够100只，不足从全池补充
# ============================================================
print("\n=== 补充不足 ===")
used_codes = set()
for b in ['Qd','Qe','Qif','Qic','Qim','Qit','Qin']:
    for c in selected[b]['代码'] if not selected[b].empty else []:
        used_codes.add(c)

for b in ['Qd','Qe','Qif','Qic','Qim','Qit','Qin']:
    deficit = TARGET - len(selected[b])
    if deficit <= 0:
        continue
    # 从全池补充
    pool = df[~df['代码'].isin(used_codes)].copy()
    pool = pool.sort_values('数字码').reset_index(drop=True)
    if len(pool) >= deficit:
        step = len(pool) / deficit
        indices = [min(int(i * step), len(pool) - 1) for i in range(deficit)]
        extra = pool.iloc[indices]
        selected[b] = pd.concat([selected[b], extra])
        for c in extra['代码']:
            used_codes.add(c)
        print(f"  [{b}] 补充{deficit}只 → {len(selected[b])}只")
    else:
        selected[b] = pd.concat([selected[b], pool])
        print(f"  [{b}] 补充{len(pool)}只(不足) → {len(selected[b])}只")

# ============================================================
# 写入文件
# ============================================================
print("\n=== 写入文件 ===")
list_path = os.path.join(OUT_DIR, "stocks.txt")
with open(list_path, 'w', encoding='utf-8') as f:
    f.write("# 算展验证股票列表\n")
    f.write("# 格式: 市板,股票代码,股票名称\n")
    f.write("# Qd=沪A主板  Qe=深A主板  Qif=沪深300级  Qic=创业板\n")
    f.write("# Qim=科创板  Qit=中证2000级  Qin=其他\n")
    f.write("# 生成: 基于花册CSV(本地), 均匀采样\n\n")
    for board in ['Qd','Qe','Qif','Qic','Qim','Qit','Qin']:
        f.write(f"[{board}]\n")
        for _, row in selected[board].iterrows():
            f.write(f"{board},{row['代码']}\n")
        f.write("\n")

print(f"  保存: {list_path}")

# 统计
total = sum(len(v) for v in selected.values())
print(f"\n=== 最终统计 ===")
print(f"总股票数: {total} 只")
for b in ['Qd','Qe','Qif','Qic','Qim','Qit','Qin']:
    cnt = len(selected[b])
    print(f"  [{b}] {cnt} 只 {'✓' if cnt >= TARGET else '✗'}")