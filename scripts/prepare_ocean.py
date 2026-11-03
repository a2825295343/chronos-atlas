"""Split the detailed global ocean into smaller polygons for stable triangulation."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.local'/'python'))
from shapely.geometry import shape,mapping,box
from shapely import make_valid,intersection,union_all

def main():
    source=json.loads((ROOT/'public/data/ne_10m_ocean.geojson').read_text(encoding='utf-8'))
    ocean=union_all([make_valid(shape(f['geometry'])) for f in source['features']])
    features=[]
    for x in range(-180,180,30):
        for y in range(-90,90,30):
            clipped=intersection(ocean,box(x,y,x+30,y+30))
            if clipped.is_empty:continue
            if clipped.geom_type=='GeometryCollection':clipped=union_all([p for p in clipped.geoms if p.geom_type in ['Polygon','MultiPolygon']])
            if clipped.is_empty:continue
            features.append({'type':'Feature','properties':{},'geometry':mapping(clipped)})
    output={'type':'FeatureCollection','features':features}
    (ROOT/'public/data/ocean-mask-hd.geojson').write_text(json.dumps(output,separators=(',',':')),encoding='utf-8')
    print(f'Ocean mask: {len(features)} smaller polygons, original geographic shape preserved.',flush=True)

if __name__=='__main__':main()
