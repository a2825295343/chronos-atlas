"""Dated Chinese campaigns/battles, explicitly named factions and sources."""
import urllib.parse
from territory_repair_stage import read,write
TAG='chinese-wars-2026-11-01'
# slug | title | first | last | side A polity | side B polity | article
DATA='''xuge|繻葛之战|-707|-707|Zheng|Eastern Zhou|Battle of Xuge
changshao|长勺之战|-684|-684|Lu|Qi|Battle of Changshao
chengpu|城濮之战|-632|-632|Jin|Chu|Battle of Chengpu
yao|崤之战|-627|-627|Jin|Qin|Battle of Xiao
bi|邲之战|-597|-597|Chu|Jin|Battle of Bi
an|鞌之战|-589|-589|Jin|Qi|Battle of An
yanling|鄢陵之战|-575|-575|Jin|Chu|Battle of Yanling
boju|柏举之战|-506|-506|Wu|Chu|Battle of Boju
wu-yue-final|越灭吴战争（最后阶段）|-478|-473|Yue|Wu|Conquest of Wu by Yue
jinyang|晋阳之战与三家分晋|-455|-453|Zhao|Jin|Battle of Jinyang
guiling|桂陵之战|-353|-353|Qi|Wei|Battle of Guiling
maling|马陵之战（约前342—341年，纪年有异说）|-342|-341|Qi|Wei|Battle of Maling
yique|伊阙之战|-293|-293|Qin|Han|Battle of Yique
changping|长平之战|-260|-260|Qin|Zhao|Battle of Changping
qin-chu|秦楚战争（统一战争末期）|-224|-223|Qin|Chu|Qin's wars of unification
seven-states|西汉七国之乱|-154|-154|Han Dynasty|Seven Han Kingdoms|Rebellion of the Seven States
mobei|漠北之战|-119|-119|Han Dynasty|Xiongnu|Battle of Mobei
kunyang|昆阳之战|23|23|Han Dynasty|Xin Dynasty|Battle of Kunyang
yellow-turban|黄巾起义（主要起事）|184|185|Han Dynasty|Yellow Turban Rebels|Yellow Turban Rebellion
guandu|官渡之战|200|200|Cao Cao|Yuan Shao|Battle of Guandu
red-cliffs|赤壁之战|208|209|Sun Quan and Liu Bei|Cao Cao|Battle of Red Cliffs
xiaoting|夷陵之战|221|222|Eastern Wu|Shu Han|Battle of Xiaoting
wei-shu|曹魏灭蜀之战|263|263|Cao Wei|Shu Han|Conquest of Shu by Wei
jin-wu|晋灭吴之战|279|280|Western Jin|Eastern Wu|Conquest of Wu by Jin
eight-princes|八王之乱|291|306|Jin Imperial Factions|Jin Rival Princes|War of the Eight Princes
fei-river|淝水之战|383|383|Eastern Jin|Former Qin|Battle of Fei River
north-wei-unification|北魏灭北凉战争|439|439|Northern Wei|Northern Liang|Northern Wei
hou-jing|侯景之乱|548|552|Liang Dynasty|Hou Jing Rebels|Hou Jing
sui-chen|隋灭陈之战|588|589|Sui Dynasty|Chen Dynasty|Sui conquest of Chen
sui-goguryeo|隋与高句丽战争（第二至四次）|612|614|Sui Dynasty|Goguryeo|Goguryeo–Sui War
hulao|虎牢之战与唐统一战争|621|621|Tang Dynasty|Dou Jiande and Wang Shichong|Battle of Hulao
tang-east-turks|唐灭东突厥战争|629|630|Tang Dynasty|Eastern Turkic Khaganate|Tang campaign against the Eastern Turks
tang-goguryeo|唐与新罗灭高句丽战争|666|668|Tang Dynasty|Goguryeo|Goguryeo–Tang War
huang-chao|黄巢起义|875|884|Tang Dynasty|Huang Chao Rebels|Huang Chao Rebellion
song-han|北宋灭北汉战争|979|979|Northern Song|Northern Han|Northern Han
gaoliang|高梁河之战|979|979|Liao Dynasty|Northern Song|Battle of Gaoliang River
song-liao-1004|辽宋澶州战役与澶渊议和|1004|1005|Liao Dynasty|Northern Song|Chanyuan Treaty
jin-liao|金灭辽战争|1114|1125|Great Jin|Liao Dynasty|Jurchen campaigns against the Liao dynasty
jingkang|靖康之变|1125|1127|Great Jin|Northern Song|Jingkang incident
caishi|采石之战|1161|1161|Southern Song|Great Jin|Battle of Caishi'''
ZH={'Zheng':'郑国','Eastern Zhou':'周王室军队','Lu':'鲁国','Qi':'齐国','Jin':'晋国','Chu':'楚国','Qin':'秦国','Wu':'吴国','Yue':'越国','Zhao':'赵氏及韩、魏盟军','Wei':'魏国','Han':'韩国','Han Dynasty':'汉朝朝廷军队',
 'Xiongnu':'匈奴','Xin Dynasty':'新朝军队','Seven Han Kingdoms':'吴、楚等七个诸侯王国','Yellow Turban Rebels':'黄巾起义军','Cao Cao':'曹操军政集团','Yuan Shao':'袁绍军政集团','Sun Quan and Liu Bei':'孙权、刘备联军',
 'Eastern Wu':'孙吴','Shu Han':'蜀汉','Cao Wei':'曹魏','Western Jin':'西晋','Jin Imperial Factions':'晋朝宗室及朝廷各派','Jin Rival Princes':'相互争权的诸王及军队','Eastern Jin':'东晋','Former Qin':'前秦',
 'Northern Wei':'北魏','Northern Liang':'北凉','Liang Dynasty':'南梁朝廷及地方军','Hou Jing Rebels':'侯景军政集团','Sui Dynasty':'隋朝','Chen Dynasty':'陈朝','Goguryeo':'高句丽',
 'Tang Dynasty':'唐朝及阶段性盟军','Dou Jiande and Wang Shichong':'窦建德、王世充集团','Eastern Turkic Khaganate':'东突厥汗国','Huang Chao Rebels':'黄巢等起义军','Northern Song':'北宋','Northern Han':'北汉','Liao Dynasty':'辽朝','Great Jin':'金朝','Southern Song':'南宋'}
