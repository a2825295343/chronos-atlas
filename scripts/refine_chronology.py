"""Apply reviewed chronological patches after the existing atlas build pipeline.
Only dated events change ownership; geometry is never interpolated between years.
The regional reconstruction is explicitly approximate, not an annual survey.
"""
import collections,copy,json,pathlib,shutil,sys,urllib.parse
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape,mapping
from shapely import make_valid,union_all
from prepare_political_presentation import label_path
PATCH='chronology-2026-10'
MING_SOURCE='https://zh.wikisource.org/wiki/明史/卷2'
MONGOL_SOURCE='https://www.nationalmuseum.mn/index.php?hall=8&lang=en&p=exhibitions&tab=permanent'
def read(path):return json.loads((ROOT/path).read_bytes())
def write(path,data):
 (ROOT/path).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def clean(g):
 g=make_valid(g)
 if g.geom_type=='GeometryCollection':g=union_all([p for p in g.geoms if p.geom_type in ['Polygon','MultiPolygon']])
 return g
def main():
 folder=ROOT/'public/data/temporal';backup=ROOT/'.local/chronology-originals';backup.mkdir(exist_ok=True)
 # Always start from the same pre-patch shards, including earlier control overlays.
 paths=sorted(folder.glob('*.geojson'));data={}
 for p in paths:
  original=backup/p.name
  if not original.exists():shutil.copyfile(p,original)
  data[int(p.stem)]=json.loads(original.read_bytes())
 catalog=read('public/data/chronology-corrections.json');successions=read('public/data/chronology-successions.json')['identityCorrections']
 modern=read('public/data/modern-identity-corrections.json')['identityCorrections']
 corrections=list({(r['name'],r['from'],r['to']):r for r in catalog['identityCorrections']+successions+modern}.values());catalog['identityCorrections']=corrections;changed=collections.Counter()
 for c,fc in data.items():
  rows=[]
  for f in fc['features']:
   p=f['properties'];a,b=p['validFrom'],p['validTo']
   matches=[r for r in corrections if r['name']==p['NAME'] and r['from']<=b and a<=r['to'] and (not p.get('sovereignName')or r['name'].startswith('British Territory - '))]
   stops=sorted({a,b+1}|{max(a,r['from'])for r in matches}|{min(b+1,r['to']+1)for r in matches})
   for start,end in zip(stops,stops[1:]):
    if end-1<c*100 or start>c*100+99:continue
    row=copy.deepcopy(f);q=row['properties'];q.update(validFrom=start,validTo=end-1)
    for r in matches:
     if r['from']<=start<=r['to']:
      q.update(sourceQid=p.get('sourceQid',p.get('qid')),sourceName=p.get('sourceName',p['NAME']),qid=r['qid'],entityId=r['qid'],displayName=r['label'],identityReviewed=True,identitySource='https://www.wikidata.org/wiki/'+r['qid']if r['qid'].startswith('Q')else'https://en.wikipedia.org/wiki/'+urllib.parse.quote(r['article']),identityCorrection=r['reason'])
      if r.get('canonicalName'):q.update(NAME=r['canonicalName'],SUBJECTO=r['canonicalName'])
      for key in ['sovereignName','sovereignQid','territoryType']:
       if key in r:q[key]=r[key]
      # A source label baseline may have the wrong character count or position.
      q.pop('labelPath',None);changed[r['name']]+=1
    rows.append(row)
  fc['features']=rows
 # Reconstruct the early Ming conquest sequence using existing historical coast
 # and polity outlines; modern provinces are spatial masks, not historical borders.
 raw=data[13]['features']
 def find(name,year):return next(f for f in raw if f['properties']['NAME']==name and f['properties']['validFrom']<=year<=f['properties']['validTo'])
 ming_late=shape(find('Ming Dynasty',1390)['geometry']);north=shape(find('Northern Yuan',1390)['geometry'])
 yuan=shape(find('Yuan Dynasty',1371)['geometry']);ming_early=shape(find('Ming Dynasty',1375)['geometry'])
 provinces={f['properties']['iso_3166_2']:shape(f['geometry'])for f in read('.local/ne_10m_admin_1_states_provinces.geojson')['features']if f['properties'].get('admin')=='China'}
 masks=lambda codes:union_all([provinces['CN-'+code]for code in codes.split()])
 sichuan=ming_late.intersection(masks('SC CQ'));shaanxi=ming_late.intersection(masks('SN NX'));gansu=ming_late.intersection(masks('GS'))
 liaoning=ming_late.intersection(masks('LN'));northeast=ming_late.intersection(masks('JL HL'))
 yunnan=clean(ming_late.difference(ming_early).intersection(masks('YN GZ')))
 # Include Yuan's Yunnan remnant, clipped to the later Ming footprint to avoid
 # expanding the patch into neighbouring polities or inventing a border in Tibet.
 yunnan=clean(union_all([yunnan,ming_late.intersection(masks('YN'))]))
 def row(name,label,qid,g,a,b,note,source=MING_SOURCE,**extra):
  g=clean(g)
  if g.is_empty:return None
  props={'NAME':name,'SUBJECTO':name,'qid':qid,'entityId':qid or name,'validFrom':a,'validTo':b,'source':'Cliopatria + 有史料的年代修订','sourceUrl':source,'sourceRecord':f'{PATCH}:{name}:{a}:{b}','chronologyPatch':PATCH,'displayName':label,'accuracy':note,'temporalResolution':'event-dated-reconstruction','yearConvention':'年末代表状态；年内转移和战线仅概化显示','geometryMethod':'历史政权轮廓与现代地理区遮罩组合；不是精确历史行政界','labelPath':label_path(g,label),**extra}
  return {'type':'Feature','properties':props,'geometry':mapping(g)}
 stages=[]
 for a,b in [(1368,1368),(1369,1369),(1370,1370),(1371,1381),(1382,1386),(1387,1401)]:
  withheld=[northeast]if a<1387 else []
  if a<1371:withheld += [sichuan,liaoning]
  if a<1369:withheld += [shaanxi]
  if a<1370:withheld += [gansu]
  if a<1382:withheld += [yunnan]
  mg=clean(ming_late.difference(union_all(withheld)))
  north_extra=[northeast]if a<1387 else []
  if a<1371:north_extra.append(liaoning)
  if a<1369:north_extra.append(shaanxi)
  if a<1370:north_extra.append(gansu)
  ng=clean(union_all([north,*north_extra]).difference(mg))
  note='按1368年明建国及北伐、1369年入陕、1370年西北战事、1371年平夏与进入辽东、1382年云南归明、1387年纳哈出降附分期概化重建。边缘轮廓采用历史GIS与现代地理遮罩，不代表逐年测绘或全部驻军实际控制。'
  stages += [row('Ming Dynasty','明朝','Q9903',mg,a,b,note),row('Northern Yuan','北元','Q8959',ng,a,b,note)]
  if a<1382:stages.append(row('Yuan remnants in Yunnan','云南梁王政权','local:yuan-yunnan',yunnan,a,b,'云南元朝残余势力由梁王把匝剌瓦尔密等维持，1381年底至1382年被明军击败。轮廓用后期明朝云南部分概化重建，不表示与北元构成连续统一控制区。',source='https://so06.tci-thaijo.org/index.php/pub_jss/article/download/157701/114216/431563'))
  if a<1371:stages.append(row('Ming Xia','明夏','local:ming-xia',sichuan,a,b,'四川明氏夏政权至1371年被明征服；使用四川、重庆地理区与历史GIS相交概化，不是精确夏国疆界。'))
 stages=[f for f in stages if f]
 for century in [13,14]:
  kept=[]
  for f in data[century]['features']:
   p=f['properties']
   if p['NAME']in['Ming Dynasty','Northern Yuan','Yuan Dynasty'] and p['validFrom']<=1401 and p['validTo']>=1368:
    if p['validFrom']<1368:
     f=copy.deepcopy(f);f['properties']['validTo']=1367;kept.append(f)
    if p['validTo']>1401:
     f=copy.deepcopy(f);f['properties']['validFrom']=1402;kept.append(f)
   else:kept.append(f)
  kept.extend(f for f in stages if f['properties']['validFrom']<=century*100+99 and f['properties']['validTo']>=century*100)
  data[century]['features']=kept
 # Modern Mongolia is not Yuan. The missing 1921 revolution and 1924 republic
 # are split at their actual years, with 1919–20 Chinese control kept explicit.
 modern=data[19]['features'];mongol=next(f for f in modern if f['properties']['NAME']=='Great Mongol State'and f['properties']['validFrom']==1922)
 mongol_geometry=shape(mongol['geometry']);modern_rows=[]
 china1914=next(f for f in modern if f['properties']['NAME']=='Republic of China'and f['properties']['validFrom']==1914)
 # Include the adjoining Inner Mongolian part (notably Hulunbuir), otherwise
 # modern province masks leave an artificial unowned hole inside the northeast.
 northeast1914=clean(shape(china1914['geometry']).intersection(masks('LN JL HL NM')))
 for f in modern:
  p=f['properties']
  if p['NAME']=='Great Mongol State':continue
  if p['NAME']=='Kuomintang' and p['validFrom']<=1929:
   f=copy.deepcopy(f);q=f['properties'];q.update(sourceName=p['NAME'],sourceQid=p['qid'],NAME='Republic of China',SUBJECTO='Republic of China',qid='Q13426199',entityId='Q13426199',displayName='中华民国',identityReviewed=True,identitySource='https://www.wikidata.org/wiki/Q13426199',accuracy='中华民国时期的概化国家轮廓。1916—1928年存在北洋政府、地方军阀及南方政府并立；该填色不表示全国都受国民党或中央政府直接控制。');q.pop('labelPath',None)
  if f['properties']['NAME']=='Republic of China'and 1917<=p['validFrom']<=1929:
   f=copy.deepcopy(f);f['geometry']=mapping(clean(union_all([shape(f['geometry']),northeast1914])));q=f['properties'];q.pop('labelPath',None)
   q.update(regionalControlNote='东北主要由奉系军事势力控制；1928年后为张学良主导。地图此处采用国家范围口径，不表示中央政府直接统治，也不代表所有军阀分界。',regionalControlSource='https://scholars.hkbu.edu.hk/en/publications/war-and-geopolitics-in-interwar-manchuria-zhang-zuolin-and-the-fe/',geometryMethod='缺失东北部分采用1914年中华民国历史轮廓与现代地理区相交补绘，保留原有租借地区空缺；不代表逐年实际驻军范围',temporalResolution='source-outline-reconstruction',yearConvention='所选年度的国家范围概化；地方实际控制另作说明')
  # Earlier source country outlines absorb occupied Mongolia; partition around
  # the separately represented authority so no point receives two owners.
  if p['NAME']in['Republic of China','Kuomintang','Qing Dynasty'] and p['validFrom']<=1925 and p['validTo']>=1911:
   pieces=[];a,b=f['properties']['validFrom'],f['properties']['validTo'];stops=sorted({a,b+1,max(a,1911),min(b+1,1926)})
   for start,end in zip(stops,stops[1:]):
    if start>end-1:continue
    part=copy.deepcopy(f);part['properties'].update(validFrom=start,validTo=end-1)
    if 1911<=start<=1925:part['geometry']=mapping(clean(shape(part['geometry']).difference(mongol_geometry)));part['properties'].pop('labelPath',None)
    if not shape(part['geometry']).is_empty:pieces.append(part)
   modern_rows.extend(pieces)
  else:modern_rows.append(f)
 for a,b in [(1911,1914),(1915,1918),(1919,1920),(1921,1923),(1924,1925)]:
  if a==1919:
   f=row('Chinese administration in Outer Mongolia','外蒙古（北洋军控制）','Q13426199',mongol_geometry,a,b,'1919年自治被撤销，至1921年政权多次更替。边界沿用相邻年份蒙古地理轮廓；并非逐日驻军范围。',MONGOL_SOURCE,controlArea=True,id='outer-mongolia-1919',controlId='outer-mongolia-1919',controller='Republic of China',sovereignName='Bogd Khanate of Mongolia',kind='occupation',timelineNote='1919年末—1920年的代表控制状态')
  elif a>=1924:f=row("Mongolian People's Republic",'蒙古','Q212056',mongol_geometry,a,b,'1924年11月宣布成立蒙古人民共和国；年度地图按年末代表状态显示。边界沿用相邻时期历史GIS，不是1924年新测国界。',MONGOL_SOURCE)
  else:f=row('Bogd Khanate of Mongolia','博克多汗国','Q2475921',mongol_geometry,a,b,'1911年建立博克多汗国；1915年起为自治阶段，1919年自治被取消。1921年革命后博克多汗仍任君主，1924年改共和国。此区域采用相邻时期历史轮廓概化，外交承认和实际控制并不等同。',MONGOL_SOURCE)
  modern_rows.append(f)
 data[19]['features']=modern_rows
 for c,fc in data.items():write(f'public/data/temporal/{c}.geojson',fc)
 # Labels independent of wrongly associated Wikidata entities.
 labels=read('src/localization/display-names.zh.json')
 for r in corrections:
  if sum(x['name']==r['name']for x in corrections)==1:labels[r['name']]=r['label']
  if r.get('canonicalName'):labels[r['canonicalName']]=r['label']
 labels.update({'Bogd Khanate of Mongolia':'博克多汗国','Great Mongol State':'博克多汗国','Great Yuan':'大宛','Yuan remnants in Yunnan':'云南梁王政权','Ming Xia':'明夏','Chinese administration in Outer Mongolia':'外蒙古（北洋军控制）','Kuomintang':'中华民国'})
 write('src/localization/display-names.zh.json',labels)
 curated=read('public/data/curated-facts.json');curated['identities'].update({'Bogd Khanate of Mongolia':'Q2475921','Yuan remnants in Yunnan':'local:yuan-yunnan','Ming Xia':'local:ming-xia'})
 curated['polities']['Q9903']['summary']='明朝为朱氏皇朝，于1368年建立。洪武时期逐步完成四川、云南等地的征服；后续疆域、首都及边疆控制随时代变化。统治者与首都按所选年份筛选。'
 for r in corrections:
  if sum(x['name']==r['name']for x in corrections)==1:
   ids={f['properties'].get('qid')for fc in data.values()for f in fc['features']if f['properties']['NAME']==r['name']}
   if ids=={r['qid']}:curated['identities'][r['name']]=r['qid']
   else:curated['identities'].pop(r['name'],None)
  if r.get('canonicalName'):curated['identities'][r['canonicalName']]=r['qid']
 curated['polities']['Q2475921']={'label':'博克多汗国','source':MONGOL_SOURCE,'summary':'1911年建立的蒙古政权，1915—1919年处于自治阶段。1921年革命后人民政府执政、博克多汗保留君主地位，1924年改为人民共和国。不能与13—14世纪元朝混为一谈。','rulers':[[1911,1919,'博克多汗'],[1921,1924,'博克多汗']],'rulersSource':MONGOL_SOURCE,'facts':[{'field':'government','value':'君主制；1915年起为自治阶段','from':1911,'to':1919},{'field':'government','value':'人民政府执政，博克多汗为立宪君主','from':1921,'to':1924},{'field':'religion','value':'藏传佛教格鲁派具有重要政治地位','from':1911,'to':1924},{'field':'capital','value':'库伦（今乌兰巴托）','from':1911,'to':1924}]}
 curated['polities']['local:yuan-yunnan']={'label':'云南梁王政权','source':MING_SOURCE,'summary':'元朝退出大都后，云南梁王等残余势力继续存在，至1382年被明军击败。不可据此把明朝统治的中国本部继续涂成元朝。','rulers':[[1368,1381,'梁王 把匝剌瓦尔密']],'rulersSource':MING_SOURCE,'facts':[{'field':'capital','value':'中庆路（今昆明）','from':1368,'to':1381}]}
 curated['polities']['local:ming-xia']={'label':'明夏','source':MING_SOURCE,'summary':'明玉珍建立的四川割据政权，明昇继位后于1371年降明；名称中的明是统治家族姓氏，与朱氏明朝有别。','rulers':[[1366,1370,'明昇']],'rulersSource':MING_SOURCE,'facts':[{'field':'capital','value':'重庆','from':1362,'to':1370}]}
 write('public/data/curated-facts.json',curated)
 index=read('public/data/temporal/index.json');records={f['properties']['sourceRecord']for fc in data.values()for f in fc['features']};index['counts']['polityRecords']=len(records)
 index['changeYears']=sorted({y for fc in data.values()for f in fc['features']for y in [f['properties']['validFrom'],f['properties']['validTo']+1]})
 index['chronologyRevision']=PATCH;index['yearlyQuery']=True;index['refinementPolicy']='逐年查询有效期；事件年份切换已核实分期。无新几何时沿用有来源轮廓，不线性推演国界。'
 write('public/data/temporal/index.json',index)
 catalog.update({'revision':PATCH,'identityRowsChanged':dict(changed),'reconstruction':{'region':'中国与蒙古','from':1368,'to':1401,'changeYears':[1368,1369,1370,1371,1382,1387],'modernMongolia':[1911,1915,1919,1921,1924],'geometryPrecision':'历史GIS轮廓 + 现代地理区遮罩的概化重建；不能视为逐年精确边界','sources':[MING_SOURCE,MONGOL_SOURCE,'https://www11.ihp.sinica.edu.tw/storage/w2_file/4004qxQPgzA.pdf']}})
 write('public/data/chronology-corrections.json',catalog)
 print(json.dumps({'reviewedRules':len(corrections),'affectedRows':sum(changed.values()),'uniqueRecords':len(records),'regionalStates':len(stages)},ensure_ascii=True),flush=True)
if __name__=='__main__':main()
