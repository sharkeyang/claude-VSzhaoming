# -*- coding: utf-8 -*-
import json

with open('_consolidated.json', encoding='utf-8') as f:
    DATA = json.load(f)

data_js = json.dumps(DATA, ensure_ascii=False, separators=(',', ':'))

HTML = r'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>同花顺 300033 · 单股行情与趋势速览</title>
<style>
  :root{
    --bg:#0b0f17; --bg2:#111827; --panel:#151c2c; --panel2:#1a2336;
    --line:#243049; --line2:#2e3b57;
    --txt:#e6edf7; --txt2:#9aa7bd; --txt3:#6b7a93;
    --up:#ff5d5d; --down:#2fd18a; --flat:#9aa7bd;
    --accent:#4f8cff; --accent2:#7aa8ff;
    --ma20:#ffb020; --ma60:#4f8cff; --ma120:#c084fc;
    --shadow:0 8px 30px rgba(0,0,0,.35);
    --radius:14px;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  html,body{background:var(--bg);color:var(--txt);
    font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",Roboto,Helvetica,Arial,sans-serif;
    -webkit-font-smoothing:antialiased;line-height:1.5}
  .wrap{max-width:1180px;margin:0 auto;padding:24px 20px 60px}

  /* Header */
  .topbar{display:flex;align-items:flex-end;justify-content:space-between;gap:16px;flex-wrap:wrap;margin-bottom:20px}
  .brand{display:flex;align-items:center;gap:14px}
  .logo{width:44px;height:44px;border-radius:12px;flex:none;
    background:linear-gradient(135deg,#4f8cff,#7a5cff);
    display:flex;align-items:center;justify-content:center;font-size:22px;box-shadow:var(--shadow)}
  .brand h1{font-size:22px;font-weight:700;letter-spacing:.5px}
  .brand .sub{font-size:12px;color:var(--txt3);margin-top:2px}
  .meta{text-align:right;font-size:12px;color:var(--txt3);line-height:1.7}
  .meta b{color:var(--txt2);font-weight:600}

  /* Price hero */
  .hero{display:flex;align-items:flex-end;gap:18px;flex-wrap:wrap;margin-bottom:18px}
  .hero .price{font-size:40px;font-weight:800;font-variant-numeric:tabular-nums;line-height:1}
  .hero .chg{font-size:16px;font-weight:700;margin-bottom:4px;font-variant-numeric:tabular-nums}
  .hero .chg.up{color:var(--up)} .hero .chg.down{color:var(--down)} .hero .chg.flat{color:var(--flat)}
  .hero .range{font-size:12px;color:var(--txt3);margin-bottom:2px}
  .hero .range b{color:var(--txt2);font-variant-numeric:tabular-nums}

  /* Stat strip */
  .stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:18px}
  .stat{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);padding:14px 16px}
  .stat .k{font-size:11px;color:var(--txt3);text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px}
  .stat .v{font-size:20px;font-weight:700;font-variant-numeric:tabular-nums}
  .stat .v small{font-size:12px;color:var(--txt3);font-weight:500;margin-left:4px}
  .stat .d{font-size:11px;color:var(--txt3);margin-top:4px}
  .stat .v.pos{color:var(--up)} .stat .v.neg{color:var(--down)}

  /* Panels */
  .panel{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);margin-bottom:18px;overflow:hidden}
  .panel-head{display:flex;align-items:center;justify-content:space-between;gap:12px;
    padding:14px 18px;border-bottom:1px solid var(--line);flex-wrap:wrap}
  .panel-head h2{font-size:15px;font-weight:700;display:flex;align-items:center;gap:9px}
  .panel-head .note{font-size:11px;color:var(--txt3)}
  .panel-body{padding:16px 18px}

  /* Chart controls */
  .controls{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
  .ctl{background:var(--panel2);border:1px solid var(--line);color:var(--txt2);
    padding:6px 14px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer;transition:all .15s;user-select:none}
  .ctl:hover{border-color:var(--line2);color:var(--txt)}
  .ctl.active{background:linear-gradient(135deg,rgba(79,140,255,.18),rgba(122,92,255,.12));
    border-color:var(--accent);color:var(--txt)}
  .ctl-sep{width:1px;height:20px;background:var(--line);margin:0 4px}

  /* Chart */
  #chartWrap{position:relative;width:100%;height:480px}
  #chart{width:100%;height:100%;display:block;touch-action:none}
  .chart-tooltip{position:absolute;pointer-events:none;background:rgba(11,15,23,.96);
    border:1px solid var(--line2);border-radius:10px;padding:10px 12px;font-size:12px;
    box-shadow:var(--shadow);opacity:0;transition:opacity .1s;z-index:20;min-width:170px}
  .chart-tooltip .tt-title{font-weight:700;margin-bottom:6px;font-size:13px}
  .chart-tooltip .tt-row{display:flex;justify-content:space-between;gap:16px;padding:2px 0}
  .chart-tooltip .tt-row .l{color:var(--txt3)}
  .chart-tooltip .tt-row .r{font-weight:600;font-variant-numeric:tabular-nums}
  .chart-tooltip .tt-row .r.up{color:var(--up)} .chart-tooltip .tt-row .r.down{color:var(--down)}
  .chart-legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px;color:var(--txt2);margin-top:10px}
  .chart-legend .item{display:flex;align-items:center;gap:6px}
  .chart-legend .sw{width:14px;height:3px;border-radius:2px}
  .chart-hint{font-size:11px;color:var(--txt3);margin-top:8px;display:flex;align-items:center;gap:6px;flex-wrap:wrap}
  .chart-hint .chip{background:var(--panel2);border:1px solid var(--line);padding:2px 9px;border-radius:20px;font-size:11px;color:var(--txt2)}
  .chart-hint .chip b{color:var(--txt)}

  /* Footer / disclaimer */
  .disclaimer{background:var(--panel);border:1px solid var(--line);border-radius:var(--radius);
    padding:16px 18px;font-size:12px;color:var(--txt3);line-height:1.8;margin-top:6px}
  .disclaimer b{color:var(--txt2)}
  .foot{text-align:center;font-size:11px;color:var(--txt3);margin-top:22px;line-height:1.8}

  @media (max-width:640px){
    .wrap{padding:16px 12px 40px}
    .brand h1{font-size:18px}
    .meta{text-align:left;margin-top:4px}
    .hero .price{font-size:32px}
    #chartWrap{height:400px}
    .panel-body{padding:12px}
    .ctl{padding:5px 10px;font-size:11px}
  }