NOTES={
 'changping':('秦赵争夺上党及太行山两侧的战略地域。','赵军败于长平，严重削弱赵国军事力量；古代伤亡数字存在史料与解释争议。'),
 'red-cliffs':('曹操控制荆州主要地区后南下，孙权与刘备联合抵抗。','曹军退回北方，孙刘势力得以巩固南方据点；此时尚不是220年后正式建立的魏、蜀、吴三国。'),
 'fei-river':('前秦苻坚大举南下，企图消灭东晋。','东晋军获胜，前秦随后陷入内部分裂；不能把该战役与整个北方政权的即时消失等同。'),
 'jingkang':('宋金结盟灭辽后矛盾加深，金军两度进攻开封。','开封陷落，徽、钦二帝及大批宗室被掳，北宋结束，宋廷其后在南方延续。'),
 'xuge':('周桓王与郑庄公之间的王室权威、职务和朝觐争端激化。','周王联军战败，显示周王室军事号召力下降；不是从此完全不存在周王室。'),
 'seven-states':('汉景帝削减诸侯王封地，引发吴楚等王国反抗。','朝廷平定叛乱，进一步削弱诸侯王军事和行政权力。'),
 'kunyang':('绿林等反新力量扩张，新朝组织大军围攻昆阳。','刘秀等击败新军，成为新朝瓦解过程中的重要战役。'),
 'yellow-turban':('东汉末年社会、经济与地方治理危机与太平道组织动员交织。','主要起事遭朝廷及地方军镇压，残余抵抗延续，地方军事集团势力增长。'),
 'eight-princes':('晋惠帝时期皇室外戚、诸王及朝廷军政集团争夺控制权。','多轮政变与战争严重消耗晋朝实力；八位诸王不是始终组成两个固定阵营。'),
 'jin-liao':('女真反抗辽朝统治，金朝建立后持续向辽朝进攻。','辽朝主要统治中心相继失陷，天祚帝被俘；耶律大石等在西方另建政权。')}
