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
    """触顶串右端 → 触顶/触哼/触哈/触底/无"""
    if not sf: return '无'
    m = {'A':'触顶','B':'触哼','v':'触哈','w':'触底'}
    return m.get(sf[-1], '无')

def load_csv(code):
    """加载谕组日CSV，按表头列名动态读取（不依赖硬编码列号，版本稳健）
    返回 (表头, 行列表[每行是dict{日期,收,...}])
    """
    path = os.path.join(DATA_DIR, f'谕组日_{code}.csv')
    if not os.path.exists(path):
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
    # 列名→索引映射
    col = {h.strip(): i for i, h in enumerate(hdr)}
    # 需要的列名（兼容新旧版本别名）
    def idx(*names):
        for n in names:
            if n in col: return col[n]
        return None
    # 动态检测触顶串列：字符集 ⊂ {A,B,v,w,_} 的那列即为触顶/合顶串
    # （新版CSV在[30]层界，旧版可能在别处；不能硬编码"上符串"列）
    ALLOWED = set('ABvw_')
    i触顶串 = None
    for cand in ('层界', '上符串'):
        ic = col.get(cand)
        if ic is None: continue
        # 抽查前200行，看是否主要为 A/B/v/w/_ 字符
        ok = True
        for l in lines[1:201]:
            cc = l.strip().split(',')
            if len(cc) <= ic: continue
            for ch in cc[ic]:
                if ch not in ALLOWED:
                    ok = False; break
            if not ok: break
        if ok:
            i触顶串 = ic
            break
    # 关键列索引
    i收=idx('收'); i开=idx('开'); i高=idx('高'); i低=idx('低')
    i涨幅=idx('涨幅'); i高幅=idx('高幅'); i护型=idx('DXAB','护型'); i柱排=idx('柱排')
    iZA=idx('日ZA'); iZC=idx('日ZC')
    iBSHA=idx('BSHA'); i脸哼JA=idx('脸哼JA'); i宽哼JC=idx('宽哼JC'); i偏顶JC=idx('偏顶JC')
    i上符串=idx('上符串'); i上符范=idx('上符范'); i宽符串=idx('宽符串')
    i顶型=idx('顶型'); i日等型=idx('日等型'); i仓日类=idx('仓日类'); iBTZA=idx('BTZA')
    # 新增列（谕组日龟/日基，需用户导入重跑后才有）
    iT顶=idx('日龟BT顶'); iT哼=idx('日龟BT哼'); i顶触=idx('日龟顶触'); i合顶哼=idx('日龟BT合顶哼')
    i基月=idx('日基月局'); i基周=idx('日基周局'); i基日=idx('日基日局'); i基乾=idx('日基乾局'); i基坤=idx('日基坤局')

    rows = []
    for l in lines[1:]:
        c = l.strip().split(',')
        if i收 is None or len(c) <= i收: continue
        try:
            dt = parse_date(c[0])
        except: continue
        def g(i):
            return c[i] if i is not None and i < len(c) else ''
        def gf(i):
            try: return float(g(i))
            except: return 0.0
        rows.append({'line': len(rows)+1, 'date': dt, 'date_s': c[0],
                     '收': gf(i收), '开': gf(i开), '高': gf(i高), '低': gf(i低),
                     '涨幅': gf(i涨幅), '高幅': gf(i高幅),
                     '护型': g(i护型), '柱排': g(i柱排), 'ZA': gf(iZA), 'ZC': gf(iZC),
                     '日机警': g(idx('日机警','日层机警')), 'BSHA': g(iBSHA),
                     '脸哼JA': g(i脸哼JA), '宽哼JC': g(i宽哼JC), '偏顶JC': g(i偏顶JC),
                     '触顶串': g(i触顶串), '上符串': g(i上符串), '上符范': g(i上符范), '宽符串': g(i宽符串),
                     '顶型': g(i顶型), '日等型': g(i日等型), '仓日类': g(i仓日类), 'BTZA': g(iBTZA),
                     't顶': g(iT顶), 't哼': g(iT哼), '顶触': g(i顶触), '合顶哼': g(i合顶哼),
                     '日基月局': g(i基月), '日基周局': g(i基周), '日基日局': g(i基日),
                     '日基乾局': g(i基乾), '日基坤局': g(i基坤)})
    return hdr, rows
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
          f"{'触顶串':<7}{'合顶':<3} {'t顶':>3} {'t哼':>3} {'顶触':<8} {'顶型':<6} {'日等型':<4} 日机标记")
    print('-'*118)
    for r in rows[ctx_start:ctx_end]:
        mark = ''
        if start <= r['date'] <= end:
            mark = judge(r)
        hd = heding_days(r['触顶串'])
        print(f"{r['date_s']:<11}{r['收']:>7.2f}{r['涨幅']:>7.2f}{r['高幅']:>7.2f} "
              f"{r['护型']:<16}{r['ZA']:>3}{r['ZC']:>4} "
              f"{r['触顶串']:<7}{hd:<3} {r['t顶']:>3} {r['t哼']:>3} {r['顶触']:<8} {r['顶型']:<6} {r['日等型']:<4} {mark}")

    print(f"\n{'='*100}")
    print("【日机标记说明】★=强烈介入/持有  ▲=可介入/关注  ●=转机/谨慎介入  ⚠=退出/回避")
    print("【主指标】触顶串(触顶A/触哼B/合顶) + t顶 + t哼 + 顶触(龙a/龙b)；顶型仅辅助")
    print(f"{'='*100}\n")

def judge(r):
    """按 DXAB护型 + 触顶/触哼(t顶/t哼) + 合顶 + 顶触 找日机
    主指标：触顶串(触顶A/触哼B/合顶) + t顶 + t哼 + 顶触(龙a/龙b)
    辅助：顶型(a龙/b龙/c雀/d虎/e非/f武/*篪) — 仅作参考，非主指标
    """
    hf = hx_first(r['护型'])
    hd = heding_days(r['触顶串'])
    touch = touch_state(r['触顶串'])
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
