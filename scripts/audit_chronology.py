"""Global, repeatable screening of every bundled territorial record.
Potential metadata conflicts and overlap diagnostics are leads, not automatic
historical verdicts. Do not truncate countries from unqualified Wikidata dates.
"""
import collections,hashlib,json,math,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape
from shapely import make_valid
from shapely.strtree import STRtree
def read(p):return json.loads((ROOT/p).read_bytes())
def read_rows(folder):
 rows={};copies=0
 for path in sorted((ROOT/folder).glob('*.geojson')):
  for f in json.loads(path.read_bytes())['features']:
   copies+=1;p=f['properties'];key=(str(p['sourceRecord']),p['NAME'],p['validFrom'],p['validTo'])
   rows.setdefault(key,f)
 return list(rows.values()),copies
def metadata_leads(rows,facts):
 polities={}
 for f in rows:
  p=f['properties']
  if p.get('sovereignName') or p.get('controlArea'):continue
  k=(p['NAME'],p.get('qid'));r=polities.setdefault(k,{'name':p['NAME'],'label':p.get('displayName',p['NAME']),'qid':p.get('qid'),'from':p['validFrom'],'to':p['validTo'],'recordCount':0})
  r['from']=min(r['from'],p['validFrom']);r['to']=max(r['to'],p['validTo']);r['recordCount']+=1
 leads=[];with_dates=0
 for (name,qid),r in polities.items():
  e=facts.get(qid,{});a=[v['value']for v in e.get('fields',{}).get('founded',[])if isinstance(v['value'],int)];b=[v['value']for v in e.get('fields',{}).get('dissolved',[])if isinstance(v['value'],int)]
  if a or b:with_dates+=1
  reasons=[]
  if a and r['to']<min(a)-2:reasons.append('地图所有记录早于关联实体的建国日期')
  elif a and r['from']<min(a)-30:reasons.append('记录起年显著早于关联实体日期，可能涉及前身或错误关联')
  if b and r['from']>max(b)+2:reasons.append('地图所有记录晚于关联实体的结束日期')
  elif b and r['to']>max(b)+30:reasons.append('记录末年显著晚于关联实体日期，可能涉及后继或错误沿用')
  if reasons:leads.append({**r,'entityLabel':e.get('label',''),'entityEnglish':e.get('en',''),'founded':a,'dissolved':b,'reasons':reasons,'status':'待进一步史料核定','source':'https://www.wikidata.org/wiki/'+str(qid)})
 return polities,leads,with_dates
