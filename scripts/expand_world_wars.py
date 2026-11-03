"""Reviewed global conflicts; preserve COW battle thresholds and distinguish campaigns."""
from territory_repair_stage import read,write
TAG='world-wars-2026-11-02'
def main():
 db=read('public/data/historical-wars-supplements.json');rows={r['war']['id']:r for r in db['wars']};added=[]
 def p(label,names,a,b):return dict(name=label,displayName=label,polityNames=names.split('|')if names else[],periods=[[a,b]])
 def war(slug,title,a,b,left,right,cause,result,source,loc,commanders):
  ident='historic-'+slug
  ps=[dict(r,side=side)for side,group in [('1',left),('2',right)]for r in group]
  note='本条按年筛选实际参战阶段；内战同一国家可同时有对立派别。同侧不自动形成永久同盟，战事期间可有停战，未据文字资料编造逐年占领线。'
  w=dict(id=ident,name=title,category='历史战争与战役',source='有来源的分期战争补录',url=source,participants=ps,periods=[[a,b]],scopeNote=note,**{'from':a,'to':b})
  d=dict(id=ident,title=title,cause=cause,result=result,sources=[source],location=loc,commanders=commanders,scopeNote=note,strengthAssessment='缺少同一战区、同一时点且口径一致的双方兵力；不把全国军队总数或后世夸张数字当作实际投入。',supplement=TAG)
  rows[ident]=dict(war=w,detail=d);added.append(ident)
 eng=lambda label,a,b:p(label,'Kingdom of England|English Territories',a,b)
 fr=lambda label,a,b:p(label,'Kingdom of France|Bourbon Kingdom of France',a,b)
 pt=lambda label,a,b:p(label,'Kingdom of Portugal|Portuguese Empire',a,b)
 war('barons-first','第一次英格兰男爵战争',1215,1217,[eng('约翰及亨利三世王党',1215,1217)],[p('反叛男爵','Kingdom of England',1215,1217),p('法国王子路易的远征军','',1216,1217)],'国王、男爵与《大宪章》履行问题的冲突扩大，反叛者邀请法国王子路易争夺王位。','约翰去世后王党拥立亨利三世；1217年林肯及桑威奇战事后，路易放弃英格兰王位主张。','https://www.english-heritage.org.uk/sieges-of-dover',[-.1,51.5],['约翰、威廉·马歇尔','路易王子及反叛男爵'])
 war('barons-second','第二次英格兰男爵战争',1264,1267,[eng('亨利三世与爱德华王党',1264,1267)],[p('西蒙·德·孟福尔及男爵反对派','Kingdom of England',1264,1267)],'改革派男爵与王室围绕王权、财政及外来亲属势力的争执导致内战。','王党在1265年伊夫舍姆击败孟福尔；其余抵抗与和解持续至1267年。','https://www.english-heritage.org.uk/learn/histories/women-in-history/eleanor-de-montfort',[-2,52.1],['亨利三世、爱德华王子','西蒙·德·孟福尔'])
 for slug,a,b,result in [('scottish-independence-first',1296,1328,'1328年爱丁堡—北安普敦条约承认苏格兰独立及罗伯特一世王权。'),('scottish-independence-second',1332,1357,'1357年伯威克条约安排大卫二世获释及赎金，结束这一轮主要战争。')]:
  war(slug,'苏格兰独立战争（'+str(a)+'—'+str(b)+'）',a,b,[p('苏格兰王权及其支持者','Scotland|Kingdom of Scotland',a,b)],[eng('英格兰王权及苏格兰竞争者的支持军',a,b)],'英格兰的宗主权要求、苏格兰王位继承及贵族派系冲突相互交织。',result,'https://en.wikipedia.org/wiki/Wars_of_Scottish_Independence',[-3.2,56],['华莱士、罗伯特一世／大卫二世等（分阶段）','爱德华一世、二世、三世等（分阶段）'])
 war('castilian-succession','卡斯蒂利亚王位继承战争',1475,1479,[p('伊莎贝拉与费尔南多支持者','Castile|Kingdom of Castile|Crown of Castile|Crown of Aragon|Aragon',1475,1479)],[pt('葡萄牙及胡安娜支持者',1475,1479)],'恩里克四世去世后，两派争夺卡斯蒂利亚王位，并牵涉葡萄牙及大西洋贸易权利。','1479年阿尔卡索瓦什条约确认伊莎贝拉的卡斯蒂利亚王位，并划分大西洋利益。','https://en.wikipedia.org/wiki/War_of_the_Castilian_Succession',[-5,40],['伊莎贝拉一世、费尔南多二世','阿方索五世、胡安娜'])
 war('portuguese-succession','葡萄牙王位继承战争',1580,1583,[p('腓力二世及支持者','Spain|Spanish Empire|Habsburg Spain',1580,1583)],[pt('安东尼奥及其支持者',1580,1583)],'恩里克无嗣去世后，多方提出葡萄牙王位要求，安东尼奥与西班牙腓力二世的支持者交战。','腓力取得葡萄牙王冠；安东尼奥支持者在亚速尔的抵抗至1583年被击败，葡萄牙进入伊比利亚共主时期。','https://en.wikipedia.org/wiki/War_of_the_Portuguese_Succession',[-9,39],['腓力二世、阿尔瓦公爵','安东尼奥、菲利波·斯特罗齐'])
 war('portuguese-restoration','葡萄牙王政复辟战争',1640,1668,[pt('布拉干萨葡萄牙王权',1640,1668)],[p('西班牙王权','Spain|Spanish Empire|Habsburg Spain',1640,1668)],'葡萄牙1640年政变拥立若昂四世，反抗伊比利亚共主统治，西班牙试图恢复王权。','1668年里斯本条约承认布拉干萨王室与葡萄牙的独立王权。','https://en.wikipedia.org/wiki/Portuguese_Restoration_War',[-7.5,39],['若昂四世、阿方索六世时期葡军','腓力四世时期西班牙军队'])
 war('french-religion','法国宗教战争（八次战争总览）',1562,1598,[fr('王室、天主教军与联盟（关系随阶段改变）',1562,1598)],[p('胡格诺派及其军队','Kingdom of France|Bourbon Kingdom of France',1562,1598)],'宗教改革、王权与贵族竞争引发数轮内战；王室、天主教联盟与新教派并非始终只有两个固定阵营。','亨利四世巩固王权，1598年南特敕令及对外和约结束这组主要战争。此条为系列概览，不把1562—1598年都视为持续作战。','https://museeprotestant.org/notice/les-huit-guerres-de-religion-1562-1598/',[2,47],['孔代亲王、科利尼、亨利·德·纳瓦拉','吉斯家族及各阶段王室将领'])
 war('english-civil-series','英格兰内战（三次战争总览）',1642,1651,[p('议会派与新模范军','Kingdom of England|Commonwealth of England|English Commonwealth',1642,1651)],[eng('王党及其分阶段支持者',1642,1651)],'王室与议会围绕财政、宗教及政治权力的长期争端，结合不列颠诸王国冲突，导致战争。','王党失败，查理一世1649年被处死；1651年伍斯特战役后英格兰主要战事结束。爱尔兰与苏格兰的相关战事另有自身分期。','https://britishcivilwars.ncl.ac.uk/background/',[-1.5,52],['查理一世、查理二世','费尔法克斯、克伦威尔'])
 war('thirty-years','三十年战争',1618,1648,[p('皇帝与奥地利哈布斯堡军','Holy Roman Empire|Habsburg Monarchy|Austrian Hereditary Lands|Archduchy of Austria',1618,1648),p('西班牙哈布斯堡军','Spain|Spanish Empire|Habsburg Spain',1618,1648),p('巴伐利亚及天主教联盟','Duchy of Bavaria|Electorate of Bavaria',1618,1648)],[p('波希米亚起义军','Kingdom of Bohemia',1618,1620),p('丹麦干预军','Kingdom of Denmark|Denmark',1625,1629),p('瑞典军','Kingdom of Sweden|Sweden',1630,1648),fr('法国军',1635,1648),p('德意志新教各邦（分阶段）','Electorate of the Palatinate',1618,1648)],'帝国内的宗教与宪制矛盾、波希米亚王位及哈布斯堡与欧洲诸强的竞争扩大为跨国战争。','1648年威斯特伐利亚和约调整帝国宗教与政治安排；法西战争延续至1659年，不能把所有相关战争都终止于1648年。',"https://en.wikipedia.org/wiki/Thirty_Years%27_War",[11,50],['华伦斯坦、蒂利','古斯塔夫二世·阿道夫、班纳、托尔斯滕森、孔代等'])
 war('ly-song','宋越战争',1075,1077,[p('北宋军','Northern Song|Song Dynasty',1075,1077)],[p('李氏大越军','Ly Dynasty|Lý Dynasty',1075,1077)],'边境竞争与军备紧张导致大越军先攻宋边区，宋随后向南出兵。','双方在如月江一线交战后撤军、谈判并逐步处理俘虏及边境问题。','https://en.wikipedia.org/wiki/L%C3%BD%E2%80%93Song_War',[106,22],['李常杰','郭逵、赵卨'])
 for slug,a,b,invader in [('mongol-viet-1258',1258,1258,'Mongol Empire'),('yuan-viet-1285',1285,1285,'Yuan Dynasty'),('yuan-viet-1287',1287,1288,'Yuan Dynasty')]:
  war(slug,'蒙古／元与大越战争（'+str(a)+('—'+str(b)if a!=b else'')+'）',a,b,[p('蒙古／元远征军',invader,a,b)],[p('陈氏大越军','Tran Dynasty|Trần Dynasty',a,b)],'蒙古及元朝要求臣服与军事通道，大越王权抵抗外来军事控制。','远征军在补给、疾病及大越反击下撤出；1288年白藤江战事是最后一次远征的关键。军事退却不等于此后双方不存在朝贡外交。','https://en.wikipedia.org/wiki/Mongol_invasions_of_Vietnam',[105.8,21],['陈太宗、陈圣宗、陈仁宗、陈兴道（依阶段）','兀良合台／脱欢等（依阶段）'])
 war('lam-son','蓝山起义与大越复国战争',1418,1427,[p('明朝驻军','Ming Dynasty',1418,1427)],[p('黎利与蓝山军','Le Dynasty|Later Le Dynasty|Lê Dynasty|Later Lê Dynasty',1418,1427)],'明朝统治交趾引发持续抵抗，黎利在清化起兵并逐渐扩大控制。','明军在主要战役中受挫后撤出；黎利1428年建立后黎王朝。此处不把1428年的正式帝号倒用于1418年起义。','https://en.wikipedia.org/wiki/Lam_S%C6%A1n_uprising',[105,20],['黎利、阮廌','王通、柳升等'])
 war('trinh-nguyen','郑阮战争（主要阶段）',1627,1672,[p('郑主与北河军','Trịnh lords|Trinh Lords|Trinh lords',1627,1672)],[p('阮主与广南军','Nguyễn lords|Nguyen Lords|Nguyen lords',1627,1672)],'名义黎朝之下的郑、阮军事集团争夺税赋、效忠及南北控制权。','1672年主要交战后南北维持分治；双方未因此成为独立现代民族国家，后续局势另有变化。','https://en.wikipedia.org/wiki/Tr%E1%BB%8Bnh%E2%80%93Nguy%E1%BB%85n_War',[106.5,18],['郑梉、郑柞','阮福源、阮福澜、阮福濒等'])
 war('tay-son','西山战争与阮氏统一（系列概览）',1771,1802,[p('西山诸军与其王权','Tay Son Dynasty|Tây Sơn dynasty|Tây Sơn Dynasty',1771,1802)],[p('阮主残部与阮福映军','Nguyễn lords|Nguyen lords|Nguyễn dynasty',1771,1802),p('郑主军（与西山关系曾改变）','Trịnh lords|Trinh lords',1774,1775)],'地方负担、阮主政权危机与西山起事，扩大为西山、郑、阮等势力的长期竞争。','阮福映1802年消灭西山政权并建立统一王朝；同侧或异侧关系随战事发生变化，本条不覆盖所有对暹罗、清朝的独立远征。','https://en.wikipedia.org/wiki/T%C3%A2y_S%C6%A1n_wars',[108,14],['阮岳、阮惠、阮光缵','阮福映'])
 war('qing-burma','清缅战争',1765,1769,[p('清军','Qing Dynasty',1765,1769)],[p('贡榜缅甸军','Konbaung Dynasty|Burma',1765,1769)],'掸邦边地归属、边民与土司冲突引发清军多次入缅。','四轮远征未实现清朝征服目标；1769年双方前线停战，正式外交修复在其后逐步进行。','https://en.wikipedia.org/wiki/Sino-Burmese_War',[97,24],['乾隆、明瑞、傅恒','辛骠信、摩诃梯诃都罗等'])
 war('alcacer-quibir','三王之战／阿尔卡塞尔基比尔战役',1578,1578,[pt('葡萄牙与穆罕默德·穆塔瓦基勒支持者',1578,1578)],[p('萨阿德摩洛哥军','Morocco|Saadi Sultanate|Saadi Dynasty',1578,1578)],'葡萄牙塞巴斯蒂昂支持失位苏丹重夺摩洛哥王位，并寻求北非扩张。','葡萄牙远征军惨败，塞巴斯蒂昂与两名摩洛哥王位竞争者均死亡；葡萄牙继承危机随后加深。','https://en.wikipedia.org/wiki/Battle_of_Alc%C3%A1cer_Quibir',[-5.9,35],['塞巴斯蒂昂、穆罕默德·穆塔瓦基勒','阿卜杜勒-马利克、艾哈迈德·曼苏尔'])
 war('mbwila','姆布维拉战役',1665,1665,[p('葡属安哥拉军与当地盟军','Kingdom of Portugal|Portugal Colony - Angola|Portuguese Colonies',1665,1665)],[p('刚果王国军','Kingdom of Kongo',1665,1665)],'刚果王权与葡属安哥拉围绕姆布维拉、地区附属关系与贸易发生冲突。','刚果国王安东尼奥一世战死，王国此后陷入长期内战；本战不表示葡萄牙立即占领整个刚果王国。','https://en.wikipedia.org/wiki/Battle_of_Mbwila',[14.4,-7.3],['安东尼奥一世','路易斯·洛佩斯·德·塞凯拉'])
 war('american-independence','美国独立战争',1775,1783,[p('北美起义殖民地／美国','United States of America|USA|Thirteen Colonies',1775,1783),fr('法国',1778,1783),p('西班牙（与英国交战，非美西正式同盟）','Spain|Spanish Empire',1779,1783)],[p('英国及效忠派','British Empire|Kingdom of Great Britain|United Kingdom',1775,1783)],'北美殖民地代表权、税收与帝国治理矛盾升级，殖民地宣布独立并争取国际支持。','1783年巴黎和约英国承认美国独立；与法国、西班牙及荷兰的相关战争有各自外交条约。','https://www.archives.gov/milestone-documents/treaty-of-paris',[-76,39],['乔治·华盛顿、罗尚博','豪、康沃利斯等'])
 war('brazilian-independence','巴西独立战争',1822,1825,[p('巴西帝国及独立支持者','Empire of Brazil',1822,1825)],[pt('葡萄牙王权与驻军',1822,1825)],'巴西与里斯本议会的政治冲突、王室权力及各省立场分化，引发陆海作战。','1823—1824年主要葡军撤出，1825年里约热内卢条约承认巴西独立；不把条约年全部解释为持续前线战斗。','https://en.wikipedia.org/wiki/Brazilian_War_of_Independence',[-38.5,-13],['佩德罗一世、托马斯·科克伦','葡萄牙驻巴西军政官'])
 db['wars']=list(rows.values());write('public/data/historical-wars-supplements.json',db)
 from merge_historical_wars import main as merge
 merge()
 # Existing COW wars retain their observed date thresholds; enrich, don't duplicate.
 detail=read('public/data/war-details.json');dd={w['id']:w for w in detail['wars']};enriched=[]
 for ident,title,cause,result,url,loc in [
  ('cow-extra-310','第一次英缅战争','英属印度与贡榜在阿萨姆、曼尼普尔及阿拉干边疆的扩张和冲突。','1826年杨达波条约使缅甸割让阿拉干、丹那沙林等并承担赔款；COW序列含1823年边境前奏，英国正式宣战在1824年。','https://www.nam.ac.uk/explore/timeline-burma-army',[96,19]),
  ('cow-extra-339','第二次英缅战争','仰光商贸纠纷及英国对下缅甸的扩张。','英国占领并吞并勃固，下缅甸进一步落入英国统治。','https://www.nam.ac.uk/explore/timeline-burma-army',[96,17]),
  ('cow-extra-387','第三次英缅战争及早期抵抗','商业争端与帝国竞争推动英国进攻贡榜王朝。','1885年王室被废黜，1886年宣布吞并上缅甸；COW条目至1889年包括早期抵抗，王朝覆灭并不等于抵抗立刻终止。','https://www.nam.ac.uk/explore/timeline-burma-army',[96,22]),
  ('cow-extra-367','英阿散蒂战争（1873—1874）','英国在黄金海岸的扩张与阿散蒂对沿海及贸易影响的竞争。','英军进入库马西，条约与赔款削弱阿散蒂势力；没有在1874年即废除整个王国。','https://en.wikipedia.org/wiki/Anglo-Ashanti_wars',[-1.6,6.7]),
  ('cow-extra-417','金凳战争','英国殖民官对金凳及阿散蒂政治主权的要求激起抵抗。','英军击败主要抵抗，1902年将阿散蒂并入殖民统治；未取得金凳不影响其继续作为阿散蒂认同象征。','https://en.wikipedia.org/wiki/War_of_the_Golden_Stool',[-1.6,6.7]),
  ('cow-extra-362','英国远征埃塞俄比亚（1867—1868）','特沃德罗斯二世扣押英国外交与传教人员，引发远征。','英军攻入马格达拉，特沃德罗斯自尽，人质获释；英军随后撤离，没有吞并埃塞俄比亚。','https://www.nam.ac.uk/explore/abyssinia', [39.3,11.2]),
  ('cow-extra-407','意埃战争与阿杜瓦战役（1895—1896）','《乌查利条约》语言版本和宗主权争执，加上意大利在非洲之角扩张。','孟尼利克二世军队在阿杜瓦击败意军，1896年和约承认埃塞俄比亚独立。','https://en.wikipedia.org/wiki/First_Italo-Ethiopian_War',[38.9,14.2]),
  ('cow-inter-64','太平洋战争（硝石战争）','阿塔卡马硝石资源、税收、边界及秘鲁—玻利维亚关系引发与智利的战争。','智利取得重要沿海领土；1883年安孔条约、1884年停战及更晚条约分阶段处理结局，玻利维亚丧失海岸控制。','https://en.wikipedia.org/wiki/War_of_the_Pacific',[-70,-20]),
  ('cow-intra-617','智利内战（1891）','巴尔马塞达总统与国会围绕预算及宪政权限的冲突。','国会派军队获胜，总统败亡，智利进入通常所称的议会共和时期。','https://en.wikipedia.org/wiki/Chilean_Civil_War_of_1891',[-71,-33]),
  ('cow-extra-315','巴西—拉普拉塔战争（西斯普拉丁战争）','乌拉圭东岸归属、地方独立运动与巴西、拉普拉塔联合省的地区竞争。','1828年调停安排促成乌拉圭独立；COW本条主要交战范围1826—1828年，不替代1825年开始的广义战争叙事。','https://en.wikipedia.org/wiki/Cisplatine_War',[-56,-33])]:
  dd[ident]={**dd.get(ident,{}),**dict(id=ident,title=title,cause=cause,result=result,sources=[url],location=loc,reviewedHistorical=True,supplement=TAG)};enriched.append(ident)
 detail['wars']=list(dd.values());write('public/data/war-details.json',detail)
 write('public/data/world-wars-review.json',dict(reviewedAt='2026-11-02',tag=TAG,added=added,enriched=enriched,limitations=['系列概览并非逐次战役完备目录。','内战的阵营与名义王权可能交错，阵营说明优先于简单国家对国家理解。','保留COW统计门槛与条约年代差异，不自动外推占领区和精确兵力。']))
 print('New historical wars',len(added),'existing wars enriched',len(enriched))
if __name__=='__main__':main()
