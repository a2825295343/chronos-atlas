"""Dated historical gazetteer regions, explicitly distinct from surveyed borders.

Large geographic regions are preferable to inventing thousands of ancient
administrative units. Names are period-specific; modern locator cells are
merged into broader historical regions. Existing better geometry wins.
"""
import hashlib
from collections import defaultdict
from territory_repair_stage import ROOT,read,write,clean
from shapely.geometry import shape,mapping,box
from shapely import union_all
TAG='global-historical-regions-2026-11-02'
ATLAS='https://maps.lib.utexas.edu/maps/historical/shepherd_1911/'
ROMAN='https://awmc.unc.edu/wordpress/'
DOMESDAY='https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/domesday-book/'
SPAIN='https://www.boe.es/gazeta/dias/1833/12/03/pdfs/GMD-1833-154.pdf'
LOC='https://guides.loc.gov/ottoman-turkish/maps'
AFRICA='https://www.unesco.org/en/general-history-africa'
AMERICAS='https://www.loc.gov/collections/discovery-and-exploration/'
def main():
 modern=read('public/data/provinces.geojson')['features'];lookup=defaultdict(list)
 for f in modern:lookup[(f['properties']['country'],f['properties']['native'])].append(f)
 historical=read('public/data/historical-provinces.geojson');kept=[f for f in historical['features']if f['properties'].get('supplement')!=TAG];added=[];missed=[]
 for f in kept:
  p=f['properties']
  if p['country']=='Japan'and p.get('ownerAny')and p.get('validTo')==1868:
   p['ownerAny']=list(dict.fromkeys([*p['ownerAny'],'Northern Alliance of Japanese Domains','Ezo Island Government']))
 def group(country,label,natives,a,b,source=ATLAS,kind='历史地理区',clip=None):
  names=natives.split('|');fs=[f for n in names for f in lookup.get((country,n),[])]
  missed.extend((country,n)for n in names if (country,n)not in lookup)
  if not fs:return
  g=clean(union_all([clean(shape(f['geometry']))for f in fs]));g=clean(g.intersection(clip))if clip is not None else g
  if g.is_empty:return
  p=dict(id=TAG+':'+hashlib.sha1(f'{country}:{label}:{a}'.encode()).hexdigest()[:14],label=label,native=label,country=country,replaces=[f['properties']['id']for f in fs],type=kind,validFrom=a,validTo=b,source='历史地图与分区地名整理；现代底图辅助定位',sourceUrl=source,dataKind='historical-geographic-reference',historicalName=True,geographicReference=True,boundaryVisible=False,accuracy='名称按本条时期核对；轮廓是合并现代定位地块的概化参考，不声称这是当年的精确行政界，也不表示一个独立国家。',supplement=TAG)
  added.append(dict(type='Feature',properties=p,geometry=mapping(g)))
 def series(country,a,b,groups,source=ATLAS):
  for label,natives in groups:group(country,label,natives,a,b,source)
 # Britain: modern boroughs are merged back into the older county context.
 uk=[('肯特郡','Kent|Medway'),('埃塞克斯郡','Essex|Southend-on-Sea|Thurrock'),('萨福克郡','Suffolk'),('诺福克郡','Norfolk'),('剑桥郡','Cambridgeshire|Peterborough'),('林肯郡','Lincolnshire|North Lincolnshire|North East Lincolnshire'),('约克郡','North Yorkshire|East Riding of Yorkshire|York|Kingston upon Hull|Leeds|Bradford|Calderdale|Kirklees|Wakefield|Barnsley|Doncaster|Rotherham|Sheffield|Middlesbrough|Redcar and Cleveland'),('兰开夏郡','Lancashire|Blackpool|Blackburn with Darwen|Manchester|Liverpool|Sefton|Knowsley|St. Helens|Wigan|Bolton|Bury|Rochdale|Oldham|Salford|Trafford|Tameside'),('柴郡','Cheshire West and Chester|Cheshire East|Warrington|Halton|Stockport|Wirral'),('什罗普郡','Shropshire|Telford and Wrekin'),('伍斯特郡','Worcestershire|Dudley'),('沃里克郡','Warwickshire|Birmingham|Coventry|Solihull'),('斯塔福德郡','Staffordshire|Stoke-on-Trent|Wolverhampton|Walsall|Sandwell'),('莱斯特郡','Leicestershire|Leicester'),('诺丁汉郡','Nottinghamshire|Nottingham'),('德比郡','Derbyshire|Derby'),('北安普敦郡','Northamptonshire'),('牛津郡','Oxfordshire'),('伯克郡','West Berkshire|Reading|Wokingham|Bracknell Forest|Royal Borough of Windsor and Maidenhead|Slough'),('白金汉郡','Buckinghamshire|Milton Keynes'),('贝德福德郡','Bedford|Central Bedfordshire|Luton'),('赫特福德郡','Hertfordshire'),('萨里郡','Surrey'),('苏塞克斯','East Sussex|West Sussex|Brighton and Hove'),('汉普郡','Hampshire|Portsmouth|Southampton|Isle of Wight'),('威尔特郡','Wiltshire|Swindon'),('萨默塞特郡','Somerset|North Somerset|Bath and North East Somerset'),('格洛斯特郡','Gloucestershire|South Gloucestershire|Bristol'),('德文郡','Devon|Plymouth|Torbay'),('康沃尔','Cornwall|Isles of Scilly'),('多塞特郡','Dorset|Poole|Bournemouth'),('赫里福德郡','Herefordshire'),('诺森伯兰','Northumberland|Newcastle upon Tyne|North Tyneside'),('达勒姆郡','Durham|Darlington|Sunderland|Gateshead|South Tyneside|Stockton-on-Tees|Hartlepool'),('坎伯兰与威斯特摩兰','Cumbria')]
 series('United Kingdom',1200,1973,uk,DOMESDAY)
 series('United Kingdom',1200,1949,[('洛锡安','Edinburgh|East Lothian|West Lothian|Midlothian'),('法夫','Fife'),('泰维戴尔与默斯','Scottish Borders'),('安格斯','Angus|Dundee'),('阿伯丁郡','Aberdeenshire|Aberdeen'),('因弗内斯与罗斯','Highland'),('阿盖尔','Argyll and Bute'),('珀斯郡','Perthshire and Kinross'),('奥克尼','Orkney'),('设得兰','Shetland Islands'),('外赫布里底','Eilean Siar')])
 series('Ireland',1600,1949,[('芒斯特','Cork|Kerry|Limerick|North Tipperary|South Tipperary|Waterford|Clare'),('康诺特','Galway|Mayo|Roscommon|Sligo|Leitrim'),('伦斯特','Dublin|Wicklow|Wexford|Carlow|Kilkenny|Kildare|Laoighis|Offaly|Westmeath|Longford|Louth|Meath'),('阿尔斯特','Donegal|Cavan|Monaghan')])
 # German landscape names do not imply the boundaries of an imperial estate.
 series('Germany',1100,1949,[('巴伐利亚','Bayern'),('萨克森','Sachsen'),('图林根','Thüringen'),('黑森','Hessen'),('勃兰登堡','Brandenburg|Berlin'),('梅克伦堡与前波美拉尼亚','Mecklenburg-Vorpommern'),('石勒苏益格与荷尔斯泰因','Schleswig-Holstein'),('汉诺威与不伦瑞克地区','Niedersachsen|Bremen'),('威斯特法伦与莱茵兰','Nordrhein-Westfalen|Rheinland-Pfalz|Saarland'),('施瓦本与巴登地区','Baden-Württemberg')])
 series('Austria',1200,1918,[('下奥地利','Niederösterreich|Wien'),('上奥地利','Oberösterreich'),('蒂罗尔','Tirol|Vorarlberg'),('萨尔茨堡','Salzburg'),('克恩顿','Kärnten'),('施蒂利亚','Steiermark')])
 series('Poland',1200,1949,[('大波兰','Greater Poland|Lubusz'),('小波兰','Lesser Poland|Świętokrzyskie|Subcarpathian'),('马佐维亚','Masovian|Łódź'),('西里西亚','Silesian|Lower Silesian|Opole'),('波美拉尼亚','Pomeranian|West Pomeranian'),('库亚维亚','Kuyavian-Pomeranian'),('波德拉谢','Podlachian'),('瓦尔米亚与马祖里','Warmian-Masurian'),('卢布林地区','Lublin')])
 series('Romania',1400,1949,[('瓦拉几亚','Dâmbovita|Ilfov|Arges|Gorj|Vâlcea|Prahova|Vrancea|Buzau|Braila|Ialomita|Bucharest|Mehedinti|Dolj|Calarasi|Teleorman|Giurgiu|Olt'),('摩尔达维亚','Botosani|Iasi|Vaslui|Galati|Suceava|Neamt|Bacau'),('特兰西瓦尼亚','Cluj|Bistrita-Nasaud|Salaj|Hunedoara|Covasna|Brasov|Sibiu|Mures|Harghita|Alba'),('马拉穆列什与克里沙纳','Satu Mare|Arad|Bihor|Maramures'),('巴纳特','Timis|Caras-Severin'),('多布罗加','Constanta|Tulcea')])
 series('Hungary',1500,1949,[('多瑙河以西','Gyor-Moson-Sopron|Sopron|Vas|Zala|Somogy|Baranya|Komárom-Esztergom|Fejér|Veszprém|Tolna|Érd|Dunaújváros|Tatabánya|Gyôr|Szombathely|Zalaegerszeg|Nagykanizsa|Kaposvár|Pécs|Szekszárd|Székesfehérvár'),('匈牙利大平原','Szabolcs-Szatmár-Bereg|Békés|Hajdú-Bihar|Csongrád|Bács-Kiskun|Szeged|Pest|Jász-Nagykun-Szolnok|Szolnok|Budapest|Hódmezôvásárhely|Kecskemét|Békéscsaba|Debrecen|Nyíregyháza'),('北部山地','Borsod-Abaúj-Zemplén|Nógrád|Salgótarján|Heves|Eger|Miskolc')])
 series('Greece',-400,600,[('阿提卡','Attiki'),('伯罗奔尼撒','Peloponnisos'),('马其顿','Dytiki Makedonia|Kentriki Makedonia'),('伊庇鲁斯','Ipeiros'),('色萨利','Thessalia'),('中希腊','Stereá Elláda|Dytiki Ellada'),('克里特','Kriti'),('爱琴海诸岛','Notio Aigaio|Voreio Aigaio'),('伊奥尼亚群岛','Ionioi Nisoi')],ROMAN)
 series('Spain',1250,1832,[('加利西亚','La Coruña|Lugo|Orense|Pontevedra'),('阿斯图里亚斯','Asturias'),('莱昂','León|Zamora|Salamanca'),('旧卡斯蒂利亚','Burgos|Palencia|Valladolid|Ávila|Segovia|Soria|Cantabria|La Rioja'),('新卡斯蒂利亚','Madrid|Toledo|Cuenca|Guadalajara|Ciudad Real'),('埃斯特雷马杜拉','Cáceres|Badajoz'),('阿拉贡','Huesca|Zaragoza|Teruel'),('加泰罗尼亚','Barcelona|Tarragona|Lérida|Gerona'),('巴伦西亚','Valencia|Alicante|Castellón'),('纳瓦拉','Navarra'),('巴斯克诸省','Gipuzkoa|Bizkaia|Álava'),('穆尔西亚','Murcia|Albacete'),('塞维利亚','Sevilla|Huelva|Cádiz'),('科尔多瓦','Córdoba'),('哈恩','Jaén'),('格拉纳达','Granada|Málaga|Almería'),('巴利阿里群岛','Baleares')],SPAIN)
 series('Portugal',1500,1834,[('米尼奥','Viana do Castelo|Braga'),('杜罗河畔与特拉斯奥斯蒙特斯','Bragança|Vila Real|Porto'),('贝拉','Aveiro|Viseu|Guarda|Coimbra|Castelo Branco'),('埃斯特雷马杜拉','Lisboa|Santarém|Leiria'),('阿连特茹','Évora|Portalegre|Beja'),('阿尔加维','Faro')])
 # Classical geographic provinces/regions, not modern-nation projections.
 series('Spain',-27,283,[('塔拉科西班牙','La Coruña|Lugo|Orense|Pontevedra|Asturias|Cantabria|Burgos|Palencia|Valladolid|León|Zamora|Navarra|Gipuzkoa|Bizkaia|Álava|La Rioja|Soria|Segovia|Ávila|Madrid|Toledo|Cuenca|Guadalajara|Albacete|Murcia|Huesca|Zaragoza|Teruel|Barcelona|Gerona|Lérida|Tarragona|Valencia|Alicante|Castellón'),('贝提卡','Sevilla|Huelva|Cádiz|Córdoba|Jaén|Málaga|Granada|Almería'),('卢西塔尼亚东部','Cáceres|Badajoz|Salamanca')],ROMAN)
 series('Portugal',-27,283,[('卢西塔尼亚','Lisboa|Santarém|Leiria|Coimbra|Castelo Branco|Guarda|Viseu|Évora|Portalegre|Beja|Faro|Setúbal|Aveiro'),('加莱西亚地区','Porto|Braga|Viana do Castelo|Vila Real|Bragança')],ROMAN)
 series('Turkey',-300,600,[('比提尼亚','Istanbul|Bursa|Kocaeli|Sakarya|Yalova|Bolu|Düzce'),('伊奥尼亚与吕底亚','Izmir|Manisa|Usak'),('卡里亚','Mugla|Aydin'),('吕基亚与潘菲利亚','Antalya|Burdur|Isparta'),('弗里吉亚','Afyonkarahisar|Kütahya|Eskisehir|Denizli'),('加拉太','Ankara|Çankiri|Kirikkale'),('卡帕多西亚','Nevsehir|Kayseri|Nigde|Aksaray|Kirsehir'),('奇里乞亚','Adana|Mersin|Osmaniye'),('本都','Trabzon|Rize|Giresun|Ordu|Samsun|Amasya|Tokat'),('帕夫拉戈尼亚','Kastamonu|Sinop|Bartın|Karabük|Zonguldak')],ROMAN)
 # Mesopotamian and Iranian historical geographical vocabulary.
 series('Iraq',-2500,-539,[('苏美尔','Al-Basrah|Maysan|Dhi-Qar|Al-Muthannia|Al-Qādisiyyah'),('阿卡德','Baghdad|Babil|Karbala\'|An-Najaf|Diyala|Wasit'),('亚述','Ninawa|Arbil|Dihok|At-Ta\'mim|As-Sulaymaniyah|Sala ad-Din')],ROMAN)
 series('Iraq',641,1917,[('巴格达与萨瓦德','Baghdad|Babil|Karbala\'|An-Najaf|Al-Qādisiyyah|Wasit|Diyala|Sala ad-Din'),('巴士拉地区','Al-Basrah|Maysan|Dhi-Qar|Al-Muthannia'),('摩苏尔与杰济拉','Ninawa|Dihok|Arbil|At-Ta\'mim|As-Sulaymaniyah'),('安巴尔','Al-Anbar')],LOC)
 series('Iran',-550,223,[('波斯本部','Fars|Bushehr|Kohgiluyeh and Buyer Ahmad'),('米底','Hamadan|Kordestan|Kermanshah|Markazi|Qom|Tehran|Alborz|Lorestan'),('苏西亚那','Khuzestan|Ilam'),('希尔卡尼亚','Golestan|Mazandaran'),('阿特罗帕特尼','West Azarbaijan|East Azarbaijan|Ardebil|Zanjan'),('卡尔马尼亚','Kerman|Hormozgan'),('德兰吉亚那与格德罗西亚','Sistan and Baluchestan')],ROMAN)
 series('Iran',650,1949,[('法尔斯','Fars|Bushehr|Kohgiluyeh and Buyer Ahmad'),('胡齐斯坦','Khuzestan'),('呼罗珊','North Khorasan|Razavi Khorasan|South Khorasan'),('锡斯坦与俾路支','Sistan and Baluchestan'),('克尔曼','Kerman|Hormozgan'),('阿塞拜疆','West Azarbaijan|East Azarbaijan|Ardebil'),('吉兰','Gilan'),('塔巴里斯坦','Mazandaran|Golestan'),('伊拉克阿贾姆','Hamadan|Markazi|Esfahan|Qom|Tehran|Alborz|Qazvin|Zanjan'),('库尔德斯坦与洛雷斯坦','Kordestan|Kermanshah|Lorestan|Ilam|Chahar Mahall and Bakhtiari'),('亚兹德','Yazd'),('库米斯','Semnan')])
 series('Afghanistan',-500,300,[('巴克特里亚','Balkh|Jawzjan|Faryab|Kunduz|Takhar|Samangan|Baghlan|Sari Pul'),('阿里亚','Hirat|Badghis|Ghor'),('阿拉霍西亚','Kandahar|Zabul|Uruzgan'),('德兰吉亚那','Nimroz|Farah|Hilmand'),('帕罗帕米萨达伊','Kabul|Parwan|Kapisa|Wardak|Bamyan|Logar')],ROMAN)
 series('Afghanistan',1500,1949,[('巴尔赫','Balkh|Jawzjan|Faryab|Samangan|Sari Pul'),('巴达赫尚','Badakhshan|Takhar|Kunduz|Baghlan'),('赫拉特','Hirat|Badghis|Ghor'),('喀布尔','Kabul|Parwan|Kapisa|Wardak|Logar|Bamyan'),('坎大哈','Kandahar|Zabul|Uruzgan'),('锡斯坦','Nimroz|Farah|Hilmand'),('加兹尼','Ghazni|Paktya|Paktika|Khost'),('南格哈尔','Nangarhar|Laghman|Kunar')])
 series('Pakistan',-300,600,[('犍陀罗地区','K.P.|F.A.T.A.|F.C.T.'),('信度','Sind'),('五河地区','Punjab'),('格德罗西亚','Baluchistan')],ROMAN)
 series('Pakistan',1500,1949,[('旁遮普','Punjab'),('信德','Sind'),('俾路支斯坦','Baluchistan'),('白沙瓦地区','K.P.|F.A.T.A.'),('克什米尔西部','Azad Kashmir|Northern Areas')])
 # Scandinavian landscapes existed before the modern county systems.
 series('Denmark',1000,1949,[('日德兰','Nordjylland|Midtjylland|Syddanmark'),('西兰与邻岛','Sjaælland|Hovedstaden')])
 series('Sweden',1300,1949,[('约塔兰','Västra Götaland|Östergötland|Jönköping|Kronoberg|Kalmar|Blekinge|Halland|Skåne|Gotland'),('斯韦阿兰','Stockholm|Uppsala|Södermanland|Orebro|Västmanland|Värmland|Dalarna'),('诺尔兰','Gävleborg|Västernorrland|Jämtland|Västerbotten|Norrbotten')])
 # Slavic principalities' regional cores, without assigning dynastic borders.
 series('Russia',1100,1549,[('诺夫哥罗德地区','Novgorod|Leningrad'),('普斯科夫地区','Pskov'),('斯摩棱斯克地区','Smolensk'),('莫斯科地区','Moskovskaya|Moskva'),('特维尔地区','Tver\''),('弗拉基米尔与苏兹达尔','Vladimir|Ivanovo'),('罗斯托夫与雅罗斯拉夫尔','Yaroslavl\''),('梁赞地区','Ryazan\''),('库尔斯克地区','Kursk|Belgorod'),('下诺夫哥罗德地区','Nizhegorod'),('伏尔加保加尔地区','Tatarstan|Chuvash|Mariy-El')])
 series('Ukraine',1100,1499,[('基辅地区','Kiev|Kiev City|Zhytomyr'),('切尔尼戈夫地区','Chernihiv|Sumy'),('佩列亚斯拉夫地区','Poltava'),('沃里尼亚','Volyn|Rivne'),('加利西亚','L\'viv|Ivano-Frankivs\'k|Ternopil\''),('波多利亚','Khmel\'nyts\'kyy|Vinnytsya')])
 # North/East/West Africa: broader regions replace anachronistic wilaya maps.
 series('Libya',-300,1949,[('的黎波里塔尼亚','Ghadamis|An Nuqat al Khams|Surt|Misratah|Al Marqab|Tajura\' wa an Nawahi al Arba|Az Zawiyah|Al Jifarah|Mizdah'),('昔兰尼加','Al Butnan|Ajdabiya|Al Qubbah|Al Jabal al Akhdar|Al Marj|Benghazi'),('费赞','Murzuq|Ash Shati\'|Ghat|Al Jufrah|Sabha|Wadi al Hayaa')],AFRICA)
 series('Tunisia',700,1949,[('伊弗里基亚沿海','Tunis|Ben Arous (Tunis Sud)|Manubah|Bizerte|Nabeul|Sousse|Monastir|Mahdia|Sfax|Gabès'),('凯鲁万与内陆','Kairouan|Zaghouan|Siliana|Sidi Bou Zid|Béja|Jendouba|Le Kef|Kassérine'),('杰里德与杰法拉','Kebili|Tozeur|Gafsa|Médenine|Tataouine')],AFRICA)
 series('Algeria',1550,1830,[('西部贝伊领','Oran|Aïn Témouchent|Tlemcen|Sidi Bel Abbès|Mascara|Mostaganem|Relizane|Saïda|Tiaret'),('提特里','Médéa|Djelfa|Laghouat|Blida|Aïn Defla|Chlef|Tissemsilt'),('君士坦丁地区','Constantine|Mila|Annaba|El Tarf|Souk Ahras|Guelma|Skikda|Jijel|Biskra|Batna|Khenchela|Oum el Bouaghi|Sétif|Tébessa'),('阿尔及尔与卡比利亚','Alger|Tipaza|Boumerdès|Tizi Ouzou|Béjaïa|Bouira|Bordj Bou Arréridj|M\'Sila')],AFRICA)
 series('Egypt',-2500,1949,[('下埃及','Al Qahirah|Al Jizah|Ad Daqahliyah|Ash Sharqiyah|Al Isma`iliyah|Dumyat|Kafr ash Shaykh|Al Buhayrah|Al Iskandariyah|Al Minufiyah|Al Qalyubiyah|Al Gharbiyah|Bur Sa`id'),('上埃及','Al Minya|Al Fayyum|Bani Suwayf|Suhaj|Qina|Asyut|Luxor|Aswan'),('西奈','Shamal Sina\'|Janub Sina\'|As Suways'),('西部沙漠与绿洲','Matruh|Al Wadi at Jadid')],AFRICA)
 series('Sudan',1600,1949,[('努比亚','Northern|River Nile'),('达尔富尔','Central Darfur|Southern Darfur|North Darfur|Western Darfur|Eastern Darfur'),('科尔多凡','South Kordufan|North Kordufan'),('森纳尔与杰济拉','Sennar|Gezira|Khartoum|White Nile|Blue Nile|Gedarif'),('贝贾地区','Red Sea|Kassala')],AFRICA)
 series('Ethiopia',1600,1949,[('提格雷','Tigray'),('阿姆哈拉','Amhara'),('绍阿与奥罗莫高地','Oromiya|Addis Ababa'),('哈勒尔','Harari People|Dire Dawa'),('阿法尔低地','Afar')],AFRICA)
 series('Nigeria',1600,1949,[('豪萨诸城地区','Sokoto|Zamfara|Katsina|Kano|Jigawa|Kebbi|Kaduna'),('博尔诺','Borno|Yobe'),('阿达马瓦','Adamawa|Taraba'),('约鲁巴地区','Oyo|Ogun|Osun|Ondo|Ekiti|Lagos'),('贝宁地区','Edo|Delta'),('努佩与尼日尔中游','Niger|Kwara|Kogi'),('伊博地区','Anambra|Enugu|Abia|Imo|Ebonyi')],AFRICA)
 # Southeast Asian geography: town/cultural regions, not invented provinces.
 series('Indonesia',1200,1949,[('爪哇西部','Jawa Barat|Banten|Jakarta Raya'),('爪哇中部','Jawa Tengah|Yogyakarta'),('爪哇东部','Jawa Timur'),('巴厘','Bali'),('亚齐','Aceh'),('米南加保地区','Sumatera Barat'),('占碑','Jambi'),('巨港地区','Sumatera Selatan|Bangka-Belitung'),('廖内','Riau|Kepulauan Riau'),('南婆罗洲','Kalimantan Selatan|Kalimantan Tengah'),('西婆罗洲','Kalimantan Barat'),('东婆罗洲','Kalimantan Timur'),('望加锡与布吉地区','Sulawesi Selatan|Sulawesi Barat|Sulawesi Tenggara'),('摩鹿加群岛','Maluku|Maluku Utara'),('小巽他群岛','Nusa Tenggara Barat|Nusa Tenggara Timur')])
 series('Vietnam',1600,1801,[('东京地区（北河）','Ha Noi|Vĩnh Phúc|Phú Thọ|Bắc Ninh|Bắc Giang|Thái Nguyên|Hải Dương|Hà Nam|Hải Phòng|Ninh Bình|Nam Định|Thái Bình|Hòa Bình|Tuyên Quang|Yên Bái|Thanh Hóa|Nghệ An|Ha Tinh|Quảng Bình'),('顺化与广南','Quảng Trị|Thừa Thiên - Huế|Quàng Nam|Đà Nẵng|Quảng Ngãi|Bình Định|Phú Yên'),('嘉定与湄公河下游','Hồ Chí Minh city|Bình Dương|Đông Nam Bộ|Tây Ninh|Long An|Ðong Tháp|An Giang|Kiên Giang|Sóc Trăng|Tiền Giang|Vĩnh Long|Trà Vinh|Bến Tre|Can Tho|Cà Mau|Bạc Liêu|Hau Giang')])
 series('Thailand',1500,1891,[('阿瑜陀耶平原','Phra Nakhon Si Ayutthaya|Ang Thong|Sing Buri|Chai Nat|Suphan Buri|Lop Buri|Saraburi'),('兰纳地区','Chiang Mai|Chiang Rai|Lamphun|Lampang|Phayao|Phrae|Nan|Mae Hong Son'),('素可泰与彭世洛','Sukhothai|Phitsanulok|Kamphaeng Phet|Phichit|Uttaradit'),('洛坤与马来半岛北部','Nakhon Si Thammarat|Surat Thani|Chumphon|Ranong|Phangnga|Phuket|Krabi|Trang|Phatthalung|Songkhla|Pattani|Yala|Narathiwat|Satun')])
 # Colonial America: the locator core never stands for a complete viceroyalty.
 series('Mexico',1787,1820,[('墨西哥总督辖区核心','México|Distrito Federal|Hidalgo|Morelos|Querétaro'),('普埃布拉监政区','Puebla|Tlaxcala'),('瓦哈卡监政区','Oaxaca'),('梅里达监政区','Yucatán|Campeche|Quintana Roo|Tabasco'),('韦拉克鲁斯监政区','Veracruz'),('瓜达拉哈拉监政区','Jalisco|Colima|Nayarit'),('瓜纳华托监政区','Guanajuato'),('萨卡特卡斯监政区','Zacatecas|Aguascalientes'),('杜兰戈监政区','Durango|Chihuahua'),('圣路易斯波托西监政区','San Luis Potosí|Tamaulipas|Nuevo León|Coahuila'),('巴利亚多利德监政区','Michoacán|Guerrero'),('索诺拉与锡那罗亚','Sonora|Sinaloa')],'https://dia.upenn.edu/es/maps/MEX0204/')
 series('Mexico',1000,1518,[('尤卡坦玛雅地区','Yucatán|Campeche|Quintana Roo'),('瓦哈卡谷地与米斯特克地区','Oaxaca'),('墨西哥盆地','México|Distrito Federal|Hidalgo|Morelos'),('特拉斯卡拉与普埃布拉谷地','Tlaxcala|Puebla'),('墨西哥湾沿岸','Veracruz|Tabasco'),('米却肯地区','Michoacán|Guanajuato')],AMERICAS)
 series('Peru',1450,1532,[('库斯科地区','Cusco|Apurímac'),('钦查苏尤中安第斯核心','Áncash|La Libertad|Lambayeque|Cajamarca|Piura|Lima|Lima Province|Callao|Huánuco|Junín|Pasco'),('孔蒂苏尤核心','Arequipa|Moquegua|Tacna'),('科利亚苏尤北部','Puno'),('万卡地区','Huancavelica|Ayacucho')],AMERICAS)
 series('Canada',1791,1840,[('上加拿大','Ontario'),('下加拿大','Québec')],AMERICAS)
 series('Canada',1841,1866,[('加拿大西部','Ontario'),('加拿大东部','Québec')],AMERICAS)
 series('Brazil',1750,1888,[('巴伊亚','Bahia|Sergipe'),('伯南布哥','Pernambuco|Alagoas|Paraíba|Rio Grande do Norte|Ceará'),('马拉尼昂与皮奥伊','Maranhão|Piauí'),('格朗帕拉','Pará|Amapá|Amazonas|Roraima'),('马托格罗索','Mato Grosso|Mato Grosso do Sul|Rondônia'),('戈亚斯','Goiás|Tocantins'),('米纳斯吉拉斯','Minas Gerais'),('里约热内卢','Rio de Janeiro|Espírito Santo'),('圣保罗地区','São Paulo|Paraná'),('圣卡塔琳娜','Santa Catarina'),('圣佩德罗地区','Rio Grande do Sul')],AMERICAS)
 series('South Africa',1910,1993,[('开普省','Western Cape|Eastern Cape|Northern Cape'),('纳塔尔省','KwaZulu-Natal'),('奥兰治自由邦省','Free State'),('德兰士瓦省','Gauteng|Limpopo|Mpumalanga|North West')],AMERICAS)
 group('Japan','虾夷地','Hokkaidō',1868,1868,'https://www.city.hokuto.hokkaido.jp/bunkazai/data/nen2-1.htm')
 # The 1869 kuni names include the newly split Mutsu/Dewa and Hokkaido
 # countries. They are not projected backwards into the old merged names.
 for f in read('public/data/japan-old-provinces.geojson')['features']:
  p=f['properties'];added.append(dict(type='Feature',geometry=f['geometry'],properties=dict(id=TAG+':jp1869:'+p['id'],label=p['name']+'国',native=p['name'],country='Japan',replaceCountry=True,type='令制国',validFrom=1869,validTo=1871,ownerAny=['Empire of Japan','Ezo Island Government'],dataKind='historical-reconstruction',sourceYear=1869,source='CODH／NIHU 旧国界；1869年区划参考',sourceUrl=p['sourceUrl'],credit=p['credit'],license=p['license'],accuracy='采用旧国轮廓作1869—1871年参考，未视为全部府藩县的边界。',supplement=TAG)))
 # Better historical geometries retain priority wherever they already exist.
 for f in added:
  p=f['properties'];g=shape(f['geometry']);conflicts=[r for r in kept if r['properties']['country']==p['country']and r['properties'].get('validFrom',99999)<=p['validTo']and r['properties'].get('validTo',-99999)>=p['validFrom']]
  # Runtime performs date-specific precedence, rather than deleting a region
  # from every century just because one better snapshot exists.
  if p.get('geographicReference'):p['priority']='fallback'
 historical['features']=kept+added;write('public/data/historical-provinces.geojson',historical)
 write('public/data/global-historical-regions-review.json',dict(reviewedAt='2026-11-02',added=len(added),countries=sorted({f['properties']['country']for f in added}),locatorCells=len({i for f in added for i in f['properties'].get('replaces',[])}),unmatchedLocatorNames=missed,sources=[ATLAS,ROMAN,DOMESDAY,SPAIN,LOC,AFRICA,AMERICAS],limitations=['历史地理区不等于精确历史省份；图上不绘制未经核实的行政分界。','不同文明的分区资料覆盖不均；史前小区域及大量早期地方名称仍未核定。','旧地理区名称按有效时期选择；近代地图用语不外推到史前。']))
 print('Historical geographic references',len(added),'countries',len({f['properties']['country']for f in added}),'locator cells',len({i for f in added for i in f['properties'].get('replaces',[])}),'unmatched',len(missed),flush=True)
if __name__=='__main__':main()
