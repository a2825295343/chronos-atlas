"""Natural Earth admin-1 geographic reference, explicitly modern (not historical)."""
from download_data import save, DEST
import json, math

def simplify(points,epsilon=.003):
    if len(points)<5:return points
    a,b=points[0],points[-1]
    dx,dy=b[0]-a[0],b[1]-a[1]
    def distance(p):
        t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/(dx*dx+dy*dy or 1)))
        return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
    index=max(range(1,len(points)-1),key=lambda i:distance(points[i]))
    if distance(points[index])>epsilon:
        return simplify(points[:index+1],epsilon)[:-1]+simplify(points[index:],epsilon)
    return [a,b]

def main():
    original=save('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_1_states_provinces.geojson',DEST.parent.parent/'.local'/'ne_10m_admin_1_states_provinces.geojson')
    data=json.loads(original)
    def ring(r):
        midpoint=len(r)//2
        output=simplify(r[:midpoint+1])[:-1]+simplify(r[midpoint:])
        return [[round(x,4),round(y,4)] for x,y,*_ in output] if len(output)>=4 else r
    for i,f in enumerate(data['features']):
        p=f['properties'];region_id=p.get('adm1_code') or str(i);f['properties']={'id':region_id,'label':p.get('name_zh') or p.get('name') or ('未命名参考区 '+region_id),'native':p.get('name') or '原始资料未命名','country':p.get('admin'),'type':p.get('type_en'),'wikidata':p.get('wikidataid'),'source':'Natural Earth · modern reference'}
        g=f['geometry']
        if g['type']=='Polygon':g['coordinates']=[ring(r) for r in g['coordinates']]
        else:g['coordinates']=[[ring(r) for r in poly] for poly in g['coordinates']]
    (DEST/'provinces.geojson').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print(f"Prepared {len(data['features'])} modern reference regions.")

if __name__=='__main__':main()