</style>
</head>
<body>
<div class="wrap">

  <!-- Header -->
  <div class="topbar">
    <div class="brand">
      <div class="logo">&#128200;</div>
      <div>
        <h1>单股行情与趋势速览</h1>
        <div class="sub">Single-Stock Overview · 前复权日K</div>
      </div>
    </div>
    <div class="meta">
      <div>标的：<b id="metaCode">—</b></div>
      <div>数据时间：<b id="metaTime">—</b> · 前复权口径：<b>forward</b></div>
      <div>数据源：<b>同花顺 hithink-finance</b></div>
    </div>
  </div>

  <!-- Price hero -->
  <div class="hero">
    <div class="price" id="heroPrice">—</div>
    <div class="chg" id="heroChg">—</div>
    <div class="range" id="heroRange">—</div>
  </div>

  <!-- Stats -->
  <div class="stats" id="stats"></div>

  <!-- Chart -->
  <div class="panel">
    <div class="panel-head">
      <h2>&#128200; 日K线 · 前复权</h2>
      <div class="controls" id="controls">
        <span class="ctl-sep"></span>
        <span class="ctl" data-window="1M">1月</span>
        <span class="ctl" data-window="3M">3月</span>
        <span class="ctl" data-window="6M">6月</span>
        <span class="ctl active" data-window="1Y">1年</span>
        <span class="ctl" data-window="all">全部</span>
        <span class="ctl-sep"></span>
        <span class="ctl" id="btnReset" title="重置视图">&#8635; 重置</span>
      </div>
    </div>
    <div class="panel-body">
      <div id="chartWrap">
        <svg id="chart"></svg>
        <div class="chart-tooltip" id="tooltip"></div>
      </div>
      <div class="chart-legend" id="legend"></div>
      <div class="chart-hint" id="chartHint"></div>
    </div>
  </div>

  <!-- Disclaimer -->
  <div class="disclaimer">
    <b>数据说明：</b>本看板数据来自同花顺 hithink-finance 行情接口（快照 + 日K历史），日K为<b>前复权（forward）</b>口径，区间为 <span id="discRange">—</span>，共 <span id="discBars">—</span> 个交易日。快照为抓取时刻的最新报价，存在一定延迟，非实时行情。均线（MA20/60/120）与最大回撤基于前复权收盘价计算，仅作趋势参考。
    <br><br>
    <b>&#9888; 非投资建议：</b>本页面仅用于行情观察与数据展示，不构成任何投资建议、荐股或收益承诺。股市有风险，投资需谨慎。据此操作，风险自担。
  </div>

  <div class="foot">
    生成时间：<span id="genTime">&mdash;</span> · 数据源：同花顺 hithink-finance · 单文件离线看板，无外部依赖，无运行时请求
  </div>
