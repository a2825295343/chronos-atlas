"""Bound vertex/JSON cost below the uncertainty of the paleocoast model."""
from territory_repair_stage import ROOT,read,write,clean
from shapely.geometry import shape,mapping,box
from shapely import set_precision
def rounded(value):
 if isinstance(value,(list,tuple)):return[rounded(v)for v in value]
 return round(value,4)if isinstance(value,float)else value
def geometry(g):return{'type':g.geom_type if not g.is_empty else'MultiPolygon','coordinates':rounded(mapping(g).get('coordinates',[]))}
def main():
 folder=ROOT/'public/data/paleogeography';before=sum(p.stat().st_size for p in folder.glob('*.geojson')if not p.name.startswith('ocean-render-'));frame=box(-180,-85,180,85)
 for p in sorted(folder.glob('land-*.geojson')):
  key=p.stem.removeprefix('land-');d=read(str(p.relative_to(ROOT)));land=clean(set_precision(clean(shape(d['features'][0]['geometry'])).simplify(.006,preserve_topology=True),.0001))
  d['features'][0]['geometry']=geometry(land);write(str(p.relative_to(ROOT)),d)
  ocean=read(f'public/data/paleogeography/ocean-{key}.geojson');ocean['features'][0]['geometry']=geometry(clean(frame.difference(land)));write(f'public/data/paleogeography/ocean-{key}.geojson',ocean)
  cultures=read(f'public/data/paleogeography/cultures-{key}.geojson')
  for f in cultures['features']:f['geometry']=geometry(clean(set_precision(clean(shape(f['geometry'])).simplify(.006,preserve_topology=True),.0001).intersection(land)))
  cultures['features']=[f for f in cultures['features']if f['geometry']['coordinates']];write(f'public/data/paleogeography/cultures-{key}.geojson',cultures)
 index=read('public/data/paleogeography/index.json');index['coordinatePrecisionDegrees']=.0001;index['simplificationDegrees']=.006;index['renderingNote']='渲染轮廓简化约0.006度、小数4位；小于约10公里计算网格的空间支持，不增加历史精度。';write('public/data/paleogeography/index.json',index)
 after=sum(p.stat().st_size for p in folder.glob('*.geojson')if not p.name.startswith('ocean-render-'));print('Paleogeography GeoJSON MB',round(before/1e6,1),'->',round(after/1e6,1),flush=True)
if __name__=='__main__':main()
