import {colorForName} from './history.mjs';

/** A source symbol is a point reference, never a territorial polygon. */
export function referenceSitesAtYear(collection,year){
 const seen=new Set();
 return {type:'FeatureCollection',features:(collection?.features||[]).filter(f=>{
  const p=f.properties;
  if(f.geometry?.type!=='Point'||!p||year<p.validFrom||year>p.validTo)return false;
  const key=[p.operator,...f.geometry.coordinates].join('|');
  if(seen.has(key))return false;seen.add(key);return true;
 }).map(f=>({...f,properties:{...f.properties,color:colorForName(f.properties.ownerName||f.properties.operator)}}))};
}
