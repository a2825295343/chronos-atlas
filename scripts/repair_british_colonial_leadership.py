"""Bound a modern UK office claim that otherwise leaks into earlier centuries."""
from territory_repair_stage import read,write
import copy

def main():
 data=read('public/data/polity-facts.json')
 for row in data['entities']['Q145']['fields']['ruler']:
  if row['value']=='Q269412'and row.get('to')==1936 and (row.get('from')is None or row.get('dateSource','').startswith('Royal Household')):
   row.update({'from':1910,'citation':['https://www.royal.uk/george-v'],
               'dateSource':'Royal Household named reign 1910–1936','reviewedAt':'2026-11-02'})
 # Prime Minister is a continuing office. Retain its exact dated appointments
 # when looking up the contemporary kingdom, without copying modern rulers.
 for q,lo,hi in [('Q161885',1707,1800),('Q174193',1801,1921)]:
  target=data['entities'][q]['fields'].setdefault('headOfGovernment',[])
  target[:]=[r for r in target if r.get('supplement')!='british-colonial-leadership-2026-11-02']
  keys={(r['value'],r.get('from'),r.get('to'))for r in target}
  for r in data['entities']['Q145']['fields'].get('headOfGovernment',[]):
   if r.get('from')is None or r.get('to')is None or not('首相'in r.get('roleLabel','')or r.get('office')=='Q14211'):continue
   a,b=max(lo,r['from']),min(hi,r['to'])
   if a>b or(r['value'],a,b)in keys:continue
   row=copy.deepcopy(r);row.update({'from':a,'to':b,'supplement':'british-colonial-leadership-2026-11-02'});target.append(row);keys.add((r['value'],a,b))
 write('public/data/polity-facts.json',data)

if __name__=='__main__':main()
