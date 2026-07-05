content = r"""{===================================================================================}
{============================  预计算：高频复用变量  ==================================}
{--- 条件：周期类型（原DATATYPE=8/9/10重复50+次）---}
周期条件DT8  := DATATYPE=8;
周期条件DT9  := DATATYPE=9;
周期条件DT10 := DATATYPE=10;
周期条件DT8L := DATATYPE<=8;
周期条件DT9H := DATATYPE>=9;
周期条件DT10H := DATATYPE>=10;

{--- REF预计算（原REF(C,1)/REF(C,2)/REF(O,1)重复15+次）---}
RC1 := REF(C,1);
RC2 := REF(C,2);
RO1 := REF(O,1);

{--- 条件：C/REF比较（重复8+次）---}
价格条件C_UP   := C>=RC1;
价格条件C_DN   := C<RC1;
价格条件R1_UP  := RC1>RC2;
价格条件R1_DN  := RC1<=RC2;
价格条件C_UO   := C>RO1;
价格条件C_DO   := C<RO1;
{===================================================================================}
{--------------------------------  顶型  ----------------------------------------}
GHHH  :=HHV(HIGH,10);
GHHH1 :=HHV(HIGH,5);
GLLL  :=LLV(LOW,10);
GLLL1 :=LLV(LOW,5);

{--- 条件：顶底判断（重复10+次）---}
顶底条件前高升 := GHHH>GHHH1;
顶底条件前高平 := GHHH=GHHH1;
顶底条件触顶1 := H=GHHH1;
顶底条件触顶  := H=GHHH;
顶底条件触底  := L=GLLL;
顶底条件触底1 := L=GLLL1;

PARTLINE(GHHH,  周期条件DT9H, RGB( 99,0,  99))     ,LAYER3,LINETHICK2;
PARTLINE(GHHH1, 周期条件DT9H, RGB( 133,0, 133))     ,LAYER3,LINETHICK1;
PARTLINE(GHHH,  周期条件DT8, RGB( 99,0,  99))     ,LAYER3,LINETHICK1;
PARTLINE(GHHH1, 周期条件DT8, RGB( 133,0, 133))     ,LAYER3,LINETHICK3;
PARTLINE(GLLL,  1, RGB(  0,0,200))     ,LAYER3,LINETHICK2;
PARTLINE(GLLL1, 1, RGB(  0,0,200))     ,LAYER3,LINETHICK1;
{===================================================================================}
{***********************************************************************************}




{===================================================================================}
{================================    均线   ========================================}
JZ := EMA(C,2);
均线基准:=JZ;
JA := EMA(均线基准,5);
JB := EMA(均线基准,12);
JC := EMA(均线基准,26);
JD := EMA(均线基准,60);
JE := EMA(均线基准,120);
JF := EMA(均线基准,240);
JG := EMA(均线基准,480);
JH := EMA(均线基准,960);
{===================================================================================}

{===================================================================================}
{=================================   均线显示   ====================================}
{================================= 图层：2-4 =======================================}
PARTLINE(JB,  1, RGB(  0,225,  0))     ,LAYER3,LINETHICK2;
PARTLINE(JA,  1, RGB(  0,111,111))     ,LAYER3,LINETHICK2,dotline;
PARTLINE(JZ,  1, RGB( 66,  0,  0))     ,LAYER3,LINETHICK1;

PARTLINE(JG,  周期条件DT8,  RGB(77, 99,99))     ,LAYER4,LINETHICK6;
PARTLINE(JF,  周期条件DT8,  RGB(88,  0,  0))     ,LAYER4,LINETHICK8;
PARTLINE(JE,  周期条件DT8L, RGB(88,88,  0))     ,LAYER4,LINETHICK8;
PARTLINE(JD,  周期条件DT8L, RGB(166,0,  0))     ,LAYER4,LINETHICK6;
PARTLINE(JC,  周期条件DT8L, RGB(166,166,0))     ,LAYER4,LINETHICK5;
PARTLINE(JE,  周期条件DT9,  RGB(77, 99,99))    ,LAYER4,LINETHICK6;
PARTLINE(JD,  周期条件DT9,  RGB(200,  0,  0))     ,LAYER4,LINETHICK5;
PARTLINE(JC,  周期条件DT9H,  RGB(188,188, 0))     ,LAYER3,LINETHICK5;
{----------------------------------------标注管宽太大----------------}
PARTLINE(JA*1.2,  周期条件DT9, RGB(  99, 99, 0))     ,LAYER3,LINETHICK1;
PARTLINE(JC*1.1,  周期条件DT8, RGB(  99, 99, 0))     ,LAYER3,LINETHICK1;
PARTLINE(JC*1.2,  周期条件DT8, RGB(  99, 99, 0))     ,LAYER3,LINETHICK1;
{===================================================================================}



{===================================================================================}
{=================================   均线条件   ====================================}
{--- 条件：均线交叉比较（在局道IFS链中重复40+次）---}
均线条件JZ上JA := JZ>=JA;    均线条件JZ上JB := JZ>=JB;    均线条件JZ上JC := JZ>=JC;
均线条件JZ上JD := JZ>=JD;    均线条件JZ上JE := JZ>=JE;    均线条件JZ上JF := JZ>=JF;    均线条件JZ上JG := JZ>=JG;
均线条件JA上JB := JA>=JB;    均线条件JA上JC := JA>=JC;
均线条件JB上JC := JB>=JC;    均线条件JB上JD := JB>=JD;
均线条件JC上JD := JC>=JD;    均线条件JC上JE := JC>=JE;
均线条件JD上JE := JD>=JE;
均线条件JE上JF := JE>=JF;    均线条件JE上JG := JE>=JG;
均线条件JF上JG := JF>=JG;
{注：反向比较用 NOT，如 JE<JG = NOT(均线条件JE上JG)}
{===================================================================================}



{===================================================================================}
{=================================    四区域   =====================================}
{--- 月级别（周期条件DT9）---------------------------------------}
四区域月:=
IFS(周期条件DT10 and 均线条件JZ上JA and  均线条件JA上JB, '多长',
IFS(周期条件DT10 and 均线条件JZ上JA, '多被',
IFS(周期条件DT10 and not(均线条件JZ上JA) and not(均线条件JA上JB) , '空长',
IFS(周期条件DT10 , '空看',
'')))),DRAWNULL,COLORwhite;
{--- 周级别（周期条件DT9）---------------------------------------}
四区域周:=
IFS(周期条件DT9 and 均线条件JZ上JC and 均线条件JC上JD and 均线条件JZ上JB, '多长',
IFS(周期条件DT9 and 均线条件JZ上JC, '多被',
IFS(周期条件DT9 and not(均线条件JZ上JC) and not(均线条件JC上JD) and not(均线条件JZ上JB), '空长',
IFS(周期条件DT9, '空看',
'')))),DRAWNULL,COLORwhite;
{--- 日级别（周期条件DT8）---------------------------------------}
四区域日:=
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JE上JF and 均线条件JZ上JD, '多长',
IFS(周期条件DT8 and 均线条件JZ上JE, '多被',
IFS(周期条件DT8 and not(均线条件JZ上JE) and not(均线条件JE上JF) and not(均线条件JZ上JD), '空长',
IFS(周期条件DT8, '空看',
'')))),DRAWNULL,COLORwhite;
{--- 合并输出 --------------------------------------------------}
四区域:=
IFS(周期条件DT10, 四区域月,
IFS(周期条件DT9, 四区域周,
IFS(周期条件DT8, 四区域日,
''))),DRAWNULL,COLORYELLOW;

四区域,DRAWNULL,COLORYELLOW;
{===================================================================================}
{--- 四区域背景色 ---}
DRAWGBK (四区域='多长', RGB( 25, 40, 99)), LAYER7;
DRAWGBK (四区域='多被', RGB( 55,22,  0)), LAYER7;
DRAWGBK (四区域='空看', RGB( 33, 33, 33)), LAYER7;
{===================================================================================}
FILLRGN( JE ,JF ,周期条件DT8, RGB(33,33,0) ),LAYER6;
{===================================================================================}


{=================================   周仓类   =======================================}
IFS(周期条件DT9 and 均线条件JC上JD and (均线条件JZ上JC), '金',
IFS(周期条件DT9 and not(均线条件JC上JD) and 均线条件JZ上JD, '仅试_银',
'')),DRAWNULL,COLORyellow;
IFS(周期条件DT9 and 均线条件JC上JD and not(均线条件JZ上JD), '勿勿勿勿勿_尿',
IFS(周期条件DT9 and 均线条件JC上JD and not(均线条件JZ上JC), '仅观观_嘘',
IFS(周期条件DT9 and 均线条件JC上JD, '',
IFS(周期条件DT9 and 均线条件JZ上JD, '',
IFS(周期条件DT9 and 均线条件JZ上JC, '仅观观_唏',
IFS(周期条件DT9 , '勿勿勿勿勿_屎',
'')))))),DRAWNULL,COLORBROWN;

IFS(周期条件DT9 and 均线条件JA上JB and not(均线条件JZ上JB), '下',
IFS(周期条件DT9 and 均线条件JA上JB and not(均线条件JZ上JA), '中',
IFS(周期条件DT9 and 均线条件JA上JB, '上',
IFS(周期条件DT9 and 均线条件JZ上JD, '忐',
IFS(周期条件DT9 and 均线条件JZ上JC, '忠',
IFS(周期条件DT9 , '忑',
'')))))),DRAWNULL,COLORwhite;
{===================================================================================}
{=================================   日仓类   =======================================}
IFS(周期条件DT8 and 均线条件JE上JF and (均线条件JZ上JE), '金',
IFS(周期条件DT8 and not(均线条件JE上JF) and 均线条件JZ上JF, '仅试_银',
'')),DRAWNULL,COLORyellow;
IFS(周期条件DT8 and 均线条件JE上JF and not(均线条件JZ上JF), '勿勿勿勿勿_尿',
IFS(周期条件DT8 and 均线条件JE上JF and not(均线条件JZ上JE), '仅观观_嘘',
IFS(周期条件DT8 and 均线条件JE上JF, '',
IFS(周期条件DT8 and 均线条件JZ上JF, '',
IFS(周期条件DT8 and 均线条件JZ上JE, '仅观观_唏',
IFS(周期条件DT8 , '勿勿勿勿勿_屎',
'')))))),DRAWNULL,COLORBROWN;

IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JC上JD and not(均线条件JZ上JD), '下',
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JC上JD and not(均线条件JZ上JC), '中',
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JC上JD, '上',
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JZ上JD, '忐',
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JZ上JC, '忠',
IFS(周期条件DT8 and 均线条件JZ上JE , '忑',
IFS(周期条件DT8 , '勿',
''))))))),DRAWNULL,COLORwhite;

IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JA上JB and not(均线条件JZ上JB), '丙',
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JA上JB and not(均线条件JZ上JA), '乙',
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JA上JB , '甲',
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JZ上JB, '己',
IFS(周期条件DT8 and 均线条件JZ上JE and 均线条件JZ上JA, '戊',
IFS(周期条件DT8 and 均线条件JZ上JE , '丁',
'')))))),DRAWNULL,COLORwhite;
{===================================================================================}
{================================  勿入提示  =======================================}
DRAWTEXT(周期条件DT8 and not(均线条件JZ上JE), L*0.99, 'x'),COLORgray,LAYER1;
DRAWTEXT(周期条件DT9 and not(均线条件JZ上JC), L*0.99, 'x'),COLORgray,LAYER1;
{===================================================================================}



{===================================================================================}
{=================================    局道   =======================================}
{------ 均线: JZ(EMA2), JA5, JB12, JC26, JD60, JE120, JF240, JG480, JH960 ------}
{------ 用法: 均线条件JZ上JC = JZ>=JC, 均线条件JE上JG = JE>=JG, NOT(均线条件JE上JG) = JE<JG ------}
{===================================================================================}
{--- 局乾条件预计算 ---}
局乾_1b := 均线条件JZ上JC and 均线条件JC上JE;
局乾_1e := 均线条件JZ上JE and 均线条件JC上JE;
局乾_1w := 均线条件JZ上JE and 均线条件JC上JD;
局乾_6u := 均线条件JZ上JD and 均线条件JC上JE;
局乾_6v := 均线条件JZ上JD and NOT(均线条件JC上JD);
局乾_6w := 均线条件JZ上JD and 均线条件JZ上JC;
局乾_2ia := 均线条件JZ上JD and NOT(均线条件JC上JE);
局乾_2ib := 均线条件JZ上JD and NOT(均线条件JC上JD);
局乾_2c := 均线条件JZ上JD and 均线条件JZ上JC;
局乾_3u := 均线条件JZ上JE and NOT(均线条件JC上JE);
局乾_3v := 均线条件JZ上JE and 均线条件JC上JD;
局乾_3w := 均线条件JZ上JE and NOT(均线条件JZ上JC);
局乾_4b := NOT(均线条件JC上JE) AND NOT(均线条件JZ上JC);
{--- 局坤条件预计算 ---}
局坤_1b := 均线条件JZ上JA and 均线条件JA上JC;
局坤_1e := 均线条件JZ上JC and 均线条件JA上JC;
局坤_1w := 均线条件JZ上JC and 均线条件JA上JB;
局坤_6u := 均线条件JZ上JB and 均线条件JA上JC;
局坤_6v := 均线条件JZ上JB and NOT(均线条件JA上JB);
局坤_6w := 均线条件JZ上JB and 均线条件JZ上JA;
局坤_2ia := 均线条件JZ上JB and NOT(均线条件JA上JC);
局坤_2ib := 均线条件JZ上JB and NOT(均线条件JA上JB);
局坤_2c := 均线条件JZ上JB and 均线条件JZ上JA and 价格条件C_UP;
局坤_3u := 均线条件JZ上JC and NOT(均线条件JA上JC);
局坤_3v := 均线条件JZ上JC and 均线条件JA上JB;
局坤_3w := 均线条件JZ上JC and NOT(均线条件JZ上JA);
局坤_4b := NOT(均线条件JA上JC) AND NOT(均线条件JZ上JA);
局乾下 :=
IFS(局乾_1b,'1b',
IFS(局乾_1e,'1e',
IFS(局乾_1w,'1w',
IFS(均线条件JZ上JE,'1v',
IFS(局乾_6u,'6u',
IFS(局乾_6v,'6v',
IFS(局乾_6w,'6w',
IFS(均线条件JZ上JD,'6h',
IFS(均线条件JC上JD,'5I',
IFS(JZ<=JC,'5c',
IFS(NOT(均线条件JD上JE),'5e',
''
)))))))))));
局乾上 :=
IFS(局乾_2ia,'2i',
IFS(局乾_2ib,'2I',
IFS(局乾_2c,'2c',
IFS(均线条件JZ上JD,'2e',
IFS(局乾_3u,'3u',
IFS(局乾_3v,'3v',
IFS(局乾_3w,'3w',
IFS(均线条件JZ上JE,'3h',
IFS(局乾_4b,'4b',
IFS(NOT(均线条件JC上JE),'4e',
IFS(NOT(均线条件JC上JD),'4w',
IFS(均线条件JD上JE,'4v',
''
))))))))))));
局乾:=IFS(NOT(均线条件JD上JE), 局乾下, 局乾上);
{------------------------------------------------------}
局坤下 :=
IFS(局坤_1b,'1b',
IFS(局坤_1e,'1e',
IFS(局坤_1w,'1w',
IFS(均线条件JZ上JC,'1v',
IFS(局坤_6u,'6u',
IFS(局坤_6v,'6v',
IFS(局坤_6w,'6w',
IFS(均线条件JZ上JB,'6h',
IFS(均线条件JA上JB,'5I',
IFS(JZ<=JA,'5c',
IFS(NOT(均线条件JB上JC),'5e',
''
)))))))))));
局坤上 :=
IFS(局坤_2ia,'2i',
IFS(局坤_2ib,'2I',
IFS(局坤_2c,'2c',
IFS(均线条件JZ上JB and 均线条件JZ上JA,'2d',
IFS(均线条件JZ上JB,'2e',
IFS(局坤_3u,'3u',
IFS(局坤_3v,'3v',
IFS(局坤_3w,'3w',
IFS(均线条件JZ上JC,'3h',
IFS(局坤_4b,'4b',
IFS(NOT(均线条件JA上JC),'4e',
IFS(NOT(均线条件JA上JB),'4w',
IFS(均线条件JB上JC,'4v',
''
)))))))))))));
局坤:=IFS(NOT(均线条件JB上JC), 局坤下, 局坤上);
{===================================================================================}
IFS(周期条件DT10H,  '__' + 局坤, ''),DRAWNULL,COLORGRAY;
{------------------------------------------------------}
IFS(周期条件DT9,   '__' + 局乾 ,''),DRAWNULL,COLORGRAY;
IFS(周期条件DT9,   '__' + 局坤 ,''),DRAWNULL,COLORGRAY;
{------------------------------------------------------}
{忽略日类月局，提高效率，以DJE为持仓基准}
IFS(周期条件DT8L,  '__' + 局乾, ''),DRAWNULL,COLORGRAY;
{逃出日线级别反复纠缠的陷阱}
IFS(周期条件DT8,   '__' + 局坤 ,''),DRAWNULL,COLORGRAY;
{===================================================================================}




{===================================================================================}
{--------------------------------   管上符   -----------------------------------}
新:=
IFS(周期条件DT9 and 顶底条件前高升 AND GHHH1>=JC and 均线条件JZ上JC,'新K',
IFS(周期条件DT9 and 顶底条件前高平 AND GHHH1>=JC AND 均线条件JZ上JC AND 均线条件JA上JB,'新G',
IFS(周期条件DT9 and 顶底条件前高平 AND GHHH1>=JC AND 均线条件JZ上JC,'新X',
'')));
DRAWTEXT(新='新G' and 顶底条件触顶1, GHHH1*1.02,  'o'),COLORCYAN;
DRAWTEXT(新='新X' and 顶底条件触顶1, GHHH1*1.02,  'ooo'),COLORGREEN;
DRAWTEXT(新='新K' and 顶底条件触顶1, GHHH1*1.02,  'oo'),COLORGREEN;
{------------------------------------------------------}
IFS(顶底条件前高平, '合','离') ,DRAWNULL,COLORgray;

  IFS(顶底条件触顶, '顶','')
+ IFS(顶底条件触顶1,'哼','')
+ IFS(顶底条件触底, '底','')
+ IFS(顶底条件触底1,'哈','')
,DRAWNULL,COLORcyan;
{------------------------------------------------------}
IFS(C<JC, '',
IFS(顶底条件前高平 and 顶底条件触顶1, '龙a',
IFS(顶底条件前高平 , '龙b',
IFS(顶底条件前高升 and 顶底条件触顶1, '离a',
IFS(顶底条件前高升 AND C>JB, '离b',
'离c'))))),DRAWNULL,COLORgray;
{===================================================================================}




{===================================================================================}
{================================  组柱形态    =====================================}
IFS(价格条件C_UP   and RC1<RC2 and 价格条件C_UO,'升吞',
IFS(价格条件C_UP   and RC1>=RC2,'升连',
IFS(价格条件C_UP   ,'升孕',
''))),DRAWNULL,COLOR008a8a;
IFS(价格条件C_DN   and 价格条件R1_UP and 价格条件C_DO,'跌吞',
IFS(价格条件C_DN   and 价格条件R1_DN,'跌连',
IFS(价格条件C_DN   ,'跌孕',
''))),DRAWNULL,COLORyellow;

DRAWTEXT(均线条件JZ上JC
and  价格条件R1_UP and 价格条件C_DO and 价格条件C_DN
, GHHH*1.02,  '吞'),layer2,COLORMAGENTA;
DRAWTEXT(均线条件JZ上JC
and  价格条件R1_DN and 价格条件C_DN
, GHHH*1.02,  '连'),layer2,COLORMAGENTA;
{===================================================================================}
{================================  柱与JA关系  =====================================}
IFS(C>=JA AND O>=JA AND L>=JA, '柱A',
IFS(C>=JA AND O>=JA AND L<JA, '柱B',
IFS(C>=JA AND O<JA, '柱C鼎',
IFS(O>=JA, '柱d薡',
IFS(O<JA  AND H>=JA, '柱e',
IFS(O<JA  AND H<JA,  '柱f',
'')))))),DRAWNULL,COLORGRAY;
{===================================================================================}





'      ',DRAWNULL,COLORblack;
{===================================================================================}
{--------------------------------   管宽撤 日类  -----------------------------------}
{--- 预计算：比率 ---}
rcp_JC := 1/JC;
rcp_JA := 1/JA;
GHHH1_div_JC := GHHH1 * rcp_JC;
GLLL1_div_JC := GLLL1 * rcp_JC;
GHHH1_div_JA := GHHH1 * rcp_JA;
GLLL1_div_JA := GLLL1 * rcp_JA;

管宽日偏哼JC := INTPART(100* (GHHH1_div_JC-1) )                 ,DRAWNULL,COLORbrown;
管宽日偏哈JC := INTPART(100* (GLLL1_div_JC-1) )                 ,DRAWNULL,COLORbrown;
管宽周偏哼JA := INTPART(100* (GHHH1_div_JA-1) )                 ,DRAWNULL,COLORbrown;
管宽周偏哈JA := INTPART(100* (GLLL1_div_JA-1) )                 ,DRAWNULL,COLORbrown;

管宽:
IFS(周期条件DT8 and 均线条件JZ上JC, 管宽周偏哼JA,
IFS(周期条件DT8, 管宽周偏哈JA,
IFS(周期条件DT9 and 均线条件JZ上JC, 管宽周偏哼JA,
IFS(周期条件DT9, 管宽周偏哈JA,
'')))),DRAWNULL,COLORbrown;

{----------------------------------------标注管宽太大----------------}
{***********************************************************************************}


{===================================================================================}
'      ',DRAWNULL,COLORblack;
{###################################################################################}
{================================   信息  ===========================================}
{--------------------------------  波动  -------------------------------------------}
高  : 100* (100*(H/RC1-1))                   ,DRAWNULL,COLORCCCCCC;
收  : 100* (100*(C/RC1-1))                   ,DRAWNULL,COLORAAAA00;
低  : 100* (100*(L/RC1-1))                   ,DRAWNULL,COLORgray;
开  : 100* (100*(O/RC1-1))                   ,DRAWNULL,COLORgray;{尝试观察并解决高开情况如何操盘}
{偏PB : 100* ((C/JB-1))                                   ,DRAWNULL,COLORgray;}
{差CE : 100* ((JC/JE-1))                               ,DRAWNULL,COLORgray;}
差AB : 100* ((JA-JB)/JC)                             ,DRAWNULL,COLORgray;{按与DJC可能的回撤进行分类}
{差AC : 100* ((JA/JC-1))                               ,DRAWNULL,COLOR008800;}
偏哼C : 管宽日偏哼JC                            ,DRAWNULL,COLORgreen;
{DRAWTEXT(周期条件DT9 and (偏顶C>=30) and JZ>JC, JC,  偏顶C  ),layer2,COLORAAAA00;}
日脸:
IFS(周期条件DT8 and 均线条件JZ上JC, 管宽周偏哼JA,
''),DRAWNULL,COLOR008800;
偏LA : INTPART(100* ((L/JA-1))  )                    ,DRAWNULL,COLORgray;
 {DRAWTEXT(周期条件DT8  and 偏LA<=-5, GLLL1*0.98,  偏LA),layer2,COLORgray;}
偏HA : INTPART(100* ((H/JA-1))  )                    ,DRAWNULL,COLORgray;
DRAWTEXT(周期条件DT8  and 偏HA>=5, GHHH1*1.02,  偏HA),layer2,COLORbrown;

{================================  冲高提示  =======================================}
{--------------------------------  提示月类  ---------------------------------------}
{月类可投：对应比较月类高点是否大于上月}
月提示 := IFS(高<=50, '0', IFS(高<=200, '2', IFS(高<=500, '5', '')));
DRAWTEXT(周期条件DT10 and 月提示<>'', H*1.05, 月提示),COLORRED;
{--------------------------------  提示周类  ---------------------------------------}
DRAWTEXT(周期条件DT9 and  均线条件JZ上JC and 管宽周偏哼JA>=20             , GHHH*1.03, 管宽周偏哼JA),COLORbrown;
{周类可投：对应比较周类高点是否大于上周}
周提示弱 := IFS(高<=0, '0', IFS(高<=100, '1', ''));
周提示强 := IFS(高<=0, '0', IFS(高<=100, '1', IFS(高<=200, '2', IFS(高<=300, '3', ''))));
周提示强灰 := IFS(高>300 and 高<=500, '5', '');
DRAWTEXT(周期条件DT9 and NOT(均线条件JZ上JC) and 周提示弱<>'',   H,       周提示弱),COLORbrown;
DRAWTEXT(周期条件DT9 and 均线条件JZ上JC     and 周提示强<>'',   H*1.01,  周提示强),COLORRED;
DRAWTEXT(周期条件DT9 and 均线条件JZ上JC     and 周提示强灰<>'', H*1.01,  周提示强灰),COLORgray;
{===================================================================================}



{================================   周期指示   =====================================}
{--- 预计算：DATETOD1970 ---}
DT1970_WD := DATETOD1970(DATE)-WEEKDAY;
{周节点}
DRAWTEXT(周期条件DT8 and ref(DT1970_WD,1)<DT1970_WD, JC, 'o'),COLORyellow,LAYER1;
{月节点}
STICKLINE(周期条件DT8 and ref(month,1)<>month,JA,JF,0.1,-1000),COLORRED;
STICKLINE(周期条件DT9 and ref(month,1)<>month,GHHH,JD,0.1,-1000),COLORblue,layer6;
{===================================================================================}





{===================================================================================}
{=================================    仓位分类   ====================================}
{--- DJEDC之上仓位操作分类（仅日线）---}
DDJE之上 := 均线条件JZ上JE;
DDJC之上 := 均线条件JZ上JC;
DDJA之上 := 均线条件JZ上JA;
DDJA之下 := NOT(均线条件JZ上JA);
{--- 日线DJE上（预计算，减少仓位分类重复判断）---}
日线DJE上 := 周期条件DT8 and DDJE之上;
{--- 上破DJC（刚上破）---}
上破DJC := DDJC之上 and NOT(REF(DDJC之上, 1));
{--- 诱多模式 ---}
连阴后阳 := REF(价格条件C_DN and 价格条件R1_DN, 1) and 价格条件C_UP;
阴阳阴后阳 := REF(价格条件C_DN and 价格条件R1_UP, 2) and REF(价格条件C_UP, 1) and REF(价格条件C_DN, 1) and 价格条件C_UP;
上破DJA三柱内 := DDJA之上 and REF(NOT(DDJA之上), 1) and NOT(REF(NOT(DDJA之上), 2));
{--- 止盈条件 ---}
偏离大 := 管宽周偏哼JA>=20;
{--- 捡漏条件 ---}
买漏日条件 := DDJA之上 and 价格条件C_UP;
买漏周条件 := DDJA之下 and 顶底条件触底1 and 价格条件C_UP;
{=================================   基本分类   =====================================}
{--- 核心持仓状态 ---}
基本分类 :=
IFS(日线DJE上 and NOT(DDJC之上), '卖浮',
IFS(日线DJE上 and DDJC之上 and 上破DJC, '买初',
IFS(日线DJE上 and DDJC之上 and DDJA之上, '持主',
IFS(日线DJE上 and DDJC之上 and DDJA之下, '持被',
'')))),DRAWNULL,COLORwhite;
{=================================   信号分类   =====================================}
{--- 仅DJC之上有效，叠加在基本分类之上 ---}
信号分类 :=
IFS(日线DJE上 and DDJC之上 and DDJA之上 and 偏离大, '警止盈',
IFS(日线DJE上 and DDJC之上 and DDJA之上 and (上破DJA三柱内 or 连阴后阳 or 阴阳阴后阳), '警诱多',
IFS(日线DJE上 and DDJC之上 and DDJA之上 and 买漏日条件, '机漏日',
IFS(日线DJE上 and DDJC之上 and DDJA之下 and 买漏周条件, '机漏周',
'')))),DRAWNULL,COLORwhite;
{=================================   仓位显示   =====================================}
{--- 基本分类显示（DJE位置） ---}
DRAWTEXT(周期条件DT8 and 基本分类='卖浮', JE, '卖浮'),COLORbrown,LAYER1;
DRAWTEXT(周期条件DT8 and 基本分类='买初', JE, '买初'),COLORgreen,LAYER2;
DRAWTEXT(周期条件DT8 and 基本分类='持主', JE, '持主'),COLOR006666,LAYER1;
DRAWTEXT(周期条件DT8 and 基本分类='持被', JE, '持被'),COLOR00AA66,LAYER1;
{--- 信号分类显示（DJC位置） ---}
DRAWTEXT(周期条件DT8 and 信号分类='警止盈', JC, '警盈'),COLORyellow,LAYER2;
DRAWTEXT(周期条件DT8 and 信号分类='警诱多', JC, '警诱'),COLORyellow,LAYER2;
DRAWTEXT(周期条件DT8 and 信号分类='机漏日', JC, '机日'),COLORgreen,LAYER2;
DRAWTEXT(周期条件DT8 and 信号分类='机漏周', JC, '机周'),COLORgreen,LAYER2;
{===================================================================================}"""

filepath = r"d:/@VSwork/VS昭明计划VBA优化/_益盟公式/益盟公式ZQQQW.txt"
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Done")
