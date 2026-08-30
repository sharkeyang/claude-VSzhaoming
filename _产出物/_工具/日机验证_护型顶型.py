"""日机验证_护型顶型.py — 按 DXAB护型 + 日顶型 寻找日机（可复用验证流程）

用法：python 日机验证_护型顶型.py <股票代码> <起始日期> <结束日期> [--列宽]
示例：python 日机验证_护型顶型.py sz300659 2019/8/9 2019/9/6
      python 日机验证_护型顶型.py sz000002 2020/3/1 2020/6/1

数据源：昭明算展/谕组日/谕组日_<代码>.csv
核心列（据 VBA 导出代码 PX算研_RAP算展1引擎.bas 精确映射，勿信表头名）：
  [0]日期 [1]收 [2]开 [3]高 [4]低 [5]涨幅 [6]高幅
  [9]日层护型 [10]日层柱排 [13]日ZA [14]日ZC
  [17]日层机警 [19]日层BSHA [21]日层脸哼JA [22]日层宽哼JC [23]偏顶JC
  [30]上符串(触顶A/哼B/哈v/底w/无_)  [43]顶型(位os基顶型)  [44]日等型
  [45]仓日类(护级+护段，非顶型)

上符串编码（VBA 结算.bas）：A=触顶 B=触哼 v=触哈 w=触底 _=无
触顶=上符串右端'A'；合顶天数=从右往左连续'A'个数。
顶型[43]：如 龙/雀/虎/篪/武/非 等形态（前缀 _/a/b/c/d/e/K 等表示位置/级别）。
仓日类[45]：护级(上中下忐忠忑)首字 + 护段(甲乙丙丁戊己)首字，如 "上a"、"忐r"。
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
                     '顶型': c[43], '日等型': c[44], '仓日类': c[45], 'BTZA': c[41]})
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
          f"{'上符串':<7}{'触顶':<4}{'合顶':<3} {'顶型[43]':<6} {'日等型':<4} {'仓日类':<4} 日机标记")
    print('-'*115)
    for r in rows[ctx_start:ctx_end]:
        mark = ''
        if start <= r['date'] <= end:
            mark = judge(r)
        ts = touch_state(r['上符串'])
        hd = heding_days(r['上符串'])
        print(f"{r['date_s']:<11}{r['收']:>7.2f}{r['涨幅']:>7.2f}{r['高幅']:>7.2f} "
              f"{r['护型']:<16}{r['ZA']:>3}{r['ZC']:>4} "
              f"{r['上符串']:<7}{ts:<4}{hd:<3} {r['顶型']:<6} {r['日等型']:<4} {r['仓日类']:<4} {mark}")

    print(f"\n{'='*100}")
    print("【日机标记说明】★=强烈介入/持有  ▲=可介入/关注  ●=转机/谨慎介入  ⚠=退出/回避")
    print(f"{'='*100}\n")

def judge(r):
    """按 DXAB护型 + 日顶型[43] + 触顶/合顶 找日机
    顶型[43]编码（VBA 神谕.bas 4460-4525）：
      a龙=多头+触顶  b龙=多头+近顶  c雀=多头+顶弱  d虎=虎族(向下/返上风险)
      e非=非多头  f武=哼JA管下弱  *篪=多头但ZA转负(异常)  前缀_/K等=位置/级别
    """
    hf = hx_first(r['护型'])
    hd = heding_days(r['上符串'])
    touch = touch_state(r['上符串'])
    top = r['顶型'] or ''
    zc = r['ZC']
    za = r['ZA']
    # 提取顶型主体（去前缀，如 _a龙→a龙, Kc雀→c雀）
    body = top
    for pfx in ['a','b','c','d','e','f','K']:
        if body.startswith(pfx):
            body = body; break
    # 判断顶型类别
    is_long = ('龙' in top or '雀' in top)      # 多头排列
    is_zhui = '篪' in top                        # 多头但ZA转负(异常)
    is_weak = ('武' in top)                    # 哼JA管下弱(真弱)；e非=非多头过渡期非弱
    is_hu = '虎' in top                          # 虎族(风险)
    is_a_long = 'a龙' in top
    is_b_long = 'b龙' in top
    is_c_que = 'c雀' in top

    # 日机规则（基于正确顶型 + 验证结论 + 用户模型）
    if zc <= 0:
        # ZC<=0: 非前提区，只标记转机观察
        if '甲' in hf or '乙' in hf:
            return '▲ 转机观察(ZC<=0)'
        return ''
    # ZC>0 前提区
    # 顶型转弱优先（风险）：仅 虎(d)/武(f) 是真转弱；e非 是"非多头→多头"过渡期非转弱
    if is_hu or is_weak:
        return '⚠ 顶型转弱(虎/武)'
    if is_zhui and '甲' in hf:
        return '⚠ 甲+篪(ZA转负)'
    # 乙启动
    if '乙' in hf and touch == '触顶' and is_long:
        return '★★ 乙启动日机(顶'+body+')'
    if '乙' in hf and touch == '触顶':
        return '★ 乙日机(触顶)'
    # 甲
    if '甲' in hf and touch == '触顶' and hd >= 3 and is_a_long:
        return '★ 甲强日机(合顶'+str(hd)+'+a龙)'
    if '甲' in hf and touch == '触顶' and hd >= 3:
        return '★ 甲强日机(合顶'+str(hd)+')'
    if '甲' in hf and touch == '触顶' and is_long:
        return '★ 甲日机(触顶+多头)'
    if '甲' in hf and touch == '触顶':
        return '★ 甲日机(触顶)'
    if '甲' in hf and is_c_que:
        return '▲ 甲关注(c雀顶弱)'
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
