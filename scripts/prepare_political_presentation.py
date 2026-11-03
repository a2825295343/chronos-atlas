"""Normal country labels, geographical colonial labels, and terrain-fitting name baselines.
Original polity identifiers, source dates, geometry lineage and regime names are retained.
Colonial geographic partitions are explicitly marked as reconstruction from modern geography.
"""
import collections,json,math,pathlib,re,sys,shutil
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape,mapping,LineString,box
from shapely.ops import transform,unary_union
from shapely.strtree import STRtree
from shapely import make_valid
from colonial_naming import colonial_label
from polity_display_names import DISPLAY_NAMES
PI=math.pi

def project(x,y,z=None):return x,180/PI*math.log(math.tan(PI/4+max(-84,min(84,y))*PI/360))
def unproject(x,y,z=None):return x,(2*math.atan(math.exp(y*PI/180))-PI/2)*180/PI

def label_path(geometry,label):
 g=shape(geometry)
 if not g.is_valid:g=make_valid(g)
 if g.geom_type=='MultiPolygon':g=max(g.geoms,key=lambda p:p.area)
 if g.geom_type!='Polygon' or g.area<.003:return None
 # Unwrap dateline fragments before doing a Mercator chord search.
 if g.bounds[2]-g.bounds[0]>180:return None
 g=make_valid(transform(project,g.simplify(.08,preserve_topology=True)))
 if g.geom_type=='MultiPolygon':g=max(g.geoms,key=lambda p:p.area)
 if g.geom_type!='Polygon':return None
 xmin,ymin,xmax,ymax=g.bounds
 width=xmax-xmin;height=ymax-ymin
 if not width or not height:return None
 center=g.representative_point();best=None
 # Maximize usable interior span with a preference for quieter, near-horizontal angles.
 for angle in [-60,-30,0,30,60]:
  a=angle*PI/180;dx,dy=math.cos(a),math.sin(a);length=max(width,height)*3
  for offset in [0]:
   cx=center.x-dy*height*offset;cy=center.y+dx*height*offset
   cut=g.intersection(LineString([(cx-dx*length,cy-dy*length),(cx+dx*length,cy+dy*length)]))
   segments=list(cut.geoms)if cut.geom_type=='MultiLineString'else[cut]if cut.geom_type=='LineString'else[]
   for line in segments:
    if line.length<=0:continue
    mid=line.interpolate(.5,normalized=True);clearance=g.boundary.distance(mid)
    score=line.length*(.82+.18*math.cos(a))*(.72+.28*min(1,clearance/max(.01,height*.2)))
    if best is None or score>best[0]:best=(score,line)
 if not best:return None
 line=best[1];points=[line.interpolate(t,normalized=True)for t in [.12,.32,.5,.68,.88]]
 coords=[list(unproject(p.x,p.y))for p in points]
 # Declutter long country names by distributing them across the principal territory.
 length=line.length*.76;glyphs=max(2,len(label));base=max(.65,min(40,length/360*512/(glyphs*1.12)))
 return {'coordinates':coords,'size':round(base,3),'span':round(length,3)}

