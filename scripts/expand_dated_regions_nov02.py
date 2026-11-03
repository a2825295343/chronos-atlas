"""Dated names and merged locator regions. Unverified boundaries stay hidden."""
import hashlib,copy
from collections import defaultdict
from territory_repair_stage import read,write,clean
from shapely import union_all
from shapely.geometry import shape,mapping
TAG='dated-regions-2026-11-02'
KOREA='https://encykorea.aks.ac.kr/Article/E0059718'
NZ='https://teara.govt.nz/en/interactive/35476/new-zealands-provinces-1853-1876'

def main():
 modern=read('public/data/provinces.geojson')['features'];lookup=defaultdict(list)
 for f in modern:lookup[(f['properties']['country'],f['properties']['native'])].append(f)
 db=read('public/data/historical-provinces.geojson');db['features']=[f for f in db['features']if f['properties'].get('supplement')!=TAG];added=[]
 def group(country,label,parts,a,b,source,owners=None,kind='历史地理区'):
  fs=[f for c,natives in parts for n in natives.split('|')for f in lookup[(c,n)]]
  missing=[(c,n)for c,natives in parts for n in natives.split('|')if not lookup[(c,n)]]
  if missing:raise ValueError(missing)
  g=clean(union_all([shape(f['geometry'])for f in fs]));p=dict(id=TAG+':'+hashlib.sha1(f'{country}:{label}:{a}'.encode()).hexdigest()[:16],label=label,native=label,country=country,replaces=[f['properties']['id']for f in fs],type=kind,validFrom=a,validTo=b,source='分期名称及制度资料；现代地理合并定位',sourceUrl=source,sourceYear=None,dataKind='historical-geographic-reference',historicalName=True,geographicReference=True,boundaryVisible=False,priority='fallback',accuracy='名称及分合按标注年代选择；范围由现代定位单元合并，是概化地理参照，不是当年精确行政分界。',supplement=TAG)
  if owners:p['ownerAny']=owners
  added.append(dict(type='Feature',properties=p,geometry=mapping(g)))
 def korea(label,parts,a,b):group('Korea',label,parts,a,b,KOREA,['Joseon','Korean Empire','Empire of Japan'],kind='历史道名／定位参考')
 south='South Korea';north='North Korea'
 cores=[('京畿道',[(south,'Gyeonggi|Incheon|Seoul')]),('江原道',[(south,'Gangwon'),(north,'Kangwŏn-do')]),('忠清道',[(south,'North Chungcheong|South Chungcheong|Daejeon|Sejong')]),('全罗道',[(south,'North Jeolla|South Jeolla|Gwangju|Jeju')]),('庆尚道',[(south,'North Gyeongsang|South Gyeongsang|Daegu|Busan|Ulsan')]),('黄海道',[(north,'Hwanghae-bukto|Hwanghae-namdo')]),('平安道',[(north,"P'yŏngan-bukto|P'yŏngan-namdo|P'yŏngyang|Chagang-do")])]
 for label,parts in cores:korea(label,parts,1416,1894)
 ham=[(north,'Hamgyŏng-bukto|Hamgyŏng-namdo|Rasŏn')]
 for a,b,label in [(1416,1469,'咸吉道'),(1470,1508,'永安道'),(1509,1894,'咸镜道')]:korea(label,ham,a,b)
 # 1895 abolished the eight administrative provinces. Do not falsely keep
 # calling the older areas administrative units during the 23-bu interval.
 for label,parts in [*cores,('咸镜道',ham)]:korea(label.removesuffix('道')+'旧域（府制时期地理参照）',parts,1895,1895)
 split=[('京畿道',[(south,'Gyeonggi|Incheon|Seoul')]),('江原道',[(south,'Gangwon'),(north,'Kangwŏn-do')]),('忠清北道',[(south,'North Chungcheong')]),('忠清南道',[(south,'South Chungcheong|Daejeon|Sejong')]),('全罗北道',[(south,'North Jeolla')]),('全罗南道',[(south,'South Jeolla|Gwangju|Jeju')]),('庆尚北道',[(south,'North Gyeongsang|Daegu')]),('庆尚南道',[(south,'South Gyeongsang|Busan|Ulsan')]),('黄海道',[(north,'Hwanghae-bukto|Hwanghae-namdo')]),('平安北道',[(north,"P'yŏngan-bukto|Chagang-do")]),('平安南道',[(north,"P'yŏngan-namdo|P'yŏngyang")]),('咸镜北道',[(north,'Hamgyŏng-bukto|Rasŏn')]),('咸镜南道',[(north,'Hamgyŏng-namdo')])]
 for label,parts in split:korea(label,parts,1896,1944)
 group('Korea','白头山边地',[(north,'Ryanggang')],1416,1944,KOREA,['Joseon','Korean Empire','Empire of Japan'])
 def nz(label,natives,a,b,kind='历史省名／定位参考'):group('New Zealand',label,[('New Zealand',natives)],a,b,NZ,kind=kind)
 nz('奥克兰省','Northland|Auckland|Waikato|Bay of Plenty|Gisborne District|Three Kings Islands',1853,1876)
 nz('新普利茅斯省','Taranaki',1853,1858);nz('塔拉纳基省','Taranaki',1859,1876)
 nz('惠灵顿省','Wellington|Manawatu-Wanganui|Hawke\'s Bay',1853,1857)
 nz('惠灵顿省','Wellington|Manawatu-Wanganui',1858,1876);nz('霍克斯湾省',"Hawke's Bay",1858,1876)
 nz('纳尔逊省','Nelson City|Tasman District|Marlborough District',1853,1858)
 nz('纳尔逊省','Nelson City|Tasman District',1859,1876);nz('马尔堡省','Marlborough District',1859,1876)
 nz('坎特伯雷省','Canterbury|West Coast',1853,1867);nz('坎特伯雷省','Canterbury',1868,1876)
 nz('韦斯特兰县','West Coast',1868,1872,'历史县名／定位参考');nz('韦斯特兰省','West Coast',1873,1876)
 for a,b in [(1853,1860),(1870,1876)]:nz('奥塔哥省','Otago|Southland',a,b)
 nz('奥塔哥省','Otago',1861,1869);nz('南地省','Southland',1861,1869)
 # Areas familiar to the reviewed monarchs, without inventing administrative
 # provinces for ethnic and geographic landscapes.
 source='https://www.unesco.org/en/general-history-africa'
 for label,natives in [('伊默里纳高地','Analamanga|Itasy|Vakinankaratra|Bongolava'),('贝齐寮高地','Haute Matsiatra|Amoron\'i Mania|Ihorombe'),('梅纳贝','Menabe'),('博伊纳','Boeny|Betsiboka|Sofia'),('贝齐米萨拉卡海岸','Analanjirofo|Atsinanana|Alaotra-Mangoro')]:group('Madagascar',label,[('Madagascar',natives)],1700,1896,source)
 for label,natives in [('加奥地区','Gao'),('廷巴克图地区','Timbuktu'),('马西纳地区','Mopti'),('曼丁核心地区','Koulikoro|Bamako'),('塞古地区','Ségou')]:group('Mali',label,[('Mali',natives)],1500,1899,source)
 for label,natives in [('马斯喀特','Muscat'),('巴提奈沿海','Al Batnah North|Al Batnah South'),('阿曼内陆','Ad Dakhliyah|Al Dhahira'),('东部地区','Ash Sharqiyah North|Ash Sharqiyah South'),('佐法尔','Dhofar'),('穆桑代姆','Musandam')]:group('Oman',label,[('Oman',natives)],1913,1970,'https://www.qdl.qa/en/financial-troubles-said-bin-taimur')
 group('Qatar','卡塔尔半岛', [('Qatar','Ar Rayyān|Al Wakrah|Ad Dawhah|Al Daayen|Al Khawr|Madinat ach Shamal|Umm Salal')],1868,1971,'https://diwan.gov.qa/en/About-Qatar/History-of-Qatar')
 db['features']+=added;write('public/data/historical-provinces.geojson',db)
 write('public/data/dated-regions-nov02-review.json',dict(reviewedAt='2026-11-02',added=len(added),countries=sorted({f['properties']['country']for f in added}),records=[f['properties']for f in added],limitations=['现代单元合并仅作空间定位；本轮未将未经核定的行政分界画成精确历史边界。','朝鲜1895年23府的精确界线未收录，显示旧道地理区并注明当时已改府制。','新西兰旧省与现代地区边界不完全重合，轮廓只是概化参照。']))
 print('Added dated regions',len(added))

if __name__=='__main__':main()
