/** COW retains state codes through transitions that change their territory. */
export function comparableEconomy(iso,year,name=''){
 if(iso==='DEU'&&year<1991)return false;
 if(iso==='VNM'&&(year<1976||['Republic of Vietnam','South Vietnam','Democratic Republic of Vietnam','North Vietnam'].includes(name)))return false;
 if(iso==='PAK'&&year<1972)return false;
 if(iso==='SDN'&&year<2011)return false;
 if(iso==='ETH'&&year<1993)return false;
 if(iso==='YEM'&&year<1990)return false;
 if(iso==='MYS'&&year>=1963&&year<=1965)return false;
 return true;
}
export function nationalObservation(database,code,year,name=''){
 if(!code)return null;
 const rows=database?.countries?.[code]?.observations;
 const lastComparable={
  'Soviet Union':1989,'Union of Soviet Socialist Republics':1989,'USSR':1989,
  'Socialist Federal Republic of Yugoslavia':1991,'West Germany':1989,
 }[name];
 if(lastComparable!=null&&year>lastComparable){
  // A clearly dated reference is preferable to substituting Russia/Serbia or
  // unified Germany. Never silently label the previous year as this year.
  const soviet=['Soviet Union','Union of Soviet Socialist Republics','USSR'].includes(name);
  if(year>lastComparable+(soviet?2:1)||!rows?.[lastComparable])return null;
  return {...rows[lastComparable],observationYear:lastComparable,reference:true,scopeNote:'政权解体／统一前的同辖区参考值；未把后继国家的统计套入本政权。'};
 }
 return rows?.[year]?{...rows[year],observationYear:year}:null;
}
