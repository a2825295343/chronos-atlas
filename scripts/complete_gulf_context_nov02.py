"""Local Gulf archive context and sourced period flags, independent of geometry."""
import copy
from territory_repair_stage import read,write
from modern_archive_media import images
from historical_archive_media import cached_thumbnail
TAG='gulf-context-2026-11-02'
def main():
 source='https://www.qatar.qa/en/qatar/al-adaam/'
 db=read('public/data/flags.json');files=['Flag of Qatar (1936–1949).svg','Flag of Qatar (1949–1971).svg']
 pool={r['file']:r for rs in db['entities'].values()for r in rs}
 available,failed=images(files,'flags',pool,workers=2,downloader=cached_thumbnail)
 if failed:raise ValueError(failed)
 rows=[{**available[f],'at':None,'role':'卡塔尔历史旗帜','source':source,'periodSource':source,'periodNote':'按历史旗式分期；1949年为旗式交接年，颜色及绘制比例存在文献与复原差别。','supplement':TAG,'from':a,'to':b}for f,a,b in [(files[0],1936,1949),(files[1],1949,1971)]]
 db['entities']['local:qatar-protectorate']=[r for r in db['entities'].get('local:qatar-protectorate',[])if r.get('supplement')!=TAG]+rows
 db['count']=len({r['path']for rs in db['entities'].values()for r in rs})
 write('public/data/flags.json',db)
 facts=read('public/data/polity-facts.json');e=facts['entities']['local:qatar-protectorate'];e['en']='Qatar (British-protected sheikhdom)'
 e['fields']['capital']=[dict(value='Q3861',label='多哈',citation=['https://diwan.gov.qa/en/About-Qatar/History-of-Qatar'],**{'from':1916,'to':1971})]
 write('public/data/polity-facts.json',facts)
 write('public/data/gulf-context-nov02-review.json',dict(reviewedAt='2026-11-02',flags=[r['file']for r in rows],sources=[source],note='历史卡塔尔旗用于本地政权档案；不再仅显示英国代表旗。'))
if __name__=='__main__':main()
