"""Cache NII/CODH public old-kuni tiles with normal system TLS validation."""
import concurrent.futures,subprocess,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];DEST=ROOT/'.local/japan-kuni'
def main():
 DEST.mkdir(exist_ok=True);curl=shutil.which('curl.exe')or shutil.which('curl')
 if not curl:raise RuntimeError('curl is required for the system certificate store')
 def get(tile):
  x,y=tile;path=DEST/f'5-{x}-{y}.pbf'
  if path.exists():return path.name+' cached'
  pending=path.with_suffix('.part');url=f'https://geoshape.ex.nii.ac.jp/kg/vector/tile/kuni/5/{x}/{y}.pbf'
  r=subprocess.run([curl,'--fail','--silent','--show-error','--connect-timeout','12','--max-time','45',url,'--output',str(pending)],capture_output=True,text=True)
  if r.returncode==0:pending.replace(path);return path.name+' downloaded'
  if pending.exists():pending.unlink()
  return path.name+' unavailable (may be an ocean-only tile)'
 with concurrent.futures.ThreadPoolExecutor(max_workers=2)as pool:
  for r in pool.map(get,[(x,y)for x in range(26,30)for y in range(11,14)]):print(r,flush=True)
 subprocess.run(['node','scripts/decode_japan_kuni.mjs'],cwd=ROOT,check=True)
if __name__=='__main__':main()
