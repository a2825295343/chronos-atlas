"""Early and regional wars, dated participation, plus existing COW detail repair."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROWS=[
 ('kadesh','卡迭石战役',-1274,-1274,['埃及新王国'],['赫梯帝国'],'埃及与赫梯争夺叙利亚的战略据点及附属城邦。','双方均有宣传性胜利叙述，埃及未持久夺取卡迭石；后来的埃及—赫梯和约不能当作战役当年就签订。',[36.5,34.5],'Battle_of_Kadesh'),
 ('assyria-fall','米底与巴比伦征服亚述',-614,-609,['新巴比伦王国','米底诸军'],['新亚述帝国'],'亚述内战和地方反抗削弱王权，巴比伦与米底联盟向其主要中心进攻。','亚述城与尼尼微相继失陷，哈兰阶段后亚述王权的主要独立抵抗终止。',[43,36],'Medo-Babylonian_conquest_of_the_Assyrian_Empire'),
 ('diadochi','亚历山大继业者战争',-322,-281,['亚历山大帝国各继承军政集团'],['相互竞争的继承军政集团（按阶段变化）'],'亚历山大死后，摄政、王室与各地将领争夺继承权和辖区。','多个希腊化王国形成。此为多轮战争总览，不能把各王国从一开始就固定放进两个阵营。',[35,37],'Wars_of_the_Diadochi'),
 ('macedonian-first','第一次马其顿战争',-214,-205,['罗马共和国及其盟邦'],['安提柯马其顿'],'马其顿与汉尼拔的联盟及亚得里亚海竞争使罗马介入希腊战区。','双方议和，主要争端未彻底解决。',[21,40],'First_Macedonian_War'),
 ('macedonian-second','第二次马其顿战争',-200,-197,['罗马共和国及希腊盟邦'],['安提柯马其顿'],'马其顿在爱琴海与希腊的扩张及各国求援促使罗马发动战争。','罗马在库诺斯克法莱获胜，马其顿失去在希腊的大部分优势。',[22,39],'Second_Macedonian_War'),
 ('roman-seleucid','罗马—塞琉古战争',-192,-188,['罗马共和国及帕加马等盟邦'],['塞琉古帝国及其盟军'],'安条克三世进入希腊，与罗马在东地中海秩序问题上冲突。','马格尼西亚后塞琉古被迫接受阿帕米亚和约，退出小亚细亚的大部分控制区。',[28,38],'Roman%E2%80%93Seleucid_War'),
 ('macedonian-third','第三次马其顿战争',-171,-168,['罗马共和国'],['安提柯马其顿'],'珀尔修斯扩大影响，与罗马和周边势力的外交、军事矛盾升级。','彼得纳战役后安提柯王朝覆灭，马其顿被重新划分。',[22.5,40.4],'Third_Macedonian_War'),
 ('mithridatic-first','第一次米特里达梯战争',-89,-85,['罗马共和国'],['本都王国及其盟军'],'本都与罗马在小亚细亚的权力、属国及地方政治争端激化。','苏拉在希腊获胜，达尔达诺斯安排结束本阶段主要战争，但冲突随后再起。',[27,38],'First_Mithridatic_War'),
 ('mithridatic-third','第三次米特里达梯战争',-73,-63,['罗马共和国'],['本都王国及亚美尼亚盟军'],'比提尼亚归属及罗马与米特里达梯六世的长期竞争再次引发战争。','本都王权失败，罗马重组东部行省和属国格局；亚美尼亚并非整个时段持续同等参战。',[35,40],'Third_Mithridatic_War'),
 ('vandal-justinian','东罗马征服汪达尔王国',533,534,['东罗马帝国'],['汪达尔王国'],'北非王位政变及查士丁尼恢复帝国控制的计划促成远征。','贝利萨留击败汪达尔军，王国覆灭，北非进入东罗马统治。',[10,36],'Vandalic_War'),
 ('gothic-italy','东罗马—东哥特战争',535,554,['东罗马帝国'],['东哥特王国'],'查士丁尼政权进军意大利，与东哥特王权争夺统治权。','东哥特主要抵抗被击败，意大利遭受长期战争破坏；后续伦巴第入侵不属于本条同一阶段。',[13,42],'Gothic_War_(535%E2%80%93554)'),
 ('persia-conquest','阿拉伯征服萨珊波斯',633,651,['正统哈里发军'],['萨珊帝国及地方抵抗力量'],'阿拉伯穆斯林政权向伊拉克与伊朗扩张，与萨珊驻军交战。','卡迪西亚、纳哈万等战役后萨珊中央王权瓦解；地方抵抗和宗教变化并未在651年瞬间结束。',[48,33],'Muslim_conquest_of_Persia'),
 ('first-fitna','第一次伊斯兰内战',656,661,['阿里及其支持者'],['反对阿里或争夺哈里发权力的各派（分阶段）'],'奥斯曼遇刺后，继承合法性、报复及地区军政集团矛盾激化。','多轮交战与仲裁后阿里遇刺，穆阿维叶建立新的统治格局；反对阵营并不是始终一致的单一集团。',[42,34],'First_Fitna'),
 ('second-fitna','第二次伊斯兰内战',680,692,['倭马亚王权支持者'],['祖拜尔派及其他竞争集团（分阶段）'],'叶齐德继位的合法性争论与地区政治、宗教分歧引发多轮冲突。','倭马亚王权恢复对主要地区的统治，其他运动并未全部消失。',[40,24],'Second_Fitna'),
 ('abbasid-revolution','阿拔斯革命',747,750,['阿拔斯运动及其盟军'],['倭马亚哈里发王权'],'呼罗珊及各地对倭马亚统治的不满与阿拔斯家族政治动员结合。','扎卜河等战役后大马士革的倭马亚王权覆灭，阿拔斯王朝建立。',[44,35],'Abbasid_Revolution'),
 ('sui-goguryeo','隋与高句丽战争',598,614,['隋朝'],['高句丽'],'隋朝与高句丽在边疆、朝贡和地区秩序问题上对立。','598年及612—614年远征未能消灭高句丽，动员与后勤负担加重隋末危机；中间年份不视为同等连续出兵。',[124,40],'Goguryeo%E2%80%93Sui_War'),
 ('tang-goguryeo','唐与高句丽战争',645,668,['唐朝'],['高句丽'],'唐朝沿袭半岛与辽东方向的军事目标，并与新罗的扩张相互配合。','668年唐与新罗联军攻陷平壤，高句丽王权覆灭，之后唐与新罗之间另有战争。',[125,39],'Goguryeo%E2%80%93Tang_War'),
 ('tang-silla','新罗—唐战争',670,676,['新罗及地方抵抗力量'],['唐朝'],'高句丽、百济覆灭后的领土与驻军安排使唐与新罗联盟破裂。','新罗巩固半岛南部控制，唐的安东机构迁移；并非新罗当时统治整个现代朝鲜半岛。',[127,37],'Silla%E2%80%93Tang_War'),
 ('mongol-korea','蒙古征服高丽',1231,1259,['蒙古帝国'],['高丽'],'蒙古要求臣服及边疆、使者争端引发多轮入侵，高丽王廷迁往江华岛。','长期战争后高丽王权接受蒙古宗主关系，其王朝和部分国内机构继续存在；期间有停战与多轮复战。',[127,38],'Mongol_invasions_of_Korea'),
 ('genpei','源平战争',1180,1185,['源氏及其盟军'],['平氏及其盟军'],'日本王廷与武士集团间的继承、军事和政治权力竞争扩大。','平氏在坛之浦失败，源赖朝随后巩固武家政权；不将所有源氏支系视为从未内斗。',[135,35],'Genpei_War'),
 ('onin','应仁之乱',1467,1477,['细川胜元一方的诸大名'],['山名持丰一方的诸大名'],'将军继承、守护大名继承与京都政治矛盾引发内战。','京都遭严重破坏，幕府权威削弱，各地冲突持续；十年结束不等于整个日本恢复和平。',[135.77,35.01],'Onin_War'),
 ('hussite','胡斯战争',1419,1434,['胡斯派各集团'],['王权、教会及十字军联盟（分阶段）'],'胡斯被处决后的宗教、等级政治与波希米亚王位争端激化。','胡斯派内部亦发生战争，1434年利帕尼改变力量格局，随后宗教与王位安排逐步达成。',[14.4,50.1],'Hussite_Wars'),
 ('granada','格拉纳达战争',1482,1492,['卡斯蒂利亚与阿拉贡王权'],['格拉纳达酋长国'],'伊比利亚王权扩张与格拉纳达内部王位争夺相互交织。','格拉纳达投降，纳斯里德王权结束；后续宗教压迫与反抗不等于所有问题于1492年消失。',[-3.6,37.2],'Granada_War'),
 ('ethiopian-adal','埃塞俄比亚—阿达尔战争',1529,1543,['埃塞俄比亚帝国'],['阿达尔苏丹国及其盟军'],'埃塞俄比亚与阿达尔的地区霸权、贡赋和宗教政治竞争演化为大规模战争。','阿达尔军早期深入高地，1543年瓦伊纳达加等战役后其攻势受挫；双方社会与政治均受到长期破坏。',[39,12],'Ethiopian%E2%80%93Adal_War'),
 ('anglo-mysore-first','第一次英迈战争',1767,1769,['迈索尔王国'],['东印度公司及阶段性盟军'],'德干政治与公司扩张使迈索尔、海得拉巴、马拉塔和英国公司关系多次转变。','海德尔·阿里逼近马德拉斯后缔结和约，双方承诺互助但很快再生争端。',[78,13],'First_Anglo-Mysore_War'),
 ('anglo-mysore-second','第二次英迈战争',1780,1784,['迈索尔王国'],['东印度公司'],'前次和约承诺、法国据点及公司在南印度的行动引发新一轮战争。','战争以芒格洛尔条约结束，迈索尔仍为重要独立力量。',[77,13],'Second_Anglo-Mysore_War'),
 ('anglo-mysore-third','第三次英迈战争',1790,1792,['迈索尔王国'],['东印度公司、海得拉巴和马拉塔联盟'],'迈索尔进攻与公司有关联的特拉凡哥尔后，英国及其盟友发动战争。','蒂普被迫割让大片领地并作出赔款和人质安排。',[77,12.5],'Third_Anglo-Mysore_War'),
 ('anglo-mysore-fourth','第四次英迈战争',1799,1799,['迈索尔王国'],['东印度公司及其盟军'],'公司试图消除蒂普及其对外联系造成的战略威胁。','塞林伽巴丹陷落，蒂普战死，迈索尔部分领土被瓜分并恢复受保护的沃德亚尔王室。',[76.7,12.4],'Fourth_Anglo-Mysore_War'),
 ('anglo-maratha-first','第一次英马拉塔战争',1775,1782,['马拉塔政治集团'],['东印度公司及其支持的竞争者'],'佩什瓦继承与公司干预马拉塔内部政治导致战争。','萨尔拜条约结束本阶段，马拉塔体系继续存在。',[74,19],'First_Anglo-Maratha_War'),
 ('anglo-maratha-second','第二次英马拉塔战争',1803,1805,['信德、博恩斯勒和霍尔卡等马拉塔集团（分阶段）'],['东印度公司及其盟军'],'佩什瓦接受公司保护及诸家族与公司之间的军事、外交竞争引发战争。','多次条约使公司取得重要优势，但马拉塔各邦并未在1805年全部消失。',[77,22],'Second_Anglo-Maratha_War'),
 ('caucasian-group','高加索战争与俄国征服（分阶段）',1763,1864,['俄罗斯帝国'],['切尔克斯诸部及其他高加索地方抵抗者'],'俄国边疆扩张、军事交通线、地方自治与土地控制的冲突引发长期战争。','1859年沙米尔投降，1864年西高加索主要战争结束，大量人口流离失所；这不是所有地方在101年里同时连续作战。',[44,43],'Caucasian_War'),
 ('ottoman-saudi','奥斯曼—沙特战争（埃及远征）',1811,1818,['奥斯曼体系下的埃及远征军'],['德拉伊耶酋长国'],'第一沙特国家在汉志的扩张及奥斯曼恢复宗教圣地控制的要求促成埃及远征。','埃及军最终攻陷并摧毁德拉伊耶，第一沙特国家瓦解；不等于埃及从此直接统治整个阿拉伯半岛。',[42,24],'Ottoman%E2%80%93Saudi_War'),
]
ALIASES={
 '埃及新王国':['New Kingdom of Egypt'],'赫梯帝国':['Hittite Empire'],'新巴比伦王国':['Neo-Babylonian Empire'],'新亚述帝国':['Neo-Assyrian Empire'],
 '罗马共和国及其盟邦':['Roman Republic'],'罗马共和国及希腊盟邦':['Roman Republic'],'罗马共和国及帕加马等盟邦':['Roman Republic'],'罗马共和国':['Roman Republic'],
 '安提柯马其顿':['Antigonid Macedonia'],'塞琉古帝国及其盟军':['Seleucid Empire'],'东罗马帝国':['Byzantine Empire','Eastern Roman Empire'],'东哥特王国':['Ostrogothic Kingdom'],'汪达尔王国':['Vandal Kingdom'],
 '正统哈里发军':['Rashidun Caliphate'],'萨珊帝国及地方抵抗力量':['Sasanian Empire'],'倭马亚王权支持者':['Umayyad Caliphate'],'倭马亚哈里发王权':['Umayyad Caliphate'],'阿拔斯运动及其盟军':['Abbasid Caliphate'],
 '隋朝':['Sui Dynasty'],'唐朝':['Tang Dynasty'],'高句丽':['Goguryeo'],'新罗及地方抵抗力量':['Silla'],'高丽':['Goryeo'],'蒙古帝国':['Mongol Empire'],
 '迈索尔王国':['Kingdom of Mysore'],'东印度公司及阶段性盟军':['British India'],'东印度公司':['British India'],'东印度公司及其盟军':['British India'],'东印度公司、海得拉巴和马拉塔联盟':['British India','Hyderabad State','Maratha Empire'],
 '马拉塔政治集团':['Maratha Empire','Maratha Confederacy States'],'信德、博恩斯勒和霍尔卡等马拉塔集团（分阶段）':['Maratha Empire','Maratha Confederacy States'],
 '俄罗斯帝国':['Russian Empire'],'切尔克斯诸部及其他高加索地方抵抗者':['Circassian Principalities','Dagestani Khanates and Free Societies'],
 '德拉伊耶酋长国':['Emirate of Diriyah'],'奥斯曼体系下的埃及远征军':['Ottoman Empire','Egypt Eyalet'],'埃塞俄比亚帝国':['Ethiopian Empire','Ethiopia'],'阿达尔苏丹国及其盟军':['Adal Sultanate'],
}
def main():
 p=ROOT/'public/data/historical-wars-supplements.json';db=json.loads(p.read_bytes());entries={r['war']['id']:r for r in db['wars']}
 for slug,title,a,b,left,right,cause,result,location,article in ROWS:
  ident='historic-'+slug;url='https://en.wikipedia.org/wiki/'+article;periods=[[a,b]]
  if slug=='sui-goguryeo':periods=[[598,598],[612,614]]
  actors=[{'side':side,'name':name,'periods':periods,'polityNames':ALIASES.get(name,[])}for side,names in [('1',left),('2',right)]for name in names]
  if slug=='ethiopian-adal':actors.append({'side':'1','name':'葡萄牙远征军','periods':[[1541,1543]],'polityNames':['Kingdom of Portugal','Portuguese Empire']})
  if slug=='tang-goguryeo':actors.append({'side':'1','name':'新罗','periods':[[660,668]],'polityNames':['Silla']})
  if slug=='caucasian-group':actors.append({'side':'2','name':'高加索伊玛目国','periods':[[1829,1859]],'polityNames':['Caucasian Imamate']})
  note='主要交战方概览；多阶段战争群不表示各方在每一年同时连续作战，盟友与竞争集团的立场可能改变。未据战争起止自动生成精确占领线。'
  war={'id':ident,'name':title,'category':'历史战争与区域战争群','source':'2026-11-01有来源补录','url':url,'from':a,'to':b,'periods':periods,'participants':actors,'scopeNote':note}
  detail={'id':ident,'title':title,'cause':cause,'result':result,'location':location,'sources':[url],'scopeNote':note,'strengthAssessment':'未收录可在同一日期、战区与口径下相加比较的双方兵力；不以伤亡人数或传说中的军队总数代填。'}
  if slug=='kadesh':detail['commanders']=['拉美西斯二世','穆瓦塔里二世'];detail['sources'].append('https://artsandculture.google.com/asset/the-kadesh-treaty/twHd3aD_Ds-YYA')
  if slug=='sui-goguryeo':detail['sources'].append('https://encykorea.aks.ac.kr/Article/E0036400')
  if slug=='ethiopian-adal':detail['commanders']=['莱布纳·登格尔与格拉乌德沃斯','艾哈迈德·伊本·易卜拉欣·加齐','克里斯托旺·达·伽马（1541—1542）']
  entries[ident]={'war':war,'detail':detail}
 db['wars']=list(entries.values());db['reviewedAt']='2026-11-01';p.write_text(json.dumps(db,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 # Enrich existing 19th-century wars instead of creating a duplicate entry.
 path=ROOT/'public/data/war-details.json';details=json.loads(path.read_bytes());dd={r['id']:r for r in details['wars']}
 dd['cow-extra-347']={**dd.get('cow-extra-347',{}),'id':'cow-extra-347','title':'1857年印度起义','reviewedHistorical':True,'cause':'公司军队的不满、宗教与军制争议，阿瓦德等地吞并、土地及地方统治权冲突共同促成起义；不能只用子弹润滑脂解释。','result':'英国军队及其盟军镇压主要起义中心，1858年王室接管公司统治；各地抵抗终止时间并不一致。','location':[80.95,26.85],'sources':['https://www.nam.ac.uk/explore/decisive-events-indian-mutiny','https://www.parliament.uk/about/living-heritage/evolutionofparliament/legislativescrutiny/parliament-and-empire/parliament-and-the-american-colonies-before-1765/east-india-company-and-raj-1785-1858/'],'commanders':['英国及公司军队的多位将领','巴哈杜尔沙二世、拉妮·拉克希米·巴伊、贝古姆·哈兹拉特·玛哈尔等各地领袖'],'strengthAssessment':'孟加拉军编制、起义军人数和英国增援不是同一口径；不同中心的兵力也随时间变化，未合并成一个虚假的精确比例。'}
 dd['cow-intra-500']={**dd.get('cow-intra-500',{}),'id':'cow-intra-500','mergeHistorical':'historic-caucasian-group'}
 details['wars']=list(dd.values());path.write_text(json.dumps(details,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 path=ROOT/'public/data/conflicts.json';conf=json.loads(path.read_bytes())
 for w in conf['wars']:
  if w['id']=='cow-extra-347':
   for actor in w.get('participants',[]):
    if actor.get('side')=='1':actor['polityNames']=list(set(actor.get('polityNames',[])+['British India','British Raj']))
    else:actor['polityNames']=list(set(actor.get('polityNames',[])+['Awadh Rebel Government']))
 conf['wars']=[w for w in conf['wars']];path.write_text(json.dumps(conf,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('New historical war records',len(ROWS),'total supplement records',len(entries),flush=True)
if __name__=='__main__':main()