</div>

<script>
const DATA = __DATA__;

// ---------- helpers ----------
const fmtNum = v => {
  if(v===null||v===undefined) return '—';
  return Number(v).toLocaleString('zh-CN',{maximumFractionDigits:2});
};
const fmtTurnover = v => {
  if(v>=1e8) return (v/1e8).toFixed(1)+'亿';
  if(v>=1e4) return (v/1e4).toFixed(1)+'万';
  return v.toLocaleString();
};
const fmtVol = v => {
  if(v>=1e8) return (v/1e8).toFixed(2)+'亿';
  if(v>=1e4) return (v/1e4).toFixed(1)+'万';
  return v.toLocaleString();
};
const UP='#ff5d5d', DOWN='#2fd18a';
const MA_COLORS={ma20:'#ffb020',ma60:'#4f8cff',ma120:'#c084fc'};

// ---------- state ----------
const records = DATA.records;
const N = records.length;
let viewStart = 0;      // index of first visible bar
let viewEnd = N-1;      // index of last visible bar
let hoverIdx = -1;      // hovered bar index
let windowMode = '1Y';  // current window preset

// ---------- window presets ----------
const WINDOWS = {
  '1M': 22, '3M': 66, '6M': 132, '1Y': 250, 'all': N
};
function applyWindow(mode){
  windowMode = mode;
  const count = WINDOWS[mode];
  viewEnd = N-1;
  viewStart = Math.max(0, N-count);
  document.querySelectorAll('.ctl[data-window]').forEach(c=>{
    c.classList.toggle('active', c.dataset.window===mode);
  });
  renderChart();
}

// ---------- render ----------
function renderAll(){
  renderHeader();
  renderStats();
  renderChart();
}

function renderHeader(){
  const s = DATA.snapshot;
  document.getElementById('metaCode').textContent = s.name+' ('+s.thscode+')';
  document.getElementById('metaTime').textContent = s.snapshot_time;
  document.getElementById('genTime').textContent = DATA.generated_at;
  document.getElementById('heroPrice').textContent = fmtNum(s.last_price);
  const ratio = s.price_change_ratio_pct;
  const cls = ratio>0?'up':ratio<0?'down':'flat';
  const arrow = ratio>0?'&#9650;':ratio<0?'&#9660;':'&#9644;';
  document.getElementById('heroChg').innerHTML = arrow+' '+fmtNum(s.price_change)+' ('+fmtNum(ratio)+'%)';
  document.getElementById('heroChg').className = 'chg '+cls;
  document.getElementById('heroRange').innerHTML =
    '今开 <b>'+fmtNum(s.open_price)+'</b> · 最高 <b>'+fmtNum(s.high_price)+'</b> · 最低 <b>'+fmtNum(s.low_price)+'</b> · 昨收 <b>'+fmtNum(s.prev_price)+'</b> · 成交额 <b>'+fmtTurnover(s.turnover)+'</b>';
  document.getElementById('discRange').textContent = DATA.metrics.first_date+' ~ '+DATA.metrics.last_date;
  document.getElementById('discBars').textContent = DATA.metrics.bars;
}

