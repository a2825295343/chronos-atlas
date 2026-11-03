"""Dated, owner-scoped historic divisions, plus attributed Japanese old kuni.

Reconstructed groups disclose modern locating geometry. NII's late-Edo kuni
boundaries are historical references, never claimed as exact 8th-century maps.
"""
import json,sys
from collections import defaultdict
from territory_repair_stage import ROOT,read,write,clean
from shapely import union_all
from shapely.geometry import shape,mapping,box
from opencc import OpenCC
CC=OpenCC('t2s');TAG='period-regions-2026-11-01'
NII='https://geoshape.ex.nii.ac.jp/kg/index.html.ja'
CREDIT='『旧国・旧郡境界データセット』（CODH作成）「幕末明治地勢地図境界データ」（人間文化研究機構作成）を加工 doi:10.20676/00000454'

def main():
 modern=read('public/data/provinces.geojson')['features'];lookup={(f['properties']['country'],f['properties']['native']):f for f in modern}
 old=read('public/data/historical-provinces.geojson');rows=[f for f in old['features']if not f['properties'].get('supplement')==TAG and not str(f['properties']['id']).startswith('MING-ADM-')]
 for f in rows:
  if f['properties']['country']=='Italy':f['properties']['replaceCountry']=True
 added=[]
 def group(series,label,parts,a,b,owners,url,clip=None,kind='历史区域概化',country=None):
  source=[lookup[p]for p in parts if p in lookup]
  if not source:return
  g=clean(union_all([shape(f['geometry'])for f in source]));g=clean(g.intersection(clip))if clip is not None else g
  if g.is_empty:return
  p={'id':f'{TAG}:{series}:{label}:{a}','label':label,'native':label,'country':country or parts[0][0],'coveredCountries':sorted({c for c,n in parts}),'replaces':[f['properties']['id']for f in source],'type':kind,'source':'历史区划制度及地名资料；现代地理辅助概化','sourceUrl':url,'validFrom':a,'validTo':b,'ownerAny':owners,'dataKind':'historical-reconstruction','accuracy':'名称与制度按有效时期、实际势力筛选；轮廓为现代地理辅助重建，不是该年的精确行政界。','supplement':TAG}
  added.append({'type':'Feature','geometry':mapping(g),'properties':p})
 def cn(series,label,names,a,b,owners,clip=None):group(series,label,[('China',n)for n in names],a,b,owners,'https://en.wikipedia.org/wiki/History_of_the_administrative_divisions_of_China',clip)
 # Chinese divisions: known administrative names, no modern "province" in Han/Tang.
 han=['Han Dynasty','Han','Western Han','Eastern Han']
 for label,names,clip in [('交趾刺史部',['Guangdong','Guangxi','Hainan'],None),('扬州刺史部',['Zhejiang','Fujian','Jiangxi','Jiangsu','Anhui','Shanghai'],box(105,20,125,32.5)),('徐州刺史部',['Jiangsu','Anhui'],box(112,32.5,123,36)),('荆州刺史部',['Hubei','Hunan'],None),('益州刺史部',['Sichuan','Chongqing','Yunnan','Guizhou'],None),('豫州刺史部',['Henan'],None),('冀州刺史部',['Hebei','Beijing','Tianjin'],None),('并州刺史部',['Shanxi'],None),('青兖诸郡',['Shandong'],None),('司隶校尉部',['Shaanxi'],None),('凉州刺史部',['Gansu','Ningxia'],None)]:cn('han',label,names,-106,187,han,clip)
 for f in list(added):
  if f['properties']['id'].split(':')[1]=='han':
   r=json.loads(json.dumps(f));p=r['properties'];p.update(validFrom=188,validTo=220,label=p['label'].replace('刺史部','').replace('校尉部','辖区'),id=p['id']+':late')
   if f['properties']['label']=='交趾刺史部':
    p.update(validTo=202,label='交趾刺史部');last=json.loads(json.dumps(r));last['properties'].update(id=p['id']+':203',validFrom=203,validTo=220,label='交州');added.append(last)
   added.append(r)
 tang=['Tang Dynasty','Tang']
 for label,names,clip in [('岭南道',['Guangdong','Guangxi','Hainan'],None),('江南东道',['Zhejiang','Fujian','Shanghai','Jiangsu','Anhui'],box(110,20,125,32.5)),('淮南道',['Anhui','Jiangsu'],box(110,32.5,124,35)),('江南西道',['Jiangxi','Hunan'],None),('河北道',['Hebei','Beijing','Tianjin'],None),('河东道',['Shanxi'],None),('河南道',['Henan','Shandong'],None),('关内道',['Shaanxi','Ningxia'],None),('陇右道',['Gansu','Qinghai'],None),('剑南道',['Sichuan'],box(97,26,104.8,35)),('山南西道',['Chongqing','Hubei','Sichuan'],box(104.8,28,111,33)),('黔中道',['Guizhou'],None)]:cn('tang',label,names,733,906,tang,clip)
 song=['Song Dynasty','Northern Song','Southern Song','Song']
 for label,names in [('江南东路',['Anhui']),('江南西路',['Jiangxi']),('荆湖北路',['Hubei']),('荆湖南路',['Hunan']),('广南东路',['Guangdong']),('广南西路',['Guangxi','Hainan']),('福建路',['Fujian']),('京东路',['Shandong']),('河北路',['Hebei','Beijing','Tianjin']),('河东路',['Shanxi']),('陕西诸路',['Shaanxi','Gansu','Ningxia']),('两川诸路',['Sichuan','Chongqing'])]:cn('song',label,names,997,1278,song)
 zhe=['Zhejiang','Shanghai','Jiangsu'];whole=box(117,20,125,32.4);west=union_all([box(118,29.4,120.5,32.4),box(118,30.4,123,32.4)])
 for a,b in [(997,1073),(1075,1075),(1077,1126)]:cn('song','两浙路',zhe,a,b,song,whole)
 for a,b in [(1074,1074),(1076,1076),(1127,1275)]:
  cn('song','两浙西路',zhe,a,b,song,whole.intersection(west));cn('song','两浙东路',zhe,a,b,song,whole.difference(west))
 yuan=['Yuan Dynasty','Great Yuan','Yuan']
 for label,names,clip in [('江浙行省',['Zhejiang','Shanghai','Jiangsu','Fujian'],box(110,20,125,32.5)),('江西行省',['Jiangxi','Guangdong','Hainan'],None),('湖广行省',['Hubei','Hunan','Guangxi','Guizhou'],None),('河南江北行省',['Henan','Anhui','Jiangsu'],box(110,32.5,125,37)),('中书省直辖府路',['Hebei','Beijing','Tianjin','Shandong','Shanxi'],None),('陕西行省',['Shaanxi'],None),('甘肃行省',['Gansu','Ningxia'],None),('四川行省',['Sichuan','Chongqing'],None),('云南行省',['Yunnan'],None)]:cn('yuan',label,names,1280,1367,yuan,clip)
 ming=['Ming Dynasty','Southern Ming']
 for a,b,label in [(1368,1402,'北平布政使司'),(1403,1406,'北京行部'),(1407,1662,'北直隶')]:cn('ming',label,['Beijing','Hebei','Tianjin'],a,b,ming)
 for a,b,label in [(1368,1420,'南京直隶'),(1421,1662,'南直隶')]:cn('ming',label,['Jiangsu','Anhui','Shanghai'],a,b,ming)
 for label,parts in [('湖广',['Hubei','Hunan']),('陕西',['Shaanxi','Gansu','Ningxia']),('山西',['Shanxi']),('山东',['Shandong']),('河南',['Henan']),('浙江',['Zhejiang']),('江西',['Jiangxi']),('福建',['Fujian']),('广东',['Guangdong','Hainan']),('广西',['Guangxi']),('四川',['Sichuan','Chongqing']),('云南',['Yunnan'])]:
  cn('ming',label+'行省',parts,1368,1375,ming);cn('ming',label+'布政使司',parts,1376,1662,ming)
 cn('ming','贵州布政使司',['Guizhou'],1413,1662,ming)
 cn('ming','思州、播州等土司',['Guizhou'],1368,1412,ming)
 qing=['Qing Dynasty']
 for n in ['Shanxi','Shandong','Henan','Zhejiang','Jiangxi','Fujian','Guangdong','Guangxi','Sichuan','Yunnan','Guizhou']:
  native=lookup.get(('China',n));label='广西省'if n=='Guangxi'else native['properties']['label']if native else n
  cn('qing',label,[n]+(['Hainan']if n=='Guangdong'else['Chongqing']if n=='Sichuan'else[]),1644,1911,qing)
 cn('qing','直隶省',['Hebei','Beijing','Tianjin'],1644,1911,qing)
 cn('qing','江南省',['Jiangsu','Anhui','Shanghai'],1644,1660,qing)
 cn('qing','江南右布政使司',['Jiangsu','Shanghai'],1661,1666,qing,box(110,20,125,32))
 cn('qing','江南左布政使司',['Anhui','Jiangsu'],1661,1666,qing,union_all([box(110,32,125,40),box(110,20,118.7,32)]))
 cn('qing','江苏省',['Jiangsu','Shanghai'],1667,1911,qing);cn('qing','安徽省',['Anhui'],1667,1911,qing)
 cn('qing','湖广辖区',['Hubei','Hunan'],1644,1663,qing);cn('qing','湖北省',['Hubei'],1664,1911,qing);cn('qing','湖南省',['Hunan'],1664,1911,qing)
 cn('qing','陕西省',['Shaanxi','Gansu','Ningxia'],1644,1666,qing);cn('qing','陕西省',['Shaanxi'],1667,1911,qing);cn('qing','甘肃省',['Gansu','Ningxia'],1667,1911,qing)
 cn('qing','伊犁将军辖区',['Xinjiang'],1762,1883,qing);cn('qing','新疆省',['Xinjiang'],1884,1911,qing)
 cn('qing','西宁办事大臣辖区',['Qinghai'],1725,1911,qing)
 # France's old provinces: union of locating departments, not modern regions.
 france=['Kingdom of France','Bourbon Kingdom of France','First French Empire','French First Republic','English Territories','Kingdom of England']
 fr=[('布列塔尼',['Finistère','Morbihan',"Côtes-d'Armor",'Ille-et-Vilaine','Loire-Atlantique']),('诺曼底',['Manche','Calvados','Eure','Seine-Maritime','Orne']),('法兰西岛',['Paris','Yvelines',"Val-d'Oise",'Val-de-Marne','Seine-Saint-Denis','Hauts-de-Seine','Essonne','Seine-et-Marne']),('勃艮第',['Côte-d’Or',"Côte-d'Or",'Saône-et-Loire','Nièvre','Yonne']),('香槟',['Marne','Aube','Haute-Marne','Ardennes']),('洛林',['Meurthe-et-Moselle','Meuse','Moselle','Vosges']),('阿尔萨斯',['Bas-Rhin','Haute-Rhin','Territoire de Belfort']),('普罗旺斯',['Var','Bouches-du-Rhône','Alpes-de-Haute-Provence']),('多菲内',['Isère','Drôme','Hautes-Alpes']),('朗格多克',['Hérault','Gard','Aude','Tarn','Haute-Garonne','Ardèche','Lozère']),('吉耶讷—加斯科涅',['Gironde','Landes','Lot-et-Garonne','Gers','Dordogne','Lot']),('普瓦图',['Vienne','Deux-Sèvres','Vendée']),('奥弗涅',['Puy-de-Dôme','Cantal','Haute-Loire']),('皮卡第',['Somme','Aisne']),('安茹',['Maine-et-Loire']),('曼恩',['Sarthe','Mayenne']),('奥尔良地区',['Loiret','Loir-et-Cher']),('图赖讷',['Indre-et-Loire'])]
 for l,parts in fr:group('france',l,[('France',n)for n in parts],1300,1789,france,'https://www.britannica.com/place/France/History')
 # Roman provincial regions, owner-clipped to avoid treating modern borders as empire boundaries.
 roman=['Roman Empire','Roman Republic','Western Roman Empire','Eastern Roman Empire','Byzantine Empire']
 for l,parts in [('纳尔榜高卢',['Var','Bouches-du-Rhône','Alpes-de-Haute-Provence','Hérault','Gard','Aude','Vaucluse']),('阿基坦',['Gironde','Landes','Dordogne','Lot-et-Garonne','Gers','Lot','Charente','Charente-Maritime']),('卢格敦高卢',['Finistère','Morbihan','Ille-et-Vilaine','Loire-Atlantique','Manche','Calvados','Orne','Paris','Yvelines','Loiret']),('比利时高卢',['Nord','Ardennes','Aisne','Marne','Somme','Pas-de-Calais'])]:group('rome',l,[('France',n)for n in parts],-27,284,roman,'https://www.britannica.com/place/Gaul-ancient-region-Europe')
 # Joseon's eight do: merge modern north/south partitions back together.
 korean=[]
 krsets=[('京畿道',['Gyeonggi','Incheon','Seoul','Kaesong']),('江原道',['Gangwon','Kangwon']),('忠清道',['South Chungcheong','North Chungcheong','Daejeon','Sejong']),('全罗道',['North Jeolla','South Jeolla','Gwangju','Jeju']),('庆尚道',['North Gyeongsang','South Gyeongsang','Busan','Ulsan','Daegu']),('黄海道',['Hwanghae-namdo','Hwanghae-bukto']),('平安道',['Pyeongan-namdo','Pyeongan-bukto','Pyongyang','Nampo']),('咸镜道',['Hamgyong-namdo','Hamgyong-bukto','Ryanggang','Rason'])]
 for l,names in krsets:
  variants={'Kangwon':['Kangwŏn-do'],'Hamgyong-namdo':['Hamgyŏng-namdo'],'Hamgyong-bukto':['Hamgyŏng-bukto'],'Rason':['Rasŏn'],'Pyeongan-namdo':["P'yŏngan-namdo"],'Pyeongan-bukto':["P'yŏngan-bukto",'Chagang-do'],'Pyongyang':["P'yŏngyang"]}
  expanded=[v for n in names for v in [n,*variants.get(n,[])]];parts=[(c,n)for c in ['South Korea','North Korea']for n in expanded];group('joseon',l,parts,1413,1894,['Joseon','Korean Empire'],'https://en.wikipedia.org/wiki/Eight_Provinces_of_Korea')
 # Mughal subahs and British presidencies, with their different administrative combinations.
 mughal=['Mughal Empire']
 for l,parts in [('孟加拉苏巴',[('India','West Bengal'),('Bangladesh','Dhaka'),('Bangladesh','Khulna'),('Bangladesh','Rajshahi')]),('比哈尔苏巴',[('India','Bihar'),('India','Jharkhand')]),('古吉拉特苏巴',[('India','Gujarat')]),('阿杰梅尔苏巴',[('India','Rajasthan')]),('拉合尔苏巴',[('India','Punjab'),('Pakistan','Punjab')]),('德里苏巴',[('India','Delhi'),('India','Haryana')])]:group('mughal',l,parts,1580,1738,mughal,'https://www.britannica.com/place/India/The-Mughal-Empire-1526-1761')
 india=['British Raj','British India']
 for l,parts,a in [('孟加拉管辖区',['West Bengal','Bihar','Jharkhand','Odisha'],1765),('马德拉斯管辖区',['Tamil Nadu','Andhra Pradesh','Kerala'],1801),('孟买管辖区',['Maharashtra','Gujarat'],1818),('旁遮普省',['Punjab','Haryana','Himachal Pradesh','Chandigarh'],1849),('联合省',['Uttar Pradesh','Uttarakhand'],1902),('中央省',['Madhya Pradesh','Chhattisgarh'],1861)]:group('raj',l,[('India',n)for n in parts],a,1946,india,'https://www.bl.uk/collection-items/map-of-india-1857')
 # Ottoman eyalet cores in Anatolia: historical level instead of current il names.
 for l,parts,a in [('安纳托利亚行省',['Bursa','Balikesir','Kütahya','Eskisehir','Ankara','Bolu','Çankiri','Kastamonu','Sinop','Sakarya','Kocaeli','Bilecik'],1393),('卡拉曼行省',['Konya','Karaman','Nigde','Kayseri','Nevsehir'],1483),('锡瓦斯行省',['Sivas','Tokat','Amasya','Çorum'],1398),('特拉布宗行省',['Trabzon','Rize','Giresun'],1598),('迪亚巴克尔行省',['Diyarbakir','Mardin','Elazig'],1515),('埃尔祖鲁姆行省',['Erzurum','Erzincan'],1533),('凡城行省',['Van','Bitlis','Hakkari'],1548)]:group('ottoman',l,[('Turkey',n)for n in parts],a,1863,['Ottoman Empire'],'https://en.wikipedia.org/wiki/Eyalet')
 # Japanese historical kuni: merge the 1869 Mutsu/Dewa partitions for earlier years.
 decoded=read('.local/japan-kuni/decoded.geojson');kuni=defaultdict(list);native={}
 for f in decoded['features']:
  p=f['properties'];kuni[p['id']].append(shape(f['geometry']));native[p['id']]=p['name']
 jp=[]
 for k,gs in sorted(kuni.items()):
  g=clean(union_all(gs)).simplify(.0015,preserve_topology=True)
  label=CC.convert(native[k]).translate(str.maketrans({'総':'总','豊':'丰','讃':'赞','隠':'隐','摂':'摄','蔵':'藏','壱':'壹'}))
  jp.append({'type':'Feature','geometry':mapping(g),'properties':{'id':k,'name':label,'native':native[k],'sourceUrl':NII,'credit':CREDIT,'license':'CC BY-NC 4.0','sourceYear':1868}})
 write('public/data/japan-old-provinces.geojson',{'type':'FeatureCollection','features':jp})
 early=[]
 for f in jp:
  k=f['properties']['id'];num=int(k[1:])
  if 27<=num<=33 or num>=74:continue
  early.append((k,f['properties']['name'],shape(f['geometry'])))
 for ids,label in [([f'K{x:02}'for x in range(27,32)],'陆奥'),(['K32','K33'],'出羽')]:early.append((label,label,clean(union_all([shape(f['geometry'])for f in jp if f['properties']['id']in ids]))))
 jpowners=['Heian Japan','Nara Japan','Kamakura Shogunate','Ashikaga Shogunate','Warring States Japan','Japanese Daimyo Domains','Tokugawa Shogunate','Tokugawa Government','Empire of Japan','Japan','Toyotomi Government','Oda Government']
 for key,label,g in early:
  p={'id':TAG+':kuni:'+key,'label':label+'国','native':label,'country':'Japan','replaceCountry':True,'type':'令制国','source':'CODH／NIHU 旧国・旧郡边界数据；幕末旧国轮廓作跨期参考','sourceUrl':NII,'credit':CREDIT,'license':'CC BY-NC 4.0','sourceYear':1868,'validFrom':824,'validTo':1868,'ownerAny':jpowners,'ownerPrefix':['Japanese clan - ','Japanese regional - '],'dataKind':'historical-reconstruction','accuracy':'采用幕末旧国界，合并1869年才分出的陆奥、出羽诸国；早期分界仍有变迁，不能视为824年以来每年完全相同的精确国界。','supplement':TAG}
  added.append({'type':'Feature','geometry':mapping(g),'properties':p})
 write('public/data/historical-provinces.geojson',{'type':'FeatureCollection','features':rows+added})
 write('public/data/period-regions-review.json',{'reviewedAt':'2026-11-01','featuresAdded':len(added),'countries':sorted({f['properties']['country']for f in added}),'japanSourceFeatures':len(jp),'japanAttribution':CREDIT,'japanLicense':'CC BY-NC 4.0','limitations':['除意大利普查界与日本旧国参考外，许多边界仍为明确标记的地理辅助概化。','未经核定的现代行政名不作为古代名称回填，缺证据处保留可点击的定位参考。','适用时期还需与当年实际控制范围相交，不因现代国名相同而自动使用。']})
 print('New dated administrative features',len(added),'Japan source provinces',len(jp),flush=True)

if __name__=='__main__':main()
