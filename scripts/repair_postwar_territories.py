"""Reviewed post-war omissions, 1945–1955. Never fill all neutral land blindly.
Modern physical regions are explicitly labelled masks, not historical surveys.
Annual pre-patch geometry is retained and only documented missing territory added.
"""
import copy,json,sys,shutil
from pathlib import Path
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely import make_valid,union_all
from shapely.geometry import shape,mapping,box
from prepare_political_presentation import label_path
TAG='postwar-territories-1945-1955-v1'
LIBYA='https://digitallibrary.un.org/record/704492/files/A_1949_Add-1-EN.pdf'
ERITREA='https://digitallibrary.un.org/record/1643155/files/A_2233-EN.pdf'
SOMALI='https://www.legislation.gov.uk/uksi/1960/1060/pdfs/uksi_19601060_en.pdf'
TIMOR='https://www.un.org/unispal/document/auto-insert-179951/'

def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def clean(g):
 g=make_valid(g)
 if g.geom_type=='GeometryCollection':g=union_all([p for p in g.geoms if p.geom_type in ['Polygon','MultiPolygon']])
 return g

def main():
 path=ROOT/'public/data/temporal/19.geojson';backup=ROOT/'.local/postwar-review/territories-original.geojson'
 # Keep the first pre-patch version, including the earlier Russian gap repair.
 # Other upstream rebuilds require deliberate migration of this backup.
 if not backup.exists():shutil.copyfile(path,backup)
 atlas=json.loads(backup.read_bytes());original=atlas['features']
 admin=read('.local/ne_10m_admin_1_states_provinces.geojson')['features'];groups=defaultdict(list)
 for f in admin:groups[f['properties']['admin']].append(shape(f['geometry']))
 masks={n:clean(union_all(groups[n])) for n in ['Libya','Eritrea','Somaliland','East Timor','Falkland Islands','Russia','Israel','Gaza Strip']}
 subdivisions={f['properties']['iso_3166_2']:shape(f['geometry'])for f in admin if f['properties']['admin']=='Libya'}
 # These modern subdivisions approximate the THREE historical provinces. The
 # internal boundary is documented as a geographical reconstruction.
 cyrenaica=union_all([subdivisions['LY-'+s]for s in ['KF','BU','AJ','QB','JA','MJ','BA']])
 fezzan=union_all([subdivisions['LY-'+s]for s in ['MQ','WS','GT','SB','WD']])
 tripoli=masks['Libya'].difference(union_all([cyrenaica,fezzan]))
 index=read('public/data/temporal/index.json');cur=read('public/data/curated-facts.json');labels={};new_entities={};generated=[];replaced=defaultdict(set);audit=[]
 def add(name,label,qid,mask,year,source,detail,parent=None,parentqid=None,kind=None,**extra):
  gap=clean(mask.difference(occupied))
  if assigned:gap=clean(gap.difference(union_all(assigned)))
  if gap.is_empty or gap.area<1e-6:return
  old=active.get(name);g=clean(union_all([shape(old['geometry']),gap]))if old else gap
  props=copy.deepcopy(old['properties'])if old else {'NAME':name,'SUBJECTO':name,'qid':qid,'entityId':qid}
  props.update(NAME=name,SUBJECTO=name,qid=qid,entityId=qid,displayName=label,validFrom=year,validTo=year,sourceRecord=f'{TAG}:{name}:{year}',chronologyPatch=TAG,source='有史料的战后过渡地区补绘',sourceUrl=source,temporalResolution='postwar-gap-reconstruction',yearConvention='按年度代表状态；独立／移交发生在年内时明确说明。',accuracy=detail,geometryMethod='以Natural Earth地理区作遮罩，仅补当年历史GIS尚无归属的部分；不是逐年历史实测疆界。',labelPath=label_path(g,label))
  if parent:props.update(sovereignName=parent,sovereignQid=parentqid,territoryType=kind or'colony')
  props.update(extra)
  generated.append({'type':'Feature','properties':props,'geometry':mapping(g)});replaced[name].add(year)
  audit.append({'year':year,'name':name,'addedSquareDegrees':gap.area,'overlapWithExisting':gap.intersection(occupied).area,'source':source})
  assigned.append(gap);labels[name]=label
  new_entities.setdefault(qid,{'label':label,'en':name,'description':detail,'fields':{}})
  cur['identities'][name]=qid;cur['polities'].setdefault(qid,{}).update(source=source)
 for year in range(1945,1956):
  active={}
  for f in original:
   p=f['properties']
   if p['validFrom']<=year<=p['validTo']:
    previous=active.get(p['NAME'])
    if not previous or(p['validFrom'],-p['validTo'])>(previous['properties']['validFrom'],-previous['properties']['validTo']):active[p['NAME']]=f
  occupied=clean(union_all([clean(shape(f['geometry']))for f in active.values()]));assigned=[]
  if year<1951:
   add('British Tripolitania','的黎波里塔尼亚（英国管理）','local:british-tripolitania',tripoli,year,LIBYA,'利比亚独立前由英国管理的的黎波里塔尼亚。行政区遮罩概化；管理关系不是现代主权归属。','United Kingdom','Q145','administration')
   add('French Fezzan','费赞（法国管理）','local:french-fezzan',fezzan,year,LIBYA,'法国对费赞的战后管理区；1951年12月利比亚独立后不再按法国管理区显示。内界为地理概化。','France','Q142','administration')
   if year<1949:add('British Cyrenaica','昔兰尼加（英国管理）','local:british-cyrenaica',cyrenaica,year,LIBYA,'战后英国管理的昔兰尼加；1949年成立埃米尔国，1951年并入独立利比亚。','United Kingdom','Q145','administration')
   else:add('Emirate of Cyrenaica','昔兰尼加埃米尔国','local:cyrenaica-emirate',cyrenaica,year,LIBYA,'伊德里斯领导的昔兰尼加埃米尔国（1949—1951），处于英国影响与管理安排之下；未把它提前画成整个独立利比亚。')
  else:
   lib=next(f for f in original if f['properties']['NAME']=='Kingdom of Libya'and f['properties']['validFrom']<=1953<=f['properties']['validTo'])
   add('Kingdom of Libya','利比亚王国',lib['properties']['qid'],masks['Libya'],year,LIBYA,'利比亚于1951年12月24日独立；1951年按独立后的年末状态显示。后续年份仅补历史轮廓的缺失部分，边缘采用地理遮罩概化。')
  if year<1952:add('British Administration of Eritrea','厄立特里亚（英国管理）','local:british-eritrea',masks['Eritrea'],year,ERITREA,'英国对原意属厄立特里亚的管理持续至1952年9月15日，不等于当时已是独立厄立特里亚国家。','United Kingdom','Q145','administration')
  else:add('Ethiopia','埃塞俄比亚','Q115',masks['Eritrea'],year,ERITREA,'1952年9月建立与埃塞俄比亚的联邦安排，按年末状态补入联邦范围。保留其余既有埃塞俄比亚轮廓，不用现代厄立特里亚独立国家身份回填。',regionalControlNote='厄立特里亚自1952年9月起为与埃塞俄比亚联邦的自治组成地区；并非立即等同中央直接行政管理，1962年后的兼并阶段不在本轮补绘范围。',regionalControlSource=ERITREA)
  add('British Somaliland Protectorate','英属索马里保护地','local:british-somaliland',masks['Somaliland'],year,SOMALI,'英属索马里保护地，1948年11月恢复民政；1960年6月才独立。以今索马里兰地理范围概化原保护地，不据此支持现代主权主张。','United Kingdom','Q145','protectorate')
  if year>=1946:add('Portuguese Timor','葡属帝汶','local:portuguese-timor',masks['East Timor'],year,TIMOR,'二战后葡萄牙恢复管理的葡属帝汶；包括欧库西飞地。1951年殖民地改称海外省，均不等于当时已是现代独立东帝汶。','Portugal','Q45')
  add('Falkland Islands Dependency','福克兰／马尔维纳斯群岛（英国管理）','local:falklands-postwar',masks['Falkland Islands'],year,'https://www.un.org/dppa/decolonization/en/nsgt/falkland-islands-malvinas','当时由英国管理、阿根廷提出主权要求的群岛。填色表示实际管理，不等于对争议主权作裁定。','United Kingdom','Q145')
  if year>=1949:
   add('Gaza Strip under Egyptian Administration','加沙地带（埃及管理）','local:gaza-egyptian-administration',masks['Gaza Strip'],year,'https://www.un.org/unispal/timeline/','按1949年停战后埃及管理加沙地带的阶段补绘；管理线不等于国际承认的主权边界。采用地理遮罩概化，未把1947年分治方案直接当作实际控制图。','Kingdom of Egypt'if year<1953 else'Egypt','Q124943'if year<1953 else'Q79','administration')
   israel=active.get('State of Israel')
   if israel:add('State of Israel','以色列',israel['properties']['qid'],masks['Israel'].intersection(shape(israel['geometry']).buffer(.08)),year,'https://www.un.org/unispal/timeline/','只补原以色列历史轮廓邻近沿海的概化缝隙，不以现代行政范围改绘整个1949年停战线；保留邻近已有控制区和加沙管理区。')
  soviet=active.get('Union of Soviet Socialist Republics')
  if soviet:
   add('Union of Soviet Socialist Republics','苏联',soviet['properties']['qid'],masks['Russia'].intersection(box(-180,64,-169,72)),year,'https://www.wikidata.org/wiki/Q15180','修补反子午线西侧楚科奇地理部分的漏绘；沿用苏联本年的其余轮廓，不用现代俄罗斯国界替换整个苏联。')
 rows=[]
 for f in original:
  p=f['properties'];excluded=replaced.get(p['NAME'],set());a=p['validFrom'];b=p['validTo'];start=a
  for y in sorted(y for y in excluded if a<=y<=b):
   if start<y:
    row=copy.deepcopy(f);row['properties'].update(validFrom=start,validTo=y-1);rows.append(row)
   start=y+1
  if start<=b:
   row=copy.deepcopy(f);row['properties'].update(validFrom=start,validTo=b);rows.append(row)
 atlas['features']=rows+generated
 central={'British Gold Coast':('United Kingdom','Q145','colony'),'British Africa':('United Kingdom','Q145','colony'),'British Colonial Empire':('United Kingdom','Q145','colony'),'French Africa':('France','Q142','colony'),'Belgian Congo':('Kingdom of Belgium','Q31','colony'),'Netherlands Antilles':('Netherlands','Q55','overseas'),'Papua New Guinea':('Australia','Q408','administration'),'Qatar Protectorate':('United Kingdom','Q145','protectorate'),'French Indochina':('France','Q142','colony'),'French Mandate for Syria and Lebanon':('France','Q142','administration'),'Dutch East Indies':('Netherlands','Q55','colony')}
 for f in atlas['features']:
  p=f['properties']
  if p['validFrom']>1955 or p['validTo']<1945:continue
  if p['NAME']in central:
   parent,qid,kind=central[p['NAME']];p.update(sovereignName=parent,sovereignQid=qid,territoryType=kind)
  if p['NAME']=='New Hebrides':p['jointRulers']=['United Kingdom','France']
  if p['NAME']=='Kingdom of Bulgaria'and p['validFrom']==1947:
   p.update(NAME="People's Republic of Bulgaria",SUBJECTO="People's Republic of Bulgaria",qid='Q121932',entityId='Q121932',displayName='保加利亚人民共和国',sourceQid='Q147909',identityCorrection='保加利亚已于1946年废除君主制；1947年的这一源轮廓不应继续显示为王国。')
  if p['NAME']=='Palestinians'and p['validFrom']==1948:
   p.update(NAME='Palestinian Arab Local Authorities',SUBJECTO='Palestinian Arab Local Authorities',qid='local:palestinian-arab-control-1948',entityId='local:palestinian-arab-control-1948',displayName='巴勒斯坦阿拉伯地方势力',sourceQid='Q201190',identityCorrection='1948年的地方政治与军事控制聚合，不将民族群体实体当成统一国家或虚构一位共同总统。')
   labels[p['NAME']]=p['displayName'];cur['identities'][p['NAME']]=p['qid'];new_entities[p['qid']]={'label':p['displayName'],'en':p['NAME'],'description':p['identityCorrection'],'fields':{}}
  if p['NAME']=='Sultanate of Aceh':
   p.update(NAME='Aceh Republican Administration',SUBJECTO='Aceh Republican Administration',qid='local:aceh-republican',entityId='local:aceh-republican',displayName='亚齐（印尼共和政权）',sovereignName='Republic of Indonesia',sovereignQid='Q252',territoryType='member',identityCorrection='1945年后亚齐为印度尼西亚共和力量的重要基地，不是仍由旧苏丹统治的独立苏丹国。',sourceQid=p.get('qid'))
   labels[p['NAME']]=p['displayName'];cur['identities'][p['NAME']]=p['qid'];new_entities[p['qid']]={'label':p['displayName'],'en':p['NAME'],'description':p['identityCorrection'],'fields':{}}
  if p['NAME']=='Hungary'and p.get('qid')=='Q28513':
   q='local:hungary-national-council'if p['validFrom']<1946 else'local:second-hungarian-republic';n='Hungarian Postwar Interim State'if p['validFrom']<1946 else'Second Hungarian Republic'
   p.update(NAME=n,SUBJECTO=n,qid=q,entityId=q,displayName='匈牙利（战后过渡）'if p['validFrom']<1946 else'匈牙利第二共和国',sourceQid='Q28513',identityCorrection='战后匈牙利不能关联早已解体的奥匈帝国实体。')
   labels[n]=p['displayName'];cur['identities'][n]=q;new_entities[q]={'label':p['displayName'],'en':n,'description':p['identityCorrection'],'fields':{}}
   if n=='Second Hungarian Republic':p['validTo']=min(p['validTo'],1948)
  if p.get('controlArea'):
   controller={'United Kingdom':'Q145','French Fourth Republic':'Q142','Union of Soviet Socialist Republics':'Q15180','United States of America':'Q30'}.get(p.get('controller'))
   if controller:p['controllerQid']=controller
   if p.get('jointRulers')and'berlin'in p['NAME']:p.update(qid='local:berlin-four-powers',entityId='local:berlin-four-powers')
  if p['NAME']in ['British Africa','French Africa','British Colonial Empire']:p['representationNote']='未能按殖民地进一步分解的剩余地理聚合；不是另一个统一国家。中央领导人取上层管理方当年任期。'
 write('public/data/temporal/19.geojson',atlas)
 records={f['properties']['sourceRecord']for c in index['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']}
 index['counts']['polityRecords']=len(records);index['changeYears']=sorted(set(index['changeYears'])|set(range(1945,1957)));index['postwarRevision']=TAG;write('public/data/temporal/index.json',index)
 for filename in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  names=read(filename);names.update(labels);write(filename,names)
 facts=read('public/data/polity-facts.json')
 for q,e in new_entities.items():facts['entities'].setdefault(q,e)
 write('public/data/polity-facts.json',facts);write('public/data/curated-facts.json',cur)
 write('public/data/postwar-territory-review.json',{'reviewedAt':'2026-10-31','window':[1945,1955],'revision':TAG,'records':audit,'limitations':['只按核实的管理／独立阶段补空白，不把全部灰区自动划给邻国。','地理遮罩不是精确历史内界；1951年利比亚和1952年厄立特里亚取年末代表状态。','湖面和变迁的内陆水域不视作待分配国土。']})
 print('Postwar additions',len(generated),'dated owners',len(labels),flush=True)

if __name__=='__main__':main()
