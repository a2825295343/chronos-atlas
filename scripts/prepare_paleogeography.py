"""Hypsometric paleocoast references from bathymetry + published sea level.

This is NOT a plate-rotation model, local GIA model or archaeological border.
Bathymetry is the bundled Tilezen terrain (including ETOPO ocean elevations).
"""
import sys,json,hashlib
from pathlib import Path
from territory_repair_stage import ROOT,read,write,clean
import numpy as np
from PIL import Image
import contourpy
from shapely.geometry import Polygon,shape,mapping,box
from shapely import union_all
TAG='paleogeography-2026-11-02';OUT=ROOT/'public/data/paleogeography';OUT.mkdir(exist_ok=True)
NOAA='https://www.ncei.noaa.gov/access/paleo-search/study/19982'
def main():
 raw=(ROOT/'.local/sea-level-spratt2016.txt').read_text(encoding='utf-8-sig');curve=[]
 for line in raw.splitlines():
  if not line or line.startswith('#'):continue
  cols=line.split()
  try:age,level,sigma=map(float,cols[:3])
  except ValueError:continue
  if age<=126:curve.append(dict(ageKa=age,level=level,sigma=sigma))
 if not curve:raise ValueError('NOAA age/sea-level columns missing')
 # At z5 the actual source support is about 5 km at the equator; output
 # sampling is approximately 10 km. No precision claim at street scale.
 dem=np.empty((8192,8192),dtype=np.int16)
 for x in range(32):
  for y in range(32):
   a=np.asarray(Image.open(ROOT/f'public/data/dem/5/{x}/{y}.png'),dtype=np.int32)
   dem[y*256:(y+1)*256,x*256:(x+1)*256]=(a[:,:,0]*256+a[:,:,1]-32768).astype(np.int16)
 xs=np.linspace(-180,180,4097);ys=np.linspace(-85,85,2049)
 ix=np.clip(((xs+180)/360*8192).astype(int),0,8191)
 iy=np.clip(((1-np.arcsinh(np.tan(np.deg2rad(ys)))/np.pi)/2*8192).astype(int),0,8191)
 z=dem[iy[:,None],ix[None,:]].astype(np.float32);del dem
 cg=contourpy.contour_generator(x=xs,y=ys,z=z,fill_type='OuterOffset')
 frame=box(-180,-85,180,85)
 def contour(level):
  coordinates,offsets=cg.filled(level,10000);polys=[]
  for pts,off in zip(coordinates,offsets):
   rings=[pts[a:b]for a,b in zip(off,off[1:])]
   if len(rings[0])<4:continue
   p=clean(Polygon(rings[0],rings[1:]))
   if p.area>=.002:polys.append(p)
  return clean(union_all(polys)).simplify(.012,preserve_topology=True)
 modern=clean(union_all([shape(f['geometry'])for f in read('public/data/ne_10m_land.geojson')['features']])).intersection(frame)
 base=contour(0);levels=[-130,-120,-110,-100,-90,-80,-70,-60,-50,-40,-30,-20,-10,0,5,10];manifest=[]
 for level in levels:
  key='m'+str(abs(level))if level<0 else'p'+str(level)
  existing=OUT/f'land-{key}.geojson'
  reuse='--reuse'in sys.argv and level<=0 and existing.exists()
  rawland=contour(level)if level and not reuse else base
  # Anchor the present coastline to the same Natural Earth base used by the
  # atlas. DEM discretisation must not remove existing modern island outlines.
  land=shape(json.loads(existing.read_bytes())['features'][0]['geometry'])if reuse else clean(union_all([modern,rawland.difference(base)]))if level<0 else clean(modern.difference(base.difference(rawland)))if level>0 else modern
  land=clean(land);ocean=clean(frame.difference(land))
  for kind,g in [('land',land),('ocean',ocean)]:
   write(f'public/data/paleogeography/{kind}-{key}.geojson',dict(type='FeatureCollection',features=[dict(type='Feature',properties=dict(seaLevelMeters=level,method='海底高程阈值复原',source=NOAA),geometry=mapping(g))]))
  cultural=[]
  zones=[('doggerland','多格兰中石器人群',-10000,-6000,box(-2,51,9,58),'https://archaeologydataservice.ac.uk/researchframeworks/mesolithic/Wiki.jsp?page=Doggerland'),('sunda','巽他陆架史前人群',-50000,-6000,box(98,-9,119,9),'https://ijog.geologi.esdm.go.id/index.php/IJOG/article/view/182'),('sahul','萨胡尔史前人群',-45000,-7000,box(127,-18,145,-5),'https://aws-digital-classroom.nma.gov.au/learning-modules/1/migration-sahul'),('beringia-west','白令陆桥人群',-15000,-10000,box(165,60,180,70),'https://www.nps.gov/articles/bering.htm'),('beringia-east','白令陆桥人群',-15000,-10000,box(-180,60,-160,70),'https://www.nps.gov/articles/bering.htm')]
  exposed=clean(land.difference(modern))
  for ident,label,a,b,region,source in zones:
   g=clean(exposed.intersection(region))
   if g.is_empty or g.area<.02:continue
   ident=ident.replace('-west','').replace('-east','');p=dict(NAME='Submerged prehistoric communities - '+ident,SUBJECTO='Submerged prehistoric communities - '+ident,qid='local:paleo-'+ident,entityId='local:paleo-'+ident,displayName=label,sourceRecord=TAG+':'+ident+':'+key,validFrom=a,validTo=b,representationKind='human-presence',regionalCollection=True,sourceUrl=source,contextSource=source,representationNote='现今海底、低海面时出露的陆架人群活动参考；不是一个统一国家，颜色不表示精确领土或遍布每一处。考古证据、分期和古岸线均有不确定性。',accuracy='以区域考古研究范围与当时出露陆架相交，未推定现代海底每处都有遗址。',seaLevelMeters=level)
   cultural.append(dict(type='Feature',properties=p,geometry=mapping(g)))
  write(f'public/data/paleogeography/cultures-{key}.geojson',dict(type='FeatureCollection',features=cultural))
  manifest.append(dict(level=level,key=key));print('Paleocoast',level,'land area degrees²',round(land.area),flush=True)
 write('public/data/paleogeography/index.json',dict(revision=TAG,curve=curve,levels=manifest,source=NOAA,doi='10.5194/cp-12-1079-2016',terrainSource='https://registry.opendata.aws/terrain-tiles/',model='以1950为BP基准；海平面千年序列插值，岸线按最接近的10米高程切片切换。',resolution='高程瓦片约5公里，计算网格约10公里；不是逐年岸线测绘。',limitations=['海平面重建通常有约9—12米的一倍标准差不确定性。','未求解冰川均衡调整、沉降、侵蚀淤积和河道迁移；局地岸线只是概化参考。','时间轴始于约12.5万年前，未伪造百万年尺度的板块漂移动画；板块运动通常每年数厘米。','现代湖泊、河流及高倍率地形在古地理模式关闭，避免被误认为当时水系。'],sha256=hashlib.sha256(raw.encode()).hexdigest()))
if __name__=='__main__':
 main()
 from prepare_paleo_archives import main as archives
 archives()
 from compact_paleogeography import main as compact
 compact()
 from prepare_ocean_render_mesh import main as render_mesh
 render_mesh([])

