"""Download public named state rosters using the Windows trust store."""
import subprocess
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PAGES=['Qin_(state)','Jin_(Chinese_state)','Chu_(state)','Qi_(state)','Lu_(state)',
       'Song_(state)','Zheng_(state)','Cai_(state)','Yan_(state)','Zhao_(state)',
       'Wei_(state)','Han_(state)','Yue_(state)','Wu_(state)','Chen_(state)']
def download(page):
 path=ROOT/'.local/chinese-archives'/(page+'.html')
 if path.exists():return page,'cached'
 result=subprocess.run(['curl.exe','--fail','--silent','--show-error','--location','--max-time','45',
     'https://en.wikipedia.org/api/rest_v1/page/html/'+quote(page,safe=''),'-o',str(path)],capture_output=True,text=True)
 return page,result.returncode,result.stderr.strip()
if __name__=='__main__':
 with ThreadPoolExecutor(max_workers=2)as pool:
  for result in pool.map(download,PAGES):print(*result,flush=True)