function renderStats(){
  const m = DATA.metrics;
  const stats = [
    {k:'区间涨跌幅', v:fmtNum(m.interval_return_pct)+'%', cls:m.interval_return_pct>=0?'pos':'neg', d:m.first_date+' ~ '+m.last_date},
    {k:'MA20', v:fmtNum(m.ma20), d:'20日均线'},
    {k:'MA60', v:fmtNum(m.ma60), d:'60日均线'},
    {k:'MA120', v:fmtNum(m.ma120), d:'120日均线'},
    {k:'近60日最大回撤', v:fmtNum(m.max_drawdown_60_pct)+'%', cls:'neg', d:'峰值至谷底'},
    {k:'20日均成交额', v:fmtTurnover(m.avg_turnover_20), d:'近20日平均'},
  ];
  document.getElementById('stats').innerHTML = stats.map(s=>
    '<div class="stat"><div class="k">'+s.k+'</div><div class="v '+(s.cls||'')+'">'+s.v+'</div><div class="d">'+s.d+'</div></div>'
  ).join('');
}

// ---------- chart ----------
const svg = document.getElementById('chart');
const wrap = document.getElementById('chartWrap');
const tooltip = document.getElementById('tooltip');

function renderChart(){
  const W = wrap.clientWidth, H = wrap.clientHeight;
  // Layout: price panel (top 70%) + volume panel (bottom 30%)
  const pad = {l:56, r:14, t:14, b:26};
  const priceH = Math.round((H-pad.t-pad.b)*0.70);
  const volH = (H-pad.t-pad.b) - priceH;
  const gap = 8;
  const iw = W-pad.l-pad.r;
  const priceTop = pad.t;
  const volTop = pad.t + priceH + gap;

  svg.setAttribute('viewBox', '0 0 '+W+' '+H);
  svg.innerHTML = '';

  // visible slice
  const vStart = viewStart, vEnd = viewEnd;
  const vCount = vEnd - vStart + 1;
  const slot = iw / vCount;
  const candleW = Math.max(1, Math.min(10, slot*0.7));

  // price domain (min low, max high over visible, plus MA)
  let minP = Infinity, maxP = -Infinity;
  for(let i=vStart;i<=vEnd;i++){
    const r = records[i];
    minP = Math.min(minP, r.low);
    maxP = Math.max(maxP, r.high);
    if(r.ma20) { minP=Math.min(minP,r.ma20); maxP=Math.max(maxP,r.ma20); }
    if(r.ma60) { minP=Math.min(minP,r.ma60); maxP=Math.max(maxP,r.ma60); }
    if(r.ma120){ minP=Math.min(minP,r.ma120); maxP=Math.max(maxP,r.ma120); }
  }
  const padP = (maxP-minP)*0.06 || 1;
  minP -= padP; maxP += padP;
  const yP = p => priceTop + (1-(p-minP)/(maxP-minP))*priceH;

  // volume domain
  let maxV = 0;
  for(let i=vStart;i<=vEnd;i++) maxV = Math.max(maxV, records[i].volume);
  const yV = v => volTop + (1-v/maxV)*volH;

  // gridlines (price)
  const gridN = 5;
  for(let g=0; g<=gridN; g++){
    const val = minP + (maxP-minP)*g/gridN;
    const yy = yP(val);
    const line = document.createElementNS('http://www.w3.org/2000/svg','line');
    line.setAttribute('x1',pad.l); line.setAttribute('x2',W-pad.r);
    line.setAttribute('y1',yy); line.setAttribute('y2',yy);
    line.setAttribute('stroke','#1c2740'); line.setAttribute('stroke-width','1');
    svg.appendChild(line);
    const t = document.createElementNS('http://www.w3.org/2000/svg','text');
    t.setAttribute('x',pad.l-8); t.setAttribute('y',yy+4);
    t.setAttribute('text-anchor','end'); t.setAttribute('font-size','10');
    t.setAttribute('fill','#6b7a93');
    t.textContent = val.toFixed(2);
    svg.appendChild(t);
  }
  // volume gridline
  const vline = document.createElementNS('http://www.w3.org/2000/svg','line');
  vline.setAttribute('x1',pad.l); vline.setAttribute('x2',W-pad.r);
  vline.setAttribute('y1',volTop+volH); vline.setAttribute('y2',volTop+volH);
  vline.setAttribute('stroke','#1c2740'); vline.setAttribute('stroke-width','1');
  svg.appendChild(vline);

  // x labels
  const labelEvery = Math.max(1, Math.ceil(vCount/8));
  for(let i=vStart;i<=vEnd;i++){
    if((i-vStart)%labelEvery!==0 && i!==vEnd) continue;
    const cx = pad.l + (i-vStart+0.5)*slot;
    const t = document.createElementNS('http://www.w3.org/2000/svg','text');
    t.setAttribute('x',cx); t.setAttribute('y',H-pad.b+16);
    t.setAttribute('text-anchor','middle'); t.setAttribute('font-size','10');
    t.setAttribute('fill','#6b7a93');
    t.textContent = records[i].date.slice(5);
    svg.appendChild(t);
  }

  // MA lines
  ['ma20','ma60','ma120'].forEach(maKey=>{
    const color = MA_COLORS[maKey];
    let d='';
    for(let i=vStart;i<=vEnd;i++){
      const v = records[i][maKey];
      if(v===null||v===undefined) continue;
      const cx = pad.l + (i-vStart+0.5)*slot;
      const cy = yP(v);
      d += (d?'L':'M')+cx.toFixed(1)+','+cy.toFixed(1);
    }
    if(!d) return;
    const path = document.createElementNS('http://www.w3.org/2000/svg','path');
    path.setAttribute('d',d);
    path.setAttribute('fill','none'); path.setAttribute('stroke',color);
    path.setAttribute('stroke-width','1.4'); path.setAttribute('opacity','0.9');
    svg.appendChild(path);
  });

  // candles
  for(let i=vStart;i<=vEnd;i++){
    const r = records[i];
    const cx = pad.l + (i-vStart+0.5)*slot;
    const up = r.close >= r.open;
    const color = up?UP:DOWN;
    const yO = yP(r.open), yC = yP(r.close), yH = yP(r.high), yL = yP(r.low);
    const bodyTop = Math.min(yO,yC), bodyH = Math.max(1, Math.abs(yC-yO));
    // wick
    const wick = document.createElementNS('http://www.w3.org/2000/svg','line');
    wick.setAttribute('x1',cx); wick.setAttribute('x2',cx);
    wick.setAttribute('y1',yH); wick.setAttribute('y2',yL);
    wick.setAttribute('stroke',color); wick.setAttribute('stroke-width','1');
    svg.appendChild(wick);
    // body
    const body = document.createElementNS('http://www.w3.org/2000/svg','rect');
    body.setAttribute('x',cx-candleW/2); body.setAttribute('y',bodyTop);
    body.setAttribute('width',candleW); body.setAttribute('height',bodyH);
    body.setAttribute('fill', up?color:'none');
    body.setAttribute('stroke',color); body.setAttribute('stroke-width','1');
    svg.appendChild(body);
    // volume bar
    const vx = cx-candleW/2;
    const vy = yV(r.volume);
    const vbar = document.createElementNS('http://www.w3.org/2000/svg','rect');
    vbar.setAttribute('x',vx); vbar.setAttribute('y',vy);
    vbar.setAttribute('width',candleW); vbar.setAttribute('height',volTop+volH-vy);
    vbar.setAttribute('fill',color); vbar.setAttribute('opacity','0.55');
    svg.appendChild(vbar);
  }

  // hover crosshair + highlight
  if(hoverIdx>=vStart && hoverIdx<=vEnd){
    const cx = pad.l + (hoverIdx-vStart+0.5)*slot;
    // vertical line
    const vl = document.createElementNS('http://www.w3.org/2000/svg','line');
    vl.setAttribute('x1',cx); vl.setAttribute('x2',cx);
    vl.setAttribute('y1',pad.t); vl.setAttribute('y2',volTop+volH);
    vl.setAttribute('stroke','#3a4a6b'); vl.setAttribute('stroke-width','1');
    vl.setAttribute('stroke-dasharray','3,3');
    svg.appendChild(vl);
    // highlight bar
    const hl = document.createElementNS('http://www.w3.org/2000/svg','rect');
    hl.setAttribute('x',pad.l+(hoverIdx-vStart)*slot); hl.setAttribute('y',pad.t);
    hl.setAttribute('width',slot); hl.setAttribute('height',volTop+volH-pad.t);
    hl.setAttribute('fill','rgba(79,140,255,.06)');
    svg.appendChild(hl);
  }

  // legend
  const last = records[N-1];
  document.getElementById('legend').innerHTML =
    '<div class="item"><span class="sw" style="background:'+UP+'"></span>阳线</div>'+
    '<div class="item"><span class="sw" style="background:'+DOWN+'"></span>阴线</div>'+
    '<div class="item"><span class="sw" style="background:'+MA_COLORS.ma20+'"></span>MA20 '+fmtNum(last.ma20)+'</div>'+
    '<div class="item"><span class="sw" style="background:'+MA_COLORS.ma60+'"></span>MA60 '+fmtNum(last.ma60)+'</div>'+
    '<div class="item"><span class="sw" style="background:'+MA_COLORS.ma120+'"></span>MA120 '+fmtNum(last.ma120)+'</div>';

  // hint
  const hint = document.getElementById('chartHint');
  hint.innerHTML =
    '&#128161; 悬停查看详情 · 滚轮缩放 · 拖拽平移 · 顶部按钮切换窗口 · 键盘 &#8592;&#8594; 平移 / +/- 缩放';
}

