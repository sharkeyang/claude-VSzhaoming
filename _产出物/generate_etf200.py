"""批量从zdata生成算展(VBA COM) + 验证"""
import os, sys, datetime, time
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

BASE = r'd:\@VSwork\VS昭明计划VBA优化'
ZDATA = r'D:\zdata\data中股'
SUANZHAN = os.path.join(BASE, '昭明算展')
excel = None

def ensure_excel():
    global excel
    try:
        excel = win32com.client.GetActiveObject('Excel.Application')
    except:
        import win32com.client
        excel = win32com.client.Dispatch('Excel.Application')
    excel.Visible = False
    return excel

# 已有算展
existing = set()
for f in os.listdir(SUANZHAN):
    if f.startswith('算展.') and f.endswith('.xlsx'):
        code = f.replace('算展.','').replace('.xlsx','')
        existing.add(code)

print(f'已有算展: {len(existing)}')

# 读ETF200列表
import akshare as ak
targets = []
with open(os.path.join(BASE, '_产出物', 'etf200_list.txt'), 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 4:
            targets.append(parts[0])

need = [c for c in targets if c not in existing]
have_zdata = []
need_dl = []
for c in need:
    short = c.replace('sh','').replace('sz','')
    zf = os.path.join(ZDATA, f'{short}.csv')
    if os.path.exists(zf) and os.path.getsize(zf) > 1000:
        have_zdata.append(c)
    else:
        need_dl.append(c)

print(f'需从zdata生成: {len(have_zdata)}')
print(f'需下载: {len(need_dl)}')

# 1. 从zdata生成算展(VBA)
import win32com.client
print(f'\n[1/3] VBA生成算展(zdata → LD sheet)...')
excel = ensure_excel()

generated = 0
for code in have_zdata:
    fp = os.path.join(SUANZHAN, f'算展.{code}.xlsx')
    if os.path.exists(fp):
        continue
    try:
        # VBA: XL算展速成
        ret = excel.Application.Run("XL算展速成", code)
        if ret:
            generated += 1
            print(f'  ✓ {code}')
        else:
            print(f'  ✗ {code}: 0行')
    except Exception as e:
        print(f'  ✗ {code}: {e}')
    time.sleep(0.1)

print(f'生成: {generated}')

# 2. 下载缺失
print(f'\n[2/3] 下载缺失 {len(need_dl)}只...')
dl_ok = []
for i, code in enumerate(need_dl):
    short = code.replace('sh','').replace('sz','')
    zf = os.path.join(ZDATA, f'{short}.csv')
    try:
        print(f'  [{i+1}/{len(need_dl)}] {code}...', end=' ', flush=True)
        df = ak.fund_etf_hist_em(symbol=short, period='daily', start_date='20020101', end_date=datetime.date.today().strftime('%Y%m%d'), adjust='qfq')
        df.to_csv(zf, index=False, encoding='gbk')
        print(f'{len(df)}行')
        dl_ok.append(code)
        time.sleep(2)  # 2秒延迟避免限流
    except Exception as e:
        print(f'失败')
        time.sleep(3)  # 失败后更长时间

print(f'下载成功: {len(dl_ok)}')

# 3. 对下载成功的生成算展
print(f'\n[3/3] VBA生成新下载的...')
for code in dl_ok:
    try:
        ret = excel.Application.Run("XL算展速成", code)
        if ret:
            print(f'  ✓ {code}')
        else:
            print(f'  ✗ {code}: 0行')
    except:
        print(f'  ✗ {code}: 失败')
    time.sleep(0.1)

excel.Visible = True

# 统计最终结果
new_existing = set()
for f in os.listdir(SUANZHAN):
    if f.startswith('算展.') and f.endswith('.xlsx'):
        code = f.replace('算展.','').replace('.xlsx','')
        new_existing.add(code)

final_etfs = [c for c in targets if c in new_existing]
print(f'\n最终ETF数: {len(final_etfs)}/{len(targets)}')
print(f'总算展文件: {len(new_existing)}')