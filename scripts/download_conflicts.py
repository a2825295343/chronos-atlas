"""Download versioned conflict datasets and preserve original archives/codebooks."""
from pathlib import Path
import concurrent.futures,urllib.request,zipfile,io
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'.local/conflicts';DEST.mkdir(parents=True,exist_ok=True)
URLS={
 'ucdp261.zip':'https://ucdp.uu.se/downloads/ucdpprio/ucdp-prio-acd-261-csv.zip',
 'ucdp261-codebook.pdf':'https://ucdp.uu.se/downloads/ucdpprio/ucdp-prio-acd-261.pdf',
 'intra51.zip':'https://correlatesofwar.org/wp-content/uploads/Intra-State-Wars-v5.1.zip',
 'extra40.csv':'https://correlatesofwar.org/wp-content/uploads/Extra-StateWarData_v4.0.csv',
 'nonstate40.csv':'https://correlatesofwar.org/wp-content/uploads/Non-StateWarData_v4.0.csv',
}
def fetch(item):
 name,url=item;path=DEST/name
 try:
  if not path.exists():
   request=urllib.request.Request(url,headers={'User-Agent':'GuanlanAtlas/1.3 historical atlas'})
   with urllib.request.urlopen(request,timeout=45) as response:path.write_bytes(response.read())
  if name.endswith('.zip'):
   with zipfile.ZipFile(io.BytesIO(path.read_bytes())) as archive:
    for f in archive.infolist():
     if not f.is_dir() and f.filename.lower().endswith(('.csv','.pdf')):(DEST/Path(f.filename).name).write_bytes(archive.read(f))
  return name,path.stat().st_size
 except Exception as error:return name,str(error)
if __name__=='__main__':
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for result in pool.map(fetch,URLS.items()):print(result,flush=True)
