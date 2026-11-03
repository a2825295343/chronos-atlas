"""Sourced early political and cultural context, kept distinct in the archive."""
import json,copy,shutil,hashlib,re
from collections import defaultdict
from territory_repair_stage import Stage,ROOT,read,write,clean
from shapely import union_all
from shapely.geometry import shape,Point,box
TAG='early-coverage-2026-11-01'
BASE='https://github.com/aourednik/historical-basemaps'
HUMAN='https://humanorigins.si.edu/evidence'

# Raw reference name -> map identity, Chinese name, valid range, representation.
# Geographic community collections do not imply a single sovereign or ethnicity.
CONTEXTS=[
 (['Indus valley civilization'],'Harappan Cultural Communities','印度河流域与哈拉帕文化','harappan',-3300,-1300,'archaeological-culture','https://whc.unesco.org/en/list/138/'),
 (['Jōmon','Late Jomon culture'],'Jomon Cultural Communities','绳文文化诸社群','jomon',-10000,-301,'archaeological-culture','https://whc.unesco.org/en/list/1632/'),
 (['Yamnaya culture'],'Yamnaya Cultural Communities','颜那亚文化','yamnaya',-3300,-2500,'archaeological-culture','https://en.wikipedia.org/wiki/Yamnaya_culture'),
 (['Afanasevo'],'Afanasievo Cultural Communities','阿凡纳谢沃文化','afanasievo',-3300,-2500,'archaeological-culture','https://en.wikipedia.org/wiki/Afanasievo_culture'),
 (['Andronovo'],'Andronovo Cultural Communities','安德罗诺沃文化诸社群','andronovo',-2000,-900,'archaeological-culture','https://en.wikipedia.org/wiki/Andronovo_culture'),
 (['Sintashta'],'Sintashta Cultural Communities','辛塔什塔文化','sintashta',-2100,-1750,'archaeological-culture','https://en.wikipedia.org/wiki/Sintashta_culture'),
 (['Beaker'],'Bell Beaker Cultural Communities','钟形杯文化诸社群','bell-beaker',-2800,-1800,'archaeological-culture','https://en.wikipedia.org/wiki/Bell_Beaker_culture'),
 (['Urnfield cultures'],'Urnfield Cultural Communities','瓮棺文化诸社群','urnfield',-1300,-750,'archaeological-culture','https://en.wikipedia.org/wiki/Urnfield_culture'),
 (['N. European Bronze Age cultures'],'Nordic Bronze Age Communities','北欧青铜时代社群','nordic-bronze',-1700,-500,'archaeological-culture','https://en.wikipedia.org/wiki/Nordic_Bronze_Age'),
 (['Oxus'],'Oxus Cultural Communities','阿姆河文明诸社群','oxus',-2300,-1700,'archaeological-culture','https://en.wikipedia.org/wiki/Bactria%E2%80%93Margiana_Archaeological_Complex'),
 (['Chavin'],'Chavin Cultural Communities','查文文化','chavin',-900,-200,'archaeological-culture','https://whc.unesco.org/en/list/330/'),
 (['Olmec'],'Olmec Cultural Communities','奥尔梅克诸中心','olmec',-1500,-400,'archaeological-culture','https://en.wikipedia.org/wiki/Olmecs'),
 (['Nazca'],'Nazca Cultural Communities','纳斯卡文化','nazca',-100,800,'archaeological-culture','https://whc.unesco.org/en/list/700/'),
 (['Moche'],'Moche Valley Polities','莫切诸河谷政权','moche',100,800,'archaeological-culture','https://whc.unesco.org/en/list/366/'),
 (['Huari Empire'],'Wari Regional Polities','瓦里诸中心','wari',600,1000,'archaeological-culture','https://en.wikipedia.org/wiki/Wari_culture'),
 (['Tiahuanaco Empire'],'Tiwanaku Cultural Communities','蒂瓦纳库文化','tiwanaku',500,1000,'archaeological-culture','https://whc.unesco.org/en/list/567/'),
 (['Maya chiefdoms and states','Maya states','Maya city-states'],'Maya Regional Polities','玛雅诸邦','maya-polities',-500,1399,'regional-polities','https://whc.unesco.org/en/list/64/'),
 (['Hopewell Culture'],'Hopewell Cultural Networks','霍普韦尔文化网络','hopewell',-200,500,'archaeological-culture','https://whc.unesco.org/en/list/1689/'),
 (['Adena Culture'],'Adena Cultural Communities','阿登纳文化','adena',-1000,-100,'archaeological-culture','https://en.wikipedia.org/wiki/Adena_culture'),
 (['Pomeranian culture '],'Pomeranian Cultural Communities','波美拉尼亚文化','pomeranian-culture',-700,-100,'archaeological-culture','https://en.wikipedia.org/wiki/Pomeranian_culture'),
 (['Amazon hunter-gatherers'],'Amazonian Indigenous Polities','亚马孙诸社群','amazonian-polities',-2000,1399,'regional-polities',HUMAN),
 (['Andean hunter-gatherers'],'Andean Local Polities','安第斯地方诸邦','andean-polities',-2000,1399,'regional-polities',HUMAN),
 (['Eastern North American hunter-gatherers'],'Eastern North American Indigenous Polities','北美东部原住民诸社群','eastern-north-american-polities',-2000,1399,'regional-polities',HUMAN),
 (['Plain bison hunters'],'Great Plains Indigenous Polities','北美大平原原住民诸社群','great-plains-polities',-2000,1399,'regional-polities',HUMAN),
 (['North American Pacific foraging, hunting and fishing peoples'],'Pacific Northwest Indigenous Societies','北美太平洋沿岸诸社群','pacific-northwest-societies',-2000,1399,'regional-polities',HUMAN),
 (['Plateau fichers and hunter gatherers'],'North American Plateau Communities','北美高原诸社群','north-american-plateau',-2000,1399,'regional-polities',HUMAN),
 (['Subarctic forest hunter-gatherers'],'Subarctic Indigenous Polities','亚北极原住民诸社群','subarctic-polities',-2000,1399,'regional-polities',HUMAN),
 (['Arctic marine mammal hunters','Paleo-Inuit'],'Arctic Early Cultural Communities','北极早期文化诸社群','arctic-early-communities',-2500,1399,'regional-polities',HUMAN),
 (['Caribbean hunter-gatherers'],'Caribbean Indigenous Polities','加勒比原住民诸社群','caribbean-polities',-2000,1399,'regional-polities',HUMAN),
 (['Patagonian shellfish and marine mammal hunters','Pampas cultures'],'Patagonian and Pampas Communities','巴塔哥尼亚与潘帕斯诸社群','patagonia-pampas',-2000,1399,'regional-polities',HUMAN),
 (['Australian aboriginal hunter-gatherers'],'Australian Indigenous Communities','澳大利亚原住民诸社群','australian-indigenous',-10000,1399,'regional-polities',HUMAN),
 (['Tasmanian hunter-gatherers','Aboriginal Tasmanians'],'Tasmanian Indigenous Communities','塔斯马尼亚原住民诸社群','tasmanian-indigenous',-10000,1399,'regional-polities',HUMAN),
 (['West African cereal farmers'],'West African Local Polities','西非地方诸邦与社群','west-african-polities',-1500,1399,'regional-polities',HUMAN),
 (['Saharan pastoral nomads'],'Saharan Pastoral Communities','撒哈拉牧业诸社群','saharan-pastoral',-3000,1399,'regional-polities',HUMAN),
 (['Khoisan'],'Southern African Indigenous Communities','非洲南部原住民诸社群','southern-african-communities',-10000,1399,'regional-polities',HUMAN),
 (['Finno-Ugric taiga hunter-gatherers'],'Northeastern European Forest Communities','东北欧森林诸社群','northeastern-european-forest',-5000,1399,'regional-polities',HUMAN),
 (['Saami','Samis'],'Northern European Forest and Tundra Communities','北欧森林与苔原诸社群','northern-european-tundra',-2000,1399,'regional-polities',HUMAN),
 (['Paleo-Siberian hunter-gatherers'],'Siberian Local Communities','西伯利亚地方诸社群','siberian-local',-5000,1399,'regional-polities',HUMAN),
 (['Proto-Altaic pastoralists'],'Inner Asian Pastoral Communities','内亚草原牧业诸社群','inner-asian-pastoral',-2000,1399,'regional-polities',HUMAN),
 (['Arabian pastoral nomads'],'Ancient Arabian Local Communities','古代阿拉伯地方诸社群','ancient-arabian-local',-2000,1399,'regional-polities',HUMAN),
]
POLITIES=[
 (['Achaemenid Empire'],'Achaemenid Empire','阿契美尼德帝国','Q389688',-550,-331),
 (['Carthaginian Empire','Carthage'],'Carthage','迦太基','Q2429397',-650,-147),
 (['Rome'],'Roman Republic','罗马共和国','Q17167',-509,-28),
 (['Parthian Empire'],'Parthian Empire','安息帝国','Q1986139',-247,223),
 (['Sasanian Empire'],'Sasanian Empire','萨珊帝国','Q83891',224,650),
 (['Gupta Empire'],'Gupta Empire','笈多帝国','Q11774',320,550),
 (['Kalinga'],'Kalinga Regional Kingdoms','羯陵伽诸王国','local:kalinga-regional',-300,1400),
 (['Satavahanihara'],'Satavahana Realm','百乘王国','local:satavahana-realm',-100,220),
 (['Cheras'],'Chera Kingdoms','哲罗诸王国','local:chera-kingdoms',1,1100),
 (['Pallavas'],'Pallava Kingdom','帕拉瓦王国','local:pallava-kingdom',275,897),
 (['Pandyas'],'Pandya Kingdom','潘地亚王国','local:pandya-kingdom',1,1345),
 (['Kadambas'],'Kadamba Kingdom','迦檀婆王国','local:kadamba-kingdom',345,540),
 (['Vakataka'],'Vakataka Kingdom','伐迦陀迦王国','local:vakataka-kingdom',250,500),
 (['Western Gangas'],'Western Ganga Kingdom','西恒伽王国','local:western-ganga',350,999),
 (['Palas'],'Pala Empire','波罗王国','local:pala-empire',750,1161),
 (['Pratiharas'],'Gurjara Pratihara Kingdom','瞿折罗-普腊蒂哈腊王国','local:gurjara-pratihara',730,1035),
 (['Funan'],'Funan','扶南','local:funan',100,600),
 (['Champa'],'Champa','占婆诸邦','local:champa',192,1399),
 (['Chalukya Empire'],'Western Chalukya Empire','西遮娄其王国','local:western-chalukya',973,1189),
 (['Kingdom of Pagan'],'Pagan Kingdom','蒲甘王国','local:pagan-kingdom',849,1287),
 (['Srivijaya Empire'],'Srivijaya','室利佛逝','local:srivijaya',650,1275),
 (['Khmer Empire'],'Khmer Empire','高棉帝国','Q201705',802,1399),
 (['Axum'],'Kingdom of Axum','阿克苏姆王国','Q139377',100,940),
 (['Ghana','Empire of Ghana'],'Ghana Empire','加纳帝国','local:ghana-empire',500,1239),
 (['Kanem'],'Kanem Empire','加涅姆王国','local:kanem-empire',800,1399),
 (['Makkura'],'Makuria','马库里亚王国','local:makuria',550,1399),
 (['Alwa'],'Alodia','阿洛迪亚王国','local:alodia',580,1399),
 (['Saba'],'Kingdom of Saba','赛伯邑王国','local:saba',-800,275),
 (['Himyarite Kingdom'],'Himyarite Kingdom','希木叶尔王国','local:himyar',-110,525),
]
CONTEXTS.extend([
 (['Aboriginal tribes'],'Australian Indigenous Communities','澳大利亚原住民诸社群','australian-indigenous',-3400,1399,'regional-polities',HUMAN),
 (['Bantu'],'Early African Local Communities','非洲早期地方诸社群','early-african-local',-3400,499,'regional-polities',HUMAN),
 (['Hunters-gatherers'],'Early Foraging Communities','早期采集狩猎诸社群','early-foraging',-3400,499,'regional-polities',HUMAN),
 (['Dravidians'],'Early South Asian Communities','南亚早期地方诸社群','early-south-asian',-3400,299,'regional-polities',HUMAN),
 (['Austronesians'],'Early Maritime Asian Communities','亚洲海域早期诸社群','early-maritime-asian',-3400,499,'regional-polities',HUMAN),
 (['Berbers'],'North African Local Communities','北非地方诸社群','north-african-local',-1500,1399,'regional-polities',HUMAN),
])