NOTES.update({
 'changshao':('齐国在齐桓公即位后的鲁齐争端中进攻鲁国。','鲁军击退齐军。后世关于曹刿论战的叙述与实际兵力应分开看待。'),
 'chengpu':('晋楚围绕宋国及中原诸侯的支持权争夺。','晋方获胜，晋文公随后会盟诸侯，楚在中原的优势暂受挫。'),
 'yao':('秦军远袭郑国未成，撤回途中与晋方交战。','晋军在崤山击败秦军，秦晋关系转入长期对抗。'),
 'bi':('楚围郑并争夺中原影响，晋军前来介入。','楚军获胜，楚庄王在中原的政治与军事影响增强。'),
 'an':('齐晋及鲁卫之间的外交和军事冲突引发联军作战。','晋方联军获胜，齐晋随后议和。'),
 'yanling':('晋楚争夺郑、许等中原诸侯的归附与影响。','晋军获胜，楚军退出战场；中原争霸并未因此永久结束。'),
 'boju':('吴国联合蔡、唐等势力进攻楚国。','吴军在柏举获胜并攻入郢都，楚随后在秦援助等条件下逐步恢复。'),
 'wu-yue-final':('吴越长期争夺下游地区霸权，越趁吴国内外困境发动进攻。','吴王夫差败亡，吴国被越兼并；此条不是把两国历次战争都并成连续五年。'),
 'jinyang':('晋国智氏联同韩、魏围攻赵氏晋阳，赵氏争取韩魏转向。','智氏被韩赵魏击败，其领地被分，三家势力壮大；周王正式承认三家为诸侯在前403年。'),
 'guiling':('魏攻赵围邯郸，齐为救赵攻击魏国后方。','齐军击败魏军，形成后世围魏救赵的典型叙述。'),
 'maling':('魏与韩冲突，齐介入并与魏军交战。','魏军遭重创，庞涓败亡。纪年常见前342或前341两说，地图按约年区间展示。'),
 'yique':('秦向韩、魏在伊阙一线的军事防御发起进攻。','白起率秦军击败韩魏联军，秦在中原的战略地位进一步增强。'),
 'qin-chu':('秦在统一战争中向楚国发动最后阶段的大规模攻势。','楚王负刍被俘，楚的主要王权被消灭，部分抵抗并非立刻全部结束。'),
 'mobei':('西汉为打击匈奴主力、改变北部边疆形势而大举出塞。','卫青、霍去病部深入漠北并获重要战果，双方均付出很大代价；匈奴并未被此次战役消灭。'),
 'guandu':('袁绍与曹操争夺北方及东汉中央权力的实际控制。','曹操击败袁绍主力，但对河北的后续征服持续数年。'),
 'xiaoting':('刘备在失去荆州和关羽败亡后东征孙权。','陆逊击败蜀汉主力，刘备退至白帝城，吴蜀关系随后逐渐恢复。'),
 'wei-shu':('曹魏政权组织钟会、邓艾等进攻蜀汉。','蜀汉后主刘禅投降，蜀汉主要朝廷结束；次年钟会等兵变另属后续事件。'),
 'jin-wu':('西晋在北方整合后多路进攻孙吴。','孙皓投降，孙吴覆灭，西晋完成这一阶段的统一。'),
 'north-wei-unification':('北魏太武帝向北凉控制的河西地区进攻。','沮渠牧犍投降，北魏取得姑臧等地，北凉余部向西延续。'),
 'hou-jing':('侯景在与梁廷关系破裂后起兵，进攻并控制建康朝廷。','梁朝中央遭破坏，梁宗室与陈霸先、王僧辩等最终击败侯景，但梁的统治已严重削弱。'),
 'sui-chen':('隋完成北方整合后组织多路军队进攻陈朝。','隋军攻陷建康，陈后主被俘，陈朝灭亡。'),
 'sui-goguryeo':('隋朝要求高句丽服从其秩序并发动大规模远征。','隋多次远征未能灭高句丽，沉重动员负担成为隋末危机的一部分。'),
 'hulao':('唐军围攻王世充的洛阳，窦建德率军来援。','李世民在虎牢击败并俘获窦建德，王世充随后投降。'),
 'tang-east-turks':('东突厥内部和边疆形势变化，唐朝多路出兵。','颉利可汗被俘，东突厥汗国主要王权瓦解，草原后续统治安排另分阶段。'),
 'tang-goguryeo':('唐与新罗在朝鲜半岛的军事合作和高句丽内争共同促成最后攻势。','平壤陷落，高句丽主要王权结束；唐与新罗其后又发生冲突。'),
 'huang-chao':('唐末社会经济危机、地方治理及军事矛盾促成大规模起义。','黄巢曾进入长安并建齐政权，后被唐军及地方军击败；唐中央权力进一步衰弱。'),
 'song-han':('北宋为消灭北汉政权、整合北方而进攻太原。','北汉刘继元投降，北汉覆灭；宋军随后攻辽并非同一场太原攻城战。'),
 'gaoliang':('北宋灭北汉后北进燕云地区，与辽军在高梁河交战。','辽军击败宋军，宋军退出这一轮北伐。'),
 'song-liao-1004':('辽军大举南下，宋军在澶州一线防御。','双方于1005年议和，形成辽宋较长期的边境与岁币安排。'),
 'caishi':('金海陵王完颜亮南侵，试图渡长江进攻南宋。','宋军在采石一线阻击金军渡江；金军内部政局变化也影响这次南侵的终止。')})

