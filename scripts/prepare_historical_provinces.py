"""Prepare dated historic administrative snapshots and explicitly marked reconstructions."""
import json,pathlib,sys,re,urllib.parse
from download_data import get
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape,mapping
from shapely.ops import unary_union
from opencc import OpenCC
CC=OpenCC('t2s')
def main():
 rows=[];years=[1861,1871,1881,1901,1911,1921,1931,1936,1951,1961,1971];names=set()
 for i,year in enumerate(years):
  data=json.loads((ROOT/f'.local/presentation/italy-{year}.geojson').read_text(encoding='utf-8'))
  for f in data['features']:
   p=f['properties'];native=p['DEN_PROV'];names.add(native)
   rows.append({'type':'Feature','geometry':f['geometry'],'properties':{'id':'ITA-H-'+str(p['COD_PROV']),'label':native,'native':native,'country':'Italy','type':'历史省份','source':'ISTAT 历史行政区界／DEMOPAST','sourceUrl':'https://demopast.it/download.html','sourceYear':year,'validFrom':year,'validTo':years[i+1]-1 if i+1<len(years)else 1980,'dataKind':'historical-snapshot','accuracy':'按此前最近一次人口普查的历史省界快照显示；未假定普查间没有区划调整'}})
 labels={};cache=ROOT/'.local/presentation/italian-province-names.json'
 if cache.exists():labels=json.loads(cache.read_text(encoding='utf-8'))
 missing=sorted(names-labels.keys())
 for i in range(0,len(missing),20):
  group=missing[i:i+20];query={'client':'gtx','sl':'it','tl':'zh-CN','dt':'t','q':'\n'.join(group)}
  data=json.loads(get('https://translate.googleapis.com/translate_a/single?'+urllib.parse.urlencode(query)));lines=''.join(p[0]or''for p in data[0]).strip().splitlines()
  if len(lines)==len(group):labels.update({n:CC.convert(v.strip())for n,v in zip(group,lines)})
 labels.update({'Torino':'都灵','Milano':'米兰','Roma':'罗马','Napoli':'那不勒斯','Firenze':'佛罗伦萨','Venezia':'威尼斯','Genova':'热那亚','Bologna':'博洛尼亚','Pola':'波拉','Fiume':'阜姆','Zara':'扎拉','Girgenti':'吉尔真蒂','Aquila degli Abruzzi':'阿布鲁齐-阿奎拉','Aosta':'奥斯塔','Terra di Lavoro':'劳沃罗地省','Terra di Bari':'巴里地省','Terra di Otranto':'奥特朗托地省','Grosseto':'格罗塞托'})
 cache.write_text(json.dumps(labels,ensure_ascii=False),encoding='utf-8')
 for f in rows:f['properties']['label']=labels.get(f['properties']['native'],f['properties']['native'])
 modern=json.loads((ROOT/'public/data/provinces.geojson').read_text(encoding='utf-8'))['features'];china={f['properties']['native']:f for f in modern if f['properties']['country']=='China'}
 groups=[('北直隶',['Beijing','Hebei','Tianjin']),('南直隶',['Jiangsu','Anhui','Shanghai']),('湖广布政使司',['Hubei','Hunan']),('陕西布政使司（含卫所区概化）',['Shaanxi','Gansu','Ningxia']),('山西布政使司',['Shanxi']),('山东布政使司',['Shandong']),('河南布政使司',['Henan']),('浙江布政使司',['Zhejiang']),('江西布政使司',['Jiangxi']),('福建布政使司',['Fujian']),('广东布政使司',['Guangdong','Hainan']),('广西布政使司',['Guangxi']),('四川布政使司',['Sichuan','Chongqing']),('贵州布政使司',['Guizhou']),('云南布政使司',['Yunnan'])]
 for i,(label,parts)in enumerate(groups):
  geoms=[shape(china[n]['geometry'])for n in parts if n in china]
  if not geoms:continue
  rows.append({'type':'Feature','geometry':mapping(unary_union(geoms)),'properties':{'id':'MING-ADM-'+str(i),'label':label,'native':label,'country':'China','type':'布政使司／直隶','source':'两京十三布政使司制度；Natural Earth 底图辅助重建','sourceUrl':'https://www.lygsz.gov.cn/lygszw/uploads_transfer/soft/181112/201706.pdf','validFrom':1421,'validTo':1643,'dataKind':'historical-reconstruction','ownerRequired':'Ming Dynasty','accuracy':'历史区域名称与组合有史料依据；轮廓由现代省区合并概化，不能视为精确明代界线'}})
 (ROOT/'public/data/historical-provinces.geojson').write_text(json.dumps({'type':'FeatureCollection','features':rows},ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print('Historical administrative features',len(rows),'Italian names',len(labels),flush=True)
if __name__=='__main__':main()

