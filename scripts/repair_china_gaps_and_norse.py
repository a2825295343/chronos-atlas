"""Dated interior omissions and two event/language identity collisions.

Provincial masks locate missing pieces only. They are not historical borders;
existing owners, Xinjiang restorations and foreign concessions are retained.
"""
import copy,json
from collections import defaultdict
from territory_repair_stage import ROOT,Stage,read,write,clean
from prepare_political_presentation import label_path
from shapely.geometry import shape,mapping,box
from shapely import union_all

TAG='china-interior-and-norse-2026-11-01'
QING='https://en.wikipedia.org/wiki/Dungan_Revolt_(1862%E2%80%931877)'
REPUBLIC='https://www.cambridge.org/core/books/abs/cambridge-history-of-china/warlord-era-politics-and-militarism-under-the-peking-government-191628/04BADE20AB7E9D27E80A97E6DEA7DE58'
COALITION='https://chiculture.org.hk/en/photo-story/2775'
INNER='https://dangshi.people.com.cn/n1/2017/0203/c85037-29054924.html'
NORTH='https://en.wikipedia.org/wiki/Norsemen'

def main():
 stage=Stage(TAG,[18,19]);admin=read('.local/ne_10m_admin_1_states_provinces.geojson')['features'];countries=read('.local/presentation/admin0.geojson')['features'];definitions={}
 china=clean(union_all([shape(f['geometry'])for f in countries if f['properties']['NAME_EN']=="People's Republic of China"]))
 def province(names):return clean(union_all([shape(f['geometry'])for f in admin if f['properties'].get('admin')=='China'and f['properties']['name']in names]))
 def repair(n,label,q,g,a,b,source,note,regional=False,remove=(),**extra):
  if g.is_empty:return
  definitions[n]={'label':label,'qid':q,'from':a,'to':b,'source':source,'note':note,'regional':regional,**extra}
  props={'regionalCollection':regional,'representationKind':'regional-polities'if regional else'polity','representationNote':note,'inferredBoundary':True,**extra}
  for lo,hi in stage.periods(g,a,b):stage.repair(g,lo,hi,[(n,label,q,g,source,note,props)],remove=remove)
 # The recurring blank is a deleted civil-war interior, not a lost outer border.
 # Restrict to land shared by the existing 1863 and 1877 Qing reference frames.
 def qing_at(y):return stage.world(y)['Qing Dynasty'][1]
 nw=clean(qing_at(1863).intersection(qing_at(1877)).intersection(china).intersection(box(89,33.5,110.5,43)))
 repair('Qing Dynasty','清朝','Q8733',nw,1864,1876,QING,'补回1863与1877两侧清朝轮廓共同覆盖的陕甘、青海及河西内陆遗漏。此底色包含行政归属概览，不表示起义期间清廷持续直接控制每处地方；已单列可定位的回军核心。')
 # Named, bounded cores make a civil-war area visible without inventing one
 # unified Dungan state or turning the whole province into rebel territory.
 cores=[('Jinjipu Hui Forces','金积堡回军','local:jinjipu-forces',box(105.94,37.6,106.35,38.12),1864,1870,'https://en.wikipedia.org/wiki/Ma_Hualong','马化龙','金积堡及邻近核心的概化示意；1866年请降后仍保留武装，不把全部陕甘回军当成同一政权。'),
 ('Suzhou Hui Forces','肃州回军','local:suzhou-hui-forces',box(98.3,39.58,98.68,39.92),1865,1872,'https://www.gsdfszw.org.cn/gssz_58/dyl_69/jqs_231/201708/P020171123362591662144.pdf','马文禄','肃州城附近核心的概化示意，不是整个河西走廊的持续控制范围；1873年战败后年度底图归清。')]
 for n,l,q,g,a,b,url,person,note in cores:
  repair(n,l,q,clean(g.intersection(china)),a,b,url,note,remove=('Qing Dynasty',),controlArea=True,controller=l,controllerZh=l,sovereignName='Qing Dynasty',sovereignQid='Q8733',territoryType='military-control');definitions[n]['person']=person
 # Missing provincial military administrations inside the Republic, never a
 # modern China mask that would annex existing Tibet/Mongolia or concessions.
 provinces=[('Yunnan Military Authorities','滇系军政当局','Yunnan'),('Guangxi Military Authorities','桂系军政当局','Guangxi'),('Guizhou Military Authorities','贵州地方军政当局','Guizhou'),('Sichuan Military Authorities','四川地方军政当局','Sichuan'),('Guangdong Military Authorities','广东地方军政当局','Guangdong'),('Hunan Military Authorities','湖南地方军政当局','Hunan'),('Northwestern Military Authorities','西北地方军政当局','Shaanxi'),('Gansu Military Authorities','甘肃地方军政当局','Gansu'),('Shanxi Military Authorities','晋系军政当局','Shanxi'),('Hebei Military Authorities','直隶地方军政当局','Hebei'),('Shandong Military Authorities','山东地方军政当局','Shandong'),('Chahar and Rehe Authorities','察热地方军政当局','Inner Mongol')]
 provinces.extend([('Beijing Tianjin Military Authorities','京津北洋军政当局',['Beijing','Tianjin']),('Ningxia Military Authorities','宁夏地方军政当局','Ningxia'),('Qinghai Military Authorities','青海地方军政当局','Qinghai'),('Chongqing Military Authorities','重庆地方军政当局','Chongqing')])
 for n,l,prov in provinces:
  g=province([prov]if isinstance(prov,str)else prov)
  # Modern eastern Sichuan is only a locating mask; Kham and Tibet are not
  # silently declared uniformly controlled by a Sichuan military governor.
  if prov=='Sichuan':g=clean(g.intersection(box(101.5,20,130,50)))
  repair(n,l,'local:'+n.lower().replace(' ','-'),g,1917,1927,REPUBLIC,'仅补原图遗漏的地方军政范围；多个军阀、行政与驻军体系先后并存，并非新独立国家或全省统一政权。以现代省域定位缺项，不能据此认定民国行政边界与现代完全相同，也不能据此复原各年的战线。',regional=True,sovereignName='Republic of China',sovereignQid='Q13426199',territoryType='administration')
 kham=clean(union_all([province(['Sichuan']).intersection(box(95,26,101.5,34.7)),province(['Xizang']).intersection(box(95,26,103,34.7))]))
 repair('Kham Local Authorities','康区地方诸政权','local:kham-authorities',kham,1917,1927,'https://en.wikipedia.org/wiki/Kham','仅补康区地方军政、土司及寺院势力的遗漏地域。拉萨政府、川边军政与地方首领的控制并不一致，未把这片概化地域认定为统一政权或统一中央直辖范围；已存在的西藏与其他控制方不覆盖。',regional=True)
 # Part of Japan's former occupied area has no successor in the 1946 frame.
 # The west was contested by Fu's forces and CCP local administrations; the
 # eastern autonomy movement is not annexed to the Mongolian People's Republic.
 inner=clean(union_all([province(['Inner Mongol']),province(['Hebei']).intersection(box(113,40,120,44.5))]));gap1946=clean(inner.difference(union_all([g for p,g in stage.world(1946).values()])))
 for n,l,q,g in [('Suiyuan Chahar Local Authorities','绥察地方军政区','local:suiyuan-chahar-1946',gap1946.intersection(box(100,35,116.5,55))),('Inner Mongolian Autonomy Movement Areas','内蒙古自治运动地区','local:inner-autonomy-1946',gap1946.intersection(box(116.5,35,125,55)))]:
  repair(n,l,q,clean(g),1946,1946,INNER,'1946年原图遗漏地区的分区概览。绥察存在国民党傅作义部与中共地方军政力量的争夺，东部自治运动也经历组织改组；这里不是一个新国家，不代表各方共同执政或全年控制线不变，不属于蒙古人民共和国。',regional=True,sovereignName='Republic of China',sovereignQid='Q13426199',territoryType='administration')
 stage.finish('china-interior-gap-review.json')
 # Separate the 1930 coalition from a war entity, then dissolve it in 1931.
 world=read('public/data/temporal/19.geojson');fs=world['features'];out=[];made=[]
 coalition=next((f for f in fs if f['properties']['NAME']=='Anti-Kuomintang Coalition'and f['properties']['validFrom']==1930),None)
 if coalition:
  g=shape(coalition['geometry']);other=union_all([shape(f['geometry'])for f in fs if f['properties']['validFrom']<=1930<=f['properties']['validTo']and f['properties']['NAME']not in ['Republic of China','Anti-Kuomintang Coalition']]);g=clean(g.difference(other))
  for f in fs:
   p=f['properties']
   if p['NAME']=='Anti-Kuomintang Coalition':continue
   if p['NAME']=='Republic of China'and p['validFrom']==1930 and p['validTo']==1931:
    f=copy.deepcopy(f);f['geometry']=mapping(clean(shape(f['geometry']).difference(g)))
   out.append(f)
  r=copy.deepcopy(coalition);r['geometry']=mapping(g);r['properties'].update(qid='local:anti-chiang-coalition',entityId='local:anti-chiang-coalition',displayName='反蒋联军',validTo=1930,sourceQid='Q717809',identityCorrection='原Q编号指向中原大战事件，现分离为参战军政联合势力。',sourceUrl=COALITION,representationKind='regional-polities',regionalCollection=True,representationNote='1930年反蒋的晋系、西北军、新桂系等联合势力；不是国家名称，图源范围为概化军政势力范围。联军1930年失败后不延续至1931年。',labelPath=label_path(mapping(g),'反蒋联军'));out.append(r)
  pieces=[('Shanxi Military Authorities','晋系军政当局','Shanxi'),('Northwestern Military Authorities','西北地方军政当局','Shaanxi'),('Guangxi Military Authorities','桂系军政当局','Guangxi')];covered=[]
  for n,l,prov in pieces:
   part=clean(g.intersection(province([prov])));covered.append(part)
   if part.is_empty:continue
   q='local:'+n.lower().replace(' ','-');r=copy.deepcopy(coalition);r['geometry']=mapping(part);r['properties'].update(NAME=n,SUBJECTO=n,displayName=l,qid=q,entityId=q,validFrom=1931,validTo=1931,sourceRecord=TAG+':1931:'+n,sourceUrl=COALITION,regionalCollection=True,representationKind='regional-polities',territoryType='administration',sovereignName='Republic of China',sovereignQid='Q13426199',representationNote='反蒋联合失败后的地方军政范围，沿用源1931年范围并按省域概化分列；并非继续存在一个统一的反蒋联军。',labelPath=label_path(mapping(part),l));out.append(r);made.append(n)
  remainder=clean(g.difference(union_all(covered)))
  if not remainder.is_empty:
   for f in out:
    p=f['properties']
    if p['NAME']=='Republic of China'and p['validFrom']==1930 and p['validTo']==1931:
     # Separate the shared source period so the 1930 coalition is not erased.
     r=copy.deepcopy(f);r['properties'].update(validFrom=1931,sourceRecord=TAG+':roc-1931-remainder');r['geometry']=mapping(clean(union_all([shape(r['geometry']),remainder])));p['validTo']=1930;out.append(r);break
  world['features']=out;write('public/data/temporal/19.geojson',world)
 # All same-named Norse rows are geographic multi-polity groups, not a language
 # or the later unified Kingdom of Norway. Keep raw source IDs for review.
 norse_count=0
 for path in list((ROOT/'public/data/temporal').glob('*.geojson'))+list((ROOT/'public/data').glob('world_*.geojson')):
  d=read(path);changed=False
  for f in d['features']:
   p=f.get('properties')or{}
   if p.get('NAME')!='Norse':continue
   p.update(displayName='北欧诸部',sourceQid=p.get('sourceQid',p.get('qid')),qid='local:norse-communities',entityId='local:norse-communities',regionalCollection=True,representationKind='regional-polities',representationNote='诺斯及北日耳曼地域社群的概览，不是语言名称，也不是统一的挪威王国；未证明整个分布区有共同君主。',sourceUrl=NORTH,labelPath=label_path(f['geometry'],'北欧诸部'));norse_count+=1;changed=True
  if changed:write(path,d)
 labels={'Norse':'北欧诸部','Norse Greenland':'格陵兰诺斯聚落','Anti-Kuomintang Coalition':'反蒋联军',**{n:d['label']for n,d in definitions.items()}}
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(path);d.update(labels);write(path,d)
 cur=read('public/data/curated-facts.json');facts=read('public/data/polity-facts.json');cur['relations']=[r for r in cur['relations']if r.get('supplement')!=TAG]
 defs={**definitions,'Anti-Kuomintang Coalition':{'label':'反蒋联军','qid':'local:anti-chiang-coalition','from':1930,'to':1930,'source':COALITION,'note':'晋系、西北军、新桂系等参加的反蒋联合，不是名为“中原大战”的国家。','regional':True},'Norse':{'label':'北欧诸部','qid':'local:norse-communities','from':161,'to':499,'source':NORTH,'note':'北欧及诺斯地域社群，不是挪威语，也不是统一挪威国家。','regional':True}}
 for n,d in defs.items():
  if n=='Qing Dynasty':continue
  q=d['qid'];cur['identities'][n]=q;e=facts['entities'].setdefault(q,{'label':d['label'],'en':n,'description':d['note'],'fields':{}});e['label']=d['label'];facts['labels'][q]=d['label']
  # Our province groups also occur in 1931 after coalition dissolution.
  a,b=d['from'],1931 if n in made else d['to']
  for field,text in [('government','地方军政势力与行政组织；该记录不是另一个主权国家'),('ruler',d.get('person')or('各地君长与地方社群（无适用于全域的共同君主）'if n=='Norse'else'分区军政首领与地方行政机构（非统一共同执政）'))]:
   person_id={'马化龙':'ma-hualong','马文禄':'ma-wenlu'}.get(d.get('person'))
   rows=e['fields'].setdefault(field,[]);rows[:]=[r for r in rows if r.get('supplement')!=TAG];rows.append({'value':'local:person:'+person_id if field=='ruler'and person_id else text,'label':text,'from':a,'to':b,'at':None,'roleLabel':'地方控制方首领'if d.get('person')else'地域与军政集合','kind':'person'if d.get('person')else'collective','citation':[d['source']],'supplement':TAG})
  if d.get('sovereignName')and not d.get('controlArea'):
   rel={'id':TAG+':'+n,'kind':'administration','child':n,'parent':d['sovereignName'],'from':a,'to':b,'detail':'地方行政、军政或自治范围；中华民国的名义国家框架不表示南京或北京政府持续直接控制。','source':d['source'],'supplement':TAG}
   cur['relations']=[r for r in cur['relations']if r.get('id')!=rel['id']]+[rel]
 write('public/data/curated-facts.json',cur);write('public/data/polity-facts.json',facts)
 index=read('public/data/temporal/index.json');allrows=[f for c in index['centuries']for f in read(f'public/data/temporal/{c}.geojson')['features']];index['counts']['polityRecords']=len({f['properties']['sourceRecord']for f in allrows});index['changeYears']=sorted(set(index['changeYears'])|{1930,1931,1932,1946,1947});index['chinaInteriorReview']=TAG;write('public/data/temporal/index.json',index)
 write('public/data/china-interior-name-review.json',{'reviewedAt':'2026-11-01','definitions':defs,'norseRows':norse_count,'postCoalitionGroups':made,'limitations':['省域仅用于定位缺项，不等于历史省界或各军阀的完整控制线。','原有外国占领、租界、西藏和新疆分期不被现代中国遮罩覆盖。','年内政变和军事进退以分期说明呈现，尚非逐月控制图。']});print('China interior and naming repairs',stage.audit.__len__(),'Norse rows',norse_count,flush=True)

if __name__=='__main__':main()
