"""Add sourced control zones. Historical base polygons are retained; a control
zone is a dated overlay, never an assertion of internationally recognized title.
"""
import json,pathlib,sys
ROOT=pathlib.Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely.geometry import shape,mapping,box,Polygon
from shapely import make_valid,union_all
RAW=json.loads((ROOT/'.local/cliopatria.geojson').read_bytes())['features']
def polity(name,year):
 rows=[f for f in RAW if f['properties']['Name']==name and f['properties']['FromYear']<=year<=f['properties']['ToYear']]
 if not rows:raise ValueError((name,year))
 return make_valid(shape(rows[-1]['geometry']))
def main():
 rows=[];ushmm='https://encyclopedia.ushmm.org/content/en/article/german-rule-in-occupied-europe'
 def add(id,name,from_,to,geometry,controller,sovereign,source,accuracy,**extra):
  geometry=make_valid(geometry).simplify(.015,preserve_topology=True)
  def polygons(g):
   if g.geom_type=='Polygon':return [g]
   if hasattr(g,'geoms'):return [p for child in g.geoms for p in polygons(child)]
   return []
  geometry=union_all(polygons(geometry))
  if geometry.is_empty:return
  rows.append({'type':'Feature','geometry':mapping(geometry),'properties':dict(id=id,NAME='Control area - '+id,SUBJECTO=controller,displayName=name,controller=controller,sovereignName=sovereign,territoryType='occupation',validFrom=from_,validTo=to,sourceUrl=source,source='补充军事控制区',accuracy=accuracy,**extra)})
 for id,name,sourceName in [('belgium','比利时（德占）','Kingdom of Belgium'),('netherlands','荷兰（德占）','Netherlands'),('norway','挪威（德占）','Kingdom of Norway')]:
  add('de-'+id,name,1940,1943 if id in ['belgium','netherlands'] else 1944,polity(sourceName,1938),'Nazi Germany',sourceName,ushmm,'以1938年历史疆界辅助重建；年度范围示意，不含逐日解放战线。')
 # Denmark-Norway is incorrectly retained as a source name into the 20th
 # century. Clip only Denmark, never silently inherit its old Norwegian lands.
 add('de-denmark','丹麦（德占）',1940,1944,polity('Denmark-Norway',1938).intersection(box(7.5,54.4,15.5,58)),'Nazi Germany','Denmark',ushmm,'丹麦本土概化；1943年前保留的丹麦政府不表示不存在德国占领。')
 france=polity('French Third Republic',1938).intersection(box(-6,41,10,52));vichy=polity('Vichy France',1941).intersection(box(-6,41,10,52))
 add('de-france-north','法国北部与大西洋沿岸（德占）',1940,1942,france.difference(vichy),'Nazi Germany','French Third Republic',ushmm,'由战前法国与1941年维希控制区差集重建；分界线经过概化，1942年内发生全面占领。')
 add('de-france-full','法国（德军占领区概览）',1943,1943,france,'Nazi Germany','French Third Republic',ushmm,'年度代表性示意，取意大利退出后德国控制法国大部分本土的阶段；不表示全年同一战线。')
 poland=polity('Second Polish Republic',1938);sovietPart=poland.intersection(polity('Union of Soviet Socialist Republics',1940))
 add('de-poland-west','波兰西部（德占）',1939,1940,poland.difference(sovietPart),'Nazi Germany','Second Polish Republic',ushmm,'以战前波兰和1940年苏联历史GIS交集重建分占线；取1939年秋后的代表性状态，区分被占领国与控制国。')
 add('su-poland-east','波兰东部（苏占）',1939,1940,sovietPart,'Union of Soviet Socialist Republics','Second Polish Republic','https://encyclopedia.ushmm.org/content/en/article/invasion-of-poland-fall-1939','按战前波兰与1940年苏联GIS交集概化；非逐日边界，主权与军事控制分开记录。')
 add('de-poland-full','波兰（德占）',1941,1943,poland,'Nazi Germany','Second Polish Republic',ushmm,'取1941年6月德国进攻苏联后的占领概览；不表示1941年全年状态不变，不细分总督府和被兼并区。')
 china=polity('Republic of China',1936)
 for year in range(1937,1945):
  japanese=polity('Empire of Japan',year).intersection(china)
  try:japanese=japanese.difference(polity('Manchukuo',year))
  except ValueError:pass
  add('jp-china-'+str(year),'中国日军占领区',year,year,japanese,'Empire of Japan','Republic of China','https://github.com/Seshat-Global-History-Databank/cliopatria','按该年日本控制区GIS与1936年中国范围相交提取；伪满洲国单列。来源疆界经过概化，不是逐日战线，也不把占领视为主权转移。')
 # Temporary governments have their own colors and state archives, even if
 # their small territory is absent from an upstream century shard.
 for name,zh,year in [('Provisional Priamurye Government','滨海临时政府',1922),('Vichy France','法国（维希政府）',1941)]:
  try:
   g=polity(name,year);p=next(f['properties'] for f in RAW if f['properties']['Name']==name)
   add('temporary-'+str(p.get('Wikidata')),zh,p['FromYear'],p['ToYear'],g,name,'',f"https://www.wikidata.org/wiki/{p['Wikidata']}",'原始历史GIS控制范围；政治地位与国际承认分开理解。',kind='temporary',qid=p['Wikidata'])
  except ValueError:pass
 # These are geographic administration zones, not invented German successor
 # states. Boundaries are intentionally a coarse sector reconstruction.
 states={f['properties']['native']:shape(f['geometry']) for f in json.loads((ROOT/'public/data/provinces.geojson').read_bytes())['features'] if f['properties']['country']=='Germany'}
 def combine(names):return union_all([states[n] for n in names])
 source='https://history.state.gov/milestones/1945-1952/germany'
 bw=states['Baden-Württemberg'];north=bw.intersection(box(-180,48.9,180,90));south=bw.difference(north)
 for id,zh,controller,geometry in [
  ('soviet','苏联占领区（德国）','Union of Soviet Socialist Republics',combine(['Sachsen','Brandenburg','Mecklenburg-Vorpommern','Thüringen','Sachsen-Anhalt'])),
  ('british','英国占领区（德国）','United Kingdom',combine(['Schleswig-Holstein','Niedersachsen','Nordrhein-Westfalen','Hamburg'])),
  ('french','法国占领区（德国）','French Fourth Republic',union_all([states['Rheinland-Pfalz'],south])),
  ('american','美国占领区（德国）','United States of America',union_all([combine(['Bayern','Hessen','Bremen']),north])),
 ]:
  add('germany-'+id,zh,1946,1948,geometry,controller,'Germany',source,'依据占领区构成，用现代州界组合近似重建；西南巴登／符腾堡分界为概化推断，柏林另外表示。',inferred=True)
 add('berlin-four-powers','柏林四国共管区',1946,1948,states['Berlin'],'Allied Control Council','Germany',source,'柏林整体范围参考；未在本比例尺下细分四国行政扇区。',jointRulers=['United States of America','United Kingdom','French Fourth Republic','Union of Soviet Socialist Republics'])
 add('saar-french','萨尔（法军占领）',1946,1946,states['Saarland'],'French Fourth Republic','Germany',source,'以现代萨尔州辅助定位，1947年起保护领地地位另计。')
 path=ROOT/'public/data/control-areas.geojson';path.write_text(json.dumps({'type':'FeatureCollection','features':rows,'policy':'军事控制覆盖层；不等于主权承认。推断轮廓明确标注，未通过战争名单推断占领区。'},ensure_ascii=False,separators=(',',':')),encoding='utf-8');print('Control area records',len(rows),flush=True)
if __name__=='__main__':main()
