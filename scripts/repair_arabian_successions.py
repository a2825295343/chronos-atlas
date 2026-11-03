"""Separate successive Najdi states rather than keeping the second until 1925."""
import copy,hashlib,json
from pathlib import Path
from territory_repair_stage import clean,label_path
from shapely import union_all
from shapely.geometry import shape,mapping
ROOT=Path(__file__).resolve().parents[1]
TAG='arabian-successions-2026-11-01'
SOURCE='https://www.qdl.qa/en/historical-profile-saudi-arabia'
PHASES=[
 (1824,1890,'Emirate of Nejd','内志酋长国','Q146862'),
 (1891,1901,'Emirate of Jabal Shammar','杰贝勒舍迈尔酋长国','local:jabal-shammar'),
 (1902,1912,'Emirate of Riyadh','利雅得酋长国','local:riyadh-emirate'),
 (1913,1920,'Emirate of Nejd and Hasa','内志与哈萨酋长国','local:nejd-hasa'),
 (1921,1925,'Sultanate of Nejd','内志苏丹国','local:nejd-sultanate'),
]
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def main():
 records=[]
 for c in range(14,21):
  path=f'public/data/temporal/{c}.geojson';data=read(path);out=[];changed=False
  for f in data['features']:
   p=f['properties'];name=p['NAME']
   if p.get('arabianPhaseReview')==TAG or name not in ['Emirate of Nejd','Kingdom of Hejaz and Nejd']:out.append(f);continue
   ranges=PHASES if name=='Emirate of Nejd'else[(1926,1931,name,'汉志与内志王国','Q1756546'),(1932,2024,'Saudi Arabia','沙特阿拉伯','Q851')]
   for lo,hi,n,label,q in ranges:
    a,b=max(lo,p['validFrom']),min(hi,p['validTo'])
    if a>b or a>(c+1)*100-1 or b<c*100:continue
    row=copy.deepcopy(f);r=row['properties'];r.update(NAME=n,SUBJECTO=n,displayName=label,qid=q,entityId=q,validFrom=a,validTo=b,sourceName=p.get('sourceName',name),sourceQid=p.get('sourceQid',p.get('qid')),arabianPhaseReview=TAG,identityCorrection='区分第二沙特国家、拉希德统治、1902年后的利雅得／内志诸阶段及1932年统一王国。原始几何仅作年度概览，不能代表实际控制始终不变。',sourceUrl=SOURCE,sourceRecord=str(p['sourceRecord'])+':'+TAG+':'+str(a)+':'+str(b));out.append(row);changed=True;records.append({'from':a,'to':b,'name':n,'label':label})
   if not any(max(lo,p['validFrom'])<=min(hi,p['validTo'])for lo,hi,*_ in ranges):out.append(f)
  if changed:data['features']=out;write(path,data)
 # A renamed Najdi outline and the existing Ha'il core are pieces of the same
 # Rashidi state. Merge their contemporaneous extents; selecting one by NAME
 # would otherwise discard the larger outline and create a new blank area.
 shards={c:read(f'public/data/temporal/{c}.geojson')for c in [18,19]};pieces={}
 for d in shards.values():
  for f in d['features']:
   p=f['properties']
   if p['NAME']=='Emirate of Jabal Shammar'and p['validFrom']<=1901 and p['validTo']>=1891:pieces[(str(p['sourceRecord']),p['validFrom'],p['validTo'])]=f
 if pieces:
  stops=sorted({1891,1902,*[y for f in pieces.values()for y in [max(1891,f['properties']['validFrom']),min(1902,f['properties']['validTo']+1)]]});merged=[]
  for a,end in zip(stops,stops[1:]):
   active=[f for f in pieces.values()if f['properties']['validFrom']<=a<=f['properties']['validTo']]
   if not active:continue
   f=copy.deepcopy(active[-1]);g=clean(union_all([shape(r['geometry'])for r in active]));f['geometry']=mapping(g);f['properties'].update(validFrom=a,validTo=end-1,sourceRecord=TAG+':rashidi-combined:'+str(a)+':'+str(end-1),arabianPhaseReview=TAG,representationNote='此阶段包括哈伊勒核心与拉希德家族控制的内志诸地；部族联系与沙漠地域不等于全年持续的直接行政控制。',labelPath=label_path(g,'杰贝勒舍迈尔酋长国'));merged.append(f)
  for c,d in shards.items():
   out=[]
   for f in d['features']:
    p=f['properties']
    if p['NAME']!='Emirate of Jabal Shammar'or p['validTo']<1891 or p['validFrom']>1901:out.append(f);continue
    for a,b in [(p['validFrom'],min(1890,p['validTo'])),(max(1902,p['validFrom']),p['validTo'])]:
     if a<=b and a<=(c+1)*100-1 and b>=c*100:r=copy.deepcopy(f);r['properties'].update(validFrom=a,validTo=b);out.append(r)
   out.extend(f for f in merged if f['properties']['validFrom']<=(c+1)*100-1 and f['properties']['validTo']>=c*100);d['features']=out;write(f'public/data/temporal/{c}.geojson',d)
 facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json');labels={n:l for _,_,n,l,_ in PHASES};labels['Saudi Arabia']='沙特阿拉伯';labels['Kingdom of Hejaz and Nejd']='汉志与内志王国'
 for a,b,n,l,q in PHASES:
  cur['identities'][n]=q
  if not q.startswith('local:nejd')and q!='local:riyadh-emirate':continue
  e=facts['entities'].setdefault(q,{'label':l,'en':n,'description':'阿卜杜勒阿齐兹统治下形成的分阶段政权，不能沿用1891年已终结的第二沙特国家身份。','fields':{}});facts['labels'][q]=l
  def fact(value,label,field):return {'value':value,'label':label,'from':a,'to':b,'at':None,'citation':[SOURCE,'https://www.wikidata.org/wiki/Q151509'],'supplement':TAG,'roleLabel':field}
  e['fields']['ruler']=[fact('Q151509','阿卜杜勒阿齐兹·本·沙特','埃米尔／苏丹（称号按阶段变化）')]
  e['fields']['government']=[fact('monarchical-emirate','埃米尔／苏丹王权与宗教、绿洲及部族网络构成的政权','政体')]
  e['fields']['capital']=[fact('riyadh','利雅得','政治中心')]
  e['fields']['religion']=[fact('sunni-court','逊尼派伊斯兰教王室礼制与宗教改革传统；不等同所有居民或每处地方的信仰完全一致','宗教与礼制')]
 cur['identities']['Saudi Arabia']='Q851';write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur)
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(path);d.update(labels);write(path,d)
 index=read('public/data/temporal/index.json');allrows=[f for c in index['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']];index['counts']['polityRecords']=len({f['properties']['sourceRecord']for f in allrows});index['changeYears']=sorted(set(index['changeYears'])|{1891,1902,1913,1921,1926,1932});index['arabianSuccessionRevision']=TAG;write('public/data/temporal/index.json',index)
 current={(p['NAME'],p['validFrom'],p['validTo']):{'name':p['NAME'],'label':p.get('displayName'),'from':p['validFrom'],'to':p['validTo']}for f in allrows if(p:=f['properties']).get('arabianPhaseReview')==TAG}
 write('public/data/arabian-succession-review.json',{'reviewedAt':'2026-11-01','records':list(current.values()),'source':SOURCE,'limitations':['纠正身份与有效时期，不把原图几何的保留解释为已完成逐月战争控制线复原。']});print('Arabian succession records refined',len(current),flush=True)
if __name__=='__main__':main()