// ---------- tooltip ----------
function showTooltip(idx){
  if(idx<viewStart||idx>viewEnd) return;
  const r = records[idx];
  const up = r.close>=r.open;
  const cls = up?'up':'down';
  tooltip.innerHTML =
    '<div class="tt-title">'+r.date+'</div>'+
    '<div class="tt-row"><span class="l">开</span><span class="r '+cls+'">'+fmtNum(r.open)+'</span></div>'+
    '<div class="tt-row"><span class="l">高</span><span class="r '+cls+'">'+fmtNum(r.high)+'</span></div>'+
    '<div class="tt-row"><span class="l">低</span><span class="r '+cls+'">'+fmtNum(r.low)+'</span></div>'+
    '<div class="tt-row"><span class="l">收</span><span class="r '+cls+'">'+fmtNum(r.close)+'</span></div>'+
    '<div class="tt-row"><span class="l">成交量</span><span class="r">'+fmtVol(r.volume)+'</span></div>'+
    '<div class="tt-row"><span class="l">成交额</span><span class="r">'+fmtTurnover(r.turnover)+'</span></div>'+
    '<div class="tt-row"><span class="l">MA20</span><span class="r">'+fmtNum(r.ma20)+'</span></div>'+
    '<div class="tt-row"><span class="l">MA60</span><span class="r">'+fmtNum(r.ma60)+'</span></div>'+
    '<div class="tt-row"><span class="l">MA120</span><span class="r">'+fmtNum(r.ma120)+'</span></div>';
  tooltip.style.opacity='1';
}
function hideTooltip(){ tooltip.style.opacity='0'; }

