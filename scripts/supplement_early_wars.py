"""Explicitly scoped early conflicts; no invented armies or occupation polygons."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
# slug, title, years, sides, cause, result, theatre, source article
ROWS=[
 ('greco-persian','希波战争',-499,-449,['阿契美尼德帝国'],['雅典及提洛同盟','斯巴达等希腊城邦'],'波斯帝国向爱琴海扩张，爱奥尼亚起义及希腊诸城邦的介入导致多轮战争。','希腊城邦挫败波斯对希腊本土的征服，爱琴海力量格局改变；不是所有希腊城邦从头到尾处于同一阵营。',[26,38],'Greco-Persian_Wars'),
 ('peloponnesian','伯罗奔尼撒战争',-431,-404,['雅典及提洛同盟'],['斯巴达及伯罗奔尼撒同盟'],'雅典海上势力增长与城邦间的安全、贸易及联盟竞争激化。','雅典于前404年投降，海上帝国瓦解；斯巴达取得短期霸权。',[23,38],'Peloponnesian_War'),
 ('alexander','亚历山大征服波斯战争',-334,-330,['马其顿王国及希腊同盟军'],['阿契美尼德帝国'],'马其顿王权承接对波斯战争计划并向小亚细亚推进。','波斯主要王都被占，大流士三世死亡；其后向中亚、印度的远征另属后续阶段。',[44,34],'Wars_of_Alexander_the_Great'),
 ('punic-first','第一次布匿战争',-264,-241,['罗马共和国'],['迦太基'],'围绕西西里城邦与海上势力范围的争夺升级。','迦太基战败并割让西西里，罗马在西地中海取得重要立足点。',[14,37],'First_Punic_War'),
 ('punic-second','第二次布匿战争',-218,-201,['罗马共和国及其盟邦'],['迦太基及其盟邦'],'伊比利亚势力扩张、萨贡托危机及罗马与迦太基的竞争导致战争。','罗马在扎马获胜，迦太基丧失海外领地并受军事限制。',[12,40],'Second_Punic_War'),
 ('punic-third','第三次布匿战争',-149,-146,['罗马共和国'],['迦太基'],'罗马对迦太基恢复实力的疑惧与迦太基对努米底亚战争引发最后冲突。','迦太基城被攻陷和摧毁，其地域纳入罗马统治。',[10.3,36.8],'Third_Punic_War'),
 ('gaul','凯撒征服高卢战争',-58,-50,['罗马共和国（凯撒军）'],['高卢诸部与抵抗联盟'],'罗马干预高卢政治、边疆安全争端及凯撒的军事扩张相互交织。','罗马征服高卢大部；阿莱西亚围城后主要联盟失败，但抵抗并非立即全部结束。',[4,47],'Gallic_Wars'),
 ('caesar-civil','凯撒内战',-49,-45,['凯撒及其支持者'],['庞培、元老院派及其继承者'],'罗马政治权力与军权危机，元老院和凯撒之间的对抗无法以政治方式解决。','凯撒击败主要对手，取得罗马最高权力；这不是屋大维与安东尼的最后战争。',[15,40],"Caesar%27s_civil_war"),
 ('roman-final','罗马共和国最后内战',-32,-30,['屋大维及其支持者'],['安东尼派','托勒密埃及'],'三头政治破裂及罗马权力竞争，埃及王室与安东尼的联盟成为争端中心。','亚克兴后安东尼和克娄巴特拉失败，埃及被罗马吞并，屋大维掌握最高权力。',[25,32],'War_of_Actium'),
 ('jewish-first','第一次犹太—罗马战争',66,73,['罗马帝国'],['犹太反抗派诸集团'],'行省统治、税收、宗教和地方社会矛盾激化为反罗马起义。','罗马攻陷耶路撒冷并毁坏第二圣殿；部分据点继续抵抗，马萨达终局也有73／74年的纪年分歧。',[35.2,31.8],'First_Jewish%E2%80%93Roman_War'),
 ('byzantine-sasanian','东罗马—萨珊战争（602—628）',602,628,['东罗马帝国'],['萨珊帝国'],'东罗马皇位政变及两帝国长期竞争促成新一轮全面战争。','萨珊前期深入东罗马领土，希拉克略反攻后双方恢复大体战前边界，两个帝国均受到严重消耗。',[40,35],'Byzantine%E2%80%93Sasanian_War_of_602%E2%80%93628'),
 ('levant-conquest','阿拉伯征服黎凡特',634,638,['正统哈里发军'],['东罗马帝国及其地方盟军'],'新形成的阿拉伯穆斯林政权向叙利亚、巴勒斯坦扩张，与东罗马驻军交战。','雅尔穆克等战役后东罗马失去黎凡特大部，城市陷落时间各异，部分沿海据点延续抵抗。',[36,33],'Muslim_conquest_of_the_Levant'),
 ('egypt-conquest','阿拉伯征服埃及',639,642,['正统哈里发军'],['东罗马帝国'],'阿拉伯军队在黎凡特胜利后继续向埃及推进。','亚历山大里亚交出，埃及转入哈里发统治；其后仍有东罗马反攻。',[31,30],'Muslim_conquest_of_Egypt'),
 ('kalinga','羯陵伽战争（约前261年）',-261,-261,['孔雀帝国'],['羯陵伽'],'孔雀帝国向印度东岸羯陵伽地区扩张。','阿育王征服羯陵伽；其敕令叙述战争造成的苦难与其悔战态度。年份为通行约年，不据敕令伤亡叙述反推精确参战兵力。',[85.8,20.2],'Kalinga_War'),
 ('qin-unification','秦统一六国战争',-230,-221,['秦国'],['韩、赵、魏、楚、燕、齐（各按被征服阶段）'],'战国末期秦国依次攻灭其他主要诸侯国。','六国相继灭亡，秦王政建立秦帝国。此条为多场战争的阶段总览，不表示六国在每一年都同时参战。',[112,34],"Qin%27s_wars_of_unification"),
 ('chu-han','楚汉战争',-206,-202,['汉王刘邦及其盟军'],['项羽西楚及其盟军'],'秦亡后分封与诸侯权力分配冲突，刘邦和项羽争夺帝国继承权。','垓下战败后项羽死，刘邦建立汉朝；各地诸侯的立场曾多次变化。',[115,33],'Chu%E2%80%93Han_Contention'),
 ('an-lushan','安史之乱',755,763,['唐朝'],['安禄山、史思明及燕政权'],'边镇军权集中、宫廷与节度使冲突及叛军夺权导致大规模内战。','燕政权覆灭，唐朝恢复两京但藩镇格局和财政军事结构深受影响。',[113,36],'An_Lushan_Rebellion'),
 ('norman-england','诺曼征服英格兰',1066,1071,['诺曼底公爵及其盟军'],['英格兰王权与地方抵抗者'],'忏悔者爱德华去世后的王位继承争议引发威廉入侵。','威廉在黑斯廷斯获胜并称王，后续镇压与领地重分配逐步巩固诺曼统治。',[0,52],'Norman_Conquest'),
 ('crusade-first','第一次十字军东征',1096,1099,['十字军诸军团'],['鲁姆塞尔柱等突厥政权','法蒂玛王朝'],'拜占庭求援与教宗号召、宗教动员和领地目标共同促成远征。','十字军攻占耶路撒冷并建立拉丁政权；拜占庭与十字军之间亦存在重大利益分歧。',[35,34],'First_Crusade'),
 ('crusade-second','第二次十字军东征',1147,1149,['法国、德意志及十字军诸军团'],['赞吉王朝等地方穆斯林政权'],'埃德萨陷落后欧洲组织新一轮远征。','对大马士革的进攻失败，主要远征军撤回；伊比利亚、波罗的海行动不是本条地图中心的同一战区。',[36.3,33.5],'Second_Crusade'),
 ('crusade-third','第三次十字军东征',1189,1192,['英格兰、法国及十字军诸军团'],['阿尤布苏丹国'],'1187年哈丁失败与耶路撒冷陷落促使欧洲组织远征。','十字军恢复部分沿海据点，未夺回耶路撒冷；休战保障部分朝圣安排。',[35,33],'Third_Crusade'),
 ('crusade-fourth','第四次十字军东征',1202,1204,['十字军部分军团','威尼斯共和国'],['东罗马帝国'],'远征筹资与运输债务、威尼斯利益及东罗马皇位争端使行动转向君士坦丁堡。','君士坦丁堡遭攻占和劫掠，拉丁帝国建立，东罗马形成多个继承中心。',[29,41],'Fourth_Crusade'),
 ('mongol-khwarezm','蒙古征服花剌子模',1219,1221,['蒙古帝国'],['花剌子模帝国'],'讹答剌商队事件、使者被杀及双方的帝国扩张与敌对导致入侵。','蒙古军摧毁花剌子模主要统治中心，苏丹及继承者继续逃亡和抵抗；未将后续所有中亚战争合并为同一阶段。',[64,39],'Mongol_conquest_of_the_Khwarazmian_Empire'),
 ('mongol-jin','蒙古灭金战争',1211,1234,['蒙古帝国'],['金朝'],'蒙古向金朝边境发动战争，双方长期交战。','金朝在蔡州覆灭；南宋在最后阶段与蒙古合作，不能把南宋列为1211年以来一直参战。',[113,36],'Mongol_conquest_of_the_Jin_dynasty'),
 ('mongol-song','蒙古—南宋战争',1235,1279,['蒙古帝国／元朝'],['南宋'],'蒙古与南宋关系破裂后，蒙古持续向长江流域及南方扩张。','临安投降后南宋残余政权继续抵抗，1279年崖山后其主要朝廷覆灭。',[113,30],'Mongol_conquest_of_the_Song_dynasty'),
 ('mongol-japan','元朝两次进攻日本',1274,1281,['元朝','高丽（受元朝支配的征发力量）'],['日本镰仓幕府及地方武士'],'忽必烈要求日本臣服未果，元朝组织跨海远征。','1274与1281年远征均未形成对日本的持久占领；风暴、海运困难与日方抵抗共同影响结果。',[130.3,33.6],'Mongol_invasions_of_Japan'),
 ('mongol-rus','蒙古西征与罗斯诸公国',1237,1242,['蒙古帝国西征军'],['罗斯诸公国','波兰及匈牙利等（分阶段）'],'蒙古向欧亚西部扩张，先后攻击罗斯与中欧诸国。','罗斯多个中心遭破坏并逐步形成对蒙古的臣属关系，蒙古军随后撤出中欧主要战区。',[35,51],'Mongol_invasion_of_Kievan_Rus%27'),
 ('hundred-years','英法百年战争',1337,1453,['英格兰及其阶段性盟友'],['法国及其阶段性盟友'],'法国王位继承主张、英王在法国的封地及政治经济竞争引发长期战争。','法国收复英格兰在法国的大部分领地，加来仍在英格兰手中；此为多阶段战争群，停战年不意味着每处持续交火。',[2,47],'Hundred_Years%27_War'),
 ('polish-teutonic','波兰—立陶宛与条顿骑士团战争',1409,1411,['波兰王国','立陶宛大公国'],['条顿骑士团国'],'萨莫吉希亚起义及波兰、立陶宛与骑士团的边疆和政治争端激化。','格伦瓦尔德会战后双方订立第一次托伦和约，骑士团遭受重大损失但并未立即灭亡。',[20,54],'Polish%E2%80%93Lithuanian%E2%80%93Teutonic_War'),
 ('roses','玫瑰战争',1455,1487,['兰开斯特派及其后继支持者'],['约克派及其后继支持者'],'英格兰王位继承、贵族派系与王权危机演化为多轮内战。','都铎王朝在博斯沃思和斯托克等战役后巩固王位；不是两个固定阵营32年连续交战。',[-1,52],'Wars_of_the_Roses'),
 ('livonian','立窝尼亚战争',1558,1583,['俄罗斯沙皇国'],['立窝尼亚诸政权及波兰—立陶宛、瑞典等（分阶段）'],'俄罗斯争取波罗的海通道，立窝尼亚秩序瓦解引发周边诸国争夺。','俄罗斯未能长期保有其主要战果，立窝尼亚地域由周边政权重新瓜分。',[26,58],'Livonian_War'),
 ('aztec-conquest','西班牙及其原住民盟军征服阿兹特克',1519,1521,['西班牙远征军','特拉斯卡拉等原住民盟邦'],['阿兹特克三邦同盟'],'西班牙殖民扩张与中部美洲既有政治冲突交织，多个原住民政权选择与科尔特斯合作。','特诺奇蒂特兰在围城后陷落，殖民秩序逐步建立；不能把原住民盟军省略为少数西班牙士兵单独征服帝国。',[-99.1,19.4],'Spanish_conquest_of_the_Aztec_Empire'),
 ('inca-conquest','西班牙征服印加及新印加抵抗',1532,1572,['西班牙征服者及原住民盟军'],['印加王权及其继承抵抗中心'],'西班牙殖民远征利用印加继承内战后的分裂与地方矛盾展开征服。','阿塔瓦尔帕被俘和库斯科失守后仍有长期抵抗；1572年比尔卡班巴被攻陷，图帕克·阿马鲁一世被处决。',[-72,-13],'Spanish_conquest_of_the_Inca_Empire'),
 ('songhai-invasion','摩洛哥入侵桑海',1591,1591,['摩洛哥萨阿德王朝军'],['桑海帝国'],'萨阿德王权争夺跨撒哈拉贸易、盐矿与苏丹地区的资源和政治控制。','通迪比战役后桑海主要城市遭占领，帝国解体；不能据此认定摩洛哥有效统治原桑海全部地域。',[-1,17],'Moroccan_invasion_of_the_Songhai_Empire'),
 ('talikota','塔利科塔战役与德干—毗奢耶那伽罗战争',1565,1565,['毗奢耶那伽罗王国'],['比贾布尔、艾哈迈德讷格尔、戈尔康达、比达尔苏丹国联军'],'毗奢耶那伽罗干预德干诸苏丹国政治及区域势力竞争促成联军。','联军在塔利科塔获胜，毗奢耶那伽罗首都遭破坏，但王朝残余并未在1565年立即灭亡。',[76.1,16.5],'Battle_of_Talikota'),
 ('mughal-maratha','莫卧儿—马拉塔战争',1680,1707,['莫卧儿帝国'],['马拉塔政权'],'莫卧儿向德干推进，与马拉塔的扩张、堡垒体系及地方征税权发生冲突。','莫卧儿未能消灭马拉塔力量，长期战争消耗其财政和军队；1707年是奥朗则布去世与这一阶段的分界，非一份终结一切冲突的和约。',[75,18],'Mughal%E2%80%93Maratha_Wars'),
]
ALIASES={
 '阿契美尼德帝国':['Achaemenid Empire'],'罗马共和国':['Roman Republic'],'罗马帝国':['Roman Empire'],
 '迦太基':['Carthage'],'托勒密埃及':['Ptolemaic Kingdom'],'东罗马帝国':['Byzantine Empire','Eastern Roman Empire'],
 '萨珊帝国':['Sasanian Empire'],'孔雀帝国':['Maurya Empire'],'蒙古帝国':['Mongol Empire'],
 '金朝':['Jin Dynasty','Jin dynasty (1115–1234)'],'南宋':['Southern Song Dynasty','Song Dynasty'],
 '蒙古帝国／元朝':['Mongol Empire','Yuan Dynasty'],'元朝':['Yuan Dynasty'],'秦国':['Qin','Qin Dynasty'],
 '唐朝':['Tang Dynasty'],'英格兰及其阶段性盟友':['Kingdom of England'],'法国及其阶段性盟友':['Kingdom of France'],
 '俄罗斯沙皇国':['Tsardom of Russia'],'桑海帝国':['Songhai Empire'],'摩洛哥萨阿德王朝军':['Saadi Sultanate','Morocco'],
 '毗奢耶那伽罗王国':['Vijayanagara Empire'],'莫卧儿帝国':['Mughal Empire'],'马拉塔政权':['Maratha Empire'],
 '波兰王国':['Kingdom of Poland'],'立陶宛大公国':['Grand Duchy of Lithuania'],'条顿骑士团国':['Teutonic Order'],
 '罗马共和国及其盟邦':['Roman Republic'],'迦太基及其盟邦':['Carthage'],'罗马共和国（凯撒军）':['Roman Republic'],
 '蒙古帝国西征军':['Mongol Empire'],'正统哈里发军':['Rashidun Caliphate'],
 '东罗马帝国及其地方盟军':['Byzantine Empire','Eastern Roman Empire'],
 '阿尤布苏丹国':['Ayyubid Dynasty','Ayyubid Sultanate'],'威尼斯共和国':['Republic of Venice'],
 '阿兹特克三邦同盟':['Aztec Empire','Aztec Triple Alliance'],'印加王权及其继承抵抗中心':['Inca Empire'],
}
def main():
 p=ROOT/'public/data/historical-wars-supplements.json';db=json.loads(p.read_bytes());existing={r['war']['id']:r for r in db['wars']}
 for slug,title,a,b,left,right,cause,result,location,article in ROWS:
  ident='historic-'+slug;url='https://en.wikipedia.org/wiki/'+article;periods=[[a,b]]
  if slug=='mongol-japan':periods=[[1274,1274],[1281,1281]]
  participants=[]
  for side,names in [('1',left),('2',right)]:
   for name in names:
    r={'side':side,'name':name,'periods':periods}
    if name in ALIASES:r['polityNames']=ALIASES[name]
    participants.append(r)
  note='有来源补录的主要交战方概览，部分地方盟军与阶段性转向未逐一穷尽。多阶段战争群不等于各方在每一年持续作战；不据战争条目自动推算占领线。'
  war={'id':ident,'name':title,'category':'古代与中世纪历史战争补录','source':'历史战争专项核对（2026-10-31）','url':url,'from':a,'to':b,'periods':periods,'participants':participants,'scopeNote':note}
  detail={'id':ident,'title':title,'cause':cause,'result':result,'location':location,'sources':[url],'strengthAssessment':'未收录可按同一日期、同一战区与同一统计口径比较的双方兵力。古代记载、后世估计与军队总额不混为精确参战人数。','sideNames':['主要阵营一','主要阵营二'],'scopeNote':note}
  if slug=='kalinga':detail['sources'].append('https://digital.library.cornell.edu/catalog/ss%3A3856336')
  existing[ident]={'war':war,'detail':detail}
 db.update(reviewedAt='2026-10-31',wars=list(existing.values()));p.write_text(json.dumps(db,ensure_ascii=False,separators=(',',':')),encoding='utf8');print('Early conflicts added',len(ROWS),'total supplements',len(existing),flush=True)
if __name__=='__main__':main()