def main():
 entities=json.loads((ROOT/'.local/temporal-entities.json').read_text(encoding='utf-8'))
 labels={**json.loads((ROOT/'src/localization/names.zh.json').read_text(encoding='utf-8')),**json.loads((ROOT/'src/localization/temporal.zh.json').read_text(encoding='utf-8'))}
 overrides={
 'Pahlavi Dynasty':'伊朗','Francoist Spain':'西班牙','Estado Novo':'葡萄牙','Portuguese Republic':'葡萄牙','Portuguese Empire':'葡萄牙','Portuguese Colonies':'葡萄牙海外领地','Portuguese Africa':'葡属非洲',
 'French First Republic':'法国','French Directory':'法国','French Consulate':'法国','First French Empire':'法国','Second French Empire':'法国','French Second Republic':'法国','French Third Republic':'法国','French Fourth Republic':'法国','French Fifth Republic':'法国','Kingdom of France':'法国','Bourbon Kingdom of France':'法国','Free French':'法国','Vichy France':'法国',
 'German Empire':'德国','Weimar Republic':'德国','Nazi Germany':'德国','Federal Republic of Germany':'西德','Federated Republic of Germany':'德国','German Democratic Republic':'东德','West Germany':'西德','East Germany':'东德',
 'First Hellenic Republic':'希腊','Third Hellenic Republic':'希腊','Kingdom of Greece':'希腊','Second Spanish Republic':'西班牙','First Spanish Republic':'西班牙','Kingdom of Spain':'西班牙','Spanish Nationalists':'西班牙国民军','Spanish Empire':'西班牙',
 'Russian Federation':'俄罗斯','Russian Empire':'俄罗斯帝国','Russian Republic':'俄国','Union of Soviet Socialist Republics':'苏联','Socialist Federal Republic of Yugoslavia':'南斯拉夫','Kingdom of Yugoslavia':'南斯拉夫',
 'Kingdom of England':'英格兰','Kingdom of Great Britain':'大不列颠','United Kingdom of Great Britain and Ireland':'英国','United Kingdom':'英国','United States of America':'美国','United States':'美国',
 'Kingdom of Portugal':'葡萄牙','Kingdom of Italy':'意大利','Republic of Italy':'意大利','Kingdom of Hungary':'匈牙利','Hungarian Republic':'匈牙利','Hungarian People\'s Republic':'匈牙利','Republic of Austria':'奥地利','Second Republic of Austria':'奥地利',
 'Republic of Albania':'阿尔巴尼亚','People\'s Socialist Republic of Albania':'阿尔巴尼亚','Republic of Bulgaria':'保加利亚','People\'s Republic of Bulgaria':'保加利亚','Socialist Republic of Romania':'罗马尼亚','Kingdom of Romania':'罗马尼亚','Second Polish Republic':'波兰','Republic of Poland':'波兰',
 'Brazilian Republic':'巴西','Federated Republic of Brazil':'巴西','Republic of Brazil':'巴西','Empire of Brazil':'巴西帝国','Argentine Republic':'阿根廷','Federated Republic of Mexico':'墨西哥','Mexican Empire':'墨西哥帝国',
 'Republic of China':'中华民国','People\'s Republic of China':'中国','Democratic People\'s Republic of Korea':'朝鲜','Republic of Korea':'韩国','Democratic Republic of Vietnam':'北越','Republic of Vietnam':'南越','Socialist Republic of Vietnam':'越南',
 'Republic of the Congo':'刚果共和国','Democratic Republic of the Congo':'刚果民主共和国','People\'s Republic of Angola':'安哥拉','People\'s Republic of Kampuchea':'柬埔寨','Mongolian People\'s Republic':'蒙古',
 'Former Yugoslav Republic of Macedonia':'北马其顿','Islamic Republic of Iran':'伊朗','Republic of Iraq':'伊拉克','Iraqi Republic':'伊拉克','Arab Republic of Egypt':'埃及','Republic of Egypt':'埃及','Libyan Arab Republic':'利比亚','Republic of Turkey':'土耳其',
 'Republic of The Gambia':'冈比亚','Oriental Republic of Uruguay':'乌拉圭','People\'s Democratic Republic of Algeria':'阿尔及利亚','Central African Republic':'中非共和国','Dominican Republic':'多米尼加','Republic of Cabo Verde':'佛得角',
 'British Raj':'英属印度','British Colonial Empire':'英国海外领地','British Empire':'英国','English Colonial Empire':'英格兰海外领地','French Africa':'法属非洲','French Indochina':'法属印度支那','First French colonial empire':'法属海外领地','German Africa':'德属非洲','British Africa':'英属非洲','British East Africa':'英属东非'}
 # Common present-day state names; constitutional styles stay in the archive.
 modern={p['NAME_EN']:p.get('NAME_ZH')or p['NAME_EN']for p in [f['properties']for f in json.loads((ROOT/'.local/presentation/admin0.geojson').read_text(encoding='utf-8'))['features']]}
 for name,p in entities.items():
  if name in overrides:continue
  core=re.sub(r"^(?:Federal|Federated|Islamic|Arab|Socialist|People's Democratic|People's|Democratic|Second|Third|First)?\s*(?:Republic|Kingdom) of (?:the )?",'',name)
  if core in modern and p['to']>=1800:overrides[name]=modern[core]
 normal={name:overrides.get(name,labels.get(name,name))for name in entities};normal.update(overrides);normal.update(DISPLAY_NAMES)
 (ROOT/'src/localization/display-names.zh.json').write_text(json.dumps(normal,ensure_ascii=False,indent=2),encoding='utf-8')
 admin=json.loads((ROOT/'.local/presentation/admin0.geojson').read_text(encoding='utf-8'))['features'];areas=[make_valid(shape(f['geometry']).simplify(.035,preserve_topology=True))for f in admin];tree=STRtree(areas)
 families={
  'Portugal':{'Portuguese Empire','Portuguese Colonies','Portuguese Africa','Portuguese Republic','Estado Novo','Kingdom of Portugal'},
  'Spain':{'Spanish Empire','Kingdom of Spain','Francoist Spain','Second Spanish Republic'},
  'France':{'French Africa','French Third Republic','French Fourth Republic','French Fifth Republic','First French colonial empire','First French Empire','Second French Empire','French First Republic','French Second Republic','French Directory','French Consulate','Kingdom of France'},
  'United Kingdom':{'British Empire','British Colonial Empire','British Africa','British East Africa','English Colonial Empire','Kingdom of Great Britain'},
  'Germany':{'German Africa','German Empire'},'Italy':{'Kingdom of Italy','Republic of Italy'},'Netherlands':{'Netherlands','Dutch Republic','Dutch Empire'},'Belgium':{'Belgium','Kingdom of Belgium'}}
 parent={n:country for country,names in families.items()for n in names}
 qids={'Portugal':'Q45','Spain':'Q29','France':'Q142','United Kingdom':'Q145','Germany':'Q183','Italy':'Q38','Netherlands':'Q55','Belgium':'Q31'}
 prefixes={'Portugal':'葡属','Spain':'西属','France':'法属','United Kingdom':'英属','Germany':'德属','Italy':'意属','Netherlands':'荷属','Belgium':'比属'}
 colony={
 ('Portugal','Angola'):'葡属安哥拉',('Portugal','Mozambique'):'葡属莫桑比克',('Portugal','Guinea-Bissau'):'葡属几内亚',('Portugal','Cabo Verde'):'葡属佛得角',('Portugal','São Tomé and Principe'):'葡属圣多美和普林西比',('Portugal','Timor-Leste'):'葡属帝汶',
 ('France','Algeria'):'法属阿尔及利亚',('France','Mali'):'法属苏丹',('France','Benin'):'法属达荷美',('France','Burkina Faso'):'法属上沃尔特',('France','Congo'):'法属中刚果',('France','Republic of the Congo'):'法属中刚果',('France','Central African Republic'):'法属乌班吉沙里',('France','Djibouti'):'法属索马里',('France','Vietnam'):'法属越南地区',
 ('United Kingdom','Myanmar'):'英属缅甸',('United Kingdom','Sri Lanka'):'英属锡兰',('United Kingdom','Ghana'):'英属黄金海岸',('United Kingdom','Zambia'):'北罗得西亚',('United Kingdom','Zimbabwe'):'南罗得西亚',('United Kingdom','Malawi'):'尼亚萨兰',('United Kingdom','Belize'):'英属洪都拉斯',('United Kingdom','Guyana'):'英属圭亚那',
 ('Spain','Equatorial Guinea'):'西属几内亚',('Spain','Western Sahara'):'西属撒哈拉',('Germany','Namibia'):'德属西南非洲',('Germany','Tanzania'):'德属东非',('Netherlands','Indonesia'):'荷属东印度',('Belgium','Democratic Republic of the Congo'):'比属刚果'}
 processed={};stats=collections.Counter();report=[]
 paths={};pathsfile=ROOT/'.local/presentation/label-paths.json'
 if pathsfile.exists():paths=json.loads(pathsfile.read_text(encoding='utf-8'))
 def process(f):
  p=f['properties'];key=str(p['sourceRecord']);name=p['NAME']
  if key in processed:return processed[key]
  rows=[f];nation=parent.get(name)
  if nation and p['validTo']>=1500:
   g=make_valid(shape(f['geometry']).simplify(.035,preserve_topology=True));parts=[];unclaimed=g
   for index in tree.query(g):
    target=admin[int(index)]['properties'];country=target.get('NAME_EN','');iso=target.get('ADM0_A3')
    if country==nation or (nation=='United Kingdom'and country in ['United Kingdom','Ireland']):continue
    # Contiguous European territorial conquests retain their political label.
    if target.get('CONTINENT')=='Europe' and not (nation=='United Kingdom'and country in ['Malta','Cyprus','Gibraltar']):continue
    cut=g.intersection(areas[int(index)])
    if cut.is_empty or cut.area<.015:continue
    if cut.geom_type=='GeometryCollection':cut=unary_union([s for s in cut.geoms if s.geom_type in ['Polygon','MultiPolygon']])
    if cut.geom_type not in ['Polygon','MultiPolygon']:continue
    # UK India was an administrative whole, not three current independent countries.
    if nation=='United Kingdom'and country in ['India','Pakistan','Bangladesh']:
     cname='英属印度';eng='British India'
    else:cname=colony.get((nation,country),prefixes[nation]+(target.get('NAME_ZH')or labels.get(country,country)));eng=nation+' Colony - '+country
    # Small European-origin enclaves within modern Asia have distinct local names.
    if nation=='Portugal'and country=='China':cname='葡属澳门';eng='Portuguese Macau'
    if nation=='Portugal'and country=='India':cname='葡属印度';eng='Portuguese India'
    cname=colonial_label(nation,country,cname)
    normal[eng]=cname
    props={**p,'NAME':eng,'SUBJECTO':eng,'sourcePolity':name,'sovereignName':nation,'sovereignQid':qids[nation],'territoryType':'colony','displayName':cname,'partitionBasis':'现代地理底图辅助划分殖民地区；不等同精确历史行政界','identityName':eng}
    parts.append({'type':'Feature','id':str(f['id'])+'-'+str(iso),'properties':props,'geometry':mapping(cut.simplify(.015,preserve_topology=True))});unclaimed=unclaimed.difference(cut)
   if parts:
    rows=[]
    if not unclaimed.is_empty and unclaimed.area>.01:
     if unclaimed.geom_type=='GeometryCollection':unclaimed=unary_union([s for s in unclaimed.geoms if s.geom_type in ['Polygon','MultiPolygon']])
     if unclaimed.geom_type in ['Polygon','MultiPolygon']:rows.append({**f,'geometry':mapping(unclaimed)})
    grouped={}
    for part in parts:
     n=part['properties']['NAME'];grouped.setdefault(n,[]).append(part)
    for n,group in grouped.items():rows.append({**group[0],'geometry':mapping(unary_union([shape(x['geometry'])for x in group]))})
    stats['splitSourceRecords']+=1;stats['colonialTerritories']+=len(grouped)
  for row in rows:
   p2=row['properties'];n=p2['NAME'];label=normal.get(n,labels.get(n,n));p2['displayName']=label
   cachekey=str(p2['sourceRecord'])+'|'+n
   if cachekey not in paths:paths[cachekey]=label_path(row['geometry'],label)
   if paths[cachekey]:p2['labelPath']=paths[cachekey]
  processed[key]=rows;return rows
 for path in sorted((ROOT/'public/data/temporal').glob('*.geojson')):
  # Always start from upstream dated shards so the build remains idempotent.
  original=ROOT/'.local/presentation/original-shards'/path.name;original.parent.mkdir(exist_ok=True)
  if not original.exists():shutil.copyfile(path,original)
  current=json.loads(path.read_text(encoding='utf-8'))
  if current['features']and all('displayName'in f['properties']for f in current['features']):
   grouped=collections.defaultdict(list)
   for f in current['features']:
    grouped[str(f['properties']['sourceRecord'])].append(f)
    normal[f['properties']['NAME']]=f['properties']['displayName']
   processed.update(grouped)
   print('Reused prepared century',path.stem,flush=True);continue
  data=json.loads(original.read_text(encoding='utf-8'));rows=[]
  for j,f in enumerate(data['features']):
   rows.extend(process(f))
   if path.stem in ['19','20']and j%100==0:print('Century',path.stem,'records',j,'/',len(data['features']),flush=True)
  path.write_text(json.dumps({'type':'FeatureCollection','features':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
  pathsfile.write_text(json.dumps(paths,ensure_ascii=False),encoding='utf-8')
  if path.stem in ['14','19','20']:print('Prepared century',path.stem,len(rows),flush=True)
 pathsfile.write_text(json.dumps(paths,ensure_ascii=False),encoding='utf-8')
 (ROOT/'src/localization/display-names.zh.json').write_text(json.dumps(normal,ensure_ascii=False,indent=2),encoding='utf-8')
 (ROOT/'public/data/name-review.json').write_text(json.dumps({'scope':'All source polity names examined by country/regime naming policy; original identifiers retained','names':len(normal),'overrides':overrides,'colonialStats':dict(stats),'colonialPartitionSource':'Natural Earth 1:10m admin-0 geographic reference','limits':'Colonial partitions use modern geographic reference as reconstruction; they are not newly verified historical administrative boundaries.'},ensure_ascii=False,indent=2),encoding='utf-8')
 shutil.copyfile(ROOT/'.local/presentation/NotoSerifSC.ttf',ROOT/'public/data/atlas-serif.ttf');shutil.copyfile(ROOT/'.local/presentation/NotoSerifSC-OFL.txt',ROOT/'public/data/SERIF_FONT_LICENSE.txt')
 print('Presentation',dict(stats),'label paths',len(paths),'names',len(normal),flush=True)
if __name__=='__main__':main()
