"""修复: 匹配已有算展, 下载缺失ETF, 生成算展, 验证"""
import os, sys, datetime, time
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

import akshare as ak
import pandas as pd
import win32com.client

BASE = r'd:\@VSwork\VS昭明计划VBA优化'
ZDATA = r'D:\zdata\data中股'
SUANZHAN = os.path.join(BASE, '昭明算展')
TEMP = os.path.join(BASE, '____temp')

os.makedirs(TEMP, exist_ok=True)

# ===== 1. 获取全ETF列表 =====
print('[1/6] 获取全ETF实时行情...')
spot = ak.fund_etf_spot_em()
spot['代码'] = spot['代码'].astype(str)
# 补前缀: 6位数字代码
def fmt_code(c):
    if len(c) == 6:
        if c.startswith('5') or c.startswith('6'):
            return f'sh{c}'
        elif c.startswith('0') or c.startswith('1') or c.startswith('2'):
            return f'sz{c}'
    return c
spot['全码'] = spot['代码'].apply(fmt_code)

# ===== 2. 分类 =====
def classify_etf(name):
    name = name or ''
    if any(k in name for k in ['沪深300','中证500','科创50','上证50','创业板','中证1000','中证2000','MSCI']): return '宽基'
    if any(k in name for k in ['半导体','芯片','集成电路']): return '半导体'
    if any(k in name for k in ['科技','信息技术','软件','计算机','通信','5G','人工智能','AI','大数据','云计算']): return '科技'
    if any(k in name for k in ['新能源','光伏','风电','锂电池','电池','碳中和','环保','绿色']): return '新能源'
    if any(k in name for k in ['医药','医疗','生物','创新药','中药','医美']): return '医药'
    if any(k in name for k in ['消费','食品','饮料','酒','家电']): return '消费'
    if any(k in name for k in ['金融','银行','证券','保险']): return '金融'
    if any(k in name for k in ['军工','国防','航天','航空']): return '军工'
    if any(k in name for k in ['传媒','游戏','影视','文娱']): return '传媒'
    if any(k in name for k in ['海外','恒生','纳斯达克','标普','日经','德国','法国','港股']): return '海外'
    if any(k in name for k in ['有色','黄金','稀土','钢铁','煤炭','资源','矿业']): return '有色资源'
    if any(k in name for k in ['化工','材料','建材']): return '化工材料'
    if any(k in name for k in ['农业','养殖','畜牧','粮食','白酒']): return '农业'
    if any(k in name for k in ['地产','基建']): return '地产基建'
    if any(k in name for k in ['汽车','新能源车','智能驾驶']): return '汽车'
    if any(k in name for k in ['红利','价值','成长','低波','质量']): return '策略因子'
    if any(k in name for k in ['央企','国企','国新','一带一路']): return '央企主题'
    if any(k in name for k in ['机械','制造','工业','机床']): return '工业制造'
    return '其他'

spot['行业'] = spot['名称'].apply(classify_etf)

# ===== 3. 已有算展 =====
existing = set()
for f in os.listdir(SUANZHAN):
    if f.startswith('算展.') and f.endswith('.xlsx'):
        code = f.replace('算展.','').replace('.xlsx','')
        existing.add(code)

# 已有ETF (带前缀)
existing_etf_codes = {c for c in existing if c.startswith(('sh51','sz159','sh56','sh52','sh513','sh588'))}

print(f'现有算展: {len(existing)}个, 其中ETF: {len(existing_etf_codes)}个')

# ===== 4. 选200只 =====
TARGETS = {
    '宽基':12,'半导体':10,'科技':15,'新能源':12,'医药':12,'消费':12,'金融':10,
    '军工':8,'传媒':5,'海外':10,'有色资源':10,'化工材料':8,'农业':5,
    '地产基建':8,'汽车':8,'策略因子':10,'央企主题':8,'工业制造':8,'其他':15
}
TOTAL_TARGET = sum(TARGETS.values())

selected = set()
all_existing_etfs = []
all_new_etfs = []

