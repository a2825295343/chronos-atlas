"""Replace period identities by courts, bakufu and sourced daimyo cores.

Kuni-based clan cores are explicitly generalized; sub-province castle control
is not inferred from the colour of an entire historical province.
"""
import copy,json,hashlib
from collections import defaultdict
from territory_repair_stage import ROOT,read,write,clean
from prepare_political_presentation import label_path
from shapely.geometry import shape,mapping,box
from shapely import union_all
TAG='japanese-polities-2026-11-01';CACHE=ROOT/'.local/japanese-polities';CACHE.mkdir(exist_ok=True)
SOURCE='https://www.japan-guide.com/e/e2123.html'
NII='https://geoshape.ex.nii.ac.jp/kg/index.html.ja'
CREDIT='『旧国・旧郡境界データセット』（CODH作成）「幕末明治地勢地図境界データ」（人間文化研究機構作成）を加工 doi:10.20676/00000454'
TARGET={'Asuka Japan','Nara Japan','Heian Japan','Warring States Japan','Tokugawa Shogunate'}

def main():
 index=read('public/data/temporal/index.json');original=CACHE/'original-target-rows.json'
 if not original.exists():
  found={}
  for c in index['centuries']:
   for f in read(f'public/data/temporal/{c}.geojson')['features']:
    p=f['properties']
    if p['NAME']in TARGET:found[(str(p['sourceRecord']),p['NAME'],p['validFrom'],p['validTo'])]=f
  original.write_text(json.dumps(list(found.values()),ensure_ascii=False),encoding='utf8')
 base=json.loads(original.read_bytes());provs=read('public/data/japan-old-provinces.geojson')['features'];kuni={f['properties']['id']:shape(f['geometry'])for f in provs};defs={};new=[]
 def kg(*ids):return clean(union_all([kuni[k]for k in ids]))
 # [first,last,actor key,label,kuni]. Core provincial influence, not exhaustive castle lists.
 specs=[(1468,1599,'Shimazu','岛津氏',kg('K71')),(1574,1599,'Shimazu','岛津氏',kg('K70')),(1468,1573,'Kimotsuki','肝付氏',kg('K70')),
 (1468,1556,'Ouchi','大内氏',kg('K55','K56')),(1557,1599,'Mori','毛利氏',kg('K55','K56')),(1555,1599,'Mori','毛利氏',kg('K54')),(1566,1599,'Mori','毛利氏',kg('K46','K47')),(1508,1565,'Amago','尼子氏',kg('K46')),
 (1468,1592,'Otomo','大友氏',kg('K66')),(1559,1582,'Oda','织田氏',kg('K09')),(1583,1589,'Oda','织田氏',kg('K09')),(1542,1566,'Saito','斋藤氏',kg('K22')),(1567,1582,'Oda','织田氏',kg('K22')),
 (1468,1581,'Takeda','武田氏',kg('K13')),(1468,1568,'Imagawa','今川氏',kg('K12')),(1569,1581,'Takeda','武田氏',kg('K12')),
 (1560,1589,'Tokugawa','德川氏',kg('K10')),(1582,1589,'Tokugawa','德川氏',kg('K13','K12')),(1493,1589,'Go-Hojo','后北条氏',kg('K14')),(1495,1589,'Go-Hojo','后北条氏',kg('K15')),(1551,1589,'Go-Hojo','后北条氏',kg('K16')),(1590,1599,'Tokugawa','德川氏',kg('K14','K15','K16')),
 (1507,1560,'Nagao','长尾氏',kg('K39')),(1561,1597,'Uesugi','上杉氏',kg('K39')),(1598,1599,'Hori','堀氏',kg('K39')),
 (1575,1599,'Chosokabe','长宗我部氏',kg('K62')),
 (1468,1590,'Date','伊达氏',clean(kg('K32').intersection(box(139.4,37.5,141,38.5)))),(1591,1599,'Date','伊达氏',clean(kg('K29').intersection(box(140.3,37.8,142,39)))),
 (1573,1582,'Oda','织田氏',kg('K01','K21')),(1583,1585,'Hashiba','羽柴政权',kg('K01','K03','K04','K05','K21','K22')),(1586,1599,'Toyotomi','丰臣政权',kg('K01','K03','K04','K05','K21','K22'))]
 phases=sorted({1468,1600,*[y for a,b,k,l,g in specs for y in [a,b+1]]})
 def actor(k):return 'Japanese clan - '+k
 def qid(k):return 'local:jp-'+('toyotomi'if k=='Hashiba'else k.lower())
 def make(f,n,l,q,a,b,g,note,**props):
  r=copy.deepcopy(f);p=r['properties'];p.update(sourceQid=p.get('sourceQid',p.get('qid')),sourceName=p.get('sourceName',p['NAME']),NAME=n,SUBJECTO=n,qid=q,entityId=q,displayName=l,validFrom=a,validTo=b,sourceRecord=TAG+':'+hashlib.sha1(f'{n}|{a}|{b}|{f["properties"]["sourceRecord"]}'.encode()).hexdigest()[:17],sourceUrl=SOURCE,japanesePolityReview=TAG,representationNote=note,accuracy=note,**props);r['geometry']=mapping(g);p['labelPath']=label_path(r['geometry'],l);new.append(r)
  if n.startswith('Japanese '):p.update(boundarySource=NII,credit=CREDIT,license='CC BY-NC 4.0')
  if q=='local:japanese-imperial-court':p['sourceUrl']='https://www.britannica.com/place/Japan/History'
  d=defs.setdefault(n,{'label':l,'qid':q,'from':a,'to':b,'note':note,'source':p['sourceUrl']});d['from']=min(a,d['from']);d['to']=max(b,d['to']);return r
 for f in base:
  p=f['properties'];n=p['NAME'];a,b=p['validFrom'],p['validTo'];g=shape(f['geometry'])
  if n in ['Asuka Japan','Nara Japan','Heian Japan']:
   make(f,n,'大和朝廷'if n=='Asuka Japan'else'日本朝廷','local:japanese-imperial-court',a,b,g,'地图显示大和王权／日本朝廷；飞鸟、奈良、平安是历史分期与都城语境，不是独立国家名称。原图轮廓仍为分期概览。');continue
  if n=='Tokugawa Shogunate':
   for lo,hi,name,label,q in [(1600,1602,'Tokugawa Government','德川政权','local:tokugawa-government'),(1603,1867,n,'德川幕府','Q205662')]:
    x,y=max(lo,a),min(hi,b)
    if x<=y:make(f,name,label,q,x,y,g,'1600年关原战后德川势力与1603年正式开幕分开；幕府不延续至1869年。藩与幕府的关系不等于所有领地均由将军直接治理。')
   continue
  if n!='Warring States Japan':continue
  for lo,end in zip(phases,phases[1:]):
   x,y=max(a,lo),min(b,end-1,1599)
   if x>y:continue
   assigned=defaultdict(list);labels={};used=[]
   for first,last,k,l,core in specs:
    if not first<=x<=last:continue
    part=clean(g.intersection(core).difference(union_all(used)))
    if part.is_empty or part.area<.0001:continue
    assigned[k].append(part);labels[k]=l;used.append(part)
   for k,gs in assigned.items():
    note='据主要领国与当主活动分期的势力核心概化；用幕末旧国轮廓作空间参考，不代表整国每座城或所有国人均被该家直接控制。'
    props={'representationKind':'polity','inferredBoundary':True}
    if x>=1590 and k not in ['Toyotomi','Hashiba']:props.update(sovereignName=actor('Toyotomi'),sovereignQid='local:jp-toyotomi',territoryType='member',partitionBasis='丰臣全国秩序中的大名领国；保留自身家政、领地与军队，不当作独立国家。')
    make(f,actor(k),labels[k],qid(k),x,y,clean(union_all(gs)),note,**props)
   rest=clean(g.difference(union_all(used)))
   for key,l,region in [('tohoku','奥羽诸大名',box(138,37.4,147,45)),('kanto','关东诸势力',box(138.5,34.5,142,37.4)),('kinai','畿内与东海诸势力',box(134.5,33.3,138.5,37.4)),('chugoku','山阴山阳诸大名',box(130.7,33.8,134.5,36.8)),('shikoku','四国诸大名',box(132,32.5,135,33.8)),('kyushu','九州诸大名',box(127,30,132,34.5))]:
    part=clean(rest.intersection(region))
    if part.is_empty:continue
    rest=clean(rest.difference(part));make(f,'Japanese regional - '+key,l,'local:jp-regional-'+key,x,y,part,'多个守护大名、战国大名、国人或寺社势力并存的地域概览，不是一个统一国家；尚未核定每个城和小领主的逐年控制。',regionalCollection=True,representationKind='regional-polities')
   if not rest.is_empty:make(f,'Japanese regional - other','日本地方诸势力','local:jp-regional-other',x,y,rest,'尚未逐领主核定的日本地方政治势力集合，不以“战国时代”作为国家名称。',regionalCollection=True,representationKind='regional-polities')
 # Replace only the saved Japanese target rows and this patch, preserving all
 # subsequent repairs in other countries and regions in shared century files.
 for c in index['centuries']:
  if c<5 or c>18:continue
  data=read(f'public/data/temporal/{c}.geojson');data['features']=[f for f in data['features']if f['properties']['NAME']not in TARGET and f['properties'].get('japanesePolityReview')!=TAG]+[f for f in new if f['properties']['validFrom']<(c+1)*100 and f['properties']['validTo']>=c*100];write(f'public/data/temporal/{c}.geojson',data)
 labels={n:d['label']for n,d in defs.items()};labels['Warring States Japan']='日本诸大名';labels['Tokugawa Shogunate']='德川幕府'
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(path);d.update(labels);write(path,d)
 facts=read('public/data/polity-facts.json');cur=read('public/data/curated-facts.json')
 ranges={}
 for d in defs.values():
  q=d['qid'];a,b=ranges.get(q,(d['from'],d['to']));ranges[q]=(min(a,d['from']),max(b,d['to']))
 done=set()
 for n,d in defs.items():
  q=d['qid'];cur['identities'][n]=q;facts['labels'][q]=d['label'];e=facts['entities'].setdefault(q,{'label':d['label'],'en':n,'description':d['note'],'fields':{}})
  if q=='Q205662'or q in done:continue
  done.add(q)
  for field,text in [('government','朝廷及律令官署'if q=='local:japanese-imperial-court'else'大名家政、家臣与领国统治'if n.startswith('Japanese clan')else'多个地方军政、国人和寺社组织并存'),('ruler','朝廷天皇与摄政等职务（人物任期仍需按年核定）'if q=='local:japanese-imperial-court'else d['label']+'的家督及地方首领（具体任期见具名补录）')]:
   rs=e['fields'].setdefault(field,[]);rs[:]=[r for r in rs if r.get('supplement')!=TAG];rs.append({'value':text,'label':text,'from':ranges[q][0],'to':ranges[q][1],'at':None,'kind':'collective','citation':[d['source']],'supplement':TAG})
 write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur)
 allrows=[f for c in index['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']];index['counts']['polityRecords']=len({f['properties']['sourceRecord']for f in allrows});index['changeYears']=sorted(set(index['changeYears'])|{p['validFrom']for f in new if(p:=f['properties'])}|{f['properties']['validTo']+1 for f in new});index['japanesePolityRevision']=TAG;write('public/data/temporal/index.json',index)
 write('public/data/japanese-polity-review.json',{'reviewedAt':'2026-11-01','definitions':defs,'newPeriods':len(new),'limitations':['领国核心采用旧国参考几何，未声称已复原所有城砦的年度控制图。','地域集合保持为多个势力，不补一个虚构的共同君主。','旧国边界来自幕末参考，早期边界变迁继续标注待核。']});print('Japanese political periods',len(new),'actors',len(defs),flush=True)

if __name__=='__main__':main()
