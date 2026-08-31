"""日机验证_护型顶型.py — 按 DXAB护型 + 触顶/触哼(t顶/t哼) + 合顶 + 顶触 找日机（可复用验证流程）

用法：python 日机验证_护型顶型.py <股票代码> <起始日期> <结束日期>
示例：python 日机验证_护型顶型.py sz300659 2019/8/9 2019/9/6
      python 日机验证_护型顶型.py sz000002 2020/3/1 2020/6/1

数据源：昭明算展/谕组日/谕组日_<代码>.csv
核心列（据 VBA 导出代码 PX算研_RAP算展1引擎.bas XL算展取样调程_谕组单股通用 精确映射，勿信表头名）：
  [0]日期 [1]收 [2]开 [3]高 [4]低 [5]涨幅 [6]高幅
  [9]日层护型 [10]日层柱排 [13]日ZA [14]日ZC
  [17]日层机警 [19]日层BSHA [21]日层脸哼JA [22]日层宽哼JC [23]偏顶JC
  [30]上符串(触顶A/哼B/哈v/底w/无_)  [43]顶型(位os基顶型)  [44]日等型
  [45]仓日类(护级+护段，非顶型)
  [53]日龟BT顶(t顶)  [54]日龟BT哼(t哼)  [55]日龟顶触(龙a/龙b)  [56]日龟BT合顶哼
  [57]日基月局 [58]日基周局 [59]日基日局 [60]日基乾局 [61]日基坤局

主指标：上符串[30] + t顶[53] + t哼[54] + 顶触[55](龙a/龙b)；顶型[43]仅辅助
上符串编码（VBA 结算.bas）：A=触顶 B=触哼 v=触哈 w=触底 _=无
触顶=上符串右端'A'；合顶天数=从右往左连续'A'个数。
⚠️ 列53-61 需用户导入修改后正式版并重跑取样才有；旧CSV无这些列（t顶/t哼/顶触为空）。
"""
import io, sys, os, datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '昭明算展', '谕组日')

def parse_date(s):
    """兼容 2019/8/9 与 2019/08/09"""
    for fmt in ('%Y/%m/%d', '%Y-%m-%d', '%Y%m%d'):
        try: return datetime.datetime.strptime(s, fmt)
        except: pass
    raise ValueError(f"无法解析日期: {s}")

def safe(s):
    """安全取字符串值"""
    return s if s is not None else ''

def heding_days(s):
    """合顶天数 = 从右往左连续'A'个数"""
    n = 0
    for c in reversed(s or ''):
        if c == 'A': n += 1
        else: break
    return n

def hx_first(hx):
    """护型首字符 → 甲乙丙丁戊己"""
    for ch, name in [('a','甲'),('b','乙'),('c','丙'),('z','丁'),('y','戊'),('r','己')]:
        if hx.startswith(ch): return name
    return '?'

def touch_state(sf):
    """上符串右端 → 触顶/触哼/触哈/触底/无"""
    if not sf: return '无'
    m = {'A':'触顶','B':'触哼','v':'触哈','w':'触底'}
    return m.get(sf[-1], '无')

def load_csv(code):
    """加载谕组日CSV，返回 (表头, 行列表[每行是dict{日期,收,...}])"""
    path = os.path.join(DATA_DIR, f'谕组日_{code}.csv')
    if not os.path.exists(path):
        # 尝试补前缀
        for pfx in ('sz','sh','bj'):
            alt = os.path.join(DATA_DIR, f'谕组日_{pfx}{code}.csv')
            if os.path.exists(alt):
                path = alt; break
    if not os.path.exists(path):
        print(f"❌ 未找到文件: {path}")
        return None, None
    with open(path, encoding='gbk') as fh:
        lines = fh.readlines()
    hdr = lines[0].strip().split(',')
    rows = []
    for l in lines[1:]:
        c = l.strip().split(',')
        if len(c) < 51: continue
        try:
            dt = parse_date(c[0])
        except: continue
        rows.append({'line': len(rows)+1, 'date': dt, 'date_s': c[0],
                     '收': float(c[1]), '开': float(c[2]), '高': float(c[3]), '低': float(c[4]),
                     '涨幅': float(c[5]), '高幅': float(c[6]),
                     '护型': c[9], '柱排': c[10], 'ZA': float(c[13]), 'ZC': float(c[14]),
                     '日机警': c[17], 'BSHA': c[19], '脸哼JA': c[21], '宽哼JC': c[22], '偏顶JC': c[23],
                     '上符串': c[30], '上符范': c[29], '宽符串': c[31],
                     '顶型': c[43], '日等型': c[44], '仓日类': c[45], 'BTZA': c[41],
                     # 新增列(需用户导入重跑后才有)
                     't顶': safe(c[53]) if len(c)>53 else '', 't哼': safe(c[54]) if len(c)>54 else '',
                     '顶触': safe(c[55]) if len(c)>55 else '', '合顶哼': safe(c[56]) if len(c)>56 else '',
                     '日基月局': safe(c[57]) if len(c)>57 else '', '日基周局': safe(c[58]) if len(c)>58 else '',
                     '日基日局': safe(c[59]) if len(c)>59 else '', '日基乾局': safe(c[60]) if len(c)>60 else '',
                     '日基坤局': safe(c[61]) if len(c)>61 else ''})
    return hdr, rows