def main():
 rows,copies=read_rows('public/data/temporal');before,_=read_rows('.local/chronology-originals');facts=read('public/data/polity-facts.json')['entities'];index=read('public/data/temporal/index.json');catalog=read('public/data/chronology-corrections.json')
 polities,leads,dated=metadata_leads(rows,facts);_,old_leads,_=metadata_leads(before,facts)
 errors=[];geometry=[];long=[];events=collections.Counter();regions=collections.Counter();hashes=collections.defaultdict(set)
 for f in rows:
  p=f['properties'];a,b=p['validFrom'],p['validTo'];name=p['NAME'];ref={'name':name,'from':a,'to':b,'record':p['sourceRecord']}
  if not isinstance(a,int)or not isinstance(b,int)or a>b:errors.append({**ref,'issue':'无效年代'})
  events[a]+=1;events[b+1]-=1
  try:
   g=shape(f['geometry']);geometry.append((f,g))
   if g.is_empty or not g.is_valid:errors.append({**ref,'issue':'空白或无效几何'})
   if not all(math.isfinite(x)for x in g.bounds)or not(-180.001<=g.bounds[0]<=g.bounds[2]<=180.001 and -90.001<=g.bounds[1]<=g.bounds[3]<=90.001):errors.append({**ref,'issue':'坐标超出范围'})
   x,y=g.representative_point().coords[0];region='美洲'if x< -30 else '欧洲'if x<45 and y>35 else '非洲'if x<55 and -40<y<=35 else '大洋洲'if x>=110 and y<0 else '亚洲';regions[region]+=1
   digest=hashlib.sha256(json.dumps(f['geometry'],separators=(',',':')).encode()).hexdigest()[:16];hashes[name].add(digest)
  except Exception as e:errors.append({**ref,'issue':'几何读取失败','detail':str(e)[:180]})
  if b-a+1>=25:long.append({**ref,'years':b-a+1,'method':p.get('temporalResolution','source-period'),'accuracy':p.get('accuracy','上游有效时期轮廓，未提供独立年度测绘')})
 # Sweep every calendar year, not just sparse reference snapshots.
 count=0;annual=[]
 for year in range(index['from'],index['to']+1):
  count+=events[year]
  if year!=0:annual.append({'year':year,'territorialRecords':count})
 # Whole-world spatial screening at independent historical checkpoints. Overlap
 # can be a contested claim, a dependency, or a source error; it is not deleted.
 checkpoints=[-500,1,500,1000,1200,1368,1371,1382,1444,1500,1600,1700,1800,1886,1900,1911,1918,1923,1939,1941,1945,1960,1991,2000,2024]
 overlaps={}
 for year in checkpoints:
  latest={}
  for f,g in geometry:
   p=f['properties']
   if p['validFrom']<=year<=p['validTo']:
    previous=latest.get(p['NAME'])
    if previous is None or (p['validFrom'],-p['validTo'])>(previous[0]['properties']['validFrom'],-previous[0]['properties']['validTo']):latest[p['NAME']]=(f,g)
  active=list(latest.values());geoms=[make_valid(g)for f,g in active];tree=STRtree(geoms)
  for i,g in enumerate(geoms):
   for j in tree.query(g,predicate='intersects'):
    j=int(j)
    if j<=i:continue
    area=g.intersection(geoms[j]).area;small=min(g.area,geoms[j].area)
    if area<.5 or not small or area/small<.1:continue
    a,b=active[i][0]['properties'],active[j][0]['properties'];key=tuple(sorted([a['NAME'],b['NAME']]))
    r=overlaps.setdefault(key,{'countries':list(key),'firstCheckpoint':year,'lastCheckpoint':year,'checkpoints':[],'maximumSmallerAreaShare':0,'status':'空间重叠线索，需区分争议、分层控制与源数据错误'})
    r['lastCheckpoint']=year;r['checkpoints'].append(year);r['maximumSmallerAreaShare']=round(max(r['maximumSmallerAreaShare'],area/small),3)
 print('Geometry and global checkpoints checked',len(rows),len(checkpoints),flush=True)
 report={'revision':catalog['revision'],'scope':'全球全部已打包领土记录；每个年份的有效期扫描；全球25个关键年份的空间交叉检查。不是逐条史学专家审定，也不是完整年度疆界库。','sources':{'territories':'https://github.com/Seshat-Global-History-Databank/cliopatria','metadata':'https://www.wikidata.org/','reviewedRules':'/data/chronology-corrections.json'},'summary':{'shards':len(index['centuries']),'storedShardRows':copies,'uniqueDatedRows':len(rows),'sourceRecords':index['counts']['polityRecords'],'polityIdentities':len(polities),'identitiesWithDateMetadata':dated,'yearQueriesChecked':len(annual),'from':index['from'],'to':index['to'],'reviewedCorrectionRules':len(catalog['identityCorrections']),'metadataLeadsBefore':len(old_leads),'metadataLeadsRemaining':len(leads),'structuralErrors':len(errors),'spatialCheckpoints':len(checkpoints),'overlapPairsToReview':len(overlaps),'intervalsAtLeast25Years':len(long)},'regions':dict(regions),'limitations':['Wikidata建国或结束日期可能代表独立、改制或某一阶段；日期冲突仅作核查线索，未自动删除领土。','古代疆界和未记录的战争控制线不能通过增加年份或平滑插值获得。','无新边界史料时，连续年份共享有出处的分期轮廓；新补绘区域明确标注概化方法。','原始资料仍有未核定的区域名称沿用和重叠；下列清单公开保留，不能据扫描无报错推断史实完全正确。'],'corrections':catalog['identityCorrections'],'metadataReviewQueue':sorted(leads,key=lambda r:(r['from'],r['name'])),'spatialReviewQueue':sorted(overlaps.values(),key=lambda r:-len(r['checkpoints'])),'longIntervals':sorted(long,key=lambda r:-r['years']),'structuralIssues':errors,'annualQueryCoverage':annual}
 out=ROOT/'public/data/chronology-audit.json';out.write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 warnings={r['name']+'|'+str(r['qid']):{'before':min(r['founded'])if r['founded']else None,'after':max(r['dissolved'])if r['dissolved']else None,'reasons':r['reasons']}for r in leads}
 (ROOT/'public/data/chronology-warning-index.json').write_text(json.dumps(warnings,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 note=ROOT/'docs/chronology-audit.md';s=report['summary'];note.write_text('# 全球时序数据核查\n\n'+report['scope']+'\n\n'+ '\n'.join(f'- {k}: {v}'for k,v in s.items())+'\n\n## 已确认修正\n\n'+'\n'.join(f"- {r['name']}（{r['from']}—{r['to']}）：{r['reason']}。https://www.wikidata.org/wiki/{r['qid']}"for r in catalog['identityCorrections'])+'\n\n## 检查边界\n\n'+'\n'.join('- '+s for s in report['limitations'])+'\n\n完整逐项清单见 `public/data/chronology-audit.json`；可视化页面 `/audit.html`。\n',encoding='utf8')
 print(json.dumps(s,ensure_ascii=True),flush=True)
if __name__=='__main__':main()
