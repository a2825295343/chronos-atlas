import {pointInGeometry} from './history.mjs';

const applies=([, ,from,to,at],year)=>
 (from!=null||to!=null||at!=null)&&(from==null||from<=year)&&(to==null||year<=to)&&(at==null||at===year);

export function reviewedCapitals(index,id,year,name){
 return (index.archive[id]||[]).filter(row=>row[6]&&(!row[7]||row[7]===name)&&applies(row,year));
}

function markerPosition(coordinates,parts,territories){
 const inside=point=>parts.some(part=>pointInGeometry(point,part.geometry));
 if(inside(coordinates))return coordinates;
 const [longitude,latitude]=coordinates;
 const longitudeScale=111*Math.cos(latitude*Math.PI/180);
 // Reconcile small coastline simplification gaps without moving a city across a border.
 for(const distance of [1,3,6]){
  for(let direction=0;direction<8;direction++){
   const angle=direction*Math.PI/4;
   const point=[longitude+distance*Math.cos(angle)/longitudeScale,latitude+distance*Math.sin(angle)/111];
   if(!inside(point))continue;
   for(const other of territories.values()){
    if(other!==parts&&other.some(part=>pointInGeometry(coordinates,part.geometry)))return undefined;
   }
   return point;
  }
 }
}

export function capitalsAtYear(world,year,index,identities){
 const features=[],territories=new Map();
 for(const feature of world?.features||[]){
  const p=feature.properties;
  if(!p?.NAME||!feature.geometry||p.controlArea||['archaeological-culture','human-presence'].includes(p.representationKind))continue;
  const owner=p.SUBJECTO?.trim()||p.NAME;
  if(!territories.has(owner))territories.set(owner,[]);
  territories.get(owner).push(feature);
 }
 for(const [owner,parts] of territories){
  const p=(parts.find(part=>part.properties.NAME===owner)||parts[0]).properties;
  const id=identities[p.NAME]||p.qid;
  const records=index.archive[id]||[];
  const dated=records.filter(row=>(!row[7]||row[7]===p.NAME)&&applies(row,year));
  const reviewed=dated.filter(row=>row[6]);
  const manual=dated.filter(record=>record[5]&&record[1]);
  const modern=year>=2024&&index.modern[p.NAME];
  const timeless=records.filter(([, ,from,to,at])=>from==null&&to==null&&at==null);
  const reference=!dated.length&&!modern;
  const singleCapital=new Set(timeless.map(row=>row[0])).size===1;
  const candidates=reviewed.length?reviewed:manual.length?manual:dated.length?dated:modern?[modern]:
   !index.hasDated.includes(id)&&singleCapital?timeless:[];
  const seen=new Set();
  for(const [label,coordinates,,,,,source,,federation] of candidates){
   if(!coordinates)continue;
   const ownPoint=markerPosition(coordinates,parts,territories);
   const federalPart=!ownPoint&&federation&&(territories.get(federation)||[])
    .find(part=>pointInGeometry(coordinates,part.geometry));
   const point=ownPoint||(federalPart?coordinates:undefined);
   if(!point)continue;
   const key=coordinates.join(',');
   if(seen.has(key))continue;
   seen.add(key);
   features.push({type:'Feature',geometry:{type:'Point',coordinates:point},
    properties:{label,owner,ownerLabel:p.displayName||owner,reference,source:source||index.source,federationLabel:federalPart?federalPart.properties.displayName||federation:undefined}});
  }
 }
 return {type:'FeatureCollection',features};
}