// map mouse x -> bar index
function xToIdx(clientX){
  const rect = wrap.getBoundingClientRect();
  const padL = 56;
  const iw = rect.width - padL - 14;
  const vCount = viewEnd-viewStart+1;
  const slot = iw/vCount;
  const rel = clientX - rect.left - padL;
  const i = viewStart + Math.floor(rel/slot);
  return Math.max(viewStart, Math.min(viewEnd, i));
}

// ---------- interactions ----------
// hover
svg.addEventListener('mousemove', function(e){
  const idx = xToIdx(e.clientX);
  if(idx!==hoverIdx){
    hoverIdx = idx;
    renderChart();
    showTooltip(idx);
  }
  // position tooltip
  const rect = wrap.getBoundingClientRect();
  let tx = e.clientX - rect.left + 14;
  let ty = e.clientY - rect.top - 10;
  const tw = tooltip.offsetWidth, th = tooltip.offsetHeight;
  if(tx+tw>rect.width) tx = e.clientX-rect.left-tw-14;
  if(ty+th>rect.height) ty = e.clientY-rect.top-th-10;
  tooltip.style.left = tx+'px'; tooltip.style.top = ty+'px';
});
svg.addEventListener('mouseleave', function(){ hoverIdx=-1; hideTooltip(); renderChart(); });

// wheel zoom (zoom around cursor)
svg.addEventListener('wheel', function(e){
  e.preventDefault();
  const rect = wrap.getBoundingClientRect();
  const padL = 56;
  const iw = rect.width - padL - 14;
  const vCount = viewEnd-viewStart+1;
  const slot = iw/vCount;
  const rel = e.clientX - rect.left - padL;
  const anchor = viewStart + Math.floor(rel/slot);
  const factor = e.deltaY<0 ? 0.7 : 1.4; // zoom in / out
  let newCount = Math.max(10, Math.min(N, Math.round(vCount*factor)));
  let newStart = Math.round(anchor - (anchor-viewStart)*(newCount/vCount));
  newStart = Math.max(0, Math.min(N-newCount, newStart));
  viewStart = newStart; viewEnd = newStart+newCount-1;
  windowMode = null;
  document.querySelectorAll('.ctl[data-window]').forEach(c=>c.classList.remove('active'));
  renderChart();
}, {passive:false});

