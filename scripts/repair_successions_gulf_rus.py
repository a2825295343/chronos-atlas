"""Bounded territorial repairs. Reads this revision's backup, not older stages."""
import copy,hashlib
from territory_repair_stage import ROOT,Stage,read,write,clean,label_path
from shapely.geometry import shape,mapping,box
from shapely import union_all
TAG='successions-gulf-rus-2026-11-02'
GULF='https://u.ae/en/about-the-uae/History'
OMAN='https://qdl.qa/en/historical-profile-oman'
HU='https://digitallibrary.un.org/record/712474'
SHAAN='https://zh.wikisource.org/wiki/清史稿/卷215'

def main():
 s=Stage(TAG,[11,12,16,18,19,20]);admin=read('.local/presentation/admin0.geojson')['features']
 def country(n):return clean(union_all([shape(f['geometry'])for f in admin if f['properties']['NAME_EN']==n]))
 provinces=read('public/data/provinces.geojson')['features']
 def province(c,n):return clean(union_all([shape(f['geometry'])for f in provinces if f['properties']['country']==c and f['properties']['native']==n]))
 def merge(names,name,label,q,a,b,note,source,props=None):
  stops=sorted({a,b+1,*[max(a,y)for f in s.rows if f['properties']['NAME']in names for y in [f['properties']['validFrom'],f['properties']['validTo']+1]if a<=y<=b+1]})
  for lo,end in zip(stops,stops[1:]):
   w=s.world(lo);fs=[(p,g)for n,(p,g)in w.items()if n in names]
   if not fs:continue
   g=clean(union_all([g for p,g in fs]));p=copy.deepcopy(fs[0][0])
   for n in names:s.replaced[n].append((lo,end-1))
   for k in ['sovereignName','sovereignQid','territoryType','memberOf','components']:p.pop(k,None)
   p.update(NAME=name,SUBJECTO=name,qid=q,entityId=q,displayName=label,sourceName=p.get('sourceName',fs[0][0]['NAME']),sourceQid=p.get('sourceQid',fs[0][0].get('qid')),validFrom=lo,validTo=end-1,sourceRecord=TAG+':merge:'+hashlib.sha1(f'{name}:{lo}:{end}'.encode()).hexdigest()[:15],chronologyPatch=TAG,sourceUrl=source,accuracy=note,labelPath=label_path(g,label),**(props or{}))
   s.new.append(dict(type='Feature',properties=p,geometry=mapping(g)));s.identities[name]=q;s.labels[name]=label
 # Austria-Hungary did not return in 1956. The mistaken identity describes
 # a Hungary-shaped source row; preserve Hungary and record the revolution.
 hungary=country('Hungary')
 s.replaced['Hungarian Nationalists'].append((1956,1957))
 for y in [1949,1956,1957]:
  note='1949年8月改制为人民共和国，年内前段仍为第二共和国。年度概览沿用战后匈牙利轮廓。'if y==1949 else'1956年革命及苏军干预造成短期多方控制与政府更替；本年国家为匈牙利，不是奥匈帝国。此图不伪造每日战线。'if y==1956 else'1957年为卡达尔政府统治下的匈牙利；源数据误标的“民族主义者／奥匈帝国”轮廓已纠正。'
  s.repair(hungary,y,y,[("Hungarian People's Republic",'匈牙利','Q16410',hungary,HU,note,{})],remove=['Hungarian Nationalists',"Hungarian People's Republic",'Second Hungarian Republic'])
 s.replaced['Hungarian Nationalists'].append((1956,1957))
 # Hainan's 1951–52 blank followed removal from the ROC but no replacement.
 hainan=province('China','Hainan')
 for y in [1950,1951,1952]:s.repair(hainan,y,y,[("People's Republic of China",'中国','Q148',hainan,'https://www.hainan.gov.cn/hainan/sq/','1950年5月海南岛主要战事结束，按年末代表状态归入中华人民共和国；1951—1952年补齐遗漏。此处不将海南省这一1988年名称前推。',{})],remove=['Republic of China'])
 # The Hanzhong–Xing'an gap is a contested transition, not uninhabited land.
 south=province('China','Shaanxi').intersection(box(105,31.5,111.2,33.8))
 for y in [1645,1646,1647]:
  assignments=[]
  if y==1645:assignments=[('Southern Shaanxi Anti-Qing Forces','陕南抗清诸军','local:shaanxi-resistance-1645',south,SHAAN,'1645年贺珍等先降清、年底反清；取年末抗清活动范围作概化。不是统一国家，未宣称各地全年均由同一军控制。',{'regionalCollection':True})]
  elif y==1646:
   assignments=[('Southern Shaanxi Anti-Qing Forces','陕南抗清诸军','local:shaanxi-resistance-1645',south.intersection(box(108.2,31.5,111.2,33.8)),SHAAN,'1646年清军进入汉中后，贺珍、孙守法等转向兴安、秦岭一带；此轮廓为地理核心概化，分界不是实测战线。',{'regionalCollection':True}),('Qing Dynasty','清朝','Q8733',south,SHAAN,'1646年清军进入汉中，东部仍有抗清军事活动；年度概览不表示全年控制不变。',{})]
  else:assignments=[('Qing Dynasty','清朝','Q8733',south,SHAAN,'1647年清军继续平定兴安与秦岭抗清武装；年度代表状态归清，不据此否定年内战事或地方抵抗。',{})]
  s.repair(south,y,y,assignments)
 # One Al Busaidi state was imported under multiple names. Keep its parts
 # together; the autonomous 1913 imamate remains a separate polity.
 merge({'Sultanate of Oman','Omani Al Busaidi State','Sultanate of Muscat and Oman','United Kingdom Colony - Oman'},'Sultanate of Muscat and Oman','马斯喀特和阿曼','Q157734',1744,1946,'合并同一阿勒赛义德政权的不同源记录；英国军事及外交影响不等于阿曼是直接殖民地。1856年后的东非继承另行分列；未把1913年内陆伊玛目国并入。',OMAN)
 # Existing colonies in the Gulf are local sheikhdoms with treaty relations.
 for c,old,local,zh,q,begin,indep,url in [
  ('Kuwait','United Kingdom Colony - Kuwait','Sheikhdom of Kuwait','科威特','Q817',1899,1961,'https://e.gov.kw/sites/kgoenglish/Pages/Visitors/AboutKuwait/GoverningBodyOverView.aspx'),
  ('Bahrain','United Kingdom Colony - Bahrain','Sheikhdom of Bahrain','巴林','Q398',1820,1971,'https://history.state.gov/countries/bahrain')]:
  region=country(c);localid='local:'+c.lower()+'-sheikhdom'
  s.replaced[old].append((begin,2024))
  for a,b in s.periods(region,begin,2024,[indep,2002]):
   historic=a<indep;name=local if historic else'State of Kuwait'if c=='Kuwait'else'State of Bahrain'if a<2002 else'Kingdom of Bahrain'
   extra={'sovereignName':'United Kingdom','sovereignQid':'Q145','territoryType':'protectorate'}if historic else{}
   note=('由本地统治者治理的酋长国，与英国有条约关系，非英国直接殖民省。'if historic else f'{indep}年终止英国保护关系；独立后的地图不再延续英国殖民标签。')+'外沿为现代地理定位参考，争议边界未作逐年测绘。'
   s.repair(region,a,b,[(name,zh,localid if historic else q,region,url,note,extra)],remove=[old,local,'State of '+c,'Kingdom of '+c])
 # Seven sheikhdoms, rather than a fictional single country called "Truce".
 uae=country('United Arab Emirates');emirates={f['properties']['native']:shape(f['geometry'])for f in provinces if f['properties']['country']=='United Arab Emirates'}
 s.replaced['Trucial States'].append((1820,1971));s.replaced['United Kingdom Colony - United Arab Emirates'].append((1820,2024))
 specs=[('Abu Dhabi','Abu Dhabi','阿布扎比'),('Dubay','Dubai','迪拜'),('Sharjah','Sharjah','沙迦'),('Umm Al Qaywayn','Umm Al Quwain','乌姆盖万'),('Ajman','Ajman','阿治曼'),('Ras Al Khaymah','Ras Al Khaimah','哈伊马角'),('Fujayrah','Fujairah','富查伊拉')]
 for a,b in s.periods(uae,1820,2024,[1833,1869,1892,1900,1901,1921,1952,1971,1972]):
  rows=[]
  if a>=1972:rows=[('United Arab Emirates','阿联酋','Q878',uae,GULF,'1971年六酋长国建国，哈伊马角于1972年加入。清除独立后仍残留的英国殖民地记录；外沿为现代定位参考。',{})]
  else:
   six=[]
   for native,eng,zh in specs:
    name=eng
    if eng=='Dubai'and a<1833:name='Abu Dhabi'
    if eng=='Fujairah'and a<1901:name='Sharjah'
    if eng=='Ras Al Khaimah'and(a<1869 or 1900<=a<1921):name='Sharjah'
    if a==1971 and eng!='Ras Al Khaimah':six.append(emirates[native]);continue
    display=next(z for _,e,z in specs if e==name);ident='local:trucial-'+name.lower().replace(' ','-')
    extra={'sovereignName':'United Kingdom','sovereignQid':'Q145','territoryType':'protectorate'}if a>=1892 else{}
    rows.append(('Sheikhdom of '+name,display+'酋长国',ident,emirates[native],GULF,'停战海岸诸酋长国分别展示；英国海上条约与1892年排他安排不等于合并成单一国家。范围采用现代酋长国定位单元概化，不是精确历史边界；部分小附属领地尚未分列。',extra))
   if six:rows.insert(0,('United Arab Emirates','阿联酋','Q878',clean(union_all(six)),GULF,'1971年12月六酋长国成立联邦；哈伊马角于1972年加入。年度图取年底代表状态。',{}))
  s.repair(uae,a,b,rows,remove=['United Arab Emirates','Trucial States','United Kingdom Colony - United Arab Emirates'])
 # Other Arab independence residues: retire their entire stale record, then
 # transfer only its claimed footprint, never a whole present-day country.
 for old,cut,c,targets in [
  ('United Kingdom Colony - Iraq',1932,'Iraq',[(1932,1957,'Kingdom of Iraq','Q149805'),(1958,2024,'Iraqi Republic','Q796')]),
  ('United Kingdom Colony - Jordan',1946,'Jordan',[(1946,2024,'Kingdom of Jordan','Q810')]),
  ('United Kingdom Colony - Yemen',1967,'Yemen',[(1967,1969,"People's Republic of Southern Yemen",'Q199841'),(1970,1989,"People's Democratic Republic of Yemen",'Q199841'),(1990,2024,'Republic of Yemen','Q805')]),
  ('United Kingdom Colony - Saudi Arabia',1932,'Saudi Arabia',[(1932,2024,'Saudi Arabia','Q851')])]:
  independence_source={'Iraq':'https://history.state.gov/countries/iraq','Jordan':'https://history.state.gov/countries/jordan','Yemen':'https://history.state.gov/historicaldocuments/frus1964-68v21/d117','Saudi Arabia':'https://history.state.gov/countries/saudi-arabia'}[c]
  independence_note='沙特阿拉伯1932年定名；不能把这一本国地区记为英国殖民地。只补原记录的本国地理范围，保留其他既有势力。'if c=='Saudi Arabia'else'清除独立后错误延续的英国殖民地区；只补原记录的本国地理范围，保留其他既有势力。'
  mask=country(c);oldfs=[g for f,g in zip(s.rows,s.geoms)if f['properties']['NAME']==old];region=clean(union_all(oldfs).intersection(mask))
  if region.is_empty:continue
  s.replaced[old].append((cut,2024))
  for a,b in s.periods(region,cut,2024,[r[0]for r in targets]):
   target=next((r for r in targets if r[0]<=a<=r[1]),None)
   if not target:continue
   _,_,n,q=target;s.repair(region,a,b,[(n,{'Iraq':'伊拉克','Jordan':'约旦','Yemen':'也门','Saudi Arabia':'沙特阿拉伯'}[c],q,region,independence_source,independence_note,{})],remove=[old])
  s.replaced[old].append((cut,2024))
 # Kievan Rus' was an umbrella source overlapping its independent successors.
 rusnames={"Kievan Rus'"}
 source='https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5CK%5CY%5CKyivanRushDA.htm'
 rs=[g for f,g in zip(s.rows,s.geoms)if f['properties']['NAME']in rusnames]
 if rs:
  region=clean(union_all(rs));bounds=region.bounds
  for a,b in s.periods(region,1132,1240):
   w=s.world(a);old=w.get("Kievan Rus'")
   if not old:continue
   others=[g for n,(p,g)in w.items()if n!="Kievan Rus'"and not(g.bounds[2]<bounds[0]or g.bounds[0]>bounds[2]or g.bounds[3]<bounds[1]or g.bounds[1]>bounds[3])]
   g=clean(old[1].difference(union_all(others)));s.replaced["Kievan Rus'"].append((a,b))
   if not g.is_empty:s.repair(region,a,b,[('Unseparated Rus Principalities','罗斯诸地','local:rus-unseparated',g,source,'1132年后为分裂时期的罗斯诸公国。已分列的基辅、切尔尼戈夫、梁赞、诺夫哥罗德等不被此层覆盖；剩余区域尚缺细界，不表示存在统一的基辅罗斯国家。',{'regionalCollection':True,'representationKind':'regional-collection','mapLabel':'罗斯诸地'})])
 s.finish('successions-gulf-rus-review.json')
 # Explicit metadata-only identity corrections also affect the earlier rows.
 replacements={'Imamate of Yemen':('也门伊玛目国','local:yemen-imamate-1814'),'Qasimids':('卡西姆伊玛目国','local:qasimid-yemen'),'Principality of Chernigov':('切尔尼戈夫公国','local:chernigov-principality'),'Principality of Ryazan':('梁赞公国','local:ryazan-principality'),'Omani Slave Coast':('阿曼东非属地','local:omani-east-africa'),"People's Republic of Zanzibar":('桑给巴尔苏丹国','local:zanzibar-sultanate')}
 review=[]
 for century in [11,12,13,16,17,18,19]:
  path=f'public/data/temporal/{century}.geojson';db=read(path);changed=False
  for f in db['features']:
   p=f['properties'];n=p['NAME']
   if n not in replacements:continue
   if n=="People's Republic of Zanzibar"and p['validFrom']>=1964:continue
   zh,q=replacements[n];p.update(sourceQid=p.get('sourceQid',p.get('qid')),qid=q,entityId=q,displayName=zh,identityReviewed=True);changed=True;review.append(dict(name=n,qid=q))
   if n=='Omani Slave Coast':p.update(sovereignName='Sultanate of Muscat and Oman',sovereignQid='Q157734',territoryType='overseas')
  if changed:write(path,db)
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  d=read(path);d.update({n:zh for n,(zh,q)in replacements.items()if n!="People's Republic of Zanzibar"});write(path,d)
 cur=read('public/data/curated-facts.json');cur['identities'].update({n:q for n,(zh,q)in replacements.items()if n!="People's Republic of Zanzibar"});write('public/data/curated-facts.json',cur)
 report=read('public/data/successions-gulf-rus-review.json');report['metadataCorrections']=review;write('public/data/successions-gulf-rus-review.json',report)

if __name__=='__main__':main()