def analyze(code, start_s, end_s):
    """主流程：加载 → 过滤 → 输出微观指标表 → 找日机"""
    hdr, rows = load_csv(code)
    if rows is None: return
    start = parse_date(start_s); end = parse_date(end_s)

    # 过滤目标区间，含前后各2行做上下文
    idx = [i for i,r in enumerate(rows) if start <= r['date'] <= end]
    if not idx:
        print(f"❌ 区间 {start_s}~{end_s} 内无数据")
        return
    ctx_start = max(0, idx[0]-2); ctx_end = min(len(rows), idx[-1]+3)

    print(f"\n{'='*100}")
    print(f"【日机验证】{code}  {start_s} ~ {end_s}   (共 {len(idx)} 个交易日)")
    print(f"{'='*100}")

    # 输出微观指标表
    print(f"\n{'日期':<11}{'收':>7}{'涨幅':>7}{'高幅':>7} {'护型':<16}{'ZA':>3}{'ZC':>4} "
          f"{'上符串':<7}{'合顶':<3} {'t顶':>3} {'t哼':>3} {'顶触':<8} {'顶型':<6} {'日等型':<4} 日机标记")
    print('-'*118)
    for r in rows[ctx_start:ctx_end]:
        mark = ''
        if start <= r['date'] <= end:
            mark = judge(r)
        hd = heding_days(r['上符串'])
        print(f"{r['date_s']:<11}{r['收']:>7.2f}{r['涨幅']:>7.2f}{r['高幅']:>7.2f} "
              f"{r['护型']:<16}{r['ZA']:>3}{r['ZC']:>4} "
              f"{r['上符串']:<7}{hd:<3} {r['t顶']:>3} {r['t哼']:>3} {r['顶触']:<8} {r['顶型']:<6} {r['日等型']:<4} {mark}")

    print(f"\n{'='*100}")
    print("【日机标记说明】★=强烈介入/持有  ▲=可介入/关注  ●=转机/谨慎介入  ⚠=退出/回避")
    print("【主指标】上符串[30](触顶A/触哼B/合顶) + t顶[53] + t哼[54] + 顶触[55](龙a/龙b)；顶型[43]仅辅助")
    print(f"{'='*100}\n")

def judge(r):
    """按 DXAB护型 + 触顶/触哼(t顶/t哼) + 合顶 + 顶触 找日机
    主指标：上符串[30](触顶A/触哼B/合顶) + t顶[53] + t哼[54] + 顶触[55](龙a/龙b)
    辅助：顶型[43](a龙/b龙/c雀/d虎/e非/f武/*篪) — 仅作参考，非主指标
    """
    hf = hx_first(r['护型'])
    hd = heding_days(r['上符串'])
    touch = touch_state(r['上符串'])
    top = r['顶型'] or ''
    zc = r['ZC']
    za = r['ZA']
    t顶 = r['t顶']; t哼 = r['t哼']; 顶触 = r['顶触'] or ''
    # 顶触/龙ab 判断（周/日顶触，如 龙a/龙b/高/低/G0一高）
    is_long_touch = ('龙' in 顶触)     # 龙a/龙b
    is_a_long = ('a龙' in 顶触) or ('龙a' in 顶触)
    # 辅助顶型[43]类别
    is_hu = '虎' in top
    is_weak = '武' in top
    is_zhui = '篪' in top

    # 日机规则（主指标优先）
    if zc <= 0:
        # ZC<=0: 非前提区
        if '甲' in hf or '乙' in hf:
            return '▲ 转机观察(ZC<=0)'
        return ''
    # ZC>0 前提区
    # 顶型转弱优先（辅助）
    if is_hu or is_weak:
        return '⚠ 顶型转弱(虎/武)'
    if is_zhui and '甲' in hf:
        return '⚠ 甲+篪(ZA转负)'
    # 乙启动
    if '乙' in hf and touch == '触顶':
        return '★★ 乙启动日机(触顶)'
    # 甲
    if '甲' in hf and touch == '触顶' and hd >= 3 and is_a_long:
        return '★ 甲强日机(合顶'+str(hd)+'+'+顶触+')'
    if '甲' in hf and touch == '触顶' and hd >= 3:
        return '★ 甲强日机(合顶'+str(hd)+')'
    if '甲' in hf and touch == '触顶' and (is_long_touch or '龙' in top):
        return '★ 甲日机(触顶+多头)'
    if '甲' in hf and touch == '触顶':
        return '★ 甲日机(触顶)'
    # 己
    if '己' in hf and touch == '触顶':
        return '● 己触顶(观察转甲)'
    return ''

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)
    code = sys.argv[1]
    start_s = sys.argv[2]
    end_s = sys.argv[3]
    analyze(code, start_s, end_s)
