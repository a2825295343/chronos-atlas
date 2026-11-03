"""Context for exposed shelves, with no fictitious unified state or ruler."""
from territory_repair_stage import ROOT,read,write
TAG='paleogeography-2026-11-02'
def main():
 facts=read('public/data/polity-facts.json');identities={}
 for path in sorted((ROOT/'public/data/paleogeography').glob('cultures-*.geojson')):
  d=read(str(path.relative_to(ROOT)))
  for f in d['features']:
   p=f['properties']
   if p['qid']=='local:paleo-sahul':p['sourceUrl']=p['contextSource']='https://aws-digital-classroom.nma.gov.au/learning-modules/1/migration-sahul'
   identities.setdefault(p['qid'],p)
  write(str(path.relative_to(ROOT)),d)
 for q,p in identities.items():
  fields={}
  for field,text in [('government','区域内存在不同的狩猎采集人群与社会联系，并非统一国家；不能由古岸线推定共同政治组织。'),('religion','本条尚未综合足以确定共同信仰制度的考古证据；不据人群分布指定统一国教。'),('ideology','史前考古分布不适用现代国家意识形态分类。'),('conflictEvidence','本条没有足以编制具名交战双方、逐年战史与兵力的证据。')]:
   fields[field]=[{'value':text,'label':text,'from':p['validFrom'],'to':p['validTo'],'at':None,'citation':[p['sourceUrl']],'supplement':TAG}]
  facts['entities'][q]={'label':p['displayName'],'en':p['NAME'],'description':'今已被海水覆盖的陆架人群活动区域参考，不是历史上的统一国家。','fields':fields};facts['labels'][q]=p['displayName']
 write('public/data/polity-facts.json',facts)
 write('public/data/paleo-communities-review.json',{'reviewedAt':'2026-11-02','regions':[{k:p[k]for k in ['qid','displayName','validFrom','validTo','sourceUrl']}for p in identities.values()],'interpretation':'考古与古地理范围概览，不推定统一政权、共享君主、国旗或固定疆界。'})
 print('Submerged shelf community contexts',len(identities))
if __name__=='__main__':main()
