import concurrent.futures,pathlib,sys
sys.path.insert(0,'scripts')
from download_data import get
root=pathlib.Path('.local/presentation');root.mkdir(exist_ok=True)
urls={
 'NotoSerifSC.ttf':'https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifsc/NotoSerifSC%5Bwght%5D.ttf',
 'NotoSerifSC-OFL.txt':'https://raw.githubusercontent.com/google/fonts/main/ofl/notoserifsc/OFL.txt',
 'admin0.geojson':'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_admin_0_countries.geojson'}
for y in [1861,1871,1881,1901,1911,1921,1931,1936,1951,1961,1971]:urls[f'italy-{y}.geojson']=f'https://demopast.it/data/geojson/province_{y}.geojson'
def run(item):
 n,url=item;p=root/n
 if not p.exists():p.write_bytes(get(url))
 print(n,p.stat().st_size,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=3)as pool:list(pool.map(run,urls.items()))