// drag pan
let dragging=false, dragStartX=0, dragStartView=0;
svg.addEventListener('mousedown', function(e){
  dragging=true; dragStartX=e.clientX; dragStartView=viewStart;
});
svg.addEventListener('mousemove', function(e){
  if(!dragging) return;
  const rect = wrap.getBoundingClientRect();
  const padL=56, iw=rect.width-padL-14;
  const vCount=viewEnd-viewStart+1;
  const slot=iw/vCount;
  const dx = e.clientX-dragStartX;
  const shift = Math.round(dx/slot);
  let ns = dragStartView - shift;
  ns = Math.max(0, Math.min(N-vCount, ns));
  viewStart=ns; viewEnd=ns+vCount-1;
  windowMode=null;
  document.querySelectorAll('.ctl[data-window]').forEach(c=>c.classList.remove('active'));
  renderChart();
});
window.addEventListener('mouseup', function(){ dragging=false; });

// touch support (narrow screens)
let touchStartX=0, touchStartView=0, touchActive=false;
svg.addEventListener('touchstart', function(e){
  if(e.touches.length===1){
    touchActive=true; touchStartX=e.touches[0].clientX; touchStartView=viewStart;
  }
}, {passive:true});
svg.addEventListener('touchmove', function(e){
  if(!touchActive||e.touches.length!==1) return;
  e.preventDefault();
  const rect = wrap.getBoundingClientRect();
  const padL=56, iw=rect.width-padL-14;
  const vCount=viewEnd-viewStart+1;
  const slot=iw/vCount;
  const dx = e.touches[0].clientX-touchStartX;
  const shift = Math.round(dx/slot);
  let ns = touchStartView - shift;
  ns = Math.max(0, Math.min(N-vCount, ns));
  viewStart=ns; viewEnd=ns+vCount-1;
  windowMode=null;
  document.querySelectorAll('.ctl[data-window]').forEach(c=>c.classList.remove('active'));
  renderChart();
}, {passive:false});
svg.addEventListener('touchend', function(){ touchActive=false; });

// keyboard
window.addEventListener('keydown', function(e){
  const vCount=viewEnd-viewStart+1;
  if(e.key==='ArrowLeft'){ let ns=Math.max(0,viewStart-5); viewStart=ns; viewEnd=ns+vCount-1; windowMode=null; renderChart(); }
  else if(e.key==='ArrowRight'){ let ns=Math.min(N-vCount,viewStart+5); viewStart=ns; viewEnd=ns+vCount-1; windowMode=null; renderChart(); }
  else if(e.key==='+'||e.key==='='){ let nc=Math.max(10,Math.round(vCount*0.7)); viewEnd=Math.min(N-1,viewStart+nc-1); viewStart=Math.max(0,viewEnd-nc+1); windowMode=null; renderChart(); }
  else if(e.key==='-'){ let nc=Math.min(N,Math.round(vCount*1.4)); viewEnd=Math.min(N-1,viewStart+nc-1); viewStart=Math.max(0,viewEnd-nc+1); windowMode=null; renderChart(); }
});

// controls
document.getElementById('controls').addEventListener('click', function(e){
  const ctl = e.target.closest('.ctl');
  if(!ctl) return;
  if(ctl.id==='btnReset'){ hoverIdx=-1; hideTooltip(); applyWindow('1Y'); return; }
  if(ctl.dataset.window){ applyWindow(ctl.dataset.window); }
});
document.getElementById('btnReset').addEventListener('click', function(){ hoverIdx=-1; hideTooltip(); applyWindow('1Y'); });

// ---------- init ----------
applyWindow('1Y');
window.addEventListener('resize', function(){ renderChart(); });
</script>
</body>
</html>
'''

html = HTML.replace('__DATA__', data_js)

# Write to 产出物 directory
import os
out_dir = r'd:\@VSwork\VS昭明计划VBA优化\_产出物'
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, 'stock-overview.html')
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)
print('written', out_path, len(html), 'bytes')