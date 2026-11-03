"""Hole-free ocean drawing pieces; geographical source masks stay untouched.

Low-zoom integer quantization can reverse a tiny hole's winding and cause
MapLibre's classifyRings to attach subsequent continent holes to that ring.
Cutting on shared meridians/parallels preserves exact area while removing
the renderer's need to infer exterior/hole relationships.
"""
import argparse,concurrent.futures,json,time
from pathlib import Path
from territory_repair_stage import ROOT,read,write,clean
from shapely.geometry import shape,mapping,box,Polygon
from shapely import union_all
TAG='ocean-render-mesh-2026-11-02'
def polygons(g):
 if g.is_empty:return []
 if g.geom_type=='Polygon':return[g]
 return[p for part in g.geoms for p in polygons(part)]
def partition(g, seam_patches=None):
 pending=polygons(g);out=[];cuts=0
 while pending:
  p=pending.pop();w,s,e,n=p.bounds
  if e-w>30 or n-s>20:
   axis=0 if (e-w)/30>=(n-s)/20 else 1;cut=(w+e)/2 if axis==0 else(s+n)/2
  elif p.interiors:
   # Median hole centres balance the work; a line through a hole opens it
   # into the exterior of both resulting pieces, with no area removed.
   centers=sorted((r.bounds[0]+r.bounds[2])/2 for r in p.interiors);axis=0;cut=centers[len(centers)//2]
  else:out.append(p);continue
  regions=[box(w,s,cut,n),box(cut,s,e,n)]if axis==0 else[box(w,s,e,cut),box(w,cut,e,n)]
  pieces=[q for region in regions for q in polygons(clean(p.intersection(region)))]
  if len(pieces)<2 or max(q.area for q in pieces)>=p.area-1e-14:
   # Width can round to a degenerate cut at a touching hole: try its
   # latitude instead. Never discard a hole or buffer the geographic mask.
   if not p.interiors:raise ValueError('Non-progressing geographic cut')
   axis=1;r=max(p.interiors,key=lambda r:Polygon(r).area);cut=(r.bounds[1]+r.bounds[3])/2
   pieces=[q for region in [box(w,s,e,cut),box(w,cut,e,n)]for q in polygons(clean(p.intersection(region)))]
   if len(pieces)<2:raise ValueError('Cannot open ocean hole')
  if seam_patches is not None:
   # Overlap artificial cut edges only. Intersect with the actual water
   # so the render patches cannot paint over islands or shorelines.
   pad=.065
   strip=box(cut-pad,s,cut+pad,n) if axis==0 else box(w,cut-pad,e,cut+pad)
   patches,_=partition(clean(p.intersection(strip)))
   seam_patches.extend(q for q in patches if q.area>=.015)
  pending.extend(pieces);cuts+=1
 return out,cuts
def generate(path):
 started=time.perf_counter();source=read(path);geoms=[clean(shape(f['geometry']))for f in source['features']];parts=[];seams=[];cuts=0
 for g in geoms:
  ps,c=partition(g,seams);parts.extend(ps);cuts+=c
 assert all(p.is_valid and not p.interiors for p in parts)
 # Cuts share exactly the same coordinates and have no area overlap.
 expected=sum(g.area for g in geoms);actual=sum(p.area for p in parts);assert abs(actual-expected)<1e-6,(path,expected,actual)
 if path.endswith('ocean-mask-hd.geojson'):target='public/data/ocean-mask-render.geojson'
 else:target=path.replace('/ocean-','/ocean-render-')
 result={'type':'FeatureCollection','features':[{'type':'Feature','properties':{},'geometry':mapping(p)}for p in parts]+[{'type':'Feature','properties':{'seamPatch':True},'geometry':mapping(p)} for p in seams]}
 write(target,result)
 return{'source':path,'target':target,'features':len(parts),'seamPatches':len(seams),'cuts':cuts,'holes':0,'areaDifferenceDegrees2':actual-expected,'seconds':round(time.perf_counter()-started,2)}
def main(argv=None):
 parser=argparse.ArgumentParser();parser.add_argument('--level');parser.add_argument('--workers',type=int,default=3);args=parser.parse_args(argv)
 paths=[f'public/data/paleogeography/ocean-{args.level}.geojson']if args.level else['public/data/ocean-mask-hd.geojson',*[str(p.relative_to(ROOT)).replace('\\','/')for p in sorted((ROOT/'public/data/paleogeography').glob('ocean-*.geojson'))if not p.name.startswith('ocean-render-')]]
 results=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers)as pool:
  for r in pool.map(generate,paths):results.append(r);print(json.dumps(r,ensure_ascii=False),flush=True)
 if args.level and(ROOT/'public/data/ocean-render-review.json').exists():
  previous={r['target']:r for r in read('public/data/ocean-render-review.json')['sources']};previous.update({r['target']:r for r in results});results=list(previous.values())
 write('public/data/ocean-render-review.json',{'revision':TAG,'method':'沿共享经线、纬线切分为无内环Polygon；切缝另用限定在原遮罩内的细水面补片覆盖，保留海岸线。','sources':results})
if __name__=='__main__':main()


