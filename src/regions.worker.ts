import type {FeatureCollection} from 'geojson';
import {regionsAtYear} from './regions.mjs';
let modern:FeatureCollection={type:'FeatureCollection',features:[]},historical:FeatureCollection=modern;
const frames=new Map<string,FeatureCollection>();
self.onmessage=({data})=>{
 if(data.type==='init'){modern=data.modern;historical=data.historical;frames.clear();return;}
 const {id,world,year}=data;
 try{
  const key=year+'|'+(world?.features||[]).map((f:any)=>[f.properties?.NAME,f.properties?.sourceRecord,f.properties?.validFrom,f.properties?.validTo].join(':')).join('|');
  let collection=frames.get(key);if(!collection){collection=regionsAtYear(modern,historical,world,year);frames.set(key,collection);if(frames.size>3)frames.delete(frames.keys().next().value!);}
  self.postMessage({id,year,collection});
 }catch(error){self.postMessage({id,year,error:String(error)});}
};
