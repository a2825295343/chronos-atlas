"""Explicit transitional repairs plus bounded, corroborated historical basemaps.
No blank space is automatically assigned to a modern neighbouring country.
"""
from collections import defaultdict
from territory_repair_stage import Stage,ROOT,read,write,clean
from shapely import union_all
from shapely.geometry import shape,box,Point

TAG='expanded-history-gaps-2026-10-31'
BASE='https://github.com/aourednik/historical-basemaps'
CLIO='https://github.com/Seshat-Global-History-Databank/cliopatria'
XINJIANG='https://islamansiklopedisi.org.tr/yakub-beg'
LIBYA='https://2001-2009.state.gov/p/nea/ci/ly/109175.htm'
ETHIOPIA='https://collection.nam.ac.uk/detail.php?acc=2005-09-60--15'
OETA='https://www.gwpda.org/1918p/kncr.htm'
IRAQ='https://searcharchives.bl.uk/catalog/040-000545804'

def main():
 stage=Stage(TAG,range(5,20));admin=read('.local/ne_10m_admin_1_states_provinces.geojson')['features']
 def mask(country):return clean(union_all([shape(f['geometry'])for f in admin if f['properties']['admin']==country]))
 def item(n,label,q,g,source,note,**props):return(n,label,q,g,source,note,props)
 # First repair the specifically reported modern transitions.
 xinjiang=clean(union_all([shape(f['geometry'])for f in admin if f['properties']['admin']=='China'and f['properties']['iso_3166_2']=='CN-XJ']))
 ili=xinjiang.intersection(box(80,42.4,83.9,44.8));kashgar=xinjiang.intersection(box(73,34,79.5,41.8));hotan=xinjiang.intersection(box(78,34,85,39.2));kucha=xinjiang.intersection(box(78,39.2,86,42.7))
 tarim=clean(xinjiang.intersection(box(73,34,91.8,44.6)).difference(ili));hami=clean(xinjiang.intersection(box(91.8,39,97,45.3)));altay=xinjiang.intersection(box(80,46.7,98,51))
 for a,b in stage.periods(xinjiang,1864,1882,[1865,1866,1867,1870,1871,1876,1877,1882]):
  rows=[]
  note='清末新疆变局的地理概化：并非整片无主地。阿古柏政权、伊犁地方政权／俄军占领及清军据点分列。内部界线仅辅助定位，未数字化逐月战线或把实际控制等同合法主权。'
  if a>=1877:
   rows.append(item('Qing Dynasty','清朝','Q8733',xinjiang.difference(ili)if a<1882 else xinjiang,XINJIANG,note+'1877年按清军收复南疆后的年末状态，伊犁另列。'))
  else:
   rows.append(item('Qing Dynasty','清朝','Q8733',union_all([hami,altay]),XINJIANG,note+'哈密及北部保留地区按既有清朝联系与军事据点概化，不把所有边民划作叛军。'))
   if a>=1865:
    territory=tarim if 1870<=a<=1875 else tarim.intersection(box(73,33,92,42.5))if a==1876 else union_all([kashgar,hotan,kucha])if a>=1867 else union_all([kashgar,hotan])if a>=1866 else kashgar
    rows.append(item('Yettishar','哲德沙尔（阿古柏政权）','local:yettishar',territory,XINJIANG,note+'1865年起自喀什扩张；不提前把1870年的扩张范围用于1865年，1876年清军收复北疆后收缩。'))
   rows.append(item('Dzungarian and Tarim Local Forces','新疆地方诸政权与武装','local:xinjiang-local-polities',xinjiang.difference(union_all([ili,hami,altay])),XINJIANG,note+'此为尚未逐邦细分的地方武装与政权集合，不虚构一个共同国王。',regionalCollection=True))
  if a<1882:
   if a>=1871:rows.append(item('Control area - russian-ili','伊犁（俄军占领）','local:russian-ili',ili,XINJIANG,note+'1871年俄军占领伊犁；1881年条约及随后交还另按阶段处理，本图1882年起回归清朝。',controlArea=True,controller='Russian Empire',controllerQid='Q34266',sovereignName='Qing Dynasty',territoryType='occupation',controlId='russian-ili'))
   else:rows.append(item('Ili Sultanate','伊犁地方苏丹政权','local:ili-sultanate',ili,XINJIANG,note+'1864—1870年伊犁地方政权；1871年俄军占领后不继续显示。'))
  stage.repair(xinjiang,a,b,rows)
 print('Xinjiang transitions prepared',flush=True)
 libya=mask('Libya');subs={f['properties']['iso_3166_2']:shape(f['geometry'])for f in admin if f['properties']['admin']=='Libya'}
 cyrenaica=union_all([subs['LY-'+s]for s in ['KF','BU','AJ','QB','JA','MJ','BA']]);fezzan=union_all([subs['LY-'+s]for s in ['MQ','WS','GT','SB','WD']]);tripoli=libya.difference(union_all([cyrenaica,fezzan]))
 for a,b in stage.periods(libya,1943,1944):
  rows=[]
  for n,label,q,g,parent,parentq in [('British Tripolitania','的黎波里塔尼亚（英国管理）','local:british-tripolitania',tripoli,'United Kingdom','Q145'),('British Cyrenaica','昔兰尼加（英国管理）','local:british-cyrenaica',cyrenaica,'United Kingdom','Q145'),('French Fezzan','费赞（法国管理）','local:french-fezzan',fezzan,'France','Q142')]:
   rows.append(item(n,label,q,g,LIBYA,'1943年初轴心军退出利比亚后，英国管理的黎波里塔尼亚和昔兰尼加，法国管理费赞。按年末管理状态补绘，省内界为地理概化；不是提前建立独立利比亚。',sovereignName=parent,sovereignQid=parentq,territoryType='administration'))
  stage.repair(libya,a,b,rows,remove=['Italian Africa','Kingdom of Italy','Nazi Germany'])
 ethiopia=mask('Ethiopia');eritrea=mask('Eritrea');ogaden=ethiopia.intersection(box(42.5,3,49,10.5))
 for a,b in stage.periods(union_all([ethiopia,eritrea]),1941,1944):
  rows=[item('Ethiopia','埃塞俄比亚','Q115',ethiopia.difference(ogaden),ETHIOPIA,'1941年皇帝返回、埃塞俄比亚和英联邦部队击败意大利占领军后的年度概览；意大利在贡德尔等地的抵抗延续到年内，未表示1941年全年已全部解放。',yearConvention='1941年以复国及主要战役结束后的年末状态表示。'),item('British Administration of Eritrea','厄立特里亚（英国管理）','local:british-eritrea',eritrea,ETHIOPIA,'1941年意军在厄立特里亚被击败后的英国军事管理区；并非当时已独立或已经并入埃塞俄比亚。',sovereignName='United Kingdom',sovereignQid='Q145',territoryType='administration'),item('Control area - british-ogaden','欧加登（英国军事管理）','local:british-ogaden',ogaden,ETHIOPIA,'埃塞俄比亚东部的英国军事管理地域示意；复国并不意味着所有东部地区立即恢复埃塞俄比亚直接行政管理。未逐段复原后来的移交线。',controlArea=True,controller='United Kingdom',controllerQid='Q145',sovereignName='Ethiopia',territoryType='administration',controlId='british-ogaden')]
  stage.repair(union_all([ethiopia,eritrea]),a,b,rows,remove=['Italian Africa','Kingdom of Italy'])
 print('Libya and Ethiopian restoration prepared',flush=True)
 iraq=mask('Iraq')
 for a,b in stage.periods(iraq,1917,1920,[1918]):
  region=iraq if a>=1918 else iraq.intersection(box(38,28,49,35))
  stage.repair(region,a,b,[item('British Administration of Mesopotamia','美索不达米亚（英国军事管理）','local:british-mesopotamia',region,IRAQ,'巴格达1917年被英军占领；摩苏尔在1918年停战后被英军占领。按年度代表阶段补出军事管理区，不提前使用1921年伊拉克王国或现代伊拉克的国际承认地位。边缘以地理区辅助概化。',controlArea=True,controller='United Kingdom',controllerQid='Q145',sovereignName='Ottoman Empire',territoryType='occupation',controlId='british-mesopotamia')],remove=['Ottoman Empire']if a>=1918 else[])
 syria=mask('Syria');lebanon=mask('Lebanon');jordan=mask('Jordan');palestine=union_all([mask('Israel'),mask('Gaza Strip'),mask('West Bank')])
 coast=syria.intersection(box(35,34.5,36.6,37));interior=union_all([syria.difference(coast),jordan]);levant=union_all([syria,lebanon,jordan,palestine])
 for a,b in stage.periods(levant,1918,1919):
  rows=[item('OETA East Arab Administration','叙利亚阿拉伯政府（费萨尔）','local:oeta-east',interior,OETA,'1918—1919年叙利亚内陆与外约旦的阿拉伯管理区，处于盟军总体军事安排中；费萨尔当时为埃米尔，1920年才短暂称叙利亚国王。不是整个汉志王国的领土。'),item('OETA Western Military Administration','黎巴嫩与叙利亚海岸（盟军管理）','local:oeta-west',union_all([lebanon,coast]),OETA,'盟军占领敌国领土管理区的西部／沿岸分区；英法管理安排分阶段变化，使用地理区概化，不等于1920年后法属委任统治边界。',sovereignName='France',sovereignQid='Q142',territoryType='administration'),item('OETA South Palestine','巴勒斯坦（英国军事管理）','local:oeta-south',palestine,OETA,'1918年秋占领完成后的OETA南区；不是现代以色列，也不是尚未生效的国际联盟委任统治。只表示当年的军事行政安排。',controlArea=True,controller='United Kingdom',controllerQid='Q145',sovereignName='Ottoman Empire',territoryType='occupation',controlId='oeta-south')]
  stage.repair(levant,a,b,rows,remove=['Kingdom of Hejaz','Ottoman Empire','United Kingdom Colony - Israel','United Kingdom Colony - Palestine','United Kingdom Colony - Jordan','United Kingdom Colony - Lebanon','United Kingdom Colony - Syria'])
 print('Post-Ottoman administrations prepared',flush=True)
 # Known core omissions: the surviving administrative/capital regions are not
 # replaced by a made-up empire covering a whole modern country.
 known=[('Gajapati Kingdom','奥里萨（加贾帕提王国）','local:gajapati-kingdom',1434,1541,Point(85.83,19.81).buffer(1.7), 'https://www.britannica.com/place/Odisha/History'),('Tomara Delhi','德里（托马拉王国）','local:tomara-delhi',900,1151,Point(77.21,28.61).buffer(.7),'https://www.britannica.com/place/Delhi/History'),('Great Zimbabwe Kingdom','大津巴布韦王国','local:great-zimbabwe',1220,1450,Point(30.93,-20.27).buffer(1.25),'https://whc.unesco.org/en/list/364/'),('Kingdom of Benin','贝宁王国','local:kingdom-of-benin',1200,1897,Point(5.63,6.34).buffer(.75),'https://www.britishmuseum.org/about-us/british-museum-story/contested-objects-collection/benin-bronzes'),('Inca Empire','印加帝国','Q28573',1438,1532,Point(-71.97,-13.52).buffer(.8),'https://www.metmuseum.org/essays/the-incas')]
 known.append(('Cahokia Polity','卡霍基亚城邦','local:cahokia',1050,1350,Point(-90.06,38.66).buffer(.35),'https://whc.unesco.org/en/list/198/'))
 land=clean(union_all([shape(f['geometry'])for f in read('public/data/ne_110m_land.geojson')['features']]))
 for n,label,q,lo,hi,g,source in known:
  # A small capital-region mask is a declared coarse minimum reconstruction,
  # not a claim to the entity's maximum historical territory.
  for a,b in stage.periods(g,lo,hi):stage.repair(g,a,b,[item(n,label,q,g.intersection(land),source,'以已核实的历史中心地及其周边地域补出遗漏的政权核心。只表示有据的概化最小范围，不代表全盛疆域；边缘为地理推断，未借现代国家范围扩大。',minimumCoreReconstruction=True)])
 # Conservative fallback catalogue: only explicitly reviewed identities or
 # clearly labelled regional collections, and only a footprint supported by
 # BOTH surrounding reference snapshots. No future snapshot is simply copied.
 definitions={
  'Benin':('Kingdom of Benin','贝宁王国','local:kingdom-of-benin',1200,1897,False),
  'Great Zimbabwe':('Great Zimbabwe Kingdom','大津巴布韦王国','local:great-zimbabwe',1220,1450,False),
  'Mwenemutapa':('Mutapa Kingdom','穆塔帕王国','local:mutapa',1450,1760,False),
  'Congo':('Kingdom of Kongo','刚果王国','local:kingdom-of-kongo',1390,1884,False),
  'Luba':('Kingdom of Luba','卢巴王国','local:luba',1585,1889,False),
  'Lunda':('Kingdom of Lunda','隆达王国','local:lunda',1660,1884,False),
  'Rozwi':('Rozvi Kingdom','罗兹维王国','local:rozvi',1684,1834,False),
  'Mossi States':('Mossi Kingdoms','莫西诸王国','local:mossi-kingdoms',1200,1896,True),
  'Hausa States':('Hausa City States','豪萨诸城邦','local:hausa-states',1000,1804,True),
  'Akan':('Akan Polities','阿坎诸邦','local:akan-polities',1200,1800,True),
  'Islamic city-states':('Swahili Coast City States','斯瓦希里沿海诸城邦','local:swahili-city-states',800,1890,True),
  'Bantu peoples':('Central and Southern African Polities','非洲中南部地方诸社群','local:central-south-african-polities',500,1850,True),
  'Khoisan':('Southern African Indigenous Communities','非洲南部原住民诸社群','local:southern-african-communities',500,1850,True),
  'West African cereal farmers':('West African Local Polities','西非地方诸邦与社群','local:west-african-polities',500,1850,True),
  'Madagascar':('Malagasy Polities','马达加斯加诸邦','local:malagasy-polities',800,1799,True),
  'Rajput kingdoms':('Rajput Principalities','拉杰普特诸邦','local:rajput-principalities',700,1800,True),
  'Rajputs':('Rajput Principalities','拉杰普特诸邦','local:rajput-principalities',700,1800,True),
  'Rajastan':('Rajput Principalities','拉杰普特诸邦','local:rajput-principalities',700,1800,True),
  'Orissa':('Odisha Regional Kingdoms','奥里萨诸王国','local:odisha-kingdoms',500,1433,True),
  'Kalinga':('Kalinga Regional Kingdoms','羯陵伽诸王国','local:kalinga-kingdoms',500,1433,True),
  'Burmese kingdoms':('Burmese Regional Kingdoms','缅甸诸王国','local:burmese-kingdoms',1300,1751,True),
  'Baltic tribes':('Baltic Local Polities','波罗的海诸部族与地方政权','local:baltic-polities',500,1300,True),
  'Prussians':('Old Prussian Polities','古普鲁士诸部族','local:old-prussian-polities',500,1283,True),
  'Karelians':('Karelian Local Polities','卡累利阿地方社群','local:karelian-polities',500,1800,True),
  'Suomi':('Finnish Local Polities','芬兰地方诸社群','local:finnish-polities',500,1249,True),
  'Finno-Ugric taiga hunter-gatherers':('Forest Zone Local Polities','东欧森林地带诸社群','local:forest-zone-polities',500,1800,True),
  'Pampas cultures':('Pampas Indigenous Polities','潘帕斯原住民诸社群','local:pampas-polities',500,1850,True),
  'Amazon hunter-gatherers':('Amazonian Indigenous Polities','亚马孙原住民诸社群','local:amazonian-polities',500,1850,True),
  'Andean hunter-gatherers':('Andean Local Polities','安第斯地方诸社群','local:andean-polities',500,1850,True),
  'Andean states and chiefdoms':('Andean Local Polities','安第斯地方诸社群','local:andean-polities',500,1850,True),
  'Maya city-states':('Maya City States','玛雅诸城邦','local:maya-city-states',500,1697,True),
  'Mesoamerican city-states and chiefdoms':('Mesoamerican Local Polities','中美洲地方诸邦','local:mesoamerican-polities',500,1518,True),
  'Eastern North American hunter-gatherers':('Eastern North American Polities','北美东部原住民诸社群','local:eastern-north-american-polities',500,1850,True),
  'North American Pacific foraging, hunting and fishing peoples':('Pacific Coast Indigenous Polities','北美太平洋沿岸原住民诸社群','local:pacific-coast-polities',500,1850,True),
  'Plain bison hunters':('Great Plains Indigenous Polities','北美大平原原住民诸社群','local:great-plains-polities',500,1850,True),
  'Subarctic forest hunter-gatherers':('Subarctic Indigenous Polities','亚北极原住民诸社群','local:subarctic-polities',500,1850,True),
  'Caribbean hunter-gatherers':('Caribbean Indigenous Polities','加勒比原住民诸社群','local:caribbean-polities',500,1650,True),
  'Taino':('Taino Chiefdoms','泰诺诸酋邦','local:taino-chiefdoms',800,1520,True),
  'Patagonian shellfish and marine mammal hunters':('Patagonian Indigenous Polities','巴塔哥尼亚原住民诸社群','local:patagonian-polities',500,1850,True),
  'Desert hunter-gatherers':('American Desert Indigenous Polities','美洲荒漠原住民诸社群','local:american-desert-polities',500,1850,True),
  'Savanna hunter-gatherers':('South American Savanna Polities','南美稀树草原诸社群','local:south-american-savanna-polities',500,1850,True),
 }
 refs=[]
 for m in read('public/data/manifest.json'):
  if 500<=m['year']<=1900:
   groups=defaultdict(list)
   for f in read('public/data/'+m['filename'])['features']:
    n=f['properties'].get('NAME')
    if n in definitions:groups[n].append(clean(shape(f['geometry'])))
   refs.append((m['year'],{n:clean(union_all(gs))for n,gs in groups.items()}))
 refs.sort()
 for (y,lower),(z,upper)in zip(refs,refs[1:]):
  if z-y>150:continue
  for raw,g in lower.items():
   if raw not in upper:continue
   n,label,q,lo,hi,collection=definitions[raw];a,b=max(y,lo),min(z-1,hi)
   if a>b:continue
   shared=clean(g.intersection(upper[raw]))
   if shared.is_empty or shared.area<.03:continue
   # Cross-continent generic labels have been assigned continent-specific IDs;
   # the geographic source, not the name alone, determines their location.
   note=f'依据{y}与{z}两幅历史参考图的共同地域，仅补当年原数据无归属部分。'
   note+=('这是多个地方政治与社会组织的地域集合，不是统一国家；不虚构共同统治者、统一宗教或全国国旗。'if collection else'国家核心与范围仍为图源概化，未宣称拥有逐年独立测绘。')
   for start,end in stage.periods(shared,a,b):stage.repair(shared,start,end,[item(n,label,q,shared,BASE,note,regionalCollection=collection,sourceReferenceYear=y,sourceReferenceEnd=z,representationKind='regional-polities'if collection else'polity')])
  print('Corroborated reference period',y,z,'prepared',flush=True)
 stage.finish()
 facts=read('public/data/polity-facts.json')
 for n,q in stage.identities.items():
  if q not in facts['entities']:facts['entities'][q]={'label':stage.labels[n],'en':n,'description':'有来源的历史政权或地方政治社群集合；地理分期和限制见地图档案。','fields':{}}
  facts['labels'][q]=stage.labels[n]
 write('public/data/polity-facts.json',facts)
if __name__=='__main__':main()
