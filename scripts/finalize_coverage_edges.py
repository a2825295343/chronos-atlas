"""Close verified coast omissions and mark remaining Deccan local polities."""
from territory_repair_stage import Stage,ROOT,read,write,clean
from shapely import union_all
from shapely.geometry import shape,Point,box
TAG='coverage-edge-refinement-2026-11-01'
def main():
 stage=Stage(TAG,range(14,21));admin=read('.local/presentation/admin0.geojson')['features'];provinces=read('.local/ne_10m_admin_1_states_provinces.geojson')['features'];definitions=read('public/data/regional-coverage-definitions.json')
 def country(n):return clean(union_all([shape(f['geometry'])for f in admin if f['properties']['NAME_EN']==n]))
 india=country('India');georgia=country('Georgia');abkhazia=clean(union_all([shape(f['geometry'])for f in provinces if f['properties']['admin']=='Georgia'and f['properties']['name']=='Abkhazia']))
 if abkhazia.is_empty:abkhazia=georgia.intersection(box(40,42.4,42.2,43.7))
 specs=[
 ('Kingdom of Cochin','科钦王国','local:kingdom-of-cochin',india.intersection(Point(76.27,9.93).buffer(.55)),1400,1782,'https://en.wikipedia.org/wiki/Kingdom_of_Cochin','沿海与河口的两套地理底图略有差异，补科钦核心陆地遗漏；已列欧洲控制区保持单列。',False),
 ('Russian Empire','俄罗斯帝国','Q34266',abkhazia,1864,1916,'https://en.wikipedia.org/wiki/Principality_of_Abkhazia','1864年取消阿布哈兹公国以后，补俄罗斯帝国在该地海岸的几何遗漏，不把现代俄罗斯国界当作1900年帝国边界。',False),
 ('Deccan Local Polities','德干地方诸邦','local:deccan-local-polities',india.intersection(box(73.5,14,80.5,20.5)),1650,1782,'https://en.wikipedia.org/wiki/Deccan','未能逐段关联到具体国家的德干地方邦、领主、军事与村社网络背景；已明确的苏丹国、马拉塔、迈索尔及海得拉巴等范围不覆盖、不合并。不是一个统一政府。',True),
  ('Saudi Arabia','沙特阿拉伯','Q851',country('Saudi Arabia'),1932,1944,'https://www.mofa.gov.sa/en/ksa/Pages/history.aspx','1932年王国成立以后原图遗漏的阿拉伯陆地。仅补空缺，以后续地理边界定位概化；南部1934年条约与其他未完全划界地带存在时序差异，不把此轮廓当作1932年即已确定的精确国界。',False),
 ]
 for n,l,q,g,lo,hi,url,note,regional in specs:
  for a,b in stage.periods(g,lo,hi):stage.repair(g,a,b,[(n,l,q,g,url,note,{'representationNote':note,'regionalCollection':regional,'representationKind':'regional-polities'if regional else'polity','inferredBoundary':True})])
  previous=definitions.get(n,{});definitions[n]={'label':l,'qid':q,'from':min(lo,previous.get('from',lo)),'to':max(hi,previous.get('to',hi)),'source':url,'note':note,'regional':regional}
 stage.finish('coverage-edge-review.json');write('public/data/regional-coverage-definitions.json',definitions)
if __name__=='__main__':main()
