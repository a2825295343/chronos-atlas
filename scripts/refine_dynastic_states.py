"""Separate composite dynastic/union records using existing historical masks.
This is an explicitly approximate partition, not newly surveyed annual borders.
The union of the source geometry is conserved; original records are backed up.
"""
import collections,copy,json,shutil,sys
from pathlib import Path
from enrich_polities import ROOT
sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape,mapping,box
from shapely import make_valid,union_all
from prepare_political_presentation import label_path
TAG='dynastic-states-2026-10-31'
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def clean(g):
 g=make_valid(g)
 if g.geom_type=='GeometryCollection':g=union_all([v for v in g.geoms if v.geom_type in ['Polygon','MultiPolygon']])
 return g
EMPTY=union_all([])
def main():
 folder=ROOT/'public/data/temporal';backup=ROOT/'.local/dynasty-originals';backup.mkdir(exist_ok=True);data={}
 for p in folder.glob('*.geojson'):
  saved=backup/p.name
  if not saved.exists():shutil.copyfile(p,saved)
  data[int(p.stem)]=json.loads(saved.read_bytes())
 def at(name,y):
  rows=[f for f in data[y//100]['features']if f['properties']['NAME']==name and f['properties']['validFrom']<=y<=f['properties']['validTo']]
  if not rows:raise ValueError('Missing historical mask '+name+' '+str(y))
  return clean(shape(max(rows,key=lambda f:f['properties']['validFrom'])['geometry']))
 masks={'norway':at('Old Kingdom of Norway',1396),'sweden':at('Kingdom of Sweden',1396),'denmark':at('Kingdom of Denmark',1396),'lithuania':at('Grand Duchy of Lithuania',1444),'bohemia':at('Kingdom of Bohemia',1527),'hungary':at('Kingdom of Hungary',1527),'burgundy':at('Free County of Burgundy',1380),'norwayLate':at('Kingdom of Norway',1910),'swedenLate':at('Kingdom of Sweden',1910)}
 labels={'Crown of the Kingdom of Poland':'波兰王国','Grand Duchy of Lithuania':'立陶宛大公国','Polish-Lithuanian Commonwealth':'波兰立陶宛联邦','Austrian Hereditary Lands':'奥地利世袭领地','Royal Hungary':'皇家匈牙利','Kingdom of Hungary':'匈牙利王国','Kingdom of Bohemia':'波希米亚王国','Burgundian Netherlands':'勃艮第尼德兰','Spanish Netherlands':'西属尼德兰','Austrian Netherlands':'奥属尼德兰','County of Burgundy':'勃艮第伯国','Kingdom of Denmark':'丹麦王国','Old Kingdom of Norway':'挪威王国','Kingdom of Norway':'挪威王国','Denmark':'丹麦','Kingdom of Sweden':'瑞典王国','Habsburg Upper Rhine Lands':'哈布斯堡上莱茵领地','Swabian Hohenstaufen Lands':'施瓦本诸领地','Bavarian Wittelsbach Duchies':'巴伐利亚诸公国','Ascanian Saxon Duchies':'萨克森诸公国','Angevin Adriatic Lands':'安茹亚得里亚领地','Duchy of Bourbon':'波旁公国','County Palatine of Cephalonia and Zakynthos':'凯法利尼亚和扎金索斯伯国','Angevin French Territories':'安茹—普罗旺斯诸领地','Duchy of Savoy':'萨伏依公国','Bahrain Sheikhdom':'巴林酋长国','County of Luxembourg':'卢森堡伯国','Duchy of Luxembourg':'卢森堡公国'}
 extra=read('.local/historical-review-2026-10-31/extra-resolved.json')
 ids={name:extra[name]for name in ['Crown of the Kingdom of Poland','Grand Duchy of Lithuania','Royal Hungary','Burgundian Netherlands','Spanish Netherlands','Austrian Netherlands','County of Burgundy','Duchy of Bourbon','Duchy of Savoy']}
 ids.update({'Kingdom of Hungary':'Q171150','Kingdom of Bohemia':'Q42585','Kingdom of Denmark':'Q756617','Old Kingdom of Norway':'Q20','Kingdom of Norway':'Q20','Denmark':'Q35','Kingdom of Sweden':'Q34','Polish-Lithuanian Commonwealth':'Q172107','Austrian Hereditary Lands':'local:austrian-hereditary-lands','Bahrain Sheikhdom':'Q398'})
 for name in labels:ids.setdefault(name,'local:'+name.lower().replace(' ','-'))
 simple={'House of Hohenstaufen':'Swabian Hohenstaufen Lands','House of Wittelsbach':'Bavarian Wittelsbach Duchies','House of Ascania':'Ascanian Saxon Duchies','House of Anjou-Sicily':'Angevin Adriatic Lands','House of Bourbon':'Duchy of Bourbon','House of Tocco':'County Palatine of Cephalonia and Zakynthos','House of Valois-Anjou':'Angevin French Territories','House of Savoy':'Duchy of Savoy','House of Khalifa':'Bahrain Sheikhdom'}
 source_names=set(simple)|{'House of Habsburg','Habsburg Monarchy','House of Jagiellon','Kalmar Union','House of Oldenburg','House of Luxembourg','Denmark-Norway','Sweden–Norway','United Kingdoms of Sweden and Norway'}
 nordic={'Kingdom of Denmark','Old Kingdom of Norway','Kingdom of Sweden'}
 component_names={'Crown of the Kingdom of Poland','Grand Duchy of Lithuania','Kingdom of Bohemia','Kingdom of Hungary','Polish-Lithuanian Commonwealth','County of Burgundy',*nordic,'Kingdom of Norway','Denmark'}
 audit=[];generated=0
 def make(name,g,a,b,parents,method,group=None):
  nonlocal generated
  if g.is_empty or g.area<1e-10:return None
  generated+=1;p={'NAME':name,'SUBJECTO':name,'qid':ids[name],'entityId':ids[name],'displayName':labels[name],'validFrom':a,'validTo':b,'sourceRecord':f'{TAG}:{name}:{a}:{b}','source':'Cliopatria · 复合记录分解','sourceNames':sorted(parents),'sourceName':' / '.join(sorted(parents)),'dynasticPatch':TAG,'geometryMethod':method,'accuracy':'保留上游外部轮廓，内界按已有历史王国轮廓裁切概化；不是逐年测绘国界。','identityReviewed':True,'identityCorrection':'以领土政治实体取代家族或共主集团名称。','sourceUrl':'https://jagiellonians.site.ox.ac.uk/jagiellonians-timeline'if group=='jagiellon'else'https://www.norgeshistorie.no/kilder/senmiddelalder/K1011-Unionsbrev.html'if group=='kalmar'else'https://www.habsburger.net/en/chapter/reuniting-habsburg-lands-maximilian-i'}
  if group:p['politicalGroup']=group
  if name in ['Austrian Hereditary Lands','Swabian Hohenstaufen Lands','Bavarian Wittelsbach Duchies','Ascanian Saxon Duchies','Angevin Adriatic Lands','Habsburg Upper Rhine Lands','Angevin French Territories']:p['representation']='territorial-aggregate';p['representationNote']='这是若干领地的集合称谓，不是声称存在同名统一主权国家；未获可靠内界的部分仍保留聚合。'
  path=label_path(g,labels[name])
  if path:p['labelPath']=path
  return {'type':'Feature','properties':p,'geometry':mapping(g)}
 for century,fc in data.items():
  affected=[f for f in fc['features']if f['properties']['NAME']in source_names]
  if not affected:
   # A source association incorrectly identifies Norway with Queen Margaret I.
   for f in fc['features']:
    if f['properties']['NAME']=='Old Kingdom of Norway':f['properties'].update(NAME='Kingdom of Norway',SUBJECTO='Kingdom of Norway',qid='Q20',entityId='Q20',displayName='挪威王国',sourceQid=f['properties'].get('sourceQid',f['properties'].get('qid')))
   continue
  lo,hi=century*100,century*100+100
  related=[f for f in fc['features']if f['properties']['NAME']in component_names]
  originals=affected+related;stops={lo,hi,1276,1354,1397,1457,1464,1497,1501,1521,1523,1524,1526,1547,1556,1569,1645,1658,1660,1699,1714,1795,1814,1905,1906}
  for f in originals:stops.update([f['properties']['validFrom'],f['properties']['validTo']+1])
  stops=sorted(s for s in stops if lo<=s<=hi);kept=[f for f in fc['features']if f not in originals];output=[]
  for a,end in zip(stops,stops[1:]):
   b=end-1;active={}
   for f in originals:
    p=f['properties'];n=p['NAME']
    if p['validFrom']<=a<=p['validTo']and(n not in active or p['validFrom']>active[n]['properties']['validFrom']):active[n]=f
   parts=collections.defaultdict(list);parents=collections.defaultdict(set);groups={}
   def put(name,g,parent,group=None):
    if name=='Old Kingdom of Norway':name='Kingdom of Norway'
    if name=='Kingdom of Denmark'and a>=1814:name='Denmark'
    if not g.is_empty:parts[name].append(g);parents[name].add(parent);groups[name]=group
   for n,f in active.items():
    if n in component_names:put(n,clean(shape(f['geometry'])),n)
   # Split the three Nordic crowns even when the source labels them "Oldenburg".
   unions=[shape(f['geometry'])for n,f in active.items()if n in ['Kalmar Union','House of Oldenburg','Denmark-Norway','Sweden–Norway','United Kingdoms of Sweden and Norway']]
   if unions:
    g=clean(union_all(unions));rest=g;np={}
    for key,n in ([('norway','Old Kingdom of Norway'),('sweden','Kingdom of Sweden'),('denmark','Kingdom of Denmark')]if a>=1658 else[('sweden','Kingdom of Sweden'),('norway','Old Kingdom of Norway'),('denmark','Kingdom of Denmark')]):
     mask=masks['norwayLate']if key=='norway'and a>=1658 else masks['swedenLate']if key=='sweden'and a>=1658 else masks[key]
     if key=='norway'and 1658<=a<1814:mask=union_all([mask,masks['norway'].intersection(box(-180,-90,5,90))])
     if a<1814 and 'Denmark-Norway'in active and not any(n in active for n in ['Kalmar Union','House of Oldenburg'])and key=='sweden':continue
     if a<1814 and ('Sweden–Norway'in active or 'United Kingdoms of Sweden and Norway'in active)and key=='denmark':continue
     np[n]=clean(rest)if a>=1814 and key=='denmark'else clean(rest.intersection(mask));rest=clean(rest.difference(np[n]))
    # Differences in coast simplification leave small isolated pieces. Assign
    # these to the nearest historic kingdom, without drawing a modern border.
    for piece in ([rest]if rest.geom_type=='Polygon'else getattr(rest,'geoms',[])):
     if piece.is_empty:continue
     closest=min(np,key=lambda n:piece.representative_point().distance(np[n]if not np[n].is_empty else masks[{'Kingdom of Sweden':'sweden','Old Kingdom of Norway':'norway','Kingdom of Denmark':'denmark'}[n]]))
     np[closest]=clean(union_all([np[closest],piece]))
    for n,part in np.items():put(n,part,' / '.join(n for n in ['Kalmar Union','House of Oldenburg','Denmark-Norway','Sweden–Norway','United Kingdoms of Sweden and Norway']if n in active),'kalmar')
    audit.append({'year':a,'group':'kalmar','sourceArea':g.area,'partitionArea':sum(v.area for v in np.values()),'method':'以1396年历史王国轮廓为早期掩膜；1658年后北欧使用后期王国轮廓，外界保留所选时期GIS。海岸碎片归最近历史轮廓。'})
   for n,f in active.items():
    if n not in source_names or n in ['Kalmar Union','House of Oldenburg','Denmark-Norway','Sweden–Norway','United Kingdoms of Sweden and Norway']:continue
    g=clean(shape(f['geometry']))
    if n=='House of Jagiellon':
     if a>=1569:put('Polish-Lithuanian Commonwealth',g,n,'jagiellon')
     else:
      lith=clean(g.intersection(masks['lithuania']));put('Grand Duchy of Lithuania',lith,n,'jagiellon');put('Crown of the Kingdom of Poland',clean(g.difference(lith)),n,'jagiellon')
     continue
    if n in ['House of Habsburg','Habsburg Monarchy']:
     before=g
     # Retain separately represented kingdoms; a dynastic overlay must not
     # replace their independent source geometry or create two territorial owners.
     for country in ['Kingdom of Bohemia','Kingdom of Hungary','County of Burgundy']:
      if country in active:g=clean(g.difference(shape(active[country]['geometry'])))
     if a>=1438:
      bg=clean(g.intersection(masks['bohemia']));put('Kingdom of Bohemia',bg,n,'habsburg');g=clean(g.difference(bg))
      hg=clean(g.intersection(masks['hungary']));put('Royal Hungary'if a<1699 else'Kingdom of Hungary',hg,n,'habsburg');g=clean(g.difference(hg))
     # The Low Countries and Franche-Comte are detached components; these
     # geographic windows separate them without inventing an interior frontier.
     ng=clean(g.intersection(box(-1,48.8,8.1,55)))if a>=1477 else EMPTY;g=clean(g.difference(ng))
     net='Burgundian Netherlands'if a<1556 else'Spanish Netherlands'if a<1714 else'Austrian Netherlands'
     put(net,ng,n,'habsburg')
     burg=clean(g.intersection(masks['burgundy']))if a>=1477 else EMPTY;put('County of Burgundy',burg,n,'habsburg');g=clean(g.difference(burg))
     put('Habsburg Upper Rhine Lands'if a<1276 else'Austrian Hereditary Lands',g,n,'habsburg');continue
    if n=='House of Luxembourg':put('County of Luxembourg'if a<1354 else'Duchy of Luxembourg',g,n);continue
    put(simple[n],g,n)
   for n,geos in parts.items():
    g=clean(union_all(geos));row=make(n,g,a,b,parents[n],'历史政权掩膜分解；优先保留独立王国原始几何。',groups.get(n))
    if row:output.append(row)
  fc['features']=kept+output
  print('Partitioned century',century,'new rows',len(output),flush=True)
 # The 1516-1517 conquest must also change the map in its event years,
 # rather than leaving the Mamluk state alive through a later snapshot.
 def historical_feature(name,y):
  candidates=[f for f in data[15]['features']if f['properties']['NAME']==name and f['properties']['validFrom']<=y<=f['properties']['validTo']]
  return max(candidates,key=lambda f:f['properties']['validFrom'])
 ott=historical_feature('Ottoman Empire',1515);mam=historical_feature('Mamluk Sultanate',1515);og=clean(shape(ott['geometry']));mg=clean(shape(mam['geometry']))
 provinces=read('.local/ne_10m_admin_1_states_provinces.geojson')['features']
 syria=clean(union_all([shape(f['geometry'])for f in provinces if f['properties'].get('admin')in ['Syria','Lebanon','Jordan','Israel','Palestine']]))
 if syria.is_empty:raise ValueError('Missing geographical mask for the 1516 Syrian campaign')
 captured=clean(mg.intersection(syria));remaining=clean(mg.difference(captured));kept=[]
 for f in data[15]['features']:
  p=f['properties'];a,b=p['validFrom'],p['validTo']
  if p['NAME']not in ['Ottoman Empire','Mamluk Sultanate']or b<1516 or a>1518:kept.append(f);continue
  if a<1516:
   row=copy.deepcopy(f);row['properties']['validTo']=1515;kept.append(row)
  if b>1518:
   row=copy.deepcopy(f);row['properties']['validFrom']=1519;kept.append(row)
 for original,name,g,a,b in [(ott,'Ottoman Empire',clean(union_all([og,captured])),1516,1516),(mam,'Mamluk Sultanate',remaining,1516,1516),(ott,'Ottoman Empire',clean(union_all([og,mg])),1517,1518)]:
  row=copy.deepcopy(original);p=row['properties'];p.update(validFrom=a,validTo=b,sourceRecord=f'{TAG}:ottoman-conquest:{name}:{a}:{b}',source='Cliopatria + 1516—1517年征服分期',sourceUrl='https://islamicceramics.ashmolean.org/Iznik/conquest.htm',geometryMethod='已有历史轮廓与叙利亚、黎凡特现代地理区相交概化；不是精确历史战线',accuracy='1516年末代表状态划出叙利亚与黎凡特，1517年末代表状态并入埃及；只调整有史料支持的事件年份，边界仍为概化重建。',yearConvention='年末代表状态；战争参与者列表仍可包括年内战败和消失的国家',chronologyPatch='ottoman-conquest-1516-1517');p.pop('labelPath',None);label=p.get('displayName',name)
  if path:=label_path(g,label):p['labelPath']=path
  row['geometry']=mapping(g);kept.append(row)
 data[15]['features']=kept
 for c,fc in data.items():
  for f in fc['features']:
   p=f['properties']
   if p.get('sovereignName')=='Denmark-Norway':p['sovereignName']='Kingdom of Norway'if any(k in p['NAME']for k in ['Greenland','Iceland','Faroe'])and p['validTo']<1814 else'Kingdom of Denmark';p['sovereignQid']='Q20'if p['sovereignName']=='Kingdom of Norway'else'Q756617'
  write(f'public/data/temporal/{c}.geojson',fc)
 for file in ['src/localization/temporal.zh.json','src/localization/display-names.zh.json']:
  names=read(file);names.update(labels);write(file,names)
 curated=read('public/data/curated-facts.json')
 for name,q in ids.items():curated['identities'][name]=q
 for n in ['House of Habsburg','Habsburg Monarchy','House of Jagiellon','House of Oldenburg']:curated['identities'].pop(n,None)
 write('public/data/curated-facts.json',curated)
 facts=read('public/data/polity-facts.json')
 for name,q in ids.items():
  e=facts['entities'].setdefault(q,{'fields':{},'description':'','en':name});e['label']=labels[name]
  if name=='Austrian Hereditary Lands':e['description']='奥地利、内奥地利、外奥地利与蒂罗尔等世袭领地的集合；各支系权力及内部界线随时代不同。'
 write('public/data/polity-facts.json',facts)
 index=read('public/data/temporal/index.json');allrows=[f for fc in data.values()for f in fc['features']];index['counts']['polityRecords']=len({f['properties']['sourceRecord']for f in allrows});index['changeYears']=sorted({y for f in allrows for y in [f['properties']['validFrom'],f['properties']['validTo']+1]});index['dynasticRevision']=TAG;write('public/data/temporal/index.json',index)
 write('public/data/dynastic-state-review.json',{'reviewedAt':'2026-10-31','generatedRows':generated,'labels':labels,'ids':ids,'partitions':audit,'limitations':['王朝不是自动等于国家，联合也不是自动等于统一国家。','卡尔马三国与波兰—立陶宛使用并集外界和较早独立王国轮廓概化分解，内界未达到逐年测绘精度。','奥地利世袭领地等仍缺少可靠细分内界的部分明确标为领地集合；不将聚合名称伪装为正式统一国名。','1569年之后的波兰立陶宛联邦保留为条约建立的复合国家，不机械拆除所有名称含联合的实体。']})
 print('Dynastic/union partition rows',generated,flush=True)
if __name__=='__main__':main()
