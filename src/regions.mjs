import {featureCenter,pointInGeometry} from './history.mjs';
import polygonClipping from 'polygon-clipping';
import {modernReferenceFrom,cellModernFrom,periodPlaceRules} from './region-policy.mjs';
import establishedNames from './region-established-names.mjs';
const empty={type:'FeatureCollection',features:[]};
const rules=[...periodPlaceRules,
 {id:'RUS-2337',from:1703,to:1913,label:'圣彼得堡',owners:['Russian Empire']},
 {id:'RUS-2337',from:1914,to:1923,label:'彼得格勒',owners:['Russian Empire','Russian Republic','Union of Soviet Socialist Republics','Republics of the Soviet Union']},
 {id:'RUS-2337',from:1924,to:1990,label:'列宁格勒',owners:['Union of Soviet Socialist Republics']},
 {id:'RUS-2369',from:1925,to:1960,label:'斯大林格勒地区',owners:['Union of Soviet Socialist Republics']},
 {id:'RUS-2324',from:1815,to:1944,label:'东普鲁士（柯尼斯堡地区）',owners:['Prussia','German Empire','Weimar Republic','Nazi Germany']},
 {id:'KOR-2497',from:1394,to:1909,label:'汉城府',owners:['Joseon','Korean Empire']},
 {id:'KOR-2497',from:1910,to:1944,label:'京城府',owners:['Empire of Japan','Japan']},
 {id:'KOR-2497',from:1945,to:2026,label:'首尔'},
 {id:'TUR-2265',from:330,to:1452,label:'君士坦丁堡地区',owners:['Roman Empire','Byzantine Empire','Eastern Roman Empire','Latin Empire']},
 {id:'TUR-2265',from:1453,to:1922,label:'科斯坦丁尼耶（伊斯坦布尔）',owners:['Ottoman Empire']},
 {id:'TUR-2230',from:1500,to:1922,label:'士麦那地区',owners:['Ottoman Empire']},
];
// Modern cells spanning a former province are only neutral hit areas.
const formerProvinceCells={
 chahar:['CHN-1838','CHN-1811','CHN-1805'],
 pingyuan:['CHN-1814','CHN-1811','CHN-1812'],
 suiyuan:['CHN-1838','CHN-1804'],
 songjiang:['CHN-1839','CHN-1828'],
 liaodong:['CHN-1813','CHN-1828'],
 liaoxi:['CHN-1813','CHN-1838'],
 rehe:['CHN-1838','CHN-1813','CHN-1811'],
 xikang:['CHN-1662','CHN-1810','CHN-1809'],
};
const sourceFor=id=>id.startsWith('RUS-')?'https://www.britannica.com/place/St-Petersburg-Russia':id.startsWith('KOR-')?'https://english.seoul.go.kr/seoul-of-the-past/':'https://www.britannica.com/place/Istanbul';
/** Actual historical geometries replace reference cells where data is available. */
export function regionsAtYear(modern=empty,historical=empty,world=empty,year){
 const bounds=g=>{let w=180,s=90,e=-180,n=-90;for(const poly of g.type==='Polygon'?[g.coordinates]:g.type==='MultiPolygon'?g.coordinates:[])for(const [x,y]of poly[0]){w=Math.min(w,x);s=Math.min(s,y);e=Math.max(e,x);n=Math.max(n,y);}return[w,s,e,n];};
 const intersects=(a,b)=>a[0]<=b[2]&&a[2]>=b[0]&&a[1]<=b[3]&&a[3]>=b[1];
 const owners=(world?.features||[]).filter(f=>f.geometry&&['Polygon','MultiPolygon'].includes(f.geometry.type)).map(f=>({f,b:bounds(f.geometry)}));
 const names=new Set(owners.map(o=>o.f.properties?.NAME));
 const ownerAt=p=>owners.find(o=>p[0]>=o.b[0]&&p[0]<=o.b[2]&&p[1]>=o.b[1]&&p[1]<=o.b[3]&&pointInGeometry(p,o.f.geometry))?.f.properties.NAME;
 const active=[];
 for(const f of [...historical.features].sort((a,b)=>Number(a.properties.priority==='fallback')-Number(b.properties.priority==='fallback'))){
  const p=f.properties;if(p.validFrom>year||p.validTo<year)continue;
  if(p.supplement==='discontinued-chinese-provinces'){
   if(p.locatorOnly&&f.geometry.type==='Point')active.push(f);
   continue;
  }
  const scoped=p.ownerRequired||p.ownerAny?.length||p.ownerPrefix?.length;
  if(!scoped){
   if(p.priority==='fallback'){
    const superior=active.filter(r=>r.properties.country===p.country&&r.properties.priority!=='fallback');
    try{const coordinates=superior.length?polygonClipping.difference(f.geometry.coordinates,...superior.map(r=>r.geometry.coordinates)):(f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates);
     if(coordinates.length)active.push({...f,geometry:{type:'MultiPolygon',coordinates}});
    }catch{/* An uncertain locator must never cover a better historical boundary. */}
   }else active.push(f);
   continue;
  }
  const allowed=n=>p.ownerRequired===n||p.ownerAny?.includes(n)||p.ownerPrefix?.some(prefix=>n?.startsWith(prefix));
  if(![...names].some(allowed))continue;
  const b=bounds(f.geometry),clips=owners.filter(o=>allowed(o.f.properties.NAME)&&intersects(b,o.b));
  if(!clips.length)continue;
  // Intersect independently: unioning all touching clan outlines first can
  // fail on sub-metre source rounding and erase an otherwise valid province.
  const pieces=[];let failures=0;
  for(const o of clips)try{pieces.push(...polygonClipping.intersection(f.geometry.coordinates,o.f.geometry.coordinates));}catch{failures++;}
  if(!pieces.length)continue;
  let coordinates=pieces;
  if(pieces.length>1)try{coordinates=polygonClipping.union(pieces);}catch{/* Keep valid clipped pieces, never restore the unsliced reference. */}
  active.push({...f,geometry:{type:'MultiPolygon',coordinates},properties:{...p,clippedToOwner:true,...(failures?{clipFailures:failures}:{} )}});
 }
 const snapshots=active.filter(f=>f.properties.supplement==='chinese-province-snapshots');
 const snapshotKeys=new Set(snapshots.map(f=>f.properties.provinceKey));
 const locatorKey=f=>f.properties.provinceKey||f.properties.id.split(':')[1].replace('-yaan','');
 const locators=active.filter(f=>f.properties.locatorOnly&&!snapshotKeys.has(locatorKey(f)));
 const withheldCells=new Set([...locators.map(locatorKey),...snapshotKeys]
  .flatMap(key=>formerProvinceCells[key]||[]));
 const historicalFeatures=[...active.filter(f=>!f.properties.locatorOnly&&!snapshots.includes(f)),...snapshots,...locators];
 const replaced=new Set(active.filter(f=>f.properties.replaceCountry||(!f.properties.replaces&&f.properties.country==='Italy')).map(f=>f.properties.country));
 const replacedIds=new Set(active.flatMap(f=>f.properties.replaces||[]));
 const chongqing=year>=1955&&year<1997?modern.features.find(f=>f.properties.id==='CHN-1154'):null;
 const modernCells=chongqing?modern.features.filter(f=>f!==chongqing).map(f=>{
  if(f.properties.id!=='CHN-1809')return f;
  const coordinates=polygonClipping.union(f.geometry.coordinates,chongqing.geometry.coordinates);
  return {...f,geometry:{type:'MultiPolygon',coordinates},properties:{...f.properties,
   sourceUrl:'https://cq.gov.cn/zjcq/sqgk/cqsq/202412/t20241231_14378256.html',
   accuracy:'重庆于1954年改为四川省辖市，1997年恢复直辖。此处合并现代底图作范围参考。'}};
 }):modern.features;
 const features=modernCells.filter(f=>!replaced.has(f.properties.country)&&!replacedIds.has(f.properties.id)
  &&!(f.properties.id==='CHN-1813'&&year>=1949&&year<=1953)).map(f=>{
  const candidate=rules.find(r=>r.id===f.properties.id&&r.from<=year&&year<=r.to);
  const modernYear=cellModernFrom[f.properties.id]??modernReferenceFrom[f.properties.country]??1950;
  const reference=()=>({...f,properties:{...f.properties,dataKind:'modern-reference',modernLabel:f.properties.label,suppressLabel:year<modernYear,boundaryVisible:year>=modernYear,accuracy:f.properties.accuracy||(year<modernYear?'该年历史名称与行政界未核定；此地块仅作可点击的空间定位参考，现代行政名不显示在古代地图上。':'现代分区定位参考；不能据此推断该年边界与现状完全相同。')}});
  if(withheldCells.has(f.properties.id))return {...f,properties:{...f.properties,dataKind:'modern-reference',
   suppressLabel:true,boundaryVisible:false,accuracy:'此处仅可定位。此参考地块的省界尚未完全核实。'}};
  if(!candidate){
   const established=establishedNames[f.properties.id];
   const dated=established?.periods?.find(r=>r.from<=year&&year<=r.to);
   if(year<modernYear&&established&&(established.from<=year||dated))return {...f,properties:{...f.properties,label:dated?.label||established.label,modernLabel:f.properties.label,historicalName:true,suppressLabel:false,boundaryVisible:false,validFrom:dated?.from||established.from,validTo:dated?.to,dataKind:'historical-name-reference-boundary',sourceUrl:established.source,accuracy:'此名称在本年已有依据；轮廓仍为现代定位参考，不据此绘制当年的行政边界。'}};
   return reference();
  }
  let center=featureCenter(f.geometry);
  if(!pointInGeometry(center,f.geometry)){const rings=f.geometry.type==='Polygon'?[f.geometry.coordinates[0]]:f.geometry.type==='MultiPolygon'?f.geometry.coordinates.map(p=>p[0]):[];let found=false;for(const ring of rings){for(const vertex of ring.filter((_,i)=>i%Math.max(1,Math.floor(ring.length/30))===0)){for(const t of [.05,.2,.5]){const candidate=[vertex[0]*(1-t)+center[0]*t,vertex[1]*(1-t)+center[1]*t];if(pointInGeometry(candidate,f.geometry)){center=candidate;found=true;break;}}if(found)break;}if(found)break;}}
  const owner=ownerAt(center);
  if(candidate.owners&&!candidate.owners.includes(owner))return reference();
  return {...f,properties:{...f.properties,label:candidate.label,modernLabel:f.properties.label,historicalName:true,boundaryVisible:true,validFrom:candidate.from,validTo:candidate.to,sourceUrl:sourceFor(candidate.id),dataKind:'historical-name-reference-boundary',accuracy:'名称按年代与实际控制势力筛选；轮廓仍为现代定位参考'}};
 });
 return {type:'FeatureCollection',features:partitionRegions([...features,...historicalFeatures],bounds)};
}

