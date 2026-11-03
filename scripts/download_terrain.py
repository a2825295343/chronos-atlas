"""Cache low-zoom global elevation and a Natural Earth raster for offline use."""
from download_data import get, save, DEST
import concurrent.futures, pathlib, math, io

def main():
    jobs=[(z,x,y) for z in range(6) for x in range(2**z) for y in range(2**z)]
    def tile(item):
        z,x,y=item
        save(f'https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png',DEST/'dem'/str(z)/str(x)/(str(y)+'.png'))
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
        for i,_ in enumerate(pool.map(tile,jobs),1):
            if i%100==0:print(f'Cached elevation: {i}/{len(jobs)}',flush=True)
    print(f'Cached {len(jobs)} elevation tiles, through zoom 5.',flush=True)
    save('https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/NotoSans%5Bwdth,wght%5D.ttf',DEST/'atlas-sans.ttf')
    save('https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/OFL.txt',DEST/'FONT_LICENSE.txt')
    save('https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/NotoSansSC%5Bwght%5D.ttf',DEST/'atlas-cjk.ttf')
    save('https://raw.githubusercontent.com/google/fonts/main/ofl/notosanssc/OFL.txt',DEST/'CJK_FONT_LICENSE.txt')
    print('Cached base raster and map glyphs.',flush=True)

if __name__=='__main__':main()
