"""Fill identified Kham and Amur omissions without annexing existing owners."""
from territory_repair_stage import ROOT,Stage,read,write,clean
from shapely.geometry import shape,box
from shapely import union_all
TAG='kham-amur-2026-11-01'
KHAM='https://mingqing.sinica.edu.tw/mingchingadminweb/SysModule/mvc/friendly_print.aspx?id=275'
AMUR='https://www.neac.gov.cn/seac/ztzl/201806/1066881.shtml'

def main():
 stage=Stage(TAG,range(13,17));admin=read('.local/ne_10m_admin_1_states_provinces.geojson')['features'];defs={}
 def province(country,names):return clean(union_all([shape(f['geometry'])for f in admin if f['properties'].get('admin')==country and f['properties'].get('name')in names]))
 def fill(n,l,q,g,a,b,url,note):
  defs[n]={'label':l,'qid':q,'from':a,'to':b,'source':url,'note':note}
  for lo,hi in stage.periods(g,a,b):stage.repair(g,lo,hi,[(n,l,q,g,url,note,{'regionalCollection':True,'representationKind':'regional-polities','representationNote':note,'inferredBoundary':True})])
 kham=clean(province('China',['Sichuan','Xizang']).intersection(box(95,26,103.7,35)))
 fill('Chakla Tusi','明正土司','local:chakla-tusi',clean(kham.intersection(box(101.6,29.7,102.3,30.4))),1645,1647,KHAM,'打箭炉、康定附近明正土司核心的定位概化；仅补原图明清交替的空缺。土司受封、名义归属与直接军政控制不能等同，不将空缺直接扩展成清朝或和硕特汗国领土。')
 fill('Kham Tusi Communities','康区土司诸部','local:kham-tusi-1645',kham,1645,1647,KHAM,'明清交替期康区地方土司、寺院和军政社群的概览；不是一个统一国家。仅补空缺，保留已有西藏、和硕特、南明与其他政权轮廓，不使用现代省域作为当时的精确疆界。')
 # Black River and Lower Amur groups were not a unified "blank" polity.
 # Keep existing Ming/Later Jin/Qing ownership; do not colour all Northeast Asia Ming.
 mainland=clean(union_all([province('China',['Heilongjiang','Jilin']),province('Russia',['Amur','Khabarovsk','Primor\'ye'])]))
 if mainland.is_empty:raise ValueError('Missing Northeast locating masks')
 fill('Amur Local Communities','黑龙江诸部','local:amur-communities',clean(mainland.intersection(box(120,43.5,136,55))),1368,1644,AMUR,'黑龙江、松花江北部等原图遗漏地域中的女真及其他地方社群概览，并非统一国家或全域直接受明廷管辖。奴儿干都司、羁縻卫所、朝贡与地方首领之间的关系须按阶段理解；仅补已有势力之外的空白。')
 fill('Lower Amur Local Communities','黑龙江下游诸部','local:lower-amur-communities',clean(mainland.intersection(box(136,46,143,55))),1368,1644,AMUR,'黑龙江下游吉列迷等地方社群的概化分布；不等同单一民族国家。明代文献中的族称和羁縻关系保留历史语境，不据现代省界认定统一行政控制。')
 stage.finish('kham-amur-review.json')
 facts=read('public/data/polity-facts.json')
 for n,d in defs.items():
  q=d['qid'];e=facts['entities'].setdefault(q,{'en':n,'label':d['label'],'description':d['note'],'fields':{}});facts['labels'][q]=d['label']
  for field,text in [('government','土司及地方政治组织'if 'Kham'in n or n=='Chakla Tusi'else'多个地方首领、部族及社群组织并存；不是统一中央政府'),('ruler','各地土司及地方首领（此地域集合不设共同君主）')]:
   rows=e['fields'].setdefault(field,[]);rows[:]=[r for r in rows if r.get('supplement')!=TAG];rows.append({'value':text,'label':text,'from':d['from'],'to':d['to'],'at':None,'kind':'collective','roleLabel':'地方政治组织','citation':[d['source']],'supplement':TAG})
 write('public/data/polity-facts.json',facts);write('public/data/kham-amur-definitions.json',defs)
 print('Kham and Northeast groups',len(defs),flush=True)

if __name__=='__main__':main()
