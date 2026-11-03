"""Correct named office/person, colonial flag dates and swapped source geometry.
Edits current data in place; repeat calls detect repaired geometry and never swap
it back. Run after territory stages if rebuilding upstream period shards.
"""
import copy,json,re,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely import make_valid,union_all
from shapely.geometry import shape,mapping,box
from prepare_political_presentation import label_path
TAG='archive-identity-geometry-2026-10-31'
CEYLON='https://tile.loc.gov/storage-services/master/frd/frdcstdy/sr/srilankacountrys00ross/srilankacountrys00ross.pdf'
INDIES='https://library.si.edu/image-gallery/101376'
IRAN='https://www.unesco.org/en/memory-world/collection-selected-maps-iran-qajar-era-1193-1344-lunar-calendar/1779-1926-gregorian-calendar'
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def main():
 report=read('public/data/archive-identity-review.json')if(ROOT/'public/data/archive-identity-review.json').exists()else{'reviewedAt':'2026-10-31','revision':TAG,'geometry':[],'flagDateCorrections':[],'ceylonPeriods':[]}
 # Flags with dates in their actual file names are not timeless assets.
 flags=read('public/data/flags.json')
 for q,rows in flags['entities'].items():
  for r in rows:
   m=re.search(r'\((1\d{3}|20\d{2})[–—-](1\d{3}|20\d{2})\)',r.get('file',''))
   if m and r.get('from')is None and r.get('to')is None and r.get('at')is None:
    r.update({'from':int(m[1]),'to':int(m[2]),'periodSource':r.get('commons'), 'periodNote':'按原图明确记载的旗式年代限定；不向更早的同地前身政权回填。'})
    report['flagDateCorrections'].append({'qid':q,'file':r['file'],'from':r['from'],'to':r['to']})
 write('public/data/flags.json',flags)
 cur=read('public/data/curated-facts.json');facts=read('public/data/polity-facts.json');labels={}
 admin=read('.local/ne_10m_admin_1_states_provinces.geojson')['features']
 central=union_all([shape(f['geometry'])for f in admin if f['properties']['admin']=='Sri Lanka'and f['properties'].get('region')=='Madhyama paḷāta'])
 for c in [12,13,14,15]:
  path=f'public/data/temporal/{c}.geojson'
  if not(ROOT/path).exists():continue
  data=read(path);out=[]
  for f in data['features']:
   p=f['properties']
   highland_missing=p['NAME']=='Kingdom of Kotte'and p['validFrom']>=1469 and p['validTo']<=1506 and not any(x['properties']['NAME']=='Kingdom of Kandy'and x['properties']['validFrom']<=p['validFrom']<=x['properties']['validTo']for x in data['features'])
   if (p['NAME']!='Ceylon'and not highland_missing)or p['validFrom']>1506:out.append(f);continue
   stops=sorted({p['validFrom'],p['validTo']+1}|{y for y in [1273,1293,1341,1412,1469]if p['validFrom']<y<=p['validTo']})
   for a,b in zip(stops,stops[1:]):
    n,label,q=('Kingdom of Kotte','科提王国','local:kingdom-of-kotte')if a>=1412 else('Sinhalese Successor Kingdoms','僧伽罗诸王国','local:sinhalese-successor-kingdoms')
    g=make_valid(shape(f['geometry']));other=[shape(x['geometry'])for x in data['features']if x['properties']['NAME']=='Jaffna kingdom'and x['properties']['validFrom']<=a<=x['properties']['validTo']]
    if other:g=make_valid(g.difference(union_all(other)))
    pieces=[(n,label,q,g)]
    if a>=1469 and not central.is_empty:
     highlands=make_valid(g.intersection(central));g=make_valid(g.difference(central));pieces=[(n,label,q,g),('Kingdom of Kandy','康提王国','local:kingdom-of-kandy',highlands)]
    for n,label,q,g in pieces:
     if g.is_empty:continue
     props=copy.deepcopy(p);props.update(NAME=n,SUBJECTO=n,displayName=label,qid=q,entityId=q,sourceQid='Q918153',identityReviewed=True,validFrom=a,validTo=b-1,sourceUrl=CEYLON,sourceRecord=TAG+':'+hashlib.sha1(f'{p["sourceRecord"]}|{n}|{a}|{b}'.encode()).hexdigest()[:16],identityCorrection='原Ceylon错误关联英属锡兰；改按欧洲殖民前的当地政权分期，不采用19世纪英国殖民旗。',temporalResolution='reviewed-ceylon-period',accuracy='1236—1411年为首都与王权变化频繁的僧伽罗诸王国概览；1412年起区分科提，1469年起另示康提高地。康提内界使用地理区概化，不冒充当年精确国界。保留贾夫纳已有轮廓。',geometryMethod='源锡兰轮廓减去同时期贾夫纳；康提高地以地理区辅助定位。',labelPath=label_path(g,label),chronologyPatch=TAG)
     if a<1412:props.update(regionalCollection=True,representationNote='多个相继或并存的僧伽罗王国概览；不是英属殖民地，也不适用一位跨世纪共同君主。')
     out.append({'type':'Feature','properties':props,'geometry':mapping(g)});labels[n]=label;cur['identities'][n]=q
     report['ceylonPeriods'].append({'name':n,'from':a,'to':b-1,'source':CEYLON})
  data['features']=out;write(path,data)
 # Both source records for 1895–1897 were misassigned. Spatial components,
 # including the small Iranian remainder, are returned to their actual region.
 path='public/data/temporal/18.geojson';data=read(path)
 qajar=[f for f in data['features']if f['properties']['NAME']=='Qajar Dynasty'and f['properties']['validFrom']==1895 and f['properties']['validTo']==1897]
 dutch=[f for f in data['features']if f['properties']['NAME']=='Dutch East Indies'and f['properties']['validFrom']==1895 and f['properties']['validTo']==1897]
 if len(qajar)!=1 or len(dutch)!=1:raise ValueError('Expected one source record per swapped polity')
 qa,de=qajar[0],dutch[0];qg,dg=shape(qa['geometry']),shape(de['geometry'])
 if qg.representative_point().x>85 and dg.representative_point().x<75:
  both=make_valid(union_all([qg,dg]));iran=make_valid(both.intersection(box(40,20,66,43)));indies=make_valid(both.intersection(box(90,-15,145,12)))
  if iran.area<50 or indies.area<50:raise ValueError('Swapped geometry failed geographical checks')
  for f,g,label,source in [(qa,iran,'伊朗',IRAN),(de,indies,'荷属东印度',INDIES)]:
   p=f['properties'];report['geometry'].append({'name':p['NAME'],'from':1895,'to':1897,'beforeBounds':list(shape(f['geometry']).bounds),'afterBounds':list(g.bounds),'source':source})
   f['geometry']=mapping(g);p.update(displayName=label,geometryCorrection='1895—1897年源记录把伊朗与荷属东印度的轮廓互换；按两记录的空间组成归还，不改变邻国。',sourceUrl=source,accuracy='修正原始标签／几何错配；保留源GIS1895—1897年时期轮廓的概化精度，非重新划定殖民地或伊朗边界。',temporalResolution='corrected-source-geometries',labelPath=label_path(g,label))
  write(path,data)
 # A geographical name is retained in the archive, not confused with a family.
 names=read('src/localization/display-names.zh.json');names.update(labels);names['Qajar Dynasty']='伊朗';write('src/localization/display-names.zh.json',names)
 names=read('src/localization/temporal.zh.json');names.update(labels);write('src/localization/temporal.zh.json',names)
 for q,label,name in [('local:kingdom-of-kotte','科提王国','Kingdom of Kotte'),('local:kingdom-of-kandy','康提王国','Kingdom of Kandy'),('local:sinhalese-successor-kingdoms','僧伽罗诸王国','Sinhalese Successor Kingdoms')]:
  facts['entities'].setdefault(q,{'label':label,'en':name,'description':'欧洲殖民前的锡兰当地政权；与后来的英属锡兰分开。','fields':{}});facts['labels'][q]=label
 write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur)
 idx=read('public/data/temporal/index.json');allrows=[f for c in idx['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']];idx['counts']['polityRecords']=len({f['properties']['sourceRecord']for f in allrows});idx['changeYears']=sorted(set(idx['changeYears'])|{1273,1293,1341,1412,1469,1507,1895,1898});write('public/data/temporal/index.json',idx)
 write('public/data/archive-identity-review.json',report);print('Flag dates',len(report['flagDateCorrections']),'Ceylon periods',len(report['ceylonPeriods']),'geometry corrections',len(report['geometry']),flush=True)
if __name__=='__main__':main()
