import {participantsAt} from './conflicts.mjs';
import {cowCode} from './country-codes.mjs';
const aliases={
 'Kingdom of Cambodia':['Cambodia','Khmer Empire','Post-Angkor Cambodia'],
 'Konbaung Dynasty':['Burma','Myanmar'],
 'Ashanti Empire':['Ashanti','Asante'],
 'Ethiopian Empire':['Ethiopia','Ethiopians'],
 'Empire of Brazil':['Brazil'],
 'Argentine Republic':['Argentina'],
 'Argentine Confederation':['Argentina'],
 'Kingdom of Spain':['Spain','Spanish Empire','Habsburg Spain'],
 'British Empire':['United Kingdom','Kingdom of Great Britain','Great Britain'],
 'Communist Party of China':['CCP','PLA','Chinese communist forces'],
 'Han Kingdom (Liu Bang)':['Han','Han Dynasty','Western Han','Liu Bang'],
 'Gengshi Han':['Gengshi','Gengshi Regime','Gengshi Emperor'],
 'Northern Song':['Song Dynasty','北宋'],'Southern Song':['Southern Song Dynasty','Song Dynasty','南宋'],
 'Great Jin':['Jin Dynasty','Jin dynasty (1115–1234)','金朝'],
 'Eastern Jin':['Jin dynasty (266–420)','东晋'],
 'Austrian Hereditary Lands':['Austria','Habsburg Monarchy','House of Habsburg'],
 'Crown of the Kingdom of Poland':['Kingdom of Poland','Poland'],
 'Old Kingdom of Norway':['Norway','Kingdom of Norway'],'Kingdom of Norway':['Norway','Old Kingdom of Norway','Denmark-Norway','Sweden–Norway'],
 'Kingdom of Denmark':['Denmark'],
 'Kingdom of Sweden':['Sweden'],
 'Royal Hungary':['Kingdom of Hungary'],
};
/** Match a polity's actual dated participation, never every dynasty member. */
export function warInvolvesPolity(war,name,year,code){
 const matches=new Set([name,...(aliases[name]||[])]);
 const polityCode=code||cowCode(name,undefined,{},year);
 return participantsAt(war,year).some(p=>{
  if(p.polityPeriods?.length)return p.polityPeriods.some(r=>r.from<=year&&year<=r.to&&matches.has(r.name));
  if(polityCode&&p.code&&String(p.code)===polityCode)return true;
  return [p.name,...(p.polityNames||[])].some(n=>matches.has(n)||
   (polityCode&&cowCode(n.replace(/^Government of /,''),undefined,{},year)===polityCode));
 });
}
