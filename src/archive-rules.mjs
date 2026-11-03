export function applies(row,year){return (row.from==null||row.from<=year)&&(row.to==null||row.to>=year)&&(row.at==null||row.at===year)&&(row.verifiedThrough==null||year<=row.verifiedThrough);}
export function scopedFacts(entity,field,year){
 const rows=entity?.fields[field]||[],leadership=['ruler','headOfGovernment','imperialSovereign'].includes(field),dated=rows.filter(row=>(leadership?(row.from!=null||row.at!=null):(row.from!=null||row.to!=null||row.at!=null))&&applies(row,year));
 if(dated.length){
  if(leadership){
   const people=new Map(),score=r=>(r.from!=null?4:0)+(r.to!=null?2:0)+(r.at!=null?3:0)+(r.rank==='preferred'?2:0)+(r.derived?0:.1);
   for(const row of dated){
    const previous=people.get(row.value),best=!previous||score(row)>score(previous)||(score(row)===score(previous)&&(row.from??row.at??-Infinity)>(previous.from??previous.at??-Infinity))?row:previous;
    const appointments=new Map();
    for(const r of [...(previous?.appointments||[]),...(previous&&!previous.appointments?[previous]:[]),row]){
     const key=[r.from,r.to,r.at,r.roleLabel||''].join('|');appointments.set(key,{...r,appointments:undefined});
    }
    const records=[...appointments.values()].filter(r=>r.roleLabel||![...appointments.values()].some(s=>s.roleLabel&&s.from===r.from&&s.to===r.to&&s.at===r.at));
    people.set(row.value,{...best,appointments:records});
   }
   return {rows:[...people.values()],reference:false};
  }
  return {rows:dated,reference:false};
 }
 if(leadership)return {rows:[],reference:false};
 return {rows:rows.filter(row=>row.from==null&&row.to==null&&row.at==null),reference:true};
}
export function selectFlag(records,year){
 const dated=records.filter(r=>(r.from!=null||r.to!=null||r.at!=null)&&applies(r,year));
 if(dated.length)return {flag:dated[0],reference:false};
 const unscoped=records.find(r=>r.from==null&&r.to==null&&r.at==null);
 return {flag:unscoped,reference:true};
}
/** A territory's central sovereign is not automatically its local governor. */
export function leadershipFor(entity,parent,year){
 const local=scopedFacts(entity,'ruler',year).rows;
 const superior=scopedFacts(parent,'ruler',year).rows;
 const fromSovereign=local.length===0&&superior.length>0;
 return {rows:fromSovereign?superior:local,fromSovereign,governmentRows:scopedFacts(fromSovereign?parent:entity,'headOfGovernment',year).rows};
}
/** COW uses continuous state codes across some regime/name changes. */
export function cowPolityName(code,fallback,year){
 const id=String(code);
 if(id==='345'&&year<1918)return year>=1882?'塞尔维亚王国':'塞尔维亚公国';
 if(id==='365'){
  if(year===1917)return '俄国（年内政权更替）';
  if(year>=1922&&year<=1990)return '苏联';
  if(year===1991)return '苏联／俄罗斯（年内更替）';
  if(year>=1918&&year<=1921)return '苏维埃俄国';
  if(year>=1721&&year<1917)return '俄罗斯帝国';
 }
 if(id==='640'&&year<=1922)return '奥斯曼帝国';
 if(id==='255'){
  if(year>=1871&&year<=1918)return '德意志帝国';
  if(year>=1919&&year<=1932)return '魏玛共和国';
  if(year>=1933&&year<=1945)return '纳粹德国';
  if(year<1871)return '普鲁士';
 }
 if(id==='710'){
  if(year<=1911)return '清朝';
  if(year<=1948)return '中华民国';
  if(year===1949)return '中国（年内政权更替）';
  return '中华人民共和国';
 }
 return fallback;
}
