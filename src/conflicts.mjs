export const inPeriods=(periods,year)=>(periods||[]).some(([from,to])=>from<=year&&year<=to);
const canonical=(name,year)=>{
 const key=name.replace(/^Government of /,'').replace(/Russia \(Soviet Union\)/,'Russia').replace(/Vietnam \(North Vietnam\)/,'North Vietnam').replace(/Yemen \(North Yemen\)/,'Yemen').replace(/Myanmar \(Burma\)/,'Myanmar').replace(/Serbia \(Yugoslavia\)/,'Serbia').trim();
 return ({USSR:'Russia','Soviet Union':'Russia','Republic of China':'China','Republic of Vietnam':'South Vietnam','Vietnam':year<=1975?'North Vietnam':'Vietnam','North Vietnam':year>=1976?'Vietnam':'North Vietnam','Viet Cong':'National Liberation Front of South Vietnam',CCP:'Chinese communist forces',PLA:'Chinese communist forces',Communists:'Communist forces',DSE:'Communist forces',Vietminh:'Viet Minh','Viet minh':'Viet Minh'})[key]||key;
};
function withExtra(rows,war,year){
 for(const p of war.detail?.extraParticipants||[])if(inPeriods(p.periods,year)){
  const anchor=p.sameSideAs?rows.find(r=>canonical(r.name,year)===canonical(p.sameSideAs,year)):undefined,side=anchor?.side||p.side;
  if(!rows.some(r=>r.side===side&&canonical(r.name,year)===canonical(p.matchName||p.name,year)))rows.push({...p,side});
 }
 return rows;
}
export function participantsAt(war,year){
 const annual=war.annual?.[year];
 if(annual){const rows=[];for(const [key,side,role] of [['sideA','1','主要交战方'],['sideB','2','主要交战方'],['secondaryA','1','直接军事介入'],['secondaryB','2','直接军事介入']])for(const name of annual[key]||[]){
  const supplements=(war.also||[]).flatMap(w=>participantsAt(w,year)).filter(p=>canonical(p.name,year)===canonical(name,year));
  const supplement=supplements.sort((a,b)=>(b.peakTheaterForces||0)-(a.peakTheaterForces||0))[0];
  rows.push({...supplement,name,side,role,periods:[[year,year]]});
 }
 for(const supplement of war.also||[]){
  const other=participantsAt(supplement,year),sameOrientation=other.some(p=>p.side==='1'&&rows.some(r=>r.side==='1'&&canonical(r.name,year)===canonical(p.name,year)));
  for(const p of other)if(!rows.some(r=>canonical(r.name,year)===canonical(p.name,year)))rows.push({...p,side:sameOrientation?p.side:p.side==='1'?'2':'1',role:'COW补充参战方（定义范围可能不同）'});
 }
 return withExtra(rows,war,year);}
 const rows=(war.participants||[]).filter(p=>inPeriods(p.periods,year)),unique=new Map();
 for(const row of rows){const key=row.side+'|'+canonical(row.name,year);const previous=unique.get(key);unique.set(key,{...previous,...row,peakTheaterForces:Math.max(previous?.peakTheaterForces||0,row.peakTheaterForces||0)||undefined});}
 return withExtra([...unique.values()],war,year);
}
export function warsAtYear(database,details,year){
 const active=(database?.wars||[]).filter(w=>w.annual?Boolean(w.annual[year]):inPeriods(w.periods,year));
 const supplements=new Map((details?.wars||[]).map(w=>[w.id,w]));
 const removed=new Set(),merged=new Map();
 for(const w of active){
  if(w.id.startsWith('ucdp'))continue;
  let counterpart=supplements.get(w.id)?.mergeUcdp||supplements.get(w.id)?.mergeHistorical;
  if(!counterpart){
   const sides=participantsAt(w,year),a=sides.filter(x=>x.side==='1').map(x=>canonical(x.name,year)),b=sides.filter(x=>x.side==='2').map(x=>canonical(x.name,year));
   const matched=active.filter(u=>u.annual).filter(u=>{const rows=participantsAt(u,year),ua=rows.filter(x=>x.side==='1').map(x=>canonical(x.name,year)),ub=rows.filter(x=>x.side==='2').map(x=>canonical(x.name,year));return (a.some(x=>ua.includes(x))&&b.some(x=>ub.includes(x)))||(a.some(x=>ub.includes(x))&&b.some(x=>ua.includes(x)));});
   if(matched.length===1)counterpart=matched[0].id;
  }
  // Merge only if that definition is actually active in this year.
  if(counterpart&&active.some(u=>u.id===counterpart)){removed.add(w.id);merged.set(counterpart,[...(merged.get(counterpart)||[]),w]);}
 }
 return active.filter(w=>!removed.has(w.id)).map(w=>{
  const also=merged.get(w.id)||[],detail=supplements.get(w.id)||also.map(x=>supplements.get(x.id)).find(Boolean);
  return {...w,detail,also};
 }).sort((a,b)=>(b.annual?.[year]?.intensity||2)-(a.annual?.[year]?.intensity||2)||a.from-b.from||a.id.localeCompare(b.id));
}
export function inferredCause(war,year){
 const a=war.annual?.[year];
 if(a)return a.issue===1?'领土归属、自治或分离诉求。此为依据数据库争议议题作出的概括推断，不能代替具体历史导火索。':a.issue===2?'中央政权归属或执政权争夺。此为依据数据库争议议题作出的概括推断，不能概括所有社会与国际原因。':'领土与中央政权争议相互交织。此为依据数据库分类作出的概括推断。';
 return war.category==='殖民／帝国战争'?'殖民统治、征服扩张或独立诉求之间的冲突（按战争类型概括推断）；具体导火索须结合原始史料。':war.category==='内战／国内冲突'?'国内政治权力、区域控制或群体利益的武装争夺（按分类概括推断）；具体原因尚未逐项核定。':'原始数据库未编码具体战争原因；不能仅凭参战国名称推断导火索。';
}
export const outcomeNames={1:'甲方胜利',2:'乙方胜利',3:'妥协／议和',4:'转为其他类型的战争',5:'数据库截止时仍在持续',6:'僵持',7:'冲突降至战争门槛以下',8:'参战方转换阵营'};
/** Interpolation is allowed only inside a short observed interval for the same
 * actor. No extrapolation, false precision, or conversion of deaths into forces. */
export function interpolateStrength(observations,year){
 const exact=observations?.[year]?.military;if(Number.isFinite(exact)&&exact>0)return {value:exact,estimated:false,years:[year]};
 const ys=Object.keys(observations||{}).map(Number).filter(y=>Number.isFinite(observations[y]?.military)&&observations[y].military>0).sort((a,b)=>a-b),before=ys.filter(y=>y<year).at(-1),after=ys.find(y=>y>year);
 if(before===undefined||after===undefined||after-before>5)return null;
 const value=observations[before].military+(observations[after].military-observations[before].military)*(year-before)/(after-before);
 return {value:Math.round(value/100)*100,estimated:true,years:[before,after]};
}
