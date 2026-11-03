"""Review missing ownership independently of modern national boundaries.

Historical reference outlines, named capital cores and clearly marked regional
collections fill unassigned land only. Existing owners are never expanded by
nearest-neighbour assignment. Modern geography is only a clipping mask.
"""
from collections import defaultdict
from territory_repair_stage import Stage,ROOT,read,write,clean
from shapely import union_all
from shapely.geometry import shape,box,Point

TAG='regional-coverage-2026-11-01'
BASE='https://github.com/aourednik/historical-basemaps'
INDIA='https://www.parliament.uk/about/living-heritage/evolutionofparliament/legislativescrutiny/parliament-and-empire/parliament-and-the-american-colonies-before-1765/east-india-company-and-raj-1785-1858/'
INDIAMAP='https://searcharchives.bl.uk/catalog/040-004363148'
CAUCASUS='https://www.britannica.com/event/Caucasian-War'
OMAN='https://www.omaninfo.om/ar/pages/161/show/572'
SAUDI='https://whc.unesco.org/document/168964'
UNOMIG='https://peacekeeping.un.org/sites/default/files/past/unomig/background.html'

def main():
 stage=Stage(TAG,range(14,21));admin=read('.local/ne_10m_admin_1_states_provinces.geojson')['features'];countries=read('.local/presentation/admin0.geojson')['features']
 def country(n):return clean(union_all([shape(f['geometry'])for f in countries if f['properties']['NAME_EN']==n]))
 def provinces(c,names):return clean(union_all([shape(f['geometry'])for f in admin if f['properties']['admin']==c and f['properties']['name']in names]))
 india=country('India');pakistan=country('Pakistan');southasia=clean(union_all([india,pakistan,country('Bangladesh')]))
 notes={};definitions={}
 def repair(n,label,q,g,lo,hi,source,note,regional=False,**props):
  if g.is_empty:return
  previous=definitions.get(n,{})
  definitions[n]={'label':label,'qid':q,'from':min(lo,previous.get('from',lo)),'to':max(hi,previous.get('to',hi)),'regional':regional,'source':source,'note':note,**props};notes[n]=note
  for a,b in stage.periods(g,lo,hi):stage.repair(g,a,b,[(n,label,q,g,source,note,{'regionalCollection':regional,'representationKind':'regional-polities'if regional else'polity','representationNote':note,'inferredBoundary':True,**props})])
 # Recover period-specific named reference regions, not an entire modern India.
 refs={}
 for m in read('public/data/manifest.json'):
  if 1400<=m['year']<=1900:
   groups=defaultdict(list)
   for f in read('public/data/'+m['filename'])['features']:
    if f['properties'].get('NAME'):groups[f['properties']['NAME']].append(clean(shape(f['geometry'])))
   refs[m['year']]={n:clean(union_all(gs))for n,gs in groups.items()}
 def ref(y,n):return refs.get(y,{}).get(n,Point(0,0).buffer(0))
 # Delhi's successors, the Deccan sultanates and surviving southern courts.
 for raw,n,label,q,lo,hi in [
  ('Ahmadnagar','Ahmadnagar Sultanate','艾哈迈德讷格尔苏丹国','Q400998',1490,1636),
  ('Bijapur','Bijapur Sultanate','比贾布尔苏丹国','Q83821',1490,1686),
  ('Golkonda','Golconda Sultanate','戈尔康达苏丹国','Q1148042',1518,1687),
  ('Bidar','Bidar Sultanate','比达尔苏丹国','local:bidar-sultanate',1492,1619),
 ]:
  for y,z in [(1500,1600),(1600,1700)]:
   a,b=max(y,lo),min(z-1,hi)
   if a<=b:repair(n,label,q,ref(y,raw).intersection(southasia),a,b,BASE,'依据对应世纪历史参考图中的具名苏丹国轮廓补遗漏；仅补无归属地，不把现代邦界当作其完整国界。')
 repair('Vijayanagara Empire','毗奢耶那伽罗王国','Q167639',ref(1600,'Vijayanagara').intersection(india),1572,1646,BASE,'1600年参考图中的南印度王国地域；塔利科塔之后仍有继承王廷与地方领主，此轮廓并不表示旧首都继续完整控制全境。')
 repair('Vijayanagara Empire','毗奢耶那伽罗王国','Q167639',india.intersection(Point(80.27,13.08).buffer(.16)),1529,1638,'https://www.britannica.com/place/Chennai/History','马德拉斯设立公司据点前，海岸纳亚克领主与毗奢耶那伽罗／钱德拉吉里王廷的关系另作概化；与邻近圣多美的葡萄牙据点不等同。')
 gujarat=provinces('India',['Gujarat']);mp=provinces('India',['Madhya Pradesh']);chhattisgarh=provinces('India',['Chhattisgarh']);tamil=provinces('India',['Tamil Nadu'])
 repair('Gujarat Sultanate','古吉拉特苏丹国','local:gujarat-sultanate',gujarat.intersection(Point(72.58,23.02).buffer(2.4)),1407,1572,'https://en.wikipedia.org/wiki/Gujarat_Sultanate','以艾哈迈达巴德和古吉拉特腹地为有据核心概化补绘，不声称囊括全盛范围或所有半岛诸侯。')
 repair('Malwa Sultanate','马尔瓦苏丹国','local:malwa-sultanate',mp.intersection(box(73,21,78.6,25.3)),1401,1561,'https://en.wikipedia.org/wiki/Malwa_Sultanate','以马尔瓦高原及曼杜周边补绘；使用地理区作概化定位，1562年莫卧儿征服后不继续保留。')
 repair('Gondwana Kingdoms','贡德瓦纳诸王国','local:gondwana-kingdoms',union_all([mp.intersection(box(78.3,20,83,25)),chhattisgarh]),1400,1853,'https://en.wikipedia.org/wiki/Gondwana_(India)','加尔哈曼德拉、德奥加尔、钱达、巴斯塔尔等不同王国与社群的地域集合；各地被征服及隶属关系不同，仅补未细分的空缺，不虚构共同国王。',True)
 repair('Madurai Nayak Kingdom','马杜赖王国','local:madurai-nayaks',tamil.intersection(box(76,8,80,11.3)),1529,1735,'https://en.wikipedia.org/wiki/Madurai_Nayak_dynasty','以马杜赖及南泰米尔地区概化，纳亚克在毗奢耶那伽罗框架下起家，后逐渐自主；不能据现代邦界确定精确历史分界。')
 repair('Thanjavur Nayak Kingdom','坦贾武尔王国','local:thanjavur-nayaks',tamil.intersection(box(78.5,10,80.7,12)),1532,1673,'https://en.wikipedia.org/wiki/Thanjavur_Nayak_kingdom','以高韦里河三角洲的纳亚克王国为核心；仅补原图空缺，内部边缘为地理推断。')
 repair('Thanjavur Maratha Kingdom','坦贾武尔王国','local:thanjavur-maratha',tamil.intersection(Point(79.14,10.79).buffer(.65)),1674,1854,'https://en.wikipedia.org/wiki/Thanjavur_Maratha_kingdom','马拉塔博恩斯勒王室继承后的坦贾武尔核心，19世纪的英国保护与实际行政权须分期理解；不延长已灭亡的纳亚克王朝。')
 kerala=provinces('India',['Kerala']);maharashtra=provinces('India',['Maharashtra']);telangana=provinces('India',['Telangana'])
 repair('Hyderabad State','海得拉巴','Q1240096',telangana,1724,1782,'https://en.wikipedia.org/wiki/Hyderabad_State','阿萨夫贾政权的特伦甘纳核心概化，不把1783年以后的完整轮廓向前复制；已存在的地方政权和马拉塔控制区保留。')
 repair('Maratha Confederacy States','马拉塔诸邦','local:maratha-confederacy-states',maharashtra,1730,1782,'https://en.wikipedia.org/wiki/Maratha_Confederacy','以马拉塔诸中心所在的马哈拉施特拉地理核心补遗漏，不复制后来延伸到北印度的极盛疆域；各王室、佩什瓦和地方家族并非一个共同直接行政机关。',True)
 repair('Kingdom of Cochin','科钦王国','local:kingdom-of-cochin',kerala.intersection(Point(76.27,9.93).buffer(.55)),1400,1782,'https://en.wikipedia.org/wiki/Kingdom_of_Cochin','只补科钦及附近海岸核心；港口与葡萄牙、荷兰的联系及王室领地不是同一层次的直接管辖。')
 repair('Kingdom of Venad','韦纳德王国','local:venad-kingdom',kerala.intersection(box(75,8,78,9.6)),1400,1728,'https://en.wikipedia.org/wiki/Venad','特拉凡哥尔形成前的韦纳德核心，不能提前把1729年后的王国名称用于全部更早时期。')
 repair('Kingdom of Travancore','特拉凡哥尔王国','local:travancore',kerala.intersection(box(75,8,78,10.1)),1729,1782,'https://en.wikipedia.org/wiki/Kingdom_of_Travancore','马尔坦达瓦尔马时期以后南部核心的概化补绘；并未将整个现代喀拉拉邦当作完整王国。')
 repair('Rajput Principalities','拉杰普特诸邦','local:rajput-principalities',provinces('India',['Rajasthan']),1400,1817,'https://en.wikipedia.org/wiki/Rajputana','诸王国、领主及其联盟集合；莫卧儿隶属、婚盟和马拉塔征贡经历变化，不等同统一民族国家。',True)
 assam=provinces('India',['Assam']);northeast=provinces('India',['Arunachal Pradesh','Nagaland','Meghalaya','Mizoram'])
 repair('Ahom Kingdom','阿洪王国','local:ahom-kingdom',assam.intersection(box(91.5,26,97,29)),1400,1825,'https://en.wikipedia.org/wiki/Ahom_kingdom','以布拉马普特拉河谷上游为核心概化；1826年条约后进入新的殖民时期，不把邻近山地全部划归阿洪。')
 repair('Kingdom of Manipur','曼尼普尔王国','local:manipur-kingdom',provinces('India',['Manipur']),1400,1890,'https://en.wikipedia.org/wiki/Kingdom_of_Manipur','以曼尼普尔谷地及周边作保守地域示意，边远山地与谷地王权的关系并不等同持续直接统治。')
 repair('Tripura Kingdom','特里普拉王国','local:tripura-kingdom',provinces('India',['Tripura']),1400,1948,'https://en.wikipedia.org/wiki/Twipra_Kingdom','只补特里普拉已知核心，历史王国曾及更广地域；不宣称现代边界就是当时完整国界。')
 repair('Northeast Indian Hill Communities','东北印度山地诸社群','local:northeast-indian-hill-communities',northeast,1400,1825,'https://en.wikipedia.org/wiki/History_of_Northeast_India','不同山地政治与村社网络的地域集合；与阿洪、曼尼普尔及其他王权的联系逐地变化，未虚构共同王名。',True)
 # Specific 18th/19th-century courts from named historical reference polygons.
 for raw,n,label,q,lo,hi in [
  ('Carnatic','Carnatic Sultanate','卡纳蒂克纳瓦布领','Q3277580',1740,1800),
  ('Cochin','Kingdom of Cochin','科钦王国','local:kingdom-of-cochin',1783,1948),
  ('Travancore','Kingdom of Travancore','特拉凡哥尔王国','local:travancore',1783,1948),
  ('Golconda','Hyderabad State','海得拉巴','Q1240096',1783,1799),
  ("Nizam's Dominions",'Hyderabad State','海得拉巴','Q1240096',1800,1814),
  ('Oudh','Nawab of Awadh','阿瓦德','Q2614237',1783,1855),
  ('Mahratta states','Maratha Confederacy States','马拉塔诸邦','local:maratha-confederacy-states',1783,1817),
 ]:
  y=1800 if raw=="Nizam's Dominions"else 1783
  repair(n,label,q,ref(y,raw).intersection(southasia),lo,hi,BASE,f'使用{y}年历史参考图中该地区的具名轮廓补遗漏；只用于该王权或邦国适用阶段，不将后来的吞并状态提前。',n=='Maratha Confederacy States')
 # The 1857 source loses a broad central/northern block, not actual political
 # society. Preserve surviving princes, distinguish a rebellion activity core.
 mainland=india.difference(provinces('India',['Jammu and Kashmir','Ladakh','Arunachal Pradesh']))
 def british(g,lo,hi):repair('British India','英属印度','local:company-india',g,lo,hi,INDIAMAP,'1857年地图与东印度公司行政史支持的英属及其保护体系。仅补空缺，已画出的土邦继续单列；1857年内各地控制多次变化，此处不表示全年平静或全部直接统治。',sovereignName='United Kingdom',sovereignQid='Q145',territoryType='colony')
 up=provinces('India',['Uttar Pradesh'])
 repair('Awadh Rebel Government','阿瓦德起义政府','local:awadh-rebel-government',up.intersection(box(80,25.5,83,28.5)),1857,1857,'https://www.nam.ac.uk/explore/decisive-events-indian-mutiny','以勒克瑙及阿瓦德抵抗中心为年度活动范围概化。贝古姆·哈兹拉特·玛哈尔与比尔吉斯·卡德尔领导的政府另列；不是精确到日期的连续战线。',controller='Awadh Rebel Government',controllerQid='local:awadh-rebel-government',sovereignName='British India',controlArea=True,controlId='awadh-uprising-1857')
 british(mainland,1856,1858)
 british(india.intersection(Point(80.27,13.08).buffer(.2)),1639,1858)
 # Known coastline omissions: Bombay was Portuguese, then British, then Indian.
 bombay=india.intersection(Point(72.88,19.08).buffer(.36))
 repair('Portuguese India','葡属印度','Q824489',bombay,1534,1660,'https://www.britannica.com/place/Mumbai/History','孟买核心海岸的归属遗漏；1534年葡萄牙取得、1661年王室婚约转交英国。不是把整个印度西岸划为葡属。',sovereignName='Portugal',sovereignQid='Q45',territoryType='colony')
 british(bombay,1661,1858)
 repair('British Raj','英属印度','Q129286',bombay,1859,1946,INDIA,'孟买及附近海岸几何遗漏；1858年以后属王室统治的英属印度。',sovereignName='United Kingdom',sovereignQid='Q145',territoryType='colony')
 repair('Republic of India','印度','Q668',bombay,1947,2024,'https://www.britannica.com/place/Mumbai/History','补孟买海岸遗漏；1947—1950年为自治领时期，1950年共和国成立，名称与制度在资料中按年代区分。')
 print('India regional and transition gaps prepared',flush=True)
 # North Caucasus cores and communities before incorporation in the empire.
 russia=country('Russia');north=russia.intersection(box(37.5,41,49.5,45.2));georgia=country('Georgia');abkhazia=provinces('Georgia',['Abkhazia'])
 if abkhazia.is_empty:abkhazia=georgia.intersection(box(40,42.4,42.2,43.7))
 circassia=north.intersection(box(37.5,42.5,42.4,45.2));kabarda=north.intersection(box(42.3,43,44.2,44.3));dagestan=provinces('Russia',['Dagestan']);chechnya=provinces('Russia',['Chechnya'])
 repair('Circassian Principalities','切尔克斯诸部与公国','local:circassian-principalities',circassia,1400,1863,CAUCASUS,'阿迪格诸部、公国与地方议事组织的地域集合；并不存在一个覆盖所有切尔克斯人的共同王位，征服战线逐年变化。',True)
 repair('Kabardian Principalities','卡巴尔达诸公国','local:kabardian-principalities',kabarda,1400,1821,CAUCASUS,'卡巴尔达诸公国的概化地理核心；与俄国、克里米亚及奥斯曼的关系不等于领土始终由同一方直接管理。',True)
 repair('Shamkhalate of Tarki','塔尔基沙姆哈勒国','local:tarki-shamkhalate',north.intersection(Point(47.45,42.9).buffer(.65)),1500,1843,'https://en.wikipedia.org/wiki/Shamkhalate_of_Tarki','塔尔基及滨海达吉斯坦的保守核心概化；不把整个达吉斯坦或所有自由山社归到沙姆哈勒。')
 repair('Dagestani Khanates and Free Societies','达吉斯坦诸汗国与山社','local:dagestani-khanates',dagestan,1400,1828,'https://en.wikipedia.org/wiki/History_of_Dagestan','阿瓦尔、库梅克、达尔金等不同汗国、自由社群及其联盟的地域集合；尚未逐邦数字化的空缺不视为无政治组织之地。',True)
 repair('Principality of Abkhazia','阿布哈兹公国','Q1760473',abkhazia,1491,1863,'https://en.wikipedia.org/wiki/Principality_of_Abkhazia','按公国核心补绘，1810年起俄国保护关系与1864年取消公国另分；不以今天的国际地位倒推早期疆界。')
 repair('Caucasian Imamate','高加索伊玛目国','Q2088141',union_all([chechnya,dagestan.intersection(box(45,41,47.2,43.3))]),1829,1858,CAUCASUS,'伊玛目国在车臣、达吉斯坦山地的活动核心示意；不是假设其在整个时段恒定控制每个山谷。1859年沙米尔投降后不沿用。')
 repair('Russian Empire','俄罗斯帝国','Q34266',north.intersection(Point(47.5,42.98).buffer(.15)),1844,1863,'https://en.wikipedia.org/wiki/Makhachkala','彼得罗夫斯科耶要塞与港口（今马哈奇卡拉）1844年起的俄军据点核心，只补海岸遗漏，不据此把1844年整个达吉斯坦都视为已征服。')
 repair('North Caucasian Mountain Communities','北高加索山地诸社群','local:north-caucasian-mountain-communities',north,1400,1863,CAUCASUS,'已明确分列的公国、汗国、伊玛目国及俄军据点之外的山地社群背景；不把奥塞梯、瓦伊纳赫等不同政治与社会网络假定为一个国家或共同君主。',True)
 repair('Russian Empire','俄罗斯帝国','Q34266',north,1864,1916,CAUCASUS,'高加索战争主要阶段结束后的北高加索陆地遗漏，含被低精度海岸线漏掉的陆地；保留已有相邻政权，不把此范围用于征服之前。')
 repair('North Caucasian Governments','北高加索山地诸政权','local:north-caucasian-governments',north,1917,1920,'https://en.wikipedia.org/wiki/Mountainous_Republic_of_the_Northern_Caucasus','革命、山地共和国、白军及红军竞争时期的未逐段核定地区集合。不是一个四年不变的统一政权，不据此宣称已复原每条内战控制线。',True)
 repair('Union of Soviet Socialist Republics','苏联','Q15180',union_all([north,georgia,country('Armenia'),country('Azerbaijan')]),1922,1990,'https://www.britannica.com/place/Caucasus/History','苏联时期的细海岸及山地多边形遗漏；补陆地底图与历史轮廓精度差，不改变加盟共和国之间的内部界线。')
 repair('Russian Federation','俄罗斯','Q159',north,1992,2024,'https://www.britannica.com/place/Caucasus/History','仅补未覆盖的北高加索陆地边缘，已收录的车臣等控制记录保持独立；不据该补绘推断地区从未存在武装冲突。')
 for n,label,q,mask in [('Georgia','格鲁吉亚','Q230',georgia.difference(abkhazia)),('Armenia','亚美尼亚','Q399',country('Armenia')),('Azerbaijan','阿塞拜疆','Q227',country('Azerbaijan'))]:repair(n,label,q,mask,1992,2024,'https://www.britannica.com/place/Caucasus/History','只补本国已有记录旁的未覆盖陆地，争议与控制状态另外标注；不据此取消既有地方控制实体。')
 repair('Abkhaz De Facto Administration','阿布哈兹','local:abkhaz-administration',abkhazia,1994,2024,UNOMIG,'1993年冲突后的阿布哈兹实际管理区概化；国际承认的格鲁吉亚主权与实际控制分开表示。科多里河谷2008年前后另有控制差异，不能据这一概化表示每年完整控制同一轮廓。',controller='Abkhaz De Facto Administration',controllerQid='local:abkhaz-administration',sovereignName='Georgia',sovereignQid='Q230',territoryType='de-facto-administration')
 print('Caucasus regional gaps prepared',flush=True)
 # Arabian states and oasis/tribal collections, rather than an early Saudi map.
 saudi=country('Saudi Arabia');yemen=country('Yemen');oman=country('Oman');najd=saudi.intersection(box(40,20.5,49,29.5));ahsa=saudi.intersection(box(48.2,24,52,28.5));hail=saudi.intersection(Point(41.69,27.52).buffer(1.6))
 repair('Nabhani Oman','阿曼纳卜汉王国','local:nabhani-oman',oman.intersection(box(54,20,60,25)),1400,1623,OMAN,'内陆纳卜汉王权、伊玛目与部族关系多次变化；仅补阿曼北部缺失区域，葡萄牙沿海据点保持原图单列。')
 repair('Yaruba Imamate','阿曼伊玛目国','local:yaruba-oman',oman.intersection(box(54,20,60,25)),1624,1748,OMAN,'1624年纳西尔·本·穆尔希德建立亚鲁卜伊玛目政权，内陆、沿海和晚期内战须分开理解；不是现代阿曼国界的反向复制。')
 repair('Omani Al Busaidi State','阿曼','local:albusaidi-oman',oman.intersection(box(54,20,60,25)),1749,1899,OMAN,'布赛义德家族兴起后的北阿曼地域；沿海苏丹与内陆伊玛目、部族的实际权力并不始终一致。')
 repair('Jabrid Emirate','贾布里德酋长国','local:jabrid-emirate',ahsa,1400,1520,'https://en.wikipedia.org/wiki/Jabrids','哈萨绿洲及东阿拉伯的概化核心；不自动包括所有阿拉伯沙漠或整个波斯湾。')
 repair('Bani Khalid Emirate','巴尼哈立德酋长国','local:bani-khalid',ahsa,1670,1792,'https://en.wikipedia.org/wiki/Bani_Khalid_Emirate','哈萨与盖提夫地区巴尼哈立德政权核心概化；1793年被沙特势力征服后的时期不继续沿用。')
 riyadh=saudi.intersection(Point(46.72,24.69).buffer(.13))
 repair('Riyadh Emirate of Dahham','利雅得酋长国','local:riyadh-dahham',riyadh,1737,1772,'https://en.wikipedia.org/wiki/Dahham_ibn_Dawwas','利雅得核心：1737—1740年胡迈伊斯摄政，1740年起达哈姆摄政、1745年起独立统治，1773年第一沙特国家取得利雅得前不提前并入德拉伊耶。')
 repair('Emirate of Diriyah','德拉伊耶酋长国','Q146871',saudi.intersection(Point(46.57,24.74).buffer(.12)),1744,1772,SAUDI,'以德拉伊耶附近为早期核心，不把1773年才取得的利雅得或后来最大疆域提前用于1744年。')
 repair('Emirate of Diriyah','德拉伊耶酋长国','Q146871',najd.intersection(box(44,22,48,26)),1773,1791,SAUDI,'取得利雅得以后的内志南部核心示意，未将哈伊勒等后来关联地区一并向前复制。')
 repair('Emirate of Diriyah','德拉伊耶酋长国','Q146871',najd,1792,1817,SAUDI,'第一沙特国家扩张阶段的内志核心概化；沙漠牧地、盟属联系与持续直接控制并不等同，汉志征服另按有效分期。')
 repair('Emirate of Nejd','内志酋长国','Q146862',najd.difference(hail),1824,1890,SAUDI,'第二沙特国家的内志核心示意；内部王位争夺、短期埃及军行动及实际控制范围存在变化，1891年失败后不继续作为统一控制者。')
 repair('Emirate of Jabal Shammar','杰贝勒舍迈尔酋长国','local:jabal-shammar',hail,1836,1920,'https://en.wikipedia.org/wiki/Emirate_of_Jabal_Shammar','以哈伊勒为中心的拉希德政权核心。晚19世纪扩张与1921年终结另按时期，不把哈伊勒王室套到所有阿拉伯部落。')
 repair('Najdi Oasis Principalities','内志绿洲诸酋邦与部族','local:najdi-oasis-principalities',najd,1400,1743,'https://www.britannica.com/place/Arabia/History','内志绿洲、地方酋邦及部族联系的地理集合，范围不等于连续的统一国家控制区；不虚构一个共同国王。',True)
 repair('Arabian Interior Tribal Communities','阿拉伯半岛内陆诸部族','local:arabian-interior-communities',saudi,1400,1931,'https://www.britannica.com/place/Arabia/History','只补已画政权之外尚未逐段核定的内陆背景。包括稀疏的绿洲、牧地和交通联系，不表示沙漠每处有人定居、拥有统一边界或存在共同政府。',True)
 westyemen=yemen.intersection(box(42,14,45.5,19))
 repair('Qasimid Imamate of Yemen','也门卡西姆伊玛目国','local:qasimid-yemen',westyemen,1636,1871,'https://en.wikipedia.org/wiki/Qasimid_State','宰德派卡西姆伊玛目政权的也门高地核心；不与苏格兰同名家族实体关联，也不把哈德拉毛各苏丹国并入统一王权。')
 repair('Qasimid Imamate of Yemen','也门卡西姆伊玛目国','local:qasimid-yemen',yemen.intersection(Point(45.03,12.79).buffer(.3)),1636,1727,'https://en.wikipedia.org/wiki/Aden','亚丁港在拉赫季苏丹国兴起以前与也门卡西姆政权的联系单列，不提前使用1839年以后的英国殖民身份。')
 repair('Lahej Sultanate','拉赫季苏丹国','local:lahej-sultanate',yemen.intersection(union_all([Point(45.03,12.79).buffer(.32),Point(44.88,13.06).buffer(.3)])),1728,1838,'https://en.wikipedia.org/wiki/Lahej_Sultanate','1839年英国取得亚丁港以前的拉赫季—亚丁核心概化；不能把英国控制港口与整个苏丹国等同。')
 repair('Kathiri Sultanate','卡西里苏丹国','local:kathiri-sultanate',yemen.intersection(Point(48.79,15.94).buffer(.8)),1488,1966,'https://en.wikipedia.org/wiki/Kathiri','赛永及哈德拉毛内陆的保守核心，苏丹国、部族与英国保护体系随时期变化。')
 repair('Quaiti Sultanate','奎艾蒂苏丹国','local:quaiti-sultanate',yemen.intersection(Point(49.12,14.54).buffer(.65)),1866,1966,'https://en.wikipedia.org/wiki/Qu%27aiti','穆卡拉及沿海政权核心；只补原图遗漏，不把整个南阿拉伯保护体系归给一个苏丹。')
 repair('Hadrami Sultanates and Tribal Societies','哈德拉毛诸苏丹国与部族','local:hadrami-sultanates',yemen.intersection(box(45.5,13,54,20)),1400,1938,'https://en.wikipedia.org/wiki/Hadhramaut','哈德拉毛各地方苏丹国、部落与绿洲政治网络集合；不设一个共同苏丹，也不等同现代也门的中央统治。',True)
 repair('Colony of Aden','亚丁','local:colony-of-aden',yemen.intersection(Point(45.03,12.79).buffer(.2)),1839,1966,'https://www.britannica.com/place/Aden','1839年英国占领亚丁后港口核心的海岸几何遗漏；1937年前后的行政体制变化不等于主权空缺。',sovereignName='United Kingdom',sovereignQid='Q145',territoryType='colony')
 print('Arabian regional gaps prepared',flush=True)
 stage.finish('regional-coverage-review.json');write('public/data/regional-coverage-definitions.json',definitions)
 print('Regional definitions',len(definitions),flush=True)
if __name__=='__main__':main()
