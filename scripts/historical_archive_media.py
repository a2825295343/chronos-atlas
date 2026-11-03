"""Merge validated historical portraits and documented representative banners."""
import argparse,json,urllib.request,urllib.parse
from enrich_polities import ROOT,label,simplify
from fetch_historical_rulers import CACHE
from modern_archive_media import images
def read(p):return json.loads((ROOT/p).read_bytes())
def write(p,d):(ROOT/p).write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf8')
def cached_thumbnail(url):
 # Commons imageinfo appends analytics queries; canonical cache paths avoid
 # expensive cache misses. Never re-request a rate-limited original image.
 url=urllib.parse.urlunsplit(urllib.parse.urlsplit(url)._replace(query='',fragment=''))
 with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.5 educational history atlas'}),timeout=25)as response:return response.read()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('stage',choices=['flags','portraits','all'],nargs='?',default='all');args=parser.parse_args()
 failures=read('public/data/historical-media-review.json').get('failures',{}) if args.stage!='all'and(ROOT/'public/data/historical-media-review.json').exists()else{}
 if args.stage in ['flags','all']:
  config=read('public/data/historical-flag-supplements.json');db=read('public/data/flags.json');pool={r['file']:r for rs in db['entities'].values()for r in rs if(ROOT/'public'/r['path'].lstrip('/')).exists()}
  available,bad=images([r['file']for r in config['records']if not r.get('reconstructed')],'flags',pool,workers=2,downloader=cached_thumbnail);failures['flags']=bad
  for r in config['records']:
   if r['file']not in available and not r.get('reconstructed'):continue
   row={**available.get(r['file'],{}),**r,'at':None,'source':r['periodSource'],'supplement':'historical-flags-2026-10-31'}
   rows=[old for old in db['entities'].get(r['qid'],[])if not(old.get('supplement')=='historical-flags-2026-10-31'and old.get('from')==r['from'])];rows.append(row);db['entities'][r['qid']]=rows
  # A king's royal banner remains a royal banner when assigned to a constituent crown.
  db['entities']['Q171348']=db['entities'].get('Q577867',[])
  db['count']=len({r['path']for rs in db['entities'].values()for r in rs});write('public/data/flags.json',db)
 if args.stage in ['portraits','all']:
  people=json.loads((CACHE/'verified-ruler-people.json').read_bytes())
  if (CACHE/'russia-gap-people.json').exists():people.update(json.loads((CACHE/'russia-gap-people.json').read_bytes()))
  postwar=ROOT/'.local/postwar-review/verified-people.json'
  if postwar.exists():people.update(json.loads(postwar.read_bytes()))
  for extra in ['.local/global-archive-review/verified-people.json','.local/ancient-roster-review/verified-people.json','.local/reviewed-reigns/verified-people.json','.local/coverage-reigns/verified-people.json','.local/three-kingdoms/verified-people.json','.local/japanese-polities/verified-people.json','.local/japan-complete/verified-people.json','.local/vietnam-war-context/verified-people.json','.local/persia-gulf-archives/verified-people.json','.local/qin-xin-people/verified-people.json','.local/global-reigns-nov02/verified-people.json','.local/chinese-archives/verified-people.json']:
   if(ROOT/extra).exists():people.update(json.loads((ROOT/extra).read_bytes()))
  world=ROOT/'.local/world-rosters/verified-people.json'
  if world.exists():people.update(json.loads(world.read_bytes()))
  db=read('public/data/portraits.json');files={}
  for q,e in people.items():
   claims=[c for c in e.get('claims',{}).get('P18',[])if c.get('rank')!='deprecated'];claims.sort(key=lambda c:c.get('rank')!='preferred')
   for c in claims:
    s=simplify(c)
    if s and isinstance(s['value'],str):files[q]=s['value'];break
  pool={r['file']:r for r in db['people'].values()if(ROOT/'public'/r['path'].lstrip('/')).exists()};available,bad=images(files.values(),'portraits',pool,workers=2,downloader=cached_thumbnail,original_fallback=False,thumbnail_width=120);failures['portraits']=bad
  for q,file in files.items():
   if file in available:db['people'][q]={**available[file],'label':label(people[q]),'source':'https://www.wikidata.org/wiki/'+q+'#P18','caption':'按人物实体核对的历史画像、纪念像或照片；后世绘像不作为同时代写生保证'}
  write('public/data/portraits.json',db);print('Historical portrait candidates',len(files),'matched',sum(f in available for f in files.values()),flush=True)
 write('public/data/historical-media-review.json',{'reviewedAt':'2026-10-31','failures':failures});print('Historical media unavailable counts',{k:len(v)for k,v in failures.items()},flush=True)
if __name__=='__main__':main()


