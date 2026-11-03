"""Dated administrative mergers and historical names with explicit geometry quality."""
import hashlib,copy
from collections import defaultdict
from territory_repair_stage import ROOT,read,write,clean
from shapely import union_all
from shapely.geometry import shape,mapping
TAG='world-regions-2026-11-02'
FR='https://www.insee.fr/fr/statistiques/1906658?sommaire=1906743'
BR='https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/14147-asi-publicacao-aborda-evolucao-da-divisao-territorial-brasileira-de-1872-a-2010'
VN='https://archives.org.vn/gioi-thieu-tai-lieu-nghiep-vu/ky-i-dia-gioi-hanh-chinh-viet-nam-thoi-ky-quan-chu.htm'

def main():
 lookup=defaultdict(list)
 for f in read('public/data/provinces.geojson')['features']:lookup[(f['properties']['country'],f['properties']['native'])].append(f)
 db=read('public/data/historical-provinces.geojson');db['features']=[f for f in db['features']if f['properties'].get('supplement')!=TAG];added=[]
 backup=ROOT/'.local/world-regions/base-brazil-regions.json';backup.parent.mkdir(exist_ok=True)
 if not backup.exists():write('.local/world-regions/base-brazil-regions.json',[f for f in db['features']if f['properties']['country']=='Brazil'and f['properties'].get('priority')=='fallback'])
 base=read('.local/world-regions/base-brazil-regions.json');baseids={f['properties']['id']for f in base};db['features']=[f for f in db['features']if f['properties']['id']not in baseids]+base
 def group(country,label,natives,a,b,url,reference=False,owners=None,note=''):
  names=natives.split('|');missing=[n for n in names if not lookup[(country,n)]]
  if missing:raise ValueError((country,missing))
  fs=[f for n in names for f in lookup[(country,n)]];g=clean(union_all([shape(f['geometry'])for f in fs]))
  p=dict(id=TAG+':'+hashlib.sha1(f'{country}:{label}:{a}'.encode()).hexdigest()[:16],label=label,native=label,country=country,replaces=[f['properties']['id']for f in fs],type='历史地区定位参考'if reference else'按行政组合重建的分期区划',validFrom=a,validTo=b,source='区划建立、分合及更名资料；Natural Earth定位几何',sourceUrl=url,sourceYear=None,dataKind='historical-geographic-reference'if reference else'historical-reconstruction',historicalName=True,geographicReference=reference,boundaryVisible=not reference,supplement=TAG,accuracy=('历史名称已有年代依据；轮廓仅为现代单元合并的核心定位，不代表该年精确行政界。'if reference else'按当时行政组合合并底图单元；边线精度为底图概化精度，不是地籍测绘。')+note)
  if reference:p['priority']='fallback'
  if owners:p['ownerAny']=owners
  added.append(dict(type='Feature',properties=p,geometry=mapping(g)))
 # Actual metropolitan administrative regions before and after the 2016 reform.
 old={
 '阿尔萨斯':'Bas-Rhin|Haute-Rhin','阿基坦':'Dordogne|Gironde|Landes|Lot-et-Garonne|Pyrénées-Atlantiques',
 '奥弗涅':'Allier|Cantal|Haute-Loire|Puy-de-Dôme','下诺曼底':'Calvados|Manche|Orne','勃艮第':"Côte-d'Or|Nièvre|Saône-et-Loire|Yonne",
 '布列塔尼':"Côtes-d'Armor|Finistère|Ille-et-Vilaine|Morbihan",'中央':'Cher|Eure-et-Loir|Indre|Indre-et-Loire|Loir-et-Cher|Loiret',
 '香槟-阿登':'Ardennes|Aube|Marne|Haute-Marne','科西嘉':'Haute-Corse|Corse-du-Sud','弗朗什-孔泰':'Doubs|Jura|Haute-Saône|Territoire de Belfort',
 '上诺曼底':'Eure|Seine-Maritime','法兰西岛':"Paris|Seien-et-Marne|Yvelines|Essonne|Hauts-de-Seine|Seine-Saint-Denis|Val-de-Marne|Val-d'Oise",
 '朗格多克-鲁西永':'Aude|Gard|Hérault|Lozère|Pyrénées-Orientales','利穆赞':'Corrèze|Creuse|Haute-Vienne','洛林':'Meurthe-et-Moselle|Meuse|Moselle|Vosges',
 '南部-比利牛斯':'Ariège|Aveyron|Haute-Garonne|Gers|Lot|Hautes-Pyrénées|Tarn|Tarn-et-Garonne','北部-加来海峡':'Nord|Pas-de-Calais',
 '卢瓦尔河地区':'Loire-Atlantique|Maine-et-Loire|Mayenne|Sarthe|Vendée','皮卡第':'Aisne|Oise|Somme','普瓦图-夏朗德':'Charente|Charente-Maritime|Deux-Sèvres|Vienne',
 '普罗旺斯-阿尔卑斯-蓝色海岸':'Alpes-de-Haute-Provence|Hautes-Alpes|Alpes-Maritimes|Bouches-du-Rhône|Var|Vaucluse',
 '罗讷-阿尔卑斯':'Ain|Ardèche|Drôme|Isère|Loire|Rhône|Savoie|Haute-Savoie'}
 for n,parts in old.items():
  if n=='中央':group('France','中央大区',parts,1990,2014,FR);group('France','中央-卢瓦尔河谷大区',parts,2015,2015,FR)
  else:group('France',n+'大区'if n!='科西嘉'else'科西嘉地方行政区',parts,1990,2015,FR)
 new=[('大东部',['阿尔萨斯','香槟-阿登','洛林']),('新阿基坦',['阿基坦','利穆赞','普瓦图-夏朗德']),('奥弗涅-罗讷-阿尔卑斯',['奥弗涅','罗讷-阿尔卑斯']),('诺曼底',['下诺曼底','上诺曼底']),('勃艮第-弗朗什-孔泰',['勃艮第','弗朗什-孔泰']),('奥克西塔尼',['朗格多克-鲁西永','南部-比利牛斯']),('上法兰西',['北部-加来海峡','皮卡第'])]
 for n,parts in new:group('France',n+'大区','|'.join(old[p]for p in parts),2016,2026,FR,note='2016年采用年末已确定名称；年初曾有组合式临时名称。')
 for n in ['布列塔尼','中央','法兰西岛','卢瓦尔河地区','普罗旺斯-阿尔卑斯-蓝色海岸','科西嘉']:
  label='中央-卢瓦尔河谷大区'if n=='中央'else'科西嘉地方行政区'if n=='科西嘉'else n+'大区';group('France',label,old[n],2016,2026,FR)
 # India's 2000 reorganisation, 2014 Telangana and 2019 Jammu/Ladakh split.
 india='https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=18420'
 for n,parts in [('比哈尔邦','Bihar|Jharkhand'),('中央邦','Madhya Pradesh|Chhattisgarh'),('北方邦','Uttar Pradesh|Uttarakhand')]:group('India',n,parts,1956,1999,india)
 for n,native in [('比哈尔邦','Bihar'),('贾坎德邦','Jharkhand'),('中央邦','Madhya Pradesh'),('恰蒂斯加尔邦','Chhattisgarh'),('北方邦','Uttar Pradesh')]:group('India',n,native,2000,2026,india)
 group('India','北安查尔邦','Uttarakhand',2000,2006,'https://agriculture.uk.gov.in/about-department/introduction/');group('India','北阿坎德邦','Uttarakhand',2007,2026,'https://agriculture.uk.gov.in/about-department/introduction/')
 tel='https://www.telangana.gov.in/About/State-Profile/'
 group('India','安得拉邦','Andhra Pradesh|Telangana',1956,2013,tel);group('India','安得拉邦','Andhra Pradesh',2014,2026,tel);group('India','特伦甘纳邦','Telangana',2014,2026,tel)
 jk='https://www.indiacode.nic.in/indiacode/handle/123456789/12030?sam_handle=123456789%2F1362&view_type=search'
 group('India','查谟和克什米尔邦（印度管辖部分）','Jammu and Kashmir|Ladakh',1956,2018,jk)
 group('India','查谟和克什米尔中央直辖区','Jammu and Kashmir',2019,2026,jk);group('India','拉达克中央直辖区','Ladakh',2019,2026,jk)
 group('India','孟买邦','Maharashtra|Gujarat',1956,1959,'https://dgipr.maharashtra.gov.in/sites/default/files/2020-08/MAhead-MAY%202012.pdf')
 # Brazil: operational administrative dates, not just promulgation of laws.
 group('Brazil','马托格罗索州','Mato Grosso|Mato Grosso do Sul',1970,1978,BR,note='南马托格罗索1977年立法设州，1979年正式安装行政机构；此处按行政运行分期。')
 group('Brazil','马托格罗索州','Mato Grosso',1979,2026,BR);group('Brazil','南马托格罗索州','Mato Grosso do Sul',1979,2026,BR)
 group('Brazil','戈亚斯州','Goiás|Tocantins',1960,1987,BR);group('Brazil','戈亚斯州','Goiás',1988,2026,BR);group('Brazil','托坎廷斯州','Tocantins',1988,2026,BR,note='1988年宪法设州，首届州政府1989年开始运行。')
 for native,zh,a,b in [('Roraima','里奥布朗库联邦领地',1943,1961),('Roraima','罗赖马联邦领地',1962,1987),('Roraima','罗赖马州',1988,2026),('Rondônia','瓜波雷联邦领地',1943,1955),('Rondônia','朗多尼亚联邦领地',1956,1981),('Rondônia','朗多尼亚州',1982,2026),('Amapá','阿马帕联邦领地',1943,1987),('Amapá','阿马帕州',1988,2026),('Acre','阿克里联邦领地',1904,1961),('Acre','阿克里州',1962,2026)]:group('Brazil',zh,native,a,b,BR,reference=a<1982)
 # Imperial provinces: locating cores, not retrospective modern state borders.
 for zh,parts,a in [('巴伊亚省','Bahia',1822),('伯南布哥省','Pernambuco',1822),('马拉尼昂省','Maranhão',1822),('皮奥伊省','Piauí',1822),('塞阿拉省','Ceará',1822),('里约热内卢省','Rio de Janeiro',1822),('米纳斯吉拉斯省','Minas Gerais',1822),('圣卡塔琳娜省','Santa Catarina',1822),('圣佩德罗-南里奥格兰德省','Rio Grande do Sul',1822),('巴拉那省','Paraná',1853),('亚马孙省','Amazonas|Roraima',1850)]:group('Brazil',zh,parts,a,1888,BR,reference=True)
 group('Brazil','圣保罗省','São Paulo|Paraná',1822,1852,BR,reference=True);group('Brazil','圣保罗省','São Paulo',1853,1888,BR,reference=True)
 # Nguyen reform: omit exact boundaries because the supplied cells are modern.
 owners=['Nguyễn dynasty','Nguyen Dynasty','French Indochina','France Colony - Vietnam']
 for label,parts,a,b in [
  ('河内省','Ha Noi|Hà Nam',1831,1883),('南定省','Nam Định|Thái Bình',1831,1883),('宁平省','Ninh Bình',1831,1883),('清化省','Thanh Hóa',1831,1883),('乂安省','Nghệ An',1831,1883),
  ('承天府','Thừa Thiên - Huế',1832,1883),('广治省','Quảng Trị',1831,1883),('广平省','Quảng Bình',1831,1883),('广南省','Quàng Nam|Đà Nẵng',1832,1883),('广义省','Quảng Ngãi',1832,1883),('平定省','Bình Định',1832,1883),('富安省','Phú Yên',1832,1883),('庆和省','Khánh Hòa',1832,1883),('平顺省','Bình Thuận|Ninh Thuận',1832,1883),
  ('藩安省','Hồ Chí Minh city|Long An|Tây Ninh',1832,1835),('嘉定省','Hồ Chí Minh city|Long An|Tây Ninh',1836,1861),('边和省','Bình Phước|Bình Dương|Đông Nam Bộ|Bà Rịa - Vũng Tàu',1832,1861),('定祥省','Tiền Giang',1832,1861),('永隆省','Vĩnh Long|Bến Tre|Trà Vinh',1832,1866),('安江省','An Giang|Ðong Tháp|Can Tho|Sóc Trăng|Hau Giang',1832,1866),('河仙省','Kiên Giang|Cà Mau|Bạc Liêu',1832,1866)]:group('Vietnam',label,parts,a,b,VN,True,owners)
 # Historical Burmese geographic/administrative cores without invented lines.
 burma='https://www.nam.ac.uk/explore/timeline-burma-army'
 group('Myanmar','阿拉干专区','Rakhine',1826,1936,burma,True)
 group('Myanmar','丹那沙林专区核心','Tanintharyi|Mon',1826,1936,burma,True)
 group('Myanmar','勃固专区核心','Bago|Yangon|Ayeyarwady',1853,1861,burma,True)
 # New dated province names supersede earlier broad locators. Split the old
 # periods and subtract only the active replacement, retaining uncovered cores.
 refined=[];db['features']=[f for f in db['features']if f['properties']['id']not in baseids]
 for f in base:
  p=f['properties'];a,b=p['validFrom'],p['validTo'];relevant=[x for x in added if x['properties']['country']=='Brazil'and set(x['properties']['replaces'])&set(p.get('replaces',[]))and x['properties']['validFrom']<=b and x['properties']['validTo']>=a]
  if not relevant:db['features'].append(f);continue
  stops=sorted({a,b+1,*[max(a,x['properties']['validFrom'])for x in relevant],*[min(b+1,x['properties']['validTo']+1)for x in relevant]})
  for lo,end in zip(stops,stops[1:]):
   cuts=[shape(x['geometry'])for x in relevant if x['properties']['validFrom']<=lo<=x['properties']['validTo']];g=clean(shape(f['geometry']).difference(union_all(cuts)))if cuts else shape(f['geometry'])
   if g.is_empty:continue
   z=copy.deepcopy(f);z['geometry']=mapping(g);z['properties'].update(id=p['id']+':refined:'+str(lo),sourceRegionId=p['id'],sourceSupplement=p.get('supplement'),supplement=TAG,validFrom=lo,validTo=end-1);refined.append(z)
 db['features']+=refined+added;write('public/data/historical-provinces.geojson',db)
 write('public/data/world-regions-review.json',dict(reviewedAt='2026-11-02',tag=TAG,added=len(added),administrativeReconstructions=sum(not f['properties']['geographicReference']for f in added),geographicReferences=sum(f['properties']['geographicReference']for f in added),records=[f['properties']for f in added],limitations=['法国大区与印度、巴西部分现代行政组合可据底图合并；底图仍经概化。','越南、巴西帝国及早期缅甸只显示有年代依据的地名与定位核心，未绘未经核定的精确省界。','不将争议地区的行政管理范围等同于国际承认的主权边界。']))
 print('Added dated divisions',len(added))
if __name__=='__main__':main()
