/** Dates in historical years, source ages in thousands of years before 1950. */
export function paleogeographyAt(index,year){
 if(!index||year>=-4000)return null;
 const age=(1950-year)/1000,curve=index.curve;
 const right=curve.findIndex(p=>p.ageKa>=age);
 const b=curve[right<0?curve.length-1:right],a=curve[Math.max(0,right-1)];
 const t=a.ageKa===b.ageKa?0:Math.max(0,Math.min(1,(age-a.ageKa)/(b.ageKa-a.ageKa)));
 const level=a.level+(b.level-a.level)*t,sigma=a.sigma+(b.sigma-a.sigma)*t;
 const slice=index.levels.reduce((best,p)=>Math.abs(p.level-level)<Math.abs(best.level-level)?p:best);
 return {...slice,estimate:Math.round(level),sigma:Math.round(sigma),ageKa:age};
}