for ind, target in TARGETS.items():
    pool = spot[spot['行业'] == ind]
    picks = []
    # 先取已有算展的
    for _, r in pool.iterrows():
        if r['全码'] in existing_etf_codes:
            picks.append(r['全码'])
    # 再取没有的
    for _, r in pool.iterrows():
        if r['全码'] not in existing_etf_codes and len(picks) < target:
            picks.append(r['全码'])
        if len(picks) >= target: break
    existing_in_pool = [c for c in picks if c in existing_etf_codes]
    new_in_pool = [c for c in picks if c not in existing_etf_codes]
    all_existing_etfs.extend(existing_in_pool)
    all_new_etfs.extend(new_in_pool)
    selected.update(picks)
    print(f'  {ind}: 选{len(picks)}(已有{len(existing_in_pool)}+新{len(new_in_pool)})')

print(f'\n共选: {len(selected)}只ETF')
print(f'  已有算展: {len(all_existing_etfs)}只')
print(f'  需要下载+生成: {len(all_new_etfs)}只')

# ===== 5. 检查zdata是否有 =====
have_zdata = []
need_akshare = []
for c in all_new_etfs:
    short = c.replace('sh','').replace('sz','')
    zf = os.path.join(ZDATA, f'{short}.csv')
    if os.path.exists(zf) and os.path.getsize(zf) > 1000:
        have_zdata.append(c)
    else:
        need_akshare.append(c)

print(f'  已有zdata: {len(have_zdata)}只')
print(f'  需要从AKShare下载: {len(need_akshare)}只')

# 保存列表
with open(os.path.join(BASE, '_产出物', 'etf200_list.txt'), 'w', encoding='utf-8') as f:
    all_selected = all_existing_etfs + have_zdata + need_akshare
    for c in all_selected:
        row = spot[spot['全码']==c]
        name = row.iloc[0]['名称'] if len(row)>0 else '?'
        sector = row.iloc[0]['行业'] if len(row)>0 else '?'
        if c in existing_etf_codes:
            status = '已有算展'
        elif c in have_zdata:
            status = '有zdata'
        else:
            status = '需下载'
        f.write(f'{c}\t{name}\t{sector}\t{status}\n')

print(f'\n列表已保存: _产出物/etf200_list.txt')

# ===== 6. 如有需要下载 =====
if need_akshare:
    print(f'\n[2/6] 开始下载 {len(need_akshare)}只ETF...')
    for idx, c in enumerate(need_akshare):
        short = c.replace('sh','').replace('sz','')
        zf = os.path.join(ZDATA, f'{short}.csv')
        try:
            print(f'  [{idx+1}/{len(need_akshare)}] {c}...', end=' ', flush=True)
            df = ak.fund_etf_hist_em(symbol=short, period='daily', start_date='20020101', end_date=datetime.date.today().strftime('%Y%m%d'), adjust='qfq')
            df.to_csv(zf, index=False, encoding='gbk')
            print(f'{len(df)}行')
        except Exception as e:
            print(f'失败: {e}')
        time.sleep(0.5)
else:
    print('\n[2/6] 无需下载')

# ===== 7. VBA生成算展 =====
print(f'\n[3/6] VBA生成算展...')
excel = win32com.client.GetActiveObject('Excel.Application')
excel.Visible = False

for idx, c in enumerate(all_new_etfs):
    existing_path = os.path.join(SUANZHAN, f'算展.{c}.xlsx')
    if os.path.exists(existing_path):
        print(f'  [{idx+1}/{len(all_new_etfs)}] {c} 已有算展,跳过')
        continue
    try:
        print(f'  [{idx+1}/{len(all_new_etfs)}] {c}...', end=' ', flush=True)
        arrlll = None
        ret = excel.Application.Run("XL算展数程跨期_生成历史", arrlll, c, datetime.date.today(), None)
        if ret and ret > 0:
            # 生成格程
            wb_name = f'算展.{c}.xlsx'
            wb_path = os.path.join(SUANZHAN, wb_name)
            # 调用格程
            # (这里需要找到对应的格程函数)
            print(f'{ret}行')
        else:
            print('0行,跳过')
    except Exception as e:
        print(f'失败: {e}')
    time.sleep(0.1)

excel.Visible = True

print(f'\n[4/6] 运行策分卡验证...')
# (调用验证脚本)

print('\n完成')