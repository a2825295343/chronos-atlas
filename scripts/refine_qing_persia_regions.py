"""Fix anachronistic autonomous-region names; add dated Ottoman/Persian locators."""
import hashlib
from collections import defaultdict
from territory_repair_stage import read,write,clean
from shapely.geometry import shape,mapping
from shapely import union_all
TAG='qing-persia-regions-2026-11-02'
GX='https://www.forestry.gov.cn/c/www/dszl/712.jhtml'
def main():
 db=read('public/data/historical-provinces.geojson');db['features']=[f for f in db['features']if f['properties'].get('supplement')!=TAG];corrected=[];added=[]
 for f in db['features']:
  p=f['properties']
  if p.get('country')=='China'and p.get('ownerAny')==['Qing Dynasty']and'广西'in p.get('label',''):
   corrected.append(dict(id=p['id'],previous=p['label']));p.update(label='广西省',native='广西',nameReview=TAG)
 modern=read('public/data/provinces.geojson')['features'];lookup=defaultdict(list)
 for f in modern:lookup[(f['properties']['country'],f['properties']['native'])].append(f)
 def group(country,label,natives,a,b,owners,source,kind='历史行政区名／定位参考'):
  ns=natives.split('|');missing=[n for n in ns if not lookup[(country,n)]]
  if missing:raise ValueError((country,missing))
  fs=[f for n in ns for f in lookup[(country,n)]];g=clean(union_all([shape(f['geometry'])for f in fs]));p=dict(id=TAG+':'+hashlib.sha1(f'{country}:{label}:{a}'.encode()).hexdigest()[:16],country=country,label=label,native=label,validFrom=a,validTo=b,ownerAny=owners,replaces=[f['properties']['id']for f in fs],type=kind,historicalName=True,geographicReference=True,boundaryVisible=False,dataKind='historical-geographic-reference',sourceUrl=source,source='按年代制度与历史地图整理；现代定位单元辅助概化',accuracy='区名及制度按时期选择；范围由现代单元合并，仅为地理核心参考，不是精确历史行政界。',supplement=TAG)
  added.append(dict(type='Feature',properties=p,geometry=mapping(g)))
 owners=['Republic of China',"People's Republic of China",'Communist Party of China']
 for label,native,a,b in [('广西省','Guangxi',1912,1957),('广西僮族自治区','Guangxi',1958,1964),('海南行政区（广东省）','Hainan',1950,1987),('琼崖地区','Hainan',1912,1948),('海南特别行政区','Hainan',1949,1949),('新疆省','Xinjiang',1912,1954),('宁夏省','Ningxia',1929,1953),('宁夏地区（甘肃省）','Ningxia',1954,1957),('西藏地方','Xizang',1912,1964)]:
  # Natural Earth uses Tibet rather than Xizang in this packaged edition.
  if native=='Xizang'and not lookup[('China',native)]:native='Tibet'
  group('China',label,native,a,b,owners,GX)
 ott=['Ottoman Empire'];source='https://islamansiklopedisi.org.tr/vilayet'
 for label,natives,a,b in [
  ('许达文迪加尔州','Bursa|Balikesir|Kütahya|Bilecik',1867,1922),('安卡拉州','Ankara|Çankiri',1867,1922),('艾登州','Izmir|Aydin|Manisa|Denizli',1867,1922),('科尼亚州','Konya|Karaman|Isparta|Burdur',1867,1922),('锡瓦斯州','Sivas|Tokat|Amasya',1867,1922),('特拉布宗州','Trabzon|Rize|Giresun',1867,1922),('埃尔祖鲁姆州','Erzurum|Erzincan',1867,1922),('凡城州','Van|Hakkari',1875,1922),('迪亚巴克尔州','Diyarbakir|Mardin',1867,1922),('阿达纳州','Adana|Mersin|Osmaniye',1869,1922)]:group('Turkey',label,natives,a,b,ott,source)
 for label,natives,a,b in [('巴格达州','Baghdad|Babil|Karbala\'|An-Najaf|Diyala|Wasit',1869,1917),('摩苏尔州','Ninawa|Arbil|Dihok|As-Sulaymaniyah|At-Ta\'mim',1878,1918),('巴士拉州','Al-Basrah|Maysan|Dhi-Qar',1875,1880),('巴士拉州','Al-Basrah|Maysan|Dhi-Qar',1884,1914)]:group('Iraq',label,natives,a,b,ott,source)
 iran='https://www.iranicaonline.org/articles/isfahan-vii-safavid-period/'
 for a,b,os in [(1501,1722,['Safavid Dynasty']),(1789,1925,['Qajar Dynasty'])]:
  for label,natives in [('法尔斯辖区','Fars|Bushehr'),('呼罗珊辖区','North Khorasan|Razavi Khorasan|South Khorasan'),('阿塞拜疆辖区','West Azarbaijan|East Azarbaijan|Ardebil'),('克尔曼辖区','Kerman'),('吉兰辖区','Gilan'),('马赞德兰辖区','Mazandaran'),('胡齐斯坦地区','Khuzestan')]:group('Iran',label,natives,a,b,os,iran)
 group('Iran','伊斯法罕王室地区','Esfahan',1598,1722,['Safavid Dynasty'],iran)
 group('Iran','德黑兰京畿地区','Tehran|Alborz',1789,1925,['Qajar Dynasty'],'https://www.iranicaonline.org/articles/tehran-i-a-persian-city-at-the-foot-of-the-alborz-mountain/')
 db['features']+=added;write('public/data/historical-provinces.geojson',db)
 write('public/data/qing-persia-regions-review.json',dict(reviewedAt='2026-11-02',corrected=corrected,added=len(added),records=[f['properties']for f in added],limitations=['现代定位轮廓不是古代或近代省界，本轮不显示未经核定的精确行政边线。','1958年广西建自治区，当时名称用“僮”，1965年改“壮”。']))
 print('Corrected Qing names',len(corrected),'added dated regions',len(added))
if __name__=='__main__':main()