/** One selectable footprint per location. Prefer dated boundaries over references. */
function partitionRegions(features,bounds){
 const rank=p=>p.dataKind==='historical-snapshot'?0:p.dataKind==='historical-reconstruction'?1:p.priority==='fallback'?3:p.dataKind==='modern-reference'?4:2;
 const accepted=[];
 const grid=new Map();
 const keys=([w,s,e,n])=>{
  const result=[];
  for(let x=Math.floor(w/10);x<=Math.floor(e/10);x++)
   for(let y=Math.floor(s/10);y<=Math.floor(n/10);y++)result.push(x+','+y);
  return result;
 };
 for(const f of features.filter(f=>!f.properties.suppressLabel).sort((a,b)=>rank(a.properties)-rank(b.properties))){
  if(f.geometry.type==='Point'){accepted.push(f);continue;}
  const modern=f.properties.dataKind==='modern-reference';
  const snapshot=f.properties.supplement==='chinese-province-snapshots'?f.properties.sourceYear:null;
  // The Chinese source is already partitioned with GEOS during import.
  // Re-clipping its shared edges can introduce floating-point topology errors.
  const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;
  let changed=false;
  const coordinates=polygons.flatMap(polygon=>{
   const box=bounds({type:'Polygon',coordinates:polygon});
   const candidates=new Set(keys(box).flatMap(cell=>grid.get(cell)||[]));
   const cuts=[...candidates].filter(({box:b,sourceYear})=>(snapshot===null||snapshot!==sourceYear)
    &&box[0]<b[2]&&box[2]>b[0]&&box[1]<b[3]&&box[3]>b[1]);
   if(!cuts.length)return [polygon];
   changed=true;
   try{return polygonClipping.difference(polygon,...cuts.map(r=>r.polygon));}
   catch{return [];}
  });
  if(!coordinates.length)continue;
  const region=changed?{...f,geometry:{type:'MultiPolygon',coordinates}}:f;
  accepted.push(region);
  // The modern reference dataset is a single base layer. Index overlays,
  // not its thousands of mutually adjacent administrative cells.
  if(modern)continue;
  for(const polygon of coordinates){
   const entry={box:bounds({type:'Polygon',coordinates:polygon}),polygon,sourceYear:snapshot};
   for(const cell of keys(entry.box)){
    if(!grid.has(cell))grid.set(cell,[]);
    grid.get(cell).push(entry);
   }
  }
 }
 return accepted;
}
