"""Shared staged, period-aware geometry repair; explicit regions only."""
import copy,hashlib,json,shutil,sys
from tempfile import NamedTemporaryFile
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely import make_valid,union_all
from shapely.geometry import shape,mapping
from shapely.strtree import STRtree
from prepare_political_presentation import label_path
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):
 path=ROOT/p
 with NamedTemporaryFile(mode='w',encoding='utf8',dir=path.parent,delete=False) as handle:
  temporary=Path(handle.name)
  try:
   handle.write(json.dumps(d,ensure_ascii=False,separators=(',',':')))
   handle.close()
   temporary.replace(path)
  finally:
   temporary.unlink(missing_ok=True)
def clean(g):
 if not g.is_valid:g=make_valid(g)
 if g.geom_type in ['Polygon','MultiPolygon']:return g
 return union_all([clean(x)for x in getattr(g,'geoms',[])if x.geom_type in ['Polygon','MultiPolygon','GeometryCollection']])
def overlaps(a,b):return a[0]<=b[2]and a[2]>=b[0]and a[1]<=b[3]and a[3]>=b[1]
class Stage:
 def __init__(self,tag,centuries):
  self.tag=tag;self.index=read('public/data/temporal/index.json');self.centuries=[c for c in self.index['centuries']if c in centuries]
  backup=ROOT/'.local'/tag/'original-shards';backup.mkdir(parents=True,exist_ok=True);rows={}
  for c in self.centuries:
   path=f'public/data/temporal/{c}.geojson';saved=backup/f'{c}.geojson'
   if not saved.exists():shutil.copyfile(ROOT/path,saved)
   for f in json.loads(saved.read_bytes())['features']:
    p=f['properties'];rows.setdefault((str(p['sourceRecord']),p['NAME'],p['validFrom'],p['validTo']),f)
  self.rows=list(rows.values());self.geoms=[shape(f['geometry'])for f in self.rows];self.tree=STRtree(self.geoms)
  self.replaced=defaultdict(list);self.new=[];self.audit=[];self.labels={};self.identities={};self.frames={}
 def periods(self,region,lo,hi,extra=()):
  stops={lo,hi+1,*[y for y in extra if lo<y<=hi]}
  for i in self.tree.query(region,predicate='intersects'):
   p=self.rows[int(i)]['properties']
   if p['validFrom']<=hi and lo<=p['validTo']:stops.update([max(lo,p['validFrom']),min(hi+1,p['validTo']+1)])
  # Prior regional changes also split subsequent repairs, avoiding a larger
  # period accidentally carrying a smaller period's ownership into other years.
  for f in self.new:
   p=f['properties']
   if p['validFrom']<=hi and lo<=p['validTo']and overlaps(shape(f['geometry']).bounds,region.bounds):stops.update([max(lo,p['validFrom']),min(hi+1,p['validTo']+1)])
  s=sorted(stops);return [(a,b-1)for a,b in zip(s,s[1:])]
 def world(self,year):
  rows={}
  for i,f in enumerate(self.rows):
   p=f['properties'];n=p['NAME']
   if not p['validFrom']<=year<=p['validTo']or any(a<=year<=b for a,b in self.replaced.get(n,[])):continue
   if n not in rows or(p['validFrom'],-p['validTo'])>(rows[n][0]['validFrom'],-rows[n][0]['validTo']):rows[n]=(p,self.geoms[i])
  for f in self.new:
   p=f['properties'];n=p['NAME']
   if p['validFrom']<=year<=p['validTo']and(n not in rows or(p['validFrom'],-p['validTo'])>=(rows[n][0]['validFrom'],-rows[n][0]['validTo'])):rows[n]=(p,shape(f['geometry']))
  return {n:[copy.deepcopy(p),g]for n,(p,g)in rows.items()}
 def repair(self,region,a,b,assignments,remove=()):
  w=self.world(a);dirty=set();removed=0
  for n,(p,g)in w.items():
   if n not in remove or not overlaps(g.bounds,region.bounds):continue
   cut=clean(g.intersection(region))
   if cut.area<1e-7:continue
   w[n][1]=clean(g.difference(region));dirty.add(n);removed+=cut.area
  occupied=clean(union_all([g.intersection(region)for p,g in w.values()if not g.is_empty and overlaps(g.bounds,region.bounds)]))
  for item in assignments:
   n,label,q,g,source,note,*extra=item;props=extra[0]if extra else{}
   g=clean(g.intersection(region).difference(occupied))
   if g.is_empty or g.area<.002:continue
   gap=g;old=w.get(n)
   if old:g=clean(union_all([old[1],g]));p=old[0]
   else:p={'NAME':n,'SUBJECTO':n,'qid':q,'entityId':q}
   p.update(NAME=n,SUBJECTO=n,displayName=label,qid=q,entityId=q,sourceUrl=source,accuracy=note,**props)
   if props.get('regionalCollection'):p['representationNote']=note
   w[n]=[p,g];dirty.add(n);occupied=clean(union_all([occupied,gap]));self.labels[n]=label;self.identities[n]=q
   self.audit.append({'name':n,'from':a,'to':b,'addedSquareDegrees':round(gap.area,7),'source':source,'sourceReferenceYear':props.get('sourceReferenceYear'),'inferred':True})
  if not dirty:return
  for n in sorted(dirty):
   p,g=w[n];self.replaced[n].append((a,b))
   if g.is_empty:continue
   p.update(validFrom=a,validTo=b,sourceRecord=self.tag+':'+hashlib.sha1(f'{n}|{a}|{b}'.encode()).hexdigest()[:16],chronologyPatch=self.tag,temporalResolution='sourced-gap-reconstruction',geometryMethod='按有效分期扣除已有政权，仅补有参考图源的空白；地理集合与推断边界明确标注。',labelPath=label_path(g,p.get('displayName',n)))
   p.setdefault('sourceUrl','https://github.com/Seshat-Global-History-Databank/cliopatria');p.setdefault('accuracy','仅扣去本轮重新分列的地区，保留原轮廓的其余部分。')
   self.new.append({'type':'Feature','properties':p,'geometry':mapping(g)})
 def finish(self,report_name='expanded-territory-review.json'):
  output=[]
  for f in self.rows:
   p=f['properties'];segments=[(p['validFrom'],p['validTo'])]
   for x,y in self.replaced.get(p['NAME'],[]):
    more=[]
    for a,b in segments:
     if y<a or x>b:more.append((a,b))
     else:
      if a<x:more.append((a,x-1))
      if y<b:more.append((y+1,b))
    segments=more
   for a,b in segments:
    if(a,b)==(p['validFrom'],p['validTo']):output.append(f)
    else:
     row=copy.deepcopy(f);row['properties'].update(validFrom=a,validTo=b);output.append(row)
  output+=self.new
  # Several regional cuts may refine the same whole-country year. Keep the
  # final version, as world() does, instead of publishing both intermediate
  # and final geometries under an identical source record.
  keyed={}
  for f in output:
   p=f['properties'];key=(str(p['sourceRecord']),p['NAME'],p['validFrom'],p['validTo']);keyed[key]=f
  output=list(keyed.values())
  for c in self.centuries:write(f'public/data/temporal/{c}.geojson',{'type':'FeatureCollection','features':[f for f in output if f['properties']['validFrom']<(c+1)*100 and f['properties']['validTo']>=c*100]})
  for file in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
   d=read(file);d.update(self.labels);write(file,d)
  cur=read('public/data/curated-facts.json');reviewed=defaultdict(set)
  if(ROOT/'public/data/chronology-corrections.json').exists():
   for r in read('public/data/chronology-corrections.json')['identityCorrections']:reviewed[r['name']].add(r['qid'])
  for n,q in self.identities.items():
   if n in reviewed:cur['identities'].pop(n,None)
   else:cur['identities'][n]=q
  write('public/data/curated-facts.json',cur)
  allrows=[f for c in self.index['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']]
  self.index['counts']['polityRecords']=len({f['properties']['sourceRecord']for f in allrows});self.index['changeYears']=sorted(set(self.index['changeYears'])|{y for f in self.new for y in [f['properties']['validFrom'],f['properties']['validTo']+1]});self.index['expandedGapRevision']=self.tag;write('public/data/temporal/index.json',self.index)
  write('public/data/'+report_name,{'revision':self.tag,'reviewedAt':self.tag[-10:]if self.tag[-10:-6].isdigit()else'2026-11-01','records':self.audit,'summary':{'newPeriodRecords':len(self.new),'ownerNames':len(self.labels)},'limitations':['补绘参考时期轮廓不等于每年的独立测绘。','地域集合不是统一国家，不虚构共同统治者或国旗。','领地实际控制、军事管理、名义主权及现代边界不混为一谈。']})
  print('Expanded territory periods',len(self.new),'owners',len(self.labels),flush=True)