def main():
 db=read('public/data/historical-wars-supplements.json');existing={r['war']['id']:r for r in db['wars']};added=[]
 for line in DATA.splitlines():
  slug,title,a,b,left,right,article=line.split('|');a=int(a);b=int(b);ident='historic-cn-'+slug
  url='https://en.wikipedia.org/wiki/'+urllib.parse.quote(article.replace(' ','_'),safe='()_%')
  cause,result=NOTES.get(slug,('相关政权围绕统治权、边疆、战略城邑或区域秩序发生军事冲突，具体导火索见所列战役史料。','战役或战事改变相关政权的军事、政治处境；不以该条记录自动推定全部领土归属或逐日战线。'))
  # Reuse any already curated record of the same named battle, not two cards.
  duplicate=next((r for r in existing.values()if r['war']['name']==title and r['war']['id']!=ident),None)
  if duplicate:continue
  participants=[]
  for side,name in [('1',left),('2',right)]:
   aliases=[name]
   if name=='Eastern Jin':aliases+=['Western Jin'] # raw source still uses its predecessor's name
   if name in ['Cao Cao','Yuan Shao','Sun Quan and Liu Bei']:aliases+=['Han Dynasty']
   if name in ['Jin Imperial Factions','Jin Rival Princes']:aliases+=['Western Jin']
   if name=='Seven Han Kingdoms':aliases+=['Han Dynasty']
   participants.append({'side':side,'name':ZH.get(name,name),'polityNames':aliases,'periods':[[a,b]]})
  if slug=='jinyang':participants[1]['name']='智氏及其军队（晋国内部）'
  if slug=='jin-liao':participants[0]['name']='女真军及金朝（1115年建国后）'
  if slug=='yique':participants.append({'side':'2','name':'魏国','polityNames':['Wei'],'periods':[[a,b]]})
  note='具名战役或主要战事的年度记录；内战阵营与正式国家分别说明。没有可靠同口径资料时不虚构兵力。'
  if slug=='sui-goguryeo':note+='不把598年的第一次战争并入612—614年的连续阶段。'
  war={'id':ident,'name':title,'category':'中国古代战争与战役补录','source':'中国历史战争专项核对','url':url,'from':a,'to':b,'periods':[[a,b]],'participants':participants,'scopeNote':note}
  detail={'id':ident,'title':title,'cause':cause,'result':result,'sources':[url],'reviewedHistorical':True,'scopeNote':note,
          'strengthAssessment':'未收录能够按同一战区、同一日期与同一统计口径比较的双方兵力；古代号称、实际参战、民夫与伤亡不混为一个精确数字。',
          'sideNames':[ZH.get(left,left),ZH.get(right,right)]}
  if slug=='fei-river':detail['sources'].append('https://www.shouxian.gov.cn/lyzn/y/7847321.html')
  if slug=='red-cliffs':detail['sources'].append('https://www.hbda.gov.cn/info/535.jspx')
  if slug in ['chengpu','bi','yanling','jinyang']:detail['sources'].append('https://ctext.org/shiji/jin-shi-jia/zhs')
  if slug=='changping':detail['sources'].append('https://ctext.org/shiji/bai-qi-wang-jian-lie-zhuan/zhs')
  existing[ident]={'war':war,'detail':detail};added.append(ident)
 db['wars']=list(existing.values());write('public/data/historical-wars-supplements.json',db)
 cur=read('public/data/curated-facts.json');cur['relations']=[r for r in cur['relations']if not r.get('id','').startswith(TAG)]
 for name,end in [('Jin',-376),('Qi',-256),('Lu',-256),('Zheng',-375),('Song',-286),('Cai',-447),('Chen',-479),('Yan',-256)]:
  cur['relations'].append({'id':TAG+':zhou:'+name,'kind':'allegiance','child':name,'parent':'Eastern Zhou','from':max(-770,-806 if name=='Zheng'else -770),'to':end,
   'detail':'周王室礼制、封建名分下的关系；霸权、卿族与实际军事控制随时期变化，不等于周王室持续直接治理该国。','source':'https://ctext.org/shiji/zhou-ben-ji/zhs'})
 cur['relations'] += [
  {'id':TAG+':kuiqiu','kind':'alliance','members':['Qi','Song','Lu','Zheng'],'from':-651,'to':-651,'title':'葵丘会盟','detail':'齐桓公主持的诸侯盟会；列出已对应到本图的部分参与国，未列入未赴会的晋献公。只记录该年会盟，不视为持续到后世的共同防御条约。','source':'https://ctext.org/shiji/qi-tai-gong-shi-jia/zhs'},
  {'id':TAG+':chanyuan','kind':'alliance','members':['Northern Song','Liao Dynasty'],'from':1005,'to':1122,'title':'澶渊之盟与辽宋和约关系','detail':'双方议和并约定岁币及边界安排；这是一种和约关系，不是共同对外作战的军事同盟。1122年北宋攻辽后不再延续。','source':'https://static.artmuseum.princeton.edu/asian-art/china/timeline'},
  {'id':TAG+':sea','kind':'alliance','members':['Northern Song','Great Jin'],'from':1120,'to':1124,'title':'海上之盟','detail':'宋金相约攻辽；各自作战与履约存在矛盾，1125年宋金战争爆发前截止，不倒推为长期友好。','source':'https://static.artmuseum.princeton.edu/asian-art/china/timeline'}]
 write('public/data/curated-facts.json',cur)
 write('public/data/chinese-wars-review.json',{'revision':TAG,'added':added,'totalNewRecords':len(added),'nominalZhouRelations':8,
    'limitations':['战役库不是古代所有战争的穷尽目录。','未有同口径依据的兵力仍待核定。','少数先秦战役纪年有不同说法，保留来源以便复核。']})
 print('Chinese war records added',len(added),flush=True)

if __name__=='__main__':main()
