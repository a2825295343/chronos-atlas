"""Keep article titles and dates in provenance, not on the political map."""
import json
from polity_display_names import DISPLAY_NAMES
from territory_repair_stage import ROOT,read,write,label_path

def main():
 rows=[];qnames={}
 for path in (ROOT/'public/data/temporal').glob('*.geojson'):
  data=json.loads(path.read_bytes());changed=False
  for f in data['features']:
   p=f['properties'];name=p['NAME']
   if name not in DISPLAY_NAMES:continue
   label=DISPLAY_NAMES[name];old=p.get('displayName')
   if old!=label:
    p.setdefault('sourceDisplayName',old);p.update(displayName=label,labelPath=label_path(f['geometry'],label));changed=True
   # The pre-1806 Neapolitan kingdom must not inherit the French client-state ID.
   if name=='Kingdom of Naples (Napoleonic)'and p['validTo']<1806:
    p.setdefault('sourceQid',p.get('qid'));p.update(qid='Q173065',entityId='Q173065',identityReviewed=True,identityCorrection='1806年以前对应那不勒斯王国；拿破仑附庸政权的专门实体仅用于1806年起的时期。');changed=True
   qnames[p.get('qid')]=label
   rows.append({'name':name,'label':label,'from':p['validFrom'],'to':p['validTo']})
  if changed:path.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf8')
 for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
  labels=read(path);labels.update(DISPLAY_NAMES);write(path,labels)
 facts=read('public/data/polity-facts.json')
 for q,label in qnames.items():
  if q in facts['entities']:facts['entities'][q]['label']=label
  if q:facts['labels'][q]=label
 write('public/data/polity-facts.json',facts)
 path=ROOT/'src/color-groups.mjs';text=path.read_text(encoding='utf8');groups=json.loads(text[text.index('=')+1:].strip().removesuffix(';'));groups.update(DISPLAY_NAMES);path.write_text('export const colorGroups='+json.dumps(groups,ensure_ascii=False)+';\n',encoding='utf8')
 write('public/data/display-name-review.json',{'reviewedAt':'2026-10-31','records':rows,'policy':'名称中的条目消歧年代与英文释名不进入地图标题；有实际含义的占领、管理状态保留。','sources':['https://www.wikidata.org/wiki/Q173065','https://www.wikidata.org/wiki/Q48779892','https://sahistory.org.za/article/batavian-republic-1803-1806']})
 print('Reviewed display name records',len(rows),flush=True)
if __name__=='__main__':main()