def main():
 stage=Stage(TAG,range(-34,14));definitions={};refs=[]
 names={r:d for d in CONTEXTS for r in d[0]};political={r:d for d in POLITIES for r in d[0]}
 manifest=read('public/data/manifest.json')
 for m in manifest:
  if -4000<=m['year']<=1400:
   groups=defaultdict(list)
   original=ROOT/'.local'/TAG/'legacy-originals'/m['filename']
   source_data=json.loads(original.read_bytes())if original.exists()else read('public/data/'+m['filename'])
   for f in source_data['features']:
    n=f['properties'].get('NAME')
    if n in names or n in political:groups[n].append(clean(shape(f['geometry'])))
   refs.append((m['year'],{n:clean(union_all(gs))for n,gs in groups.items()}))
 refs.sort()
 for (y,lower),(z,upper)in zip(refs,refs[1:]):
  for raw,g in lower.items():
   if raw not in upper:continue
   if raw in names:
    _,n,label,key,lo,hi,kind,source=names[raw];q='local:'+key;regional=True
   else:
    if z-y>250:continue
    _,n,label,q,lo,hi=political[raw];kind='polity';regional=False;source=BASE
   a,b=max(-3400,y,lo),min(1399,z-1,hi)
   if a>b:continue
   shared=clean(g.intersection(upper[raw]));
   if shared.is_empty or shared.area<.04:continue
   note=f'取{y}与{z}两幅参考图共同的分布地域，仅补未关联政治实体的地区。'
   note+=('属于考古文化或多社群分布概览，不是一个统一国家；长时段的共同分布不证明各年疆域或文化边缘恒定。'if regional else'以两幅图的共同地域作为保守补缺，不复制未来最大疆域；无法确定的边缘继续留为未核定。')
   variants=[(n,label,q,shared)]
   if raw=='Aboriginal tribes':variants=[(n,label,q,clean(shared.intersection(box(110,-45,155,-10))))]
   if raw=='Bantu':variants=[(n,label,q,clean(shared.intersection(box(-20,-36,52,15))))];note+=' 源图使用的后世语言／民族名称不作为此时代身份的证据，已改为中性地域称呼。'
   if raw=='Hunters-gatherers':
    variants=[]
    for key,cn,bounds in [('africa','非洲',(-20,-36,55,35)),('europe','欧洲',(-25,35,50,85)),('asia','亚洲',(50,-12,180,85)),('americas','美洲',(-170,-60,-30,75)),('australia','澳大利亚',(110,-45,155,-10))]:variants.append((n+' - '+key,cn+'早期采集狩猎诸社群',q+'-'+key,clean(shared.intersection(box(*bounds)))))
   for name,zh,identity,footprint in variants:
    if footprint.is_empty or footprint.area<.04:continue
    definitions[name]={'label':zh,'qid':identity,'from':lo,'to':hi,'regional':regional,'representationKind':kind,'source':source,'note':note}
    for start,end in stage.periods(footprint,a,b):stage.repair(footprint,start,end,[(name,zh,identity,footprint,BASE,note,{'regionalCollection':regional,'representationKind':kind,'representationNote':note,'sourceReferenceYear':y,'sourceReferenceEnd':z,'contextSource':source,'inferredBoundary':True})])
  print('Early reference interval',y,z,'prepared',flush=True)
 stage.finish('early-coverage-review.json');write('public/data/early-coverage-definitions.json',definitions)
 # Pre-3400 legacy culture snapshots need the same identities and explanatory
 # archive types. Do not extrapolate the modern language label Bantu into 8000BC.
 backup=ROOT/'.local'/TAG/'legacy-originals';backup.mkdir(parents=True,exist_ok=True)
 metadata={r:d for d in CONTEXTS for r in d[0]}
 for m in manifest:
  if m['year']>=-3400:continue
  path=ROOT/'public/data'/m['filename'];saved=backup/path.name
  if not saved.exists():shutil.copyfile(path,saved)
  data=json.loads(saved.read_bytes())
  for f in data['features']:
   p=f['properties'];raw=p.get('NAME');definition=metadata.get(raw)
   if definition and definition[4]<=m['year']<=definition[5]:
    _,n,label,key,lo,hi,kind,source=definition
    p.update(sourceName=raw,NAME=n,SUBJECTO=n,displayName=label,qid='local:'+key,entityId='local:'+key,regionalCollection=True,representationKind=kind,contextSource=source,representationNote='史前文化与人类活动分布示意，不等于国家疆界；没有可据此补出的全国国旗或具名统治者。')
    definitions.setdefault(n,{'label':label,'qid':'local:'+key,'from':lo,'to':hi,'regional':True,'representationKind':kind,'source':source,'note':p['representationNote']})
   elif raw in ['Bantu','Austronesians','Thai','Koreans']:
    generic={'Bantu':('Early African Communities','非洲早期社群'),'Austronesians':('Early Coastal Asian Communities','亚洲沿海早期社群'),'Thai':('Early Mainland Southeast Asian Communities','东南亚内陆早期社群'),'Koreans':('Early Korean Peninsula Communities','朝鲜半岛早期社群')};n,label=generic[raw];q='local:'+n.lower().replace(' ','-');p.update(sourceName=raw,NAME=n,SUBJECTO=n,displayName=label,qid=q,entityId=q,regionalCollection=True,representationKind='archaeological-culture',representationNote='删除源参考图中回溯使用的后世语言或民族称呼，仅保留宽泛人类活动地域。不是已证实的单一考古文化、民族或国家。',contextSource=HUMAN);definitions.setdefault(n,{'label':label,'qid':q,'from':-10000,'to':-3401,'regional':True,'representationKind':'archaeological-culture','source':HUMAN,'note':p['representationNote']})
   elif raw and raw.strip():
    special={'Homo erectus':('Homo erectus distribution','直立人活动参考区'),'Homo heidelbergensis':('Archaic human distribution','古人类活动参考区'),'Neanderthal':('Neanderthal distribution','尼安德特人活动参考区'),'Egypt':('Predynastic Nile Communities','尼罗河史前聚落社群'),'Minoan':('Early Cretan Communities','克里特岛早期聚落社群'),'Kerma':('Early Middle Nile Communities','中尼罗河早期聚落社群'),'Norte Chico':('Early Andean Coastal Communities','安第斯沿海早期聚落社群'),'Ur':('Early Ur Region Communities','乌尔地区早期聚落社群'),'Semites':('Early Mesopotamian and Levantine Communities','两河与黎凡特早期社群'),'Hurrian Kingdoms':('Early West Asian Highland Communities','西亚山地早期社群')}
    n,label=special.get(raw,('Prehistoric context - '+raw,read('src/localization/names.zh.json').get(raw,raw)))
    q='local:prehistoric-'+re.sub('[^a-z0-9]+','-',n.lower()).strip('-');kind='human-presence'if raw in ['Homo erectus','Homo heidelbergensis','Neanderthal']else'archaeological-culture';note='源地图的史前活动分布概览；物种分类、文化联系和具体年代须按遗址证据核对，不表示统一国家、现代民族或真实政治国界。资料页起止仅用于适配快照，不能当作物种或文化的精确存续期。'
    p.update(sourceName=raw,NAME=n,SUBJECTO=n,displayName=label,qid=q,entityId=q,regionalCollection=True,representationKind=kind,representationNote=note,contextSource=HUMAN)
    definitions.setdefault(n,{'label':label,'qid':q,'from':-123000,'to':-3401,'regional':True,'representationKind':kind,'source':HUMAN,'note':note})
  path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8');m.setdefault('sourceSha256',m.get('sha256'));m['sha256']=hashlib.sha256(path.read_bytes()).hexdigest();m['countries']=sorted({f['properties']['NAME']for f in data['features']if f['properties'].get('NAME')});m['contextRevision']=TAG
  print('Legacy culture metadata reviewed',m['year'],flush=True)
 write('public/data/manifest.json',manifest)
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json','src/localization/names.zh.json']:
  labels=read(path);labels.update({n:d['label']for n,d in definitions.items()});write(path,labels)
 provenance=read('src/localization/provenance.json');provenance.update({n:'reviewed-historical-context'for n in definitions});write('src/localization/provenance.json',provenance)
 write('public/data/early-coverage-definitions.json',definitions)
 print('Early identities',len(definitions),flush=True)
if __name__=='__main__':main()
