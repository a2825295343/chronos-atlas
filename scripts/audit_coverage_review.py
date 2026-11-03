"""Compare the actual pre-repair inputs to current map coverage and landmarks."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'.local/python'))
from shapely import union_all,make_valid
from shapely.geometry import shape,Point,box
def read(p):return json.loads((ROOT/p).read_bytes())
def main():
 admin=read('.local/presentation/admin0.geojson')['features'];masks={n:make_valid(union_all([shape(f['geometry'])for f in admin if f['properties']['NAME_EN']in names]))for n,names in [('印度',['India']),('阿拉伯半岛',['Saudi Arabia','Yemen','Oman','United Arab Emirates','Qatar','Kuwait','Bahrain']),('高加索',['Georgia','Armenia','Azerbaijan'])]};russia=next(make_valid(shape(f['geometry']))for f in admin if f['properties']['NAME_EN']=='Russia');masks['高加索']=union_all([masks['高加索'],russia.intersection(box(37.5,41,49.5,45.2))]);masks['全球早期资料']=union_all([make_valid(shape(f['geometry']))for f in admin if f['properties']['NAME_EN']not in ['Antarctica','Greenland']]);cache={}
 def frame(folder,year):
  key=(folder,year//100)
  if key not in cache:cache[key]=read(folder+'/'+str(year//100)+'.geojson')['features']
  latest={}
  for f in cache[key]:
   p=f['properties'];n=p['NAME']
   if p['validFrom']<=year<=p['validTo']and(n not in latest or(p['validFrom'],-p['validTo'])>(latest[n]['properties']['validFrom'],-latest[n]['properties']['validTo'])):latest[n]=f
  return [(f['properties'],make_valid(shape(f['geometry'])))for f in latest.values()]
 rows=[]
 for name,years in [('印度',[1500,1600,1750,1800,1857,1900,1950]),('高加索',[1500,1750,1800,1850,1900,1922,2000]),('阿拉伯半岛',[1500,1600,1750,1800,1850,1900,1923,1932,1950]),('全球早期资料',[-3000,-1000,-500,100,500,1000,1300])]:
  mask=masks[name];beforefolder='.local/'+('early-coverage-2026-11-01'if name=='全球早期资料'else'regional-coverage-2026-11-01')+'/original-shards'
  for year in years:
   stats=[]
   for folder in [beforefolder,'public/data/temporal']:
    active=frame(folder,year);geoms=[g.intersection(mask)for p,g in active if g.intersects(mask)];gap=mask.difference(union_all(geoms));stats.append({'unassociatedPlanarAreaPercent':round(100*gap.area/mask.area,2),'intersectingRecords':len(geoms),'culturalOrCommunityRecords':sum(p.get('regionalCollection',False)for p,g in active if g.intersects(mask))})
   rows.append({'region':name,'year':year,'before':stats[0],'after':stats[1]});print(name,year,stats[0]['unassociatedPlanarAreaPercent'],'->',stats[1]['unassociatedPlanarAreaPercent'],flush=True)
 landmarks=[]
 for year,label,point in [(1500,'艾哈迈达巴德',[72.58,23.02]),(1500,'今博帕尔附近',[77.41,23.26]),(1600,'今金奈附近',[80.27,13.08]),(1750,'科钦',[76.27,9.93]),(1750,'海得拉巴',[78.49,17.39]),(1857,'勒克瑙',[80.95,26.85]),(1900,'孟买',[72.88,19.08]),(1750,'今格罗兹尼附近',[45.69,43.32]),(1850,'彼得罗夫斯科耶',[47.5,42.98]),(1900,'苏呼米',[41.02,43]),(1750,'利雅得',[46.72,24.69]),(1750,'尼兹瓦',[57.53,22.93]),(1750,'亚丁',[45.03,12.79]),(1900,'哈伊勒',[41.69,27.52])]:
  active=frame('public/data/temporal',year);owners=[{'name':p['NAME'],'label':p.get('displayName',p['NAME']),'kind':p.get('representationKind','polity')}for p,g in active if g.covers(Point(point))];landmarks.append({'year':year,'place':label,'point':point,'owners':owners})
 report={'reviewedAt':'2026-11-01','rows':rows,'landmarks':landmarks,'regional':read('public/data/regional-coverage-review.json')['summary'],'early':read('public/data/early-coverage-review.json')['summary'],'namedRulers':read('public/data/coverage-reigns-review.json')['summary'],'newWars':32,'method':'在同一地理遮罩内比较修订前输入与修订后的多边形覆盖；平面面积比例只作同图源对比，不是史实准确率、人口密度、实控面积或文明完整度。','limitations':['古代和史前仍有大量边缘与人物无法核定。','以文化或地域集合补出的背景，不等于已复原其中每个国家和统治者。','年份可逐年查询，但无新证据时会沿用有来源的分期轮廓。']};report['namedRulers']['verifiedWikiReigns']=report['namedRulers']['records'];report['namedRulers']['sourcedFollowups']=len(read('public/data/coverage-ruler-followup.json')['records']);report['namedRulers']['records']+=report['namedRulers']['sourcedFollowups'];report['edges']=read('public/data/coverage-edge-review.json')['summary'];(ROOT/'public/data/coverage-review.json').write_text(json.dumps(report,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 print('Unresolved checked landmarks',[r['place']for r in landmarks if not r['owners']],flush=True)
if __name__=='__main__':main()
