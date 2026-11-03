"""License-checked portraits for the exact humans in this expansion."""
import subprocess,urllib.parse
from territory_repair_stage import ROOT,read,write
from enrich_polities import simplify,label
import modern_archive_media as media

def download(url):
 parts=urllib.parse.urlsplit(url)
 if parts.scheme!='https'or parts.hostname not in {'commons.wikimedia.org','upload.wikimedia.org','thumb.wikimedia.org'}:raise ValueError('Unexpected public media host')
 url=urllib.parse.urlunsplit(parts._replace(query=''if parts.hostname!='commons.wikimedia.org'else parts.query,fragment=''))
 result=subprocess.run(['curl.exe','--fail','--location','--silent','--show-error','--max-time','25','--retry','1','--retry-delay','1','--retry-max-time','30',url],capture_output=True,timeout=65)
 if result.returncode:raise RuntimeError(result.stderr.decode('utf8',errors='replace').strip())
 return result.stdout

def main():
 people=read('.local/world-rosters/verified-people.json');db=read('public/data/portraits.json');files={}
 for q,e in people.items():
  claims=sorted([c for c in e.get('claims',{}).get('P18',[])if c.get('rank')!='deprecated'],key=lambda c:c.get('rank')!='preferred')
  for c in claims:
   if(s:=simplify(c))and isinstance(s['value'],str):files[q]=s['value'];break
 pool={r['file']:r for r in db['people'].values()if(ROOT/'public'/r['path'].lstrip('/')).exists()}
 media.request=download
 available,bad=media.images(files.values(),'portraits',pool,workers=2,downloader=download,original_fallback=False,thumbnail_width=120)
 for q,f in files.items():
  if f in available:db['people'][q]={**available[f],'label':label(people[q]),'source':'https://www.wikidata.org/wiki/'+q+'#P18','caption':'核对人物身份的画像、照片或纪念像；后世绘像不作为同时代写生保证'}
 write('public/data/portraits.json',db);write('public/data/world-roster-media-review.json',dict(reviewedAt='2026-11-02',people=len(people),imageCandidates=len(files),matched=sum(f in available for f in files.values()),failures=bad))
 print('World roster images',sum(f in available for f in files.values()),'/',len(files),'download failures',len(bad),flush=True)
if __name__=='__main__':main()
