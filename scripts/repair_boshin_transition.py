"""Restore Japan's 1868–69 geometry without extending a dissolved shogunate."""
from territory_repair_stage import Stage,read,write,clean
from shapely.geometry import shape,box
from shapely import union_all
TAG='boshin-transition-2026-11-02'
SOURCE='https://www.archives.go.jp/exhibition/digital/henbou/contents/01.html'
HAKODATE='https://www.city.hokuto.hokkaido.jp/bunkazai/data/nen2-1.htm'
def main():
 s=Stage(TAG,[18]);w=s.world(1867);home=clean(w['Tokugawa Shogunate'][1].intersection(box(128,30,146,45.8)))
 kuni=read('public/data/japan-old-provinces.geojson')['features']
 # Approximate member-domain cores, not a rectilinear latitude partition.
 north=clean(union_all([shape(f['geometry'])for f in kuni if f['properties']['id']in ['K28','K29','K30','K31','K32','K33']])).intersection(home)
 ezo=clean(home.intersection(box(139.6,41.35,141.4,43.1)))
 note='戊辰战争年度概览：按战前日本本土轮廓与旧国位置补回源数据空白；年内征服、投降快速变化，不代表某一日的精确战线。'
 for y in [1868,1869]:
  base=s.world(y)['Empire of Japan'][1];target=clean(union_all([home,base]));region=box(128,30,146,45.8)
  assignments=[]
  if y==1868:assignments.append(('Northern Alliance of Japanese Domains','奥羽越列藩同盟','local:jp-northern-alliance',north,SOURCE,note,dict(regionalCollection=True,representationKind='regional-polities',yearConvention='1868年东北诸藩结盟至当年秋陆续投降；此为年内活动范围概览。')))
  assignments.append(('Ezo Island Government','虾夷政权'if y==1869 else'虾夷旧幕府军','local:ezo-government',ezo,HAKODATE,note,dict(yearConvention='1868年秋旧幕府军攻占箱馆；政权于1868年末至1869年上半年存在。仅示渡岛、箱馆附近活动核心，不宣称实际统治整个北海道。')))
  assignments.append(('Empire of Japan','日本','Q188712',target,SOURCE,note,dict(yearConvention='明治新政府与诸藩并存的年度概览；1869年虾夷军投降后当地亦归新政府。',sourceReferenceYear=1867)))
  s.repair(region,y,y,assignments,remove=['Empire of Japan'])
 s.finish('boshin-transition-review.json')
 db=read('public/data/conflicts.json');details=read('public/data/war-details.json');wid='historic-boshin-reviewed'
 # Avoid a second displayed Boshin conflict when a COW record is available.
 existing=next((w for w in db['wars']if w['id'].startswith('cow-')and any(t in w.get('name','')for t in ['Boshin','Meiji Restoration'])),None)
 if existing:
  wid=existing['id'];existing.setdefault('originalParticipants',existing['participants'])
  for p in existing['participants']:
   if p.get('code')=='740':p.update(name='Empire of Japan',polityNames=['Japan'])
   elif p.get('name')=='Tokugawa Bafuku':p.update(name='Former bakufu forces',sourceName='Tokugawa Bafuku')
  db['wars']=[w for w in db['wars']if w['id']!='historic-boshin-reviewed']
 else:db['wars']=[w for w in db['wars']if w['id']!=wid]+[dict(id=wid,name='戊辰战争',category='内战／国内冲突',from_=1868,to=1869,periods=[[1868,1869]],participants=[dict(name=n,side=side,periods=ps)for n,side,ps in [('Empire of Japan','1',[[1868,1869]]),('Northern Alliance of Japanese Domains','2',[[1868,1868]]),('Ezo Island Government','2',[[1868,1869]])]],source='日本国立公文书馆、北斗市年表',url=SOURCE)]
 for w in db['wars']:
  if'from_'in w:w['from']=w.pop('from_')
 details['wars']=[w for w in details['wars']if w['id']not in [wid,'historic-boshin-reviewed']]+[dict(id=wid,title='戊辰战争',reviewedHistorical=True,cause='王政复古与幕府权力移交后，新政府和旧幕府、部分东北诸藩之间围绕政权归属发生武装冲突。',result='新政府军占领江户、击败东北抵抗力量，1869年箱馆旧幕府军投降。各藩随后继续经历版籍奉还和废藩置县。',location=[140.7,38.2],sources=[SOURCE,HAKODATE],forceNote='保留COW所编码的阵营兵力与伤亡口径。列藩同盟与虾夷部队属于旧幕府阵营，不能把它们再与阵营总兵力相加。',extraParticipants=[dict(name=n,side='2',periods=ps,role='旧幕府阵营的地区组织；不另行重复累加阵营兵力')for n,ps in [('Northern Alliance of Japanese Domains',[[1868,1868]]),('Ezo Island Government',[[1868,1869]])]])]
 write('public/data/conflicts.json',db);write('public/data/war-details.json',details)
if __name__=='__main__':main()
