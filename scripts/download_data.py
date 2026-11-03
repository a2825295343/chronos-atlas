"""Download versioned public source data, preserving attribution. Safe to resume."""
import concurrent.futures, hashlib, json, pathlib, time, urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEST = ROOT / 'public' / 'data'
BASE = 'https://raw.githubusercontent.com/aourednik/historical-basemaps/master/'

def get(url):
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={'User-Agent':'GuanlanAtlas/1.0'})
            with urllib.request.urlopen(req, timeout=70) as response:
                return response.read()
        except Exception:
            if attempt == 5: raise
            time.sleep(1 + attempt)

def save(url, path):
    if path.exists(): return path.read_bytes()
    content = get(url)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return content

def main():
    DEST.mkdir(parents=True, exist_ok=True)
    index = json.loads(save(BASE+'index.json', DEST/'index.json'))
    def download(entry):
        data = save(BASE+'geojson/'+entry['filename'], DEST/entry['filename'])
        parsed = json.loads(data)
        entry['features'] = len(parsed['features'])
        entry['sha256'] = hashlib.sha256(data).hexdigest()
        print(entry['year'],entry['features'],len(data),flush=True)
        return entry
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        entries = list(pool.map(download, index['years']))
    (DEST/'manifest.json').write_text(json.dumps(entries,ensure_ascii=False),encoding='utf-8')
    save(BASE+'LICENSE', DEST/'HISTORICAL_BASEMAPS_LICENSE.txt')
    # Natural Earth public domain modern geography, not historical provincial borders.
    ne = 'https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/'
    for name in ['ne_110m_land','ne_110m_ocean','ne_50m_admin_1_states_provinces','ne_10m_land','ne_10m_ocean','ne_10m_lakes','ne_10m_rivers_lake_centerlines']:
        save(ne+name+'.geojson', DEST/(name+'.geojson'))
    print('All public datasets downloaded.',flush=True)

if __name__ == '__main__': main()
